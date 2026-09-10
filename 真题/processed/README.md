# 真题处理区

这里区分三种状态：

- `raw/`：从 PDF/DOCX 直接抽取的文本，不人工润色；
- `ocr/`：扫描 PDF 的 OCR 草稿，可能有错字、漏字和题目顺序问题；
- `../analysis/`：经过题号、题型、题干、知识点和状态复核后的结构化数据。

`questions.jsonl` 中只有 `status: confirmed` 的记录才会进入频次和重点计算。
2013—2023 的部分题目来自“参考答案中可确认的考查主题”，`question_fidelity` 会标明是
`question-confirmed`、`topic-confirmed` 还是 `answer-confirmed`；这允许统计主题频次，
同时避免把答案 OCR 误装成逐字原题。OCR 不能识别出的题目必须保留在 `review-queue.md`，不得静默删除或猜测。
