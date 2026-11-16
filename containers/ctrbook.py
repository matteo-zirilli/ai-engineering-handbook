"""ctrbook — build and run the container examples of Part V (and of Part VI).

Every Dockerfile, shell command and Kubernetes manifest of Part V is executed
when the book is built, by a Python cell that calls the helpers below.  The
helpers

  1. write Dockerfiles, sources and manifests to a private temporary directory
     (``WORK``), one sub-directory per example;
  2. run ``docker build`` / ``docker run`` / ``kubectl`` there;
  3. print Markdown: the files as code blocks, the command, and its output;
  4. mask what changes from build to build or from machine to machine:
     container and image IDs and digests (replaced by stable placeholders such
     as ``<id-1>``, so that *equal* digests still look equal), temporary
     paths, durations and ages.

The cells are executed once by Quarto and the results stored in ``_freeze/``
like every other cell of the book.  Requirements for re-executing them: a
running Docker daemon, root (for ``unshare``/cgroups experiments) and, for the
Kubernetes section, k3s (see ``ensure_k3s``).  Registries are *not* needed:
the base images are built locally from an Ubuntu root filesystem
(``ensure_base_images``); the Dockerfiles shown to the reader take the base
image as a build argument (``ARG BASE=python:3.12-slim``) and the book passes
the local equivalent with ``--build-arg``.
"""
from __future__ import annotations

import os
import re
import shlex
import shutil
import subprocess
import tempfile
import textwrap
import time
from pathlib import Path

WORK = Path(tempfile.mkdtemp(prefix="ctrbook-"))
ROOT = Path(__file__).resolve().parent.parent

# Local stand-ins for the official images named in the Dockerfiles.
LOCAL = {
    "ubuntu": "local/ubuntu:noble",          # debootstrap minbase, imported
    "python": "local/python:3.12-slim",       # Ubuntu 24.04 + python3.12 + pip
    "gcc": "local/gcc:13",                    # Ubuntu 24.04 + build-essential (GCC 13)
}
BUILD_ARGS = {"BASE": LOCAL["python"], "BUILDER": LOCAL["gcc"]}

LAST = None  # CompletedProcess of the last command
LAST_BUILD_LOG = ""  # BuildKit log (plain progress) of the last build


# --------------------------------------------------------------------------- masking
_IDS: dict[str, str] = {}


def reset_ids() -> None:
    """Restart the numbering of masked IDs (call at the start of an example)."""
    _IDS.clear()


def _label_for(full: str) -> str:
    if full not in _IDS:
        _IDS[full] = f"<id-{len(_IDS) + 1}>"
    return _IDS[full]


def mask(text: str, keep=()) -> str:
    """Replace machine- and build-specific strings by stable placeholders."""
    keep = set(keep)
    text = text.replace(str(WORK) + "/", "").replace(str(WORK), ".")
    text = text.replace(str(Path.home()), "~")
    text = re.sub(r"/tmp/[\w.\-]+", "<tmp>", text)
    # 64-hex digests (image IDs, layer digests, container IDs)
    for h in dict.fromkeys(re.findall(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])", text)):  # first-appearance order
        if h not in keep:
            text = text.replace(h, _label_for(h))
    # short (12-hex) IDs: the same placeholder as the full digest they abbreviate
    def short(m):
        s = m.group(0)
        if any(k.startswith(s) for k in keep):
            return s
        for full, lab in _IDS.items():
            if full.startswith(s):
                return lab
        return _label_for(s)
    text = re.sub(r"(?<![0-9a-f<\-])[0-9a-f]{12}(?![0-9a-f>])", short, text)
    # durations and ages printed by docker / kubectl
    text = re.sub(r"\b\d+(\.\d+)?(ms|s)\b(?=\s|$|\)|,)", "<t>", text)
    text = re.sub(r"\b(Up|Exited \(\d+\)) [\w ]+? ago\b", r"\1 <t> ago", text)
    return text


# --------------------------------------------------------------------------- markdown
def _dedent(code: str) -> str:
    return textwrap.dedent(code).strip("\n") + "\n"


def _fence(body: str, cls: str = "", attrs: str = "") -> str:
    ticks = "````" if "```" in body else "```"
    head = ticks
    if cls or attrs:
        head += "{" + " ".join(x for x in (cls, attrs) if x) + "}"
    return f"{head}\n{body.rstrip()}\n{ticks}\n"


def _output_block(body: str, kind: str = "stdout") -> str:
    return f"::: {{.cell-output .cell-output-{kind}}}\n" + _fence(body) + ":::\n"


_LANG = {"Dockerfile": "dockerfile", ".py": "python", ".yaml": "yaml", ".yml": "yaml",
         ".txt": "default", ".json": "json", ".cpp": "cpp", ".c": "c", ".sh": "bash",
         ".dockerignore": "default", ".toml": "toml", ".csv": "default"}


def _lang(name: str) -> str:
    base = Path(name).name
    if base.startswith("Dockerfile"):
        return "dockerfile"
    if base == ".dockerignore":
        return "default"
    return _LANG.get(Path(name).suffix, "default")


# --------------------------------------------------------------------------- files
def project(name: str) -> Path:
    """A fresh example directory WORK/name (emptied if it exists)."""
    d = WORK / name
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    return d


def write(directory: Path | str, name: str, content: str | bytes) -> Path:
    """Write a file in an example directory without showing it."""
    d = WORK / directory if isinstance(directory, str) else directory
    p = d / name
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        p.write_bytes(content)
    else:
        p.write_text(_dedent(content), encoding="utf-8")
    return p


def show(directory: Path | str, name: str, content: str | None = None, *, title: bool = True,
         lang: str | None = None) -> None:
    """Write (if content is given) and print a file as a code block with its name."""
    d = WORK / directory if isinstance(directory, str) else directory
    if content is not None:
        write(d, name, content)
    body = (d / name).read_text(encoding="utf-8")
    attrs = f'filename="{name}"' if title else ""
    print(_fence(body, "." + (lang or _lang(name)), attrs))


def files(directory: Path | str, mapping: dict[str, str], *, hide=()) -> None:
    """Write several files and show those not listed in ``hide``."""
    for name, content in mapping.items():
        if name in hide:
            write(directory, name, content)
        else:
            show(directory, name, content)


# --------------------------------------------------------------------------- commands
def run(cmd: str, *, cwd: Path | str | None = None, timeout: float = 600, env=None,
        input: str | None = None) -> subprocess.CompletedProcess:
    """Run a shell command (bash) silently; return the CompletedProcess."""
    d = (WORK / cwd if isinstance(cwd, str) else cwd) if cwd is not None else WORK
    full_env = dict(os.environ, **(env or {}))
    proc = subprocess.run(cmd, shell=True, cwd=d, capture_output=True, text=True,
                          timeout=timeout, env=full_env, executable="/bin/bash", input=input)
    global LAST
    LAST = proc
    return proc


def sh(cmd: str, *, cwd: Path | str | None = None, shown: str | None = None, show_cmd: bool = True,
       max_lines: int | None = None, filter_fn=None, timeout: float = 600, keep=(),
       env=None, status: bool = True, input: str | None = None, check: bool = False) -> None:
    """Run a command and print it (as ``$ cmd``) with its masked output."""
    proc = run(cmd, cwd=cwd, timeout=timeout, env=env, input=input)
    out = mask(proc.stdout + proc.stderr, keep=keep)
    if filter_fn:
        out = "\n".join(l for l in out.splitlines() if filter_fn(l))
    if max_lines is not None:
        lines = out.splitlines()
        if len(lines) > max_lines:
            out = "\n".join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} more lines)"
    if status and proc.returncode != 0:
        out = out.rstrip("\n") + f"\n[exit status {proc.returncode}]"
    if show_cmd:
        print(_fence("$ " + (shown or cmd), ".bash"))
    if out.strip():
        print(_output_block(out))
    if check and proc.returncode != 0:
        raise RuntimeError(f"command failed ({proc.returncode}): {cmd}\n{proc.stderr}")
    return None


# --------------------------------------------------------------------------- docker build
_STEP = re.compile(r"^#(\d+) \[(?:(?P<stage>[\w\-.]+) )?(?P<i>\d+)/(?P<n>\d+)\] (?P<instr>.*)$")


def build(directory: Path | str, tag: str, *, args: dict | None = None, extra: str = "",
          show_cmd: bool = True, table: bool = True, dockerfile: str | None = None,
          shown_args: bool = False, expect_error: bool = False, timeout: float = 1800):
    """``docker build`` an example directory and print, per Dockerfile step,
    whether it was rebuilt or taken from the cache.  Returns
    ``(seconds, steps)`` where steps is a list of ``(instruction, cached)``.

    Base images are passed with ``--build-arg`` (local stand-ins); the command
    shown to the reader omits them unless ``shown_args`` is true.
    """
    d = WORK / directory if isinstance(directory, str) else directory
    a = dict(BUILD_ARGS)
    a.update(args or {})
    text = (d / (dockerfile or "Dockerfile")).read_text()
    used = {k: v for k, v in a.items() if re.search(rf"^\s*ARG\s+{k}\b", text, re.M)}
    argstr = " ".join(f"--build-arg {k}={shlex.quote(v)}" for k, v in used.items())
    fflag = f"-f {dockerfile} " if dockerfile else ""
    cmd = f"docker build --progress=plain {fflag}{argstr} {extra} -t {tag} ."
    t0 = time.perf_counter()
    proc = run(cmd, cwd=d, timeout=timeout)
    secs = time.perf_counter() - t0
    log = proc.stderr
    global LAST_BUILD_LOG
    LAST_BUILD_LOG = log
    if proc.returncode != 0 and not expect_error:
        raise RuntimeError("docker build failed:\n" + log[-3000:])
    steps: dict[str, list] = {}
    order, stages = [], []
    for line in log.splitlines():
        m = _STEP.match(line)
        if m:
            key = m.group(1)
            instr = m.group("instr")
            if instr.startswith(("FROM", "ARG")) or "internal" in line:
                continue
            if key not in steps:
                stage = m.group("stage") or ""
                if stage not in stages:
                    stages.append(stage)
                steps[key] = [f"{stage + ' ' if stage and stage != 'stage-0' else ''}{instr}", False,
                              (stages.index(stage), int(m.group("i")))]
                order.append(key)
        else:
            mm = re.match(r"^#(\d+) CACHED", line)
            if mm and mm.group(1) in steps:
                steps[mm.group(1)][1] = True
    order.sort(key=lambda k: steps[k][2])
    result = [(steps[k][0], steps[k][1]) for k in order]
    if show_cmd:
        shown = f"docker build {fflag}{argstr + ' ' if shown_args else ''}{extra + ' ' if extra else ''}-t {tag} ."
        shown = re.sub(r"\s+", " ", shown)
        print(_fence("$ " + shown, ".bash"))
    if table and result:
        rows = "\n".join(f"| `{_short(i)}` | {'cached' if c else '**rebuilt**'} |" for i, c in result)
        print("\n| Step | Result |\n|---|---|\n" + rows + "\n")
    if expect_error and proc.returncode != 0:
        err = [l for l in log.splitlines() if "ERROR" in l or "error" in l.lower()][-3:]
        print(_output_block(mask("\n".join(err)), "stderr"))
    return secs, result


def _short(instr: str, n: int = 70) -> str:
    instr = instr.replace("|", "\\|").replace("`", "'")
    return instr if len(instr) <= n else instr[: n - 1] + "…"


def quiet(cmd: str, **kw) -> None:
    """Run a command (typically a clean-up) and return nothing, so that a cell ending with it prints nothing."""
    run(cmd, **kw)


def image_size(tag: str) -> int:
    """Size in bytes of an image (uncompressed content, as reported by docker)."""
    out = run(f"docker image inspect -f '{{{{.Size}}}}' {tag}").stdout.strip()
    return int(out)


def image_id(tag: str) -> str:
    return run(f"docker image inspect -f '{{{{.Id}}}}' {tag}").stdout.strip()


def rm_images(*tags: str) -> None:
    run("docker rmi -f " + " ".join(tags) + " >/dev/null 2>&1")


def prune_cache() -> None:
    """Empty the BuildKit cache (so that a measurement starts cold)."""
    run("docker builder prune -af >/dev/null 2>&1")


# --------------------------------------------------------------------------- environment
def ensure_docker() -> None:
    if run("docker info >/dev/null 2>&1").returncode == 0:
        return
    subprocess.Popen("dockerd >/tmp/dockerd.log 2>&1", shell=True)
    for _ in range(60):
        time.sleep(1)
        if run("docker info >/dev/null 2>&1").returncode == 0:
            return
    raise RuntimeError("dockerd did not start")


_SOURCES = " ".join(shlex.quote(f"deb http://archive.ubuntu.com/ubuntu {s} main universe")
                    for s in ("noble", "noble-updates", "noble-security"))


def ensure_base_images() -> None:
    """Build the local stand-ins of the official base images if missing."""
    ensure_docker()
    have = set(run("docker images --format '{{.Repository}}:{{.Tag}}'").stdout.split())
    if LOCAL["ubuntu"] not in have:
        rootfs = Path(tempfile.mkdtemp(prefix="rootfs-")) / "rootfs"
        if shutil.which("debootstrap") is None:
            run("apt-get update -qq && apt-get install -y -qq debootstrap", timeout=900)
        p = run(f"debootstrap --variant=minbase noble {rootfs} http://archive.ubuntu.com/ubuntu/",
                timeout=1800)
        if p.returncode:
            raise RuntimeError(p.stderr[-2000:])
        run(f"tar -C {rootfs} -c . | docker import - {LOCAL['ubuntu']}", timeout=900)
        shutil.rmtree(rootfs.parent, ignore_errors=True)
    if LOCAL["python"] not in have:
        d = project("_base_python")
        # The sandbox re-terminates TLS with its own CA: the local stand-in trusts it
        # (verification stays on), so that pip can reach PyPI inside builds.
        ca = Path.home() / ".ccr" / "ca-bundle.crt"
        write(d, "sandbox-ca.crt", ca.read_text() if ca.exists() else "")
        write(d, "Dockerfile", f"""
            FROM {LOCAL['ubuntu']}
            RUN printf '%s\\n' {_SOURCES} > /etc/apt/sources.list
            ENV DEBIAN_FRONTEND=noninteractive PIP_ROOT_USER_ACTION=ignore PIP_DISABLE_PIP_VERSION_CHECK=1
            COPY sandbox-ca.crt /etc/ssl/sandbox-ca-bundle.crt
            ENV PIP_CERT=/etc/ssl/sandbox-ca-bundle.crt
            RUN apt-get update -qq && apt-get install -y -qq --no-install-recommends python3 python3-pip python3-venv ca-certificates \\
             && ln -s /usr/bin/python3 /usr/local/bin/python \\
             && rm -f /usr/lib/python3*/EXTERNALLY-MANAGED && rm -rf /var/lib/apt/lists/*
            CMD ["python3"]
            """)
        p = run(f"docker build -q -t {LOCAL['python']} .", cwd=d, timeout=1800)
        if p.returncode:
            raise RuntimeError(p.stderr[-2000:])
    if LOCAL["gcc"] not in have:
        d = project("_base_gcc")
        write(d, "Dockerfile", f"""
            FROM {LOCAL['ubuntu']}
            RUN printf '%s\\n' {_SOURCES} > /etc/apt/sources.list
            ENV DEBIAN_FRONTEND=noninteractive
            RUN apt-get update -qq && apt-get install -y -qq --no-install-recommends g++ libc6-dev \\
             && rm -rf /var/lib/apt/lists/*
            """)
        p = run(f"docker build -q -t {LOCAL['gcc']} .", cwd=d, timeout=1800)
        if p.returncode:
            raise RuntimeError(p.stderr[-2000:])


# --------------------------------------------------------------------------- kubernetes
# Sandbox-specific: allow cgroup v1, and relax the eviction thresholds (the build
# machine's disk reports far more capacity than is available, so the default
# "less than 10-15 % free" rule would taint the node with disk pressure).
K3S_FLAGS = ("--disable traefik,metrics-server,servicelb --write-kubeconfig-mode 644 "
             "--kubelet-arg=fail-cgroupv1=false "
             "'--kubelet-arg=eviction-hard=nodefs.available<1%,imagefs.available<1%,memory.available<100Mi' "
             "--kubelet-arg=image-gc-high-threshold=100 --kubelet-arg=image-gc-low-threshold=99")
_NO_PROXY = "127.0.0.1,localhost,192.0.2.0/24,10.42.0.0/16,10.43.0.0/16,.svc,.cluster.local"
K8S_ENV = {"NO_PROXY": _NO_PROXY, "no_proxy": _NO_PROXY}


def ensure_k3s() -> None:
    """Start a single-node k3s cluster (offline images) if it is not running.

    Two sandbox-specific settings: cgroup v1 must be allowed explicitly
    (``fail-cgroupv1=false``), and containerd must not try to *lower* the OOM
    score of pods (``restrict_oom_score_adj``), which the sandbox forbids.
    """
    if run("k3s kubectl get --raw /readyz", env=K8S_ENV).stdout.strip() == "ok":
        return
    tmpl = Path("/var/lib/rancher/k3s/agent/etc/containerd/config-v3.toml.tmpl")
    if not tmpl.exists():
        raise RuntimeError("start k3s once by hand and create config-v3.toml.tmpl "
                           "with restrict_oom_score_adj = true (see CLAUDE.md)")
    env = dict(os.environ, **K8S_ENV)
    subprocess.Popen(f"nohup k3s server {K3S_FLAGS} >/tmp/k3s.log 2>&1", shell=True, env=env)
    for _ in range(180):
        time.sleep(2)
        if "Ready" in run("k3s kubectl get nodes --no-headers", env=K8S_ENV).stdout and \
                "Running" in run("k3s kubectl -n kube-system get pods --no-headers", env=K8S_ENV).stdout:
            time.sleep(5)
            return
    raise RuntimeError("k3s did not become ready")


def kube(args: str, *, shown: str | None = None, **kw) -> None:
    """Run ``kubectl <args>`` (through k3s) and print it like ``sh``."""
    sh(f"k3s kubectl {args}", shown=shown or f"kubectl {args}", env=K8S_ENV, **kw)


def kube_run(args: str, **kw) -> subprocess.CompletedProcess:
    return run(f"k3s kubectl {args}", env=K8S_ENV, **kw)


def load_image(tag: str) -> None:
    """Copy an image from Docker into the cluster's containerd (no registry)."""
    p = run(f"docker save {tag} | k3s ctr images import -", timeout=900)
    if p.returncode:
        raise RuntimeError(p.stderr[-2000:])


def machine() -> str:
    """One line describing the machine, for measurements."""
    cpus = os.cpu_count()
    mem = int(run("free -g | awk '/Mem:/{print $2}'").stdout.strip() or 0)
    cg = "v2" if Path("/sys/fs/cgroup/cgroup.controllers").exists() else "v1"
    kern = os.uname().release.split("-")[0]
    return f"a {cpus}-CPU virtual machine with {mem} GB of RAM, Linux {kern}, cgroup {cg}"


# --------------------------------------------------------------------------- chapter setup
COLORS = None


def setup() -> None:
    """Figure style of Part III and the local base images."""
    import sys
    global COLORS
    sys.path.insert(0, str(ROOT / "ml"))
    import mlbook  # noqa: E402
    mlbook.setup()
    COLORS = mlbook.COLORS
    ensure_base_images()
    run("docker builder prune -af >/dev/null 2>&1")    # keep the disk bounded across renders
    run("docker container prune -f >/dev/null 2>&1")


# --------------------------------------------------------------------------- the running example
# A small "model in production": a classifier of the wine data (scikit-learn,
# UCI, CC BY 4.0) trained at build time, served over HTTP with the standard
# library only (Part VI replaces this server with FastAPI), and usable in batch.
REQUIREMENTS = """\
numpy==2.5.3
scipy==1.18.1
scikit-learn==1.9.1
joblib==1.6.0
threadpoolctl==3.7.0
"""

TRAIN_PY = '''\
"""Train the wine classifier; save the model and its metadata."""
import json
import sys

import joblib
from sklearn.datasets import load_wine
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

version = sys.argv[1] if len(sys.argv) > 1 else "1"
X, y = load_wine(return_X_y=True)                      # ships with scikit-learn
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
cv = cross_val_score(model, X, y, cv=5).mean()           # scaler inside the pipeline: no leakage
model.fit(X, y)
joblib.dump(model, "model.joblib")
with open("model.json", "w") as f:
    json.dump({"model": "wine-logreg", "version": version,
               "cv_accuracy": round(float(cv), 4), "n_features": X.shape[1]}, f)
print(f"trained version {version}: 5-fold CV accuracy {cv:.3f}")
'''

SERVE_PY = '''\
"""Serve the model over HTTP with the standard library (GET /health, GET /version, POST /predict)."""
import json
import os
import signal
import socket
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import joblib

time.sleep(float(os.environ.get("STARTUP_DELAY", "0")))  # simulate loading a large model
MODEL = joblib.load("model.joblib")
with open("model.json") as f:
    META = json.load(f)


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"status": "ok", "host": socket.gethostname()})
        elif self.path == "/version":
            self._send(200, META)
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/predict":
            return self._send(404, {"error": "not found"})
        try:
            rows = json.loads(self.rfile.read(int(self.headers["Content-Length"])))["features"]
            classes = MODEL.predict(rows).tolist()
        except Exception as err:                       # bad JSON, wrong shape, ...
            return self._send(400, {"error": str(err)})
        self._send(200, {"classes": classes, "version": META["version"]})

    def log_message(self, *args):                       # keep the logs quiet
        pass


signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))  # stop promptly on docker stop
print(f"serving model version {META['version']} on port 8000", flush=True)
ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "8000"))), Handler).serve_forever()
'''

SCORE_PY = '''\
"""Batch scoring: read every CSV in IN_DIR (13 numeric columns), write predictions to OUT_DIR."""
import csv
import os
from pathlib import Path

import joblib

model = joblib.load("model.joblib")
src, dst = Path(os.environ.get("IN_DIR", "/data/in")), Path(os.environ.get("OUT_DIR", "/data/out"))
dst.mkdir(parents=True, exist_ok=True)
for path in sorted(src.glob("*.csv")):
    with path.open() as f:
        rows = [[float(v) for v in r] for r in csv.reader(f)]
    preds = model.predict(rows)
    with (dst / path.name).open("w", newline="") as f:
        csv.writer(f).writerows([[int(p)] for p in preds])
    print(f"{path.name}: {len(rows)} rows scored")
'''

DOCKERFILE_SCORING = """\
ARG BASE=python:3.12-slim
FROM ${BASE}
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY train.py .
RUN python train.py
COPY serve.py score.py ./
EXPOSE 8000
CMD ["python", "serve.py"]
"""


def scoring(name: str, *, dockerfile: str = DOCKERFILE_SCORING, version: str | None = None,
            show_files=()) -> Path:
    """Create the example directory of the scoring service; show the listed files."""
    d = project(name)
    train = TRAIN_PY if version is None else TRAIN_PY.replace('else "1"', f'else "{version}"')
    content = {"requirements.txt": REQUIREMENTS, "train.py": train, "serve.py": SERVE_PY,
               "score.py": SCORE_PY, "Dockerfile": dockerfile}
    for n, c in content.items():
        (d / n).write_text(c if n != "Dockerfile" else _dedent(c), encoding="utf-8")
        if n in show_files:
            show(d, n)
    return d


def layers(tag: str) -> list[dict]:
    """The layers of an image, read from ``docker save`` (OCI layout): for each,
    the instruction that created it, the compressed size of the blob and the
    size of the uncompressed tar (what the layer adds to the filesystem)."""
    import gzip
    import json as _json
    import tarfile
    out = Path(tempfile.mkdtemp(prefix="save-", dir=WORK))
    p = run(f"docker save {tag} | tar -C {out} -x", timeout=900)
    if p.returncode:
        raise RuntimeError(p.stderr)

    def blob(d):
        return out / "blobs" / d.replace(":", "/")
    m = _json.loads((out / "index.json").read_text())
    while "manifests" in m:
        m = _json.loads(blob(m["manifests"][0]["digest"]).read_text())
    cfg = _json.loads(blob(m["config"]["digest"]).read_text())
    hist = [h for h in cfg["history"] if not h.get("empty_layer")]
    res = []
    for h, l in zip(hist, m["layers"]):
        raw = blob(l["digest"]).read_bytes()
        data = gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw
        res.append({"created_by": h.get("created_by", "(base image)").replace("/bin/sh -c ", ""),
                    "compressed": len(raw), "size": len(data), "digest": l["digest"]})
    shutil.rmtree(out, ignore_errors=True)
    return res
