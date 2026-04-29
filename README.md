<div align="center">

# Zotero x Codex Literature Review Workflow

### From zero Zotero setup to a citation-safe literature review paper, with Codex as your managed research copilot.

[![CI](https://github.com/KobeBryant0127/zotero-codex-review-workflow/actions/workflows/ci.yml/badge.svg)](https://github.com/KobeBryant0127/zotero-codex-review-workflow/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Windows](https://img.shields.io/badge/platform-Windows%2010%2F11-blue)](README.md)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](README.md)
[![Research Workflow](https://img.shields.io/badge/focus-literature%20review-0f766e)](README.md)
[![Citation Safe](https://img.shields.io/badge/output-Zotero%20refreshable%20citations-b58900)](README.md)
[![Codex](https://img.shields.io/badge/Codex-orchestration-111827?logo=openai&logoColor=white)](README.md)
[![Zotero](https://img.shields.io/badge/Zotero-reference%20truth-B91C1C?logo=zotero&logoColor=white)](README.md)
[![Word](https://img.shields.io/badge/Word-final%20manuscript-185ABD?logo=microsoftword&logoColor=white)](README.md)

<p>
  <a href="#why-this-repo-exists">Why</a> •
  <a href="#what-makes-this-feel-different">Why it feels different</a> •
  <a href="#managed-workflow">Workflow</a> •
  <a href="#60-second-start">60-second start</a> •
  <a href="#what-you-get">Output</a> •
  <a href="#docs">Docs</a>
</p>

</div>

> **TL;DR**
>
> This repo turns literature review writing into a managed pipeline:
> **Codex runs the workflow, Zotero anchors the references, Word ships the final refreshable citations.**

<p align="center">
  <img src="docs/images/hero-codex-zotero-word.png" alt="Codex, Zotero, and Word powering a citation-safe literature review workflow" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Codex-Workflow%20Brain-111827?logo=openai&logoColor=white" alt="Codex badge">
  <img src="https://img.shields.io/badge/Zotero-Reference%20Truth-B91C1C?logo=zotero&logoColor=white" alt="Zotero badge">
  <img src="https://img.shields.io/badge/Word-Manuscript%20Surface-185ABD?logo=microsoftword&logoColor=white" alt="Word badge">
</p>

---

## At A Glance

<table>
  <tr>
    <td width="25%" align="center">
      <img src="https://img.shields.io/badge/Codex-111827?logo=openai&logoColor=white" alt="Codex badge"><br><br>
      <strong>Managed by Codex</strong><br>
      Handoffs, resume points, prompts, and workflow state stay explicit.
    </td>
    <td width="25%" align="center">
      <img src="https://img.shields.io/badge/Zotero-B91C1C?logo=zotero&logoColor=white" alt="Zotero badge"><br><br>
      <strong>Anchored in Zotero</strong><br>
      References, collections, metadata, PDFs, and citation truth remain grounded.
    </td>
    <td width="25%" align="center">
      <img src="https://img.shields.io/badge/Word-185ABD?logo=microsoftword&logoColor=white" alt="Word badge"><br><br>
      <strong>Delivered in Word</strong><br>
      Final manuscripts keep real in-text citations and bibliography fields.
    </td>
    <td width="25%" align="center">
      <img src="https://img.shields.io/badge/Package-F2C94C?logo=gitbook&logoColor=111827" alt="Package badge"><br><br>
      <strong>Packaged for review</strong><br>
      Evidence matrix, RIS exports, draft assets, and audit trail stay together.
    </td>
  </tr>
</table>

## Why This Repo Exists

Most literature review writing still feels like stitching together five half-connected worlds:

- search manually in databases
- dump papers into Zotero
- read and annotate in an ad hoc way
- draft with placeholder citations
- manually insert dozens or hundreds of Zotero references in Word at the end

That process breaks down hardest on review papers, where citation volume is high, synthesis is wide, and reference drift is easy.

This project exists to compress that pain into one tracked workflow:

- Codex manages the next step
- Zotero remains the source of truth
- Word stays the final scholarly delivery surface
- the repo remembers state, handoffs, and resume points

---

## What Makes This Feel Different

It is not only:

- a Zotero tutorial
- a literature search helper
- a prompt collection
- a Word citation macro
- or a generic AI writing scaffold

It is a **managed literature review workflow** with explicit checkpoints.

| Traditional approach | This repo |
|---|---|
| Search, collect, draft, and cite are loosely connected | One stateful pipeline tracks topic, search, synthesis, drafting, and final citation checks |
| Zotero is often used only at the end | Zotero is treated as the bibliographic truth layer throughout |
| AI may generate text, but workflow still stays manual | Codex orchestrates the workflow and only stops when a human step is truly required |
| Final Word references are easy to break | Final output is designed around Zotero-refreshable Word citations |

<p align="center">
  <img src="docs/images/before-after.png" alt="Traditional literature review workflow versus Codex plus Zotero plus Word workflow" width="100%">
</p>

### The three pillars

| Codex | Zotero | Word |
|---|---|---|
| Orchestrates workflow, handoffs, prompts, and synthesis | Stores references, metadata, collections, PDFs, and citation truth | Holds the final literature review manuscript with real in-text citations and bibliography fields |

### What it can already do

<p>
  <img src="https://img.shields.io/badge/Search-PubMed%20%2B%20OpenAlex-0F172A?logo=googlescholar&logoColor=white" alt="Search badge">
  <img src="https://img.shields.io/badge/State-Handoffs%20%2B%20Resume-0F172A?logo=git&logoColor=white" alt="State badge">
  <img src="https://img.shields.io/badge/Output-RIS%20%2B%20DOCX%20%2B%20CSV-0F172A?logo=microsoftoffice&logoColor=white" alt="Output badge">
  <img src="https://img.shields.io/badge/Check-Zotero%20Field%20Audit-0F172A?logo=checkmarx&logoColor=white" alt="Audit badge">
</p>

- Check whether Python, Zotero, Word, Git, and GitHub CLI are available.
- Create a stateful literature review project for a new topic.
- Generate the brief, protocol, evidence ledger, draft scaffold, and table/figure plans.
- Search PubMed and OpenAlex and export CSV plus Zotero-importable RIS.
- Merge candidate literature into one tracked pool.
- Tell the user exactly when manual Zotero, PDF, or Word steps are required.
- Generate a persistent handoff file and a next-prompt file for Codex.
- Audit whether the final DOCX actually contains Zotero-style fields.
- Produce a final readiness summary for the whole project package.

### What it deliberately does not fake

- It does not claim every generated sentence is academically correct.
- It does not pretend placeholder citations are the same as real Zotero Word fields.
- It does not bypass paywalls or institutional access limits.
- It does not replace human judgment on scope, inclusion, or final claims.

---

## Managed Workflow



<p align="center">
  <img src="docs/images/workflow-overview.png" alt="End-to-end Codex, Zotero, and Word literature review workflow overview" width="100%">
</p>

### The user experience this repo is aiming for

> “Take me from zero to a real literature review draft. Stop only when you truly need me.”

---

## 60-Second Start

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
- Excel or WPS for evidence matrix editing

### 2. Run the environment check

```powershell
powershell -ExecutionPolicy Bypass -File .\START_HERE.ps1
```

or:

```powershell
py scripts\reviewflow.py check
```

### 3. Create a managed literature review project

```powershell
py scripts\reviewflow.py intake --name my_first_review --topic "your literature review topic" --output .\outputs
py scripts\reviewflow.py run --project .\outputs\my_first_review
```

### 4. Follow the handoff

```powershell
py scripts\reviewflow.py handoff --project .\outputs\my_first_review
```

This creates the two files that make the beginner experience work:

- `quality/codex_handoff.md`
- `quality/next_prompt_to_codex.md`

One tells the human what to do next.  
One tells the human what to tell Codex next.

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

For the fuller walkthrough, see [QUICKSTART.md](QUICKSTART.md).

---

## What You Get

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

### Final outputs that matter most

- `word/final_review.docx`
- `word/final_review.pdf`
- `notes/evidence_matrix.csv`
- `literature/combined_candidates.ris`
- `quality/final_check_summary.md`

---

## Why This Matters for Literature Review Papers

Literature review papers are a special case. Compared with many original research manuscripts, they usually require:

- broader search coverage
- more explicit inclusion logic
- many more citations
- more comparison tables
- higher risk of reference drift during revision

That makes them unusually painful to manage with a half-manual workflow.

This repository is built around one belief:

**literature review writing deserves orchestration, not just note-taking.**

---

## Current Commands

```powershell
py scripts\reviewflow.py --help
```

| Command | Purpose |
|---|---|
| `check` | Inspect local environment assumptions |
| `intake` | Create a managed literature review brief and project state |
| `init` | Initialize a project scaffold directly |
| `run` | Auto-run machine-doable stages |
| `resume` | Mark a human checkpoint as completed |
| `handoff` | Generate the current human checklist |
| `final-check` | Summarize readiness and remaining risk |
| `search-pubmed` | Export PubMed results to CSV / RIS |
| `search-openalex` | Export OpenAlex results to CSV / RIS |
| `audit-docx` | Statically inspect a Word document for Zotero fields |

---

## Who This Is For

| Good fit | Not a good fit |
|---|---|
| Students writing their first serious literature review | People expecting a push-button publishable paper with zero oversight |
| Researchers who already use Zotero but want less manual coordination | Users who do not want Zotero or Word in the final workflow |
| Labs that want a repeatable literature-review-writing pipeline | Teams that need a Linux-only or browser-only writing stack today |
| People who like AI assistance but do not want fake references | Anyone looking for paywall bypasses or fake-reference generation |

---

## Positioning You Can Say Publicly

Strong and fair claims:

- “A managed literature-review-writing workflow from zero setup to real Zotero citations in Word.”
- “An end-to-end Codex + Zotero + Word pipeline for literature review papers.”
- “A beginner-friendly literature review copilot that knows when to stop and ask a human.”
- “A serious attempt at making literature review writing stateful, resumable, and citation-safe.”

Claims to avoid unless you can prove them:

- “The first project in the world to do this.”
- “Fully automatic publishable reviews.”
- “Zero human involvement.”

For more launch and messaging guidance, see [docs/11_launch_playbook.md](docs/11_launch_playbook.md).

---

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

---

## Roadmap

See [ROADMAP.md](ROADMAP.md).

Short version:

- Better BibTeX workflow
- Crossref and more databases
- evidence matrix to polished tables
- PRISMA / Mermaid figure generation
- full example project
- stronger multi-language docs

---

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
