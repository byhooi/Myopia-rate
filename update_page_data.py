from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

import openpyxl


ROOT = Path(__file__).resolve().parent
EXCEL_PATH = ROOT / "近视率.xlsx"
HTML_PATH = ROOT / "index.html"

EXPECTED_GENDERS = ("女", "男")
EXPECTED_MYOPIA_VALUES = ("是", "否", "")


def read_records(warnings: list[str]) -> list[dict[str, object]]:
    workbook = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
    sheet = workbook.active
    header = [cell.value for cell in sheet[1]]
    columns = {str(name).strip(): index for index, name in enumerate(header) if name is not None}

    missing = [name for name in ("性别", "近视") if name not in columns]
    if missing:
        raise ValueError(f"Excel 缺少必要列：{', '.join(missing)}")

    records: list[dict[str, object]] = []
    gender_index = columns["性别"]
    myopia_index = columns["近视"]

    for row_number, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
        gender = row[gender_index] if gender_index < len(row) else None
        if gender is None or str(gender).strip() == "":
            continue

        gender_text = str(gender).strip()
        if gender_text not in EXPECTED_GENDERS:
            warnings.append(f"第 {row_number} 行性别为“{gender_text}”，将按独立分组统计。")

        myopia_value = row[myopia_index] if myopia_index < len(row) else None
        myopia_text = str(myopia_value).strip() if myopia_value is not None else ""
        if myopia_text not in EXPECTED_MYOPIA_VALUES:
            warnings.append(f"第 {row_number} 行近视列为“{myopia_text}”，已按未近视处理。")

        records.append({
            "gender": gender_text,
            "myopia": myopia_text == "是",
        })

    return records


def update_html(records: list[dict[str, object]], updated: str) -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    data = json.dumps(records, ensure_ascii=False, separators=(",", ":"))

    html, data_count = re.subn(
        r'(<script type="application/json" id="records-data">).*?(</script>)',
        lambda match: f"{match.group(1)}{data}{match.group(2)}",
        html,
        count=1,
        flags=re.S,
    )
    if data_count != 1:
        raise ValueError('没有在 index.html 中找到 id="records-data" 的数据块')

    html, date_count = re.subn(
        r'(<span id="dataUpdated">)[^<]*(</span>)',
        lambda match: f"{match.group(1)}{updated}{match.group(2)}",
        html,
        count=1,
    )
    if date_count != 1:
        raise ValueError('没有在 index.html 中找到 id="dataUpdated" 的时间戳占位')

    HTML_PATH.write_text(html, encoding="utf-8")


def gender_summary(records: list[dict[str, object]]) -> str:
    order = {gender: index for index, gender in enumerate(EXPECTED_GENDERS)}
    genders = sorted(
        {str(item["gender"]) for item in records},
        key=lambda gender: (order.get(gender, len(order)), gender),
    )
    parts = []
    for gender in genders:
        items = [item for item in records if item["gender"] == gender]
        count = sum(1 for item in items if item["myopia"])
        rate = count / len(items) * 100
        parts.append(f"{gender} {count}/{len(items)}={rate:.1f}%")
    return "；".join(parts)


def main() -> None:
    warnings: list[str] = []
    records = read_records(warnings)
    if not records:
        print("错误：Excel 中没有有效记录，请检查「性别」列是否为空。", file=sys.stderr)
        sys.exit(1)

    updated = date.today().isoformat()
    update_html(records, updated)

    total = len(records)
    myopia = sum(1 for item in records if item["myopia"])
    rate = myopia / total * 100 if total else 0
    print(f"已更新 index.html：{total} 人，{myopia} 人近视，近视率 {rate:.1f}%。数据日期 {updated}。")

    summary = gender_summary(records)
    if summary:
        print(f"性别分组：{summary}。")

    if warnings:
        print(f"发现 {len(warnings)} 条数据异常，请修正 Excel 后重新运行：", file=sys.stderr)
        for message in warnings:
            print(f"  警告：{message}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
