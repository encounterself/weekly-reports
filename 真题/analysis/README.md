# 867 环境学考试分析产物

## 先看什么

1. `priority-summary.md`：考前分层清单，决定先背什么。
2. `must-memorize.md`：★★★★★ 核心必背。
3. `exam-knowledge-map.html`：可搜索的考试知识地图。
4. `concept-question-index.md`：从知识点回看历年题目。
5. `exam-trends.md`：年份覆盖、跨年频次和趋势标签。
6. `review-queue.md`：尚未确认的题目，不应直接背诵。

## 重新生成

```bash
python3 study-assistant-skills/exam-analysis/scripts/validate_exam_data.py \
  --concepts 真题/analysis/concepts.json \
  --questions 真题/analysis/questions.jsonl

python3 study-assistant-skills/exam-analysis/scripts/analyze_exam.py \
  --concepts 真题/analysis/concepts.json \
  --questions 真题/analysis/questions.jsonl \
  --out 真题/analysis
```

## 统计边界

当前纳入 2012—2025 年资料。2013—2023 的部分记录是根据参考答案核对出的考查主题，不保证逐字复原原题，具体见 `question_fidelity` 和 `source-inventory.md`。
