# 真题来源清单 V2

- canonical questions：`136` 条，作为 V2 唯一统计入口。
- historical_questions：`111` 条，仅用于旧版重叠/来源审计，不重复计数。
- canonical 与 historical 重叠 ID：`111`。

## 证据转换

`question-confirmed` → `question_confirmed`；`topic-confirmed` → `topic_confirmed`；`answer-confirmed` → `answer_confirmed`；缺少 fidelity 的非 2025 记录 → `inferred`。2025 来自题目材料且 status confirmed 的记录按 `question_confirmed` 处理；2025 `needs_review` 记录仍为 `inferred`。

## 统计边界

paper_question_count 按 `parent_question_id` 折叠；subquestion_count 单独列出。多 concept 题在关系层保留多标签，但不把一条纸面题重复算成多个 paper question。

## 旧 ID 兼容

`legacy-compatibility-v2.json` 显式列出 `v01`—`v10` 到 V2 concept 的一对多映射；旧版文件不被覆盖。
