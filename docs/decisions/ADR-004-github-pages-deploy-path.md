# ADR-004：GitHub Pages 部署路徑 — 本機腳本 + 獨立 gh-pages branch

> 狀態：已採納
> 日期：2026-07-05
> 決策者：黑暗傑客（Eason Tsai）／Claude Code

## 背景

Layer 3（前台 Dashboard，UC-BJSPG 3.2.1 ～ 3.2.3）開始前，`docs/design/ARCHITECTURE.md` 留了一項待確認事項：GitHub Pages 原生設定只能選 repo 根目錄或 `/docs` 當發布來源，但本專案 `docs/` 已作專案文件（TODO/SETUP/design）用途，無法直接拿來放前台網頁內容，需要在 Layer 3 開始前定案部署方式。

使用者於 2026-07-05 指示跳過 Layer 2 尚未 100% 驗收（正式交易日情境待 Layer 4）的 gate，直接開始 Layer 3，因此本決策需在動手實作前先定案。

## 選項

| 選項 | 優點 | 缺點 |
|---|---|---|
| A. GitHub Actions：push 到 `main` 後由 Actions 執行轉換並部署到 `gh-pages` | 就算本機腳本沒跑轉換，Actions 也能自動補跑；不依賴本機 Python 環境 | 多一層 CI 設定與除錯成本；對單人使用、本來就已在本機跑排程+git push 的專案而言是多餘複雜度，不符合 Simplicity First |
| B. 本機腳本（`web/deploy.sh`）+ 獨立 `gh-pages` orphan branch，由 `job/run_analysis.sh` 報告 commit 後順便觸發 | 沿用現有本機 git push 工作流程，不需額外設定 CI；`gh-pages` 為 orphan branch 與 `main` 無共同歷史，和 `docs/` 完全不衝突；轉換腳本用純 Python 標準函式庫（`web/build.py`），不引入 pip/pandoc 依賴，未來遷移到常駐機器時無額外安裝需求 | 若本機排程當次未觸發或執行失敗，網頁不會自動補跑（但這與 Layer 2 報告本身「未觸發即無報告」的既有行為一致，非新增風險） |

## 決策

選擇 **選項 B**。

理由：本專案 `job/run_analysis.sh` 已經是「本機執行 + 自行 git commit/push」的既有模式（見 ADR-001），Layer 3 的網頁部署只是在既有流程尾端多加一步「build + push 到另一個 branch」，不需要引入 GitHub Actions 這種本專案目前完全沒有的新機制。`gh-pages` 用 orphan branch 而非 `main` 內的資料夾，從根本解決「`docs/` 已被專案文件佔用」的路徑衝突，且未來若專案遷移到常駐機器（見 memory：`project_deployment_target`），純 stdlib 的 `web/build.py` 不需要額外安裝任何套件即可直接運作。

後果：
- 新增 `web/build.py`（Markdown → HTML 轉換 + 產生 `index.html`）與 `web/deploy.sh`（build 後 push 到 `gh-pages`），已於 2026-07-05 本機測試成功並 push。
- `job/run_analysis.sh` 在既有的報告 commit/push 之後，新增一行呼叫 `web/deploy.sh`。
- `.gh-pages-worktree/`（本機操作 `gh-pages` branch 用的獨立 git worktree）加入 `.gitignore`，不進 `main` 版控。
- **代價**：GitHub Pages 的「Settings → Pages → Source」仍需使用者手動設定一次（本機無 `gh` CLI 或 API token 可自動化這一步），設定後才能真正對外瀏覽，見 `docs/SETUP.md`。
