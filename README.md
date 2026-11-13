# AI Engineering Handbook

A from-scratch, proof-driven, hands-on handbook on **AI Engineering**, written
in English and published as a website with [Quarto](https://quarto.org).

📖 **Read it online:** <https://matteo-zirilli.github.io/ai-engineering-handbook/>

The handbook follows, course by course, the twelve courses of the Master in AI
Engineering attended by the author, going far beyond the lectures:

- **self-contained** — it assumes no prior knowledge and builds every concept
  from the foundations;
- **proof-driven** — every formula is derived or proved, with the idea behind
  it and the paper, book or standard where it was first proposed (proofs are
  in collapsible boxes, so they never get in the way);
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
| II–XII | remaining courses of the master | — | 🛠 in preparation |

## Repository layout

```text
_quarto.yml            book configuration (chapters, theme, crossrefs)
index.qmd              preface
how-to-study.qmd       study method, conventions, notation
python/                Part I — Programming with Python (one .qmd per module + project)
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
`matplotlib`, `pillow`, `packaging`.

```bash
quarto preview            # live preview in the browser
quarto render             # full build into _book/
```

Code cells are executed once and their results stored in `_freeze/`
(`execute: freeze: auto`): the GitHub Action only needs Quarto, not Python.
After changing a chapter's code, render it locally and commit the updated
`_freeze/` folder together with the `.qmd` file.

## Authoring conventions

Every chapter follows the same template:

1. **Learning objectives** and the course lessons covered;
2. **Intuition** (no formulas);
3. **Theory**: definitions, theorems and algorithms, each with its history and
   primary source; each proof sits in a collapsed
   `callout-caution` box titled *"For the interested reader — proof of …"*,
   preceded by a one-line *"In one line:"* statement of what it proves;
4. **Worked examples** (by hand) and **practice** (executed code);
5. **In the project** box linking the chapter to the course project;
6. **Common pitfalls**, **Summary**, **Exercises** (collapsed solutions),
   **Further reading** (annotated, with section numbers).

Cross-references use Quarto ids: `sec-`, `thm-`, `lem-`, `def-`, `prp-`,
`exm-`, `exr-`, `eq-`, `fig-`, `tbl-`. Citation keys are `firstauthorYEAR`.

© 2026 Matteo Zirilli — all rights reserved.
