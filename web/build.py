#!/usr/bin/env python3
# ============================================================
# 檔案名稱：build.py
# 中文名稱：前台網頁建置腳本
# 功能說明：掃描 reports/ 下所有 Markdown 報告，轉成靜態 HTML（含首頁列表），輸出到指定目錄供部署到 gh-pages branch
# 所屬模組：web/（UC-BJSPG 3.2.1 ～ 3.2.2）
# 建立日期：2026-07-05
# 修改日期：2026-07-05
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

import html
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
@media (prefers-color-scheme: dark) {
  body { background: #1a1a1a; color: #e6e6e6; }
  a { color: #7cb8ff; }
  table { border-color: #444 !important; }
  th, td { border-color: #444 !important; }
  blockquote { border-color: #a06; background: #2a1a1a; }
  hr { border-color: #444; }
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


def render_table(lines: list[str]) -> str:
    """轉換一段 Markdown 表格（含表頭分隔線），回傳 <table> HTML；資料列欄位數不足/超出表頭時自動補齊/截斷，避免欄位錯位"""
    rows = [
        [c.strip() for c in line.strip().strip("|").split("|")]
        for line in lines
        if not re.match(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$", line)
    ]
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
        body_html = markdown_to_html(md_file.read_text(encoding="utf-8"))
        out_html = out_dir / date / f"{time}_{rtype}.html"
        out_html.parent.mkdir(parents=True, exist_ok=True)
        out_html.write_text(
            page(title, f'<a class="back-link" href="../index.html">← 回首頁</a>\n{body_html}'),
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
