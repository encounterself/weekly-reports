"""Validate derived learning content and printable PDF outputs."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONTENT = ROOT / "publish" / "content"
PDF = ROOT / "publish" / "pdf"


def main() -> None:
    data = json.loads((CONTENT / "learning-units.json").read_text(encoding="utf-8"))
    units = data["learning_units"]
    ids = [u["learning_unit_id"] for u in units]
    assert len(ids) == len(set(ids)) == 40, "learning_unit IDs must be unique"
    ranked = [u for u in units if u["content"].get("priority_rank")]
    assert len(data["core_top20"]) == 20
    assert len(ranked) == 39
    assert all(u["question_ids"] for u in ranked), "ranked unit without question evidence"
    assert all(u["source_refs"] for u in units), "unit without source anchor"

    practice = json.loads((CONTENT / "practice-book.json").read_text(encoding="utf-8"))
    qids = [q["question_id"] for q in practice["questions"]]
    assert len(qids) == len(set(qids)) == practice["unique_question_count"]
    assert all(q.get("learning_unit_ids") for q in practice["questions"])

    expected = ["01_知识地图与重点", "02_核心背诵手册", "03_历年真题考点册", "04_真题训练册", "05_考前冲刺手册"]
    for name in expected:
        path = PDF / f"{name}.pdf"
        assert path.exists() and path.stat().st_size > 10000, f"missing PDF: {name}"
        try:
            import fitz
            doc = fitz.open(path)
            assert len(doc) >= 1 and all(page.get_text().strip() for page in doc), f"blank PDF page: {name}"
            text = "".join(page.get_text() for page in doc)
            assert "今年必考" not in text
        except ImportError:
            pass
    print(f"valid publish: {len(units)} learning units, {len(qids)} unique practice questions, {len(expected)} PDFs")


if __name__ == "__main__":
    main()
