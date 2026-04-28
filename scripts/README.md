# scripts

## `reviewflow.py`

标准库 Python CLI，方便在新电脑上直接运行。

```powershell
py scripts\reviewflow.py check
py scripts\reviewflow.py intake --name my_review --topic "your topic" --output .\outputs
py scripts\reviewflow.py run --project .\outputs\my_review
py scripts\reviewflow.py handoff --project .\outputs\my_review
py scripts\reviewflow.py resume --project .\outputs\my_review --mark zotero_imported
py scripts\reviewflow.py final-check --project .\outputs\my_review
py scripts\reviewflow.py audit-docx --docx .\outputs\my_review\word\final_review.docx
```

新的推荐路径是：

1. `intake`：创建综述需求简报和状态文件；
2. `run`：自动执行机器能完成的部分，比如文献检索和候选文件导出；
3. `handoff`：当需要人工做 Zotero / PDF / Word 操作时，生成明确清单；
4. `resume`：人工完成后打标记，让 Codex 继续；
5. `final-check`：最后输出 readiness report。

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
