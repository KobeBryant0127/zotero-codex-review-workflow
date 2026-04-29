<div align="center">

# CORA

### Codex Literature Review Automation with Zotero-backed references and Word-ready citations.

[![CI](https://github.com/KobeBryant0127/zotero-codex-review-workflow/actions/workflows/ci.yml/badge.svg)](https://github.com/KobeBryant0127/zotero-codex-review-workflow/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Windows](https://img.shields.io/badge/platform-Windows%2010%2F11-blue)](README.md)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](README.md)

<p>
  <a href="README.md">English</a> •
  <a href="#为什么是-cora">为什么</a> •
  <a href="#在-codex-里使用-cora">Codex 用法</a> •
  <a href="#工作流">工作流</a> •
  <a href="#输出结果">输出结果</a> •
  <a href="#文档">文档</a>
</p>

</div>

> **CORA** 的底层是完整的综述工作流引擎，表层是 Codex 托管体验。  
> 你负责描述综述需求，Codex 负责推进流程，Zotero 负责参考文献真源，Word 负责最终可刷新的正式引用。

<p align="center">
  <img src="docs/images/hero-codex-zotero-word.png" alt="CORA 头图" width="100%">
</p>

## 最新能力

- 默认按 Codex-first 方式使用
- 支持 handoff / resume 状态推进
- 自动生成 RIS，导入 Zotero 后继续推进
- 支持 Word Zotero 字段审计

## 为什么是 CORA

写综述通常意味着手动拼接很多环节：检索、筛选、笔记、写作、Zotero、Word。CORA 的目标就是把这些压缩成一条可追踪的流水线：

- **Codex** 负责托管流程
- **Zotero** 负责参考文献真源
- **Word** 负责最终成稿和正式交叉引用

<table>
  <tr>
    <td width="25%" align="center"><strong>🧠 Codex 托管</strong><br>提示词、handoff、checkpoint、resume 都是显式的。</td>
    <td width="25%" align="center"><strong>📚 Zotero 真源</strong><br>参考文献、元数据、PDF、collection 都有统一落点。</td>
    <td width="25%" align="center"><strong>📝 Word 成稿</strong><br>最终稿保留真实 Zotero 文内引用和 bibliography 字段。</td>
    <td width="25%" align="center"><strong>📦 项目打包</strong><br>evidence matrix、RIS、草稿、质控文件都在一个项目里。</td>
  </tr>
</table>

## 在 Codex 里使用 CORA

大多数用户不需要先学命令行。默认体验应该是：

1. 在 Codex 中打开这个仓库
2. 直接发下面这段起始请求
3. 让 Codex 自动执行能做的步骤
4. 只有在必须人工介入时再操作

```text
I want you to fully manage a literature review project for me using this repository.
My topic is: [TOPIC]
My review type is: [TYPE]
My language is: [LANGUAGE]
My goal is: [GOAL]
Please handle everything you can, and only stop when you truly need me to do a manual step such as Zotero import, PDF verification, or Word citation insertion.
When you stop, tell me exactly what to do and exactly what to reply with.
```

### 底层逻辑

底层工作流是完整的：

- intake
- literature search
- RIS export
- Zotero import
- evidence matrix
- drafting
- Word manuscript
- Zotero citation refresh
- final audit

但多数时候你并不需要自己逐步驱动这条流水线。

## 工作流

<p align="center">
  <img src="docs/images/before-after.png" alt="CORA 前后对比图" width="100%">
</p>

<p align="center">
  <img src="docs/images/workflow-overview.png" alt="CORA 工作流总览图" width="100%">
</p>

### CORA 已经能做什么

- 为新的综述主题创建带状态的项目目录
- 检索 PubMed / OpenAlex 并导出 CSV + RIS
- 合并候选文献池
- 生成 handoff 和下一条给 Codex 的提示词
- 审计最终 Word 文档里的 Zotero 字段
- 生成最终完成度报告

### CORA 不会伪装什么

- 不承诺自动学术正确
- 不替代人类对范围和结论的判断
- 不把占位引用伪装成真实 Zotero Word 字段
- 不绕过访问权限限制

## 输出结果

<p align="center">
  <img src="docs/images/project-structure.png" alt="CORA 项目结构图" width="100%">
</p>

最关键的最终产物：

- `word/final_review.docx`
- `word/final_review.pdf`
- `notes/evidence_matrix.csv`
- `literature/combined_candidates.ris`
- `quality/final_check_summary.md`

## 底层命令

如果你想看底层命令，可以用：

```powershell
py scripts\reviewflow.py check
py scripts\reviewflow.py intake --name my_review --topic "你的综述主题" --output .\outputs
py scripts\reviewflow.py run --project .\outputs\my_review
py scripts\reviewflow.py handoff --project .\outputs\my_review
py scripts\reviewflow.py resume --project .\outputs\my_review --mark zotero_imported
py scripts\reviewflow.py final-check --project .\outputs\my_review --docx .\outputs\my_review\word\final_review.docx
```

## 文档

- [README.md](README.md)
- [QUICKSTART.md](QUICKSTART.md)
- [docs/00_portable_project_design.md](docs/00_portable_project_design.md)
- [docs/08_word_zotero_citation_workflow.md](docs/08_word_zotero_citation_workflow.md)
- [docs/11_launch_playbook.md](docs/11_launch_playbook.md)
- [ROADMAP.md](ROADMAP.md)

## 定位

- **CORA**：Codex Literature Review Automation
- **承诺**：Codex 托管综述流程，Zotero 保持引用真源，Word 输出可刷新的正式引用
- **现实**：底层是工作流引擎，表层是解放双手的 Codex 使用体验

## License

MIT. See [LICENSE](LICENSE).
