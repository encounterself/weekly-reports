#!/usr/bin/env python3
"""Build a consolidated Markdown, HTML, and Chinese PDF review book."""
from __future__ import annotations

import argparse
import html
import pathlib
import re
from xml.sax.saxutils import escape as xml_escape


def read(root: pathlib.Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def strip_mermaid(text: str) -> str:
    return re.sub(r"```mermaid.*?```", "", text, flags=re.S).strip()


def build_markdown(root: pathlib.Path) -> str:
    analysis = root / "真题" / "analysis"
    sections = []
    sections.append("""# 867 环境学真题驱动复习总册

> 版本：2026-09-11
>
> 本总册把已有 Cangjie 知识蒸馏、2012—2025 历年真题结构化分析、考试权重、知识地图和学习工作区整合成一份复习材料。它用于决定复习优先级，不用于预测某一年必考。

## 使用顺序

1. 先看“考试结论”，明确全科主线和核心必背范围。
2. 再看“考试知识地图”和“推荐学习顺序”，按前置关系建立框架。
3. 用“高频重点”和“知识点—历年真题索引”做专题背诵与答题训练。
4. 最后查看“复核边界”，区分已核题干、主题重建和 OCR 草稿。

## 目录

- [一、考试结论](#一考试结论)
- [二、核心必背](#二核心必背)
- [三、高频重点](#三高频重点)
- [四、考试知识地图](#四考试知识地图)
- [五、真题趋势](#五真题趋势)
- [六、推荐学习顺序](#六推荐学习顺序)
- [七、知识点—历年真题索引](#七知识点历年真题索引)
- [八、复核边界与来源](#八复核边界与来源)
""")
    sections.append("\n## 一、考试结论\n\n" + read(root, "真题/analysis/exam-topic-analysis.md"))
    sections.append("\n## 二、核心必背\n\n" + read(root, "真题/analysis/must-memorize.md"))
    sections.append("\n## 三、高频重点\n\n" + read(root, "真题/analysis/high-frequency-topics.md"))
    sections.append("\n## 四、考试知识地图\n\n" + strip_mermaid(read(root, "真题/analysis/exam-knowledge-map.md")))
    sections.append("\n## 五、真题趋势\n\n" + read(root, "真题/analysis/exam-trends.md"))
    sections.append("\n## 六、推荐学习顺序\n\n" + read(root, "真题/analysis/recommended-study-order.md"))
    sections.append("\n## 七、知识点—历年真题索引\n\n" + read(root, "真题/analysis/concept-question-index.md"))
    sections.append("\n## 八、复核边界与来源\n\n" + read(root, "真题/analysis/source-inventory.md") + "\n\n" + read(root, "真题/analysis/review-queue.md"))
    sections.append("""\n## 附录：文件入口

- 可搜索知识地图：`真题/analysis/exam-knowledge-map.html`
- 结构化统计：`真题/analysis/exam-frequency.csv`
- 学习工作区：`复习笔记-study/`
- 学习仪表盘：`复习笔记-study/open/dashboard.html`
- 复习工作区知识树：`复习笔记-study/internal/state/knowledge.json`
- 真题题库：`复习笔记-study/question-bank/question-bank.json`
""")
    return "\n\n".join(sections).replace("\n\n\n", "\n\n") + "\n"


def inline_html(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    return text


def markdown_to_html(md: str) -> str:
    out = []
    lines = md.splitlines()
    in_ul = False
    in_code = False
    in_table = False
    for line in lines:
        if line.startswith("```"):
            if in_code:
                out.append("</pre>")
            else:
                out.append("<pre>")
            in_code = not in_code
            continue
        if in_code:
            out.append(html.escape(line, quote=False))
            continue
        if line.startswith("|"):
            if re.match(r"^\|\s*-+", line):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            tag = "th" if not in_table else "td"
            if not in_table:
                out.append("<table><tr>" + "".join(f"<th>{inline_html(c)}</th>" for c in cells) + "</tr>")
                in_table = True
            else:
                out.append("<tr>" + "".join(f"<td>{inline_html(c)}</td>" for c in cells) + "</tr>")
            continue
        if in_table:
            out.append("</table>")
            in_table = False
        if line.startswith("- "):
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{inline_html(line[2:])}</li>")
            continue
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if not line.strip():
            continue
        if line.startswith("### "):
            out.append(f"<h3>{inline_html(line[4:])}</h3>")
        elif line.startswith("## "):
            out.append(f"<h2>{inline_html(line[3:])}</h2>")
        elif line.startswith("# "):
            out.append(f"<h1>{inline_html(line[2:])}</h1>")
        elif line.startswith("> "):
            out.append(f"<blockquote>{inline_html(line[2:])}</blockquote>")
        else:
            out.append(f"<p>{inline_html(line)}</p>")
    if in_ul:
        out.append("</ul>")
    if in_table:
        out.append("</table>")
    return "\n".join(out)


def build_pdf(md: str, pdf_path: pathlib.Path, font_path: pathlib.Path):
    import sys
    sys.path.insert(0, "/tmp/pdf-debs/root/usr/lib/python3/dist-packages")
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
                                    Spacer, Table, TableStyle)

    pdfmetrics.registerFont(TTFont("WQY", str(font_path)))
    styles = getSampleStyleSheet()
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontName="WQY", fontSize=9.2, leading=13.5, spaceAfter=4)
    h1 = ParagraphStyle("H1", parent=body, fontSize=19, leading=24, textColor=colors.HexColor("#17365d"), spaceBefore=12, spaceAfter=9)
    h2 = ParagraphStyle("H2", parent=body, fontSize=14, leading=18, textColor=colors.HexColor("#24527a"), spaceBefore=11, spaceAfter=6)
    h3 = ParagraphStyle("H3", parent=body, fontSize=11, leading=15, textColor=colors.HexColor("#3d5a80"), spaceBefore=8, spaceAfter=4)
    quote = ParagraphStyle("Quote", parent=body, leftIndent=8, borderColor=colors.HexColor("#b8c7d9"), borderWidth=0.5, borderPadding=5, textColor=colors.HexColor("#59636e"))
    small = ParagraphStyle("Small", parent=body, fontSize=7.5, leading=10)
    story = []
    table_rows = []
    in_code = False
    for raw in md.splitlines():
        line = raw.strip()
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not line:
            continue
        if line.startswith("|"):
            if re.match(r"^\|\s*-+", line):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            table_rows.append([Paragraph(xml_escape(c), small) for c in cells])
            continue
        if table_rows:
            story.append(Table(table_rows, repeatRows=1, colWidths=[(180 / max(len(table_rows[0]), 1)) * mm] * len(table_rows[0]), style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eaf1f8")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#b7c4d1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (-1, -1), "WQY"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ])))
            story.append(Spacer(1, 4))
            table_rows = []
        if line == "---":
            story.append(PageBreak())
        elif line.startswith("### "):
            story.append(Paragraph(xml_escape(line[4:]), h3))
        elif line.startswith("## "):
            story.append(Paragraph(xml_escape(line[3:]), h2))
        elif line.startswith("# "):
            story.append(Paragraph(xml_escape(line[2:]), h1))
        elif line.startswith("- "):
            story.append(Paragraph("• " + xml_escape(line[2:]), body))
        elif re.match(r"^\d+\. ", line):
            story.append(Paragraph(xml_escape(line), body))
        elif line.startswith("> "):
            story.append(Paragraph(xml_escape(line[2:]), quote))
        else:
            text = xml_escape(line)
            text = re.sub(r"`([^`]+)`", r"<font name='WQY'>\1</font>", text)
            text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
            story.append(Paragraph(text, body))
    if table_rows:
        story.append(Table(table_rows, repeatRows=1, style=TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.grey)])))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("WQY", 7)
        canvas.setFillColor(colors.HexColor("#6b7280"))
        canvas.drawString(18 * mm, 10 * mm, "867 环境学真题驱动复习总册 · 仅供复习整理")
        canvas.drawRightString(192 * mm, 10 * mm, f"第 {doc.page} 页")
        canvas.restoreState()

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=16 * mm, leftMargin=16 * mm, topMargin=15 * mm, bottomMargin=16 * mm, title="867 环境学真题驱动复习总册", author="Study Assistant")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default="真题/analysis/final")
    parser.add_argument("--font", required=True)
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    out = (root / args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    md = build_markdown(root)
    (out / "867环境学真题驱动复习总册.md").write_text(md, encoding="utf-8")
    body = markdown_to_html(md)
    html_doc = """<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'><title>867环境学真题驱动复习总册</title><style>
body{font-family:-apple-system,BlinkMacSystemFont,'Noto Sans CJK SC','WenQuanYi Zen Hei',sans-serif;max-width:980px;margin:0 auto;padding:36px 42px;color:#202124;line-height:1.65}h1{color:#17365d;border-bottom:2px solid #17365d;padding-bottom:8px}h2{color:#24527a;border-left:5px solid #6b8fb3;padding-left:10px;margin-top:34px}h3{color:#3d5a80}blockquote{background:#f4f7fa;border-left:4px solid #9db4ca;padding:8px 12px;color:#53606c}table{border-collapse:collapse;width:100%;font-size:13px;margin:12px 0}th,td{border:1px solid #b7c4d1;padding:6px;vertical-align:top}th{background:#eaf1f8}code{background:#f1f3f4;padding:1px 4px}li{margin:4px 0}pre{white-space:pre-wrap;background:#f7f7f7;padding:12px;border:1px solid #ddd}@media print{body{max-width:none;padding:0}h1,h2,h3{break-after:avoid}table{break-inside:avoid}}
</style></head><body>""" + body + "</body></html>"
    (out / "867环境学真题驱动复习总册.html").write_text(html_doc, encoding="utf-8")
    build_pdf(md, out / "867环境学真题驱动复习总册.pdf", pathlib.Path(args.font))
    print(out)


if __name__ == "__main__":
    main()
