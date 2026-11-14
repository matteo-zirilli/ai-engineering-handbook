# AI Engineering Handbook

A from-scratch, proof-driven, hands-on handbook on **AI Engineering**, written
in English and published as a website with [Quarto](https://quarto.org).

📖 **Read it online:** <https://matteo-zirilli.github.io/ai-engineering-handbook/>

The handbook follows, course by course, the topics of the twelve courses of the
Master in AI Engineering attended by the author, going far beyond them. It is an
independent work, not affiliated with the course provider, and it does not
reproduce any course material. It is:

- **self-contained** — it assumes no prior knowledge and builds every concept
  from the foundations;
- **proof-driven** — every formula is derived or proved, with the idea behind
  it and the paper, book or standard where it was first proposed;
- **two-layered** — a *Reading mode* switch (Essentials / Full) shows only the
  must-know content or also every deep dive (proofs, history, internals,
  extra code), which sit in place as collapsible coloured bars;
- **example-rich** — each idea is shown as an intuition, a worked example by
  hand, and runnable code whose output is produced by actually executing it;
- **interactive** — some pages contain small simulations that run in the
  browser;
- **verifiable** — every chapter ends with an annotated reading list, and the
  bibliography says, for each source, how to obtain it and which parts are
  used.

Each part ends with the course's final project, implemented in the companion
repository [`matteo-zirilli/ai-projects`](https://github.com/matteo-zirilli/ai-projects).

## Contents

| Part | Course | Project | Status |
|---|---|---|---|
| I | Programming with Python | Terminal phone-book prototype | ✅ |
| II | High-performance programming with C and C++ | Command-line CRM for an insurance company | ✅ |
| III–XII | remaining courses of the master | — | 🛠 in preparation |

## Repository layout

```text
_quarto.yml            book configuration (chapters, theme, crossrefs)
index.qmd              preface
how-to-study.qmd       study method, conventions, notation
python/                Part I — Programming with Python (one .qmd per module + project)
cpp/                   Part II — C and C++ (one .qmd per module + project)
cpp/cppbook.py         helper that compiles and runs the C/C++ examples (used by the cells)
cpp/_crm/              reference implementation of the Part II project (CMake project)
appendices/            finding and reading the sources
references.qmd         the bibliography page
references.bib         all sources (BibTeX), with DOI/arXiv/ISBN/URL and access notes
images/                static figures
styles/                theme customisations
_freeze/               stored results of the executed Python cells (do not edit by hand)
.github/workflows/     GitHub Action that renders the book and publishes it to GitHub Pages
```

## Building locally

Requirements: [Quarto](https://quarto.org/docs/get-started/) ≥ 1.6 and, to
re-execute the code, Python 3.13 with `jupyter`, `numpy`, `pandas`,
`matplotlib`, `pillow`, `packaging`. Re-executing Part II also needs GCC
(`g++`/`gcc` with C++20 support), GDB, Make, CMake, Ninja, `strace` and the
binutils (`nm`, `objdump`, `readelf`), on Linux.

```bash
quarto preview            # live preview in the browser
quarto render             # full build into _book/
```

Code cells are executed once and their results stored in `_freeze/`
(`execute: freeze: auto`): the GitHub Action only needs Quarto, not Python or
a C++ compiler. In Part II each C/C++ example is a Python cell that calls
`cpp/cppbook.py` to write, compile and run the program and print its source and
output as Markdown (`output: asis`, set in `cpp/_metadata.yml`).
After changing a chapter's code, render it locally and commit the updated
`_freeze/` folder together with the `.qmd` file.

## Authoring conventions

Every chapter follows the same template:

1. **Learning objectives** and **Topics covered** (in my own words);
2. **Intuition** (no formulas);
3. **Theory**: definitions, theorems and algorithms, each with its history and
   primary source, and with a one-line *"In one line:"* explanation after each
   statement;
4. **Worked examples** (by hand) and **practice** (executed code);
5. **In the project** box linking the chapter to the course project;
6. **Common pitfalls**, **Summary**, **Exercises** (collapsed solutions),
   **Further reading** (annotated, with section numbers).

### Essentials and deep dives

Every page has two layers, switched by the *Reading mode* control
(Essentials by default; explained in `how-to-study.qmd#sec-reading-modes`):

- **Essentials** — must-know content, self-sufficient for later chapters and
  the project. Plain text, no markup.
- **Deep dives** — proofs, history, internals, extra code. Mark them in place:

  ```markdown
  ::: {.deep kind="proof"}          <!-- a proof (amber bar) -->
  ## Proof of @thm-something
  ...
  :::

  ::: {.deep}                       <!-- any other deep dive (purple bar) -->
  ## Title shown on the bar
  ...
  :::

  ### A whole section {.deep}       <!-- the entire section collapses under its heading -->
  ```

  Rule: if a deep dive introduces something used later, the essentials must
  contain at least its statement.

Implementation: `filters/deep.lua` (blocks), `styles/deep-mode.html` (switch,
banner, reading times, table-of-contents marks), `styles/handbook.css`.

### Course material

The handbook never reproduces the course provider's material (lectures,
slides, texts, project assignments, lesson titles). Topics and project
requirements are always restated in my own words.

Cross-references use Quarto ids: `sec-`, `thm-`, `lem-`, `def-`, `prp-`,
`exm-`, `exr-`, `eq-`, `fig-`, `tbl-`. Citation keys are `firstauthorYEAR`.

© 2026 Matteo Zirilli — all rights reserved.
