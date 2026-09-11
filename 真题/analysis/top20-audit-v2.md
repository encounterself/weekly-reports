# Top 20 V2 规则审查

> 自动审查结果；需要人工回看原 PDF/DOCX 的关系会明确列出。

- canonical records：136；relations：170；active concepts：39；bridge concepts：1。
- paper questions（按 parent 折叠）：131（关系层全局）。
- subquestions：13 条关系；原始子问记录：8。

## Top 20

| rank | concept | paper | subquestion | years | score | bridge |
|---:|---|---:|---:|---:|---:|---|
| 1 | 环境质量评价与监测指标 | 12 | 4 | 8 | 32 | no |
| 2 | 土壤重金属形态与迁移 | 14 | 3 | 7 | 16 | no |
| 3 | 生态农业、循环与生物多样性 | 7 | 0 | 7 | 46 | no |
| 4 | 环境规划与方案决策 | 8 | 0 | 7 | 58 | no |
| 5 | 活性污泥法 | 7 | 1 | 4 | 23 | no |
| 6 | 富营养化与氮磷负荷 | 6 | 0 | 6 | 38 | no |
| 7 | 生物有效性与食物链风险 | 7 | 1 | 5 | 12 | no |
| 8 | 固废焚烧、填埋与渗滤液 | 6 | 0 | 4 | 25 | no |
| 9 | 污染物迁移与暴露路径 | 8 | 0 | 6 | 8 | no |
| 10 | 清洁生产、源头减量与 3R | 7 | 0 | 6 | 50 | no |
| 11 | 烟气脱硫与除尘 | 6 | 0 | 4 | 18 | no |
| 12 | 环境污染判定 | 5 | 0 | 4 | 38 | no |
| 13 | 农药迁移、残留与风险控制 | 4 | 0 | 4 | 20 | no |
| 14 | 环境标准与基准 | 4 | 1 | 3 | 8 | no |
| 15 | A²/O 与生物脱氮除磷 | 3 | 1 | 3 | 15 | no |
| 16 | 水质指标（BOD/COD/TOC/TOD/pH） | 5 | 0 | 4 | - | no |
| 17 | 光化学烟雾 | 5 | 0 | 4 | 10 | no |
| 18 | 臭氧层与全球气候风险 | 3 | 0 | 3 | 18 | no |
| 19 | 酸雨 | 4 | 0 | 4 | 20 | no |
| 20 | 土壤污染修复与安全利用 | 3 | 1 | 3 | 18 | no |

## 需要人工复核

- `x01` 兼容桥接节点的 7 条关系必须逐题回看原 PDF/DOCX 后再细分；它不进入 Top 20。
- 2025 `S-01`、`S-03` 的原始题干已有 `needs_review`，其关系保留为 `inferred`，不应当写成题干确认。
- 多 concept 题的分值仍按原题记录复制到各关联 concept；若需要 concept-level 分值分摊，应在人工复核后增加 allocation 字段，不在 V2 自动猜测。

## v02/v05/v09/v10 对齐记录

| question_id | legacy | V2 concept(s) | method |
|---|---|---|---|
| `2025-J-01` | v10 | e01 | keyword/default |
| `2025-J-02` | v05 | s01 | keyword/default |
| `2025-J-03` | v02 | w01 | keyword/default |
| `2025-S-01` | v02 | w02 | keyword/default |
| `2025-S-02` | v05 | s04 | manual |
| `2025-S-03` | v02,v05 | s01 | keyword/default |
| `2025-S-04` | v02,v05 | x01 | manual |
| `2025-S-06` | v02 | w05 | keyword/default |
| `2025-SA-01` | v09 | m02,m03 | keyword/default |
| `2025-SA-02` | v05 | g03 | manual |
| `2025-SA-03` | v02 | w03,w02 | keyword/default |
| `2025-SA-04` | v02 | w05 | keyword/default |
| `2025-SA-05` | v09,v10 | m03,e03 | keyword/default |
| `2025-SA-06` | v02 | s01,g01,f04 | keyword/default |
| `2025-CA-01-1` | v02 | w02 | manual |
| `2025-CA-01-2` | v09,v10 | m03,e01 | manual |
| `2025-CA-01-3` | v02 | w07 | keyword/default |
| `2025-CA-02-1` | v02,v05 | s01,s04 | manual |
| `2025-CA-02-2` | v05,v09 | m01,m03 | manual |
| `2025-CA-02-3` | v05,v09 | s03,m03 | manual |
| `2013-N-03` | v02 | w02 | manual |
| `2013-N-04` | v10 | e02 | keyword/default |
| `2013-N-05` | v10 | e03 | keyword/default |
| `2013-SA-01` | v10 | g03 | keyword/default |
| `2013-SA-02` | v10 | e04 | keyword/default |
| `2014-N-01` | v02 | f04 | manual |
| `2014-N-02` | v09 | m03 | keyword/default |
| `2014-N-03` | v02 | w04 | manual |
| `2014-N-04` | v02 | w09 | manual |
| `2014-SA-02` | v05 | a03 | keyword/default |
| `2014-SA-04` | v02,v05 | s01,f04 | keyword/default |
| `2015-SA-01` | v02,v05 | s01,f04 | keyword/default |
| `2015-CA-01` | v02 | x01 | manual |
| `2015-CA-02` | v10 | e03 | keyword/default |
| `2016-N-01` | v02 | a06,f04 | manual |
| `2016-N-02` | v10 | e02 | keyword/default |
| `2016-SA-02` | v02 | g01,f04 | keyword/default |
| `2017-N-01` | v02 | w01 | keyword/default |
| `2017-N-02` | v10 | a02,e03 | keyword/default |
| `2017-N-03` | v10 | e04 | manual |
| `2017-SA-01` | v02 | r03 | manual |
| `2017-CA-01` | v09,v10 | m03,e03 | keyword/default |
| `2018-N-01` | v02 | w01,f01 | keyword/default |
| `2018-N-02` | v10 | e02,e03 | keyword/default |
| `2018-L-01` | v10 | x01 | manual |
| `2019-N-01` | v02 | w01,g03 | keyword/default |
| `2019-N-02` | v02 | w03 | keyword/default |
| `2019-SA-01` | v05 | s04,f03 | keyword/default |
| `2019-CA-01` | v02,v05 | s01,f04 | keyword/default |
| `2020-N-02` | v02,v09 | s04,m03 | keyword/default |
| `2020-N-03` | v10 | r03 | keyword/default |
| `2020-SA-01` | v05 | s02 | keyword/default |
| `2020-SA-03` | v09 | m03 | keyword/default |
| `2020-SA-04` | v05 | s03 | keyword/default |
| `2020-CA-01` | v05,v10 | x01 | manual |
| `2020-L-01` | v10 | f05 | manual |
| `2020-L-02` | v10 | r02 | keyword/default |
| `2021-SA-01` | v10 | e01 | keyword/default |
| `2021-SA-04` | v02 | w10 | manual |
| `2021-SA-05` | v02 | w07 | keyword/default |
| `2021-SA-07` | v09 | m02,m03 | keyword/default |
| `2021-CA-01` | v10 | r02 | keyword/default |
| `2021-L-01` | v09,v10 | x01 | manual |
| `2021-L-02` | v02,v05 | s04 | keyword/default |
| `2022-SA-01` | v02 | w06 | keyword/default |
| `2022-SA-02` | v02 | f02 | keyword/default |
| `2022-SA-04` | v09 | m01,m03 | keyword/default |
| `2022-SA-06` | v05 | a01 | keyword/default |
| `2022-SA-07` | v05 | w08,g03 | keyword/default |
| `2022-L-01` | v02 | w07,w02 | keyword/default |
| `2023-J-01` | v02,v05 | s01,f03 | keyword/default |
| `2023-S-01` | v05,v09 | x01 | manual |
| `2023-L-01` | v09 | w08 | keyword/default |
| `2023-L-02` | v10 | g01,g03 | keyword/default |
| `2023-CA-01` | v02,v10 | e03 | keyword/default |
| `2023-CA-02` | v10 | a05 | keyword/default |
| `2024-J-01` | v02,v05 | s01 | keyword/default |
| `2024-J-03` | v02 | w02 | keyword/default |
| `2024-S-01` | v05 | s01 | manual |
| `2024-S-02` | v02,v05 | s01 | manual |
| `2024-S-04` | v02 | w11 | manual |
| `2024-S-05` | v02 | w06 | keyword/default |
| `2024-S-08` | v10 | x01 | keyword/default |
| `2024-SA-01` | v10 | g01,g03 | keyword/default |
| `2024-SA-02` | v02,v05,v09 | s01 | keyword/default |
| `2024-SA-03` | v02 | w03,w02 | keyword/default |
| `2024-SA-05` | v09 | a03 | keyword/default |
| `2024-CA-01-1` | v02,v05 | s01 | manual |
| `2024-CA-01-2` | v02,v05,v09 | s01,m03 | manual |
| `2012-N-01` | v09,v10 | e01 | keyword/default |
| `2012-N-02` | v10 | e03 | keyword/default |
| `2012-N-03` | v02,v05 | s03 | keyword/default |
| `2012-SA-02` | v09 | m03 | keyword/default |
| `2012-SA-03` | v02 | w04 | keyword/default |
| `2012-SA-05` | v02,v05 | s01,f04 | keyword/default |
| `2012-L-01` | v10 | r03,f03 | keyword/default |
