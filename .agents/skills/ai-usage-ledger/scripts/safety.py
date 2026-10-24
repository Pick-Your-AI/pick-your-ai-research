#!/usr/bin/env python3
"""
safety.py - input validation shared by the pipeline, renderers and scheduler.

Everything the skill executes or renders is built from operator-controlled files (manifest, config, branding).
Those files are trusted input, but a value with shell syntax, HTML or a stray newline must stay literal rather
than become a command or markup. This module is the single place that enforces it:

  check_path(value, what)          no NUL, newline or other control characters in a path or argument
  validate_ssh_host(host)          ssh target, remote_tmp and python interpreter grammar for SSH hosts
  validate_wsl_host(host)          distro name and python interpreter grammar for WSL hosts
  warn_if_writable(path)           POSIX: warn when a config file is group- or world-writable
  sanitize_branding(b, base_dir)   escaped text, validated colours/tokens/fonts, local-only logo, opt-in extra CSS
  CSP_META                         a restrictive Content-Security-Policy for every generated HTML page
  private_dir(path) / write_private(path, text) / private_file(path) / private_open(path) / private_copy(src, dst)
                                   0700 directories and 0600 files for everything the ledger keeps about its owner
  refuse_if_shared(path)           stop when a config file others can edit would be executed as configuration
  check_source_path(p)             grammar for a log file path that goes into an archive (local or remote)
  safe_relative(rel) / contained(root, dest) / check_host_name(name)
                                   archive layout: no '..', no absolute, realpath containment, plain host names

Standard library only.
"""
import contextlib
import html
import os
import re
import shutil
import stat
import sys

_CONTROL = re.compile(r"[\x00-\x1f\x7f]")
HOST_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
IS_POSIX = os.name != "nt"
ALLOW_SHARED_ENV = "AI_USAGE_LEDGER_ALLOW_SHARED"
SSH_TARGET_RE = re.compile(r"^(?:[A-Za-z0-9._-]+@)?[A-Za-z0-9][A-Za-z0-9._-]*$")
REMOTE_PATH_RE = re.compile(r"^/[A-Za-z0-9._/-]+$")
INTERPRETER_RE = re.compile(r"^(?:python3?(?:\.\d+)?|/[A-Za-z0-9._/-]+/python3?(?:\.\d+)?)$")
DISTRO_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
PYTHON_BASENAME_RE = re.compile(r"^python(?:3(?:\.\d+)?)?w?(?:\.exe)?$", re.IGNORECASE)
COLOR_RE = re.compile(r"^(?:#[0-9A-Fa-f]{3,8}|[A-Za-z]{3,30}|(?:rgb|rgba|hsl|hsla)\([0-9.,%\s]+\))$")
CSS_TOKEN_NAME_RE = re.compile(r"^[a-z0-9-]{1,40}$")
CSS_TOKEN_VALUE_RE = re.compile(r"^[A-Za-z0-9#%.,()\s'\"-]{1,120}$")
FONT_RE = re.compile(r"^[A-Za-z0-9 ,'\"-]{1,120}$")
_CSS_FORBIDDEN = re.compile(r"</|@import|url\s*\(|expression\s*\(|javascript:|behavior\s*:|-moz-binding", re.IGNORECASE)

# inline styles and scripts are what the self-contained pages are made of; nothing may be fetched from anywhere
CSP_META = '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; script-src \'unsafe-inline\'; img-src data:; font-src data:; connect-src \'none\'; frame-ancestors \'none\'; form-action \'none\'">'
CSP_META_EXTERNAL = '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\' https://fonts.googleapis.com; script-src \'unsafe-inline\'; img-src data: https:; font-src data: https://fonts.gstatic.com; connect-src \'none\'; frame-ancestors \'none\'; form-action \'none\'">'


class UnsafeValue(SystemExit):
    pass


def check_path(value, what="path"):
    """Reject control characters (NUL, newline, ...) in anything that becomes a path or a command argument."""
    if value is None:
        return value
    s = str(value)
    if _CONTROL.search(s):
        raise UnsafeValue("%s contains a control character and was refused: %r" % (what, s[:80]))
    if s.startswith("-") and what != "argument":
        raise UnsafeValue("%s must not start with '-' (looks like an option): %r" % (what, s[:80]))
    return s


def validate_ssh_host(host):
    """SSH hosts: the target, the remote scratch directory and the interpreter are passed to a remote shell."""
    target = str(host.get("ssh") or "")
    if not SSH_TARGET_RE.match(target):
        raise UnsafeValue("ssh target must be host or user@host without options or spaces: %r" % target)
    remote_tmp = str(host.get("remote_tmp") or "/tmp/ai-usage-ledger")
    if not REMOTE_PATH_RE.match(remote_tmp) or ".." in remote_tmp:
        raise UnsafeValue("remote_tmp must be an absolute path of [A-Za-z0-9._/-]: %r" % remote_tmp)
    python = str(host.get("python") or "python3")
    if not INTERPRETER_RE.match(python):
        raise UnsafeValue("python must be python3, python, python3.N or an absolute path to one: %r" % python)
    return target, remote_tmp, python


def validate_local_python(host, default):
    """local/share hosts launch this interpreter directly, so a manifest-supplied value selects the executable.
    The default comes from --python (this process), never from the manifest."""
    raw = host.get("python")
    if not raw:
        return default
    python = check_path(str(raw), "python")
    if not PYTHON_BASENAME_RE.match(os.path.basename(python)):
        raise UnsafeValue("python must name a python interpreter: %r" % python)
    if (os.sep in python or "/" in python) and not os.path.isfile(os.path.realpath(python)):
        raise UnsafeValue("python does not exist: %r" % python)
    return python


def validate_wsl_host(host):
    distro = str(host.get("distro") or "Ubuntu")
    if not DISTRO_RE.match(distro):
        raise UnsafeValue("WSL distro name is not plain: %r" % distro)
    python = str(host.get("python") or "python3")
    if not INTERPRETER_RE.match(python):
        raise UnsafeValue("python must be python3, python, python3.N or an absolute path to one: %r" % python)
    return distro, python


def warn_if_writable(path, log=None):
    """Manifests and configs are executable configuration; say so when others could edit them."""
    if os.name == "nt" or not path or not os.path.exists(path):
        return False
    try:
        mode = os.stat(path).st_mode
    except OSError:
        return False
    if mode & (stat.S_IWGRP | stat.S_IWOTH):
        msg = "warning: %s is group- or world-writable; anyone who can edit it controls what this skill runs" % path
        (log or (lambda m: sys.stderr.write(m + "\n")))(msg)
        return True
    return False


def private_dir(path):
    """Create (or fix) a directory that only its owner may read: 0700 on POSIX; NTFS inherits the profile ACL on Windows."""
    os.makedirs(path, exist_ok=True)
    if IS_POSIX:
        try:
            if os.stat(path).st_mode & 0o077:
                os.chmod(path, 0o700)
        except OSError:
            pass
    return path


def private_file(path):
    """0600 on POSIX for a file that already exists (SQLite databases, appended logs); no-op on Windows."""
    if IS_POSIX and path and os.path.exists(path):
        try:
            if os.stat(path).st_mode & 0o077:
                os.chmod(path, 0o600)
        except OSError:
            pass
    return path


def write_private(path, text, encoding="utf-8"):
    """Write a sensitive text file atomically with mode 0600 (owner read/write only)."""
    private_dir(os.path.dirname(os.path.abspath(path)) or ".")
    tmp = path + ".tmp-%d" % os.getpid()
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding=encoding, newline="\n") as fh:
        fh.write(text)
    os.replace(tmp, path)
    private_file(path)
    return path


@contextlib.contextmanager
def private_open(path, mode="w", encoding="utf-8", newline=None):
    """Open a sensitive output file with mode 0600 from the moment it is created; its directory becomes 0700.

    The mode passed to os.open only applies when the file is created, so private_file() also repairs an existing
    file that was opened with O_TRUNC and kept a wider mode. Use write_private() when the whole document is
    already in memory and it can be replaced atomically."""
    private_dir(os.path.dirname(os.path.abspath(path)) or ".")
    base = mode.replace("b", "").replace("t", "")
    flags = {"w": os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
             "a": os.O_WRONLY | os.O_CREAT | os.O_APPEND,
             "x": os.O_WRONLY | os.O_CREAT | os.O_EXCL}[base]
    fd = os.open(path, flags, 0o600)
    try:
        if "b" in mode:
            fh = os.fdopen(fd, "wb")
        else:
            fh = os.fdopen(fd, "w", encoding=encoding, newline=newline)
        with fh:
            yield fh
    finally:
        private_file(path)


def private_copy(src, dst):
    """Copy a sensitive file, then make the destination and its directory owner-only even over a permissive umask."""
    private_dir(os.path.dirname(os.path.abspath(dst)) or ".")
    shutil.copyfile(src, dst)
    private_file(dst)
    return dst


def refuse_if_shared(path, what="configuration"):
    """A config file that others can edit decides which hosts we reach and what we run: refuse unless overridden."""
    if not IS_POSIX or not path or not os.path.exists(path):
        return
    try:
        st = os.stat(path)
    except OSError:
        return
    if st.st_mode & (stat.S_IWGRP | stat.S_IWOTH) and not os.environ.get(ALLOW_SHARED_ENV):
        raise UnsafeValue("%s %s is group- or world-writable; fix it with chmod 600 (or set %s=1 to override)" % (what, path, ALLOW_SHARED_ENV))
    if hasattr(os, "geteuid") and st.st_uid not in (os.geteuid(), 0) and not os.environ.get(ALLOW_SHARED_ENV):
        raise UnsafeValue("%s %s is owned by another user (set %s=1 to override)" % (what, path, ALLOW_SHARED_ENV))


def check_host_name(name):
    if not HOST_NAME_RE.match(str(name or "")):
        raise UnsafeValue("host name must be plain [A-Za-z0-9._-]: %r" % str(name)[:60])
    return str(name)


def check_source_path(p, what="source path"):
    """A log file path that will be archived: absolute (POSIX, drive or UNC), no control characters, no option-looking start."""
    s = check_path(p, what)
    n = s.replace("\\", "/")
    if not (n.startswith("/") or re.match(r"^[A-Za-z]:/", n)):
        raise UnsafeValue("%s must be absolute: %r" % (what, s[:80]))
    if any(part == ".." for part in n.split("/")):
        raise UnsafeValue("%s must not contain '..': %r" % (what, s[:80]))
    return s


def safe_relative(rel):
    """An archive-relative path: no absolute prefix, no '..' component, no empty result."""
    r = str(rel).replace("\\", "/").strip("/")
    parts = [x for x in r.split("/") if x not in ("", ".")]
    if not parts or any(x == ".." for x in parts) or re.match(r"^[A-Za-z]:", parts[0]) and len(parts[0]) == 2 and False:
        raise UnsafeValue("unsafe relative path: %r" % str(rel)[:80])
    return "/".join(parts)


def contained(root, dest):
    """True when dest (after symlink resolution of its parent) stays inside root."""
    root_r = os.path.realpath(root)
    parent_r = os.path.realpath(os.path.dirname(dest))
    try:
        return os.path.commonpath([root_r, parent_r]) == root_r
    except ValueError:
        return False


def _text(v):
    return html.escape(str(v), quote=True) if v is not None else ""


def sanitize_branding(b, base_dir=None, logo_to_data_uri=None):
    """Return a branding dict safe to interpolate into HTML/CSS. Invalid values are dropped with a warning, never passed through."""
    b = dict(b or {})
    out = {}
    warnings = []
    for k in ("name", "eyebrow", "tagline", "contact", "footer"):
        if b.get(k):
            out[k] = _text(b[k])
    if b.get("accent"):
        if COLOR_RE.match(str(b["accent"]).strip()):
            out["accent"] = str(b["accent"]).strip()
        else:
            warnings.append("branding.accent is not a colour and was ignored: %r" % str(b["accent"])[:40])
    for k in ("font_display", "font_body", "font_mono"):
        if b.get(k):
            if FONT_RE.match(str(b[k])):
                out[k] = str(b[k])
            else:
                warnings.append("branding.%s is not a font family list and was ignored" % k)
    for theme in ("light", "dark"):
        tokens = {}
        for name, value in (b.get(theme) or {}).items():
            if CSS_TOKEN_NAME_RE.match(str(name)) and CSS_TOKEN_VALUE_RE.match(str(value)) and not _CSS_FORBIDDEN.search(str(value)):
                tokens[str(name)] = str(value)
            else:
                warnings.append("branding.%s.%s was ignored (not a plain CSS value)" % (theme, str(name)[:40]))
        if tokens:
            out[theme] = tokens
    allow_external = bool(b.get("allow_external_resources"))
    logo = b.get("logo")
    if logo:
        s = str(logo)
        if s.startswith("data:image/"):
            out["logo"] = s
        elif s.startswith(("http://", "https://")):
            if allow_external and s.startswith("https://"):
                out["logo"] = _text(s)
            else:
                warnings.append("branding.logo is a remote URL; set allow_external_resources: true to load it, or point it at a local file")
        else:
            uri = logo_to_data_uri(s, base_dir) if logo_to_data_uri else None
            if uri and str(uri).startswith("data:"):
                out["logo"] = uri
            else:
                warnings.append("branding.logo file not found and was ignored: %r" % s[:80])
    if b.get("google_fonts_url"):
        u = str(b["google_fonts_url"])
        if allow_external and u.startswith("https://fonts.googleapis.com/") and not _CONTROL.search(u):
            out["google_fonts_url"] = _text(u)
        else:
            warnings.append("branding.google_fonts_url ignored: pages are self-contained unless allow_external_resources is true and the URL is on fonts.googleapis.com")
    if b.get("extra_css"):
        css = str(b["extra_css"])
        if b.get("unsafe_extra_css") and not _CSS_FORBIDDEN.search(css):
            out["extra_css"] = css
        else:
            warnings.append("branding.extra_css ignored: set unsafe_extra_css: true and avoid </, @import, url(), expression()")
    out["allow_external_resources"] = allow_external
    out["_warnings"] = warnings
    for w in warnings:
        sys.stderr.write("branding: %s\n" % w)
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(sanitize_branding(json.loads(sys.stdin.read() or "{}")), indent=2))

# ---------------------------------------------------------------------------------------------- shared predicates
_CRED_BASENAMES = ("auth.json", ".credentials.json", "credentials.json", ".env", "id_rsa", "id_ed25519", "id_ecdsa", "id_dsa")
_CRED_PATTERNS = re.compile(r"(?:^|[^a-z])(?:token|secret|credential|password|passwd|apikey|api_key)(?:[^a-z]|$)|\.pem$|\.key$|\.p12$|\.pfx$|^\.env\.|^id_rsa|^id_ed25519", re.IGNORECASE)
_CRED_DIRS = {".ssh", ".aws", ".gnupg", ".azure", ".kube", ".docker"}
_ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]|\x1b[@-Z\\-_]|\x9b[0-?]*[ -/]*[@-~]")
_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")


def is_credential_file(path):
    """True for anything that looks like a credential, key or secret store: never archived, scanned or copied."""
    p = str(path or "").replace("\\", "/")
    base = p.rstrip("/").split("/")[-1]
    if base.lower() in _CRED_BASENAMES or _CRED_PATTERNS.search(base):
        return True
    return any(part in _CRED_DIRS for part in p.split("/")[:-1])


def clean_for_terminal(text, limit=4000):
    """Strip ANSI escape sequences and control characters (except newline and tab) from text that came from a
    subprocess, a remote host or a data file before it is printed, and cap its length."""
    s = str(text or "")
    s = _ANSI.sub("", s)
    s = _CTRL.sub("", s)
    if len(s) > limit:
        s = s[:limit] + "... [%d more characters]" % (len(s) - limit)
    return s


def validate_study_url(value):
    """An external study link may only be an absolute HTTPS URL; anything else (javascript:, data:, //host, http:,
    control characters) is refused and the caller must drop it."""
    from urllib.parse import urlparse
    v = str(value or "")
    if not v:
        return ""
    if v != v.strip() or _CONTROL.search(v):
        raise UnsafeValue("study_url contains whitespace or control characters")
    parsed = urlparse(v)
    if parsed.scheme.lower() != "https" or not parsed.netloc or v.startswith("//"):
        raise UnsafeValue("study_url must be an absolute https:// URL: %r" % v[:80])
    return v


_BROAD_DIRS = {"", "appdata", "roaming", "local", ".config", ".local", "share", "documents", "desktop", "downloads", "users", "home", "library", "application support"}


def check_generic_root(path):
    """A generic-sniffer root must point at one tool's own directory, never at a home, a drive root or a broad
    container such as AppData or .config, because every JSON file below it will be read."""
    p = str(path or "").replace("\\", "/").rstrip("/")
    check_path(p, "generic root")
    home = os.path.expanduser("~").replace("\\", "/").rstrip("/")
    norm = p.lower()
    if norm in ("", home.lower()) or re.fullmatch(r"[a-z]:", norm) or norm in ("/", "/home", "/users", "/root", "/mnt", "/srv", "/opt", "/var", "/tmp"):
        raise UnsafeValue("generic root %r is a home, drive or system root; point it at the tool's own directory" % p)
    parts = [x for x in norm.split("/") if x]
    last = parts[-1] if parts else ""
    if last in _BROAD_DIRS:
        raise UnsafeValue("generic root %r is a broad directory; point it at the tool's own directory below it" % p)
    return p

