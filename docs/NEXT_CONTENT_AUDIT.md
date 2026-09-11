# 下一阶段内容审计：从考试分析到可学习复习资料

> 审计日期：2026-09-11  
> 目的：在不重做 Cangjie、OCR 或 exam-analysis 的前提下，把已验证的考试数据加工为学生可以阅读、背诵、训练和冲刺的内容。  
> 状态：本文件是内容生产的输入审计和验收基线，不是新的考试统计结果，也不作“今年必考”预测。

## 1. 审计范围与结论

本次只读检查了以下内容：

- `真题/analysis/`：旧版十节点产物、V2 `course-tree-v2.json`、`topics-v2.json`、`concepts-v2.json`、`question-concepts-v2.jsonl`、`evidence-v2.jsonl`、`exam-stats-v2.json`、V2 频率/趋势/重点/索引、知识地图、复习总册及来源清单。
- `books/867-chushi-notes/`：`BOOK_OVERVIEW.md`、`DIGEST.md`、`GLOSSARY.md`、`candidates/`、`verified.md`、`dist/867-environmental-study/` 及其能力卡。
- `复习笔记-study/`：`knowledge.json`、`progress.json`、`digest.md`、`exam-style.md`、全局题库、dashboard 和工作区脚本。
- `study-assistant-skills/`：study-assistant、study-teach、study-quiz、study-feynman、study-mindmap 与 exam-analysis 的既有契约和脚本。

总体判断：数据分析 V2 已解决“旧节点过大”和“纸面题/小问混计”的主要结构问题，但尚未形成学习内容层。下一阶段应新增 `learning_units` 和出版内容模型，使用 V2 统计作证据、使用 Cangjie 能力卡作解释骨架、使用 study-assistant 作学习状态和训练入口。旧版产物继续作为兼容和追溯层，不能覆盖或删除。

### 当前可核验的基线

| 项目 | 当前事实 | 内容生产含义 |
|---|---:|---|
| canonical `questions.jsonl` | 136 条 | 作为唯一考试记录入口；不把 `historical_questions.jsonl` 再加一次 |
| paper questions（按 `parent_question_id` 折叠） | 131 道 | 纸面题数量用于“独立大题/试卷题”统计 |
| 子问记录 | 8 条；关系层 13 条 | 子问单独显示，不能当成 13 道独立大题 |
| V2 关系 | 170 条 | 一题多学习单元时保留关系，但要避免重复加总分值 |
| V2 concept | 40 个，其中 active 39、bridge 1 | V2 concept 仍是考试映射层，不等于学生最小背诵单元 |
| evidence 关系 | question 89、topic 44、answer 35、inferred 2 | 学习内容必须显示证据等级；`inferred` 不能写成原题事实 |
| 证据权重 | 1.00 / 0.75 / 0.60 / 0.35 | 重点排序可使用加权分，不能只看原始题目数 |
| 2025 待复核 | `2025-S-01`、`2025-S-03` | 不生成确定题干式答案；只能标注待复核或主题级内容 |
| historical 重叠 | 111 条与 canonical 重叠 | 仅作来源/旧版审计，不进入出版统计 |
| study 题库 | 34 条 | 可作训练入口，但不是 136 条考试记录的替代物 |
| study 知识树 | 10 个大点 | 需迁移到 `priority_rank → learning_unit`，保留 mastery 字段 |

## 2. 复用与转换矩阵

| 既有产物 | 可直接复用 | 必须转换/补充 | 不应直接复用 |
|---|---|---|---|
| `questions.jsonl` | question_id、parent、年份、题型、题干、分值、来源、状态 | 映射到 `learning_unit_id`；派生 paper/subquestion 计数；展示 evidence | 未核实题干不得润色成“原题”；多标签分值不得逐单元重复相加 |
| `historical_questions.jsonl` | 历史主题和答案证据的来源审计 | 作为低证据题目输入并带 `evidence_level` | 不与 canonical 合并计数；不伪装逐字题干 |
| `concepts.json` (`v01`–`v10`) | 旧 ID、模块/章节、向后兼容链接 | 在下游同时保留 `legacy_concept_id` 和 V2/learning_unit ID | 不再把十个旧节点当背诵标题 |
| `course-tree-v2.json` / `concepts-v2.json` | module→topic→concept 骨架、来源引用、bridge 标记 | 在 topic 下添加 learning unit；为每个单元写学习目标和内容卡 | 不修改旧 V2 ID 或把 bridge 当核心重点 |
| `exam-frequency-v2.csv` / `exam-stats-v2.json` | paper、subquestion、year、subjective、comprehensive、total/weighted score、rank/trend | 生成 learning-unit 聚合；明确多概念题的分值分摊策略 | 不用旧 `exam-frequency.csv` 的大节点数字直接印进新册 |
| `priority-summary-v2.md` / `must-memorize-v2.md` | Top 20/Top 10 的初筛、证据混合、趋势标签 | 转成少量 `priority_rank`（核心必背、高频重点、重点理解、一般掌握、低优先级） | 不把 `core` 或五星解释成预测；不把 Top 20 全部写成同等必背 |
| `exam-trends-v2.md` | 由实际年份计算的趋势标签 | 在单元层重算，并说明样本年数和最近窗口 | 不沿用旧版“稳定”泛标签或主观预测 |
| `concept-question-index-v2.md` | 题目回溯入口、父子关系、证据等级 | 改为 learning unit→question 索引；同一 paper 题只显示一次并列出子问 | 不按关系行数误称独立题数 |
| `exam-knowledge-map.*` | 离线 HTML/Mermaid/Markdown 的展示方式 | 节点改为 module→topic→learning_unit，显示 rank、证据、mastery | 不把概念列表当学生学习路线 |
| `final/867环境学真题驱动复习总册.*` | 版式、来源边界、旧版导读和打印经验 | 作为旧版链接/对照；从新 `publish/content/` 生成五册 | 不在旧总册上原地改写或覆盖 |
| Cangjie `BOOK_OVERVIEW.md` / `DIGEST.md` | 课程十二章主线、源—过程—后果—对策论证链、局限声明 | 拆成学习目标、背诵块、答题骨架和边界提示 | 不把资料的“常见/重点”当考试事实；不覆盖最新版标准 |
| Cangjie `GLOSSARY.md`、`candidates/`、`verified.md` | 定义、易混点、出处、框架、反例、案例、能力卡 | 按单元填“必须掌握/背诵/高频考法/关键词/易错点” | 不直接复制未经证实的参数、法规、案例数据 |
| `复习笔记-study/internal/state/knowledge.json` | status、mastery、note、学习状态持久化约定 | 改为引用 learning_unit；以 priority_rank 决定入口 | 不把十个旧点继续作为唯一学习粒度 |
| `question-bank/question-bank.json` | 题库格式和 study-quiz 的全局题库契约 | 增加来源/证据/learning_unit 关联或建立只读映射 | 不为每章复制一套题库，不把 AI 新题当历年事实 |

## 3. 统计边界与防重复规则

1. **唯一入口**：出版统计只读取 `questions.jsonl`；`historical_questions.jsonl` 只用于来源审计。任何合并脚本必须检查重复 `question_id`。
2. **纸面题与子问**：`paper_question_id = parent_question_id ?? question_id`。`paper_count` 按唯一 paper ID 计，`subquestion_count` 按子问 ID 计。案例题的多个子问可以映射不同单元，但不得把父题重复计为多道大题。
3. **多单元映射**：一题可有多个关系；关系用于回溯和覆盖，分值默认记在 paper 层。只有人工确认后才能增加 `score_allocation`，否则不得把整题分值复制到每个单元。
4. **证据等级**：`question_confirmed`、`topic_confirmed`、`answer_confirmed`、`inferred` 必须逐题保留。统计表同时给原始计数、加权计数和证据混合；学习单元正文引用题目时标出等级。
5. **趋势**：只由出现年份计算；保留样本年份，不对缺失年份插值，不产生“明年必考”“今年必考”。趋势标签至少覆盖长期稳定高频、长期稳定但近期下降、近年升温、近年下降、周期性、偶发、多年未考。
6. **优先级**：`core_score` 用于排序，`priority_rank` 用于学习顺序，`importance_level` 用于出版分层。五星仅作兼容显示；新册正文必须以 Top 20/Top 50 和分层清单为准。
7. **可追溯性**：每个 learning unit 至少有一条 question/evidence 关系或明确标为“课程补全、暂无真题证据”。没有真题证据的课程核心可以进入地图和一般掌握，但不能伪称高频。

## 4. learning_unit 切分规则

### 定义

`learning_unit` 是学生可以独立学习、背诵、被测验，并能对应一组真题的最小合理内容单元。层级固定为：

```text
module → topic → learning_unit
```

V2 `concept_id` 作为考试映射和兼容字段保留；一个学习单元可关联一个或多个 V2 concept，但不能反向修改既有 concept ID。

### 切分原则

- **可独立教学**：一个单元能在一次 study-teach 讲解中完成，拥有明确学习目标和边界。
- **可独立背诵**：能形成一页左右的定义/机制/比较/答题骨架，而不是把整章或整套工艺塞在一起。
- **可独立出题**：至少能设计名词解释、简答或案例的一个可评分任务；综合题可通过多个单元组合。
- **按考试动作切分**：优先拆成定义、机理/过程、参数或条件、方法比较、风险与控制、监测/评价等可评分动作。
- **保留综合关系**：跨介质、综合案例和决策流程用 `bridge`/`composite` 关系连接，不强行归入单一单元。
- **避免过细**：COD、BOD 等只有在题型或答题边界明显不同、且能独立训练时才拆开；不要把一个定义的组成部分做成单独节点。
- **证据驱动**：先从 V2 concept 和 Cangjie 已有能力卡候选，再依据题目聚类确认，不凭空扩展课程树。

### 首批候选单元（用于生成阶段，不覆盖 V2）

首批应优先覆盖当前 Top 20 与 v02/v05/v09/v10 高影响映射。示例：

| module/topic | learning unit 候选 | 主要已有来源 |
|---|---|---|
| 水环境/污水处理 | 活性污泥法、生物膜法、沉淀、混凝、A²/O 与生物脱氮除磷、厌氧/UASB、膜分离与反渗透 | V2 `w02`–`w11`；Cangjie `principles.md` |
| 水环境/水质与生态 | BOD/COD/TOC/TOD/pH、水体富营养化与氮磷负荷、水体自净 | V2 `w01`、`w08`、`f02`；`GLOSSARY.md` |
| 大气环境/污染事件与控制 | 酸雨、光化学烟雾、大气扩散与气象条件、烟气脱硫与除尘、噪声污染 | V2 `a01`–`a06`；能力卡 `atmospheric-episode.md` |
| 土壤与农业/土壤风险 | 土壤重金属形态与迁移、土壤背景值、土壤修复与安全利用、生物有效性与食物链风险 | V2 `s01`–`s04`；`soil-remediation.md` |
| 土壤与农业/农业生态 | 农药迁移残留与风险控制、农业污染与畜禽粪污消纳、生态农业/循环/生物多样性 | V2 `g01`–`g03`；`pesticide-risk.md`、`agro-resource-loop.md` |
| 固废与全过程/固废 | 危险固废鉴别、焚烧/填埋/渗滤液、清洁生产/源头减量/3R | V2 `r01`–`r03`；`preventive-material-flow.md` |
| 监测与治理/监测 | 环境监测设计与采样、QA/QC 与有效数据、环境质量评价与指标 | V2 `m01`–`m03`；`monitoring-data.md` |
| 监测与治理/规划 | 环境标准与基准、环境影响评价、环境规划与多方案决策、制度与经济手段 | V2 `e01`–`e04`；`planning-alternatives.md` |

候选表不是最终单元清单。生成时必须为每个单元记录 `unit_id`、`name`、`module_id`、`topic_id`、`source_refs`、`v2_concept_ids`、`legacy_concept_ids`、`question_ids`、`evidence_mix`、`priority_rank`、`importance_level`、`learning_objectives` 和 `status`。

## 5. Cangjie 来源与边界

### 可复用内容

Cangjie 已提供课程知识树的语义骨架，而不是考试统计替代品：

- `BOOK_OVERVIEW.md` 的十二章主线可用于 module/topic 命名和章节导航。
- `GLOSSARY.md` 提供定义、易混点和可追溯原文锚点，适合生成“必须掌握/必须背诵”。
- `candidates/principles.md`、`frameworks.md`、`counter-examples.md`、`cases.md` 提供原理、比较、边界、反例和案例素材。
- `verified.md` 与 `dist/.../references/capabilities/*.md` 提供十个已验证能力：容量判断、跨介质迁移、富营养化负荷、大气事件诊断、土壤修复选择、预防生产、农药风险、农业资源闭环、监测闭环、多目标规划决策。
- 每张能力卡已有 `source_anchor` 和 Boundary，可直接作为答题骨架和易错点来源。

### 明确边界

- Cangjie 来源是匿名考试讲义，作者/年份/教材版本未知；不能将“笔记中有”转写成“真题高频”。
- 法规、标准、阈值、工艺参数和现实工程选型需标注版本并回到官方/指定教材核验；不在本阶段自行补齐。
- 能力卡中的新情境属于训练示例，不得当作历年原题或统计证据。
- Cangjie 的 `promoted/router` 是能力发现和复用状态，不等于 priority_rank；两套字段必须分开。

## 6. study-assistant 集成审计

已有 study-assistant 的编排、讲解、测验、费曼检验和脑图技能可继续使用，尤其是：

```text
priority_rank → learning_unit → study-teach → study-quiz/study-feynman → mastery
```

当前缺口如下：

1. `复习笔记-study/internal/state/knowledge.json` 仍只有 10 个大点，并引用旧 `exam-frequency.csv`；需要增加或迁移到 learning unit，但保留旧字段/状态兼容。
2. 题库只有 34 条，且尚未全面带 V2 evidence、paper/subquestion 和 learning_unit 关系；训练册必须同时支持“历年原题”和“新编练习”两种来源标签。
3. `validate_workspace.py` 当前报告缺少 `open/chapters`、`open/quizzes`、`internal/textbook`、`internal/lessons`、`internal/mindmaps`、`internal/reports` 目录；内容生产前应按既有脚本契约补齐目录或调整验证输入。
4. study-teach 要求一次讲一个知识点；出版内容应把每个 learning unit 作为一个讲义单元，不能直接把 Top 20 表格当讲义。
5. study-quiz 的全局题库契约应保持不变；章节训练、高频训练、综合训练和模拟训练用筛选/组卷配置实现，不复制题库。
6. study-feynman 的 mastery/note 写回必须使用稳定 `learning_unit_id`，并保留旧 `knowledge.json` ID 的兼容映射。

## 7. 五册出版输入与验收清单

PDF 不直接由模型从零输出。先从既有 V2/Cangjie/study 数据生成 `publish/content/`，建议至少包含：

| 文件 | 必需内容 | 主要来源 |
|---|---|---|
| `knowledge-map.json` | module/topic/unit 树、rank、evidence、mastery、题量摘要、学习顺序 | course-tree-v2、learning_units、exam-stats-v2、knowledge.json |
| `core-handbook.json` | Top 20/Top 50 单元卡：重要度、证据、掌握、背诵、考法、关键词、骨架、易错、真题 | learning_units、V2 索引、Cangjie glossary/frameworks |
| `exam-guide.json` | 题型、纸面题/子问边界、年份覆盖、趋势、证据说明和答题策略 | questions、evidence-v2、exam-trends-v2、exam-style |
| `practice-book.json` | 题目、paper/subquestion、来源、答案、评分点、单元、题目与答案分离 | questions、question-bank、concept-question-index |
| `crash-course.json` | 核心背诵、简答/论述骨架、对比表、易错点、最后一日清单 | core-handbook、Cangjie cheatsheet、exam-style |

五册验收要求：

- `01_知识地图与重点.pdf`：首屏给出全科 module/topic、核心 Top 20、学习顺序和统计边界；地图节点能追溯到 unit。
- `02_核心背诵手册.pdf`：只收录核心必背和高频重点；每单元必须有“必须掌握”和“必须背诵”两栏，背诵文本可脱离表格阅读。
- `03_历年真题考点册.pdf`：按 learning unit→题目组织；显示年份、题型、paper/subquestion、证据等级和来源，不按年份堆砌。
- `04_真题训练册.pdf`：题目与答案分页或分册分离；支持章节/高频/综合/模拟四种组卷；原题和新编题有明显标签。
- `05_考前冲刺手册.pdf`：严格压缩为核心记忆、常见答题骨架、对比表、易错点和 Checklist；不添加无证据预测。

### 内容质量门

在导出 PDF 前逐单元检查：

1. 是否有真实 `question_ids` 或明确的课程补全标记；
2. paper_count、subquestion_count、year_count、subjective_count、comprehensive_count、total_score 是否来自同一统计口径；
3. 是否存在同一 paper 题重复计数或整题分值复制；
4. evidence_level 是否显示且与题干 fidelity 一致；
5. 是否把大主题改写成可学习的 unit，而不是再次输出“污染物迁移与转化 45题”；
6. 必须掌握是否回答“学完会什么”，必须背诵是否给出可复述文本；
7. 高频考法是否来自实际 question 记录，答题骨架是否来自 Cangjie 可追溯来源；
8. 不得出现“今年必考”“一定会考”等预测措辞；
9. 中文字体、表格换页、长题干、脚注和来源链接在 A4 打印/导出后无溢出、截断或重叠；
10. PDF 目录、页码、书签、标题层级和五册间 unit 名称一致；生成后应做文本抽检、页数/空白页检查和至少一轮视觉检查。

## 8. 旧产物保护协议

- 不删除、不覆盖、不重命名 `真题/analysis/` 现有旧版和 V2 统计、`final/867环境学真题驱动复习总册.*`、Cangjie 源文件以及 study-assistant 既有题库/状态。
- 新文件统一使用新后缀或新目录：`*-v2` 已存在的继续保留；学习内容放在 `learning_units/` 或 `publish/content/`；五册 PDF 使用明确的 `01`–`05` 文件名。
- 任何脚本重跑前先做输入快照和输出路径检查，禁止把新结果写回旧文件。
- 旧版统计只用于兼容对照；新 PDF 的“事实来源”必须能回溯到 canonical question、evidence、Cangjie source_anchor 或明确的课程补全记录。
- 每个阶段完成后记录：修改/新增文件、使用的已有数据、验证命令和剩余缺口；未经质量门通过不得进入下一册或继续 PDF 产品化。

## 9. 推荐执行顺序

1. 依据本审计建立 `learning_units` 数据模型和兼容映射。
2. 用 V2 Top 20 及 v02/v05/v09/v10 审查记录生成首批核心单元，逐单元绑定 Cangjie 来源和题目证据。
3. 计算 unit-level priority_rank 与内容字段，人工检查题量、分值、重复和证据等级。
4. 生成 `publish/content/` 五类 JSON，先做 schema/引用/统计一致性校验。
5. 生成并视觉检查五册 PDF；失败时只修正新内容层或模板，不回写旧产物。
6. 将 study-assistant 的入口从旧十节点切换到 `priority_rank → learning_unit`，并验证 mastery 写回、题库筛选和脑图渲染。

