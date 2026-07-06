#!/usr/bin/env python3
# ============================================================
# 檔案名稱：build.py
# 中文名稱：前台網頁建置腳本
# 功能說明：掃描 reports/ 下所有 Markdown 報告，轉成靜態 HTML（含首頁列表），輸出到指定目錄供部署到 gh-pages branch
# 所屬模組：web/（UC-BJSPG 3.2.1 ～ 3.2.2）
# 建立日期：2026-07-05
# 修改日期：2026-07-06
# 開發者　：Claude Code
# ============================================================
#
# 用法：python3 web/build.py <輸出目錄>
#
# 設計原則：
# - 純 Python 標準函式庫，不依賴 pip 套件（pandoc / markdown 套件皆未安裝，
#   且排程機器未來會遷移，避免引入額外安裝依賴）。
# - 只支援本專案報告實際會用到的 Markdown 語法：標題、粗體、行內反引號、
#   水平線、blockquote、有序/無序清單、表格。不追求通用 Markdown 相容性。

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

REPORT_TYPE_LABEL = {"PRE": "盤前", "MID": "盤中", "POST": "盤後"}

CSS = """
:root { color-scheme: light dark; }
* { box-sizing: border-box; }
body {
  margin: 0; padding: 0;
  font-family: -apple-system, "PingFang TC", "Noto Sans TC", sans-serif;
  line-height: 1.7;
  background: #fafafa; color: #1a1a1a;
}
.container { max-width: 780px; margin: 0 auto; padding: 16px 20px 60px; }
h1 { font-size: 1.4rem; }
h2 { font-size: 1.2rem; margin-top: 2em; border-bottom: 2px solid currentColor; padding-bottom: 4px; }
h3 { font-size: 1.05rem; margin-top: 1.5em; }
a { color: #0645ad; text-decoration: none; }
a:hover { text-decoration: underline; }
hr { border: none; border-top: 1px solid #ccc; margin: 2em 0; }
blockquote {
  margin: 1em 0; padding: 8px 14px;
  border-left: 4px solid #c00; background: #fff0f0;
}
code {
  background: rgba(127,127,127,0.15);
  padding: 1px 5px; border-radius: 4px;
  font-size: 0.9em;
}
.table-wrap { overflow-x: auto; margin: 1em 0; }
table { border-collapse: collapse; width: 100%; min-width: 320px; }
th, td { border: 1px solid #ccc; padding: 6px 10px; text-align: left; font-size: 0.95rem; }
th { background: rgba(127,127,127,0.15); }
.back-link { display: inline-block; margin-bottom: 1em; font-size: 0.9rem; }
.index-date { margin-top: 1.6em; }
.index-date h2 { margin-bottom: 0.4em; border: none; }
.index-list { list-style: none; padding: 0; margin: 0; display: flex; gap: 10px; flex-wrap: wrap; }
.index-list li a {
  display: inline-block; padding: 8px 14px;
  border: 1px solid rgba(127,127,127,0.4); border-radius: 8px;
}
.empty-state { margin-top: 3em; text-align: center; opacity: 0.7; }
footer { margin-top: 3em; font-size: 0.8rem; opacity: 0.6; }

.summary-btn {
  display: inline-block; margin: 0 0 1em 10px;
  padding: 6px 14px; border-radius: 8px; cursor: pointer;
  border: 1px solid rgba(127,127,127,0.4);
  background: rgba(127,127,127,0.12); font-size: 0.9rem;
}
.summary-toggle { display: none; }
.summary-backdrop, .summary-modal { display: none; }
.summary-toggle:checked ~ .summary-backdrop,
.summary-toggle:checked ~ .summary-modal { display: block; }
.summary-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.55); z-index: 20; }
.summary-modal {
  position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
  z-index: 21; background: #fff; color: #1a1a1a;
  width: min(92vw, 480px); max-height: 82vh; overflow-y: auto;
  border-radius: 14px; padding: 20px 22px; box-shadow: 0 10px 40px rgba(0,0,0,0.3);
}
.summary-modal h2 { margin-top: 0; }
.summary-close {
  position: absolute; top: 10px; right: 16px; cursor: pointer;
  font-size: 1.3rem; opacity: 0.6;
}
.summary-close:hover { opacity: 1; }
.stock-card {
  border: 1px solid rgba(127,127,127,0.3); border-radius: 10px;
  padding: 10px 14px; margin-bottom: 10px;
}
.stock-card-head { display: flex; justify-content: space-between; align-items: center; gap: 10px; }
.stock-card-head strong { font-size: 1.05rem; }
.badge {
  display: inline-block; padding: 2px 10px; border-radius: 999px;
  font-size: 0.82rem; font-weight: 600; white-space: nowrap;
}
.badge-buy { background: #16833e22; color: #0f6b31; }
.badge-hold { background: #77777730; color: #555; }
.badge-sell { background: #c0392b22; color: #a53324; }
.stock-card-body { margin-top: 6px; font-size: 0.88rem; opacity: 0.9; }

/* Dark-mode 覆寫必須放在最後：CSS 對相同選擇器的優先權以「後寫者贏」，
   若放在對應的淺色規則之前，會被後面的淺色規則蓋掉而失效（曾經發生過的真實 bug）。 */
@media (prefers-color-scheme: dark) {
  body { background: #1a1a1a; color: #e6e6e6; }
  a { color: #7cb8ff; }
  hr { border-color: #444; }
  blockquote { border-color: #ff6b6b; background: #33201f; color: #f2d9d9; }
  table { border-color: #444; }
  th, td { border-color: #444; }
  .summary-modal { background: #232323; color: #e6e6e6; }
  .badge-buy { background: #2ecc7133; color: #7bedac; }
  .badge-hold { background: #ffffff26; color: #ddd; }
  .badge-sell { background: #ff6b6b33; color: #ffabab; }
}
"""


def page(title: str, body: str) -> str:
    """包一層 HTML 骨架（含內嵌 CSS），回傳完整頁面字串"""
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{CSS}</style>
</head>
<body>
<div class="container">
{body}
<footer>BJSPG — 個人台股現股觀察輔助系統，僅供參考，不構成投資建議。</footer>
</div>
</body>
</html>
"""


def inline_md(text: str) -> str:
    """轉換單行內的粗體／行內反引號語法，回傳已 escape 的 HTML 片段"""
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text


def parse_pipe_rows(lines: list[str]) -> list[list[str]]:
    """把一段 `|` 分隔的 Markdown 表格文字轉成儲存格二維陣列，自動濾掉表頭分隔線（`---`）那一行"""
    return [
        [c.strip() for c in line.strip().strip("|").split("|")]
        for line in lines
        if not re.match(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$", line)
    ]


def find_pipe_table(lines: list[str], header_predicate) -> list[list[str]] | None:
    """在整份文件的行陣列中找第一個表頭符合 header_predicate 的 `|` 表格區塊，回傳解析後的儲存格二維陣列；找不到回傳 None"""
    for i, line in enumerate(lines):
        if not header_predicate(line):
            continue
        j = i + 1
        while j < len(lines) and lines[j].strip().startswith("|"):
            j += 1
        rows = parse_pipe_rows(lines[i:j])
        if len(rows) >= 2:
            return rows
    return None


def render_table(lines: list[str]) -> str:
    """轉換一段 Markdown 表格（含表頭分隔線），回傳 <table> HTML；資料列欄位數不足/超出表頭時自動補齊/截斷，避免欄位錯位"""
    rows = parse_pipe_rows(lines)
    if not rows:
        return ""
    head, *body = rows
    col_count = len(head)
    out = ['<div class="table-wrap"><table>', "<thead><tr>"]
    out += [f"<th>{inline_md(c)}</th>" for c in head]
    out.append("</tr></thead><tbody>")
    for r in body:
        cells = (r + [""] * col_count)[:col_count]
        out.append("<tr>" + "".join(f"<td>{inline_md(c)}</td>" for c in cells) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def markdown_to_html(md_text: str) -> str:
    """把單篇報告的 Markdown 全文轉成 HTML 區塊字串（僅支援本專案報告實際會用到的語法子集）"""
    lines = md_text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if re.match(r"^<!--.*-->$", stripped):
            # 單行 HTML 註解（例如 append_continuity_table.py 附加的機器可讀 JSON 標記）不顯示在頁面上
            i += 1
            continue

        if re.match(r"^-{3,}$", stripped):
            out.append("<hr>")
            i += 1
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{inline_md(m.group(2))}</h{level}>")
            i += 1
            continue

        if stripped.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            out.append(render_table(table_lines))
            continue

        if stripped.startswith(">"):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote_lines.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append(f"<blockquote>{inline_md(' '.join(quote_lines))}</blockquote>")
            continue

        if re.match(r"^[-*]\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append(re.sub(r"^[-*]\s+", "", lines[i].strip()))
                i += 1
            out.append("<ul>" + "".join(f"<li>{inline_md(it)}</li>" for it in items) + "</ul>")
            continue

        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            out.append("<ol>" + "".join(f"<li>{inline_md(it)}</li>" for it in items) + "</ol>")
            continue

        para_lines = []
        while i < len(lines) and lines[i].strip() and not re.match(
            r"^(#{1,6}\s|-{3,}$|\||>|[-*]\s+|\d+\.\s+)", lines[i].strip()
        ):
            para_lines.append(lines[i].strip())
            i += 1
        out.append(f"<p>{inline_md(' '.join(para_lines))}</p>")

    return "\n".join(out)


ACTION_BADGE = {
    "金字塔低接": "badge-buy",
    "觀望看戲": "badge-hold",
    "高位停利變現": "badge-sell",
}


def badge_class(action: str) -> str:
    """依建議動作文字對應徽章樣式 class，遇到未知動作一律用中性樣式，不假設"""
    for key, cls in ACTION_BADGE.items():
        if key in action:
            return cls
    return "badge-hold"


def _is_action_summary_header(line: str) -> bool:
    """判斷是否為「建議動作彙整表」的表頭：以代號/名稱開頭且含「建議」字樣，與 B 節籌碼表（代號/名稱/融資...）區分"""
    return bool(re.match(r"^\s*\|\s*代號\s*\|\s*名稱\s*\|", line)) and "建議" in line


def extract_stock_summary(md_text: str) -> list[dict]:
    """擷取報告中的建議動作彙整表，回傳每檔標的的代號/名稱/建議動作/備註；找不到則回傳空清單"""
    rows = find_pipe_table(md_text.splitlines(), _is_action_summary_header)
    if not rows:
        return []
    stocks = []
    for r in rows[1:]:
        r = (r + [""] * 4)[:4]
        stocks.append({"code": r[0], "name": r[1], "action": r[2], "note": r[3]})
    return stocks


def extract_stock_detail(md_text: str, code: str) -> dict:
    """在該股票代號對應的段落內盡力擷取收盤價與第一批金字塔限價區間；本報告未提供時對應欄位回傳 None，不臆測填值"""
    detail: dict = {"price": None, "limit_range": None}
    blocks = re.findall(rf"^###\s+{re.escape(code)}\b.*?(?=^###\s|\Z)", md_text, re.S | re.M)
    block = "\n".join(blocks)

    price_m = re.search(r"收盤價[^\n|]*\|\s*\*{0,2}(?:NT\$)?([\d,]+\.?\d*)", block)
    if not price_m:
        price_m = re.search(rf"\|\s*{re.escape(code)}\s*\S*\s*\|\s*([\d,]+\.\d+)（", md_text)
    if price_m:
        detail["price"] = price_m.group(1)

    range_m = re.search(r"第一批[^\n|]*\|\s*([^\|]+?)\s*\|", block)
    if range_m:
        detail["limit_range"] = range_m.group(1).strip()

    return detail


def extract_continuity_table(md_text: str) -> dict:
    """擷取 `job/append_continuity_table.py` 附加的機器可讀 JSON 註解（`<!-- BJSPG_CONTINUITY: {...} -->`），回傳以代號為 key 的 {price, limit_range} dict；找不到或 JSON 損毀則回傳空 dict（相容尚未套用此機制的舊報告，不拋錯）"""
    m = re.search(r"<!--\s*BJSPG_CONTINUITY:\s*(\{.*?\})\s*-->", md_text, re.S)
    if not m:
        return {}
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return {}


def render_summary_modal(md_text: str) -> str:
    """組出「重點摘要」按鈕 + lightbox（純 CSS checkbox-hack，不需要 JS）；報告沒有建議動作彙整表時回傳空字串，不顯示按鈕。收盤價/限價優先讀 `append_continuity_table.py` 寫入的 JSON 註解，舊報告沒有這個註解時 fallback 到逐段落最佳猜測擷取"""
    stocks = extract_stock_summary(md_text)
    if not stocks:
        return ""

    continuity = extract_continuity_table(md_text)

    cards = []
    for s in stocks:
        if continuity:
            detail = continuity.get(s["code"], {"price": None, "limit_range": None})
        else:
            detail = extract_stock_detail(md_text, s["code"])
        head = (
            f'<div class="stock-card-head"><strong>{html.escape(s["code"])} {html.escape(s["name"])}</strong>'
            f'<span class="badge {badge_class(s["action"])}">{html.escape(s["action"])}</span></div>'
        )
        body_bits = []
        if detail["price"]:
            body_bits.append(f'收盤價 NT${detail["price"]}')
        if detail["limit_range"]:
            body_bits.append(f'第一批限價 {html.escape(detail["limit_range"])}')
        if s["note"] and s["note"] not in ("—", "-"):
            body_bits.append(html.escape(s["note"]))
        body = f'<div class="stock-card-body">{" ／ ".join(body_bits)}</div>' if body_bits else ""
        cards.append(f'<div class="stock-card">{head}{body}</div>')

    return f"""
<input type="checkbox" id="summary-toggle" class="summary-toggle">
<label for="summary-toggle" class="summary-btn">📊 重點摘要</label>
<label for="summary-toggle" class="summary-backdrop"></label>
<div class="summary-modal">
<label for="summary-toggle" class="summary-close">✕</label>
<h2>重點摘要</h2>
{''.join(cards)}
</div>
"""


def find_reports(reports_dir: Path):
    """掃描 reports/ 下所有符合 {HHMM}_{PRE|MID|POST}.md 命名的報告檔，回傳 (date, time, type, path) 清單；reports/ 尚不存在時視為無報告，回傳空清單"""
    if not reports_dir.is_dir():
        return []
    reports = []
    for date_dir in sorted(reports_dir.iterdir(), reverse=True):
        if not date_dir.is_dir():
            continue
        for md_file in sorted(date_dir.glob("*.md")):
            m = re.match(r"^(\d{4})_(PRE|MID|POST)$", md_file.stem)
            if not m:
                continue
            reports.append((date_dir.name, m.group(1), m.group(2), md_file))
    return reports


def build(out_dir: Path, reports_dir: Path):
    """建置整個靜態網站：每篇報告轉出一頁 HTML，並產生依日期列出所有報告的 index.html"""
    out_dir.mkdir(parents=True, exist_ok=True)
    reports = find_reports(reports_dir)

    by_date: dict[str, list[tuple[str, str, Path]]] = {}
    for date, time, rtype, md_file in reports:
        title = f"{date} {time} {REPORT_TYPE_LABEL[rtype]}報告（{rtype}）"
        md_text = md_file.read_text(encoding="utf-8")
        body_html = markdown_to_html(md_text)
        summary_html = render_summary_modal(md_text)
        out_html = out_dir / date / f"{time}_{rtype}.html"
        out_html.parent.mkdir(parents=True, exist_ok=True)
        out_html.write_text(
            page(title, f'<a class="back-link" href="../index.html">← 回首頁</a>{summary_html}\n{body_html}'),
            encoding="utf-8",
        )
        by_date.setdefault(date, []).append((time, rtype, out_html.relative_to(out_dir)))

    if by_date:
        sections = []
        for date in sorted(by_date, reverse=True):
            items = sorted(by_date[date])
            links = "".join(
                f'<li><a href="{rel_path.as_posix()}">{time} {REPORT_TYPE_LABEL[rtype]}（{rtype}）</a></li>'
                for time, rtype, rel_path in items
            )
            sections.append(
                f'<div class="index-date"><h2>{date}</h2><ul class="index-list">{links}</ul></div>'
            )
        index_body = "\n".join(sections)
    else:
        index_body = '<div class="empty-state">尚無報告，排程尚未產出任何分析。</div>'

    index_html = page(
        "BJSPG 台股觀察報告",
        f"<h1>BJSPG 台股現股觀察報告</h1>\n{index_body}",
    )
    (out_dir / "index.html").write_text(index_html, encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法：python3 web/build.py <輸出目錄>", file=sys.stderr)
        sys.exit(1)

    project_dir = Path(__file__).resolve().parent.parent
    build(Path(sys.argv[1]), project_dir / "reports")
