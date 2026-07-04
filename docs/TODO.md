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

- [ ] UC-BJSPG 3.5.6 撰寫排程分析用 prompt / slash command，內含資料正確性原則（多來源比對、抓不到不捏造）
- [ ] UC-BJSPG 3.5.1 08:30 盤前分析邏輯
- [ ] UC-BJSPG 3.5.2 12:30 盤中複核邏輯
- [ ] UC-BJSPG 3.5.3 21:30 盤後定錨邏輯
- [ ] UC-BJSPG 3.5.4 Markdown 報告格式（A/B/C/D 欄位、CASH_WARNING 警語）
- [ ] UC-BJSPG 3.5.5 `reports/state.json` 狀態記錄與回補提示邏輯
- [ ] UC-BJSPG 3.5.7 關注清單管理（新增/移除標的、YouTube/新聞連結輸入）

## Layer 3：前台 Dashboard（UC-BJSPG 3.2.1 ～ 3.2.3）

- [ ] UC-BJSPG 3.2.1 靜態報告列表頁（簡單列表，最新在最上）
- [ ] UC-BJSPG 3.2.2 RWD 版面（手機/桌機皆可讀）
- [ ] UC-BJSPG 3.2.3 決定 GitHub Pages 部署方式（root / gh-pages 分支，因 `docs/` 已作專案文件用途，見 ARCHITECTURE.md 待確認事項）
- [ ] UC-BJSPG 3.2.3 GitHub Pages 部署設定完成，確認可上網瀏覽

## Layer 4：端對端整合測試

- [ ] 實際跑一次 08:30 排程，確認報告產出、`state.json` 更新、git push 成功
- [ ] 實際跑一次 12:30 排程，確認複核邏輯正確
- [ ] 實際跑一次 21:30 排程，確認盤後定錨與明日規劃
- [ ] 確認前台 GitHub Pages 可看到當日三份報告
- [ ] Error path：模擬資料抓不到 → 報告正確標示「資料未取得」
- [ ] Error path：模擬機器未開機/未登入 → 排程正確跳過不報錯
- [ ] Error path：模擬訂閱額度不足 → 排程失敗即結束不重試
