"""opsbook — helpers shared by the chapters of Part VII (MLOps).

* `setup()` applies the figure style of Part III (`ml/mlbook.py`) and seeds NumPy.
* `make_posts(n, ...)` generates short, synthetic social-media posts with a
  sentiment label (0 = negative, 1 = neutral, 2 = positive — the encoding of
  the model used in the project). Every kind of shift used in the part can be
  switched on in a controlled way: class priors (label shift), topics, length,
  emoji rate and unseen slang (covariate shift), and words that change meaning
  (concept shift). No real person's text is used.
* `train_model(texts, labels)` fits the small local model of the theory
  chapters: TF-IDF (word uni- and bigrams) + multinomial logistic regression.
* `write`, `show`, `sh`, `run`, `mask`: files in a private working directory
  (``WORK``) and commands whose output is printed without machine-specific
  paths, ports or durations.
* `server(...)`: a real uvicorn process on a free loopback port.
* `tool(name)`: path of an external binary (Prometheus, Alertmanager,
  actionlint, act, the CNCF Distribution registry), downloaded once from the
  project's GitHub release.
* `SERVICE_APP`, `make_service()`: the prediction service of the serving
  chapter, reused by the following chapters.

Cells run with the chapter's folder (`mlops/`) as working directory.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import os
import re
import shutil
import socket
import subprocess
import sys
import tarfile
import tempfile
import textwrap
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
WORK = Path(tempfile.mkdtemp(prefix="opsbook-"))
sys.path.insert(0, str(WORK))
COLORS: list[str] = []
LABELS = ["negative", "neutral", "positive"]

# --------------------------------------------------------------------------- style


def setup() -> None:
    """Seed, display options and figure style (as in Parts III–VI)."""
    global COLORS
    sys.path.insert(0, str(ROOT / "ml"))
    import mlbook  # noqa: E402

    mlbook.setup()
    COLORS[:] = mlbook.COLORS
    np.random.seed(0)


# --------------------------------------------------------------------------- data
TOPICS = ["the new phone", "the delivery", "customer service", "the app update", "the battery",
          "the price", "the camera", "the support team", "the checkout", "the subscription"]
NEW_TOPICS = ["the outage", "the recall", "the data breach", "the price increase"]
POS = ["love", "great", "amazing", "excellent", "fantastic", "happy", "awesome", "perfect",
       "brilliant", "smooth", "fast", "helpful", "impressed", "recommend", "cheap"]
NEG = ["hate", "terrible", "awful", "broken", "slow", "useless", "disappointed", "angry",
       "worst", "buggy", "rude", "expensive", "refund", "crashes", "annoying"]
FILLER = ["today", "just", "got", "this", "my", "with", "about", "after", "week", "order",
          "using", "again", "still", "really", "so", "honestly", "now", "here", "new", "it"]
NEUTRAL = ["arrived", "tried", "opened", "installed", "checked", "ordered", "called", "updated",
           "looked at", "read about", "asked about", "waiting for"]
STATES = ["here", "on its way", "the same", "out now", "back", "scheduled", "on sale", "in the news"]
SLANG = ["mid", "bussin", "lowkey", "no cap", "slaps", "cooked", "rizz", "sus"]
EMOJI = {0: ["😡", "👎", "😞"], 1: ["🤔", "📦", "📱"], 2: ["😍", "👍", "🙂"]}


def make_posts(n: int, *, prior=(0.3, 0.4, 0.3), seed: int = 0, topics: list[str] | None = None,
               emoji_rate: float = 0.25, slang_rate: float = 0.0, extra_words: int = 0,
               swap: dict[str, int] | None = None, noise: float = 0.06,
               negation_rate: float = 0.12) -> pd.DataFrame:
    """Generate `n` labelled synthetic posts.

    prior          class probabilities (negative, neutral, positive)        -> label shift
    topics         list of topics to draw from (default TOPICS)             -> covariate shift
    emoji_rate     probability that a post ends with an emoji               -> covariate shift
    slang_rate     probability of each post containing an unseen slang word -> covariate shift
    extra_words    extra filler words per post (longer posts)               -> covariate shift
    swap           {word: class}: the word now expresses that class         -> concept shift
    noise          probability that the annotator's label is a random other class
    negation_rate  probability that a polar post is phrased with "not" + opposite word
    """
    rng = np.random.default_rng(seed)
    topics = topics or TOPICS
    pos, neg = list(POS), list(NEG)
    if swap:                                  # a word moves to the other lexicon
        for w, c in swap.items():
            if w in pos:
                pos.remove(w)
            if w in neg:
                neg.remove(w)
            (pos if c == 2 else neg).append(w)
    y = rng.choice(3, size=n, p=np.asarray(prior) / np.sum(prior))
    texts = []
    for c in y:
        topic = topics[rng.integers(len(topics))]
        fill = list(rng.choice(FILLER, size=rng.integers(1, 4) + extra_words))
        if c == 1:
            if rng.random() < 0.5:
                words = [NEUTRAL[rng.integers(len(NEUTRAL))], topic]
            else:
                words = [topic, "is", STATES[rng.integers(len(STATES))]]
            if rng.random() < 0.15:           # a weak polar word in a neutral post
                words.append((pos + neg)[rng.integers(len(pos) + len(neg))])
        else:
            same, other = (pos, neg) if c == 2 else (neg, pos)
            if rng.random() < negation_rate:  # "not awful" is positive, "not great" negative
                words = [topic, "is", "not", other[rng.integers(len(other))]]
            elif rng.random() < 0.6:
                k = rng.integers(1, 3)
                words = [topic, "is"] + list(rng.choice(same, size=k, replace=False))
            else:
                words = [same[rng.integers(len(same))], topic]
            if rng.random() < 0.15:           # mixed post: one word of the other polarity
                words += ["but", other[rng.integers(len(other))]]
        if rng.random() < slang_rate:
            words.insert(rng.integers(len(words) + 1), SLANG[rng.integers(len(SLANG))])
        post = " ".join(fill[: len(fill) // 2] + words + fill[len(fill) // 2:])
        if rng.random() < emoji_rate:
            post += " " + EMOJI[int(c)][rng.integers(3)]
        texts.append(post)
    flip = rng.random(n) < noise              # annotation noise
    y_obs = np.where(flip, (y + rng.integers(1, 3, size=n)) % 3, y)
    return pd.DataFrame({"text": texts, "label": y_obs.astype(int)})


def train_model(texts, labels, *, C: float = 4.0, ngram=(1, 2), seed: int = 0):
    """TF-IDF (uni+bigrams) + multinomial logistic regression: the local model of Part VII."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline

    model = make_pipeline(TfidfVectorizer(ngram_range=ngram, token_pattern=r"(?u)\b\w+\b|[^\w\s]"),
                          LogisticRegression(C=C, max_iter=2000, random_state=seed))
    return model.fit(list(texts), np.asarray(labels))


def sha256(data: bytes | str | Path) -> str:
    """SHA-256 of bytes, of a string (UTF-8) or of a file's content."""
    if isinstance(data, Path):
        data = data.read_bytes()
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()


# --------------------------------------------------------------------------- files and commands


def write(name: str | Path, content: str, *, base: Path | None = None) -> Path:
    """Write a file (dedented) under WORK (or `base`) and return its path."""
    p = (base or WORK) / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(content).strip("\n") + "\n", encoding="utf-8")
    sys.modules.pop(Path(name).stem, None)
    return p


_LANG = {".py": "python", ".yml": "yaml", ".yaml": "yaml", ".toml": "toml", ".json": "json",
         ".txt": "text", ".cfg": "ini", ".ini": "ini", ".md": "markdown", ".sh": "bash"}


def lang(name: str) -> str:
    n = Path(name).name
    if n.startswith("Dockerfile"):
        return "dockerfile"
    return _LANG.get(Path(n).suffix, "text")


def show(path: Path | str, *, title: str | None = None, base: Path | None = None) -> None:
    """Print a file as a fenced Markdown code block (for cells with `output: asis`)."""
    p = Path(path)
    if not p.is_absolute():
        p = (base or WORK) / p
    shown = title or mask(str(p.relative_to(base or WORK)) if p.is_relative_to(base or WORK) else p.name)
    body = p.read_text(encoding="utf-8").rstrip("\n")
    print(f"\n**`{shown}`**\n\n``` {{.{lang(p.name)}}}\n{body}\n```\n")


# Commands run without the build machine's personal Git configuration (signing keys,
# aliases) and without colours, so that outputs are the same on every machine.
CLEAN_ENV = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1", "NO_COLOR": "1",
             "PIP_DISABLE_PIP_VERSION_CHECK": "1", "PIP_ROOT_USER_ACTION": "ignore"}
LAST: subprocess.CompletedProcess | None = None


def run(cmd: str, *, cwd: Path | str | None = None, timeout: float = 900, env: dict | None = None,
        check: bool = False) -> subprocess.CompletedProcess:
    full_env = dict(os.environ, **CLEAN_ENV, **(env or {}))
    p = subprocess.run(cmd, shell=True, cwd=cwd or WORK, capture_output=True, text=True,
                       timeout=timeout, env=full_env, executable="/bin/bash")
    if check and p.returncode:
        raise RuntimeError(f"{cmd!r} failed ({p.returncode}):\n{p.stdout[-3000:]}\n{p.stderr[-3000:]}")
    return p


def sh(cmd: str, *, cwd: Path | str | None = None, shown: str | None = None, env: dict | None = None,
       timeout: float = 900, max_lines: int = 60, filt=None) -> None:
    """Run a command and print it with its (masked) output as Markdown (`output: asis`).

    The CompletedProcess is kept in `LAST` (nothing is returned, so that a cell ending
    with `sh(...)` does not print it)."""
    global LAST
    p = LAST = run(cmd, cwd=cwd, env=env, timeout=timeout)
    out = mask((p.stdout + p.stderr).rstrip("\n"))
    if filt:
        out = filt(out)
    lines = out.splitlines()
    if len(lines) > max_lines:
        lines = lines[: max_lines - 3] + [f"… ({len(lines) - max_lines + 3} more lines)"] + lines[-2:]
    status = "" if p.returncode == 0 else f"\n[exit status {p.returncode}]"
    print(f"\n``` {{.bash}}\n$ {shown or cmd}\n```\n\n```\n" + "\n".join(lines) + status + "\n```\n")


_DUR = re.compile(r"\b\d+(\.\d+)?(ms|s)\b")


def mask(text: str, durations: bool = False) -> str:
    """Remove machine-specific paths, ports, colour codes and (optionally) durations."""
    text = re.sub(r"\x1b\[[0-9;]*m", "", text)
    text = text.replace(str(WORK) + "/", "").replace(str(WORK), ".")
    text = re.sub(r"/tmp/[\w.\-/]+", "<tmp>", text)
    text = text.replace(str(Path.home()), "~")
    text = re.sub(r"127\.0\.0\.1:\d{4,5}", "127.0.0.1:PORT", text)
    text = re.sub(r"localhost:\d{4,5}", "localhost:PORT", text)
    if durations:
        text = _DUR.sub("<t>", text)
    return text


def project(name: str) -> Path:
    """A fresh empty directory under WORK."""
    d = WORK / name
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    return d


# --------------------------------------------------------------------------- servers


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def wait_port(port: int, timeout: float = 30) -> None:
    end = time.time() + timeout
    while time.time() < end:
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.05)
    raise RuntimeError(f"nothing listening on port {port}")


@contextlib.contextmanager
def server(app: str | None = None, *, cmd: list[str] | None = None, cwd: Path | None = None,
           port: int | None = None, env: dict | None = None, wait: bool = True):
    """Run ``uvicorn <app>`` (or `cmd`, with ``{port}`` substituted) and yield (base URL, process)."""
    port = port or free_port()
    full_env = dict(os.environ, **(env or {}))
    full_env["PYTHONPATH"] = str(cwd or WORK) + os.pathsep + full_env.get("PYTHONPATH", "")
    if cmd is None:
        cmd = [sys.executable, "-m", "uvicorn", app, "--host", "127.0.0.1", "--port", str(port),
               "--log-level", "warning"]
    else:
        cmd = [c.replace("{port}", str(port)) for c in cmd]
    proc = subprocess.Popen(cmd, cwd=cwd or WORK, env=full_env, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True)
    try:
        if wait:
            wait_port(port)
        yield f"http://127.0.0.1:{port}", proc
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


# --------------------------------------------------------------------------- external tools
TOOLS_DIR = Path(os.environ.get("OPSBOOK_TOOLS", Path.home() / ".cache" / "opsbook-tools"))
_TOOLS = {
    "prometheus": ("https://github.com/prometheus/prometheus/releases/download/v3.16.0/"
                   "prometheus-3.16.0.linux-amd64.tar.gz", "prometheus-3.16.0.linux-amd64/prometheus"),
    "promtool": ("https://github.com/prometheus/prometheus/releases/download/v3.16.0/"
                 "prometheus-3.16.0.linux-amd64.tar.gz", "prometheus-3.16.0.linux-amd64/promtool"),
    "alertmanager": ("https://github.com/prometheus/alertmanager/releases/download/v0.35.0/"
                     "alertmanager-0.35.0.linux-amd64.tar.gz", "alertmanager-0.35.0.linux-amd64/alertmanager"),
    "amtool": ("https://github.com/prometheus/alertmanager/releases/download/v0.35.0/"
               "alertmanager-0.35.0.linux-amd64.tar.gz", "alertmanager-0.35.0.linux-amd64/amtool"),
    "actionlint": ("https://github.com/rhysd/actionlint/releases/download/v1.7.12/"
                   "actionlint_1.7.12_linux_amd64.tar.gz", "actionlint"),
    "act": ("https://github.com/nektos/act/releases/download/v0.2.98/act_Linux_x86_64.tar.gz", "act"),
    "registry": ("https://github.com/distribution/distribution/releases/download/v3.1.2/"
                 "registry_3.1.2_linux_amd64.tar.gz", "registry"),
}


def tool(name: str) -> str:
    """Path of an external binary, downloaded once from its GitHub release."""
    url, member = _TOOLS[name]
    dest = TOOLS_DIR / member
    if not dest.exists():
        TOOLS_DIR.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url, timeout=600) as r:
            data = r.read()
        with tarfile.open(fileobj=io.BytesIO(data)) as tf:
            tf.extractall(TOOLS_DIR, filter="data")
    return str(dest)


# --------------------------------------------------------------------------- separate environments
VENVS_DIR = Path(os.environ.get("OPSBOOK_VENVS", Path.home() / ".cache" / "opsbook-venvs"))
VENV_SPECS = {
    # MLflow pulls in its own web stack: kept out of the book's kernel.
    "mlflow": (["mlflow==3.18.0", "scikit-learn==1.9.1", "pandas"], None),
    # Airflow must be installed with the constraint file of its release.
    # (with the tasks' own dependencies, as in a real deployment).
    "airflow": (["apache-airflow==3.4.0", "scikit-learn==1.9.1", "pandas", "numpy", "joblib"],
                "https://raw.githubusercontent.com/apache/airflow/constraints-3.4.0/constraints-3.13.txt"),
}


def venv_python(name: str) -> str:
    """Python interpreter of a separate virtual environment (created once, pinned)."""
    pkgs, constraints = VENV_SPECS[name]
    py = VENVS_DIR / name / "bin" / "python"
    if not py.exists():
        VENVS_DIR.mkdir(parents=True, exist_ok=True)
        run(f"{sys.executable} -m venv {VENVS_DIR / name}", check=True)
        extra = f"--constraint {constraints}" if constraints else ""
        run(f"{py} -m pip install -q {' '.join(pkgs)} {extra}", check=True, timeout=3600)
    return str(py)


# --------------------------------------------------------------------------- the running example
# The prediction service of @sec-ch-ops-serving, reused by the chapters on testing,
# deployment, CI/CD and monitoring.
SERVICE_APP = '''"""Sentiment service: the local model behind an HTTP API."""

import os
import time
from contextlib import asynccontextmanager
from typing import Annotated

import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, StringConstraints

LABELS = ["negative", "neutral", "positive"]  # index = the model's class id
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=280)]


class PredictRequest(BaseModel):
    texts: list[Text] = Field(min_length=1, max_length=64)


class Prediction(BaseModel):
    label: str
    label_id: int
    probabilities: dict[str, float]


class PredictResponse(BaseModel):
    model_version: str
    predictions: list[Prediction]


STATE: dict = {}
OBSERVERS: list = []  # callbacks f(texts, probabilities), e.g. to record metrics


@asynccontextmanager
async def lifespan(app: FastAPI):
    start = time.perf_counter()
    STATE["model"] = joblib.load(os.environ.get("MODEL_PATH", "model.joblib"))
    STATE["version"] = os.environ.get("MODEL_VERSION", "dev")
    STATE["load_seconds"] = round(time.perf_counter() - start, 3)
    yield
    STATE.clear()


app = FastAPI(title="Sentiment service", version="1.0.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    """Liveness: the process answers."""
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict:
    """Readiness: the model is loaded."""
    if "model" not in STATE:
        raise HTTPException(status_code=503, detail="model not loaded")
    return {"status": "ready", "model_version": STATE["version"]}


@app.post("/v1/predict", response_model=PredictResponse)
def predict(request: PredictRequest) -> PredictResponse:
    proba = STATE["model"].predict_proba(request.texts)
    for observe in OBSERVERS:
        observe(request.texts, proba)
    predictions = [
        Prediction(
            label=LABELS[int(p.argmax())],
            label_id=int(p.argmax()),
            probabilities={name: round(float(q), 4) for name, q in zip(LABELS, p, strict=True)},
        )
        for p in proba
    ]
    return PredictResponse(model_version=STATE["version"], predictions=predictions)
'''


def make_service(directory: Path, model) -> Path:
    """Write the service (app.py) and the model (model.joblib) into `directory`."""
    import joblib

    directory.mkdir(parents=True, exist_ok=True)
    write("app.py", SERVICE_APP, base=directory)
    joblib.dump(model, directory / "model.joblib")
    return directory
