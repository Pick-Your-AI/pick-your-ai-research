"""Real qualification-record integrity and synthetic capture rejection fixtures."""
import copy
import errno
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
try:
    import mr09_native_capture as capture
finally:
    sys.path.pop(0)
DIRECTORY=ROOT/capture.DIRECTORY

class NativeCaptureTests(unittest.TestCase):
    def setUp(self): self.record=json.loads((DIRECTORY/"init-r1.json").read_text())
    def mutate_event(self,key,value,field,new_value):
        events=[json.loads(l) for l in self.record["stdout"].splitlines()]
        event=next(e for e in events if e.get(key)==value)
        event[field]=new_value
        self.record["stdout"]="\n".join(json.dumps(e) for e in events)+"\n"

    def test_committed_qualification_recomputes(self):
        actual=capture.summarize(DIRECTORY)
        expected=json.loads((DIRECTORY/"qualification-summary.json").read_text())
        self.assertEqual(actual,expected)
        self.assertEqual(actual["initialization_trials"],3)
        self.assertEqual(actual["accepted_estimator_pairs"],0)
        self.assertEqual({r["exact_admitted_live_buffer_bytes"] for r in actual["observations"]},{334511360})
        self.assertTrue(all(r["cleanup_live_bytes"]==0 for r in actual["observations"]))

    def test_no_alloc_and_effective_type_aliases_rejected(self):
        for field,value in (("no_alloc",True),("sequences",True),("generation_forwards",1),("extra_buffer_types",True)):
            self.record=json.loads((DIRECTORY/"init-r1.json").read_text())
            self.mutate_event("mr09_event","effective",field,value)
            with self.subTest(field=field),self.assertRaises(ValueError): capture.validate_capture(self.record)

    def test_cap_or_graph_attempt_drift_rejected(self):
        for field,value in (("live_bytes",3*2**30),("graph_denials",2),("admission_denials",2)):
            self.record=json.loads((DIRECTORY/"init-r1.json").read_text())
            events=[json.loads(l) for l in self.record["stdout"].splitlines()]
            next(e for e in events if e.get("stage")=="before_capture")[field]=value
            self.record["stdout"]="\n".join(json.dumps(e) for e in events)+"\n"
            with self.subTest(field=field),self.assertRaises(ValueError): capture.validate_capture(self.record)

    def test_duplicate_capture_event_rejected(self):
        line=next(l for l in self.record["stdout"].splitlines() if 'fit_memory_breakdown' in l)
        self.record["stdout"]+=line+"\n"
        with self.assertRaises(ValueError): capture.validate_capture(self.record)

    def test_native_rounding_must_reconcile_with_live_ledger(self):
        events=[json.loads(l) for l in self.record["stdout"].splitlines()]
        event=next(e for e in events if e.get("type")=="fit_memory_breakdown")
        event["data"]["rows"][0]["self"]=318
        self.record["stdout"]="\n".join(json.dumps(e) for e in events)+"\n"
        with self.assertRaises(ValueError): capture.validate_capture(self.record)

    def test_mixed_hardware_cohort_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            dest=Path(temp)/"copy";shutil.copytree(DIRECTORY,dest)
            path=dest/"init-r2.json";record=json.loads(path.read_text())
            record["driver_csv"]=record["driver_csv"].replace('610.88','synthetic-other-driver')
            path.write_text(json.dumps(record))
            with self.assertRaises(ValueError): capture.summarize(dest)

    def test_failed_publication_keeps_all_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            dest=Path(temp)/"copy";shutil.copytree(DIRECTORY,dest)
            path=dest/"init-r3.json";record=json.loads(path.read_text());record["exit_code"]=1
            path.write_text(json.dumps(record))
            before={p.name:p.read_bytes() for p in dest.glob('init-*.json')}
            with self.assertRaises(ValueError): capture.publish(dest,Path(temp)/"archive")
            self.assertEqual(before,{p.name:p.read_bytes() for p in dest.glob('init-*.json')})
            self.assertFalse((Path(temp)/"archive").exists())

    def test_consistently_changed_pins_or_command_rejected(self):
        for field,value in (("model_sha256","0"*64),("harness_git_ref","0"*40),
                            ("launcher_sha256","0"*64),("argv",["synthetic-other-command"])):
            with self.subTest(field=field),tempfile.TemporaryDirectory() as temp:
                dest=Path(temp)/"copy";shutil.copytree(DIRECTORY,dest)
                for path in dest.glob("init-r?.json"):
                    record=json.loads(path.read_text());record[field]=value
                    path.write_text(json.dumps(record))
                with self.assertRaises(ValueError): capture.summarize(dest)

    def test_nonfinite_and_duplicate_event_keys_rejected(self):
        for text in ('{"x":1,"x":1}','{"x":NaN}','{"x":1e999}'):
            with self.subTest(text=text),self.assertRaises(ValueError): capture.loads(text)

    def test_driver_csv_ambiguity_rejected_but_quoted_reordering_supported(self):
        original=self.record["driver_csv"]
        for text in (
            original.replace("driver_version,", "driver_version,driver_version,").replace("610.88,", "conflicting,610.88,"),
            original.replace("driver_version,", "driver_version, driver_version ,").replace("610.88,", "conflicting,610.88,"),
            original.replace("name,", "name, ,").replace("NVIDIA", "value,NVIDIA",1),
            original+",extra",
        ):
            with self.subTest(text=text),self.assertRaises(ValueError): capture.driver_readback(text)
        reordered='"memory.free [MiB]","driver_version","name","memory.total [MiB]"\n"10134 MiB","610.88","NVIDIA, synthetic quoted name","16303 MiB"'
        parsed=capture.driver_readback(reordered)
        self.assertEqual(parsed["name"],"NVIDIA, synthetic quoted name")
        self.assertEqual(parsed["driver_version"],"610.88")

    def test_rehashed_invalid_preflights_rejected_without_publication(self):
        def set_nested(record,group,key,value): record[group][key]=value
        cases=[
            lambda r:r.update(guards={}),
            lambda r:r.update(status="blocked"),
            lambda r:set_nested(r,"observed","available_host_ram_bytes",1),
            lambda r:set_nested(r,"guards","available_host_ram_bytes",1),
            lambda r:set_nested(r,"observed","available_host_ram_bytes",float(r["observed"]["available_host_ram_bytes"])),
            lambda r:set_nested(r,"thresholds","available_host_ram_bytes",1),
            lambda r:r.update(methods=[]),
            lambda r:r.update(observed_utc="2026-10-19T00:00:00+00:00"),
            lambda r:r.update(observed_utc="2026-10-18T06:40:00+00:00"),
            lambda r:set_nested(r,"observed","nvidia_smi_free_mib",999999),
        ]
        for index,change in enumerate(cases):
            with self.subTest(case=index),tempfile.TemporaryDirectory() as temp:
                dest=Path(temp)/"copy";shutil.copytree(DIRECTORY,dest)
                preflight=dest/"init-r1-preflight.json";screen=json.loads(preflight.read_text())
                change(screen);preflight.write_text(json.dumps(screen))
                path=dest/"init-r1.json";record=json.loads(path.read_text())
                record["preflight_sha256"]=capture.sha(preflight);path.write_text(json.dumps(record))
                before={p.name:p.read_bytes() for p in dest.glob('init-*.json')}
                with self.assertRaises(ValueError): capture.publish(dest,Path(temp)/"archive")
                self.assertEqual(before,{p.name:p.read_bytes() for p in dest.glob('init-*.json')})
                self.assertFalse((Path(temp)/"archive").exists())

    def test_capture_cannot_move_after_cleanup(self):
        lines=self.record["stdout"].splitlines()
        line=next(l for l in lines if 'fit_memory_breakdown' in l)
        lines.remove(line);lines.append(line)
        self.record["stdout"]="\n".join(lines)+"\n"
        with self.assertRaises(ValueError): capture.validate_capture(self.record)

    def test_cleanup_peak_cannot_decrease(self):
        events=[json.loads(l) for l in self.record["stdout"].splitlines()]
        next(e for e in events if e.get("stage")=="after_cleanup")["peak_admitted_bytes"]=8388608
        self.record["stdout"]="\n".join(json.dumps(e) for e in events)+"\n"
        with self.assertRaises(ValueError): capture.validate_capture(self.record)

    def test_native_discovery_requires_typed_sufficient_consistent_bytes(self):
        for field,value in (("cuda_reported_free_bytes",0),("cuda_reported_free_bytes",2**65),
                            ("driver_total_bytes",17094475776.0),("cuda_reported_free_bytes",True)):
            self.record=json.loads((DIRECTORY/"init-r1.json").read_text())
            self.mutate_event("mr09_event","qualification",field,value)
            with self.subTest(field=field,value=value),self.assertRaises(ValueError): capture.validate_capture(self.record)

    def test_native_capture_capacity_matches_discovery(self):
        for field,value in (("total",1),("total",16302.0),("total",True),
                            ("free",-1),("free",20000),("free",14717.0)):
            with self.subTest(field=field,value=value),tempfile.TemporaryDirectory() as temp:
                dest=Path(temp)/"copy";shutil.copytree(DIRECTORY,dest)
                path=dest/"init-r1.json";record=json.loads(path.read_text())
                events=[json.loads(line) for line in record["stdout"].splitlines()]
                event=next(e for e in events if e.get("type")=="fit_memory_breakdown")
                event["data"]["rows"][0][field]=value
                record["stdout"]="\n".join(json.dumps(e) for e in events)+"\n"
                path.write_text(json.dumps(record))
                before={p.name:p.read_bytes() for p in dest.glob('init-*.json')}
                with self.assertRaises(ValueError): capture.summarize(dest)
                with self.assertRaises(ValueError): capture.publish(dest,Path(temp)/"archive")
                self.assertEqual(before,{p.name:p.read_bytes() for p in dest.glob('init-*.json')})
                self.assertFalse((Path(temp)/"archive").exists())

    def test_rehashed_overlapping_trials_cannot_count_as_serial(self):
        for mode in ("overlap","reused_screen"):
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as temp:
                dest=Path(temp)/"copy";shutil.copytree(DIRECTORY,dest)
                first=json.loads((dest/"init-r1.json").read_text())
                path=dest/"init-r2.json";second=json.loads(path.read_text())
                preflight=dest/second["preflight_file"]
                screen=json.loads(preflight.read_text())
                if mode=="overlap":
                    screen["observed_utc"]=json.loads((dest/"init-r1-preflight.json").read_text())["observed_utc"]
                    second["started_utc"]=first["started_utc"]
                    second["finished_utc"]=first["finished_utc"]
                else:
                    # Still within the existing 30-second freshness bound, but
                    # obtained before the preceding child had finished.
                    screen["observed_utc"]=first["started_utc"]
                    second["started_utc"]="2026-10-18T06:45:50+00:00"
                    second["finished_utc"]="2026-10-18T06:45:51+00:00"
                preflight.write_text(json.dumps(screen))
                second["preflight_sha256"]=capture.sha(preflight)
                path.write_text(json.dumps(second))
                before={p.name:p.read_bytes() for p in dest.glob('init-*.json')}
                with self.assertRaises(ValueError): capture.summarize(dest)
                with self.assertRaises(ValueError): capture.publish(dest,Path(temp)/"archive")
                self.assertEqual(before,{p.name:p.read_bytes() for p in dest.glob('init-*.json')})
                self.assertFalse((Path(temp)/"archive").exists())

    def test_native_quota_portable_cpu_selftest(self):
        compiler=shutil.which("g++")
        if not compiler: self.skipTest("portable compiler absent; MSVC execution separately recorded")
        with tempfile.TemporaryDirectory() as temp:
            exe=Path(temp)/"quota-test"
            subprocess.run([compiler,"-std=c++17","-pthread","-UNDEBUG","-I",str(ROOT/"research/market/measurements/native"),str(ROOT/"tests/native/mr09_quota_selftest.cpp"),"-o",str(exe)],check=True,capture_output=True)
            result=json.loads(subprocess.check_output([str(exe)],text=True))
            self.assertEqual(result["concurrent_admissions"],16000)
            self.assertEqual(result["boundary_denials"],2)
            self.assertEqual(result["final_live_bytes"],0)


class NativeCaptureCLITests(unittest.TestCase):
    def run_cli(self,directory):
        # subprocess.run kills and reaps only its child if the deadline expires.
        return subprocess.run(
            [sys.executable,"-B",str(ROOT/"scripts/mr09_native_capture.py"),
             "--directory",str(directory)],
            cwd=ROOT,capture_output=True,text=True,timeout=5,check=False)

    def test_read_only_cli_accepts_committed_regular_inputs(self):
        result=self.run_cli(DIRECTORY)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stderr,"")
        self.assertEqual(json.loads(result.stdout),{
            "initialization_trials":3,"accepted_estimator_pairs":0,
            "exact_live_buffer_bytes":[334511360,334511360,334511360]})

    @unittest.skipUnless(hasattr(os,"mkfifo"),"FIFO creation is unavailable")
    def test_read_only_cli_rejects_fifo_inputs_without_a_writer(self):
        names=("build-loader-v2.json","runtime-artifacts.json",
               *(f"init-r{rep}.json" for rep in (1,2,3)),
               *(f"init-r{rep}-preflight.json" for rep in (1,2,3)))
        for name in names:
            with self.subTest(input=name),tempfile.TemporaryDirectory() as temp:
                directory=Path(temp)/"inputs";shutil.copytree(DIRECTORY,directory)
                path=directory/name
                path.unlink()
                os.mkfifo(path)
                result=self.run_cli(directory)
                self.assertNotEqual(result.returncode,0)
                self.assertEqual(result.stdout,"")
                self.assertIn("regular native capture input required: "+name,result.stderr)

class NativePublicationTests(unittest.TestCase):
    """Synthetic publication state/faults; no new native observation is created."""

    def prepare(self,directory,*,summary=True):
        shutil.copytree(DIRECTORY,directory)
        for rep in (1,2,3):
            path=directory/f"init-r{rep}.json"
            record=json.loads(path.read_text())
            record.pop("publication",None)
            # Deliberately noncanonical whitespace exercises raw-preflight
            # preservation as well as record and summary restoration.
            preflight=directory/record["preflight_file"]
            preflight.write_text(json.dumps(json.loads(preflight.read_text()),separators=(",",":"))+"\n")
            record["preflight_sha256"]=capture.sha(preflight)
            path.write_text(json.dumps(record,indent=2)+"\n")
        if not summary:
            (directory/"qualification-summary.json").unlink()
        capture.summarize(directory)

    def inputs(self,directory):
        return {path.name:(path.read_bytes(),path.stat().st_mode&0o7777)
                for path in directory.iterdir() if path.is_file()}

    def assert_no_staging(self,directory):
        self.assertEqual(list(directory.glob(".mr09-publication-*")),[])

    def assert_published(self,directory):
        result=capture.summarize(directory)
        self.assertEqual(result,json.loads((directory/"qualification-summary.json").read_text()))
        self.assertEqual(result["initialization_trials"],3)
        self.assertEqual(result["accepted_estimator_pairs"],0)
        self.assertTrue(all("publication" in json.loads((directory/f"init-r{rep}.json").read_text())
                            for rep in (1,2,3)))

    def test_success_archives_raw_preflights_records_and_summary(self):
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp)/"inputs";self.prepare(directory)
            (directory/"init-r1.json").chmod(0o640)
            before=self.inputs(directory);archive=Path(temp)/"archive"
            result=capture.publish(directory,archive)
            expected={name:raw for name,(raw,_) in before.items() if name in {
                "build-loader-v2.json","runtime-artifacts.json","qualification-summary.json",
                *(f"init-r{rep}.json" for rep in (1,2,3)),
                *(f"init-r{rep}-preflight.json" for rep in (1,2,3))}}
            self.assertEqual({path.name:path.read_bytes() for path in archive.iterdir()},expected)
            self.assertEqual(result,capture.summarize(directory))
            self.assertEqual((directory/"init-r1.json").stat().st_mode&0o7777,before["init-r1.json"][1])
            self.assert_published(directory);self.assert_no_staging(directory)
            published=self.inputs(directory)
            with self.assertRaisesRegex(ValueError,"already published"):
                capture.publish(directory,Path(temp)/"second-archive")
            self.assertEqual(self.inputs(directory),published)
            self.assertFalse((Path(temp)/"second-archive").exists())
            self.assert_no_staging(directory)

    def test_preparation_write_failure_keeps_every_original(self):
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp)/"inputs";self.prepare(directory)
            before=self.inputs(directory);archive=Path(temp)/"archive"
            write=Path.write_bytes
            def fail(path,data):
                if path.parent.name=="prepared" and path.name=="init-r2.json":
                    raise OSError(errno.ENOSPC,"synthetic staging write failure")
                return write(path,data)
            with mock.patch.object(Path,"write_bytes",fail),self.assertRaises(OSError):
                capture.publish(directory,archive)
            self.assertEqual(self.inputs(directory),before)
            self.assertFalse(archive.exists());self.assert_no_staging(directory)
            capture.publish(directory,Path(temp)/"retry-archive")
            self.assert_published(directory)

    def test_new_summary_uses_staged_supported_mode(self):
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp)/"inputs";self.prepare(directory,summary=False)
            before=self.inputs(directory);archive=Path(temp)/"archive"
            chmod=capture.os.chmod;observed=[]
            def limited_modes(path,mode):
                path=Path(path)
                if path.parent.name=="prepared" and path.name=="qualification-summary.json":
                    self.assertEqual(mode,0o644)
                    # Synthetic permission support, not a native Windows run:
                    # requested POSIX bits need not be the filesystem's result.
                    chmod(path,0o666)
                    observed.append(path.stat().st_mode&0o7777)
                else:
                    chmod(path,mode)
            with mock.patch.object(capture.os,"chmod",limited_modes):
                capture.publish(directory,archive)
            self.assertEqual(observed,[0o666])
            self.assertEqual((directory/"qualification-summary.json").stat().st_mode&0o7777,observed[0])
            for name,(_,mode) in before.items():
                self.assertEqual((directory/name).stat().st_mode&0o7777,mode)
            self.assertFalse((archive/"qualification-summary.json").exists())
            self.assert_published(directory);self.assert_no_staging(directory)

    def test_archive_write_failure_never_partly_publishes_and_retry_works(self):
        targets=["build-loader-v2.json","runtime-artifacts.json","qualification-summary.json",
                 *(f"init-r{rep}.json" for rep in (1,2,3)),
                 *(f"init-r{rep}-preflight.json" for rep in (1,2,3))]
        for target in targets:
            with self.subTest(target=target),tempfile.TemporaryDirectory() as temp:
                directory=Path(temp)/"inputs";self.prepare(directory)
                before=self.inputs(directory);archive=Path(temp)/"archive"
                write=Path.write_bytes
                def fail(path,data):
                    if path==archive/target:
                        raise OSError(errno.ENOSPC,"synthetic archive write failure")
                    return write(path,data)
                with mock.patch.object(Path,"write_bytes",fail),self.assertRaises(OSError):
                    capture.publish(directory,archive)
                self.assertEqual(self.inputs(directory),before)
                self.assert_no_staging(directory)
                for path in archive.iterdir():
                    self.assertEqual(path.read_bytes(),before[path.name][0])
                capture.publish(directory,Path(temp)/"retry-archive")
                self.assert_published(directory)

    def test_publication_faults_under_aliased_temporary_root(self):
        with tempfile.TemporaryDirectory() as temp:
            real=Path(temp)/"real";real.mkdir()
            alias=Path(temp)/"alias"
            try:
                alias.symlink_to(real,target_is_directory=True)
            except OSError as error:
                if os.name=="nt" and getattr(error,"winerror",None)==1314:
                    self.skipTest("directory symlink creation is unavailable "
                                  "(Windows privilege not held; winerror 1314)")
                if error.errno in (errno.EPERM,errno.EACCES,errno.ENOSYS):
                    self.skipTest("directory symlink creation is unavailable")
                raise
            self.assertNotEqual(alias,alias.resolve())
            cases=(
                "test_replacement_failure_restores_bytes_modes_and_summary_presence",
                "test_final_readback_failure_removes_new_summary_and_restores_preflights",
                "test_rollback_failure_retains_archive_and_local_recovery_bytes",
            )
            # Exercise every existing fault/restoration assertion with the
            # same symlinked-root condition that /var supplies on macOS.
            with mock.patch.object(tempfile,"tempdir",str(alias)):
                for name in cases:
                    with self.subTest(fault_sequence=name):
                        getattr(self,name)()

    def test_replacement_failure_restores_bytes_modes_and_summary_presence(self):
        targets=[*(f"init-r{rep}.json" for rep in (1,2,3)),
                 *(f"init-r{rep}-preflight.json" for rep in (1,2,3)),"qualification-summary.json"]
        for present in (False,True):
            for target in targets:
                with self.subTest(summary_present=present,target=target),tempfile.TemporaryDirectory() as temp:
                    directory=Path(temp)/"inputs";self.prepare(directory,summary=present)
                    (directory/"init-r1-preflight.json").chmod(0o640)
                    before=self.inputs(directory);archive=Path(temp)/"archive"
                    replace=capture.os.replace
                    def fail(source,dest):
                        if Path(source).parent.name=="prepared" and Path(dest)==directory.resolve()/target:
                            raise OSError(errno.EIO,"synthetic input replacement failure")
                        return replace(source,dest)
                    with mock.patch.object(capture.os,"replace",fail),self.assertRaises(OSError):
                        capture.publish(directory,archive)
                    self.assertEqual(self.inputs(directory),before)
                    self.assert_no_staging(directory)
                    self.assertEqual((archive/"qualification-summary.json").exists(),present)
                    capture.publish(directory,Path(temp)/"retry-archive")
                    self.assert_published(directory)

    def test_final_readback_failure_removes_new_summary_and_restores_preflights(self):
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp)/"inputs";self.prepare(directory,summary=False)
            before=self.inputs(directory);archive=Path(temp)/"archive"
            read=Path.read_bytes;failed=False
            def fail(path):
                nonlocal failed
                if not failed and path==directory.resolve()/"qualification-summary.json" and path.exists():
                    failed=True
                    raise OSError(errno.EIO,"synthetic final readback failure")
                return read(path)
            with mock.patch.object(Path,"read_bytes",fail),self.assertRaises(OSError):
                capture.publish(directory,archive)
            self.assertTrue(failed)
            self.assertEqual(self.inputs(directory),before)
            self.assert_no_staging(directory)
            capture.publish(directory,Path(temp)/"retry-archive")
            self.assert_published(directory)

    def test_rollback_failure_retains_archive_and_local_recovery_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp)/"inputs";self.prepare(directory)
            before=self.inputs(directory);archive=Path(temp)/"archive"
            replace=capture.os.replace
            def fail(source,dest):
                source=Path(source);dest=Path(dest)
                if source.parent.name=="prepared" and dest==directory.resolve()/"init-r2.json":
                    raise OSError(errno.EIO,"synthetic publication failure")
                if source.parent.name=="originals" and dest==directory.resolve()/"init-r1.json":
                    raise OSError(errno.EACCES,"synthetic rollback failure")
                return replace(source,dest)
            with mock.patch.object(capture.os,"replace",fail),self.assertRaises(capture.PublicationRecoveryRequired) as caught:
                capture.publish(directory,archive)
            error=caught.exception
            self.assertEqual(error.unrestored_files,("init-r1.json",))
            self.assertEqual(error.archive,archive)
            self.assertTrue(error.staging_directory.is_dir())
            self.assertEqual((error.staging_directory/"originals/init-r1.json").read_bytes(),before["init-r1.json"][0])
            self.assertEqual((archive/"init-r1.json").read_bytes(),before["init-r1.json"][0])
            for name,(raw,_) in before.items():
                if (archive/name).exists(): self.assertEqual((archive/name).read_bytes(),raw)
            # Demonstrate recovery using retained bytes in this disposable
            # fixture only; the publisher does not silently recover user input.
            replace(error.staging_directory/"originals/init-r1.json",directory/"init-r1.json")
            shutil.rmtree(error.staging_directory)
            self.assertEqual(self.inputs(directory),before)
            capture.publish(directory,Path(temp)/"retry-archive")
            self.assert_published(directory)

    def test_changed_input_after_archival_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp)/"inputs";self.prepare(directory)
            before=self.inputs(directory);archive=Path(temp)/"archive"
            write=Path.write_bytes
            changed=before["init-r2.json"][0]+b"\n"
            def mutate(path,data):
                result=write(path,data)
                if path==archive/"qualification-summary.json":
                    write(directory/"init-r2.json",changed)
                return result
            with mock.patch.object(Path,"write_bytes",mutate),self.assertRaisesRegex(ValueError,"changed after snapshot"):
                capture.publish(directory,archive)
            expected=dict(before);expected["init-r2.json"]=(changed,before["init-r2.json"][1])
            self.assertEqual(self.inputs(directory),expected)
            self.assert_no_staging(directory)

    def test_cleanup_failure_reports_completed_publication_and_retains_staging(self):
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp)/"inputs";self.prepare(directory)
            archive=Path(temp)/"archive"
            with mock.patch.object(capture.shutil,"rmtree",side_effect=OSError(errno.EACCES,"synthetic cleanup failure")):
                with self.assertRaises(capture.PublicationCleanupRequired) as caught:
                    capture.publish(directory,archive)
            self.assertTrue(caught.exception.publication_completed)
            self.assertIn("publication completed and verified",str(caught.exception))
            self.assertTrue(caught.exception.staging_directory.exists())
            self.assert_published(directory)
            shutil.rmtree(caught.exception.staging_directory)

    def test_cleanup_failure_after_archive_error_reports_unchanged_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp)/"inputs";self.prepare(directory)
            before=self.inputs(directory);archive=Path(temp)/"archive"
            write=Path.write_bytes
            def fail(path,data):
                if path==archive/"init-r2.json": raise OSError(errno.ENOSPC,"synthetic archive failure")
                return write(path,data)
            with mock.patch.object(Path,"write_bytes",fail),mock.patch.object(capture.shutil,"rmtree",side_effect=OSError(errno.EACCES,"synthetic cleanup failure")):
                with self.assertRaises(capture.PublicationCleanupRequired) as caught:
                    capture.publish(directory,archive)
            self.assertFalse(caught.exception.publication_completed)
            self.assertEqual(self.inputs(directory),before)
            self.assertTrue(caught.exception.staging_directory.exists())
            shutil.rmtree(caught.exception.staging_directory)
            capture.publish(directory,Path(temp)/"retry-archive")
            self.assert_published(directory)


if __name__=="__main__":unittest.main()
