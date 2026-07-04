# 系統簡介 — 黑暗傑客股市控球後衛

| 項目 | 內容 |
|---|---|
| **中文名稱** | 黑暗傑客股市控球後衛 |
| **英文名稱** | BlackJ Stock Point Guard |
| **系統代號** | `BJSPG` |
| **縮寫** | `BJSPG` |
| **資料庫** | 無（不使用資料庫） |
| **相依系統** | 無 |
| **GitHub Repo** | https://github.com/Blackjtsai/blackj-stock-point-guard.git（Public） |

> 本文件同時供**人類隊友**與**其他專案 Agent** 閱讀。
> 最後更新：2026-07-04

---

## 這個系統是什麼

個人使用的台股現股買賣建議輔助工具。由 Claude Code 在每日三個固定時間點（08:30 / 12:30 / 21:30）本機排程執行分析，蒐集公開市場資料（融資融券、三大法人、費半、WTI），產出買賣建議報告，寫入專案資料夾並 push 到 GitHub，透過 GitHub Pages 靜態網頁瀏覽歷史紀錄。系統不連接券商、不自動下單，所有交易決策仍由使用者本人執行。

---

## 對外介面

### 靜態網頁（前台）

| 路由 | 說明 |
|---|---|
| GitHub Pages 首頁 | 依日期列出已產出的報告（08:30/12:30/21:30 三份），最新在最上方 |

本系統無 REST API、無 MCP Server、無傳統後台管理介面。

---

## 如果你是接入方

本系統不對外提供 API，僅供使用者本人透過瀏覽器查看 GitHub Pages 網址。若要串接排程，參考 `docs/SETUP.md` 的 `launchd` 設定方式。

---

## 技術棧

| 層 | 技術 |
|---|---|
| 執行引擎 | Claude Code CLI（headless） |
| 排程 | macOS `launchd` |
| 資料儲存 | Markdown 報告檔 + `reports/state.json` |
| 前台 | 純 HTML/CSS/JS，無框架 |
| 部署 | Git + GitHub Pages |

---

## 常見坑

- 排程觸發當下若電腦未開機/未登入/無網路，該次報告不會產生，屬預期行為，非故障
- 公開網頁抓到的盤中報價有 delay，12:30 報告是「複核」性質，不是即時大單追蹤
- 「回補提示」只根據系統自己過去的建議紀錄推算，不代表使用者真實持股狀態

---

## 維護者

| 角色 | 姓名 / 聯絡方式 |
|---|---|
| 負責人 | 黑暗傑客（Eason Tsai） |
| Issue tracker | GitHub repo Issues |
