# 快速开始：换一台电脑也能跑

这个项目的目标不是让 AI 直接“凭空写完综述”，而是让新手按一个可复制流程完成：

```text
安装软件 → 初始化综述项目 → 检索文献 → 导入 Zotero → 读文献/证据矩阵 → 生成表图 → 起草 Word → Zotero 插入真实引用 → 质控
```

## 0. 需要安装的软件

最低要求：

1. Windows 10/11；
2. Python 3.10+；
3. Zotero 桌面版；
4. Zotero Connector 浏览器插件；
5. Microsoft Word；
6. Codex 或任意可读取本项目文件的 AI 编程/写作助手。

可选但推荐：

- Better BibTeX for Zotero：方便生成稳定 CitationKey；
- Excel 或 WPS：查看 evidence matrix；
- draw.io / PowerPoint：后期润色综述图。

## 1. 一键环境检查

在本项目根目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\START_HERE.ps1
```

或：

```powershell
py scripts\reviewflow.py check
```

## 2. 初始化一个综述项目

```powershell
py scripts\reviewflow.py init --name my_first_review --topic "你的综述主题" --output .\outputs
```

生成目录示例：

```text
outputs/my_first_review/
  README_PROJECT.md
  protocol/review_protocol.md
  literature/search_queries.md
  literature/candidates.csv
  literature/candidates.ris
  zotero_exports/
  notes/evidence_matrix.csv
  tables/
  figures/
  draft/review_outline.md
  draft/manuscript.md
  word/
  quality/quality_check_report.md
```

## 3. 检索文献并生成 Zotero 可导入 RIS

PubMed 示例：

```powershell
py scripts\reviewflow.py search-pubmed --query "machine learning EEG review" --max 30 --out .\outputs\my_first_review\literature\pubmed
```

OpenAlex 示例：

```powershell
py scripts\reviewflow.py search-openalex --query "machine learning EEG" --max 30 --out .\outputs\my_first_review\literature\openalex
```

然后把生成的 `.ris` 导入 Zotero：

```text
Zotero → File → Import → 选择 .ris → 导入到当前项目 Collection
```

## 4. 写作方式

1. 先在 `protocol/review_protocol.md` 写清楚综述边界；
2. 在 Zotero 中整理 collection、标签、PDF 和笔记；
3. 在 `notes/evidence_matrix.csv` 中填证据矩阵；
4. 让 Codex 根据 evidence matrix 生成表格、图和段落；
5. 在 `draft/manuscript.md` 中保留 `[CitationKey]` 占位；
6. 最终复制到 Word，用 Zotero 插件逐条插入真实引用；
7. 插入 Bibliography，运行 Zotero Refresh；
8. 用 `audit-docx` 检查 Word 文档里的 Zotero 字段。

## 5. 检查 Word 文档 Zotero 字段

```powershell
py scripts\reviewflow.py audit-docx --docx .\outputs\my_first_review\word\final_review.docx
```

合格标准：

- `zotero_item_count > 0`
- `zotero_bibl_count == 1`，如果需要参考文献列表；
- `field_separate_count >= zotero_item_count + zotero_bibl_count`；
- Word 中运行 Zotero Refresh 后引用不消失。

## 重要提醒

- 这个项目可以把综述流程高度自动化，但不能保证“无需人工判断”。
- AI 不应该编造参考文献；所有引用都必须来自 Zotero/数据库。
- 最终 Word 引用必须由 Zotero 插件插入，不能只是普通文本。
