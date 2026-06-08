from __future__ import annotations

import json
import re
from pathlib import Path

import openpyxl


ROOT = Path(__file__).resolve().parent
EXCEL_PATH = ROOT / "近视率.xlsx"
HTML_PATH = ROOT / "index.html"


def read_records() -> list[dict[str, object]]:
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

    for row in sheet.iter_rows(min_row=2, values_only=True):
        gender = row[gender_index] if gender_index < len(row) else None
        if gender is None or str(gender).strip() == "":
            continue

        myopia_value = row[myopia_index] if myopia_index < len(row) else None
        records.append({
            "gender": str(gender).strip(),
            "myopia": str(myopia_value).strip() == "是" if myopia_value is not None else False,
        })

    return records


def update_html(records: list[dict[str, object]]) -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    data = json.dumps(records, ensure_ascii=False, separators=(",", ":"))
    pattern = r"const records = \[.*?\];"
    replacement = f"const records = {data};"
    html, count = re.subn(pattern, replacement, html, count=1, flags=re.S)
    if count != 1:
        raise ValueError("没有在 index.html 中找到 records 数据块")

    HTML_PATH.write_text(html, encoding="utf-8")


def main() -> None:
    records = read_records()
    update_html(records)

    total = len(records)
    myopia = sum(1 for item in records if item["myopia"])
    rate = myopia / total * 100 if total else 0
    print(f"已更新 index.html：{total} 人，{myopia} 人近视，近视率 {rate:.1f}%。")


if __name__ == "__main__":
    main()
