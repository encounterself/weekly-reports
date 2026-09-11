# 学习版出版物

本目录是从现有 `真题/analysis` V2 证据层和 `books/867-chushi-notes` Cangjie 课程资料派生的学习内容层，不覆盖旧版分析和第一版总册。

## 内容入口

- `content/learning-units.json`：`module → topic → learning_unit` 和每个单元的考试型学习卡。
- `content/knowledge-map.json`：学生学习地图，含 `priority_rank`、题目数量和掌握度字段。
- `content/core-handbook.json`：核心/高频背诵内容。
- `content/exam-guide.json`：按学习单元组织的历年题目与证据。
- `content/practice-book.json`：唯一题目列表；多标签题通过 `learning_unit_ids` 关联，不重复计数。
- `content/crash-course.json`：冲刺清单、背诵项、答题骨架和易错点。
- `content/study-assistant-entry.json`：`priority_rank → learning_unit → study-teach/quiz/feynman → mastery` 入口。

## PDF

`pdf/` 中的五册 PDF 与 `html/` 中的可打印 HTML 由 `build_publish_books.py` 统一生成。PDF 使用 A4、中文字体、页码和题目/核对区分离；统计口径继承 V2：131 道 paper question、136 条 canonical question，子问不冒充独立大题，多标签题分值不可跨单元求和。

## 重建

```powershell
python study-assistant-skills\exam-analysis\scripts\build_learning_content.py
python study-assistant-skills\exam-analysis\scripts\build_publish_books.py
```

