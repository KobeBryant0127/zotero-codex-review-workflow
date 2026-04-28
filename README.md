# Zotero x Codex Review Workflow

> From zero Zotero setup to a citation-safe review paper, with Codex as your managed research copilot.

[![CI](https://github.com/KobeBryant0127/zotero-codex-review-workflow/actions/workflows/ci.yml/badge.svg)](https://github.com/KobeBryant0127/zotero-codex-review-workflow/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Windows](https://img.shields.io/badge/platform-Windows%2010%2F11-blue)](README.md)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](README.md)

This repository is an opinionated end-to-end workflow for beginners who want to go from:

`I have a review topic`

to:

`I have a structured review project, a tracked literature pool, evidence tables, a Word draft, and real Zotero citations that can refresh`

The goal is not to let AI hallucinate a paper. The goal is to let **Codex manage the boring, failure-prone, high-friction parts of review writing** while **Zotero remains the source of truth for references** and **Word remains the final citation-safe delivery surface**.

## Why this hits a real pain point

Writing a review is usually a mess of disconnected tools:

- search manually in databases;
- dump citations into Zotero;
- read papers in a scattered way;
- lose track of inclusion decisions;
- draft in Markdown or Word with placeholder citations;
- manually insert dozens or hundreds of Zotero references one by one at the end.

That last step is especially painful for review papers. A 100+ citation review is not rare, and maintaining clean Zotero-managed citations inside Word is slow and fragile when the rest of the workflow is still ad hoc.

This project is trying to compress that pain into one managed pipeline:

- Codex handles orchestration;
- Zotero handles bibliographic truth;
- Word handles final scholarly formatting;
- the repository tracks what has happened, what still needs a human, and what Codex should do next.

## What feels different here

This repo is not just:

- a Zotero tip sheet;
- a literature search script;
- a prompt collection;
- a Word citation macro;
- or a generic AI writing scaffold.

It is a **managed review workflow** with explicit state, handoffs, resume points, and final citation checks.

In practical terms:

- `intake` creates a guided project brief;
- `run` executes the machine-doable stages;
- `handoff` tells the user exactly what human action is needed next;
- `resume` lets Codex continue after that manual checkpoint;
- `final-check` verifies the package before you call it done.

That means the repo is designed for a beginner to say:

> "Take me from zero to a real review draft. Stop only when you truly need me."

## What this repo can do today

- Check whether Python, Zotero, Word, Git, and GitHub CLI are available.
- Create a stateful review project for a new topic.
- Generate the project brief, protocol, evidence ledger, draft scaffold, and table/figure plans.
- Search PubMed and OpenAlex and export CSV + Zotero-importable RIS.
- Merge candidate literature into one tracked candidate pool.
- Tell the user exactly when manual Zotero / PDF / Word steps are required.
- Generate a persistent handoff file and a "next prompt to Codex" file.
- Audit whether a final DOCX actually contains Zotero-style fields.
- Produce a final readiness summary for the project package.

## What it deliberately does not fake

- It does not claim every generated sentence is academically correct.
- It does not pretend placeholder citations are the same as real Zotero Word fields.
- It does not bypass paywalls or institutional access limits.
- It does not replace human judgment on scope, inclusion, and conclusions.

The north star is simple:

**AI manages flow. Zotero anchors truth. Word ships the paper.**

## Managed Workflow

```mermaid
flowchart LR
    A["Topic + Constraints"] --> B["intake"]
    B --> C["run"]
    C --> D["Search PubMed / OpenAlex"]
    D --> E["Merged Candidates CSV / RIS"]
    E --> F["Import into Zotero"]
    F --> G["handoff"]
    G --> H["Human checkpoint"]
    H --> I["resume"]
    I --> J["Evidence Matrix + Draft"]
    J --> K["Move to Word"]
    K --> L["Insert official Zotero citations"]
    L --> M["audit-docx + final-check"]
    M --> N["Review package ready"]
```

## Quick Start

### 1. Install the basics

Minimum:

- Windows 10/11
- Python 3.10+
- Zotero desktop
- Zotero Connector browser extension
- Microsoft Word
- Codex or another AI coding assistant that can work with local files

Recommended:

- Better BibTeX for stable citation keys
- Excel / WPS for evidence matrix editing

### 2. Run the environment check

```powershell
powershell -ExecutionPolicy Bypass -File .\START_HERE.ps1
```

or:

```powershell
py scripts\reviewflow.py check
```

### 3. Create a managed review project

```powershell
py scripts\reviewflow.py intake --name my_first_review --topic "your review topic" --output .\outputs
py scripts\reviewflow.py run --project .\outputs\my_first_review
```

### 4. Follow the handoff

```powershell
py scripts\reviewflow.py handoff --project .\outputs\my_first_review
```

That creates:

- `quality/codex_handoff.md`
- `quality/next_prompt_to_codex.md`

These two files are the core beginner experience:

- one says what the human must do next;
- the other says what to tell Codex next.

### 5. Continue only when needed

After a manual step such as importing RIS into Zotero:

```powershell
py scripts\reviewflow.py resume --project .\outputs\my_first_review --mark zotero_imported
```

At the end:

```powershell
py scripts\reviewflow.py final-check --project .\outputs\my_first_review --docx .\outputs\my_first_review\word\final_review.docx
py scripts\reviewflow.py audit-docx --docx .\outputs\my_first_review\word\final_review.docx
```

For a fuller walkthrough, see [QUICKSTART.md](QUICKSTART.md).

## What the output looks like

```text
outputs/my_review/
  README_PROJECT.md
  .reviewflow/
    state.json

  intake/
    review_brief.md

  protocol/
    review_protocol.md

  literature/
    search_queries.md
    combined_candidates.csv
    combined_candidates.ris
    pubmed_auto.csv
    pubmed_auto.ris
    openalex_auto.csv
    openalex_auto.ris
    auto_search_summary.md

  zotero_exports/

  notes/
    evidence_matrix.csv
    screening_decisions.csv

  tables/
    table_plan.md

  figures/
    figure_plan.md

  draft/
    review_outline.md
    manuscript.md
    codex_prompts.md

  word/
    final_review.docx
    final_review.pdf

  quality/
    codex_handoff.md
    next_prompt_to_codex.md
    quality_check_report.md
    final_check_summary.md

  logs/
    search_log.jsonl
```

## Why this matters for review papers

Review papers are a special case. Unlike many original research manuscripts, they often require:

- broader search coverage;
- more explicit inclusion logic;
- many more citations;
- more comparison tables;
- more risk of reference drift during revision.

That makes them unusually painful to manage with a half-manual workflow.

This repository is built around the idea that **review writing deserves orchestration, not just note-taking**.

## Current Commands

```powershell
py scripts\reviewflow.py --help
```

Available now:

- `check`: inspect local environment assumptions
- `intake`: create a managed review brief and project state
- `init`: initialize a project scaffold directly
- `run`: auto-run machine-doable stages
- `resume`: mark a human checkpoint as completed
- `handoff`: generate the current human checklist
- `final-check`: summarize readiness and remaining risk
- `search-pubmed`: export PubMed results to CSV / RIS
- `search-openalex`: export OpenAlex results to CSV / RIS
- `audit-docx`: statically inspect a Word document for Zotero fields

## Who this is for

- Students writing their first serious review
- Researchers who already use Zotero but want less manual coordination
- Labs that want a repeatable review-writing pipeline
- People who like AI assistance but do not want fake references

## Who this is not for

- People expecting a push-button publishable paper with zero oversight
- Users who do not want Zotero or Word in the final workflow
- Teams that need a Linux-only or browser-only writing stack today

## Docs

- [QUICKSTART.md](QUICKSTART.md)
- [docs/00_portable_project_design.md](docs/00_portable_project_design.md)
- [docs/01_environment_setup.md](docs/01_environment_setup.md)
- [docs/02_review_topic_and_protocol.md](docs/02_review_topic_and_protocol.md)
- [docs/03_literature_search.md](docs/03_literature_search.md)
- [docs/04_zotero_library_management.md](docs/04_zotero_library_management.md)
- [docs/05_reading_notes_and_evidence_matrix.md](docs/05_reading_notes_and_evidence_matrix.md)
- [docs/06_review_tables_and_figures.md](docs/06_review_tables_and_figures.md)
- [docs/07_drafting_with_codex.md](docs/07_drafting_with_codex.md)
- [docs/08_word_zotero_citation_workflow.md](docs/08_word_zotero_citation_workflow.md)
- [docs/09_final_quality_check.md](docs/09_final_quality_check.md)
- [docs/10_publish_to_github.md](docs/10_publish_to_github.md)
- [docs/11_launch_playbook.md](docs/11_launch_playbook.md)

## Positioning You Can Say Publicly

Strong and fair claims:

- "A managed review-writing workflow from zero setup to real Zotero citations in Word."
- "An end-to-end Codex + Zotero + Word pipeline for review papers."
- "A beginner-friendly review copilot that knows when to stop and ask a human."
- "A serious attempt at making literature review writing stateful, resumable, and citation-safe."

Claims to avoid unless you can prove them:

- "The first project in the world to do this."
- "Fully automatic publishable reviews."
- "Zero human involvement."

## Roadmap

See [ROADMAP.md](ROADMAP.md).

Short version:

- Better BibTeX workflow
- Crossref and more databases
- evidence matrix to polished tables
- PRISMA / Mermaid figure generation
- full example project
- stronger multi-language docs

## Contributing

Issues and pull requests are welcome. High-leverage contributions would include:

- more database connectors
- stronger Zotero integration
- better example projects
- cleaner Word / Zotero verification tools
- English polishing and launch assets

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).
