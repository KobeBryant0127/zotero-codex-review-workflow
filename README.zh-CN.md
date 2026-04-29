<div align="center">

# CORA

### Codex Literature Review Automation with Zotero-backed references and Word-ready citations.

[![CI](https://github.com/KobeBryant0127/zotero-codex-review-workflow/actions/workflows/ci.yml/badge.svg)](https://github.com/KobeBryant0127/zotero-codex-review-workflow/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Windows](https://img.shields.io/badge/platform-Windows%2010%2F11-blue)](README.md)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](README.md)
[![Codex](https://img.shields.io/badge/Codex-orchestration-111827?logo=openai&logoColor=white)](README.md)
[![Zotero](https://img.shields.io/badge/Zotero-reference%20truth-B91C1C?logo=zotero&logoColor=white)](README.md)
[![Word](https://img.shields.io/badge/Word-final%20manuscript-185ABD?logo=microsoftword&logoColor=white)](README.md)

<p>
  <a href="README.md">English</a> •
  <a href="#为什么会有-cora">为什么</a> •
  <a href="#1-分钟开始">1 分钟开始</a> •
  <a href="#工作流">工作流</a> •
  <a href="#最终会得到什么">输出</a> •
  <a href="#文档">文档</a>
</p>

</div>

> **TL;DR**
>
> **CORA** 的底层是完整的综述工作流引擎，表层是 Codex 托管体验。  
> 你只需要告诉 Codex 你的综述主题、语言和目标；Codex 推进流程，Zotero 负责参考文献真源，Word 负责最终可刷新的正式引用。

<p align="center">
  <img src="docs/images/hero-codex-zotero-word.png" alt="Codex、Zotero 和 Word 协作完成综述" width="100%">
</p>

---

## 为什么会有 CORA

大多数人写综述，还是在手动拼很多断开的环节：

- 检索数据库
- 把文献扔进 Zotero
- 边读边记
- 先写草稿
- 最后再去 Word 里一条条插入引用

综述最痛的地方恰好就在这里：文献多、对比多、引用多，最后最容易乱。

**CORA** 想做的是把这件事压缩成一条能追踪、能暂停、能继续、能交给 Codex 托管的流程。

<table>
  <tr>
    <td width="25%" align="center">
      <strong>🧠 Codex 托管</strong><br>
      提示词、handoff、checkpoint、resume 都是显式的。
    </td>
    <td width="25%" align="center">
      <strong>📚 Zotero 真源</strong><br>
      参考文献、元数据、PDF、collection 有统一落点。
    </td>
    <td width="25%" align="center">
      <strong>📝 Word 成稿</strong><br>
      最终稿保留真实 Zotero 文内引用和 bibliography 字段。
    </td>
    <td width="25%" align="center">
      <strong>📦 项目打包</strong><br>
      evidence matrix、RIS、草稿、质控文件都在一个项目里。
    </td>
  </tr>
</table>

---

## 1 分钟开始

> **默认体验就是 Codex 全程接管。**
> 你和 Codex 对话，Codex 推进流程，只有真的需要人工动作时它才会停下来。

### 1. 在 Codex 里打开仓库，然后直接发这段

```text
I want you to fully manage a literature review project for me using this repository.
My topic is: [TOPIC]
My review type is: [TYPE]
My language is: [LANGUAGE]
My goal is: [GOAL]
Please handle everything you can, and only stop when you truly need me to do a manual step such as Zotero import, PDF verification, or Word citation insertion.
When you stop, tell me exactly what to do and exactly what to reply with.
```

### 2. Codex 会替你推进这些步骤

- 检查环境
- 创建综述项目
- 运行能自动完成的阶段
- 生成 handoff 文件
- 只在必须时叫你介入

常见人工节点只有这几类：

- 把 RIS 导入 Zotero
- 核对关键 PDF
- 在 Word 中插入最终 Zotero 引用
- 保存最终 DOCX 供审计

### 3. 底层命令在跑什么

大多数用户不需要记这些命令，但 CORA 的底层不是空提示词，而是真正的工作流引擎：

```powershell
py scripts\reviewflow.py check
py scripts\reviewflow.py intake --name my_review --topic "你的综述主题" --output .\outputs
py scripts\reviewflow.py run --project .\outputs\my_review
py scripts\reviewflow.py handoff --project .\outputs\my_review
py scripts\reviewflow.py resume --project .\outputs\my_review --mark zotero_imported
py scripts\reviewflow.py final-check --project .\outputs\my_review --docx .\outputs\my_review\word\final_review.docx
py scripts\reviewflow.py audit-docx --docx .\outputs\my_review\word\final_review.docx
```

---

## 工作流

<p align="center">
  <img src="docs/images/before-after.png" alt="传统综述流程和 CORA 流程对比" width="100%">
</p>

<p align="center">
  <img src="docs/images/workflow-overview.png" alt="CORA 工作流总览" width="100%">
</p>

### 底层逻辑

底层完整流程包括：

- topic intake and scope definition
- literature search across trusted sources
- candidate merging and RIS export
- Zotero import and library organization
- evidence matrix building
- structured drafting
- Word manuscript assembly
- Zotero citation insertion and refresh
- final audit and readiness check

### 但你大多数时候可以忽略它

真正的使用感受应该是：

1. 告诉 Codex 你的综述题目和要求
2. 让 Codex 跑它能跑的一切
3. 它停下来时，你只做那一个必须的人类动作
4. 再把结果回复给 Codex，让它继续

---

## CORA 现在已经能做什么

- 检查 Python、Zotero、Word、Git、GitHub CLI 等环境
- 为新主题创建带状态的综述项目
- 检索 PubMed 和 OpenAlex，并导出 CSV + RIS
- 合并候选文献池
- 生成 handoff 和下一条给 Codex 的提示词
- 审计最终 Word 文档里的 Zotero 字段
- 输出最终完成度和风险总结

### 它不会假装做到这些

- 不承诺自动学术正确
- 不替代人类对范围和结论的判断
- 不把占位引用伪装成真实 Zotero Word 字段
- 不绕过访问权限限制

---

## 最终会得到什么

<p align="center">
  <img src="docs/images/project-structure.png" alt="CORA 项目结构图" width="100%">
</p>

关键交付物包括：

- `word/final_review.docx`
- `word/final_review.pdf`
- `notes/evidence_matrix.csv`
- `literature/combined_candidates.ris`
- `quality/final_check_summary.md`

---

## 文档

- [README.md](README.md)
- [QUICKSTART.md](QUICKSTART.md)
- [docs/00_portable_project_design.md](docs/00_portable_project_design.md)
- [docs/08_word_zotero_citation_workflow.md](docs/08_word_zotero_citation_workflow.md)
- [docs/11_launch_playbook.md](docs/11_launch_playbook.md)
- [ROADMAP.md](ROADMAP.md)

## License

MIT. See [LICENSE](LICENSE).
