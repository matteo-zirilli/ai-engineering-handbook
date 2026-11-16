"""apibook — small helpers shared by the chapter of Part VI.

* `setup()` applies the figure style of Part III (`ml/mlbook.py`).
* `write(name, code)` saves a source file in a private temporary directory
  (``WORK``), which is on ``sys.path`` so that the chapter can import it.
* `server(module, ...)` starts a real HTTP server (uvicorn, in a separate
  process) on a free port of ``127.0.0.1`` and stops it at the end of a
  ``with`` block; used where an in-process ``TestClient`` is not enough
  (sockets, load tests, curl).
* `mask(text)` removes the temporary directory and port numbers from outputs.

Everything runs on the local machine: no public test service is contacted.
Cells run with the chapter's folder (`rest/`) as working directory.
"""
from __future__ import annotations

import contextlib
import os
import re
import socket
import subprocess
import sys
import tempfile
import textwrap
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORK = Path(tempfile.mkdtemp(prefix="apibook-"))
sys.path.insert(0, str(WORK))
COLORS = None


def setup() -> None:
    """Seed, display options and figure style (as in Parts III–V)."""
    global COLORS
    sys.path.insert(0, str(ROOT / "ml"))
    import mlbook  # noqa: E402
    mlbook.setup()
    COLORS = mlbook.COLORS


def write(name: str, code: str) -> Path:
    """Write a source file into WORK (importable as a module)."""
    p = WORK / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(code).strip("\n") + "\n", encoding="utf-8")
    sys.modules.pop(Path(name).stem, None)          # a rewritten module is re-imported
    return p


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def wait_port(port: int, timeout: float = 20) -> None:
    end = time.time() + timeout
    while time.time() < end:
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.05)
    raise RuntimeError(f"nothing listening on port {port}")


@contextlib.contextmanager
def server(app: str, *, port: int | None = None, workers: int = 1, env: dict | None = None,
           cmd: list[str] | None = None):
    """Run ``uvicorn <app>`` (e.g. ``"crud:app"`` for WORK/crud.py) and yield its base URL.

    With ``cmd`` a different command is run instead (``{port}`` is substituted)."""
    port = port or free_port()
    full_env = dict(os.environ, **(env or {}))
    full_env["PYTHONPATH"] = str(WORK) + os.pathsep + full_env.get("PYTHONPATH", "")
    if cmd is None:
        cmd = [sys.executable, "-m", "uvicorn", app, "--host", "127.0.0.1", "--port", str(port),
               "--log-level", "warning", "--workers", str(workers)]
    else:
        cmd = [c.replace("{port}", str(port)) for c in cmd]
    proc = subprocess.Popen(cmd, cwd=WORK, env=full_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True)
    try:
        wait_port(port)
        yield f"http://127.0.0.1:{port}"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


def mask(text: str) -> str:
    """Remove machine-specific paths and port numbers."""
    text = text.replace(str(WORK) + "/", "").replace(str(WORK), ".")
    text = re.sub(r"127\.0\.0\.1:\d{4,5}", "127.0.0.1:PORT", text)
    text = re.sub(r"localhost:\d{4,5}", "localhost:PORT", text)
    return text
