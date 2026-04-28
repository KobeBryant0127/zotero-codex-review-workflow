#!/usr/bin/env python3
"""reviewflow.py

Portable orchestrator for a Zotero x Codex review-writing workflow.
It uses Python standard library only so beginners can run it on a new Windows PC.

Core commands:
  check          Check local environment assumptions.
  intake         Create a guided review brief and project state.
  init           Initialize a new review project folder.
  run            Auto-run the next machine-doable stages.
  resume         Mark human checkpoints as done and continue.
  handoff        Generate the current human action checklist.
  final-check    Build a final readiness report.
  search-pubmed  Search PubMed and export CSV/RIS for Zotero import.
  search-openalex Search OpenAlex and export CSV/RIS for Zotero import.
  audit-docx     Inspect a DOCX for Zotero Word fields.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
UA = "zotero-codex-review-workflow/0.2 (educational; local user)"
STATE_VERSION = "0.2"
DEFAULT_OUTPUT = ROOT / "outputs"
DEFAULT_DATABASES = ["pubmed", "openalex"]
MARK_CHOICES = [
    "zotero_imported",
    "pdfs_checked",
    "evidence_ready",
    "draft_ready",
    "citations_inserted",
    "final_docx_ready",
]


def now_iso() -> str:
    return dt.datetime.now().replace(microsecond=0).isoformat()


def safe_slug(text: str) -> str:
    text = text.strip().replace(" ", "_")
    text = re.sub(r"[^0-9A-Za-z_\-\u4e00-\u9fff]+", "", text)
    return text or "review_project"


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    value = str(value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def year_from_date(value: str | None) -> str:
    if not value:
        return ""
    match = re.search(r"(19|20)\d{2}", value)
    return match.group(0) if match else ""


def ris_escape(value: str) -> str:
    return clean_text(value).replace("\n", " ").replace("\r", " ")


def read_url_json(url: str, timeout: int = 30) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8-sig")


def write_json(path: Path, data: Any) -> None:
    write_text(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})


def count_csv_rows(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        rows = list(reader)
    return max(0, len(rows) - 1)


def write_ris(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for row in rows:
        item_type = "JOUR" if row.get("journal") else "GEN"
        lines.append(f"TY  - {item_type}")
        if row.get("title"):
            lines.append(f"TI  - {ris_escape(row['title'])}")
        authors = row.get("authors") or ""
        if isinstance(authors, list):
            author_list = authors
        else:
            author_list = [item.strip() for item in str(authors).split(";") if item.strip()]
        for author in author_list:
            lines.append(f"AU  - {ris_escape(author)}")
        if row.get("year"):
            lines.append(f"PY  - {ris_escape(str(row['year']))}")
        if row.get("journal"):
            lines.append(f"T2  - {ris_escape(row['journal'])}")
            lines.append(f"JO  - {ris_escape(row['journal'])}")
        if row.get("doi"):
            lines.append(f"DO  - {ris_escape(row['doi'])}")
        if row.get("url"):
            lines.append(f"UR  - {ris_escape(row['url'])}")
        if row.get("abstract"):
            lines.append(f"AB  - {ris_escape(row['abstract'])}")
        if row.get("source"):
            lines.append(f"N1  - Source: {ris_escape(row['source'])}")
        if row.get("cited_by_count") not in ("", None):
            lines.append(f"N1  - cited_by_count: {ris_escape(str(row['cited_by_count']))}")
        lines.append("ER  -")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8-sig")


def invert_abstract(index: dict[str, list[int]] | None) -> str:
    if not index:
        return ""
    words: list[tuple[int, str]] = []
    for word, positions in index.items():
        for pos in positions:
            words.append((pos, word))
    return " ".join(word for _, word in sorted(words))


def parse_databases(text: str | None) -> list[str]:
    if not text:
        return list(DEFAULT_DATABASES)
    values = [clean_text(item).lower() for item in text.split(",")]
    return [item for item in values if item]


def project_state_dir(project: Path) -> Path:
    return project / ".reviewflow"


def project_state_path(project: Path) -> Path:
    return project_state_dir(project) / "state.json"


def project_handoff_path(project: Path) -> Path:
    return project / "quality" / "codex_handoff.md"


def project_prompt_path(project: Path) -> Path:
    return project / "quality" / "next_prompt_to_codex.md"


def default_state(project: Path, name: str, topic: str, language: str, review_type: str, audience: str, goal: str, time_range: str) -> dict[str, Any]:
    return {
        "version": STATE_VERSION,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "project_name": name,
        "project_dir": str(project),
        "brief": {
            "topic": topic,
            "language": language,
            "review_type": review_type,
            "audience": audience,
            "goal": goal,
            "time_range": time_range,
            "databases": ["PubMed", "OpenAlex"],
        },
        "search": {
            "databases": list(DEFAULT_DATABASES),
            "max_results": 30,
            "queries": {},
            "outputs": {},
            "records": {},
        },
        "artifacts": {
            "combined_candidates_csv": "",
            "combined_candidates_ris": "",
            "final_docx": "",
            "final_docx_audit_report": "",
        },
        "checkpoints": {
            "intake_completed": True,
            "project_initialized": True,
            "searches_completed": False,
            "zotero_imported": False,
            "pdfs_checked": False,
            "evidence_ready": False,
            "draft_ready": False,
            "citations_inserted": False,
            "final_docx_ready": False,
            "final_check_completed": False,
        },
        "history": [
            {
                "time": now_iso(),
                "event": "project_initialized",
                "detail": "Project scaffold created.",
            }
        ],
    }


def load_state(project: Path) -> dict[str, Any]:
    path = project_state_path(project)
    if not path.exists():
        raise FileNotFoundError(f"State file not found: {path}")
    return read_json(path)


def save_state(project: Path, state: dict[str, Any]) -> None:
    state["updated_at"] = now_iso()
    write_json(project_state_path(project), state)


def ensure_checkpoint_defaults(state: dict[str, Any]) -> None:
    checkpoints = state.setdefault("checkpoints", {})
    for name in [
        "intake_completed",
        "project_initialized",
        "searches_completed",
        "zotero_imported",
        "pdfs_checked",
        "evidence_ready",
        "draft_ready",
        "citations_inserted",
        "final_docx_ready",
        "final_check_completed",
    ]:
        checkpoints.setdefault(name, False)


def resolve_project(args: argparse.Namespace, allow_missing: bool = False) -> Path:
    project_arg = getattr(args, "project", "")
    if project_arg:
        project = Path(project_arg).expanduser().resolve()
    else:
        name = getattr(args, "name", "") or safe_slug(getattr(args, "topic", "review_project"))
        output = Path(getattr(args, "output", DEFAULT_OUTPUT)).expanduser().resolve()
        project = output / safe_slug(name)
    if not allow_missing and not project.exists():
        raise FileNotFoundError(f"Project not found: {project}")
    return project


def merge_candidate_rows(groups: list[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    seen: set[str] = set()
    for rows in groups:
        for row in rows:
            doi = clean_text(row.get("doi", "")).lower()
            title = clean_text(row.get("title", "")).lower()
            key = doi or title
            if not key or key in seen:
                continue
            seen.add(key)
            merged.append(
                {
                    "source": row.get("source", ""),
                    "title": row.get("title", ""),
                    "authors": row.get("authors", ""),
                    "year": row.get("year", ""),
                    "journal": row.get("journal", ""),
                    "doi": row.get("doi", ""),
                    "url": row.get("url", ""),
                    "cited_by_count": row.get("cited_by_count", ""),
                    "abstract": row.get("abstract", ""),
                }
            )
    return merged


def build_review_brief(topic: str, language: str, review_type: str, audience: str, goal: str, time_range: str) -> str:
    return f"""# Review Brief

## Required inputs

- Topic: {topic or "[fill me]"}
- Review type: {review_type or "[fill me]"}
- Language: {language or "[fill me]"}
- Audience: {audience or "[fill me]"}
- Goal / deliverable: {goal or "[fill me]"}
- Time range: {time_range or "[fill me]"}

## Guidance for a beginner

Use this file to tell Codex exactly what you want.

Suggested prompt:

```text
I want you to act as my review-writing copilot. Read this project, use the review brief below, and take me from literature search to a Word draft with Zotero-ready citations. Only stop when you truly need me to do something manually, and when you stop, tell me exactly what to do and what to send back to you.
```

## Topic framing

- Core question:
- Why this review matters:
- Inclusion boundary:
- Exclusion boundary:
- Target journals / course requirements:

## Constraints

- Databases I can access:
- Whether I need Chinese + English sources:
- Whether I need only high-impact / classic / recent papers:
- Deadline:

## Human-only checkpoints

- Approve the review scope.
- Confirm import into Zotero.
- Confirm Word Zotero plugin worked.
- Confirm final claims are acceptable.
"""


def build_protocol(topic: str, language: str, review_type: str, audience: str, goal: str, time_range: str) -> str:
    return f"""# 综述写作协议

## 基本信息

- 综述题目：{topic}
- 综述类型：{review_type}
- 目标期刊/用途：{goal}
- 目标读者：{audience}
- 语言：{language}

## 核心问题

1.
2.
3.

## 纳入标准

- 时间范围：{time_range}
- 文献类型：
- 研究对象/数据集：
- 方法/技术：
- 语言：

## 排除标准

-
-

## 数据库与检索式

- PubMed:
- Web of Science:
- Scopus:
- OpenAlex:
- Google Scholar:
- 其他：

## 计划表格

1. 经典/高影响文献表
2. 方法/主题比较表

## 计划图

1. 领域框架图
2. 研究发展时间线或证据地图
"""


def scaffold_project(project: Path, name: str, topic: str, language: str, review_type: str, audience: str, goal: str, time_range: str) -> dict[str, Any]:
    project.mkdir(parents=True, exist_ok=True)
    for folder in [
        "intake",
        "protocol",
        "literature",
        "zotero_exports",
        "notes",
        "tables",
        "figures",
        "draft",
        "word",
        "quality",
        "logs",
        ".reviewflow",
    ]:
        (project / folder).mkdir(exist_ok=True)

    state = default_state(project, name, topic, language, review_type, audience, goal, time_range)

    write_text(
        project / "README_PROJECT.md",
        f"""# {name}

综述主题：{topic}

## 工作模式

这个项目现在支持“Codex 托管式推进”：

1. `intake`：生成需求简报；
2. `run`：自动执行机器能完成的阶段；
3. `handoff`：当需要你人工介入时，生成明确清单；
4. `resume`：你完成人工步骤后，标记并继续；
5. `final-check`：最终质控。

## 最重要的文件

- `intake/review_brief.md`
- `protocol/review_protocol.md`
- `literature/combined_candidates.csv`
- `literature/combined_candidates.ris`
- `notes/evidence_matrix.csv`
- `draft/manuscript.md`
- `quality/codex_handoff.md`

## 常用命令

```powershell
py "{ROOT / 'scripts' / 'reviewflow.py'}" run --project "{project}"
py "{ROOT / 'scripts' / 'reviewflow.py'}" handoff --project "{project}"
py "{ROOT / 'scripts' / 'reviewflow.py'}" resume --project "{project}" --mark zotero_imported
py "{ROOT / 'scripts' / 'reviewflow.py'}" final-check --project "{project}"
```
""",
    )
    write_text(project / "intake" / "review_brief.md", build_review_brief(topic, language, review_type, audience, goal, time_range))
    write_text(project / "protocol" / "review_protocol.md", build_protocol(topic, language, review_type, audience, goal, time_range))
    write_text(
        project / "literature" / "search_queries.md",
        f"""# 检索式记录

主题：{topic}

## PubMed

```text
{topic}
```

## OpenAlex

```text
{topic}
```

## Web of Science / Scopus

```text

```

## 检索日志

| 日期 | 数据库 | 检索式 | 结果数 | 导出文件 | 备注 |
|---|---|---|---:|---|---|
|  |  |  |  |  |  |
""",
    )
    write_text(project / "literature" / "candidates.csv", "CitationKey,Authors,Year,Title,Journal,DOI,URL,Source,Decision,Reason,Tags\n")
    write_text(project / "literature" / "combined_candidates.csv", "source,title,authors,year,journal,doi,url,cited_by_count,abstract\n")
    write_text(project / "literature" / "combined_candidates.ris", "")
    write_text(project / "notes" / "evidence_matrix.csv", "CitationKey,Claim,Evidence,QuoteOrPage,StudyType,PopulationOrDataset,Method,MainFinding,Limitation,Section,Confidence,NeedsVerification\n")
    write_text(project / "notes" / "screening_decisions.csv", "Title,Decision,Reason,Priority,PDFStatus,Notes\n")
    write_text(project / "tables" / "table_plan.md", "# 综述表格计划\n\n| 表格 | 目的 | 数据来源 | 状态 |\n|---|---|---|---|\n| Table 1 经典/高影响文献 | 梳理发展脉络 | evidence_matrix | todo |\n| Table 2 方法/主题比较 | 比较路线和局限 | evidence_matrix | todo |\n")
    write_text(project / "figures" / "figure_plan.md", "# 综述图计划\n\n| 图 | 目的 | 形式 | 状态 |\n|---|---|---|---|\n| Figure 1 领域框架图 | 解释综述结构 | Mermaid/PowerPoint | todo |\n| Figure 2 时间线/证据地图 | 展示发展和证据 | Mermaid/Excel/PowerPoint | todo |\n")
    write_text(
        project / "draft" / "review_outline.md",
        f"""# 综述大纲：{topic}

## Title

{topic}

## Abstract

- Background:
- Objective:
- Main themes:
- Conclusion:

## 1. Introduction

## 2. Search and Selection Strategy

## 3. Conceptual Background

## 4. Main Theme 1

## 5. Main Theme 2

## 6. Main Theme 3

## 7. Challenges and Limitations

## 8. Future Directions

## 9. Conclusion

## References

由 Zotero 在 Word 中生成。
""",
    )
    write_text(
        project / "draft" / "manuscript.md",
        f"""# {topic}

> 写作规则：所有事实性论断后先放 `[CitationKey]`，最后在 Word 中用 Zotero 插件替换为真实引用。

## Introduction


## Search and Selection Strategy


## Conceptual Background


## Main Themes


## Challenges and Future Directions


## Conclusion
""",
    )
    write_text(
        project / "draft" / "codex_prompts.md",
        f"""# Codex 托管工作提示词

## 让 Codex 接管项目

```text
Read this repository and this project directory. Treat yourself as my review-writing copilot. Continue automatically whenever you can. Stop only when you truly need me to do something manual, and when you stop, give me a short checklist plus the exact next prompt I should send back to you.
```

## 主题拆解

```text
我准备写一篇关于“{topic}”的综述。请帮我拆解核心问题、同义词、检索关键词、章节结构和表图设计。不要编造具体文献。
```

## 文献矩阵归纳

```text
下面是 evidence matrix。请归纳主题簇、共识、冲突发现、研究空白和可视化建议。不要新增文献。
```

## 段落写作

```text
请基于以下证据写一段综述正文。每个事实性论断后保留 [CitationKey]，不要编造文献。
```
""",
    )
    write_text(
        project / "quality" / "quality_check_report.md",
        """# 质量检查报告

## 内容

- [ ] 主题边界清楚
- [ ] 每个关键论断有证据
- [ ] 覆盖经典、高影响、前沿文献
- [ ] 有比较、归纳、批判，而非罗列

## Zotero/Word

- [ ] Zotero 条目元数据完整
- [ ] Word 中引用是真 Zotero 字段
- [ ] Bibliography 是 Zotero 管理字段
- [ ] Zotero Refresh 后引用不消失
- [ ] audit-docx 通过

## 表图

- [ ] 表格标题、列名、注释完整
- [ ] 图可以独立解释综述框架
- [ ] 表图与正文互相引用
""",
    )
    write_text(
        project / "quality" / "manual_checkpoints.md",
        """# Manual Checkpoints

这些步骤无法完全自动完成，Codex 会在这些点上停下来叫你：

1. 确认综述主题和边界；
2. 把 RIS 导入 Zotero，并确认 collection 建好了；
3. 检查关键文献是否有 PDF / 元数据是否正确；
4. 在 Word 里用 Zotero 插件插入正式引用；
5. 确认最终结论符合你的学术判断。
""",
    )
    save_state(project, state)
    render_handoff(project, state)
    return state


def search_pubmed(query: str, retmax: int) -> list[dict[str, Any]]:
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    params = urllib.parse.urlencode({"db": "pubmed", "term": query, "retmode": "json", "retmax": retmax, "sort": "relevance"})
    esearch = read_url_json(f"{base}/esearch.fcgi?{params}")
    ids = esearch.get("esearchresult", {}).get("idlist", [])
    rows: list[dict[str, Any]] = []
    if not ids:
        return rows
    params2 = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(ids), "retmode": "json"})
    esummary = read_url_json(f"{base}/esummary.fcgi?{params2}")
    result = esummary.get("result", {})
    for pmid in result.get("uids", ids):
        item = result.get(pmid, {})
        articleids = item.get("articleids", []) or []
        doi = ""
        for aid in articleids:
            if aid.get("idtype") == "doi":
                doi = aid.get("value", "")
        authors = [entry.get("name", "") for entry in item.get("authors", []) if entry.get("name")]
        rows.append(
            {
                "source": "PubMed",
                "pmid": pmid,
                "title": clean_text(item.get("title", "")),
                "authors": "; ".join(authors),
                "year": year_from_date(item.get("pubdate", "")),
                "journal": clean_text(item.get("fulljournalname") or item.get("source", "")),
                "doi": doi,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "cited_by_count": "",
                "abstract": "",
            }
        )
    return rows


def search_openalex(query: str, per_page: int) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode({"search": query, "per-page": per_page, "sort": "cited_by_count:desc"})
    data = read_url_json(f"https://api.openalex.org/works?{params}")
    rows: list[dict[str, Any]] = []
    for item in data.get("results", []):
        authors: list[str] = []
        for author_row in item.get("authorships", []) or []:
            name = (author_row.get("author") or {}).get("display_name")
            if name:
                authors.append(name)
        src = ((item.get("primary_location") or {}).get("source") or {}).get("display_name", "")
        doi = item.get("doi") or ""
        rows.append(
            {
                "source": "OpenAlex",
                "openalex_id": item.get("id", ""),
                "title": clean_text(item.get("title", "")),
                "authors": "; ".join(authors),
                "year": item.get("publication_year", ""),
                "journal": clean_text(src),
                "doi": doi.replace("https://doi.org/", "") if doi else "",
                "url": item.get("doi") or item.get("id", ""),
                "cited_by_count": item.get("cited_by_count", ""),
                "abstract": invert_abstract(item.get("abstract_inverted_index")),
            }
        )
    return rows


def write_search_outputs(project: Path, db_name: str, rows: list[dict[str, Any]]) -> dict[str, str]:
    prefix = project / "literature" / f"{db_name}_auto"
    csv_path = prefix.with_suffix(".csv")
    ris_path = prefix.with_suffix(".ris")
    if db_name == "pubmed":
        fields = ["source", "pmid", "title", "authors", "year", "journal", "doi", "url", "cited_by_count", "abstract"]
    else:
        fields = ["source", "openalex_id", "title", "authors", "year", "journal", "doi", "url", "cited_by_count", "abstract"]
    write_csv(csv_path, rows, fields)
    write_ris(ris_path, rows)
    return {"csv": str(csv_path), "ris": str(ris_path)}


def render_state_summary(state: dict[str, Any]) -> str:
    checkpoints = state["checkpoints"]
    lines = [
        f"- Intake completed: {checkpoints['intake_completed']}",
        f"- Project initialized: {checkpoints['project_initialized']}",
        f"- Searches completed: {checkpoints['searches_completed']}",
        f"- Zotero import confirmed: {checkpoints['zotero_imported']}",
        f"- PDFs checked: {checkpoints['pdfs_checked']}",
        f"- Evidence matrix ready: {checkpoints['evidence_ready']}",
        f"- Draft ready: {checkpoints['draft_ready']}",
        f"- Word citations inserted: {checkpoints['citations_inserted']}",
        f"- Final DOCX ready: {checkpoints['final_docx_ready']}",
        f"- Final check completed: {checkpoints['final_check_completed']}",
    ]
    return "\n".join(lines)


def compute_human_tasks(project: Path, state: dict[str, Any]) -> list[dict[str, str]]:
    checkpoints = state["checkpoints"]
    artifacts = state.get("artifacts", {})
    tasks: list[dict[str, str]] = []

    if not checkpoints["zotero_imported"]:
        tasks.append(
            {
                "title": "Import the auto-generated RIS into Zotero",
                "why": "Codex can collect candidates, but Zotero import and collection setup still need a real Zotero library on your machine.",
                "done_when": "A dedicated Zotero collection exists for this review and the imported references look correct.",
                "prompt": "I have imported the RIS into Zotero and checked the collection. Continue.",
            }
        )
    if checkpoints["zotero_imported"] and not checkpoints["pdfs_checked"]:
        tasks.append(
            {
                "title": "Check whether the core papers have PDFs and acceptable metadata",
                "why": "Codex should not reason from empty metadata or missing full-text when the review depends on deeper evidence extraction.",
                "done_when": "You have looked at the highest-priority papers and marked missing PDFs / broken metadata in notes/screening_decisions.csv.",
                "prompt": "I checked the PDFs and metadata. Continue using the screening decisions file.",
            }
        )
    if checkpoints["pdfs_checked"] and not checkpoints["evidence_ready"]:
        tasks.append(
            {
                "title": "Fill or verify the evidence matrix",
                "why": "This is the main evidence ledger for the review. Codex can draft from it, but the source claims need a human sanity check.",
                "done_when": "notes/evidence_matrix.csv contains the core claims, methods, findings, and limitations for the main papers.",
                "prompt": "The evidence matrix is ready. Draft the review structure and first-pass manuscript.",
            }
        )
    if checkpoints["evidence_ready"] and not checkpoints["draft_ready"]:
        tasks.append(
            {
                "title": "Review the draft for scope and argument quality",
                "why": "Codex can draft quickly, but the review still needs your subject-level approval before it goes into Word.",
                "done_when": "You accept the Markdown draft as a good basis for the final Word version.",
                "prompt": "The Markdown draft looks good. Continue to the Word/Zotero citation stage.",
            }
        )
    if checkpoints["draft_ready"] and not checkpoints["citations_inserted"]:
        tasks.append(
            {
                "title": "Insert official Zotero citations inside Word",
                "why": "The final paper must use real Zotero Word fields, not placeholder text.",
                "done_when": "The Word file has Zotero-managed in-text citations and a Zotero bibliography.",
                "prompt": "I inserted the Zotero citations in Word. Continue with final checks.",
            }
        )
    if checkpoints["citations_inserted"] and not checkpoints["final_docx_ready"]:
        tasks.append(
            {
                "title": "Save the final Word document into the project",
                "why": "Codex needs a stable file path to audit the final Zotero fields.",
                "done_when": f"A DOCX such as `{project / 'word' / 'final_review.docx'}` exists.",
                "prompt": "The final DOCX is saved in the project. Continue with final-check.",
            }
        )
    if checkpoints["final_docx_ready"] and not checkpoints["final_check_completed"]:
        tasks.append(
            {
                "title": "Run the final readiness check",
                "why": "This ensures the project has the expected evidence, draft, and Zotero field structure before you call it finished.",
                "done_when": "final-check reports that the package is ready or clearly lists the remaining gaps.",
                "prompt": "Run the final readiness check and summarize the remaining risks.",
            }
        )
    if not tasks:
        tasks.append(
            {
                "title": "No blocking human task right now",
                "why": "The project appears to have cleared the main checkpoints.",
                "done_when": "You are happy with the paper and any remaining polish.",
                "prompt": "Summarize the final review package and remaining improvement ideas.",
            }
        )
    return tasks


def next_codex_prompt(state: dict[str, Any]) -> str:
    checkpoints = state["checkpoints"]
    topic = state["brief"]["topic"]
    if not checkpoints["zotero_imported"]:
        return (
            f"I am working on the review topic '{topic}'. "
            "Use the generated candidate files and tell me exactly how to import them into Zotero, "
            "what collection structure to create, and what to verify before we continue."
        )
    if checkpoints["zotero_imported"] and not checkpoints["pdfs_checked"]:
        return (
            "Use the imported Zotero library as the source of truth. "
            "Tell me how to mark missing PDFs and metadata problems in notes/screening_decisions.csv, "
            "and then help me prioritize the first papers to read."
        )
    if checkpoints["pdfs_checked"] and not checkpoints["evidence_ready"]:
        return (
            "Use notes/evidence_matrix.csv and notes/screening_decisions.csv as the current evidence base. "
            "Help me turn the main papers into a reliable evidence matrix and identify missing evidence."
        )
    if checkpoints["evidence_ready"] and not checkpoints["draft_ready"]:
        return (
            "The evidence matrix is ready. Draft the review outline, main comparison tables, figure plan, "
            "and a first-pass manuscript while preserving citation placeholders."
        )
    if checkpoints["draft_ready"] and not checkpoints["citations_inserted"]:
        return (
            "The Markdown draft is approved. Walk me through moving it to Word and inserting official Zotero citations "
            "plus the bibliography without losing the structure."
        )
    if checkpoints["citations_inserted"] and not checkpoints["final_docx_ready"]:
        return (
            "The Word citations are inserted. Tell me where to save the final DOCX in the project and what filename to use "
            "so you can audit it."
        )
    if checkpoints["final_docx_ready"] and not checkpoints["final_check_completed"]:
        return "Run the final-check stage and summarize the remaining quality risks."
    return "Summarize the completed review workflow, the final artifacts, and the best next improvements."


def render_handoff(project: Path, state: dict[str, Any]) -> None:
    tasks = compute_human_tasks(project, state)
    prompt = next_codex_prompt(state)
    lines = [
        "# Codex Handoff",
        "",
        f"- Project: {state['project_name']}",
        f"- Topic: {state['brief']['topic']}",
        f"- Last updated: {state['updated_at']}",
        "",
        "## Current state",
        "",
        render_state_summary(state),
        "",
        "## Human tasks",
        "",
    ]
    for idx, task in enumerate(tasks, start=1):
        lines.extend(
            [
                f"### Task {idx}: {task['title']}",
                "",
                f"- Why: {task['why']}",
                f"- Done when: {task['done_when']}",
                f"- Suggested reply to Codex: {task['prompt']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Next prompt to Codex",
            "",
            "```text",
            prompt,
            "```",
            "",
        ]
    )
    write_text(project_handoff_path(project), "\n".join(lines))
    write_text(project_prompt_path(project), prompt + "\n")


def note_history(state: dict[str, Any], event: str, detail: str) -> None:
    state.setdefault("history", []).append({"time": now_iso(), "event": event, "detail": detail})


def append_search_log(project: Path, db_name: str, query: str, count: int, csv_path: Path) -> None:
    log_path = project / "logs" / "search_log.jsonl"
    line = json.dumps(
        {
            "time": now_iso(),
            "database": db_name,
            "query": query,
            "results": count,
            "csv": str(csv_path),
        },
        ensure_ascii=False,
    )
    with log_path.open("a", encoding="utf-8-sig") as handle:
        handle.write(line + "\n")


def run_machine_stages(project: Path, state: dict[str, Any], databases: list[str], max_results: int, refresh_search: bool = False) -> list[str]:
    messages: list[str] = []
    search_outputs: dict[str, dict[str, str]] = state["search"].setdefault("outputs", {})
    search_records: dict[str, int] = state["search"].setdefault("records", {})
    state["search"]["databases"] = databases
    state["search"]["max_results"] = max_results

    all_rows: list[list[dict[str, Any]]] = []
    queries: dict[str, str] = state["search"].setdefault("queries", {})
    topic = state["brief"]["topic"]

    for db_name in databases:
        query = queries.get(db_name) or topic
        queries[db_name] = query

        if db_name == "pubmed":
            rows = search_pubmed(query, max_results)
        elif db_name == "openalex":
            rows = search_openalex(query, max_results)
        else:
            messages.append(f"Skipped unsupported database: {db_name}")
            continue

        outputs = write_search_outputs(project, db_name, rows)
        search_outputs[db_name] = outputs
        search_records[db_name] = len(rows)
        append_search_log(project, db_name, query, len(rows), Path(outputs["csv"]))
        all_rows.append(rows)
        messages.append(f"{db_name}: {len(rows)} records")

    combined_rows = merge_candidate_rows(all_rows)
    combined_csv = project / "literature" / "combined_candidates.csv"
    combined_ris = project / "literature" / "combined_candidates.ris"
    combined_fields = ["source", "title", "authors", "year", "journal", "doi", "url", "cited_by_count", "abstract"]
    write_csv(combined_csv, combined_rows, combined_fields)
    write_ris(combined_ris, combined_rows)

    artifacts = state.setdefault("artifacts", {})
    artifacts["combined_candidates_csv"] = str(combined_csv)
    artifacts["combined_candidates_ris"] = str(combined_ris)
    state["checkpoints"]["searches_completed"] = True
    note_history(
        state,
        "searches_completed",
        f"Searched {', '.join(databases)} and wrote {len(combined_rows)} merged candidate rows.",
    )

    summary_md = [
        "# Auto Search Summary",
        "",
        f"- Topic: {topic}",
        f"- Databases: {', '.join(databases)}",
        f"- Max results per database: {max_results}",
        "",
        "## Result counts",
        "",
    ]
    for name in databases:
        summary_md.append(f"- {name}: {search_records.get(name, 0)}")
    summary_md.extend(
        [
            "",
            f"- Merged candidates: {len(combined_rows)}",
            f"- CSV: `{combined_csv}`",
            f"- RIS: `{combined_ris}`",
            "",
            "## Next expected manual step",
            "",
            "Import `combined_candidates.ris` into Zotero and check the first-pass metadata.",
        ]
    )
    write_text(project / "literature" / "auto_search_summary.md", "\n".join(summary_md))
    render_handoff(project, state)
    save_state(project, state)
    return messages


def run_final_check(project: Path, state: dict[str, Any], docx_override: str = "") -> dict[str, Any]:
    docx_path = Path(docx_override).expanduser().resolve() if docx_override else None
    if docx_path is None:
        artifact_docx = state.get("artifacts", {}).get("final_docx", "")
        docx_path = Path(artifact_docx).resolve() if artifact_docx else project / "word" / "final_review.docx"

    evidence_rows = count_csv_rows(project / "notes" / "evidence_matrix.csv")
    candidate_rows = count_csv_rows(project / "literature" / "combined_candidates.csv")
    manuscript_chars = len((project / "draft" / "manuscript.md").read_text(encoding="utf-8-sig")) if (project / "draft" / "manuscript.md").exists() else 0

    report: dict[str, Any] = {
        "project": str(project),
        "topic": state["brief"]["topic"],
        "candidate_rows": candidate_rows,
        "evidence_rows": evidence_rows,
        "manuscript_chars": manuscript_chars,
        "checkpoints": state["checkpoints"],
        "docx_exists": docx_path.exists(),
        "docx": str(docx_path),
        "docx_audit": None,
        "ready_for_manual_submission_review": False,
        "remaining_gaps": [],
    }

    if candidate_rows == 0:
        report["remaining_gaps"].append("No merged candidate literature file was populated.")
    if evidence_rows == 0:
        report["remaining_gaps"].append("Evidence matrix is still empty.")
    if manuscript_chars < 200:
        report["remaining_gaps"].append("Manuscript draft is still very short.")
    if not state["checkpoints"]["citations_inserted"]:
        report["remaining_gaps"].append("Word/Zotero citations are not yet confirmed.")
    if not docx_path.exists():
        report["remaining_gaps"].append("Final DOCX not found in the project.")

    if docx_path.exists():
        audit = audit_docx_file(docx_path)
        report["docx_audit"] = audit
        if audit["zotero_item_count"] == 0:
            report["remaining_gaps"].append("DOCX does not appear to contain Zotero item fields.")
        if not audit["passes_basic_structure_check"]:
            report["remaining_gaps"].append("DOCX Zotero field structure check failed.")

    report["ready_for_manual_submission_review"] = not report["remaining_gaps"]
    state["checkpoints"]["final_check_completed"] = report["ready_for_manual_submission_review"]
    if docx_path.exists():
        state["artifacts"]["final_docx"] = str(docx_path)
        state["checkpoints"]["final_docx_ready"] = True
    report_path = project / "quality" / "final_check_summary.md"
    write_text(
        report_path,
        "# Final Check Summary\n\n```json\n" + json.dumps(report, ensure_ascii=False, indent=2) + "\n```\n",
    )
    state["artifacts"]["final_docx_audit_report"] = str(report_path)
    note_history(state, "final_check", "Final readiness report generated.")
    render_handoff(project, state)
    save_state(project, state)
    return report


def audit_docx_file(docx: Path) -> dict[str, Any]:
    xml_files = ["word/document.xml", "word/footnotes.xml", "word/endnotes.xml"]
    combined = ""
    found_files: list[str] = []
    with zipfile.ZipFile(docx) as handle:
        for name in xml_files:
            if name in handle.namelist():
                combined += "\n" + handle.read(name).decode("utf-8", errors="replace")
                found_files.append(name)

    zotero_item_count = combined.count("ZOTERO_ITEM")
    zotero_bibl_count = combined.count("ZOTERO_BIBL")
    addin_count = combined.count("ADDIN ZOTERO")
    field_begin_count = combined.count('w:fldCharType="begin"') + combined.count("w:fldCharType='begin'")
    field_separate_count = combined.count('w:fldCharType="separate"') + combined.count("w:fldCharType='separate'")
    field_end_count = combined.count('w:fldCharType="end"') + combined.count("w:fldCharType='end'")
    visible_text = re.sub(r"<[^>]+>", " ", combined)
    visible_text = re.sub(r"\s+", " ", visible_text)
    parenthetical_candidates = re.findall(r"\([A-Z][A-Za-zÀ-ÿ'\-]+(?: et al\.)?,? \d{4}[a-z]?[^)]{0,80}\)", visible_text)

    return {
        "docx": str(docx),
        "xml_files_scanned": found_files,
        "addin_zotero_count": addin_count,
        "zotero_item_count": zotero_item_count,
        "zotero_bibl_count": zotero_bibl_count,
        "field_begin_count": field_begin_count,
        "field_separate_count": field_separate_count,
        "field_end_count": field_end_count,
        "parenthetical_text_candidates_count": len(parenthetical_candidates),
        "parenthetical_text_candidates_sample": parenthetical_candidates[:10],
        "passes_basic_structure_check": bool(
            zotero_item_count >= 0
            and field_begin_count >= addin_count
            and field_end_count >= addin_count
            and (addin_count == 0 or field_separate_count >= min(addin_count, zotero_item_count + zotero_bibl_count))
        ),
        "note": "This is a static DOCX XML audit. Final validation still requires opening Word and running Zotero Refresh.",
    }


def command_check(args: argparse.Namespace) -> int:
    print("== System ==")
    print(f"Python: {sys.version.split()[0]} ({sys.executable})")
    print(f"OS: {platform.platform()}")
    print(f"Project root: {ROOT}")

    print("\n== Commands ==")
    for cmd in ["py", "python", "zotero", "winword", "git", "gh"]:
        found = shutil.which(cmd)
        print(f"{cmd}: {found or 'not found in PATH'}")

    print("\n== Common Windows install paths ==")
    common = [
        Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Zotero" / "zotero.exe",
        Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Zotero" / "zotero.exe",
    ]
    for path in common:
        print(f"{'[OK]' if path.exists() else '[--]'} {path}")

    if platform.system().lower().startswith("win"):
        print("\n== Running processes: zotero/winword ==")
        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "Get-Process | Where-Object { $_.ProcessName -match 'zotero|winword' } | Select-Object ProcessName,Id,Path | Format-Table -AutoSize",
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )
            print(result.stdout.strip() or "No Zotero/Word process currently running.")
        except Exception as exc:
            print(f"Could not query processes via PowerShell: {exc}")

    print("\n== Next ==")
    print('Start a managed review project: py scripts\\reviewflow.py intake --name my_review --topic "your topic" --output .\\outputs')
    return 0


def command_init(args: argparse.Namespace) -> int:
    topic = args.topic.strip()
    name = safe_slug(args.name)
    project = Path(args.output).expanduser().resolve() / name
    scaffold_project(project, name, topic, args.language, args.review_type, args.audience, args.goal, args.time_range)
    print(f"Created review project: {project}")
    print("Next:")
    print(f"  py {ROOT / 'scripts' / 'reviewflow.py'} run --project \"{project}\"")
    return 0


def command_intake(args: argparse.Namespace) -> int:
    topic = clean_text(args.topic)
    name = safe_slug(args.name or topic or "review_project")
    project = Path(args.output).expanduser().resolve() / name
    state = scaffold_project(project, name, topic, args.language, args.review_type, args.audience, args.goal, args.time_range)
    note_history(state, "intake_created", "Review brief created.")
    save_state(project, state)
    render_handoff(project, state)
    print(f"Prepared guided intake project: {project}")
    print(f"Review brief: {project / 'intake' / 'review_brief.md'}")
    print(f"Next prompt file: {project_prompt_path(project)}")
    return 0


def command_run(args: argparse.Namespace) -> int:
    project = resolve_project(args, allow_missing=True)
    if project.exists() and project_state_path(project).exists():
        state = load_state(project)
        ensure_checkpoint_defaults(state)
    else:
        topic = clean_text(args.topic)
        if not topic:
            print("A topic is required when creating a new managed project.", file=sys.stderr)
            return 2
        name = project.name
        state = scaffold_project(project, name, topic, args.language, args.review_type, args.audience, args.goal, args.time_range)
        note_history(state, "run_bootstrap", "Project created through the run command.")

    databases = parse_databases(args.databases)
    messages = run_machine_stages(project, state, databases, args.max, args.refresh_search)
    print(f"Managed run finished for: {project}")
    for message in messages:
        print(f"- {message}")
    print(f"Handoff: {project_handoff_path(project)}")
    print(f"Next prompt: {project_prompt_path(project)}")
    return 0


def command_resume(args: argparse.Namespace) -> int:
    project = resolve_project(args)
    state = load_state(project)
    ensure_checkpoint_defaults(state)
    for mark in args.mark:
        if mark == "zotero_imported":
            state["checkpoints"]["zotero_imported"] = True
            note_history(state, mark, "Human confirmed Zotero import.")
        elif mark == "pdfs_checked":
            state["checkpoints"]["pdfs_checked"] = True
            note_history(state, mark, "Human checked PDFs and metadata.")
        elif mark == "evidence_ready":
            state["checkpoints"]["evidence_ready"] = True
            note_history(state, mark, "Human confirmed evidence matrix readiness.")
        elif mark == "draft_ready":
            state["checkpoints"]["draft_ready"] = True
            note_history(state, mark, "Human approved the Markdown draft.")
        elif mark == "citations_inserted":
            state["checkpoints"]["citations_inserted"] = True
            note_history(state, mark, "Human inserted Zotero citations in Word.")
        elif mark == "final_docx_ready":
            state["checkpoints"]["final_docx_ready"] = True
            note_history(state, mark, "Human confirmed the final DOCX exists.")

    if args.docx:
        docx = Path(args.docx).expanduser().resolve()
        state["artifacts"]["final_docx"] = str(docx)
        state["checkpoints"]["final_docx_ready"] = docx.exists()
        note_history(state, "final_docx_path_set", f"Set final DOCX path to {docx}.")

    render_handoff(project, state)
    save_state(project, state)

    if args.auto_final_check and state["checkpoints"]["final_docx_ready"]:
        report = run_final_check(project, state, state["artifacts"].get("final_docx", ""))
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Resume markers recorded for: {project}")
        print(f"Handoff: {project_handoff_path(project)}")
        print(f"Next prompt: {project_prompt_path(project)}")
    return 0


def command_handoff(args: argparse.Namespace) -> int:
    project = resolve_project(args)
    state = load_state(project)
    ensure_checkpoint_defaults(state)
    render_handoff(project, state)
    print(project_handoff_path(project))
    print(project_prompt_path(project))
    return 0


def command_final_check(args: argparse.Namespace) -> int:
    project = resolve_project(args)
    state = load_state(project)
    ensure_checkpoint_defaults(state)
    report = run_final_check(project, state, args.docx)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def command_search_pubmed(args: argparse.Namespace) -> int:
    query = args.query.strip()
    rows = search_pubmed(query, max(1, min(int(args.max), 200)))
    out = Path(args.out).expanduser().resolve()
    fields = ["source", "pmid", "title", "authors", "year", "journal", "doi", "url", "cited_by_count", "abstract"]
    write_csv(out.with_suffix(".csv"), rows, fields)
    write_ris(out.with_suffix(".ris"), rows)
    print(f"PubMed query: {query}")
    print(f"Records: {len(rows)}")
    print(f"CSV: {out.with_suffix('.csv')}")
    print(f"RIS: {out.with_suffix('.ris')}")
    print("Import RIS into Zotero: File -> Import -> select .ris")
    return 0


def command_search_openalex(args: argparse.Namespace) -> int:
    query = args.query.strip()
    rows = search_openalex(query, max(1, min(int(args.max), 200)))
    out = Path(args.out).expanduser().resolve()
    fields = ["source", "openalex_id", "title", "authors", "year", "journal", "doi", "url", "cited_by_count", "abstract"]
    write_csv(out.with_suffix(".csv"), rows, fields)
    write_ris(out.with_suffix(".ris"), rows)
    print(f"OpenAlex query: {query}")
    print(f"Records: {len(rows)}")
    print(f"CSV: {out.with_suffix('.csv')}")
    print(f"RIS: {out.with_suffix('.ris')}")
    print("Import RIS into Zotero: File -> Import -> select .ris")
    return 0


def command_audit_docx(args: argparse.Namespace) -> int:
    docx = Path(args.docx).expanduser().resolve()
    if not docx.exists():
        print(f"DOCX not found: {docx}", file=sys.stderr)
        return 2
    report = audit_docx_file(docx)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.report:
        out = Path(args.report).expanduser().resolve()
        write_text(out, "# DOCX Zotero audit\n\n```json\n" + json.dumps(report, ensure_ascii=False, indent=2) + "\n```\n")
        print(f"Report written: {out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Portable Zotero x Codex review workflow helper")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("check", help="Check local environment")
    sp.set_defaults(func=command_check)

    sp = sub.add_parser("intake", help="Create a guided review brief and project state")
    sp.add_argument("--name", default="", help="Project folder name. Defaults to a slug from the topic.")
    sp.add_argument("--topic", default="", help="Review topic")
    sp.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output parent directory")
    sp.add_argument("--language", default="中文 / English", help="Manuscript language")
    sp.add_argument("--review-type", default="Narrative / Scoping / Systematic / Other", help="Review type")
    sp.add_argument("--audience", default="", help="Target audience")
    sp.add_argument("--goal", default="", help="Target journal, course, or deliverable")
    sp.add_argument("--time-range", default="", help="Preferred publication year range")
    sp.set_defaults(func=command_intake)

    sp = sub.add_parser("init", help="Initialize a new review project")
    sp.add_argument("--name", required=True, help="Project folder name")
    sp.add_argument("--topic", required=True, help="Review topic")
    sp.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output parent directory")
    sp.add_argument("--language", default="中文 / English", help="Manuscript language")
    sp.add_argument("--review-type", default="Narrative / Scoping / Systematic / Other", help="Review type")
    sp.add_argument("--audience", default="", help="Target audience")
    sp.add_argument("--goal", default="", help="Target journal, course, or deliverable")
    sp.add_argument("--time-range", default="", help="Preferred publication year range")
    sp.set_defaults(func=command_init)

    sp = sub.add_parser("run", help="Auto-run the next machine-doable stages")
    sp.add_argument("--project", default="", help="Existing project directory")
    sp.add_argument("--name", default="", help="Project name if creating a new project")
    sp.add_argument("--topic", default="", help="Review topic if creating a new project")
    sp.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output parent directory")
    sp.add_argument("--language", default="中文 / English", help="Manuscript language")
    sp.add_argument("--review-type", default="Narrative / Scoping / Systematic / Other", help="Review type")
    sp.add_argument("--audience", default="", help="Target audience")
    sp.add_argument("--goal", default="", help="Target journal, course, or deliverable")
    sp.add_argument("--time-range", default="", help="Preferred publication year range")
    sp.add_argument("--databases", default="pubmed,openalex", help="Comma-separated database list")
    sp.add_argument("--max", default=30, type=int, help="Max results per database")
    sp.add_argument("--refresh-search", action="store_true", help="Re-run searches even if files already exist")
    sp.set_defaults(func=command_run)

    sp = sub.add_parser("resume", help="Mark human checkpoints as done and continue")
    sp.add_argument("--project", required=True, help="Existing project directory")
    sp.add_argument("--mark", action="append", default=[], choices=MARK_CHOICES, help="Checkpoint to mark as done")
    sp.add_argument("--docx", default="", help="Final DOCX path, if available")
    sp.add_argument("--auto-final-check", action="store_true", help="Run final-check automatically if a DOCX is ready")
    sp.set_defaults(func=command_resume)

    sp = sub.add_parser("handoff", help="Generate the current human action checklist")
    sp.add_argument("--project", required=True, help="Existing project directory")
    sp.set_defaults(func=command_handoff)

    sp = sub.add_parser("final-check", help="Build a final readiness report")
    sp.add_argument("--project", required=True, help="Existing project directory")
    sp.add_argument("--docx", default="", help="Optional DOCX path override")
    sp.set_defaults(func=command_final_check)

    sp = sub.add_parser("search-pubmed", help="Search PubMed and export CSV/RIS")
    sp.add_argument("--query", required=True)
    sp.add_argument("--max", default=30, type=int)
    sp.add_argument("--out", required=True, help="Output prefix, e.g. outputs/my_review/literature/pubmed")
    sp.set_defaults(func=command_search_pubmed)

    sp = sub.add_parser("search-openalex", help="Search OpenAlex and export CSV/RIS")
    sp.add_argument("--query", required=True)
    sp.add_argument("--max", default=30, type=int)
    sp.add_argument("--out", required=True, help="Output prefix, e.g. outputs/my_review/literature/openalex")
    sp.set_defaults(func=command_search_openalex)

    sp = sub.add_parser("audit-docx", help="Static audit of Zotero fields inside a DOCX")
    sp.add_argument("--docx", required=True)
    sp.add_argument("--report", default="", help="Optional markdown report path")
    sp.set_defaults(func=command_audit_docx)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
