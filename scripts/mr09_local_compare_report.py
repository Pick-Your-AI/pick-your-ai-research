"""Offline integrity/arithmetic readback for the prospective local H1 cohort.

This never launches a GPU process or grants receiving-owner acceptance.
"""
from datetime import datetime
from fractions import Fraction
import json
from pathlib import Path
import statistics

from mr09_local_compare_run import (ROOT, DIRECTORY, MODEL_SHA, CAP_BYTES,
                                    matching_driver, sha, validate_h1,
                                    validate_screen, verify_files)
from mr09_native_capture import read_json
from mr09_total_memory_setup import error_interval


def summarize(directory=DIRECTORY):
    freeze = read_json(directory / 'prediction-freeze.json')
    verify_files(ROOT, freeze['files'])
    frozen = datetime.fromisoformat(freeze['observed_utc'])
    prediction = read_json(ROOT / freeze['prediction_file'])
    receipt = read_json(directory / 'prediction-receipt.json')
    if (prediction['artifact_sha256'] != MODEL_SHA or prediction['artifact_bytes'] != 270885952
            or prediction['identity'] != 'gguf-parser-go-v0.26.4+mr09-output.1-experimental'
            or prediction['upstream_commit'] != '637cd9a7a03993ab30ace3c53dd8af5c37f46a94'):
        raise ValueError('prediction identity drift')
    profile = read_json(directory / 'estimator-profile.json')
    if prediction['declared_profile'] != profile:
        raise ValueError('declared profile drift')
    devices = prediction['estimate']['devices']
    if len(devices) != 2:
        raise ValueError('host plus one CUDA0 device required')
    device = devices[1]
    if (device['remote'] is not False or type(device['position']) is not int
            or device['position'] != 0 or device['handleOutputLayer'] is not True):
        raise ValueError('device placement drift')
    # Validate both raw operands before max can discard either one.
    graph, output = device['computation']['graph'], device['computation']['output']
    if any(type(value) is not int or not 0 <= value < 2**64 for value in (graph, output)):
        raise ValueError('exact integer byte terms required')
    terms = [device['footprint'], *[device['weight'][key] for key in ('input','compute','computeOverridden','output')],
             device['kvCache']['key'], device['kvCache']['value'], device['computation']['footprint'],
             device['computation']['input'], max(graph, output)]
    if any(type(value) is not int or not 0 <= value < 2**64 for value in terms):
        raise ValueError('exact integer byte terms required')
    estimate = sum(terms)
    if not 0 < estimate == freeze['managed_device_estimate_bytes'] == receipt['managed_device_estimate_bytes']:
        raise ValueError('prediction aggregation drift')
    if sha(ROOT / freeze['prediction_file']) != receipt['raw_prediction_sha256']:
        raise ValueError('raw prediction receipt drift')
    build = read_json(directory / 'build.json')
    observations = []
    previous_finished = None
    for repetition in (1,2,3):
        path = directory / f'H1-r{repetition}.json'
        record = read_json(path)
        if (record['status'] != 'native_initialization_completed' or type(record['repetition']) is not int
                or record['repetition'] != repetition or record['cell'] != 'H1'
                or record['driver_readback'] != {'status':'completed','timeout_seconds':10}):
            raise ValueError('incomplete or mismatched trial')
        expected = {'prediction_freeze_sha256':sha(directory / 'prediction-freeze.json'),
                    'prediction_file':freeze['prediction_file'],
                    'prediction_sha256':sha(ROOT / freeze['prediction_file']),
                    'harness_sha256':build['executables']['native-init.exe'],
                    'harness_git_ref':build['harness_git_ref'],
                    'build_sha256':sha(directory / 'build.json'),
                    'launcher_sha256':sha(ROOT / 'scripts/mr09_local_compare_run.py'),
                    'model_sha256':MODEL_SHA,
                    'runtime_artifact_ledger_sha256':sha(directory / 'runtime-artifacts.json'),
                    'preflight_file':f'H1-r{repetition}-preflight.json'}
        if any(record.get(key) != value for key,value in expected.items()):
            raise ValueError('cohort identity drift')
        preflight = directory / expected['preflight_file']
        if sha(preflight) != record['preflight_sha256']:
            raise ValueError('preflight bytes drift')
        screen = read_json(preflight)
        started, finished = [datetime.fromisoformat(record[key]) for key in ('started_utc','finished_utc')]
        validate_screen(screen, frozen, started)
        if not 0 <= (finished-started).total_seconds() <= 90:
            raise ValueError('native duration outside bound')
        if previous_finished is not None and datetime.fromisoformat(screen['observed_utc']) <= previous_finished:
            raise ValueError('serial cohort chronology drift')
        previous_finished = finished
        for key in ('driver_preflight_csv','driver_csv'):
            matching_driver(record[key])
        values = validate_h1(record)
        if values != record['native_validation']:
            raise ValueError('native validation receipt drift')
        interval = values['native_self_byte_interval']
        live = values['exact_admitted_live_buffer_bytes']
        error = error_interval(estimate, interval)
        observations.append({'file':path.name,'sha256':sha(path),'started_utc':record['started_utc'],
                             'finished_utc':record['finished_utc'], **values,
                             'predicted_managed_device_bytes':estimate,
                             'primary_error_interval':error,
                             'corroborating_ledger_signed_error_bytes':estimate-live,
                             'corroborating_ledger_signed_relative_percent_exact':str(Fraction(100*(estimate-live),live))})
    ledgers = [row['exact_admitted_live_buffer_bytes'] for row in observations]
    return {'classification':'one prospective H1 configuration, three descriptive supplemental comparisons; receiving acceptance pending',
            'metric':'managed_device_buffers_snapshot','configuration_count':1,'fresh_process_observations':3,
            'technical_matched_pairs':3,'accepted_pairs':0,'whole_runtime_peak_pairs':0,
            'predicted_managed_device_bytes':estimate,'observations':observations,
            'exact_ledger_live_bytes_min_median_max':[min(ledgers),statistics.median(ledgers),max(ledgers)],
            'tolerance':None,'fit_verdict':None,
            'limits':['instrumented initialization only; host buffers and opaque CUDA/library/context memory excluded',
                      'native self interval is primary; exact ledger is corroboration',
                      'three repetitions of one configuration do not establish universal bounds',
                      'experimental project derivative; no accuracy claim for unmodified upstream release',
                      'no inference, whole-runtime peaks, new named-owner acceptance or ResourceEstimate']}


if __name__ == '__main__':
    print(json.dumps(summarize(), indent=2, allow_nan=False))
