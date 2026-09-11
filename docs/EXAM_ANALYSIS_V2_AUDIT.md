# 867 环境学真题分析 V2 审计

> 审计日期：2026-09-11。V2 只新增文件，不删除或覆盖 `真题/analysis/` 下的旧版产物。

## 1. 当前知识点粒度问题

旧版 `concepts.json` 只有 10 个 `v01`—`v10` 节点，节点同时承担课程章节、考试主题和统计单元三种职责。`v02 污染物迁移与转化` 被用于 COD/BOD、混凝、沉淀、活性污泥、生物膜、A²/O、农药迁移和土壤重金属等不同机制，因而不能回答“具体应该背哪一项”。`v10` 也把环境标准、环境影响评价、规划、厂址和方案决策混在一起。

旧版的 `children` 只是字符串清单，没有稳定的子节点 ID、来源锚点、题目映射或统计边界。`复习笔记-study/internal/state/knowledge.json` 复制了这 10 个统计节点，因此不能作为细粒度课程树。V2 将保留旧 ID 的别名关系，并用 Cangjie 已有章节、术语、原则和能力卡建立 `module → topic → concept` 三层树。

## 2. 当前题目统计问题

- `questions.jsonl` 有 136 条 canonical 记录，`historical_questions.jsonl` 有 111 条历史记录；后者是历史来源补充，不应与前者简单相加。
- 旧版按 concept assignment 计 `question_count`，没有区分一道综合题的父题和子问。`2025-CA-02-1/2/3` 因而会被当作三道完全独立的题。
- 旧版没有稳定的 `paper_question_count`、`subquestion_count`，也没有明确年数、近年年数、主观题、综合题和已知分值的统计口径。
- 多概念题会同时计入多个旧大节点，超级主题的计数因此膨胀；V2 会保留多标签关系，但把每个 paper question 和 subquestion 的统计字段分开。

## 3. 当前证据质量问题

现有记录的 `question_fidelity` 分布是：`question-confirmed` 50、`topic-confirmed` 33、`answer-confirmed` 28，另有 25 条没有该字段。旧版只把这些状态写成一句“跨年证据”，没有进入数值统计。

V2 统一为四级 `evidence_level`：

- `question_confirmed`：题干或题目材料可直接核对。
- `topic_confirmed`：可确认考查主题，但不保证逐字题干。
- `answer_confirmed`：主要由参考答案确认术语或主题。
- `inferred`：缺少明确题干/答案证据，依据现有 legacy concept 或关键词推断；不进入“已确认原题”的表述。

统计使用固定权重 1.00、0.75、0.60、0.35，并同时输出未加权计数，避免推断记录与原题确认记录看起来完全等价。

## 4. 当前重点计算问题

旧版使用 1—5 星级，且把多个大节点直接标为 `★★★★★`。星级阈值没有呈现纸面题、子问、年份、证据或分值之间的关系，`priority-summary.md` 因而无法区分“背哪一个细分单元”。

V2 改用：

- `core_score`：可复算的排序分数，使用证据权重后的 paper、subquestion、year、recent year、主观/综合题和已知分值。
- `priority_rank`：全体细粒度 concept 的稳定排序。
- `importance_level`：只按排名输出 `core`（Top 10）、`high`（Top 20）、`monitor`、`reference`，不再给所有主题贴五星。

公式和题型口径写入 `EXAM_ANALYSIS_V2_SCHEMA.md`，结果写入 `exam-frequency-v2.csv`。

## 5. 可复用的 Cangjie 知识体系

V2 不重新蒸馏 Cangjie，而是复用其已有可追溯材料：

- `books/867-chushi-notes/BOOK_OVERVIEW.md`：十二章课程骨架、源—过程—后果—对策答题链和章节边界。
- `books/867-chushi-notes/candidates/glossary.md`：环境容量、自净、BOD、COD、富营养化、监测等术语边界。
- `books/867-chushi-notes/candidates/principles.md`：污水处理级别、混凝/沉淀工艺比较、土壤修复、农药风险、监测 QA/QC、环评和规划决策等 25 条可复用原则。
- `books/867-chushi-notes/candidates/frameworks.md`：污染链、工艺比较、监测到治理闭环、生命周期和食物链等框架。
- `books/867-chushi-notes/dist/867-environmental-study/references/capabilities/`：已验证的能力卡及其章节/行号锚点。
- `复习笔记-study/`：只作为旧版学习状态和题库消费者；V2 不改写其内部状态。

## 6. V2 数据与产物变更

新增：

- `course-tree-v2.json`、`topics-v2.json`、`concepts-v2.json`
- `legacy-compatibility-v2.json`
- `exam-stats-v2.json`
- `question-concepts-v2.jsonl`、`evidence-v2.jsonl`
- `exam-frequency-v2.csv`
- `exam-topic-analysis-v2.md`、`exam-trends-v2.md`
- `priority-summary-v2.md`、`must-memorize-v2.md`
- `concept-question-index-v2.md`、`source-inventory-v2.md`
- `top20-audit-v2.md`

旧版 `concepts.json`、`questions.jsonl`、`historical_questions.jsonl`、旧统计 Markdown/CSV、PDF 和学习工作区均保留。V2 生成脚本为 `study-assistant-skills/exam-analysis/scripts/build_exam_v2.py`，校验脚本为 `study-assistant-skills/exam-analysis/scripts/validate_exam_v2.py`。

## 7. 典型题人工审查范围

V2 对 `v02`、`v05`、`v10`、`v09` 的高影响题目优先采用题干关键词和 Cangjie 原有术语进行细分：活性污泥、生物膜、沉淀、混凝、A²/O、BOD/COD、土壤重金属形态/修复、监测采样/QA-QC、环境质量评价/标准、环评和规划方案分别进入不同 concept。无法从现有记录确认的关系保留 `inferred` 或 `needs_review`，不伪装成逐字原题。
