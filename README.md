# Zotero × Codex Review Workflow

> 从零配置 Zotero / Word / Codex，到完成一篇带有真实 Zotero 引文、综述表格和框架图的综述文章。

这是一个面向科研新手的开源工作流项目。它不会鼓励 AI 凭空生成参考文献，而是把 **文献检索、Zotero 管理、证据矩阵、AI 辅助写作、Word 中 Zotero 引用闭环** 串成一个可复制流程。

现在它也开始支持一种更接近“代理”的用法：

- `intake`：先把综述需求变成项目简报；
- `run`：Codex 自动执行机器能完成的阶段；
- `handoff`：真正需要你介入时，自动生成清单和下一句提示词；
- `resume`：你做完人工步骤后，告诉 Codex 继续；
- `final-check`：最后汇总质量和风险。

## 适合谁

- 第一次系统写综述的本科生、研究生、规培/临床科研新手；
- 不熟悉 Zotero、Word Zotero 插件、Codex/AI 辅助写作的人；
- 想把“文献调研 → 阅读笔记 → 综述表格/图 → 正文 → Word 引用”标准化的人。

## 这个项目能做什么

- 一键检查本机 Python、Zotero、Word 环境；
- 一键初始化一个综述项目目录；
- 一键生成可由 Codex 托管推进的项目状态；
- 自动生成综述协议、检索记录、evidence matrix、写作大纲、表图计划；
- 从 PubMed / OpenAlex 检索文献，导出 CSV 和 Zotero 可导入 RIS；
- 指导你把文献保存到 Zotero 并建立 collection / tag；
- 用 Codex 辅助总结文献、生成表格、规划图和起草段落；
- 在必须人工操作时，输出明确的 handoff checklist 和 next prompt；
- 静态审计 Word `.docx` 中是否存在 Zotero citation / bibliography 字段；
- 配合 Zotero Word 插件完成可刷新的参考文献列表。

## 不能替你自动完成的事

- 判断某篇文献是否应该纳入；
- 判断结论是否被证据充分支持；
- 绕过数据库/PDF 权限下载全文；
- 代替 Zotero Word 插件插入最终官方引文；
- 保证 AI 生成内容完全正确。

核心原则：**AI 只辅助组织和表达；引用来源必须来自真实数据库和 Zotero。**

## 快速开始

### 1. 安装基础软件

最低要求：

- Windows 10/11；
- Python 3.10+；
- Zotero 桌面版；
- Zotero Connector 浏览器插件；
- Microsoft Word；
- Codex 或其他可读取项目文件的 AI 助手。

推荐：

- Better BibTeX for Zotero，用于稳定 citation key；
- Excel / WPS，用于编辑 evidence matrix。

### 2. 环境检查

在项目根目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\START_HERE.ps1
```

或：

```powershell
py scripts\reviewflow.py check
```

### 3. 创建托管式综述项目

```powershell
py scripts\reviewflow.py intake --name my_first_review --topic "你的综述主题" --output .\outputs
py scripts\reviewflow.py run --project .\outputs\my_first_review
```

生成目录示例：

```text
outputs/my_first_review/
  protocol/review_protocol.md
  literature/search_queries.md
  literature/candidates.csv
  zotero_exports/
  notes/evidence_matrix.csv
  tables/table_plan.md
  figures/figure_plan.md
  draft/review_outline.md
  draft/manuscript.md
  word/
  quality/quality_check_report.md
```

`run` 完成后，项目里会多出：

- `quality/codex_handoff.md`
- `quality/next_prompt_to_codex.md`

这两个文件会告诉新手“现在该人工做什么”和“下一句该怎么对 Codex 说”。

### 4. 让 Codex 自动跑检索，然后按提示导入 Zotero

`run` 默认会自动检索 PubMed 和 OpenAlex，并在 `literature/` 里生成合并后的候选文件。接着把生成的 `.ris` 导入 Zotero：

```text
Zotero → File → Import → 选择 .ris → 导入到当前项目 Collection
```

### 5. 写作与引用闭环

1. 在 `protocol/review_protocol.md` 明确综述边界；
2. 在 Zotero 中整理 collection、tag、PDF、笔记；
3. 在 `notes/evidence_matrix.csv` 填证据矩阵；
4. 用 Codex 根据 evidence matrix 生成表格、图和段落；
5. 在 `draft/manuscript.md` 里保留 `[CitationKey]` 占位；
6. 最终复制到 Word，用 Zotero 插件逐条插入真实引用；
7. 插入 Zotero Bibliography，运行 Zotero Refresh；
8. 审计 Word 文档：

```powershell
py scripts\reviewflow.py audit-docx --docx .\outputs\my_first_review\word\final_review.docx
```

详见 [`QUICKSTART.md`](QUICKSTART.md)。

## 文档导航

1. [`docs/00_portable_project_design.md`](docs/00_portable_project_design.md)
2. [`docs/01_environment_setup.md`](docs/01_environment_setup.md)
3. [`docs/02_review_topic_and_protocol.md`](docs/02_review_topic_and_protocol.md)
4. [`docs/03_literature_search.md`](docs/03_literature_search.md)
5. [`docs/04_zotero_library_management.md`](docs/04_zotero_library_management.md)
6. [`docs/05_reading_notes_and_evidence_matrix.md`](docs/05_reading_notes_and_evidence_matrix.md)
7. [`docs/06_review_tables_and_figures.md`](docs/06_review_tables_and_figures.md)
8. [`docs/07_drafting_with_codex.md`](docs/07_drafting_with_codex.md)
9. [`docs/08_word_zotero_citation_workflow.md`](docs/08_word_zotero_citation_workflow.md)
10. [`docs/09_final_quality_check.md`](docs/09_final_quality_check.md)

## 命令行工具

```powershell
py scripts\reviewflow.py --help
```

当前命令：

- `check`：检查本机环境；
- `intake`：创建托管式综述项目和需求简报；
- `init`：初始化综述项目；
- `run`：自动推进机器可做的阶段；
- `resume`：人工完成节点后，更新状态并继续；
- `handoff`：生成当前人工清单和下一句提示词；
- `final-check`：汇总项目完成度和剩余风险；
- `search-pubmed`：检索 PubMed，导出 CSV/RIS；
- `search-openalex`：检索 OpenAlex，导出 CSV/RIS；
- `audit-docx`：静态检查 Word 文档中的 Zotero 字段。

## 项目结构

```text
.
├── docs/               # 分阶段教程
├── templates/          # 综述协议、矩阵、大纲、提示词模板
├── scripts/            # CLI 与 Windows 检查脚本
├── examples/           # 示例占位
├── outputs/            # 本地生成结果，默认不提交
├── QUICKSTART.md       # 新手快速开始
├── START_HERE.ps1      # Windows 一键入口
└── README.md
```

## 开源协议

本项目采用 MIT License。见 [`LICENSE`](LICENSE)。

## 贡献

欢迎提交 issue 和 pull request。建议优先贡献：

- 更多数据库检索接口；
- 更好的 Zotero / Better BibTeX 集成；
- 完整示例综述；
- Word/Zotero 引文质控脚本；
- 中文/英文教程润色。

见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。
