# Contributing

感谢你考虑贡献本项目。

## 开发原则

1. 不鼓励 AI 编造引用；所有参考文献必须可追溯到数据库或 Zotero 条目。
2. 尽量使用 Python 标准库，降低新手安装门槛。
3. Windows + Word + Zotero 是当前优先支持环境。
4. 所有自动化都应该保留人工质控节点。

## 本地验证

```powershell
py scripts\reviewflow.py --help
py scripts\reviewflow.py check
py -m unittest discover -s tests
```

## Pull Request 建议

- 说明修改目的；
- 如果修改 CLI，请补充或更新测试；
- 如果新增教程，请确保新手能按步骤复现；
- 不要提交个人 Zotero 数据库、PDF、Word 临时文件或真实未授权文献全文。
