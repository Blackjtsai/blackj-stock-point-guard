# 系統設計說明書（SDD）— BLACKJ-STOCK-POINT-GUARD

> 版本：v0.1 / 建立日期：2026-07-04

## 1. 系統概述

個人使用的台股現股買賣建議輔助系統。由 Claude Code 於每日 08:30 / 12:30 / 21:30 三個時間點本機排程執行分析，蒐集公開市場資料，產出買賣建議報告，透過 GitHub Pages 靜態網頁供使用者瀏覽。系統邊界與核心原則見 `docs/requirements/需求.md`。

## 2. UC 清單

> UC 編號格式：`UC-BJSPG {大類}.{子層}.{子子層}`
> 此清單由 Claude 依需求文件展開，開發過程中持續維護。

| UC 編號 | 名稱 | API / 元件 | 負責人 | 狀態 |
|---|---|---|---|---|
| UC-BJSPG 3.1 | 基礎建設 | — | — | ⏳ |
| UC-BJSPG 3.1.1 | 環境建置 | 專案骨架、GitHub repo、`.gitignore` | — | ✅ |
| UC-BJSPG 3.1.2 | 本機排程設定 | 3 個 `launchd` plist | — | ⏳ |
| UC-BJSPG 3.1.3 | Git 推送設定 | 本機 git 憑證、自動 commit+push | — | ⏳ |
| UC-BJSPG 3.2 | WEB（前台） | — | — | ⏳ |
| UC-BJSPG 3.2.1 | 報告列表頁 | `web/` 靜態 HTML | — | ⏳ |
| UC-BJSPG 3.2.2 | RWD 版面 | `web/` CSS | — | ⏳ |
| UC-BJSPG 3.2.3 | GitHub Pages 部署 | GitHub Pages / Actions | — | ⏳ |
| UC-BJSPG 3.5 | JOB（排程分析） | — | — | ⏳ |
| UC-BJSPG 3.5.1 | 08:30 盤前分析 | `job/` 分析流程 | — | ⏳ |
| UC-BJSPG 3.5.2 | 12:30 盤中複核 | `job/` 分析流程 | — | ⏳ |
| UC-BJSPG 3.5.3 | 21:30 盤後定錨 | `job/` 分析流程 | — | ⏳ |
| UC-BJSPG 3.5.4 | 報告產出與寫檔 | `reports/*.md` | — | ⏳ |
| UC-BJSPG 3.5.5 | 建議歷史狀態追蹤 | `reports/state.json` | — | ⏳ |
| UC-BJSPG 3.5.6 | 資料正確性把關 | `job/` 分析流程 | — | ⏳ |
| UC-BJSPG 3.5.7 | 關注清單管理 | `job/` 分析流程 | — | ⏳ |

## 3. 架構決策

見 `docs/design/ARCHITECTURE.md` 待確認事項（GitHub Pages 部署路徑），以及 `docs/decisions/`（重大決策落地後於此補 ADR）。

## 4. API 規格

無。本系統不提供 API，僅有 headless CLI 執行與靜態網頁輸出。

## 5. 資料 Schema

不使用資料庫。見 `docs/design/ARCHITECTURE.md` 的「資料 Schema」章節。

## 版本記錄

| 版本 | 日期 | 摘要 |
|---|---|---|
| v0.1 | 2026-07-04 | 初始建立，Layer 1～4 UC 清單定案 |
