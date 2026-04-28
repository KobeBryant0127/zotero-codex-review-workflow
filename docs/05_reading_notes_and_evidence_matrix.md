# 05 阅读笔记与证据矩阵

综述写作不要只堆摘要。建议建立 evidence matrix。

## 最小字段

见：`templates/literature_screening_table.csv`

核心列：

- CitationKey
- Authors
- Year
- Title
- StudyType
- PopulationOrDataset
- Method
- MainFinding
- Limitation
- ReviewSection
- UseInTable
- UseInFigure

## Codex 用法

你可以把单篇论文摘要/PDF 摘录给 Codex，让它按固定字段输出，但必须人工核对。

```text
请根据下面论文内容，填充 evidence matrix 的一行。
要求：只基于原文内容；不确定处写 unclear；不要补充外部信息。
字段：StudyType, PopulationOrDataset, Method, MainFinding, Limitation, ReviewSection。
```
