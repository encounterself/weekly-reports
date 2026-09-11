"""Build student-facing learning units from the existing exam-analysis V2 layer.

This script is deliberately a transformation layer: it never edits the V1/V2
analysis files and keeps every unit traceable to concept IDs and question IDs.
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
ANALYSIS = ROOT / "真题" / "analysis"
OUT = ROOT / "publish" / "content"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def clean(value: Any) -> str:
    return str(value or "").strip()


# These are concise, exam-oriented transformations of the existing Cangjie
# principles. They are not new frequency claims and do not add legal limits.
CARDS: dict[str, dict[str, Any]] = {
    "m03": {"why": "监测、指标和质量评价同时出现在多年真题中，且常以简答或材料题要求完整流程。", "master": ["区分监测目的、指标选择、评价对象与评价结论", "能把指标含义、采样结果和环境质量判断连成证据链"], "memorize": ["监测目的→污染源/受体调查→点位、时间、频次→采样分析→质量控制→评价报告", "BOD、COD、TOC、TOD、pH 的定义和适用场景对照"], "ask": ["监测目的、基本程序与质量评价", "给出指标或监测结果并判断环境质量"], "keywords": ["目的明确", "代表性", "指标选择", "质量控制", "评价结论"], "skeleton": ["先界定评价对象和目标", "再说明指标与采样设计依据", "补充 QA/QC 和异常值处理", "最后按标准或基准给出有条件的评价结论"], "pitfalls": ["只罗列指标，不说明指标与问题的对应关系", "把监测结果直接当成达标结论，忽略标准、时段和代表性"]},
    "s01": {"why": "土壤重金属题跨名词、简答和案例，近年连续出现；题目常要求形态、迁移和风险联系。", "master": ["区分总量、形态、有效态和可迁移态", "解释 pH、有机质、氧化还原条件等对迁移的影响"], "memorize": ["重金属形态→土壤性质控制→迁移介质→植物/水体暴露", "风险控制优先切断源头、降低有效性并进行安全利用"], "ask": ["形态分析方法及意义", "重金属在土壤—水体—植物间迁移的机制与控制"], "keywords": ["形态分级", "pH", "有机质", "氧化还原", "生物有效性", "暴露路径"], "skeleton": ["先定义污染物形态和风险对象", "按物理、物理化学、生物过程解释迁移", "再联系暴露路径和生物有效性", "最后提出源头控制、稳定化和监测措施"], "pitfalls": ["把总量高等同于生物有效性高", "只写修复技术名称，不写土壤条件和适用边界"]},
    "g03": {"why": "生态农业、循环利用和生物多样性在多年主观题中反复出现，适合用系统性论述得分。", "master": ["说明生态农业的物质循环、能量利用和风险控制逻辑", "区分资源化、循环和生物多样性保护目标"], "memorize": ["减量—再利用—再循环的优先顺序", "生态农业闭环：种植/养殖互补、养分回流、土壤肥力与承载力校核"], "ask": ["生态农业内涵、原则与实施路径", "农业污染综合防治与生态循环方案"], "keywords": ["闭环", "养分回流", "承载力", "源头减量", "多样性", "全过程"], "skeleton": ["先界定系统边界与主要输入输出", "再写减量、循环和污染控制措施", "补充承载力、经济可行性和生态风险", "最后给出可监测的实施与反馈机制"], "pitfalls": ["把循环利用写成单一末端处理", "忽略规模、运输和消纳能力"]},
    "e03": {"why": "环境规划与方案决策常以论述或案例出现，分值高且要求比较多个约束条件。", "master": ["能从目标、污染削减、技术、经济和实施条件比较方案", "区分规划流程与环评工程分析"], "memorize": ["目标确定→基线与约束→方案生成→定性/定量比较→推荐与实施反馈", "方案比较五维：达标效果、技术可行、经济成本、环境风险、实施管理"], "ask": ["环境规划基本程序", "多方案比较并提出推荐方案"], "keywords": ["目标", "约束", "定性定量", "综合比较", "可实施性"], "skeleton": ["先写目标和评价准则", "逐项比较污染削减、成本、风险和可实施性", "指出权衡关系与不确定性", "给出推荐方案及监测反馈安排"], "pitfalls": ["只写一个方案的优点", "用‘最优’替代有条件的比较结论"]},
    "w02": {"why": "活性污泥法是水处理核心工艺，近年连续出现，常考原理、运行条件和工艺比较。", "master": ["解释微生物降解有机物、沉淀分离和污泥回流", "联系负荷、溶解氧、泥龄和污泥沉降性分析运行"], "memorize": ["进水→曝气反应→二沉分离→回流/剩余污泥处置", "运行控制：有机负荷、DO、SRT/HRT、回流比、污泥沉降性"], "ask": ["活性污泥法原理与流程", "与生物膜法或厌氧法比较"], "keywords": ["微生物絮体", "曝气", "二沉池", "回流污泥", "泥龄", "负荷"], "skeleton": ["先画/写流程和功能", "再说明微生物反应与固液分离", "结合运行参数解释处理效果", "最后指出剩余污泥和异常工况控制"], "pitfalls": ["把 HRT、SRT、污泥回流比混为一谈", "只写曝气，不写二沉和污泥线"]},
    "w08": {"why": "富营养化与氮磷负荷贯穿水生态题，题目常要求成因、过程、后果和治理闭环。", "master": ["从外源输入、内源释放和水体响应解释富营养化", "能按氮磷负荷和水体条件提出分层治理措施"], "memorize": ["外源控制优先：调查排放、监测氮磷、核算负荷、削减输入", "内源措施需结合底泥累积、释放条件和水体交换"], "ask": ["形成条件、生态后果与治理", "氮磷负荷核算或控制方案"], "keywords": ["限制因子", "氮磷负荷", "藻类暴发", "缺氧", "外源/内源"], "skeleton": ["先列出营养盐来源和水体条件", "说明藻类增长、分解耗氧和生态后果", "提出外源优先、内源协同的措施", "用监测指标和反馈评价效果"], "pitfalls": ["把‘有营养盐’直接等同于必然富营养化", "只治理藻类，不控制负荷来源"]},
    "s04": {"why": "生物有效性和食物链风险把土壤污染与健康效应连接起来，适合综合题和辨析题。", "master": ["区分环境浓度、有效态、吸收和食物链暴露", "能识别污染物进入人体或生态受体的主要路径"], "memorize": ["污染源→土壤形态/有效性→生物吸收→食物链富集→受体风险", "风险控制优先降低有效性、切断暴露并持续监测"], "ask": ["为何总量不等于风险", "食物链暴露路径及控制"], "keywords": ["有效态", "吸收", "富集", "暴露路径", "受体", "风险"], "skeleton": ["先区分总量与有效性", "再按迁移和摄取过程说明暴露", "判断受体、剂量和不确定性", "提出源头、过程和末端组合控制"], "pitfalls": ["把生物富集和生物放大混写", "忽略受体和暴露途径"]},
    "r02": {"why": "焚烧、填埋和渗滤液题覆盖工艺、二次污染和全过程管理，近年证据集中。", "master": ["比较焚烧与填埋的适用条件、主要污染物和控制环节", "解释渗滤液产生、收集和处理逻辑"], "memorize": ["焚烧控制：3T+1E、烟气净化、飞灰/底渣分流", "填埋控制：防渗、渗滤液收集处理、填埋气和长期监测"], "ask": ["焚烧影响因素与污染控制", "填埋渗滤液处理或工艺比较"], "keywords": ["3T+1E", "二噁英", "飞灰", "防渗", "渗滤液", "长期监测"], "skeleton": ["先按废物性质和目标比较路线", "分别写主过程、污染物和控制点", "补充二次污染与运行维护", "最后落到监测和安全处置"], "pitfalls": ["把焚烧等同于无害化终点", "忽略飞灰危险性和填埋长期风险"]},
    "f04": {"why": "迁移与暴露是多个模块的共同机制，适合用来串联案例，但不应替代具体工艺单元。", "master": ["识别污染物进入的介质、受体和迁移类型", "把迁移变化连接到危害、暴露和控制点"], "memorize": ["机械迁移、物理化学迁移、生物迁移三类过程", "源→介质→迁移/转化→受体→暴露→控制"], "ask": ["污染物迁移机制", "跨介质暴露路径分析"], "keywords": ["介质", "迁移", "转化", "受体", "暴露", "控制点"], "skeleton": ["先界定源、介质和受体", "按三类迁移过程解释变化", "指出暴露路径和风险", "提出切断源头、阻断迁移和监测措施"], "pitfalls": ["把所有水处理或土壤题都归为迁移", "只写污染源，不写受体和控制点"]},
    "r03": {"why": "清洁生产和 3R 是跨章节的全过程治理框架，常用于论述题收束答案。", "master": ["按源头、过程、产品和末端识别减排机会", "能按减量—再利用—再循环解释措施优先级"], "memorize": ["输入端减量优先，过程少废/无废，产品可维修回收，末端处理兜底", "3R：Reduce→Reuse→Recycle，剩余物再安全处置"], "ask": ["清洁生产内涵与实施", "资源约束、循环经济与污染治理"], "keywords": ["源头", "过程", "产品生命周期", "3R", "少废", "末端兜底"], "skeleton": ["先做物料/能量流分析", "按源头、过程、产品、末端列措施", "比较减排效果、成本和风险", "安排审核、监测和持续改进"], "pitfalls": ["把末端治理当作清洁生产全部内容", "只列口号，缺少可核查的过程节点"]},
    "a04": {"why": "烟气脱硫与除尘属于大气污染控制的典型工艺比较题，要求同时写机理、设备和适用条件。", "master": ["区分颗粒物捕集与气态污染物吸收/吸附机制", "能按粒径、浓度、温度和副产物处理选择工艺"], "memorize": ["除尘：惯性/离心、过滤、静电、湿式等机制对照", "脱硫：吸收剂、气液接触、脱硫效率与副产物处置"], "ask": ["除尘器原理和影响因素", "脱硫工艺比较与组合控制"], "keywords": ["粒径", "荷电", "过滤", "吸收", "脱硫效率", "副产物"], "skeleton": ["先识别污染物性质和排放条件", "写设备机理与关键控制参数", "比较效率、压降、能耗和二次污染", "给出组合工艺与监测要求"], "pitfalls": ["把粉尘和气态污染物用同一种机理解释", "只写去除率，不写副产物和运行约束"]},
    "f03": {"why": "污染判定是基础概念，却常以辨析或判断题考查边界条件。", "master": ["用自净能力、环境质量和健康/生态影响综合判定污染", "区分‘存在污染物’与‘构成环境污染’"], "memorize": ["输入量/强度超过自净能力并造成质量或健康生态影响，才构成污染判定依据", "判定需结合介质、时间尺度、功能目标和受体"], "ask": ["环境污染定义与判定条件", "判断陈述是否完整"], "keywords": ["自净能力", "环境质量", "受体", "功能目标", "条件"], "skeleton": ["先列输入与环境容量/自净能力", "再检查质量、健康和生态影响", "说明时间、空间和功能条件", "避免仅凭污染物存在下结论"], "pitfalls": ["看到污染物就直接判定污染", "忽略环境功能和受体影响"]},
    "g01": {"why": "农药题常把迁移、残留、抗性和安全间隔期组合考查，适合用风险链回答。", "master": ["解释农药在环境中的迁移、降解和残留", "能提出预测预报、对症用药、轮换和安全间隔措施"], "memorize": ["预测预报→精准选药/定量→轮换或合理混用→残留监测→安全间隔", "优先综合防治和低毒低残留方案"], "ask": ["农药残留风险控制", "农业污染综合防治"], "keywords": ["预测预报", "对症施药", "轮换", "抗性", "安全间隔", "残留"], "skeleton": ["先识别来源和迁移路径", "再写施用端、过程端和收获前控制", "补充残留监测与追溯", "最后说明生态和健康风险"], "pitfalls": ["只写减少用量，不写施药时机和替代方案", "把检测合格等同于全过程安全"]},
    "e01": {"why": "环境标准与基准是判断题、名词题和评价题的共同依据。", "master": ["区分标准、基准、限值和功能目标的作用", "能在不越界的前提下说明标准用于比较和管理"], "memorize": ["基准偏向科学风险依据，标准是管理要求；具体适用需核对现行文本", "评价结论必须写明对象、时段、指标和适用标准"], "ask": ["标准与基准概念辨析", "按标准判断环境质量"], "keywords": ["基准", "标准", "限值", "功能区", "适用范围", "核对版本"], "skeleton": ["先说明术语和适用对象", "再列评价指标与时空条件", "与现行适用标准比较", "给出有边界的结论"], "pitfalls": ["把基准和标准当同义词", "引用未经核验的具体限值"]},
    "w07": {"why": "A²/O 是脱氮除磷综合工艺的代表，常考分区功能、回流和碳源条件。", "master": ["说明厌氧—缺氧—好氧分区及其生物反应", "分析内回流、污泥回流、碳源和溶解氧对脱氮除磷的影响"], "memorize": ["厌氧释磷、缺氧反硝化、好氧硝化/吸磷的分区逻辑", "流程诊断要看回流方向、电子供体和泥龄"], "ask": ["A²/O 原理和流程", "脱氮除磷效果影响因素"], "keywords": ["厌氧", "缺氧", "好氧", "硝化", "反硝化", "释磷/吸磷"], "skeleton": ["先按分区写目标反应", "再说明回流和碳源如何连接各区", "分析氮磷去除的限制条件", "给出运行调节和污泥处置措施"], "pitfalls": ["混淆硝化与反硝化位置", "只写流程名称，不解释碳源和回流"]},
    "w01": {"why": "BOD/COD 等指标是水质判断和工艺选择的基础，常见于判断、选择和名词解释。", "master": ["说清各指标的含义、测定对象和互相区别", "能用指标关系判断有机物可生化性或处理需求"], "memorize": ["BOD 表示可生化有机物耗氧需求，COD 表示化学氧化所需氧量；二者不可简单互换", "pH 反映酸碱性，TOC/TOD 从碳或总耗氧角度表征有机污染"], "ask": ["指标定义与比较", "根据指标组合判断水质或工艺"], "keywords": ["可生化性", "化学氧化", "耗氧量", "有机碳", "酸碱性"], "skeleton": ["先定义指标测量对象", "再比较测定原理和适用场景", "联系 BOD/COD 比值或 pH 对处理的意义", "结论注明数据和条件"], "pitfalls": ["把 COD 全部等同于可生化有机物", "忽略测定方法和时间条件"]},
    "a02": {"why": "光化学烟雾的形成条件和前体控制是典型机制题，历史上有明确年份证据。", "master": ["识别 NOx、挥发性有机物和强日照等形成条件", "能从前体物控制和气象监测提出措施"], "memorize": ["前体物+强辐射+高温静稳等条件→二次氧化性污染", "控制重点是前体物减排、区域协同和预警监测"], "ask": ["形成机制与必要条件", "污染控制与气象条件分析"], "keywords": ["NOx", "VOCs", "光照", "静稳", "二次污染", "前体物"], "skeleton": ["先列前体物和气象条件", "再写光化学反应与污染物累积", "提出前体物源头控制", "补充区域传输和预警"], "pitfalls": ["只写臭氧，不写前体物和辐射条件", "把一次排放物和二次污染物混为一谈"]},
    "a05": {"why": "臭氧层与全球气候风险要求区分机制、尺度和治理对象，适合综合论述。", "master": ["区分臭氧层破坏与温室效应的物质、过程和影响", "能按全球协同、源头减排和适应思路组织答案"], "memorize": ["臭氧层问题关注平流层臭氧消耗；气候风险关注温室气体增暖及其生态影响", "答案需写机制—影响—控制/适应三段"], "ask": ["全球环境问题机制比较", "气候变化或臭氧层保护措施"], "keywords": ["平流层", "臭氧消耗", "温室气体", "辐射收支", "全球协同"], "skeleton": ["先界定问题与空间尺度", "分别写驱动机制和主要影响", "提出减排、替代和适应措施", "说明国际协同与长期监测"], "pitfalls": ["把臭氧层变薄和地面臭氧污染混淆", "只写口号，缺少机制和治理对象"]},
    "a01": {"why": "酸雨是大气污染事件的经典考点，常考前体物、形成过程和生态影响。", "master": ["解释 SO2/NOx 等前体物的转化和湿沉降", "能把排放控制与土壤、水体、植被影响联系起来"], "memorize": ["前体排放→大气氧化转化→酸性沉降→受体酸化和生态损伤", "治理重点是源头脱硫脱硝、能源结构和区域协同"], "ask": ["形成机制", "危害与防治"], "keywords": ["SO2", "NOx", "湿沉降", "酸化", "区域传输"], "skeleton": ["列前体物和气象传输", "说明氧化、成酸和沉降", "写受体影响", "提出源头、过程和区域控制"], "pitfalls": ["只写酸性降水，不写前体物转化", "忽略区域传输"]},
    "s03": {"why": "土壤修复题要求技术选择与场地条件匹配，不能只背技术名词。", "master": ["按土壤渗透性、污染物挥发/溶解性、深度和面积筛选技术", "能说明修复后安全利用与长期监测"], "memorize": ["调查—风险分区—技术筛选—施工控制—效果评估—安全利用", "源头切断与风险管控优先，修复技术需写适用边界"], "ask": ["修复技术比较", "污染场地安全利用方案"], "keywords": ["场地条件", "原位/异位", "稳定化", "地下水", "效果评估", "安全利用"], "skeleton": ["先描述污染物和场地", "按技术机理、优缺点、适用条件比较", "安排施工和二次污染控制", "以效果评估和后续监测收束"], "pitfalls": ["不看土壤性质直接选技术", "把修复达标等同于永久无风险"]},
}


def make_card(cid: str, name: str, rank: int | None, level: str, stats: dict[str, Any], refs: list[str], qids: list[str]) -> dict[str, Any]:
    card = CARDS.get(cid, {})
    detailed = level in {"core", "high"}
    return {
        "importance_level": level,
        "priority_rank": rank,
        "why_important": card.get("why", f"该单元属于课程知识树中的“{name}”，保留其真题索引以便按证据学习。") if detailed else "作为课程知识树中的基础单元，先完成定义和基本关系，再按题目证据补强。",
        "must_master": card.get("master", [f"说清{name}的定义、核心过程和适用边界。"] if detailed else []),
        "must_memorize": card.get("memorize", []),
        "high_frequency_approaches": card.get("ask", []) if detailed else [],
        "answer_keywords": card.get("keywords", []) if detailed else [],
        "answer_skeleton": card.get("skeleton", []) if detailed else [],
        "pitfalls": card.get("pitfalls", []) if detailed else [],
        "evidence_note": "统计来自 V2 题目—concept 关系；多标签题的原题分值不可跨单元求和。",
        "source_refs": refs,
        "question_ids": qids,
        "statistics": stats,
    }


def build() -> dict[str, Any]:
    concepts = read_json(ANALYSIS / "concepts-v2.json")
    rows = list(csv.DictReader((ANALYSIS / "exam-frequency-v2.csv").open(encoding="utf-8-sig", newline="")))
    row_by_id = {r["concept_id"]: r for r in rows}
    relations = read_jsonl(ANALYSIS / "question-concepts-v2.jsonl")
    questions = {q["question_id"]: q for q in read_jsonl(ANALYSIS / "questions.jsonl")}

    rel_by_concept: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for rel in relations:
        rel_by_concept[rel["concept_id"]].append(rel)

    units: list[dict[str, Any]] = []
    for concept in concepts:
        cid = concept["concept_id"]
        row = row_by_id.get(cid, {})
        qrels = rel_by_concept.get(cid, [])
        qids = sorted({r["question_id"] for r in qrels}, reverse=True)
        # Bridge nodes remain traceable but are intentionally not study cards.
        level = row.get("importance_level", "bridge" if concept.get("status") == "bridge" else "reference")
        rank = int(row["priority_rank"]) if row.get("priority_rank", "").isdigit() else None
        years = [int(y) for y in clean(row.get("exam_years")).split(",") if y.strip().isdigit()]
        stats = {
            "paper_count": int(row.get("paper_question_count") or 0),
            "subquestion_count": int(row.get("subquestion_count") or 0),
            "year_count": int(row.get("year_count") or 0),
            "recent_year_count": int(row.get("recent_year_count") or 0),
            "subjective_count": int(row.get("subjective_count") or 0),
            "comprehensive_count": int(row.get("comprehensive_count") or 0),
            "total_score": row.get("total_score") or "",
            "weighted_score": row.get("weighted_score") or "",
            "core_score": row.get("core_score") or "",
            "trend": row.get("trend") or "",
            "exam_years": years,
            "evidence_mix": row.get("evidence_mix", ""),
        }
        unit = {
            "learning_unit_id": f"lu-{cid}",
            "name": concept["name"],
            "module_id": concept["module_id"],
            "topic_id": concept["topic_id"],
            "concept_ids": [cid],
            "legacy_concept_ids": concept.get("legacy_concept_ids", []),
            "status": "bridge" if concept.get("status") == "bridge" else "active",
            "source_refs": concept.get("source_refs", []),
            "question_ids": qids,
            "question_count": len(qids),
            "question_types": sorted({clean(questions.get(qid, {}).get("question_type")) for qid in qids if questions.get(qid)}),
            "year_span": years,
            "content": make_card(cid, concept["name"], rank, level, stats, concept.get("source_refs", []), qids),
        }
        units.append(unit)

    modules: dict[str, dict[str, Any]] = {}
    for unit in units:
        m = modules.setdefault(unit["module_id"], {"module_id": unit["module_id"], "name": unit["module_id"], "units": []})
        m["units"].append(unit["learning_unit_id"])
    ranked = sorted([u for u in units if u["content"]["priority_rank"]], key=lambda u: u["content"]["priority_rank"])
    data = {
        "schema_version": "learning-content-1.0",
        "generated_from": ["真题/analysis/exam-frequency-v2.csv", "真题/analysis/question-concepts-v2.jsonl", "books/867-chushi-notes/"],
        "scope": {"canonical_questions": 136, "paper_questions": 131, "note": "统计继承 V2；多标签题分值不可跨单元相加。"},
        "modules": list(modules.values()),
        "learning_units": units,
        "core_top20": [u["learning_unit_id"] for u in ranked if u["content"]["priority_rank"] <= 20],
        "high_frequency_top50": [u["learning_unit_id"] for u in ranked if u["content"]["priority_rank"] <= 39],
    }
    return data


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    data = build()
    (OUT / "learning-units.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "required": ["schema_version", "learning_units", "core_top20"],
        "properties": {"schema_version": {"const": "learning-content-1.0"}, "learning_units": {"type": "array"}, "core_top20": {"type": "array", "maxItems": 20}},
    }
    (OUT / "learning-units.schema.json").write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")
    ranked = sorted([u for u in data["learning_units"] if u["content"]["priority_rank"]], key=lambda u: u["content"]["priority_rank"])
    study_entry = {"version": "1.0", "entry_flow": ["priority_rank", "learning_unit", "study-teach", "study-quiz", "study-feynman", "mastery"], "units": [{"learning_unit_id": u["learning_unit_id"], "priority_rank": u["content"]["priority_rank"], "name": u["name"], "question_ids": u["question_ids"], "mastery": 0, "next_actions": ["study-teach", "study-quiz", "study-feynman"]} for u in ranked]}
    (OUT / "study-assistant-entry.json").write_text(json.dumps(study_entry, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"built {len(data['learning_units'])} learning units; core/high ranked={len(ranked)}")


if __name__ == "__main__":
    main()
