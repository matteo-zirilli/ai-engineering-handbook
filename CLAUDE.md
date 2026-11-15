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
author finishes the course).

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

## Pending work on earlier parts

- Add the graded **Practice** blocks (Easy / Medium / Hard with Hint and
  Solution, see the chapter-template rules) to Parts I–III, section by
  section. It does not change chapter numbering; re-render the affected
  chapters and re-check every numeric claim afterwards. Agreed with the
  author, to be done later (not before Part IV).
- Part order stays as in the master (I, II, III, IV, …); chapters keep the
  current global numbering. Do not introduce per-part numbering.
