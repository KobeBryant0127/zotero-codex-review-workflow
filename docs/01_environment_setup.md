# 01 环境配置：Zotero、Word、Codex

## A. 安装 Zotero

1. 安装 Zotero 桌面版。
2. 安装浏览器插件 Zotero Connector。
3. 打开 Zotero，确认可以新建 Collection。
4. 在浏览器打开一篇论文页面，测试 Connector 能否保存题录和 PDF。

## B. 检查 Word Zotero 插件

Zotero 通常会自动安装 Word 插件。打开 Word 后应能看到 Zotero 选项卡。

如果没有：

1. Zotero → Edit/Preferences → Cite → Word Processors；
2. 点击 Install Microsoft Word Add-in；
3. 重启 Word。

## C. 检查本机 Word/Zotero 状态

Windows PowerShell：

```powershell
Get-Process | Where-Object { $_.ProcessName -match 'zotero|winword' } | Select ProcessName,Id,Path
```

检查 Word Add-in：

```powershell
$word = New-Object -ComObject Word.Application
$word.Visible = $true
foreach($a in $word.AddIns){ [pscustomobject]@{Name=$a.Name; Installed=$a.Installed; Path=$a.Path} }
$word.Quit()
```

也可以运行本项目脚本：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check_word_zotero.ps1
```

## D. 配置 Codex 工作方式

建议每个综述项目建立独立目录：

```text
my-review-project/
  literature/
  notes/
  tables/
  figures/
  draft/
  zotero_exports/
```

不要让 AI 直接编造参考文献。所有引用必须来自 Zotero 或数据库检索结果。
