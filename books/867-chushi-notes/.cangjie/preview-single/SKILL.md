---
name: 867-environmental-study
description: |
  用于学习和回答《867 环境学 初试高分笔记》覆盖的环境学问题：先识别污染源或形成条件，再追踪迁移转化与受体后果，最后按源头、过程、末端、监测和管理组织可评分答案。触发信号包括“环境污染原因/危害/防治”“水气土固废农业生态”“环评、监测、QA/QC、清洁生产、循环经济”。不用于替代最新版教材、官方大纲、现行法规标准或真实工程设计。
metadata:
  cangjie.generated-by: cangjie-tools v2.5.0
  cangjie.variant: single
  cangjie.bundle-id: bundle.867-chushi-notes
  cangjie.capability-count: 10
  cangjie.entrypoint-count: 1
---
# 867 环境学 初试高分笔记 — 全书能力入口

## 触发与不触发

**适用**：与本书能力域相关的咨询与任务（见下方路由表的意图列）。
**不适用**：
- 只要求查当前法律、排放标准、限值或最新政策的事实查询。
- 没有现场数据和专业设计条件的真实工程参数、设备定型或安全决策。
- 只要求背诵未经来源核验的常考概率、历史数据或作者信息。

## 核心原则（常驻速览，概览类问题读到这里即可回答）

1. 先用环境容量与自净能力判断负荷是否在情境中超载。
2. 把污染物作为会迁移、转化、富集并影响受体的过程对象。
3. 治理优先前移到清洁原料、源头减量和过程控制，再处理残余物。
4. 技术选择必须匹配污染物性质、介质条件、目标、成本和二次污染风险。
5. 用目的驱动的监测、质量控制和评价把数据转成治理决策。
6. 规划先定目标并比较多方案，再安排实施保障和反馈。

## 能力路由（先读本表，按意图加载 1 张能力卡）

| 用户意图 | 先读 | 补读/备注 |
|---|---|---|
| 判断某排放是否构成环境污染；分析环境容量或自净能力是否被超过；解释同一排放在不同水体/土壤条件下的后果 | references/capabilities/context-capacity.md | references/capabilities/eutrophication-load.md、references/capabilities/soil-remediation.md、references/capabilities/agro-resource-loop.md、references/capabilities/planning-alternatives.md、references/capabilities/monitoring-data.md |
| 分析污染物会迁移到哪里；解释污染物在环境中的转化和暴露路径；设计跨介质污染监测点位 | references/capabilities/cross-media-tracing.md | references/capabilities/atmospheric-episode.md、references/capabilities/soil-remediation.md、references/capabilities/pesticide-risk.md、references/capabilities/monitoring-data.md |
| 分析水体富营养化或水华持续原因；区分外源负荷与内源负荷；设计氮磷削减和富营养化治理答案 | references/capabilities/eutrophication-load.md | references/capabilities/context-capacity.md、references/capabilities/monitoring-data.md |
| 判断伦敦型或光化学烟雾成因；分析大气污染为何在某天气积聚；提出前体物控制和气象关联监测措施 | references/capabilities/atmospheric-episode.md | references/capabilities/cross-media-tracing.md、references/capabilities/monitoring-data.md |
| 比较原位和异位土壤修复；为特定污染物和土壤条件选择修复技术；分析重金属固定稳定与植物/电动力学修复 | references/capabilities/soil-remediation.md | references/capabilities/context-capacity.md、references/capabilities/cross-media-tracing.md、references/capabilities/preventive-material-flow.md |
| 把末端治理方案改成源头预防方案；设计清洁生产或循环经济措施；按3R顺序分析企业物料流和固废治理 | references/capabilities/preventive-material-flow.md | references/capabilities/agro-resource-loop.md |
| 制定农药使用和病虫害防治方案；分析农药残留、抗药性或天敌损伤风险；回答农业面源污染与农产品安全题 | references/capabilities/pesticide-risk.md | references/capabilities/cross-media-tracing.md、references/capabilities/monitoring-data.md |
| 判断畜禽粪污能否资源化利用；设计生态农业种养循环；分析农田消纳能力、运输和季节约束 | references/capabilities/agro-resource-loop.md | references/capabilities/context-capacity.md、references/capabilities/preventive-material-flow.md |
| 设计环境监测方案和采样计划；解释监测质量保证与质量控制；判断异常值、检出限和数据能否上报 | references/capabilities/monitoring-data.md | references/capabilities/context-capacity.md、references/capabilities/cross-media-tracing.md、references/capabilities/eutrophication-load.md、references/capabilities/atmospheric-episode.md、references/capabilities/pesticide-risk.md、references/capabilities/planning-alternatives.md |
| 制定环境规划或区域综合治理方案；比较多个环境工程或生态治理备选方案；分析环评、目标设定和污染削减量分配 | references/capabilities/planning-alternatives.md | references/capabilities/context-capacity.md、references/capabilities/monitoring-data.md |

**非能力类查询**：
- 书名/作者/章节/整书概览 → references/overview.md
- 术语解释 → references/glossary.md
- 决策规则速查（不需要原文依据时） → references/cheatsheet.md
- 完整意图与关键词索引（本表未覆盖的意图先查这里） → references/capability-index.md

## 加载规则

- 每次任务先读本文件，再按路由表加载 **1** 张能力卡；任务明确跨域时最多加载 2 张。
- 概览/书名类问题不加载能力卡，用「核心原则」与 overview.md 回答。
- 路由表与 capability-index.md 都无法命中的意图，明确告知超出本书范围，不要硬套。

## 边界与判停

- 若题目要求现行法规、标准、阈值或最新真题证据，暂停套用资料并标记需要外部核验。
- 若缺少污染物、介质、受体或情境条件，不得假装给出唯一工艺选择，应先列出假设和信息缺口。
- 若原文表述疑似 OCR、错别字或反应式有冲突，保留原文锚点并明确不把它当作无条件事实。
