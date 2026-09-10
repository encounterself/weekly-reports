#!/usr/bin/env python3
"""Validate the explicit, reviewable exam-analysis data contract."""
from __future__ import annotations

import argparse
import json
import pathlib
import sys


QUESTION_TYPES = {"判断题", "辨析题", "选择题", "名词解释", "简答题", "问答题", "计算题", "论述题", "分析题", "分析论述题", "综合题", "案例分析", "材料分析题"}
STATUSES = {"confirmed", "needs_review"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--concepts", required=True)
    parser.add_argument("--questions", required=True)
    args = parser.parse_args()
    errors = []

    concepts = json.loads(pathlib.Path(args.concepts).read_text(encoding="utf-8"))
    concept_ids = {item.get("id") for item in concepts}
    if len(concept_ids) != len(concepts) or None in concept_ids:
        errors.append("concept ids must be unique and non-empty")

    question_ids = set()
    for line_no, line in enumerate(pathlib.Path(args.questions).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        try:
            question = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_no}: invalid JSON ({exc})")
            continue
        question_id = question.get("question_id")
        if not question_id or question_id in question_ids:
            errors.append(f"line {line_no}: duplicate or empty question_id")
        question_ids.add(question_id)
        if question.get("question_type") not in QUESTION_TYPES:
            errors.append(f"line {line_no}: invalid question_type")
        if question.get("status", "confirmed") not in STATUSES:
            errors.append(f"line {line_no}: invalid status")
        unknown = set(question.get("concept_ids", [])) - concept_ids
        if unknown:
            errors.append(f"line {line_no}: unknown concept_ids {sorted(unknown)}")
        if question.get("score") is not None and not isinstance(question["score"], (int, float)):
            errors.append(f"line {line_no}: score must be numeric or null")
        if not question.get("source"):
            errors.append(f"line {line_no}: source is required")

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"valid: {len(concepts)} concepts, {len(question_ids)} questions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
