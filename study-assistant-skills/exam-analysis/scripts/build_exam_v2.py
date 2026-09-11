#!/usr/bin/env python3
"""Build the additive, fine-grained exam-analysis V2 artifacts.

The source of truth is the canonical questions.jsonl. historical_questions.jsonl
is deliberately used only for overlap/audit information, never added to counts.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

WEIGHTS = {
    "question_confirmed": 1.0,
    "topic_confirmed": 0.75,
    "answer_confirmed": 0.60,
    "inferred": 0.35,
}
SUBJECTIVE = {"名词解释", "辨析题", "简答题", "问答题", "论述题", "分析题", "分析论述题", "案例分析", "材料分析题", "综合题"}
COMPREHENSIVE = {"论述题", "分析题", "分析论述题", "案例分析", "材料分析题", "综合题"}

MODULES = [
    {"module_id": "foundation", "name": "环境问题基础与污染过程", "source_chapters": ["第一章 环境学绪论"]},
    {"module_id": "water", "name": "水环境与污水处理", "source_chapters": ["第二章 水污染及其防治"]},
    {"module_id": "air", "name": "大气与物理性污染", "source_chapters": ["第三章 大气污染及其防治", "第六章 物理性污染及其控制"]},
    {"module_id": "soil_agriculture", "name": "土壤、农业与生态", "source_chapters": ["第四章 土壤污染及其防治", "第七章 农业污染及其防治", "第八章 农产品安全与人体健康", "第九章 生态保护与生态建设"]},
    {"module_id": "governance", "name": "固废、监测与环境治理", "source_chapters": ["第五章 固体废物污染及其防治", "第十章 环境监测与评价", "第十一章 环境规划与管理", "第十二章 可持续发展"]},
]

TOPICS = [
    {"topic_id": "foundation-capacity", "module_id": "foundation", "name": "环境容量、自净与污染判定", "source_refs": ["books/867-chushi-notes/candidates/glossary.md#g03", "books/867-chushi-notes/candidates/glossary.md#g04"]},
    {"topic_id": "foundation-process", "module_id": "foundation", "name": "污染物迁移与暴露路径", "source_refs": ["books/867-chushi-notes/candidates/principles.md#p02"]},
    {"topic_id": "foundation-science", "module_id": "foundation", "name": "环境科学与环境系统", "source_refs": ["books/867-chushi-notes/BOOK_OVERVIEW.md#27"]},
    {"topic_id": "water-quality", "module_id": "water", "name": "水质指标与水环境评价", "source_refs": ["books/867-chushi-notes/candidates/glossary.md#g05", "books/867-chushi-notes/candidates/glossary.md#g06"]},
    {"topic_id": "water-treatment", "module_id": "water", "name": "污水处理工艺", "source_refs": ["books/867-chushi-notes/candidates/principles.md#p06", "books/867-chushi-notes/candidates/principles.md#p08"]},
    {"topic_id": "water-separation", "module_id": "water", "name": "膜分离、吸附与离子交换", "source_refs": ["books/867-chushi-notes/candidates/principles.md#p08"]},
    {"topic_id": "water-nature", "module_id": "water", "name": "人工湿地与自然处理", "source_refs": ["books/867-chushi-notes/candidates/principles.md#p06"]},
    {"topic_id": "water-ecology", "module_id": "water", "name": "富营养化与水生态响应", "source_refs": ["books/867-chushi-notes/candidates/principles.md#p05"]},
    {"topic_id": "air-events", "module_id": "air", "name": "大气污染事件与扩散", "source_refs": ["books/867-chushi-notes/candidates/principles.md#p09", "books/867-chushi-notes/candidates/principles.md#p10"]},
    {"topic_id": "air-control", "module_id": "air", "name": "大气污染控制与物理性污染", "source_refs": ["books/867-chushi-notes/candidates/principles.md#p15"]},
    {"topic_id": "soil-risk", "module_id": "soil_agriculture", "name": "土壤污染、形态与暴露", "source_refs": ["books/867-chushi-notes/candidates/principles.md#p11", "books/867-chushi-notes/candidates/principles.md#p12"]},
    {"topic_id": "soil-remediation", "module_id": "soil_agriculture", "name": "土壤修复与安全利用", "source_refs": ["books/867-chushi-notes/candidates/principles.md#p03", "books/867-chushi-notes/candidates/principles.md#p11"]},
    {"topic_id": "agriculture-ecology", "module_id": "soil_agriculture", "name": "农业污染、农药与生态循环", "source_refs": ["books/867-chushi-notes/candidates/principles.md#p16", "books/867-chushi-notes/candidates/principles.md#p17", "books/867-chushi-notes/candidates/principles.md#p20"]},
    {"topic_id": "governance-solid", "module_id": "governance", "name": "固体废物与清洁生产", "source_refs": ["books/867-chushi-notes/candidates/principles.md#p13", "books/867-chushi-notes/candidates/principles.md#p14", "books/867-chushi-notes/candidates/principles.md#p25"]},
    {"topic_id": "governance-monitoring", "module_id": "governance", "name": "监测、QA/QC 与环境评价", "source_refs": ["books/867-chushi-notes/candidates/principles.md#p21", "books/867-chushi-notes/candidates/principles.md#p22"]},
    {"topic_id": "governance-planning", "module_id": "governance", "name": "环评、标准与环境规划", "source_refs": ["books/867-chushi-notes/candidates/principles.md#p23", "books/867-chushi-notes/candidates/principles.md#p24"]},
    {"topic_id": "governance-policy", "module_id": "governance", "name": "环境制度与经济手段", "source_refs": ["books/867-chushi-notes/candidates/glossary.md#201"]},
]

CONCEPTS = [
    ("f01", "环境容量", "foundation-capacity", ["v01"], "books/867-chushi-notes/candidates/glossary.md#g03"),
    ("f02", "环境自净", "foundation-capacity", ["v01"], "books/867-chushi-notes/candidates/glossary.md#g04"),
    ("f03", "环境污染判定", "foundation-capacity", ["v01"], "books/867-chushi-notes/candidates/glossary.md#g02"),
    ("f04", "污染物迁移与暴露路径", "foundation-process", ["v02"], "books/867-chushi-notes/candidates/principles.md#p02"),
    ("f05", "环境科学与环境系统", "foundation-science", ["v01", "v10"], "books/867-chushi-notes/BOOK_OVERVIEW.md#27"),
    ("w01", "水质指标（BOD/COD/TOC/TOD/pH）", "water-quality", ["v01", "v02", "v03"], "books/867-chushi-notes/candidates/glossary.md#g05"),
    ("w02", "活性污泥法", "water-treatment", ["v02"], "books/867-chushi-notes/candidates/principles.md#p06"),
    ("w03", "生物膜法", "water-treatment", ["v02"], "books/867-chushi-notes/candidates/principles.md#p08"),
    ("w04", "厌氧与 UASB 生物处理", "water-treatment", ["v02"], "books/867-chushi-notes/candidates/principles.md#p06"),
    ("w05", "沉淀", "water-treatment", ["v02"], "books/867-chushi-notes/candidates/principles.md#p08"),
    ("w06", "混凝", "water-treatment", ["v02"], "books/867-chushi-notes/candidates/principles.md#p08"),
    ("w07", "A²/O 与生物脱氮除磷", "water-treatment", ["v02", "v03"], "books/867-chushi-notes/candidates/principles.md#p06"),
    ("w09", "膜分离与反渗透", "water-separation", ["v02"], "books/867-chushi-notes/candidates/principles.md#p08"),
    ("w10", "人工湿地与自然处理", "water-nature", ["v02"], "books/867-chushi-notes/candidates/principles.md#p06"),
    ("w11", "吸附与离子交换", "water-separation", ["v02"], "books/867-chushi-notes/candidates/glossary.md#g03"),
    ("w08", "富营养化与氮磷负荷", "water-ecology", ["v03"], "books/867-chushi-notes/candidates/principles.md#p05"),
    ("a01", "酸雨", "air-events", ["v04"], "books/867-chushi-notes/candidates/principles.md#p09"),
    ("a02", "光化学烟雾", "air-events", ["v04"], "books/867-chushi-notes/candidates/principles.md#p10"),
    ("a03", "大气扩散与气象条件", "air-events", ["v04"], "books/867-chushi-notes/candidates/principles.md#p09"),
    ("a04", "烟气脱硫与除尘", "air-control", ["v04"], "books/867-chushi-notes/candidates/principles.md#p09"),
    ("a05", "臭氧层与全球气候风险", "air-events", ["v04", "v10"], "books/867-chushi-notes/BOOK_OVERVIEW.md#27"),
    ("a06", "噪声污染", "air-control", ["v04"], "books/867-chushi-notes/candidates/principles.md#p15"),
    ("s01", "土壤重金属形态与迁移", "soil-risk", ["v02", "v05"], "books/867-chushi-notes/candidates/principles.md#p12"),
    ("s02", "土壤背景值", "soil-risk", ["v01", "v05"], "books/867-chushi-notes/candidates/glossary.md#g03"),
    ("s03", "土壤污染修复与安全利用", "soil-remediation", ["v05"], "books/867-chushi-notes/candidates/principles.md#p11"),
    ("s04", "生物有效性与食物链风险", "soil-risk", ["v05", "v07", "v08"], "books/867-chushi-notes/candidates/principles.md#p12"),
    ("g01", "农药迁移、残留与风险控制", "agriculture-ecology", ["v02", "v07"], "books/867-chushi-notes/candidates/principles.md#p16"),
    ("g02", "农业污染与畜禽粪污消纳", "agriculture-ecology", ["v08"], "books/867-chushi-notes/candidates/principles.md#p17"),
    ("g03", "生态农业、循环与生物多样性", "agriculture-ecology", ["v07", "v08"], "books/867-chushi-notes/candidates/principles.md#p20"),
    ("r01", "危险固体废物鉴别", "governance-solid", ["v06"], "books/867-chushi-notes/candidates/principles.md#p14"),
    ("r02", "固废焚烧、填埋与渗滤液", "governance-solid", ["v06"], "books/867-chushi-notes/candidates/principles.md#p13"),
    ("r03", "清洁生产、源头减量与 3R", "governance-solid", ["v06"], "books/867-chushi-notes/candidates/principles.md#p13"),
    ("m01", "环境监测设计与采样", "governance-monitoring", ["v09"], "books/867-chushi-notes/candidates/principles.md#p21"),
    ("m02", "监测 QA/QC 与有效数据", "governance-monitoring", ["v09"], "books/867-chushi-notes/candidates/principles.md#p22"),
    ("m03", "环境质量评价与监测指标", "governance-monitoring", ["v09", "v10"], "books/867-chushi-notes/candidates/principles.md#p21"),
    ("e01", "环境标准与基准", "governance-planning", ["v09", "v10"], "books/867-chushi-notes/candidates/glossary.md#g03"),
    ("e02", "环境影响评价", "governance-planning", ["v10"], "books/867-chushi-notes/candidates/principles.md#p23"),
    ("e03", "环境规划与方案决策", "governance-planning", ["v10"], "books/867-chushi-notes/candidates/principles.md#p24"),
    ("e04", "环境保护制度与经济手段", "governance-policy", ["v10"], "books/867-chushi-notes/candidates/glossary.md#201"),
    ("x01", "跨介质迁移兼容桥接（待细分）", "foundation-process", ["v02", "v05", "v09", "v10"], "books/867-chushi-notes/candidates/principles.md#p02"),
]

CONCEPT_BY_ID = {row[0]: row for row in CONCEPTS}
CONCEPTS_BY_LEGACY = defaultdict(list)
for cid, _, _, legacy, _ in CONCEPTS:
    for old in legacy:
        CONCEPTS_BY_LEGACY[old].append(cid)

LEGACY_DEFAULT = {
    "v01": "f03",
    "v02": None,
    "v03": "w08",
    "v04": "a03",
    "v05": None,
    "v06": "r03",
    "v07": "g01",
    "v08": "g03",
    "v09": None,
    "v10": None,
}

KEYWORDS = [
    ("w07", ["A2/O", "A²/O", "脱氮除磷", "生物脱氮"]),
    ("w03", ["生物膜", "附着生长"]),
    ("w02", ["活性污泥", "污泥龄", "MLSS", "曝气池", "氧化沟"]),
    ("w04", ["UASB", "厌氧", "好氧与厌氧"]),
    ("w09", ["反渗透", "膜分离"]),
    ("w10", ["人工湿地"]),
    ("w11", ["离子交换", "吸附过程"]),
    ("w05", ["沉淀", "表面负荷"]),
    ("w06", ["混凝"]),
    ("w01", ["COD", "BOD", "TOC", "TOD", "pH", "耗氧量", "水质指标"]),
    ("w08", ["富营养化", "氮磷", "营养盐", "水华"]),
    ("a02", ["光化学", "洛杉矶型"]),
    ("a01", ["酸雨", "伦敦型"]),
    ("a04", ["脱硫", "除尘", "粉尘", "烟气"]),
    ("a06", ["噪声", "热岛"]),
    ("a05", ["臭氧洞", "臭氧层", "温室", "全球变暖", "冰盖", "海平面"]),
    ("a03", ["扩散", "气象", "逆温", "风速", "污染事件"]),
    ("s03", ["修复", "安全利用", "土壤气相", "电动力学", "生物修复"]),
    ("s02", ["背景值"]),
    ("s04", ["食物链", "生物多样性", "农产品", "健康", "作物品质"]),
    ("s01", ["重金属", "镉", "砷", "形态", "迁移转化", "络合"]),
    ("g01", ["农药", "残留", "抗药性", "天敌"]),
    ("g02", ["畜禽", "粪污", "养殖污染", "消纳"]),
    ("g03", ["生态农业", "有机农业", "生态平衡", "种养", "循环农业"]),
    ("r01", ["危险废物", "危险固体", "鉴别"]),
    ("r02", ["焚烧", "填埋", "渗滤液", "二噁英", "垃圾"]),
    ("r03", ["清洁生产", "源头减量", "循环经济", "3R", "绿色贸易", "重复利用", "中水回用"]),
    ("m02", ["质量控制", "质量保证", "QA/QC", "有效数据", "平行样", "加标"]),
    ("m01", ["采样", "布点", "监测方案", "监测程序", "监测基本原则"]),
    ("m03", ["环境监测", "生物监测", "环境质量评价", "评价结果"]),
    ("e01", ["环境标准", "环境基准", "标准体系", "标准关系"]),
    ("e02", ["环境影响评价", "环评", "工程分析"]),
    ("e03", ["环境规划", "方案", "厂址", "削减量", "区域建设项目", "规划"]),
    ("e04", ["基本制度", "排污收费", "收费制度", "经济手段"]),
    ("f05", ["环境科学形成", "学科关系", "环境科学"]),
    ("f01", ["环境容量", "纳污能力"]),
    ("f02", ["自净", "净化机制"]),
    ("f03", ["环境污染", "污染判定", "原生环境"]),
    ("f04", ["迁移", "暴露路径", "污染物过程"]),
]

# Manual alignment for high-impact or historically broad records. These are
# mappings, not new question text; their evidence level still comes from the
# source record and remains visible in evidence-v2.jsonl.
MANUAL_MAP = {
    "2025-S-02": ["s04"],
    "2025-S-04": ["x01"],
    "2025-SA-02": ["g03"],
    "2025-CA-01-1": ["w02"],
    "2025-CA-01-2": ["m03", "e01"],
    "2025-CA-02-1": ["s01", "s04"],
    "2025-CA-02-2": ["m01", "m03"],
    "2025-CA-02-3": ["s03", "m03"],
    "2013-N-03": ["w02"],
    "2014-N-01": ["f04"],
    "2014-N-03": ["w04"],
    "2014-N-04": ["w09"],
    "2015-CA-01": ["x01"],
    "2016-N-01": ["a06", "f04"],
    "2017-SA-01": ["r03"],
    "2017-N-03": ["e04"],
    "2018-L-01": ["x01"],
    "2020-CA-01": ["x01"],
    "2020-L-01": ["f05"],
    "2021-SA-04": ["w10"],
    "2021-L-01": ["x01"],
    "2023-S-01": ["x01"],
    "2024-S-01": ["s01"],
    "2024-S-02": ["s01"],
    "2024-S-04": ["w11"],
    "2024-CA-01-1": ["s01"],
    "2024-CA-01-2": ["s01", "m03"],
}

def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#")]

def evidence_level(q):
    value = q.get("question_fidelity")
    if value == "question-confirmed": return "question_confirmed"
    if value == "topic-confirmed": return "topic_confirmed"
    if value == "answer-confirmed": return "answer_confirmed"
    if q.get("year") == 2025 and q.get("status") == "confirmed": return "question_confirmed"
    return "inferred"

def map_concepts(q):
    if q.get("question_id") in MANUAL_MAP:
        return MANUAL_MAP[q["question_id"]]
    text = q.get("question", "")
    ids = []
    for cid, words in KEYWORDS:
        if any(word in text for word in words) and cid not in ids:
            ids.append(cid)
    if not ids:
        for old in q.get("concept_ids", []):
            fallback = LEGACY_DEFAULT.get(old)
            if fallback and fallback not in ids:
                ids.append(fallback)
    return ids or ["x01"]

def trend(years):
    ys = sorted(set(years))
    recent = [y for y in ys if y >= 2021]
    if len(ys) <= 2: return "偶发"
    if not recent: return "多年未考"
    if len(ys) >= 6 and len(recent) >= 3: return "长期稳定高频"
    if len(ys) >= 6 and len(recent) < len(ys) / 2: return "长期稳定但近期下降"
    if len(recent) >= 3 and len(recent) >= len([y for y in ys if y <= 2020]): return "近年升温"
    gaps = [b - a for a, b in zip(ys, ys[1:])]
    if any(g >= 2 for g in gaps): return "周期性"
    return "偶发"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", default="真题/analysis/questions.jsonl")
    ap.add_argument("--historical", default="真题/analysis/historical_questions.jsonl")
    ap.add_argument("--out", default="真题/analysis")
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    questions = load_jsonl(Path(args.questions))
    historical = load_jsonl(Path(args.historical)) if Path(args.historical).exists() else []
    by_id = {q["question_id"]: q for q in questions}
    relations, evidence = [], []
    for q in questions:
        level = evidence_level(q); weight = WEIGHTS[level]
        paper_id = q.get("parent_question_id") or q["question_id"]
        is_sub = bool(q.get("parent_question_id"))
        evidence.append({"question_id": q["question_id"], "paper_question_id": paper_id, "evidence_level": level, "evidence_weight": weight, "question_fidelity": q.get("question_fidelity"), "status": q.get("status", "confirmed"), "source": q.get("source"), "note": "题干/主题/答案证据等级由现有字段转换；未标注记录按 inferred 处理" if level == "inferred" else ""})
        mapped = map_concepts(q)
        manual = q.get("question_id") in MANUAL_MAP
        keyword_ids = {cid for cid, words in KEYWORDS if any(word in q.get("question", "") for word in words)}
        for cid in mapped:
            row = CONCEPT_BY_ID[cid]
            relations.append({"question_id": q["question_id"], "paper_question_id": paper_id, "is_subquestion": is_sub, "year": q["year"], "concept_id": cid, "topic_id": row[2], "module_id": next(x["module_id"] for x in TOPICS if x["topic_id"] == row[2]), "legacy_concept_ids": q.get("concept_ids", []), "mapping_method": "manual" if manual else ("keyword" if cid in keyword_ids else ("legacy_bridge" if cid == "x01" else "legacy_default")), "evidence_level": level, "evidence_weight": weight, "source": q.get("source")})
    def dump_jsonl(path, rows):
        path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
    dump_jsonl(out / "question-concepts-v2.jsonl", relations)
    dump_jsonl(out / "evidence-v2.jsonl", evidence)
    tree = {"schema_version": "2.0", "legacy_compatibility": {"source": "concepts.json", "ids": [f"v{i:02d}" for i in range(1, 11)]}, "modules": []}
    for module in MODULES:
        m = dict(module); m["topic_ids"] = [t["topic_id"] for t in TOPICS if t["module_id"] == module["module_id"]]; m["topics"] = []
        for topic in [t for t in TOPICS if t["module_id"] == module["module_id"]]:
            t = dict(topic); t["concept_ids"] = [c[0] for c in CONCEPTS if c[2] == topic["topic_id"]]; t["concepts"] = []
            for cid, name, _, legacy, source in [c for c in CONCEPTS if c[2] == topic["topic_id"]]:
                t["concepts"].append({"concept_id": cid, "name": name, "legacy_concept_ids": legacy, "source_refs": [source], "status": "bridge" if cid == "x01" else "active"})
            m["topics"].append(t)
        tree["modules"].append(m)
    (out / "course-tree-v2.json").write_text(json.dumps(tree, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "topics-v2.json").write_text(json.dumps([{k: v for k, v in t.items()} for t in TOPICS], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "concepts-v2.json").write_text(json.dumps([{ "concept_id": cid, "name": name, "topic_id": topic, "module_id": next(t["module_id"] for t in TOPICS if t["topic_id"] == topic), "legacy_concept_ids": legacy, "source_refs": [source], "status": "bridge" if cid == "x01" else "active"} for cid, name, topic, legacy, source in CONCEPTS], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    legacy_map = []
    for old in [f"v{i:02d}" for i in range(1, 11)]:
        children = [{"concept_id": cid, "name": name, "status": "bridge" if cid == "x01" else "active"} for cid, name, _, legacy, _ in CONCEPTS if old in legacy]
        legacy_map.append({"legacy_concept_id": old, "legacy_source": "真题/analysis/concepts.json", "v2_concept_ids": [c["concept_id"] for c in children], "children": children, "compatibility_note": "旧节点保留用于回溯；V2 统计使用其细粒度子节点。"})
    (out / "legacy-compatibility-v2.json").write_text(json.dumps(legacy_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    grouped = defaultdict(list)
    seen_relations = set()
    for rel in relations:
        key = (rel["question_id"], rel["concept_id"])
        if key not in seen_relations:
            grouped[rel["concept_id"]].append(rel)
            seen_relations.add(key)
    rows = []
    for cid, name, topic, legacy, source in CONCEPTS:
        rs = grouped[cid]; papers = {r["paper_question_id"] for r in rs}; subs = [r for r in rs if r["is_subquestion"]]; years = {r["year"] for r in rs}; recent_years = {y for y in years if y >= 2021}
        qids = [r["question_id"] for r in rs]; weighted_papers = sum(max(r["evidence_weight"] for r in rs if r["paper_question_id"] == p) for p in papers)
        weighted_subs = sum(r["evidence_weight"] for r in subs); weighted_years = sum(max(r["evidence_weight"] for r in rs if r["year"] == y) for y in years); weighted_recent = sum(max(r["evidence_weight"] for r in rs if r["year"] == y) for y in recent_years)
        qrows = [by_id[r["question_id"]] for r in rs]; subjective = sum(q.get("question_type") in SUBJECTIVE for q in qrows); comprehensive = sum(q.get("question_type") in COMPREHENSIVE for q in qrows); scores = sum(q.get("score") or 0 for q in qrows)
        core = 4 * weighted_papers + 1.5 * weighted_subs + 1.5 * weighted_years + weighted_recent + .25 * subjective + .5 * comprehensive + .02 * scores
        mix = "; ".join(f"{k}={sum(r['evidence_level']==k for r in rs)}" for k in WEIGHTS if any(r['evidence_level']==k for r in rs)) or "none"
        rows.append({"concept_id": cid, "topic_id": topic, "module_id": next(t["module_id"] for t in TOPICS if t["topic_id"] == topic), "concept": name, "paper_question_count": len(papers), "subquestion_count": len(subs), "question_assignment_count": len(rs), "year_count": len(years), "recent_year_count": len(recent_years), "exam_years": ",".join(map(str, sorted(years))), "recent_years": ",".join(map(str, sorted(recent_years))), "subjective_count": subjective, "comprehensive_count": comprehensive, "total_score": scores or "", "weighted_score": round(sum((q.get("score") or 0) * r["evidence_weight"] for q, r in zip(qrows, rs)), 2), "weighted_paper_count": round(weighted_papers, 2), "weighted_subquestion_count": round(weighted_subs, 2), "weighted_year_count": round(weighted_years, 2), "weighted_recent_year_count": round(weighted_recent, 2), "core_score": round(core, 3), "priority_rank": 0, "importance_level": "bridge" if cid == "x01" else "reference", "trend": trend(years), "evidence_mix": mix, "question_ids": ",".join(qids)})
    rows.sort(key=lambda x: (x["concept_id"] == "x01", -x["core_score"], x["concept_id"]))
    ranked_rows = [row for row in rows if row["concept_id"] != "x01"]
    for i, row in enumerate(ranked_rows, 1):
        row["priority_rank"] = i
        if i <= 10: row["importance_level"] = "core"
        elif i <= 20: row["importance_level"] = "high"
        elif i <= 30: row["importance_level"] = "monitor"
        else: row["importance_level"] = "reference"
    bridge = next((row for row in rows if row["concept_id"] == "x01"), None)
    if bridge:
        bridge["priority_rank"] = ""
        bridge["importance_level"] = "bridge"
    fields = list(rows[0])
    with (out / "exam-frequency-v2.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    level_counts = Counter(r["evidence_level"] for r in relations)
    stats = {
        "schema_version": "2.0",
        "canonical_question_count": len(questions),
        "paper_question_count": len({q.get("parent_question_id") or q["question_id"] for q in questions}),
        "subquestion_record_count": sum(bool(q.get("parent_question_id")) for q in questions),
        "relation_count": len(relations),
        "relation_subquestion_count": sum(bool(r["is_subquestion"]) for r in relations),
        "evidence_level_relation_count": dict(level_counts),
        "legacy_question_count": len(historical),
        "active_concept_count": sum(c["status"] == "active" for c in [{"status": "bridge" if cid == "x01" else "active"} for cid, *_ in CONCEPTS]),
        "bridge_concept_count": sum(cid == "x01" for cid, *_ in CONCEPTS),
        "evidence_weights": WEIGHTS,
        "source_files": {"questions": str(args.questions), "historical": str(args.historical)},
    }
    (out / "exam-stats-v2.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    row_by_id = {r["concept_id"]: r for r in rows}
    lines = ["# 考试主题分析 V2", "", "> V2 使用细粒度 concept；paper question 与 subquestion 分开统计。证据权重仅用于排序，不把推断伪装成原题确认。", "", "| 排名 | module | topic | concept | paper | subquestion | years | subjective | comprehensive | weighted score | trend | evidence |", "|---:|---|---|---|---:|---:|---:|---:|---:|---:|---|---|"]
    for r in rows: lines.append(f"| {r['priority_rank']} | {r['module_id']} | {r['topic_id']} | {r['concept']} | {r['paper_question_count']} | {r['subquestion_count']} | {r['year_count']} | {r['subjective_count']} | {r['comprehensive_count']} | {r['core_score']} | {r['trend']} | {r['evidence_mix']} |")
    (out / "exam-topic-analysis-v2.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    trend_lines = ["# 真题趋势 V2", "", "> 趋势只由实际出现年份按 Schema 规则计算，不对缺失年份插值，也不预测下一年。", "", "## 标签规则", "", "`长期稳定高频`、`长期稳定但近期下降`、`近年升温`、`周期性`、`多年未考`、`偶发`。", "", "## 主题趋势", "", "| concept | years | recent years | label |", "|---|---|---|---|"]
    for r in rows: trend_lines.append(f"| {r['concept']} | {r['exam_years'] or '-'} | {r['recent_years'] or '-'} | {r['trend']} |")
    (out / "exam-trends-v2.md").write_text("\n".join(trend_lines) + "\n", encoding="utf-8")
    priority = ["# 核心考查单元 V2", "", "> 这是按 `core_score` 排名的 Top 20，不是五星预测；`bridge` 节点只用于追踪尚未细分的旧归因。", ""]
    for r in ranked_rows[:20]: priority += [f"## Top {r['priority_rank']}：{r['concept']}", f"- module/topic：`{r['module_id']}` / `{r['topic_id']}`", f"- core_score：`{r['core_score']}`；importance_level：`{r['importance_level']}`；trend：{r['trend']}", f"- paper questions：{r['paper_question_count']}；subquestions：{r['subquestion_count']}；years：{r['year_count']}；recent years：{r['recent_year_count']}", f"- subjective：{r['subjective_count']}；comprehensive：{r['comprehensive_count']}；known score：{r['total_score'] or '未完整核对'}", f"- evidence：{r['evidence_mix']}", ""]
    (out / "priority-summary-v2.md").write_text("\n".join(priority), encoding="utf-8")
    must = ["# 细粒度背诵清单 V2", "", "> 仅列 Top 10 core concepts；这表示数据优先级，不表示今年必考。", ""]
    for r in ranked_rows[:10]: must += [f"## {r['concept']}", f"- Top {r['priority_rank']}；core_score {r['core_score']}；paper {r['paper_question_count']}；subquestion {r['subquestion_count']}；years {r['year_count']}。", f"- 证据混合：{r['evidence_mix']}；趋势：{r['trend']}。", ""]
    (out / "must-memorize-v2.md").write_text("\n".join(must), encoding="utf-8")
    index = ["# concept—真题索引 V2", "", "> 每个 concept 下列出题目关系，保留 paper question ID 以识别综合题父子关系。", ""]
    for r in rows:
        index += [f"## {r['concept']} (`{r['concept_id']}`) — Top {r['priority_rank']}", ""]
        for rel in grouped[r["concept_id"]]:
            q = by_id[rel["question_id"]]; marker = "subquestion" if rel["is_subquestion"] else "paper question"; index.append(f"- `{q['question_id']}` ({marker}; paper `{rel['paper_question_id']}`; {rel['evidence_level']})：{q.get('question','')}")
        if not grouped[r["concept_id"]]: index.append("- 暂无映射题目")
        index.append("")
    (out / "concept-question-index-v2.md").write_text("\n".join(index), encoding="utf-8")
    src = ["# 真题来源清单 V2", "", f"- canonical questions：`{len(questions)}` 条，作为 V2 唯一统计入口。", f"- historical_questions：`{len(historical)}` 条，仅用于旧版重叠/来源审计，不重复计数。", f"- canonical 与 historical 重叠 ID：`{len(set(by_id) & {q['question_id'] for q in historical})}`。", "", "## 证据转换", "", "`question-confirmed` → `question_confirmed`；`topic-confirmed` → `topic_confirmed`；`answer-confirmed` → `answer_confirmed`；缺少 fidelity 的非 2025 记录 → `inferred`。2025 来自题目材料且 status confirmed 的记录按 `question_confirmed` 处理；2025 `needs_review` 记录仍为 `inferred`。", "", "## 统计边界", "", "paper_question_count 按 `parent_question_id` 折叠；subquestion_count 单独列出。多 concept 题在关系层保留多标签，但不把一条纸面题重复算成多个 paper question。", "", "## 旧 ID 兼容", "", "`legacy-compatibility-v2.json` 显式列出 `v01`—`v10` 到 V2 concept 的一对多映射；旧版文件不被覆盖。"]
    (out / "source-inventory-v2.md").write_text("\n".join(src) + "\n", encoding="utf-8")
    audit = ["# Top 20 V2 规则审查", "", "> 自动审查结果；需要人工回看原 PDF/DOCX 的关系会明确列出。", "", f"- canonical records：{len(questions)}；relations：{len(relations)}；active concepts：{len(CONCEPTS)-1}；bridge concepts：1。", f"- paper questions（按 parent 折叠）：{len({r['paper_question_id'] for r in relations})}（关系层全局）。", f"- subquestions：{sum(r['is_subquestion'] for r in relations)} 条关系；原始子问记录：{sum(bool(q.get('parent_question_id')) for q in questions)}。", "", "## Top 20", "", "| rank | concept | paper | subquestion | years | score | bridge |", "|---:|---|---:|---:|---:|---:|---|"]
    for r in ranked_rows[:20]: audit.append(f"| {r['priority_rank']} | {r['concept']} | {r['paper_question_count']} | {r['subquestion_count']} | {r['year_count']} | {r['total_score'] or '-'} | no |")
    audit += ["", "## 需要人工复核", "", "- `x01` 兼容桥接节点的 7 条关系必须逐题回看原 PDF/DOCX 后再细分；它不进入 Top 20。", "- 2025 `S-01`、`S-03` 的原始题干已有 `needs_review`，其关系保留为 `inferred`，不应当写成题干确认。", "- 多 concept 题的分值仍按原题记录复制到各关联 concept；若需要 concept-level 分值分摊，应在人工复核后增加 allocation 字段，不在 V2 自动猜测。", "", "## v02/v05/v09/v10 对齐记录", "", "| question_id | legacy | V2 concept(s) | method |", "|---|---|---|---|"]
    for q in questions:
        old = set(q.get("concept_ids", [])) & {"v02", "v05", "v09", "v10"}
        if old:
            mapped = map_concepts(q)
            audit.append(f"| `{q['question_id']}` | {','.join(sorted(old))} | {','.join(mapped)} | {'manual' if q['question_id'] in MANUAL_MAP else 'keyword/default'} |")
    (out / "top20-audit-v2.md").write_text("\n".join(audit) + "\n", encoding="utf-8")
    print(f"questions={len(questions)} relations={len(relations)} concepts={len(CONCEPTS)} output={out}")

if __name__ == "__main__":
    main()
