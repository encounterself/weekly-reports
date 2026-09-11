"""Render publish/content models and five printable study PDFs.

The source of truth remains the existing V2 JSON/CSV/JSONL files. This module
only creates derived files under publish/ and leaves legacy outputs untouched.
"""
from __future__ import annotations

import html
import json
import os
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CONTENT = ROOT / "publish" / "content"
HTML = ROOT / "publish" / "html"
PDF = ROOT / "publish" / "pdf"
ANALYSIS = ROOT / "真题" / "analysis"
EDGE = Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")
if not EDGE.exists():
    EDGE = Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def repair_mojibake(value: Any) -> str:
    """Repair legacy GB18030-as-UTF8 display text without altering source data."""
    text = str(value or "")
    if not text:
        return ""
    try:
        candidate = text.encode("gb18030").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text
    # Only use the conversion when it looks like a real Chinese recovery.
    if any("\u4e00" <= ch <= "\u9fff" for ch in candidate) and sum("\ufffd" == ch for ch in candidate) <= sum("\ufffd" == ch for ch in text):
        return candidate
    return text


def esc(value: Any) -> str:
    return html.escape(repair_mojibake(value), quote=True)


def bullets(values: list[Any]) -> str:
    if not values:
        return "<p class='muted'>本单元暂不生成详细背诵卡，先完成定义和题目索引。</p>"
    return "<ul>" + "".join(f"<li>{esc(v)}</li>" for v in values) + "</ul>"


def badge(unit: dict[str, Any]) -> str:
    c = unit["content"]
    level = c.get("importance_level", "reference")
    rank = c.get("priority_rank")
    label = {"core": "核心必背", "high": "高频重点", "monitor": "重点理解", "reference": "一般掌握", "bridge": "桥接待复核"}.get(level, level)
    return f"<span class='badge {esc(level)}'>{esc(label)}{f' · Top {rank}' if rank else ''}</span>"


def stats_line(unit: dict[str, Any]) -> str:
    s = unit["content"]["statistics"]
    return (f"纸面题 {s['paper_count']} · 小问 {s['subquestion_count']} · 年份 {s['year_count']} · "
            f"近年 {s['recent_year_count']} · 主观题 {s['subjective_count']} · 综合题 {s['comprehensive_count']} · "
            f"趋势：{esc(s['trend'])}")


def unit_card(unit: dict[str, Any], compact: bool = False) -> str:
    c = unit["content"]
    if compact:
        return f"<section class='unit compact'><h3>{esc(unit['name'])} {badge(unit)}</h3><p>{stats_line(unit)}</p><p><b>背诵：</b>{esc('；'.join(c.get('must_memorize', [])[:2]))}</p></section>"
    return f"""
    <section class='unit'>
      <div class='unit-head'><h2>{esc(unit['name'])}</h2>{badge(unit)}</div>
      <p class='meta'>{stats_line(unit)}</p>
      <p class='note'>{esc(c.get('evidence_note'))}</p>
      <h3>为什么重要</h3><p>{esc(c.get('why_important'))}</p>
      <div class='grid'>
        <div><h3>必须掌握</h3>{bullets(c.get('must_master', []))}</div>
        <div><h3>必须背诵</h3>{bullets(c.get('must_memorize', []))}</div>
        <div><h3>高频考法</h3>{bullets(c.get('high_frequency_approaches', []))}</div>
        <div><h3>答题关键词</h3>{bullets(c.get('answer_keywords', []))}</div>
      </div>
      <h3>答题骨架</h3>{bullets(c.get('answer_skeleton', []))}
      <h3>易错点</h3>{bullets(c.get('pitfalls', []))}
      <p class='source'><b>证据：</b>{esc(c.get('evidence_mix', ''))}<br><b>来源：</b>{esc('; '.join(unit.get('source_refs', [])))}<br><b>题目：</b>{esc(', '.join(unit.get('question_ids', [])))}</p>
    </section>"""


CSS = """
@page { size: A4; margin: 16mm 15mm 17mm; }
* { box-sizing: border-box; }
body { font-family: "Microsoft YaHei", "Noto Sans CJK SC", Arial, sans-serif; color:#1d2939; line-height:1.55; font-size:10.5pt; margin:0; }
h1 { font-size:26pt; color:#123b5d; margin:0 0 8px; letter-spacing:0; }
h2 { font-size:17pt; color:#123b5d; margin:0 0 6px; letter-spacing:0; }
h3 { font-size:11.5pt; color:#1d5b78; margin:11px 0 4px; letter-spacing:0; }
p { margin:5px 0; } ul { margin:4px 0 8px 18px; padding:0; } li { margin:2px 0; }
.cover { min-height:250mm; display:flex; flex-direction:column; justify-content:center; border-left:8px solid #e07a3f; padding:20mm; background:#f6f8fa; page-break-after:always; }
.cover .kicker { color:#e07a3f; font-weight:700; font-size:12pt; } .cover .sub { color:#52606d; font-size:13pt; }
.toc li { margin:4px 0; }
.unit { border-top:2px solid #d9e2ec; padding:10px 0 12px; break-inside:avoid; }
.unit-head { display:flex; justify-content:space-between; align-items:flex-start; gap:8px; }
.unit-head h2 { flex:1; }
.compact { border:1px solid #d9e2ec; padding:8px 10px; margin:7px 0; border-radius:4px; }
.compact h3 { margin:0; display:flex; justify-content:space-between; gap:8px; }
.badge { display:inline-block; white-space:nowrap; border-radius:12px; padding:2px 8px; color:#fff; font-size:9pt; font-weight:700; background:#668; }
.badge.core { background:#c2413b; } .badge.high { background:#d97706; } .badge.monitor { background:#287c78; } .badge.reference { background:#6b7280; } .badge.bridge { background:#7c3aed; }
.meta { color:#52606d; font-size:9.5pt; } .note { background:#fff7ed; border-left:3px solid #f59e0b; padding:5px 8px; color:#7c4a03; }
.source { color:#52606d; font-size:8.5pt; border-top:1px dashed #cbd5e1; padding-top:5px; }
.grid { display:grid; grid-template-columns:1fr 1fr; gap:0 20px; } .page-break { page-break-before:always; }
.muted { color:#667085; font-style:italic; } .small { font-size:9pt; color:#52606d; }
table { border-collapse:collapse; width:100%; font-size:9pt; } th,td { border:1px solid #cbd5e1; padding:5px 6px; vertical-align:top; } th { background:#eef4f7; color:#123b5d; }
.q { padding:8px 0; border-bottom:1px solid #e5e7eb; break-inside:avoid; } .q .qid { color:#c2413b; font-weight:700; }
"""


def shell(title: str, body: str) -> str:
    return f"<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'><title>{esc(title)}</title><style>{CSS}</style></head><body>{body}</body></html>"


def add_page_numbers(path: Path) -> None:
    """Add a restrained page marker after browser PDF rendering."""
    try:
        import fitz
    except ImportError:
        return
    doc = fitz.open(path)
    total = len(doc)
    for index, page in enumerate(doc, 1):
        rect = page.rect
        page.insert_text((rect.width - 42, rect.height - 12), f"{index}/{total}", fontsize=8, color=(0.32, 0.38, 0.45), fontname="helv")
    tmp = path.with_suffix(".numbered.pdf")
    doc.save(tmp)
    doc.close()
    tmp.replace(path)


def question_text(q: dict[str, Any]) -> str:
    return repair_mojibake(q.get("question") or q.get("stem") or "（题干未提供）")


def build_models() -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    data = load_json(CONTENT / "learning-units.json")
    questions = {q["question_id"]: q for q in load_jsonl(ANALYSIS / "questions.jsonl")}
    relations = load_jsonl(ANALYSIS / "question-concepts-v2.jsonl")
    by_q: dict[str, list[str]] = defaultdict(list)
    for rel in relations:
        by_q[rel["question_id"]].append(rel["concept_id"])
    units = {u["learning_unit_id"]: u for u in data["learning_units"]}
    concepts_to_unit = {cid: uid for uid, u in units.items() for cid in u.get("concept_ids", [])}
    # Keep unit question lists traceable to the canonical question record.
    for u in units.values():
        u["questions"] = [{"question_id": qid, "year": questions.get(qid, {}).get("year"), "type": repair_mojibake(questions.get(qid, {}).get("question_type")), "text": question_text(questions[qid])} for qid in u["question_ids"] if qid in questions]
    module_names = {"foundation": "环境问题基础与污染过程", "water": "水环境与水处理", "air": "大气环境与污染控制", "soil_agriculture": "土壤、农业与生态", "governance": "固废、监测与环境管理"}
    topic_names = {"foundation-capacity": "环境容量、自净与污染判定", "foundation-process": "污染物迁移与暴露路径", "foundation-science": "环境科学与环境系统", "water-quality": "水质指标与水环境评价", "water-treatment": "污水处理工艺", "water-separation": "膜分离、吸附与离子交换", "water-nature": "人工湿地与自然处理", "water-ecology": "富营养化与水生态响应", "air-events": "大气污染事件与扩散", "air-control": "大气污染控制", "soil-risk": "土壤污染、形态与暴露", "soil-remediation": "土壤修复与安全利用", "agriculture-ecology": "农业污染、农药与生态循环", "governance-solid": "固体废物与清洁生产", "governance-monitoring": "监测、QA/QC 与环境评价", "governance-planning": "环评、标准与环境规划", "governance-policy": "环境制度与经济手段"}
    modules = []
    for mid in sorted({u["module_id"] for u in units.values()}):
        us = [u for u in units.values() if u["module_id"] == mid]
        topics = []
        for tid in sorted({u["topic_id"] for u in us}):
            ts = [u for u in us if u["topic_id"] == tid]
            topics.append({"topic_id": tid, "name": topic_names.get(tid, tid), "learning_units": [{"learning_unit_id": u["learning_unit_id"], "name": u["name"], "priority_rank": u["content"].get("priority_rank"), "importance_level": u["content"].get("importance_level"), "paper_count": u["content"]["statistics"]["paper_count"], "question_count": u["question_count"], "mastery": 0} for u in sorted(ts, key=lambda x: (x["content"].get("priority_rank") or 999, x["name"]))]})
        modules.append({"module_id": mid, "name": module_names.get(mid, mid), "topics": topics})
    map_model = {"schema_version": "knowledge-map-1.0", "title": "867 环境学考试驱动学习地图", "source": "publish/content/learning-units.json", "modules": modules}
    ranked = sorted(units.values(), key=lambda u: (u["content"].get("priority_rank") or 999, u["name"]))
    core = [u for u in ranked if u["content"].get("importance_level") in {"core", "high"}]
    core_model = {"schema_version": "core-handbook-1.0", "title": "核心背诵手册", "selection": "V2 priority_rank：核心 Top20 + 高频重点 Top50", "units": [{k: u[k] for k in ["learning_unit_id", "name", "module_id", "topic_id", "content"]} for u in core]}
    guide_model = {"schema_version": "exam-guide-1.0", "title": "历年真题考点册", "units": [{"learning_unit_id": u["learning_unit_id"], "name": u["name"], "statistics": u["content"]["statistics"], "evidence_mix": u["content"]["statistics"]["evidence_mix"], "question_ids": u["question_ids"], "questions": u["questions"]} for u in ranked]}
    practice_questions: list[dict[str, Any]] = []
    practice_seen: set[str] = set()
    practice_units: dict[str, list[str]] = defaultdict(list)
    for u in core:
        for q in u["questions"]:
            practice_units[q["question_id"]].append(u["learning_unit_id"])
            if q["question_id"] not in practice_seen:
                practice_seen.add(q["question_id"])
                practice_questions.append({**q, "learning_unit_ids": sorted(set(practice_units[q["question_id"]]))})
    # Fill all cross-unit links after the unique question list is known.
    for q in practice_questions:
        q["learning_unit_ids"] = sorted(set(practice_units[q["question_id"]]))
    practice_model = {"schema_version": "practice-book-1.0", "title": "真题训练册", "question_count": len(practice_questions), "unique_question_count": len(practice_questions), "questions": practice_questions, "sections": [{"learning_unit_id": u["learning_unit_id"], "name": u["name"], "question_ids": [q["question_id"] for q in u["questions"]]} for u in core if u["questions"]]}
    crash_model = {"schema_version": "crash-course-1.0", "title": "考前冲刺手册", "checklist": ["先背核心 Top20，再补高频重点", "每个单元用答题骨架写一次提纲", "训练册先做题目部分，再对照答案与证据等级", "多标签题分值不可跨单元求和", "不把趋势标签当成下一年预测"], "units": [{"learning_unit_id": u["learning_unit_id"], "name": u["name"], "rank": u["content"].get("priority_rank"), "importance_level": u["content"].get("importance_level"), "memorize": u["content"].get("must_memorize", []), "skeleton": u["content"].get("answer_skeleton", []), "pitfalls": u["content"].get("pitfalls", []), "questions": u["question_ids"]} for u in core]}
    return {"map": map_model, "core": core_model, "guide": guide_model, "practice": practice_model, "crash": crash_model}, units, questions


def render_books(models: dict[str, Any], units: dict[str, dict[str, Any]], questions: dict[str, dict[str, Any]]) -> dict[str, str]:
    ranked = sorted(units.values(), key=lambda u: (u["content"].get("priority_rank") or 999, u["name"]))
    top20_rows = "".join(f"<tr><td>Top {u['content']['priority_rank']}</td><td>{esc(u['name'])}</td><td>{badge(u)}</td><td>{esc(stats_line(u))}</td></tr>" for u in ranked if u["content"].get("priority_rank") and u["content"]["priority_rank"] <= 20)
    map_body = f"<div class='cover'><div class='kicker'>867 环境学 · 学习版 V2</div><h1>知识地图与重点</h1><p class='sub'>先看路线，再按 priority_rank 学习。统计继承 exam-analysis V2，不构成预测。</p><p class='small'>136 canonical questions · 131 paper questions · 40 concepts/learning units</p></div><div class='toc'><h2>使用顺序</h2><ol><li>先看 Top 20，建立模块—主题—学习单元全貌。</li><li>按排名进入核心背诵手册，用 study-teach / quiz / feynman 训练。</li><li>做历年考点和训练册，回到证据等级核对。</li></ol><h2>核心 Top 20</h2><table><tr><th>排名</th><th>学习单元</th><th>等级</th><th>证据摘要</th></tr>{top20_rows}</table></div>"
    map_body += "<div class='page-break'><h2>模块学习地图</h2>" + "".join(f"<h2>{esc(m['name'])}</h2>" + "".join(f"<h3>{esc(t['name'])}</h3>" + "".join(f"<p>• {esc(i['name'])} {badge(units[i['learning_unit_id']])} · 纸面题 {i['paper_count']} · 掌握度 {i['mastery']}%</p>" for i in t['learning_units']) for t in m['topics']) for m in models['map']['modules']) + "</div>"
    handbook = "<div class='cover'><div class='kicker'>日常背诵</div><h1>核心背诵手册</h1><p class='sub'>每个单元都带必须掌握、必须背诵、答题骨架和易错点。</p></div><div class='intro'><h2>使用说明</h2><p>核心 Top20 与高频重点按 V2 priority_rank 选取。题目证据以 paper/subquestion 分开；多标签题分值不可跨单元相加。</p></div>" + "".join(unit_card(u) for u in ranked if u["content"].get("importance_level") in {"core", "high"})
    guide = "<div class='cover'><div class='kicker'>按学习单元查真题</div><h1>历年真题考点册</h1><p class='sub'>先学知识，再按单元回看年份、题型和原题证据。</p></div>" + "".join(f"<section class='unit'><h2>{esc(u['name'])} {badge(u)}</h2><p class='meta'>{stats_line(u)}</p><p><b>证据混合：</b>{esc(u['content']['statistics']['evidence_mix'])}</p>" + "".join(f"<div class='q'><span class='qid'>{esc(q['question_id'])}</span> · {esc(q.get('year'))} · {esc(q.get('type'))}<br>{esc(q.get('text'))}</div>" for q in u['questions']) + "</section>" for u in ranked if u['questions'])
    practice_questions = []
    seen = set()
    linked_units: dict[str, list[str]] = defaultdict(list)
    for u in ranked:
        if u["content"].get("importance_level") not in {"core", "high"}:
            continue
        for q in u["questions"]:
            linked_units[q["question_id"]].append(u["name"])
            if q["question_id"] not in seen:
                seen.add(q["question_id"]); practice_questions.append((u, q))
    pqs = "".join(f"<div class='q'><span class='qid'>{esc(q['question_id'])}</span> · {esc(q.get('year'))} · {esc(q.get('type'))}<br>{esc(q.get('text'))}<p class='small'>关联学习单元：{esc('、'.join(dict.fromkeys(linked_units[q['question_id']])))} · 原题分值/答案请回看来源文件</p></div>" for u, q in practice_questions)
    answers = "".join(f"<div class='q'><span class='qid'>{esc(q['question_id'])}</span><br><b>核对：</b>题目来源 {esc(q.get('source', '真题/analysis/questions.jsonl'))}；本册保留题目与答案分离，答案请使用已有参考答案文件。</div>" for _, q in practice_questions)
    practice = "<div class='cover'><div class='kicker'>动手训练</div><h1>真题训练册</h1><p class='sub'>章节训练、高频重点训练与综合训练。题目和核对页分离。</p></div><h2>题目区</h2>" + pqs + "<div class='page-break'><h2>核对与复盘区</h2><p>本册不复制未经确认的答案。请按 question_id 回到仓库原始题目/参考答案核对；证据等级见历年真题考点册。</p>" + answers + "</div>"
    crash = "<div class='cover'><div class='kicker'>考前最后一轮</div><h1>考前冲刺手册</h1><p class='sub'>严格压缩成核心背诵、答题骨架、易错点和 Checklist。</p></div><h2>最后一日 Checklist</h2><ol>" + "".join(f"<li>{esc(x)}</li>" for x in models['crash']['checklist']) + "</ol>" + "".join(f"<section class='unit'><div class='unit-head'><h2>{esc(u['name'])}</h2>{badge(u)}</div><p class='small'>题目证据：{esc(', '.join(u['question_ids']))}</p><h3>必须背诵</h3>{bullets(u['content'].get('must_memorize', []))}<h3>答题骨架</h3>{bullets(u['content'].get('answer_skeleton', []))}<h3>易错点</h3>{bullets(u['content'].get('pitfalls', []))}</section>" for u in ranked if u["content"].get("importance_level") in {"core", "high"})
    return {"01_知识地图与重点": map_body, "02_核心背诵手册": handbook, "03_历年真题考点册": guide, "04_真题训练册": practice, "05_考前冲刺手册": crash}


def main() -> None:
    CONTENT.mkdir(parents=True, exist_ok=True); HTML.mkdir(parents=True, exist_ok=True); PDF.mkdir(parents=True, exist_ok=True)
    models, units, questions = build_models()
    filenames = {"map": "knowledge-map.json", "core": "core-handbook.json", "guide": "exam-guide.json", "practice": "practice-book.json", "crash": "crash-course.json"}
    for key, name in filenames.items():
        (CONTENT / name).write_text(json.dumps(models[key], ensure_ascii=False, indent=2), encoding="utf-8")
    pages = render_books(models, units, questions)
    for title, body in pages.items():
        hpath = HTML / f"{title}.html"; ppath = PDF / f"{title}.pdf"
        hpath.write_text(shell(title, body), encoding="utf-8")
        if EDGE.exists():
            subprocess.run([str(EDGE), "--headless", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={ppath}", hpath.as_uri()], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            add_page_numbers(ppath)
    print(f"models={len(filenames)}; html={len(pages)}; pdf={sum((PDF / (k + '.pdf')).exists() for k in pages)}")


if __name__ == "__main__":
    main()
