# 10 发布到 GitHub

## 初始化仓库

```powershell
git init
git add .
git commit -m "Initial open source release"
```

## 创建公开仓库并推送

```powershell
gh repo create zotero-codex-review-workflow --public --source . --remote origin --push
```

## 发布前检查

- [ ] 没有提交 Zotero 数据库；
- [ ] 没有提交未授权 PDF；
- [ ] 没有提交真实用户 Word 文档；
- [ ] `py scripts\reviewflow.py --help` 正常；
- [ ] `py -m unittest discover -s tests` 通过；
- [ ] README 中快速开始命令可复制运行。
