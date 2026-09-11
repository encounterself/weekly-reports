# 867 环境学真题分析 V2 Schema

## 数据层

```text
course-tree-v2.json
  modules[]
    topics[]
      concepts[]
questions.jsonl / historical_questions.jsonl
  question-concepts-v2.jsonl
  evidence-v2.jsonl
  exam-frequency-v2.csv
```

### module

课程一级模块。字段：`module_id`、`name`、`source_chapters`、`topic_ids`。模块来自 `BOOK_OVERVIEW.md` 和 `knowledge.json` 的章节，而不是从频次倒推。

### topic

模块内的考试主题。字段：`topic_id`、`module_id`、`name`、`source_refs`、`concept_ids`。topic 解决“水环境/污水处理/土壤风险”等中层归属，不作为最终背诵统计单元。

### concept

可单独学习和统计的细粒度单元。字段：

```json
{
  "concept_id": "w05",
  "name": "活性污泥法",
  "module_id": "water",
  "topic_id": "water-treatment",
  "legacy_concept_ids": ["v02"],
  "source_refs": ["books/867-chushi-notes/candidates/principles.md#p06"],
  "status": "active"
}
```

`v01`—`v10` 不删除、不重命名；它们在 `legacy_concepts` 中作为兼容别名，并通过 `legacy_concept_ids` 指向 V2 concept。一个旧节点可以映射到多个新 concept。

## 题目关系层

### question-concepts-v2.jsonl

一行表示一条题目到一个细粒度 concept 的关系：

```json
{
  "question_id": "2025-CA-02-2",
  "paper_question_id": "2025-CA-02",
  "is_subquestion": true,
  "year": 2025,
  "concept_id": "monitoring-design",
  "legacy_concept_ids": ["v05", "v09"],
  "mapping_method": "keyword",
  "evidence_level": "inferred",
  "evidence_weight": 0.35,
  "source": "真题/25真题.docx"
}
```

`paper_question_id` 是统计纸面大题的唯一键；父题没有单独记录时，由子问的 `parent_question_id` 形成虚拟父题。`is_subquestion` 不改变题目来源，但会阻止把同一综合题的三个子问误报成三道独立大题。

### evidence-v2.jsonl

每条题目记录一行，保存 `evidence_level`、原始 `question_fidelity`、`status`、`source`、`evidence_weight`、`evidence_note`。`inferred` 只能表示映射或主题推断，不能在文档中写成“原题已确认”。

## 统计层

`exam-frequency-v2.csv` 每行一个 active concept，至少包含：

```text
concept_id,topic_id,module_id,concept,paper_question_count,subquestion_count,
question_assignment_count,year_count,recent_year_count,exam_years,recent_years,
subjective_count,comprehensive_count,total_score,weighted_score,
weighted_paper_count,weighted_subquestion_count,weighted_year_count,
weighted_recent_year_count,core_score,priority_rank,importance_level,
evidence_mix,question_ids
```

口径：

- `paper_question_count`：不同 `paper_question_id` 数，不把子问拆成独立大题。
- `subquestion_count`：有 `parent_question_id` 的记录数。
- `question_assignment_count`：题目—concept 关系条数，用于检查多标签，不作为独立大题数。
- `year_count`、`recent_year_count`：分别为 distinct 年份和最近可见五年（2021—2025）年份。
- `subjective_count`：名词解释、辨析、简答、问答、论述、分析、案例、材料等非客观题记录数。
- `comprehensive_count`：论述、分析、分析论述、案例分析、材料分析、综合题记录数。
- `total_score`：原记录中可核对的分值总和；空值不补估。
- `weighted_*`：按 evidence weight 加权；同一 paper 的子问仍单独反映在 subquestion 字段。

`core_score` 固定为：

```text
4 × weighted_paper_count
+ 1.5 × weighted_subquestion_count
+ 1.5 × weighted_year_count
+ 1.0 × weighted_recent_year_count
+ 0.25 × subjective_count
+ 0.50 × comprehensive_count
+ 0.02 × weighted_score
```

按 `core_score` 降序、`concept_id` 升序排名。`importance_level` 仅由排名产生：1—10 为 `core`，11—20 为 `high`，21—30 为 `monitor`，其余为 `reference`。它不是押题结论。

## 趋势层

趋势只基于该 concept 的实际出现年份，不对缺失年份插值：

- `长期稳定高频`：至少 6 个年份，且最近五年出现年份不少于 3。
- `长期稳定但近期下降`：至少 6 个年份，且最近五年出现年份少于长期年份的一半。
- `近年升温`：最近五年出现年份不少于 3，且早期（2012—2020）不超过最近五年。
- `周期性`：至少 3 个年份，存在间隔至少 2 年的重复出现，且不是上述三类。
- `多年未考`：有历史记录但最近五年没有出现。
- `偶发`：出现年份不超过 2。

标签是规则计算结果，不能写成“今年必考”或其他预测。

