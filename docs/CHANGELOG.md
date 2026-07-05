# CHANGELOG — BLACKJ-STOCK-POINT-GUARD

> 每次 `/checkpoint` 追加一筆。本檔為首次執行 checkpoint，故回溯彙整專案啟動以來的全部異動。

---

## 2026-07-04 手動驗證 MID/POST 邏輯，發現並修正 WebFetch 全市場大表格編造數字風險（ADR-003）

- 手動觸發一次 12:30 `MID` 與 21:30 `POST` 分析邏輯（Layer 2 驗證，非 launchd 正式排程），確認當天（2026-07-04，週六）台股休市、大盤與四檔關注股數據皆與 08:30 `PRE` 報告相同，兩份報告皆如實標示「無新資料」，`state.json` 未更動
- 查詢大聯大(3702) 融資融券時，查詢 TWSE 全市場總表 `MI_MARGN`（未篩選代號）遭截斷，WebFetch 摘要一度回傳格式正確但實際上該股票未出現在畫面內容中的編造數字，與改查 Yahoo 個股頁面取得的正確數字明顯矛盾；換更明確的提示詞（要求「找不到就如實說找不到」）後才確認原數字為編造
- 新增 `docs/decisions/ADR-003-avoid-full-market-table-fetch.md` 記錄此發現與決策：禁止 WebFetch 查詢未篩選代號的全市場總表，一律改用已篩選單一代號的個股頁面查詢
- 同步更新 `docs/design/SDD.md`（第 6.2 節，v0.2→v0.3）、`job/blueprint.md`（v0.4→v0.5）、`job/prompts/{PRE,MID,POST}.md` 的「資料正確性鐵律」段落，補上此規則
- 確認此為工具使用層級的通用經驗（WebFetch 對截斷的大表格有編造風險），非本專案獨有

## 2026-07-04 需求文件與設計文件引用邊界修正（ADR-002）

- 使用者發現 `job/prompts/{PRE,MID,POST}.md` 直接用「第 X 節」引用 `docs/requirements/需求.md` 章節編號，而需求文件會持續改版、章節易位移，屬於脆弱耦合；進一步追問這規範是否該放進設計文件
- 檢查發現同樣寫法還存在於 `CLAUDE.md`、`job/blueprint.md`，共 3 處
- 確認正確做法：`docs/design/SDD.md` 新增第 6 節「核心規則」，把核心原則、資料正確性原則、報告欄位規範、三時段任務差異整理成穩定摘要（衍生自需求.md，需求變更時須人工同步此節）；`CLAUDE.md`、`job/blueprint.md`、三份 job prompts 全部改為引用 `docs/design/SDD.md` 第 6.x 節，不再直接引用 `需求.md` 章節編號
- 在 `CLAUDE.md` 文件資料夾管理規範新增一般性規則：下游程式引用規格內容一律指向 `docs/design/` 衍生文件，不得直接引用 `docs/requirements/` 來源文件的章節編號
- 新增 `docs/decisions/ADR-002-requirements-design-boundary.md` 記錄此決策與取捨（需求變更時 SDD 第 6 節需人工同步，用「明確同步成本」換「隱性耦合風險」）
- 本次為文件與 prompt 引用目標調整，未變動報告產出邏輯或欄位規範本身內容

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
