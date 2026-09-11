#!/usr/bin/env python3
"""Validate additive V2 exam-analysis artifacts and their invariants."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

LEVELS = {"question_confirmed", "topic_confirmed", "answer_confirmed", "inferred"}


def jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--analysis", default="真题/analysis")
    ap.add_argument("--questions", default="真题/analysis/questions.jsonl")
    args = ap.parse_args()
    root = Path(args.analysis)
    errors = []
    questions = jsonl(Path(args.questions))
    qids = {q.get("question_id") for q in questions}
    concepts = json.loads((root / "concepts-v2.json").read_text(encoding="utf-8"))
    topics = {t["topic_id"]: t for t in json.loads((root / "topics-v2.json").read_text(encoding="utf-8"))}
    concept_ids = {c["concept_id"] for c in concepts}
    if len(concept_ids) != len(concepts): errors.append("concept ids are not unique")
    for c in concepts:
        if c.get("topic_id") not in topics: errors.append(f"unknown topic for {c.get('concept_id')}")
    tree = json.loads((root / "course-tree-v2.json").read_text(encoding="utf-8"))
    tree_concepts = {c["concept_id"] for m in tree["modules"] for t in m["topics"] for c in t["concepts"]}
    if tree_concepts != concept_ids: errors.append("course tree concepts differ from concepts-v2")
    relations = jsonl(root / "question-concepts-v2.jsonl")
    seen = set()
    for r in relations:
        key = (r.get("question_id"), r.get("concept_id"))
        if key in seen: errors.append(f"duplicate relation {key}")
        seen.add(key)
        if r.get("question_id") not in qids: errors.append(f"unknown question {r.get('question_id')}")
        if r.get("concept_id") not in concept_ids: errors.append(f"unknown concept {r.get('concept_id')}")
        if r.get("evidence_level") not in LEVELS: errors.append(f"invalid evidence level {r.get('evidence_level')}")
        if r.get("is_subquestion") != bool(next(q for q in questions if q["question_id"] == r["question_id"]).get("parent_question_id")):
            errors.append(f"subquestion mismatch {r.get('question_id')}")
    evidence = jsonl(root / "evidence-v2.jsonl")
    if {e["question_id"] for e in evidence} != qids: errors.append("evidence coverage differs from canonical questions")
    for e in evidence:
        if e.get("evidence_level") not in LEVELS: errors.append(f"invalid evidence record {e.get('question_id')}")
    rows = list(csv.DictReader((root / "exam-frequency-v2.csv").open(encoding="utf-8-sig", newline="")))
    if {r["concept_id"] for r in rows} != concept_ids: errors.append("CSV concepts differ from concepts-v2")
    ranked = [r for r in rows if r["priority_rank"]]
    ranks = [int(r["priority_rank"]) for r in ranked]
    if ranks != list(range(1, len(ranks) + 1)): errors.append("priority ranks are not contiguous")
    for r in rows:
        if r["concept_id"] == "x01" and r["priority_rank"]: errors.append("bridge concept must not have a priority rank")
        if int(r["subquestion_count"]) > int(r["paper_question_count"]): errors.append(f"subquestions exceed papers for {r['concept_id']}")
    stats = json.loads((root / "exam-stats-v2.json").read_text(encoding="utf-8"))
    expected_stats = {
        "canonical_question_count": len(questions),
        "paper_question_count": len({q.get("parent_question_id") or q["question_id"] for q in questions}),
        "subquestion_record_count": sum(bool(q.get("parent_question_id")) for q in questions),
        "relation_count": len(relations),
        "relation_subquestion_count": sum(bool(r["is_subquestion"]) for r in relations),
        "active_concept_count": sum(c.get("status") == "active" for c in concepts),
        "bridge_concept_count": sum(c.get("status") == "bridge" for c in concepts),
    }
    for key, value in expected_stats.items():
        if stats.get(key) != value: errors.append(f"exam-stats mismatch {key}: {stats.get(key)} != {value}")
    if errors:
        for error in errors: print(f"ERROR: {error}")
        return 1
    print(f"valid V2: {len(concepts)} concepts, {len(questions)} questions, {len(relations)} relations, {len(ranked)} ranked concepts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
