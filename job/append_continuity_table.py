#!/usr/bin/env python3
# ============================================================
# 檔案名稱：append_continuity_table.py
# 中文名稱：延續數據表附加腳本
# 功能說明：排程分析（claude -p）寫完報告後，由本腳本讀取 reports/state.json 與
#           watchlist，決定性地把「延續數據表」（人讀表格 + 機器可讀 JSON 註解）
#           附加到該份報告檔案末尾，不假手 LLM 排版
# 所屬模組：job/（UC-BJSPG 3.5、SDD.md 6.5、ADR-005）
# 建立日期：2026-07-06
# 修改日期：2026-07-06
# 開發者　：Claude Code
# ============================================================
#
# 用法：python3 job/append_continuity_table.py <report_md_path>
#
# 設計原則（見 ADR-005 修訂）：
# - 這是純粹的資料轉錄工作（把 state.json 現有數字寫成表格），不需要 LLM 判斷，
#   交給 headless LLM 手工排版容易因格式漂移導致 web/build.py 擷取失敗或抓錯欄位。
#   改由本腳本決定性產出固定格式，格式風險歸零。
# - 同時輸出「人讀表格」（供人直接看 .md）與「機器可讀 JSON 註解」
#   （<!-- BJSPG_CONTINUITY: {...} -->，供 web/build.py 直接 json.loads()，
#   不必再用正則猜測表格儲存格內容）。
# - 純 Python 標準函式庫，不依賴 pip 套件（與 web/build.py 一致的限制）。
# - 某檔股票在 state.json 尚無 last_price/limit_range（例如當日新加入 watchlist）
#   時，一律標示「資料未取得」，絕不推算或沿用其他標的數字（見 SDD.md 6.2）。

import json
import re
import sys
from pathlib import Path


def load_watchlist(path: Path) -> list[dict]:
    """讀取 watchlist.json 的股票清單，檔案不存在時回傳空清單"""
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("stocks", [])


def load_state(path: Path) -> dict:
    """讀取 state.json 的股票狀態，檔案不存在或內容非預期時視為空狀態"""
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("stocks", {})


def build_continuity_section(watchlist: list[dict], state: dict) -> str:
    """組出「延續數據表」區塊：人讀 Markdown 表格 + 機器可讀 JSON 註解；state.json 缺資料的欄位固定顯示「資料未取得」"""
    machine_data = {}
    rows = []
    for stock in watchlist:
        code = stock["code"]
        name = stock.get("name", "")
        info = state.get(code, {})
        price = info.get("last_price")
        limit_range = info.get("limit_range")
        rows.append(
            f"| {code} | {name} | {price if price else '資料未取得'} | {limit_range if limit_range else '資料未取得'} |"
        )
        machine_data[code] = {"price": price, "limit_range": limit_range}

    table = "\n".join(
        [
            "## 延續數據表",
            "",
            "> 本表由排程腳本依 `reports/state.json` 目前記錄的數字決定性產出，非本次報告分析內容。",
            "",
            "| 代號 | 名稱 | 收盤價 | 第一批限價 |",
            "|---|---|---|---|",
            *rows,
        ]
    )
    comment = f"<!-- BJSPG_CONTINUITY: {json.dumps(machine_data, ensure_ascii=False)} -->"
    return f"{table}\n\n{comment}\n"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法：python3 job/append_continuity_table.py <report_md_path>", file=sys.stderr)
        sys.exit(1)

    report_path = Path(sys.argv[1])
    if not report_path.is_file():
        print(f"找不到報告檔案：{report_path}", file=sys.stderr)
        sys.exit(1)

    project_dir = Path(__file__).resolve().parent.parent
    watchlist = load_watchlist(project_dir / "job" / "watchlist.json")
    state = load_state(project_dir / "reports" / "state.json")

    section = build_continuity_section(watchlist, state)
    with report_path.open("a", encoding="utf-8") as f:
        f.write("\n---\n\n" + section)
