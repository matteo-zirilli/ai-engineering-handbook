# Instructions for working on this repository

This file lets any new working session continue the handbook with the same
rules. Read it fully before writing anything. The author (Matteo) talks in
**Italian**; the handbook is written in **English**.

## What this is

A Quarto book (`_quarto.yml`, HTML only) published to GitHub Pages by
`.github/workflows/publish.yml` on every push to `main`. One **part** per
course of the author's Master in AI Engineering; each part ends with the
course's final project, implemented in the separate repository
`matteo-zirilli/ai-projects` (public; some projects may be missing until the
author finishes the course). **Exception (agreed with the author,
2026-11-16):** a course without a final project (Parts V and VI) gets no
project chapter; its `index.qmd` says so explicitly, the chapter ends with
synthesis exercises, the Hard practice exercises follow a common thread chosen
with the author, and the "In the project" box links to the projects of
earlier parts instead.

Part I (Programming with Python, `python/`) is complete and is the **reference
for style, depth and structure**: read one chapter (e.g.
`python/03-collections.qmd`) and the project chapter
(`python/15-project-phone-book.qmd`) before writing a new part.

## Workflow for a new course

1. The author sends a zip with screenshots of the course structure (modules,
   theory/practice lessons) and of the project brief. Treat it as **input
   only**: never reproduce it.
2. Create a folder for the part (e.g. `cpp/`) with `_metadata.yml`, an
   `index.qmd` overview (what you will be able to do, prerequisites, map of the
   part, the project) and one `.qmd` per module, plus a project chapter.
   Register them in `_quarto.yml` and update the parts table in `index.qmd`
   and `README.md`.
3. Push directly to `main` (the author agreed); check that the *Publish*
   workflow succeeds.

## Non-negotiable rules

- **No course material.** Do not copy or translate the provider's texts,
  project briefs, fictional company profiles, persona letters, tips, or lesson
  titles/numbering. Restate topics in your own words; write the project as an
  own-words "The problem" section with requirements R1…Rn and the note that it
  is the author's restatement. The preface's independence note must stay true.
- **Self-contained, from the foundations**: assume no prior knowledge beyond
  earlier parts; link back to earlier chapters instead of repeating them.
- **Every formula proved**, with the idea behind it and the primary source
  (paper/book/standard) cited. Proofs go in `::: {.deep kind="proof"}` blocks,
  each preceded by the statement and an *"In one line:"* explanation.
- **Many examples**: intuition → worked example by hand → executed code.
- **Two reading layers** (see `how-to-study.qmd#sec-reading-modes`):
  essentials must be self-sufficient; proofs, history, internals and extra
  code are deep dives, placed in context:
  `::: {.deep}` + `## Title` for a block, `## Heading {.deep}` for a whole
  section. If a deep dive contains something used later, put its statement in
  the essentials.
- **Chapter template**: Learning objectives · Topics covered (own words) ·
  Intuition · Theory · Worked examples · Practice · "In the project" box
  (`::: {.project-link}`) · Common pitfalls · Summary · Exercises with
  collapsed solutions · Further reading (annotated, with section numbers).
- **Graded practice per section** (from Part IV on; author's request): at the
  end of every main section (`##`) where it makes sense — not for purely
  historical or introductory sections — a `### Practice {.unnumbered}` block
  with **three exercises: Easy, Medium, Hard**. Easy = apply the idea just
  seen, often by hand; Medium = implement or vary it in code; Hard = a small
  open problem combining several ideas, in the direction of the part's final
  project (without giving away the project's solution). Each exercise is
  followed by **two separate collapsed callouts**: first a **Hint** (guidance,
  never the answer), then the **Solution** — complete, with code commented
  where it helps, **executed** like all code, plus a short explanation of why
  it works and of the typical mistakes. The end-of-chapter "Exercises" remain,
  as synthesis problems spanning several sections. Markup (blank lines
  between blocks are required, otherwise `:::` is not parsed):

  ```markdown
  ### Practice {.unnumbered}

  ::: {#exr-<chapter>-<topic>-easy}
  ## Easy — <short title>
  <statement>
  :::

  ::: {.callout-note collapse="true"}
  ## Hint
  <a nudge, not the answer>
  :::

  ::: {.callout-tip collapse="true"}
  ## Solution
  <explanation + executed, commented code>
  :::
  ```

  (then the same for `-medium` and `-hard`). This makes chapters longer and
  renders slower: for a large part, split the work over two sessions (theory
  chapters first, then the project chapter).
- **Bibliography** (`references.bib`): key `firstauthorYEAR`; DOI / arXiv /
  ISBN / URL whenever they exist; a `note` saying how to obtain the source and
  which parts are used (no final period: the CSL adds it). Group entries by
  part and chapter. Verify facts that may have changed (tools, versions,
  study figures) with a web search before stating them.
- **Accuracy over speed**: run every code cell; if an output contradicts the
  text, fix the text. Check every numeric claim.

## Build and verification

- Quarto **1.6.42** (pinned in CI). Python cells execute locally once; results
  are stored in `_freeze/` (`execute: freeze: auto`) and **must be committed**.
  CI only re-renders from the frozen results.
- Render with `quarto render` (or one file at a time) and treat any `WARN`
  (unresolved crossref/citation) as an error.
- Look at rendered pages (headless browser) in both reading modes; the CDN
  libraries (MathJax, Observable) are not reachable from the sandbox, so serve
  them from local npm copies when taking screenshots.
- Interactive widgets use `{ojs}` cells; put `viewof` inputs and the labelled
  figure in **separate** cells (otherwise subfigure labels appear). Mermaid
  cells need `%%| echo: false`.
- Sidebar: the bold "Index" heading and the numbers "0." (Preface) and
  "1.", "2.", … (parts) come from CSS in `styles/handbook.css` (a counter on
  the top-level sections that link to a page); a new part is numbered
  automatically. Do not put numbers in part titles.
- Do not leave machine-specific paths (`/tmp/...`, `/root/...`) in outputs.

## Notes for Part II (C and C++, `cpp/`)

- Executed C/C++: every example is a Python cell calling `cpp/cppbook.py`
  (`run`, `show`, `sh`, `write`, `compile_sources`, `run_exe`), which writes the
  source to a private temp dir, compiles it (`g++ -std=c++20 -O2 -Wall -Wextra`
  or `gcc -std=c17`), runs it and prints source + output as Markdown.
  `cpp/_metadata.yml` sets `echo: false` and `output: asis`; cells whose Python
  code must be shown override with `#| echo: true` and `#| output: true`.
  The helper strips temp-dir paths and PIDs from outputs; check `_freeze/cpp`
  for machine-specific paths before committing.
- The project's reference implementation is a real CMake project in
  `cpp/_crm` (the leading `_` keeps Quarto from rendering it). The project
  chapter reads and displays those files: **freeze does not notice changes to
  them**, so after editing `_crm` delete `_freeze/cpp/09-project-crm` and
  re-render. Build and test it with `-Werror` and sanitizers (GCC and Clang).
- The author's own CRM solution is not yet in `ai-projects`; when it is,
  add a walkthrough and code review to `cpp/09-project-crm.qmd` as in Part I.
- Screenshots: serve `_book` over HTTP (OJS modules fail on `file://`) and
  map `cdn.jsdelivr.net/npm/<pkg>@<version>/...` to local npm installs of the
  exact versions requested (mathjax@3, @observablehq/plot, @observablehq/inputs,
  d3, htl).

## Notes for Part III (Foundations of machine learning, `ml/`)

- Structure: `ml/index.qmd` + `01-what-is-ml` … `07-clustering` (one per
  module) + `08-project-real-estate`. Chapter ids: `sec-ch-ml-intro`,
  `sec-ch-ml-data`, `sec-ch-ml-preprocessing`, `sec-ch-ml-regression`,
  `sec-ch-ml-regularization`, `sec-ch-ml-classification`,
  `sec-ch-ml-clustering`, `sec-ch-project-housing`. Later parts should link
  back to them for risk/ERM, train/test, cross-validation, bias–variance,
  regularisation, classification metrics (e.g. `@thm-bias-variance`,
  `@sec-cross-validation`, `@sec-classification-metrics`, `@thm-auc`,
  `@sec-leakage`, `@sec-gradient-descent`).
- Ordinary Python cells (`ml/_metadata.yml`: `jupyter: python3`, code shown).
  Every chapter starts with a hidden cell `import mlbook; mlbook.setup()`.
  `ml/mlbook.py` holds the figure style (light surface `#fcfcfb`, recessive
  grid, the fixed categorical order `mlbook.COLORS` — never cycle more than 8
  hues; for many lines draw them grey and highlight ≤ 3), and
  `load_housing(encoded=...)`. Matplotlib figures use `#| label: fig-…` and
  `#| fig-cap:`. Inline values use `` `{python} expr` ``.
- Data: only public data with a clear licence or data generated in code.
  `ml/_data/housing.csv` is a byte-identical CC0 copy of the Kaggle "Housing
  Prices Dataset" (provenance and the link to Anglin & Gençay 1996 in
  `ml/_data/README.md`); `load_breast_cancer` and `load_wine` ship with
  scikit-learn (UCI, CC BY 4.0). Folders starting with `_` are not rendered.
- Versions used: Python 3.13, scikit-learn 1.9.1, NumPy 2.5, pandas 3.0
  (text columns have dtype `str`; `df.drop(columns=..., axis=1)` raises),
  Matplotlib 3.11. `ml/index.qmd` prints the versions at build time.
- The project chapter **downloads** two files at render time, both pinned to a
  commit: the author's notebook from `ai-projects` (commit `2e2c86d…`) and the
  Ecdat `Housing.csv` from Rdatasets (commit `1dcc2bf…`). Re-rendering it needs
  network access to `raw.githubusercontent.com` (and `seaborn`, imported by the
  replayed notebook). If the author updates the notebook, update the pinned
  commit and re-check the review table.
- Pattern established for project chapters with the author's notebook:
  re-execute it (top to bottom **and** in the order of the stored
  `execution_count`s) before reviewing; Part III found a doubly-applied
  `log1p` and metrics computed on a CV fold that way. Do not name the course's
  fictional company.
- Render times: full book ≈ 6–7 min when Part III re-executes (ch. 5 ≈ 1 min,
  ch. 8 ≈ 2–3 min). Single-file renders show crossref WARNs for other chapters;
  only the full render must be WARN-free.
- Screenshots (playwright with `/usr/bin/google-chrome`): the OJS runtime
  requests exactly `@observablehq/inputs@0.10.6`, `@observablehq/plot@0.6.11`,
  `d3@7.9.2` (and 7.8.5), `htl@0.3.1`, `marked@0.3.12`, `mathjax@3`; install
  those versions with npm and map `cdn.jsdelivr.net/npm/<pkg>@<ver>/<path>`
  to `node_modules/<pkg>/<path>`. Polyfill and Google-fonts failures are
  harmless.
- CI installs `scikit-learn scipy seaborn openpyxl lxml` as a safety net, but
  still relies on `_freeze/`.

## Notes for Part IV and later

- Before writing, read `ml/05-overfitting-regularization.qmd` and
  `ml/08-project-real-estate.qmd` (latest reference for depth, proofs in
  context, widgets, walkthrough + forensic review + reference implementation).
- Bibliography: Part III has its own block in `references.bib`, grouped by
  chapter; general ML textbooks (`hastie2009`, `james2023`, `bishop2006`,
  `murphy2022`, `shalevshwartz2014`, `pedregosa2011`) are already there — reuse
  them instead of adding duplicates (`grep -n "^@" references.bib`).
- Keep every numeric claim in the text consistent with the executed output:
  after the last render, re-read the outputs (e.g. from
  `_freeze/<part>/<chapter>/execute-results/html.json`) and fix the prose.

## Notes for Part IV (Machine learning: models and algorithms, `mlalg/`)

- Status (2026-11-15): complete. Theory chapters and project chapter
  `08-project-fruits.qmd` (id `sec-ch-mla-project`, labels `fruit`) published
  the same day, in two working sessions.
- Structure: `mlalg/index.qmd` + one chapter per course module (the course's
  introductory module is folded into the overview): `01-optimization`,
  `02-parametric`, `03-naive-bayes`, `04-svm`, `05-neural-networks`,
  `06-knn`, `07-trees-forests`. Chapter ids: `sec-ch-mla-optim`,
  `sec-ch-mla-parametric`, `sec-ch-mla-nb`, `sec-ch-mla-svm`,
  `sec-ch-mla-nn`, `sec-ch-mla-knn`, `sec-ch-mla-trees`, project
  `sec-ch-mla-project` (`08-project-fruits`).
- Label stems per chapter (theorems, figures, equations, sections): `opt`,
  `npar`, `nb`, `svm`, `nn`, `knn`, `tree`; exercises
  `exr-mla<N>-<section>-easy|medium|hard` (Practice) and `exr-mla<N>-<name>`
  (end of chapter). Check collisions with
  `grep -rhoE "\{#[a-z]+-[A-Za-z0-9_-]+" --include=*.qmd . | sort | uniq -d`.
- Every main section has the graded Practice block (Easy/Medium/Hard, Hint and
  Solution callouts); Hard exercises use wine, breast cancer, digits or
  synthetic data and point towards the fruit project without solving it.
- Helper `mlalg/mlalgbook.py`: imports `ml/mlbook.py` (same style and
  palette), adds `regions()` (decision regions with class colours `COLORS[i]`),
  `grid()`, `tint()` and `load_fruits()` (reads the pinned raw URL and checks
  the MD5). Every chapter starts with the hidden cell
  `import mlalgbook; mlalgbook.setup()`.
- Widgets: heavy computations are done in hidden Python cells and passed to
  OJS with `ojs_define(...)` (stored in `_freeze`); light ones (momentum,
  KDE, universal approximation) are computed in JS. Use `Inputs.radio` for
  discrete knobs and `type: "ordinal"` in `color:` when the domain is numeric
  (otherwise Plot draws a continuous legend). Pages using `ojs_define` load
  require.js and jQuery from cdnjs (added by Quarto, with SRI hashes): in the
  sandbox this gives a harmless "define is not defined" console error.
- Data. Theory chapters: data generated in code and scikit-learn's wine,
  breast cancer, iris and digits (UCI, CC BY 4.0; keys `aeberhard1992`,
  `wolberg1993`, `fisher1936data`, `alpaydin1998`). **Project data**:
  `fruits.csv` was provided by the course, licence not declared, no public
  source found (web searches, 2026-11-15). The author explicitly agreed to
  an exception to the "public data with a clear licence" rule: a byte-identical
  copy (MD5 `1f5d3d3ec83265951fb8d4eee0f6d1c6`, SHA-256 `e6e8da80…fed1b`,
  16 433 bytes) is in `ai-projects` at the repository root next to the
  notebook, with `fruits_README.md` (origin, "not covered by the MIT
  licence", structure, known problems) — commit `dec0cb2`; commit `090cac3`
  changed only the CSV URL in the two notebooks (English and `it/`) to the
  raw URL pinned at `dec0cb2`. The handbook must **not** contain a copy:
  the project chapter reads it with `mlalgbook.load_fruits()` (pinned to
  `dec0cb2`). **Re-rendering the project chapter needs network access** to
  `raw.githubusercontent.com` (the CSV and the notebook, both pinned to
  `dec0cb2`) and `seaborn` (imported by the replayed notebook). The preface's
  independence note and `mlalg/index.qmd` state this exception.
- Known problems of `fruits.csv`, verified **in code** in the project chapter
  (@sec-fruit-data): 500 rows, 5 classes × 100, no missing
  values, no duplicates; 40 values of `Durezza buccia (1-10)` above 10 (24
  Uva, 15 Banana, 1 Mela; max 13.72); bananas have "diameter" 119.8–299.9 mm
  and "length" 1.6–4.3 mm (swapped, and the lengths look like cm); lengths of
  every fruit 1.2–11.1 "mm"; implausibly low weights (apples 31–111 g);
  bananas are separable by the diameter alone (min 119.8 > max of the others
  115.4). The course's S3 URL is not reachable from the sandbox: the copy came
  from the zip the author sent.
  Also found: within each type the five measurements are uncorrelated and
  Gaussian-looking — the data look like independent Gaussian draws per type,
  so Gaussian naive Bayes is (nearly) the Bayes classifier; the chapter
  estimates the Bayes accuracy by simulation (≈ 0.94) as a ceiling. All five
  compared models reach ≈ 0.91–0.92 by nested CV.
- Notebook review: done on the version at `dec0cb2` (the one submitted; it
  reads the course's S3 URL, replaced by the pinned copy in the replay).
  Replayed top to bottom it reproduces **every** published output (the
  replay must run under NumPy's default print options, since
  `mlalgbook.setup()` changes them); replayed in counter order it fails
  (counters are leftovers of an interactive session). Main review items: $k$
  chosen on the test set (optimism ≈ 2 points, measured), Yeo–Johnson fitted
  outside the CV (negligible effect here), ambiguous final model ($k = 6$ vs
  15), no metric comparison, data anomalies not discussed. If the author
  updates the notebook, update the pinned commit and re-check the review table.
- Project chapter render time ≈ 8 min (nested grid search over scaler × p ×
  weights × 17 values of $k$); `n_jobs=-1` is used in the searches.
- Versions used: Python 3.13, scikit-learn 1.9.1, NumPy 2.5.3, SciPy 1.18.1,
  pandas 3.0.5, Matplotlib 3.11.2. Pitfalls met with these versions:
  `MLPClassifier`/`MLPRegressor` take `hidden_layer_sizes=` as a keyword;
  `QuadraticDiscriminantAnalysis` with singular class covariances needs
  `solver="eigen", shrinkage=...`; `RadiusNeighborsClassifier(outlier_label=)`
  must have the dtype of `y`; `scipy.stats.kstest(x, "norm", args=...)` fails —
  pass a frozen distribution's `cdf`. Print numbers with f-strings (no
  `np.float64(...)` reprs) and silence warnings whose text contains
  `site-packages` paths.
- Render times: re-executing all of Part IV ≈ 4 min (trees chapter ≈ 2 min,
  SVM and k-NN ≈ 1 min); the full book from `_freeze` ≈ 2 min.

## Notes for Part V and later

- Same pattern as Part IV: one chapter per module, Practice blocks per main
  section, proofs in deep blocks, widgets via `ojs_define` when the
  computation is heavy, `mlalgbook.py` (or an analogous helper importing
  `ml/mlbook.py`) for style.
- Before writing numbers in the prose, run the chapter alone
  (`quarto render <file>`), read the outputs from
  `_freeze/<part>/<chapter>/execute-results/html.json`, then write; the
  simulations of Part IV contradicted several "expected" claims (e.g. complement
  naive Bayes on data generated by the multinomial model, early stopping with a
  tiny validation set), and the text was rewritten to follow the outputs.

## Notes for Part V (Introduction to containers, `containers/`)

- Status (2026-11-16): complete. The course has **one module** (theory:
  containers and orchestration, foundations; practice: running a container
  with Docker, orchestrating with Kubernetes) and **no final project**:
  `containers/index.qmd` + one chapter `01-containers.qmd`, id
  `sec-ch-ctr-containers`, label stem `ctr`, sections `sec-ctr-what`,
  `sec-ctr-kernel`, `sec-ctr-images`, `sec-ctr-build`, `sec-ctr-run`,
  `sec-ctr-k8s`; exercises `exr-ctr1-<section>-easy|medium|hard` and
  `exr-ctr1-reproducible`, `exr-ctr1-pod`. Compose is not covered (the
  course does not cover it); Kubernetes is (the course does).
- Common thread of the Hard exercises: a wine classifier (scikit-learn,
  trained at build time) served over HTTP with the standard library, scored in
  batch, rolled out on Kubernetes. Never `fruits.csv` here.
- Helper `containers/ctrbook.py`: writes files to a private temp dir
  (`project`, `write`, `show`, `files`), runs commands (`run`, `sh`, `quiet`),
  builds (`build` prints a per-step cached/rebuilt table, returns seconds;
  `LAST_BUILD_LOG`), reads layers from `docker save` (`layers`), drives k3s
  (`ensure_k3s`, `kube`, `kube_run`, `load_image`), and masks IDs/digests as
  `<id-N>` (same value, same placeholder), temp paths and durations. The
  running example's files are constants (`REQUIREMENTS`, `TRAIN_PY`,
  `SERVE_PY`, `SCORE_PY`, `DOCKERFILE_SCORING`, `scoring()`). Cells that print
  Markdown are hidden with `output: asis`; Python the reader should see is in
  ordinary cells. Before committing, grep `_freeze/containers` for `/tmp/`,
  `/root/`, `ctrbook-` and 64-hex strings.
- **Environment (sandbox, verified 2026-11-16).** Docker 29.9.3 CLI and daemon,
  buildx 0.38.1, Compose v5.7.0, runc 1.5.2 are installed; start the daemon
  with `dockerd &` (root) — `ctrbook.ensure_docker()` does it. **No image
  registry is reachable** (Docker Hub, ghcr, quay, registry.k8s.io all 403);
  archive.ubuntu.com, PyPI and GitHub release downloads are. Base images are
  built locally by `ensure_base_images()`: `debootstrap --variant=minbase
  noble` → `local/ubuntu:noble` (no default command: `docker create` needs
  one), then `local/python:3.12-slim` (python3, pip, venv; trusts the
  sandbox's CA bundle via `PIP_CERT`, because TLS to PyPI from containers is
  re-terminated by the proxy — verification stays on) and `local/gcc:13`.
  Dockerfiles shown use `ARG BASE=python:3.12-slim` / `ARG BUILDER=gcc:13` and
  `FROM ${BASE}`; `build()` passes the local images with `--build-arg`.
  `--no-cache` for the first scoring build (so its timing is a cold build);
  `setup()` prunes the BuildKit cache to keep the disk bounded.
- **cgroup v1** in the sandbox (cgroupfs driver), v2 on almost every real
  host: the text explains v2 and says the measured numbers come from v1. The
  shares→weight conversion on v2 is quadratic in log2 since runc 1.3.2
  (Holder 2026): 2048:1024 becomes 174:100.
- **k3s** (v1.37.2, binary and air-gap images from GitHub releases into
  `/usr/local/bin/k3s` and `/var/lib/rancher/k3s/agent/images/`). Three
  sandbox workarounds: `--kubelet-arg=fail-cgroupv1=false`; a containerd
  template `/var/lib/rancher/k3s/agent/etc/containerd/config-v3.toml.tmpl`
  (copy of the generated `config.toml` without its first line, plus
  `restrict_oom_score_adj = true` under `[plugins.'io.containerd.cri.v1.runtime']`,
  since the sandbox forbids lowering `oom_score_adj`); relaxed eviction
  thresholds (the disk reports 252 GB but has ~20 GB free, so the default
  rules taint the node with disk pressure and the image GC deletes imported
  images). `NO_PROXY` must include the node and cluster ranges (`K8S_ENV`),
  or `kubectl logs` fails. Images reach the node with `load_image()` (`docker
  save | k3s ctr images import -`) and `imagePullPolicy: Never`.
- Times: rendering `01-containers.qmd` ≈ 10 min (Docker builds with pip
  installs from PyPI, a 200 MB context test, k3s rollouts); measurements
  (CPU shares, build times, stop times) depend on the machine — the prose
  uses ratios and inline values.

## Notes for Part VI (Introduction to REST APIs, `rest/`)

- Status (2026-11-16): complete. One module (introduction to APIs, HTTP
  methods, REST, endpoints), **no final project**: `rest/index.qmd` + one
  chapter `01-rest-apis.qmd`, id `sec-ch-api-rest`, label stem `api`,
  sections `sec-api-http`, `sec-api-methods`, `sec-api-rest`,
  `sec-api-endpoints`, `sec-api-production`; exercises
  `exr-api1-<section>-easy|medium|hard` and `exr-api1-model-service`,
  `exr-api1-problem`, `exr-api1-hmac`.
- Ordinary Python cells. Helper `rest/apibook.py`: `setup()` (Part III style),
  `write()` (modules in a temp dir on `sys.path`), `server()` (uvicorn or any
  command in a subprocess on a free loopback port), `mask()`. Everything runs
  on 127.0.0.1 (FastAPI `TestClient` in-process, or uvicorn); httpbin and
  jsonplaceholder are not reachable. The last exercise imports
  `containers/ctrbook.py` to build and run the service image (Docker needed).
- Versions: FastAPI 0.163.1 (emits OpenAPI 3.1.0; the current spec is 3.2.0),
  httpx 0.28.1, uvicorn 0.54.0, Pydantic 2.13.5, jsonschema 4.26.0 (installed
  with pip; `jupyter` must be installed for Quarto to execute). Pitfalls met:
  exception handlers added to a FastAPI app after its first request are
  ignored (the middleware stack is built once) — create a new app;
  `asyncio.run` inside Jupyter needs a separate thread; `nest_asyncio` is not
  installed.
- Rendering `01-rest-apis.qmd` ≈ 2–3 min.

## Notes for Part VII (MLOps: machine learning in production, `mlops/`)

- Status (2026-11-18): **phase 1 complete** — overview and the eight theory
  chapters; the project chapter (phase 2) is pending, blocked on two
  decisions asked to the author (below). The course has eight modules (zip:
  intro to MLOps; venv/Git/model registry; serving with FastAPI; tests and
  linting; Docker and deployment; CI/CD with GitHub Actions; monitoring with
  drift, Compose, Grafana, alerts; orchestration with Airflow) — they differ
  from the topics proposed in the author's message, and the zip was followed
  as instructed. Files: `01-mlops` (`sec-ch-ops-intro`), `02-reproducibility`
  (`sec-ch-ops-repro`), `03-serving` (`sec-ch-ops-serving`), `04-testing`
  (`sec-ch-ops-testing`), `05-deployment` (`sec-ch-ops-deploy`), `06-cicd`
  (`sec-ch-ops-cicd`), `07-monitoring` (`sec-ch-ops-monitor`),
  `08-orchestration` (`sec-ch-ops-orch`); project to come as
  `09-project-sentiment` (`sec-ch-ops-project`). Label stem `ops`
  (`sec-ops-…`, `thm-ops-…`, `prp-ops-…`, `eq-ops-…`, `fig-ops-…`); exercises
  `exr-ops<N>-<section>-easy|medium|hard` and `exr-ops<N>-<name>`.
- Formulas proved (for later reference): churn bounds `@prp-ops-churn`, ML
  Test Score decomposition `@prp-ops-mltestscore`, summation error
  `@prp-ops-summation`, commit authenticates history `@prp-ops-commit`,
  load-once `@prp-ops-load-once`, temperature scaling `@prp-ops-temperature`,
  batching `@prp-ops-batching`, Wilson `@prp-ops-wilson`, test size
  `@prp-ops-test-size`, formatter idempotence `@prp-ops-formatter`, canary
  size `@prp-ops-canary`, stage order `@prp-ops-stage-order`, critical path
  `@prp-ops-critical-path`, McNemar `@prp-ops-mcnemar`, burn rate
  `@prp-ops-burn`, histogram quantiles `@prp-ops-hist-quantile`, PSI =
  Jeffreys `@prp-ops-psi`, KS/DKW size `@prp-ops-ks-size`, BBSE
  `@thm-ops-bbse`, EM priors `@prp-ops-em-prior`, CUSUM `@prp-ops-cusum`, Kahn
  `@thm-ops-kahn`, greedy bounds `@prp-ops-greedy`, backfill idempotence
  `@prp-ops-backfill`, retraining period `@prp-ops-retrain-period`.
- Helper `mlops/opsbook.py`: `setup()` (Part III style), `make_posts()` —
  synthetic posts with labels 0/1/2 and switchable shifts (`prior`, `topics`,
  `slang_rate`, `extra_words`, `emoji_rate`, `swap` for concept shift,
  `noise` = annotation noise 6 %; the same seed with `noise=0` gives the same
  texts with the true labels) — `train_model()` (TF-IDF 1–2-grams + logistic
  regression, accuracy ≈ 0.93 against noisy labels, ≈ 0.99 against true
  ones), `SERVICE_APP`/`make_service()` (the FastAPI service reused by
  chapters 3–7; it has an `OBSERVERS` hook for metrics; keep it Ruff-clean:
  chapter 6 lints it in CI), `write/show/sh/run/mask/project/server`,
  `tool(name)` (Prometheus 3.16.0, promtool, Alertmanager 0.35.0, amtool,
  actionlint 1.7.12, act 0.2.98, CNCF Distribution registry 3.1.2, from
  GitHub releases into `~/.cache/opsbook-tools`), `venv_python(name)`
  (separate venvs in `~/.cache/opsbook-venvs`: `mlflow` = MLflow 3.18.0 +
  scikit-learn 1.9.1; `airflow` = Apache Airflow 3.4.0 with its constraints
  file for Python 3.13, plus scikit-learn/pandas/joblib for the tasks). `run`
  uses `GIT_CONFIG_GLOBAL=/dev/null` (the sandbox's global Git config signs
  commits — the signature leaked into an output once) and `mask` strips ANSI
  colours. Docker builds reuse `containers/ctrbook.py` (local base images).
- Environment (sandbox, verified 2026-11-18): huggingface.co, hf-mirror,
  download.pytorch.org, mlflow.org, zenodo.org, dagshub.com, kaggle.com,
  UCI, dl.grafana.com and every image registry unreachable; PyPI, npm,
  raw.githubusercontent.com, GitHub release downloads and anonymous `git
  clone` of public GitHub repositories work. **Grafana cannot be installed**
  (binaries only on dl.grafana.com): its provisioning and dashboard JSON are
  written and validated (YAML parses, data-source uids, no overlapping
  panels, every PromQL query returns data from the live Prometheus) but not
  rendered; the Compose file puts Grafana in a `dashboards` profile.
  Prometheus/Alertmanager run as binaries and in Compose as local images
  (`local/prometheus:latest`, `local/alertmanager:latest`, built from the
  binaries on `local/ubuntu:noble`, `WORKDIR /prometheus` so Alertmanager can
  write its data). MLflow 3.18 refuses the file store (maintenance mode) and
  `mlflow-skinny` has no registry: the full `mlflow` with `sqlite:///` is used.
  **act** runs workflows with `-P ubuntu-latest=-self-hosted` (on the host;
  no runner images reachable); act's own Git client cannot clone actions
  through the proxy ("authentication required"), so `actions/setup-python@v7`
  and `actions/cache@v6` are cloned with plain `git` and passed with
  `--local-repository`; `actions/checkout` is handled by act itself; the
  workflow skips `setup-python` with `if: ${{ !env.ACT }}`. Docker push/pull
  goes to a local `registry` on 127.0.0.1:5000 (127.0.0.0/8 is insecure by
  default and in dockerd's NoProxy).
- Versions: Python 3.13.18, scikit-learn 1.9.1, NumPy 2.5.3, SciPy 1.18.1,
  pandas 3.0.5, FastAPI 0.163.2, Pydantic 2.13.5, uvicorn 0.54.0, httpx
  0.28.1, pytest 9.1.1, pytest-cov 7.1.0, Hypothesis 6.170.15, Ruff 0.17.5
  (use `python -m ruff`: an older `ruff` 0.16.9 is first on PATH),
  prometheus-client 0.26.0, Docker 29.10.0, Compose 5.7.1. Pitfalls met:
  Hypothesis `st.characters` takes `min_codepoint`/`max_codepoint` and
  `st.text(alphabet=...)` accepts only one-character elements; FastAPI's
  `TestClient` waits for background tasks (measure shadow latency with
  uvicorn); `app.mount("/metrics", make_asgi_app())` redirects `/metrics` to
  `/metrics/` (clients need `follow_redirects=True`; Prometheus follows);
  Airflow 3 `dags test` needs `airflow db migrate` first and the tasks'
  dependencies in Airflow's venv; patch generated DAG files with an
  indentation-aware helper (string replaces with the wrong indentation fail
  silently).
- Data: only synthetic posts in the theory chapters (no real person's text).
  **Pending decisions for phase 2 (asked 2026-11-18, no answer yet):**
  (1) the RoBERTa weights cannot be downloaded (HF unreachable) — options:
  the author publishes the original files as a release asset of
  `ai-projects` (read pinned by SHA-256, exported once to ONNX and served
  with onnxruntime + tokenizers), or publishes ONNX directly, or the service
  uses torch; (2) project data — DynaSent v1.1 (CC BY 4.0, explicit in its
  README, 3 classes, on raw.githubusercontent; Yelp sentences, Round 1
  selected adversarially against RoBERTa) recommended; TweetEval sentiment
  (in-domain, licence unclear: needs an explicit exception like
  `fruits.csv`); GoEmotions (Apache 2.0 on the repo, Reddit, sentiment
  derived from emotions); or DynaSent + GoEmotions as a real domain shift;
  (3) Grafana as above (or the author publishes the OSS tarball); (4)
  whether a real GitHub Actions workflow for `mlops/_sentiment/**` should be
  added to this repository, or the project's workflow stays inert and is run
  with act. The reference implementation goes to `mlops/_sentiment` (no
  author solution in `ai-projects` yet).
- Render times (2 CPUs): `07-monitoring` ≈ 5–6 min (Compose build + two
  minutes of traffic for the alert), `08-orchestration` ≈ 5 min (about twenty
  `airflow dags test` runs), `06-cicd` ≈ 1–2 min (act runs), `05-deployment`
  ≈ 1.5 min (image builds, registry), the others < 1 min; the whole part
  ≈ 15–20 min when re-executed.

## Pending work on earlier parts

- Add the graded **Practice** blocks (Easy / Medium / Hard with Hint and
  Solution, see the chapter-template rules) to Parts I–III, section by
  section. It does not change chapter numbering; re-render the affected
  chapters and re-check every numeric claim afterwards. Agreed with the
  author, to be done later (not before Part IV).
- Part order stays as in the master (I, II, III, IV, …); chapters keep the
  current global numbering. Do not introduce per-part numbering.
