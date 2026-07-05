# TODO — BLACKJ-STOCK-POINT-GUARD

> 進度唯一來源。每次對話查進度從此檔讀取，不從記憶體查。
> 任務說明請查 `docs/design/TASK.md`；UC 清單請查 `docs/design/SDD.md`；架構請查 `docs/design/ARCHITECTURE.md`。
> 格式：`[ ]` 待辦 / `[x]` 完成 / `[-]` 進行中
> 任務項目請附 UC 編號，例：`[ ] UC-BJSPG 3.1.1 專案骨架建置`

---

## Layer 1：環境建置與排程骨架（UC-BJSPG 3.1.1 ～ 3.1.3）

- [x] UC-BJSPG 3.1.1 專案骨架建置（CLAUDE.md / docs / .claude 等）
- [x] UC-BJSPG 3.1.1 `git init` + 設定 remote（SSH：`git@github.com:Blackjtsai/blackj-stock-point-guard.git`）
- [x] UC-BJSPG 3.1.1 初始 commit + push
- [x] UC-BJSPG 3.1.2 撰寫 3 個 `launchd` plist（08:30 / 12:30 / 21:30），已 `launchctl load` 並用 `job/run_analysis.sh` 手動測試通過（headless 執行 + log + 自動 commit/push 皆正常）
- [x] UC-BJSPG 3.1.2 確認 `claude` CLI 可 headless 執行並使用訂閱帳號額度（`claude -p` 已測試成功）
- [x] UC-BJSPG 3.1.3 確認本機 git 憑證可直接 push（改用 SSH remote，已 push 成功）

## Layer 2：分析與報告產出邏輯（UC-BJSPG 3.5.1 ～ 3.5.6）

- [x] UC-BJSPG 3.5.6 撰寫排程分析用 prompt / slash command，內含資料正確性原則（多來源比對、抓不到不捏造）（`job/prompts/{PRE,MID,POST}.md`）
- [x] UC-BJSPG 3.5.1 08:30 盤前分析邏輯（已實跑一次，成功產出 `0830_PRE.md`）
- [ ] UC-BJSPG 3.5.2 12:30 盤中複核邏輯（已於 2026-07-04 手動驗證執行一次，因當日休市無新資料可複核；正式交易日的複核情境仍待 Layer 4 實跑驗證）
- [ ] UC-BJSPG 3.5.3 21:30 盤後定錨邏輯（已於 2026-07-04 手動驗證執行一次，因當日休市數據與前一日相同；正式交易日的盤後定錨情境仍待 Layer 4 實跑驗證；過程中發現並修正 WebFetch 查全市場大表格會編造數字的風險，見 ADR-003）
- [x] UC-BJSPG 3.5.4 Markdown 報告格式（A/B/C/D 欄位、CASH_WARNING 警語）（已於 `0830_PRE.md` 驗證）
- [x] UC-BJSPG 3.5.5 `reports/state.json` 狀態記錄與回補提示邏輯（已實跑驗證首次執行情境；回補分支邏輯待有實際「高位停利變現→低接」案例時再驗證）
- [x] UC-BJSPG 3.5.7 關注清單管理（新增/移除標的、YouTube/新聞連結輸入）（`job/watchlist.json`、`job/inbox/links.md`，使用者手動編輯即可，無需額外指令）

## Layer 3：前台 Dashboard（UC-BJSPG 3.2.1 ～ 3.2.3）

> 使用者於 2026-07-05 確認 Layer 2 手動驗證已足夠，指示跳過 Layer gate 直接開始 Layer 3。

- [x] UC-BJSPG 3.2.1 靜態報告列表頁（`web/build.py` 產生 `index.html`，依日期新到舊列出 PRE/MID/POST 連結；已用 2026-07-04 三份報告本機測試通過）
- [x] UC-BJSPG 3.2.2 RWD 版面（手寫 CSS，flexbox + 表格 `overflow-x:auto`，支援淺色/深色模式）
- [x] UC-BJSPG 3.2.3 決定 GitHub Pages 部署方式：**本機腳本（`web/deploy.sh`）+ 獨立 `gh-pages` orphan branch**，不用 GitHub Actions，與 `docs/` 專案文件互不衝突（見 ARCHITECTURE.md）
- [x] UC-BJSPG 3.2.3 `web/deploy.sh` 已本機測試成功，`gh-pages` branch 已建立並 push 到 GitHub（已串接進 `job/run_analysis.sh`，每次報告 commit 後自動觸發）
- [ ] UC-BJSPG 3.2.3 GitHub Pages 設定（repo Settings → Pages → Source: Deploy from branch → `gh-pages` / `/(root)`）——**需使用者手動至 GitHub 網頁設定一次**（沒有 `gh` CLI/API token 可自動化），設定後確認網址可上網瀏覽

## Layer 4：端對端整合測試

- [ ] 實際跑一次 08:30 排程，確認報告產出、`state.json` 更新、git push 成功
- [ ] 實際跑一次 12:30 排程，確認複核邏輯正確
- [ ] 實際跑一次 21:30 排程，確認盤後定錨與明日規劃
- [ ] 確認前台 GitHub Pages 可看到當日三份報告
- [ ] Error path：模擬資料抓不到 → 報告正確標示「資料未取得」
- [ ] Error path：模擬機器未開機/未登入 → 排程正確跳過不報錯
- [ ] Error path：模擬訂閱額度不足 → 排程失敗即結束不重試

## 待辦（遷移到常駐機器時一併處理）

- [ ] `job/run_analysis.sh` 開頭加 `git pull`，避免遠端（如手機 dispatch）改的 `watchlist.json` 沒同步到常駐機器就被排程覆蓋
- [ ] 建立 on-demand（非排程）RemoteTrigger routine：讓使用者離開電腦時可用手機口語告知「新增/移除追蹤股票」，routine 內容為 clone repo → 編輯 `job/watchlist.json` → commit → push
- [ ] 確認上述兩項不影響現有 ADR-001 headless 權限設計（`run_analysis.sh` 本身不受 `--allowedTools` 限制，`git pull` 由 shell 執行，非 claude 工具）
