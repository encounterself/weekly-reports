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

## V2 细粒度分析

V2 是新增的、可重复生成的细粒度数据层，不覆盖上述旧版文件：

- `course-tree-v2.json`：`module → topic → concept` 课程树。
- `concepts-v2.json`、`legacy-compatibility-v2.json`：细粒度 concept 与 `v01`—`v10` 兼容关系。
- `question-concepts-v2.jsonl`、`evidence-v2.jsonl`：题目关系、父子题和证据等级。
- `exam-stats-v2.json`、`exam-frequency-v2.csv`：纸面题/子问/年份/题型/分值及证据加权统计。
- `exam-topic-analysis-v2.md`、`exam-trends-v2.md`、`priority-summary-v2.md`、`must-memorize-v2.md`：细粒度分析、趋势和 Top 10/Top 20 优先级。
- `top20-audit-v2.md`：`v02`、`v05`、`v09`、`v10` 高影响归因审查及待人工复核项。

重新生成和校验：

```bash
python3 study-assistant-skills/exam-analysis/scripts/build_exam_v2.py \
  --questions 真题/analysis/questions.jsonl \
  --historical 真题/analysis/historical_questions.jsonl \
  --out 真题/analysis

python3 study-assistant-skills/exam-analysis/scripts/validate_exam_v2.py \
  --analysis 真题/analysis \
  --questions 真题/analysis/questions.jsonl
```
