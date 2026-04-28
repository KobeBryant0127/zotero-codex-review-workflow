#!/usr/bin/env python3
"""reviewflow.py

Portable command-line helper for a Zotero x Codex review-writing workflow.
It uses Python standard library only so beginners can run it on a new Windows PC.

Commands:
  check          Check local environment assumptions.
  init           Initialize a new review project folder.
  search-pubmed  Search PubMed and export CSV/RIS for Zotero import.
  search-openalex Search OpenAlex and export CSV/RIS for Zotero import.
  audit-docx     Inspect a DOCX for Zotero Word fields.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import textwrap
import urllib.parse
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
UA = "zotero-codex-review-workflow/0.1 (educational; local user)"


def safe_slug(text: str) -> str:
    text = text.strip().replace(" ", "_")
    text = re.sub(r"[^0-9A-Za-z_\-\u4e00-\u9fff]+", "", text)
    return text or "review_project"


def read_url_json(url: str, timeout: int = 30) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def year_from_date(value: str | None) -> str:
    if not value:
        return ""
    m = re.search(r"(19|20)\d{2}", value)
    return m.group(0) if m else ""


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    value = str(value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def ris_escape(value: str) -> str:
    return clean_text(value).replace("\n", " ").replace("\r", " ")


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})


def write_ris(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for r in rows:
        item_type = "JOUR" if r.get("journal") else "GEN"
        lines.append(f"TY  - {item_type}")
        if r.get("title"):
            lines.append(f"TI  - {ris_escape(r['title'])}")
        authors = r.get("authors") or ""
        if isinstance(authors, list):
            author_list = authors
        else:
            author_list = [a.strip() for a in str(authors).split(";") if a.strip()]
        for au in author_list:
            lines.append(f"AU  - {ris_escape(au)}")
        if r.get("year"):
            lines.append(f"PY  - {ris_escape(r['year'])}")
        if r.get("journal"):
            lines.append(f"T2  - {ris_escape(r['journal'])}")
            lines.append(f"JO  - {ris_escape(r['journal'])}")
        if r.get("doi"):
            lines.append(f"DO  - {ris_escape(r['doi'])}")
        if r.get("url"):
            lines.append(f"UR  - {ris_escape(r['url'])}")
        if r.get("abstract"):
            lines.append(f"AB  - {ris_escape(r['abstract'])}")
        if r.get("source"):
            lines.append(f"N1  - Source: {ris_escape(r['source'])}")
        if r.get("cited_by_count") != "" and r.get("cited_by_count") is not None:
            lines.append(f"N1  - cited_by_count: {ris_escape(str(r['cited_by_count']))}")
        lines.append("ER  -")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8-sig")


def command_check(args: argparse.Namespace) -> int:
    print("== System ==")
    print(f"Python: {sys.version.split()[0]} ({sys.executable})")
    print(f"OS: {platform.platform()}")
    print(f"Project root: {ROOT}")

    print("\n== Commands ==")
    for cmd in ["py", "python", "zotero", "winword"]:
        found = shutil.which(cmd)
        print(f"{cmd}: {found or 'not found in PATH'}")

    print("\n== Common Windows install paths ==")
    common = [
        Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Zotero" / "zotero.exe",
        Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Zotero" / "zotero.exe",
    ]
    for p in common:
        print(f"{'[OK]' if p.exists() else '[--]'} {p}")

    if platform.system().lower().startswith("win"):
        print("\n== Running processes: zotero/winword ==")
        try:
            ps = subprocess.run(
                ["powershell", "-NoProfile", "-Command", "Get-Process | Where-Object { $_.ProcessName -match 'zotero|winword' } | Select-Object ProcessName,Id,Path | Format-Table -AutoSize"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            print(ps.stdout.strip() or "No Zotero/Word process currently running.")
        except Exception as e:
            print(f"Could not query processes via PowerShell: {e}")

    print("\n== Next ==")
    print('Initialize a review project: py scripts\\reviewflow.py init --name my_review --topic "your topic" --output .\\outputs')
    return 0


def command_init(args: argparse.Namespace) -> int:
    name = safe_slug(args.name)
    topic = args.topic.strip()
    output = Path(args.output).expanduser().resolve()
    project = output / name
    project.mkdir(parents=True, exist_ok=True)

    dirs = [
        "protocol", "literature", "zotero_exports", "notes", "tables", "figures",
        "draft", "word", "quality", "logs"
    ]
    for d in dirs:
        (project / d).mkdir(exist_ok=True)

    def write(rel: str, content: str) -> None:
        (project / rel).parent.mkdir(parents=True, exist_ok=True)
        (project / rel).write_text(content, encoding="utf-8-sig")

    write("README_PROJECT.md", f"""# {name}

综述主题：{topic}

## 每次工作顺序

1. 更新 `protocol/review_protocol.md`；
2. 在 `literature/search_queries.md` 记录检索式；
3. 把检索结果导入 Zotero，并导出备份到 `zotero_exports/`；
4. 在 `notes/evidence_matrix.csv` 填证据矩阵；
5. 在 `draft/manuscript.md` 写作，引用先用 `[CitationKey]` 占位；
6. 成稿复制到 Word，在 Zotero 插件中逐条插入真实引用；
7. 保存到 `word/final_review.docx`；
8. 运行 `quality/quality_check_report.md` 清单和 audit-docx。

## 常用命令

```powershell
py "{ROOT / 'scripts' / 'reviewflow.py'}" search-pubmed --query "{topic}" --max 30 --out "{project / 'literature' / 'pubmed'}"
py "{ROOT / 'scripts' / 'reviewflow.py'}" search-openalex --query "{topic}" --max 30 --out "{project / 'literature' / 'openalex'}"
py "{ROOT / 'scripts' / 'reviewflow.py'}" audit-docx --docx "{project / 'word' / 'final_review.docx'}"
```
""")

    write("protocol/review_protocol.md", f"""# 综述写作协议

## 基本信息

- 综述题目：{topic}
- 综述类型：Narrative / Scoping / Systematic / Meta-analysis / Other
- 目标期刊/用途：
- 目标读者：
- 语言：{args.language}

## 核心问题

1. 
2. 
3. 

## 纳入标准

- 时间范围：
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
""")

    write("literature/search_queries.md", f"""# 检索式记录

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
""")

    write("literature/candidates.csv", "CitationKey,Authors,Year,Title,Journal,DOI,URL,Source,Decision,Reason,Tags\n")
    write("literature/candidates.ris", "")
    write("notes/evidence_matrix.csv", "CitationKey,Claim,Evidence,QuoteOrPage,StudyType,PopulationOrDataset,Method,MainFinding,Limitation,Section,Confidence,NeedsVerification\n")
    write("tables/table_plan.md", "# 综述表格计划\n\n| 表格 | 目的 | 数据来源 | 状态 |\n|---|---|---|---|\n| Table 1 经典/高影响文献 | 梳理发展脉络 | evidence_matrix | todo |\n| Table 2 方法/主题比较 | 比较路线和局限 | evidence_matrix | todo |\n")
    write("figures/figure_plan.md", "# 综述图计划\n\n| 图 | 目的 | 形式 | 状态 |\n|---|---|---|---|\n| Figure 1 领域框架图 | 解释综述结构 | Mermaid/PowerPoint | todo |\n| Figure 2 时间线/证据地图 | 展示发展和证据 | Mermaid/Excel/PowerPoint | todo |\n")
    write("draft/review_outline.md", f"""# 综述大纲：{topic}

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
""")
    write("draft/manuscript.md", f"""# {topic}

> 写作规则：所有事实性论断后先放 `[CitationKey]`，最后在 Word 中用 Zotero 插件替换为真实引用。

## Introduction


## Search and Selection Strategy


## Conceptual Background


## Main Themes


## Challenges and Future Directions


## Conclusion


""")
    write("draft/codex_prompts.md", f"""# Codex 提示词

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
""")
    write("quality/quality_check_report.md", """# 质量检查报告

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
""")

    print(f"Created review project: {project}")
    print("Next:")
    print(f"  py {ROOT / 'scripts' / 'reviewflow.py'} search-pubmed --query \"{topic}\" --max 30 --out \"{project / 'literature' / 'pubmed'}\"")
    return 0


def command_search_pubmed(args: argparse.Namespace) -> int:
    query = args.query.strip()
    retmax = max(1, min(int(args.max), 200))
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    params = urllib.parse.urlencode({"db": "pubmed", "term": query, "retmode": "json", "retmax": retmax, "sort": "relevance"})
    esearch = read_url_json(f"{base}/esearch.fcgi?{params}")
    ids = esearch.get("esearchresult", {}).get("idlist", [])
    rows: list[dict[str, Any]] = []
    if ids:
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
            authors = [a.get("name", "") for a in item.get("authors", []) if a.get("name")]
            rows.append({
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
            })
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


def invert_abstract(idx: dict[str, list[int]] | None) -> str:
    if not idx:
        return ""
    words: list[tuple[int, str]] = []
    for word, positions in idx.items():
        for pos in positions:
            words.append((pos, word))
    return " ".join(w for _, w in sorted(words))


def command_search_openalex(args: argparse.Namespace) -> int:
    query = args.query.strip()
    per_page = max(1, min(int(args.max), 200))
    params = urllib.parse.urlencode({"search": query, "per-page": per_page, "sort": "cited_by_count:desc"})
    url = f"https://api.openalex.org/works?{params}"
    data = read_url_json(url)
    rows: list[dict[str, Any]] = []
    for item in data.get("results", []):
        authors = []
        for au in item.get("authorships", []) or []:
            name = (au.get("author") or {}).get("display_name")
            if name:
                authors.append(name)
        source = ""
        loc = item.get("primary_location") or {}
        src = loc.get("source") or {}
        if src:
            source = src.get("display_name") or ""
        doi = item.get("doi") or ""
        rows.append({
            "source": "OpenAlex",
            "openalex_id": item.get("id", ""),
            "title": clean_text(item.get("title", "")),
            "authors": "; ".join(authors),
            "year": item.get("publication_year", ""),
            "journal": clean_text(source),
            "doi": doi.replace("https://doi.org/", "") if doi else "",
            "url": item.get("doi") or item.get("id", ""),
            "cited_by_count": item.get("cited_by_count", ""),
            "abstract": invert_abstract(item.get("abstract_inverted_index")),
        })
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
    xml_files = [
        "word/document.xml",
        "word/footnotes.xml",
        "word/endnotes.xml",
    ]
    combined = ""
    found_files = []
    with zipfile.ZipFile(docx) as z:
        for name in xml_files:
            if name in z.namelist():
                text = z.read(name).decode("utf-8", errors="replace")
                combined += "\n" + text
                found_files.append(name)
    zotero_item_count = combined.count("ZOTERO_ITEM")
    zotero_bibl_count = combined.count("ZOTERO_BIBL")
    addin_count = combined.count("ADDIN ZOTERO")
    field_begin_count = combined.count('w:fldCharType="begin"') + combined.count("w:fldCharType='begin'")
    field_separate_count = combined.count('w:fldCharType="separate"') + combined.count("w:fldCharType='separate'")
    field_end_count = combined.count('w:fldCharType="end"') + combined.count("w:fldCharType='end'")

    # Extract rough visible citation snippets from simple field results.
    visible_text = re.sub(r"<[^>]+>", " ", combined)
    visible_text = re.sub(r"\s+", " ", visible_text)
    parenthetical_candidates = re.findall(r"\([A-Z][A-Za-zÀ-ÿ'\-]+(?: et al\.)?,? \d{4}[a-z]?[^)]{0,80}\)", visible_text)

    report = {
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
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.report:
        out = Path(args.report).expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("# DOCX Zotero audit\n\n```json\n" + json.dumps(report, ensure_ascii=False, indent=2) + "\n```\n", encoding="utf-8-sig")
        print(f"Report written: {out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Portable Zotero x Codex review workflow helper")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("check", help="Check local environment")
    sp.set_defaults(func=command_check)

    sp = sub.add_parser("init", help="Initialize a new review project")
    sp.add_argument("--name", required=True, help="Project folder name")
    sp.add_argument("--topic", required=True, help="Review topic")
    sp.add_argument("--output", default=str(ROOT / "outputs"), help="Output parent directory")
    sp.add_argument("--language", default="中文 / English", help="Manuscript language")
    sp.set_defaults(func=command_init)

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

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
