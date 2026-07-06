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
- [x] 2026-07-07：排程實際執行機制確認已全面改為 Claude Code 雲端 Routines（`BJSPG-PRE-0800`／`BJSPG-MID-1230`／`BJSPG-POST-2130`），本機 `launchd` + `run_analysis.sh` 停用，文件同步更新，見 ADR-007

## Layer 2：分析與報告產出邏輯（UC-BJSPG 3.5.1 ～ 3.5.6）

- [x] UC-BJSPG 3.5.6 撰寫排程分析用 prompt / slash command，內含資料正確性原則（多來源比對、抓不到不捏造）（`job/prompts/{PRE,MID,POST}.md`）
- [x] UC-BJSPG 3.5.1 08:00 盤前分析邏輯（2026-07-04 手動實跑成功產出 `0830_PRE.md`；2026-07-06 為正式交易日 launchd 排程正式觸發，成功產出 `0800_PRE.md` 並更新 `state.json`、git push 成功）
- [ ] UC-BJSPG 3.5.2 12:30 盤中複核邏輯（已於 2026-07-04 手動驗證執行一次，因當日休市無新資料可複核；正式交易日的複核情境仍待 Layer 4 實跑驗證）
- [ ] UC-BJSPG 3.5.3 21:30 盤後定錨邏輯（已於 2026-07-04 手動驗證執行一次，因當日休市數據與前一日相同；正式交易日的盤後定錨情境仍待 Layer 4 實跑驗證；過程中發現並修正 WebFetch 查全市場大表格會編造數字的風險，見 ADR-003）
- [x] UC-BJSPG 3.5.4 Markdown 報告格式（A/B/C/D 欄位、CASH_WARNING 警語）（已於 `0830_PRE.md` 驗證）
- [x] UC-BJSPG 3.5.5 `reports/state.json` 狀態記錄與回補提示邏輯（已實跑驗證首次執行情境；回補分支邏輯待有實際「高位停利變現→低接」案例時再驗證）
- [x] UC-BJSPG 3.5.7 關注清單管理（新增/移除標的、YouTube/新聞連結輸入）（`job/watchlist.json`、`job/inbox/links.md`，使用者手動編輯即可，無需額外指令）
- [-] UC-BJSPG 3.5.6 除權除息查證補強：新增 TWSE 官方除權除息預告表 API（`TWT48U`）查證步驟；法人數據備援順序明確化，禁止以 `T86`/`TWT44U` 全市場表當備援（實測不支援單一代號篩選，且 `TWT48U` 本身也是近 300 筆的大表格，一併補上逐列比對代號的查詢要求）（2026-07-06 規則已寫定，見 SDD v0.9）；**進行中，待下次排程實跑驗證 LLM 確實依新規則查證**
- [-] UC-BJSPG 3.5.4 新增護盾續抱規則（SDD 6.6）：`job/holdings.local.json`（本機專用、未進版控）記錄真實成本價，安全墊 ≥5% 時 C 段預設不建議「高位停利變現」，除非大盤系統性崩盤（2026-07-06 規則已寫定）；**進行中，待下次 PRE/MID/POST 實跑驗證規則確實套用後才標記完成**

## Layer 3：前台 Dashboard（UC-BJSPG 3.2.1 ～ 3.2.3）

> 使用者於 2026-07-05 確認 Layer 2 手動驗證已足夠，指示跳過 Layer gate 直接開始 Layer 3。

- [x] UC-BJSPG 3.2.1 靜態報告列表頁（`web/build.py` 產生 `index.html`，依日期新到舊列出 PRE/MID/POST 連結；已用 2026-07-04 三份報告本機測試通過）
- [x] UC-BJSPG 3.2.2 RWD 版面（手寫 CSS，flexbox + 表格 `overflow-x:auto`，支援淺色/深色模式）
- [x] UC-BJSPG 3.2.3 決定 GitHub Pages 部署方式：**本機腳本（`web/deploy.sh`）+ 獨立 `gh-pages` orphan branch**，不用 GitHub Actions，與 `docs/` 專案文件互不衝突（見 ARCHITECTURE.md）
- [x] UC-BJSPG 3.2.3 `web/deploy.sh` 已本機測試成功，`gh-pages` branch 已建立並 push 到 GitHub（已串接進 `job/run_analysis.sh`，每次報告 commit 後自動觸發）
- [x] UC-BJSPG 3.2.3 GitHub Pages 設定完成，網址 https://blackjtsai.github.io/blackj-stock-point-guard/ 已可上網瀏覽，2026-07-05 以 WebFetch 確認首頁正確列出 2026-07-04 三份報告連結（PRE/MID/POST）

## Layer 4：端對端整合測試

- [x] 實際跑一次 08:00 排程，確認報告產出、`state.json` 更新、git push 成功（2026-07-06，launchd 正式觸發，非手動）
- [ ] 實際跑一次 12:30 排程，確認複核邏輯正確
- [ ] 實際跑一次 21:30 排程，確認盤後定錨與明日規劃
- [ ] 確認前台 GitHub Pages 可看到當日三份報告（2026-07-06 目前僅 PRE，等 MID/POST 觸發後再確認）
- [ ] Error path：模擬資料抓不到 → 報告正確標示「資料未取得」
- [ ] Error path：模擬機器未開機/未登入 → 排程正確跳過不報錯（本機 launchd 時期情境，已停用，見 ADR-007，此項可能不再適用）
- [ ] Error path：模擬訂閱額度不足 → 排程失敗即結束不重試
- [-] Error path：雲端 Routine sandbox 網路故障 / git push 失敗 → 排程正確不重試、不深入除錯地結束。2026-07-06 21:30 POST 撞上此情境，Routine 卡在自行除錯 GPG 簽名／GitHub MCP 權限，耗費大量 tool call 後仍未 push 成功，該份報告確認遺失（不回溯補產出，見 ADR-007）；已在 `job/prompts/{PRE,MID,POST}.md` 補上版本控制段落（失敗即停止、不重試、不深入除錯），待下次真的撞到網路故障時驗證是否確實乾淨結束

## 待辦：GitHub App 整合權限（見 ADR-007）

- [ ] 到 GitHub 網頁把 Routine 用的 GitHub App 整合權限從 Read-only 改成 **Contents: Read and write**，否則 `git push` 撞網路故障時，MCP push 這條備援路徑也走不通（僅使用者可操作，Claude Code 無法代為完成）

## 待辦（原「遷移到常駐機器時」清單，前提是本機 launchd；現已全面改雲端 Routines，下列項目需重新檢視是否仍適用，見 ADR-007）

- [ ] ~~`job/run_analysis.sh` 開頭加 `git pull`~~ — 腳本已停用，若要避免 watchlist.json 衝突，需改成在各 `job/prompts/*.md` 開頭指示 Routine 自己 `git pull`
- [ ] 建立 on-demand（非排程）RemoteTrigger routine：讓使用者離開電腦時可用手機口語告知「新增/移除追蹤股票」，routine 內容為 clone repo → 編輯 `job/watchlist.json` → commit → push
- [ ] ~~確認上述兩項不影響現有 ADR-001 headless 權限設計~~ — ADR-001 的權限假設已被 ADR-007 架空（雲端 Routine 現在本來就有 Bash/git 能力），需另外重新評估
- [ ] `job/holdings.local.json`（本機專用、未進版控，見 ADR-006）不會隨雲端 Routine 的 git 操作同步到任何本機，需要決定手動維護方式或另建私有同步機制
