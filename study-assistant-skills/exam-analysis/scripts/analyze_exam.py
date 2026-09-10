#!/usr/bin/env python3
"""Generate explainable exam-weight reports from reviewed JSONL questions.

The script deliberately does not infer concepts from raw OCR. Concept mapping is
an explicit, reviewable field on each question record.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import pathlib
from collections import Counter, defaultdict


STAR_LABELS = {
    5: "核心必背",
    4: "高频重点",
    3: "重点理解",
    2: "一般掌握",
    1: "低优先级",
}


def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: pathlib.Path):
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{line_no}: invalid JSON: {exc}")
    return rows


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def streak(years):
    years = sorted(set(years), reverse=True)
    if not years:
        return 0
    count = 1
    for current, previous in zip(years, years[1:]):
        if current - previous == 1:
            count += 1
        else:
            break
    return count


def classify(score, year_count):
    if year_count == 0:
        return 1
    if year_count == 1:
        return min(3, max(1, int(math.ceil(score / 20))))
    if score >= 80:
        return 5
    if score >= 62:
        return 4
    if score >= 44:
        return 3
    if score >= 25:
        return 2
    return 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--concepts", required=True)
    parser.add_argument("--questions", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    out_dir = pathlib.Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    concepts = load_json(pathlib.Path(args.concepts))
    questions = load_jsonl(pathlib.Path(args.questions))
    concept_by_id = {item["id"]: item for item in concepts}

    valid = [q for q in questions if q.get("status", "confirmed") == "confirmed"]
    review = [q for q in questions if q.get("status") != "confirmed"]
    years = [int(q["year"]) for q in valid if q.get("year") is not None]
    latest = max(years) if years else 0
    recent_floor = latest - 4
    by_concept = defaultdict(list)
    for question in valid:
        for concept_id in question.get("concept_ids", []):
            if concept_id in concept_by_id:
                by_concept[concept_id].append(question)

    rows = []
    for concept in concepts:
        concept_id = concept["id"]
        entries = by_concept.get(concept_id, [])
        question_years = [int(q["year"]) for q in entries if q.get("year") is not None]
        distinct_years = set(question_years)
        recent_count = sum(year >= recent_floor for year in question_years)
        subjective = sum(q.get("question_type") in {"名词解释", "简答题", "问答题", "论述题", "分析题", "分析论述题", "综合题", "案例分析"} for q in entries)
        comprehensive = sum(q.get("question_type") in {"分析题", "分析论述题", "综合题", "案例分析"} for q in entries)
        score_total = sum(float(q["score"]) for q in entries if q.get("score") is not None)
        cooccurrence = Counter(
            other
            for q in entries
            for other in q.get("concept_ids", [])
            if other != concept_id
        )
        max_score = max((float(q["score"]) for q in entries if q.get("score") is not None), default=0)
        occurrence_signal = clamp(len(distinct_years) / 6)
        recent_signal = clamp(recent_count / 4)
        score_signal = clamp(score_total / 60)
        subjective_signal = clamp(subjective / 4)
        comprehensive_signal = clamp(comprehensive / 3)
        core_signal = 1.0 if concept.get("course_core") else 0.0
        prerequisite_signal = clamp(int(concept.get("prerequisite_count", 0)) / 4)
        raw = 100 * (
            0.25 * occurrence_signal
            + 0.18 * recent_signal
            + 0.12 * score_signal
            + 0.15 * subjective_signal
            + 0.12 * comprehensive_signal
            + 0.10 * core_signal
            + 0.08 * prerequisite_signal
        )
        star = classify(raw, len(distinct_years))
        evidence_note = (
            "暂无真题证据"
            if not distinct_years else
            "单年集中，待更多年份验证"
            if len(distinct_years) == 1 else
            "跨年证据"
        )
        rows.append({
            "concept_id": concept_id,
            "concept": concept["name"],
            "module": concept.get("module", ""),
            "chapter": concept.get("chapter", ""),
            "question_count": len(entries),
            "year_count": len(distinct_years),
            "exam_years": ",".join(map(str, sorted(distinct_years))),
            "recent_count": recent_count,
            "streak": streak(question_years),
            "score_total": round(score_total, 2),
            "max_score": max_score,
            "subjective_count": subjective,
            "comprehensive_count": comprehensive,
            "cooccurrence_count": sum(cooccurrence.values()),
            "raw_score": round(raw, 2),
            "stars": "★" * star + "☆" * (5 - star),
            "importance": STAR_LABELS[star],
            "evidence_note": evidence_note,
            "trend": (
                "证据不足" if len(distinct_years) < 2
                else "近年升温" if recent_count >= 2 and len(distinct_years) <= 3
                else "稳定"
            ),
            "question_ids": ",".join(q["question_id"] for q in entries),
            "top_related": ",".join(k for k, _ in cooccurrence.most_common(4)),
        })
    rows.sort(key=lambda row: (-row["raw_score"], row["concept_id"]))

    csv_path = out_dir / "exam-frequency.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["concept_id"])
        writer.writeheader()
        writer.writerows(rows)

    def evidence(row):
        return f"出现 {row['question_count']} 题 / {row['year_count']} 年；近5年 {row['recent_count']} 题；主观题 {row['subjective_count']} 题；综合题 {row['comprehensive_count']} 题；总分 {row['score_total']}。"

    lines = ["# 867 环境学考试版知识体系", "", f"> 已纳入 {len(valid)} 条已确认题目；另有 {len(review)} 条待复核。权重用于复习排序，不是押题结论。", "", f"> 数据年份：{min(years) if years else '-'}—{max(years) if years else '-'}；未提供 2024 年真题，因此 2024 不参与趋势判断。", ""]
    lines += ["## 重点排序", "", "| 等级 | 知识点 | 证据摘要 | 趋势 |", "|---|---|---|---|"]
    for row in rows:
        lines.append(f"| {row['stars']} {row['importance']} | {row['concept']} | {evidence(row)} | {row['trend']} |")
    lines += ["", "## 证据链", ""]
    for row in rows:
        lines.append(f"### {row['stars']} {row['concept']}（{row['concept_id']}）")
        lines.append(f"- 章节位置：{row['chapter']} / {row['module']}")
        lines.append(f"- 判定依据：{evidence(row)}")
        lines.append(f"- 证据状态：{row['evidence_note']}")
        lines.append(f"- 题目 ID：{row['question_ids'] or '暂无已确认题目'}")
        lines.append(f"- 共现知识点：{row['top_related'] or '暂无'}")
        lines.append("")
    (out_dir / "exam-topic-analysis.md").write_text("\n".join(lines), encoding="utf-8")

    index_lines = ["# 知识点—历年真题索引", "", "> 题干来自原始题目或参考答案可确认主题；`question_fidelity` 用于区分逐题核对和主题重建。", ""]
    question_by_id = {question["question_id"]: question for question in valid}
    for row in rows:
        index_lines += [f"## {row['stars']} {row['concept']}（{row['concept_id']}）", ""]
        ids = row["question_ids"].split(",") if row["question_ids"] else []
        for question_id in ids:
            question = question_by_id[question_id]
            score = f"，{question['score']}分" if question.get("score") is not None else "，分值未核对"
            fidelity = question.get("question_fidelity", "未标注")
            index_lines.append(f"- `{question_id}`：{question['year']}年 / {question['question_type']}{score} / {fidelity} — {question['question']}")
        if not ids:
            index_lines.append("- 暂无已确认题目")
        index_lines.append("")
    (out_dir / "concept-question-index.md").write_text("\n".join(index_lines), encoding="utf-8")

    map_lines = ["# 考试知识地图", "", "```mermaid", "mindmap", "  root((867 环境学))"]
    for row in rows:
        map_lines.append(f"    {row['stars']} {row['concept']} ({row['concept_id']})")
        concept = concept_by_id[row["concept_id"]]
        for child in concept.get("children", []):
            map_lines.append(f"      {child}")
        for dependency in concept.get("depends_on", []):
            map_lines.append(f"      前置：{dependency}")
    map_lines += ["```", "", "## 学习顺序", ""]
    map_lines += [f"{index}. **{row['stars']} {row['concept']}** — {row['importance']}（{row['trend']}）" for index, row in enumerate(rows, 1)]
    (out_dir / "exam-knowledge-map.md").write_text("\n".join(map_lines), encoding="utf-8")
    (out_dir / "exam-knowledge-map.mmd").write_text("\n".join(map_lines[3:map_lines.index("```")]), encoding="utf-8")

    trend_lines = ["# 真题趋势报告", "", "> 趋势只描述已经提供的年份，不对缺失年份补值，也不用于预测下一年必考。", ""]
    trend_lines += ["## 年份覆盖", "", "| 年份 | 已确认题目数 | 涉及知识点 |", "|---|---:|---:|"]
    year_groups = defaultdict(list)
    for question in valid:
        year_groups[int(question["year"])].append(question)
    for year in sorted(year_groups):
        ids = sorted({concept_id for question in year_groups[year] for concept_id in question.get("concept_ids", [])})
        trend_lines.append(f"| {year} | {len(year_groups[year])} | {', '.join(ids)} |")
    trend_lines += ["", "## 知识点趋势", "", "| 知识点 | 跨年数 | 最近5年 | 连续年份 | 判断 |", "|---|---:|---:|---:|---|"]
    for row in rows:
        trend_lines.append(f"| {row['concept']} | {row['year_count']} | {row['recent_count']} | {row['streak']} | {row['trend']}；{row['evidence_note']} |")
    (out_dir / "exam-trends.md").write_text("\n".join(trend_lines), encoding="utf-8")

    high_lines = ["# 高频重点", "", "> 这里的“高频”指跨年份重复出现，并结合主观题、综合题与课程核心程度排序；不是押题。", ""]
    for row in rows:
        if row["year_count"] >= 2:
            high_lines += [f"## {row['stars']} {row['concept']}", f"- 出现：{row['question_count']} 题 / {row['year_count']} 年；近5年 {row['recent_count']} 题。", f"- 主观题：{row['subjective_count']}；综合题：{row['comprehensive_count']}；连续年份：{row['streak']}。", f"- 证据状态：{row['evidence_note']}；题目：{row['question_ids']}", ""]
    (out_dir / "high-frequency-topics.md").write_text("\n".join(high_lines), encoding="utf-8")

    tiers = {5: [], 4: [], 3: [], 2: [], 1: []}
    for row in rows:
        tiers[len(row["stars"].replace("☆", ""))].append(row)
    priority_lines = ["# 考前最终版", "", "> 先按星级学习；同一星级内优先主观题和综合题。", ""]
    for star in [5, 4, 3, 2, 1]:
        label = STAR_LABELS[star]
        priority_lines += [f"## {'★' * star}{'☆' * (5 - star)} {label}", ""]
        priority_lines += [f"- {row['concept']}（{row['concept_id']}）：{row['question_count']}题 / {row['year_count']}年；主观题 {row['subjective_count']}；综合题 {row['comprehensive_count']}。" for row in tiers[star]] or ["- 暂无"]
        priority_lines.append("")
    (out_dir / "priority-summary.md").write_text("\n".join(priority_lines), encoding="utf-8")

    study_lines = ["# 推荐学习顺序", "", "> 先掌握前置节点，再进入同星级的具体题型训练。", ""]
    for index, row in enumerate(rows, 1):
        prerequisites = ", ".join(concept_by_id[dependency]["name"] for dependency in concept_by_id[row["concept_id"]].get("depends_on", [])) or "无"
        study_lines.append(f"{index}. **{row['stars']} {row['concept']}** — 前置：{prerequisites}；建议训练：名词定义 → 简答框架 → 综合题迁移。")
    (out_dir / "recommended-study-order.md").write_text("\n".join(study_lines), encoding="utf-8")

    html_rows = []
    for row in rows:
        html_rows.append("<tr data-text='%s'><td>%s</td><td>%s</td><td>%s</td><td>%s 年</td><td>%s 题</td><td>%s</td></tr>" % (
            row["concept"], row["stars"], row["concept"], row["importance"], row["year_count"], row["question_count"], row["trend"]))
    html = """<!doctype html><meta charset='utf-8'><title>867 环境学考试知识地图</title>
<style>body{font:16px system-ui,sans-serif;max-width:1100px;margin:32px auto;padding:0 18px;color:#202124}input{padding:10px;width:320px}table{border-collapse:collapse;width:100%%;margin-top:18px}th,td{border-bottom:1px solid #ddd;padding:10px;text-align:left}th{background:#f4f6f8}.star{color:#b26a00}.note{color:#666}</style>
<h1>867 环境学考试版知识地图</h1><p class='note'>基于已确认真题的历史统计；不代表下一年必考。</p><input id='search' placeholder='筛选知识点'><table><thead><tr><th>等级</th><th>知识点</th><th>分类</th><th>跨年</th><th>题数</th><th>趋势</th></tr></thead><tbody>%s</tbody></table>
<script>const input=document.querySelector('#search');input.oninput=()=>{const q=input.value.toLowerCase();document.querySelectorAll('tbody tr').forEach(r=>r.hidden=!r.dataset.text.toLowerCase().includes(q))}</script>""" % "\n".join(html_rows)
    (out_dir / "exam-knowledge-map.html").write_text(html, encoding="utf-8")

    must = ["# 核心必背清单", "", "> 仅列入当前数据中达到 ★★★★★ 的知识点；数据不足的节点不会被伪装成重点。", ""]
    for row in rows:
        if row["stars"] == "★★★★★":
            must += [f"## {row['concept']}", f"- 证据：{evidence(row)}", f"- 真题：{row['question_ids']}", ""]
    if len(must) == 4:
        must.append("当前没有足够的已确认真题证据达到 ★★★★★；先完成 review-queue 中的复核。")
    (out_dir / "must-memorize.md").write_text("\n".join(must), encoding="utf-8")

    review_lines = ["# 真题人工复核队列", "", "以下记录不能进入频次统计，直到 `status` 改为 `confirmed`。", ""]
    for q in review:
        review_lines.append(f"- `{q.get('question_id', '?')}` {q.get('year', '?')}：{q.get('review_reason', '待核对')}（来源：{q.get('source', '')}）")
    if not review:
        review_lines.append("当前没有待复核记录。")
    (out_dir / "review-queue.md").write_text("\n".join(review_lines), encoding="utf-8")

    print(f"confirmed questions: {len(valid)}")
    print(f"review questions: {len(review)}")
    print(f"concepts: {len(rows)}")
    print(f"outputs: {out_dir}")


if __name__ == "__main__":
    main()
