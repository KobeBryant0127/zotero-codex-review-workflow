# 08 Word 与 Zotero 交叉引用闭环

## 推荐流程

1. 在 Markdown/草稿中先用 `[CitationKey]` 或 `(Author, Year)` 占位；
2. 打开 Word 成稿；
3. 用 Zotero 插件逐条插入真实引用；
4. 设置样式，例如 APA 7th；
5. 插入 Bibliography；
6. 运行 Zotero Refresh；
7. 审计字段是否真实可刷新。

## 关键注意

普通文本 `(Smith, 2020)` 不是 Zotero 引文。最终 Word 里必须是 Zotero Word field。

## 使用 zotero-word-citations skill 做审计/修复

该 skill 可用于：

- 检查 `ZOTERO_ITEM` 和 `ZOTERO_BIBL` 字段；
- 修复有 Zotero 代码但显示为空的字段；
- 删除真实 Zotero 字段旁边残留的重复文本引用；
- 运行 Word/Zotero Refresh 后再次审计。

示例：

```powershell
py C:\Users\m1382\.codex\skills\zotero-word-citations\scripts\audit_zotero_fields.py output.docx
py C:\Users\m1382\.codex\skills\zotero-word-citations\scripts\audit_zotero_metadata_and_leftovers.py output.docx
```

## 合格标准

- Word 打开无修复提示；
- Zotero Refresh 不清空引用；
- 所有引用显示正常；
- Bibliography 由 Zotero 管理；
- 没有残留重复纯文本引用。
