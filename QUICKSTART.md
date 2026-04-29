# 快速开始：在 Codex 里全程托管跑完第一篇综述

默认体验不是你手动敲完整套命令，而是你在 Codex 里打开这个仓库，然后把流程交给 Codex 托管。

这个项目的目标不是让 AI 直接“凭空写完综述”，而是让新手在 Codex 托管下按一个可复制流程完成：

```text
安装软件 → check → intake → run → 人工导入 Zotero / 检查 PDF → resume → evidence matrix → 草稿 → Word Zotero 引用 → final-check
```

## 0. 先在 Codex 里发这段

```text
I want you to fully manage a literature review project for me using this repository.
My topic is: [TOPIC]
My review type is: [TYPE]
My language is: [LANGUAGE]
My goal is: [GOAL]
Please handle everything you can, and only stop when you truly need me to do a manual step such as Zotero import, PDF verification, or Word citation insertion.
When you stop, tell me exactly what to do and exactly what to reply with.
```

这就是推荐入口。  
从这里开始，Codex 应该负责检查环境、创建项目、推进流程、生成 handoff，并在真正需要人工介入时告诉你下一步。

## 1. 需要安装的软件

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

## 2. 一键环境检查

在本项目根目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\START_HERE.ps1
```

或：

```powershell
py scripts\reviewflow.py check
```

## 3. Codex 在底层会跑什么

大多数新手不需要自己手动执行这些，但知道底层逻辑有助于理解 CORA 不是单纯提示词：

```powershell
py scripts\reviewflow.py intake --name my_first_review --topic "你的综述主题" --output .\outputs
py scripts\reviewflow.py run --project .\outputs\my_first_review
py scripts\reviewflow.py handoff --project .\outputs\my_first_review
py scripts\reviewflow.py resume --project .\outputs\my_first_review --mark zotero_imported
py scripts\reviewflow.py final-check --project .\outputs\my_first_review --docx .\outputs\my_first_review\word\final_review.docx
py scripts\reviewflow.py audit-docx --docx .\outputs\my_first_review\word\final_review.docx
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

## 4. 看 handoff，再做第一个人工动作

运行完 `run` 之后，先看：

```powershell
py scripts\reviewflow.py handoff --project .\outputs\my_first_review
```

项目里会生成：

- `quality/codex_handoff.md`
- `quality/next_prompt_to_codex.md`

通常第一步会要求你把生成的 `literature/combined_candidates.ris` 导入 Zotero：

```text
Zotero → File → Import → 选择 .ris → 导入到当前项目 Collection
```

完成后：

```powershell
py scripts\reviewflow.py resume --project .\outputs\my_first_review --mark zotero_imported
```

## 5. 写作方式

1. `run` 自动生成候选文献和项目模板；
2. `handoff` 明确告诉你现在要人工做什么；
3. 你完成人工步骤后用 `resume --mark ...` 告诉系统继续；
4. Codex 根据 `notes/evidence_matrix.csv`、`draft/manuscript.md`、`quality/next_prompt_to_codex.md` 继续推进；
5. 最终复制到 Word，用 Zotero 插件逐条插入真实引用；
6. 保存 `word/final_review.docx`；
7. 运行 `final-check` 和 `audit-docx`。

## 6. 检查 Word 文档 Zotero 字段

```powershell
py scripts\reviewflow.py audit-docx --docx .\outputs\my_first_review\word\final_review.docx
py scripts\reviewflow.py final-check --project .\outputs\my_first_review --docx .\outputs\my_first_review\word\final_review.docx
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
