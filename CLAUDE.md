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

## Notes for the C++ part (Part II, next)

Executed C++ needs a decision before writing: the simplest robust option is
Python cells that write a `.cpp` file, compile it with `g++ -std=c++20 -O2`
and run it (outputs then go into `_freeze/` like Python), showing the C++
source as a normal `cpp` code block. Check compiler availability first, and
state the compiler and standard used in the part overview.
