# CHANGELOG — BLACKJ-STOCK-POINT-GUARD

> 每次 `/checkpoint` 追加一筆。本檔為首次執行 checkpoint，故回溯彙整專案啟動以來的全部異動。

---

## 2026-07-04 首次 Checkpoint（回溯彙整 Layer 1 ～ Layer 2 進行中）

- 建立專案骨架：`CLAUDE.md`、`docs/`（design / requirements / decisions）、`.claude/commands/checkpoint.md`
- 完成 Layer 1：`git init` + SSH remote + 初始 push；撰寫並 `launchctl load` 3 個 launchd plist（08:30 / 12:30 / 21:30）；驗證 `claude -p` headless 執行可用
- 撰寫 `job/run_analysis.sh` 作為 launchd 統一入口：無檔案異動不 commit、claude 執行失敗不重試直接結束、找不到 prompt 檔案視為 Layer 2 未完成的預期狀況
- 完成 ADR-001：無人值守排程的工具權限設計，決定採用 `--tools` 硬白名單（`WebSearch,WebFetch,Read,Write,Edit,Glob,Grep`，不含 Bash/Agent）+ `--allowedTools` 將 Write/Edit 限定在 `reports/`、`job/inbox/`，WebFetch 限定信任網域（`tw.stock.yahoo.com`、`finance.yahoo.com`、`www.twse.com.tw`），以降低 prompt injection 情境下的影響範圍
- 撰寫 `job/prompts/{PRE,MID,POST}.md` 三份排程 prompt，皆內含「資料正確性鐵律」（抓不到或矛盾一律標示，禁止捏造）
- 建立 `job/watchlist.json`（4 檔初始關注股）與 `job/inbox/links.md`（YouTube/新聞連結輸入介面，供 21:30 POST 讀取分析）
- 實際執行一次 08:30 PRE 排程：成功產出 `reports/2026-07-04/0830_PRE.md`（完整 A/B/C/D 欄位 + CASH_WARNING）並建立 `reports/state.json`；MID / POST 兩份 prompt 已撰寫但尚未實際執行過
- **發現並修正**：`.claude/scheduled_tasks.lock`（Claude Code CLI 執行期產生的 runtime lock 檔）被 `run_analysis.sh` 的 `git add -A` 誤帶入版控，已補進 `.gitignore` 並 `git rm --cached`
- **發現並修正的流程缺口**：專案啟動以來共 6 次 commit，全部由 `run_analysis.sh` 自動 commit 或手動 commit 完成，從未執行過 `/checkpoint`，導致 `docs/CHANGELOG.md` 不存在、`docs/TODO.md` 未同步實際進度、memory 目錄全空。本次為補做的第一次 checkpoint。

---

## 2026-07-04 排程自動化 commit 與 checkpoint 紀律定案

- 將上一筆記錄的流程缺口（排程自動 commit ≠ 執行過 `/checkpoint`）確認具有通用性，同步升級寫入全域 `~/.claude/universal.md`，新增「排程自動化 commit 與 checkpoint 紀律」章節：判斷 checkpoint 是否做過要看 checkpoint commit / `CHANGELOG.md` 時間戳，不能只看有沒有 commit
- 釐清規則方向：`/checkpoint` 不是「commit 前的必經關卡」，排程腳本（`run_analysis.sh`）的自動 commit 與 `/checkpoint` 各自獨立運作、互不阻擋；`/checkpoint` 步驟 10 的 commit 只是整套流程做完後的收尾動作
- 確認往後對話收尾時的執行方式：不會另外詢問「要不要跑 checkpoint」，因為這已是 CLAUDE.md 訂下的既定規範（依「不問已知規範」原則），改由主動偵測對話收尾訊號後直接執行；若該次對話完全沒有開發異動則略過
- 本次對話本身無程式碼異動（純規範釐清與文件同步），略過 code review
