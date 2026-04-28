# scripts

## `reviewflow.py`

标准库 Python CLI，方便在新电脑上直接运行。

```powershell
py scripts\reviewflow.py check
py scripts\reviewflow.py init --name my_review --topic "your topic" --output .\outputs
py scripts\reviewflow.py search-pubmed --query "your topic" --max 30 --out .\outputs\my_review\literature\pubmed
py scripts\reviewflow.py search-openalex --query "your topic" --max 30 --out .\outputs\my_review\literature\openalex
py scripts\reviewflow.py audit-docx --docx .\outputs\my_review\word\final_review.docx
```

## `check_word_zotero.ps1`

检查 Windows 上 Word COM 和 Zotero Word 插件是否可见。

```powershell
powershell -ExecutionPolicy Bypass -File scripts\check_word_zotero.ps1
```

## 深度 Word/Zotero 字段修复

如果本机安装了 Codex skill `zotero-word-citations`，可进一步调用：

```powershell
py C:\Users\m1382\.codex\skills\zotero-word-citations\scripts\audit_zotero_fields.py your.docx
py C:\Users\m1382\.codex\skills\zotero-word-citations\scripts\audit_zotero_metadata_and_leftovers.py your.docx
```

本项目自带的 `audit-docx` 是便携静态检查；`zotero-word-citations` skill 更适合在作者电脑上做深度修复和 Word/Zotero Refresh 验证。
