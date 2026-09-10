---
name: exam-analysis
description: >
  将历年考研真题转成可复核的结构化题目，映射到已有课程知识点，并计算可解释的考试权重。
  用于 past paper analysis、题型统计、知识点对齐、重点排序和复习优先级生成；不用于预测某一年必考。
---

# Exam Analysis

这个 Skill 是 `study-assistant` 的前置数据层，不重新蒸馏教材，也不替代
`books/867-chushi-notes/dist/867-environmental-study` 中已经审计过的课程能力。

## 数据流

```text
PDF / DOCX / OCR 原文
  -> raw text（只读归档）
  -> questions.jsonl（人工复核的题目记录）
  -> concept_ids（一个题目允许多个知识点）
  -> metrics.csv + exam-knowledge-map.md + HTML/Mermaid
```

## 可靠性边界

- OCR 文本只能作为草稿，`needs_review` 记录不能进入最终频次结论。
- `score` 不确定时使用 `null`，不为了完整而猜分值。
- “出现频率”描述历史，不等于“下一年必考”。
- 每条重点必须能回溯到年份、题号、题型和原始文件。
- 综合题拆成小问；每个小问分别映射知识点，同时保留 `parent_question_id`。

## 当前 867 课程节点

优先复用 Cangjie 已产出的 10 个能力节点，使用稳定 ID `v01`—`v10`。
后续若需要更细的“定义/原理/方法/比较”子节点，在 `concepts.json` 中新增
子节点，不修改历史题目的 `question_id`。

## 生成命令

```bash
python3 study-assistant-skills/exam-analysis/scripts/analyze_exam.py \
  --concepts 真题/analysis/concepts.json \
  --questions 真题/analysis/questions.jsonl \
  --out 真题/analysis
```

输出包括：

- `exam-frequency.csv`：每个知识点的可解释指标；
- `exam-topic-analysis.md`：重点判定理由与证据题目；
- `exam-knowledge-map.md`：按星级排序的考试版知识地图；
- `exam-knowledge-map.mmd`：Mermaid 层级图；
- `must-memorize.md`：核心必背清单；
- `review-queue.md`：仍需人工核对的 OCR 或映射记录。
