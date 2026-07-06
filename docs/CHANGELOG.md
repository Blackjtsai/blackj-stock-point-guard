# CHANGELOG — BLACKJ-STOCK-POINT-GUARD

> 每次 `/checkpoint` 追加一筆。本檔為首次執行 checkpoint，故回溯彙整專案啟動以來的全部異動。

---

## 2026-07-06 護盾續抱規則（ADR-006）與資料查證流程補強，查核 0800_PRE 報告優化指示

- 使用者對 0800_PRE 報告提出三點優化指示：(1) 質疑英業達(2356) 除息日/股利數字為幻覺 (2) 要求對真實持股套用「成本護盾」邏輯避免短線散戶思維過早停利 (3) 質疑大聯大(3702) 法人數據又缺失、要求補 TWSE T86 備援。逐項查核後動手實作，過程中修正了使用者的兩個錯誤前提，未盲目照單全收：
  - **(1) 查核結果：不是幻覺**。直接 curl TWSE 官方除權除息預告表 API（`https://www.twse.com.tw/rwd/zh/exRight/TWT48U?response=json`）驗證，2356 確實登記 115/07/15 除息、現金股利 2.00 元，與報告一致。但排程流程本身沒有查證步驟，這次只是剛好蒙對，屬於流程缺口而非結果錯誤——已補上正式查證步驟。
  - **(3) 查核結果：不是本次報告的問題**。翻歷史報告確認「上緯投控」誤標事件發生在 2026-07-04，當天 21:30 POST 報告已修復；2026-07-06 報告本身法人數據是完整的。使用者提議的「T86 備援」方向也證實不可行：實測 `T86`（`selectType` 僅接受預設分類值）與 `TWT44U`（`stockNo` 參數對回傳內容無效）皆不支援單一代號篩選，改用等於重踩 ADR-003 已修好的坑；改為明訂備援順序為 Yahoo 個股頁 → `finance.yahoo.com` 個股頁 → 才標示「資料未取得」，任何情況不得退回全市場總表。
  - **(2) 查核結果：方向合理，但需使用者決定兩件事**——用 `AskUserQuestion` 確認：3702 真實成本價是 $110（沿用 2026-07-06 券商截圖 memory）而非訊息中提到的 $106.75；真實成本價存放位置選「本機、不進版控」而非寫進 Public repo（該 repo 已公開股票代號，但使用者不接受成本/未實現損益也公開）。
- 新增 `job/holdings.local.json`（`.gitignore` 排除，不進版控）存放真實持股成本快照；新增 `docs/design/SDD.md` 第 6.6 節「護盾續抱規則」：安全墊 `(現價-cost_basis)/cost_basis ≥5%` 時 C 段預設不給「高位停利變現」，除非大盤系統性崩盤（TWII 單日跌幅≥3% 或 SOX 單日重挫≥5% 且台股同步走弱）；6.2 節新增除權息官方查證來源與法人數據備援順序（禁止退回全市場總表）
- 新增 `docs/decisions/ADR-006-cost-basis-shield-rule.md` 完整記錄決策脈絡；`docs/decisions/ADR-003-avoid-full-market-table-fetch.md` 追記 T86/TWT44U 不支援單一代號篩選的實測結果，回答當初留下的開放問題
- 同步更新 `job/blueprint.md`（v0.8→v0.9）、`job/prompts/{PRE,MID,POST}.md`、`docs/design/ARCHITECTURE.md`（Mermaid 圖與資料 Schema 新增 `holdings.local.json`）、`docs/TODO.md`（新增待驗證項目、遷移常駐機器待辦補一項）
- 尚未驗證：這些規則要等下一次排程實跑（08:00/12:30/21:30）才能確認 LLM 是否真的照做，已在 `docs/TODO.md` 標記

## 2026-07-06 重點摘要 lightbox + 延續數據表機制（ADR-005），修正 dark mode CSS bug

- 使用者反映前台報告頁面 dark mode 對比度差、看不清楚；追查發現根因是 CSS 撰寫順序 bug：`@media (prefers-color-scheme: dark)` 覆寫區塊寫在對應淺色樣式「之前」，同優先權下被後面的淺色規則蓋掉，導致 `blockquote` 等元素的深色覆寫從未真正生效。修正為統一移到 CSS 檔案最後，並用 Playwright 實際截圖驗證 light/dark 兩種模式皆正常
- 新增每份報告頁面的「📊 重點摘要」按鈕（純 CSS checkbox-hack，維持無 JS 設計），跳出 lightbox 列出關注股卡片：代號/名稱、建議動作徽章（金字塔低接＝綠／觀望看戲＝灰／高位停利變現＝紅）、收盤價、第一批限價
- 發現 08:30 PRE 報告資料完整，但 12:30 MID 缺限價區間、21:30 POST 連股價都沒有；使用者確認要修，選擇「擴充 `state.json`」而非「直接讀即時狀態」（後者會讓 `build.py` 每次全量重建歷史頁面時被之後的狀態覆寫，等同竄改歷史紀錄）
- **執行高強度（high）code review 時，8 角度之一（altitude）指出更根本的問題**：原設計讓無人值守的 headless LLM 自己在報告內文手寫「延續數據表」，屬於純機械轉錄工作卻交給格式可靠度最低的環節負責，格式一旦漂移 `web/build.py` 就會抓錯或抓不到，且無錯誤訊號——與 ADR-001「git commit/push 不假手 claude」是同一類風險，但當初沒有把這個原則延伸到報告格式本身
- 修正：新增 `job/append_continuity_table.py`（純 Python 決定性腳本），由 `job/run_analysis.sh` 在 `claude -p` 執行完、`git commit` 前呼叫，讀 `reports/state.json` + `job/watchlist.json` 決定性產出「延續數據表」（人讀 Markdown 表格 + 機器可讀 `<!-- BJSPG_CONTINUITY: {json} -->` 註解），LLM 只需把 `last_price`/`limit_range` 寫進 `state.json`，不用自己排版；`web/build.py` 改用 `json.loads()` 直接解析該註解，不再靠正則猜測表格內容，並修正 `markdown_to_html()` 讓單行 HTML 註解不會顯示在頁面上
- Code review 另找出並修復：3 處表格解析邏輯重複（抽出 `parse_pipe_rows`/`find_pipe_table` 共用函式）、`web/build.py` 檔頭修改日期未同步更新
- **意外插曲**：撰寫過程中，2026-07-06（週一，正式交易日）08:00 的 launchd PRE 排程真的觸發了，其 `run_analysis.sh` 的 `git add -A` 把當時尚在進行中的所有編輯（含本次的架構修訂）連同真實報告一起打包進自動 commit `4dcefdb`（訊息看起來只是例行報告 commit，實際內容涵蓋整個 ADR-005 修訂）；確認已 push 到 `origin/main` 不宜 amend，故不重新 commit 同一批異動，僅將後續補充（回填今日報告的延續數據表、文件同步）另開新 commit。這也是「排程自動 commit ≠ 執行過 `/checkpoint`」規範的又一個實例
- 用最終版腳本回填今天真實的 `reports/2026-07-06/0800_PRE.md`，補上延續數據表（資料取自當時已寫入 `state.json` 的真實查證數字，非杜撰），重新 `web/deploy.sh` 部署並以 curl／raw GitHub 內容確認正確
- `docs/design/SDD.md` 6.5 節同步修訂為最終機制（v0.7→v0.8），`ADR-005` 補上修訂記錄段落，`job/blueprint.md`、`web/blueprint.md` 同步更新

## 2026-07-05 Layer 3 前台 Dashboard 實作（跳過 Layer 2 gate，ADR-004）

- 使用者確認 Layer 2 手動驗證已足夠，指示跳過「上一 Layer 全部 `[x]` 才能開新 Layer」的 gate，直接開始 Layer 3（UC-BJSPG 3.2.1 ～ 3.2.3）
- 新增 `web/build.py`：純 Python 標準函式庫（不依賴 pandoc/pip 套件）掃描 `reports/*.md`，轉出靜態 HTML 首頁列表與各報告頁，RWD + 深色模式；已用 2026-07-04 三份既有報告本機測試通過
- 新增 `web/deploy.sh`：build 後用獨立 git worktree（`.gh-pages-worktree/`，已加入 `.gitignore`）操作獨立的 `gh-pages` orphan branch，commit + push；已本機測試成功，`gh-pages` branch 已建立並 push 到 GitHub
- `job/run_analysis.sh` 在報告 commit/push 後新增一行呼叫 `web/deploy.sh`，讓每次排程執行完自動更新前台網頁
- 新增 `docs/decisions/ADR-004-github-pages-deploy-path.md`：定案 GitHub Pages 部署路徑為「本機腳本 + 獨立 gh-pages branch」，不用 GitHub Actions，解決 `docs/` 已作專案文件用途與 GitHub Pages 原生設定路徑衝突的問題
- 確認本機沒有 `gh` CLI 或 API token，GitHub Pages 的「Settings → Pages → Source」無法自動化，需使用者手動設定一次（已寫入 `docs/SETUP.md`），設定前網頁尚無法對外瀏覽
- 同步更新 `docs/design/SDD.md`（UC-BJSPG 3.2.1/3.2.2 完成、3.2.3 定案，v0.3→v0.4）、`docs/design/ARCHITECTURE.md`（Mermaid 圖新增 `gh-pages` 部署路徑、待確認事項改寫為已定案機制）、`web/blueprint.md`（v0.1→v0.2）、`job/blueprint.md`（v0.5→v0.6，補上 web deploy 觸發與 MID/POST 已驗證狀態）、`docs/TODO.md`
- **Code review（medium，8 角度平行）發現並修復 7 項問題**：(1) `web/deploy.sh` 建立 orphan branch 時 `git checkout --orphan &amp;&amp; git rm -rf .` 若前半失敗會靜默留下 main 全樹內容並被後續 commit/push 到公開 gh-pages branch，改為顯式檢查失敗並清掉損毀的 worktree；(2)(3) `job/run_analysis.sh` 呼叫 `web/deploy.sh` 原本不檢查 exit status、也不管報告 `git push` 是否成功就無條件部署，改為 push 失敗時略過部署、deploy 失敗時記錄明確錯誤訊息；(4) `web/deploy.sh` 的 `git push origin gh-pages` 與 `python3 build.py` 原本都不檢查結果，改為失敗即記錄並中止，不繼續 commit/push 半成品；(5) `web/build.py` 的 `find_reports()` 在 `reports/` 不存在時會丟未捕捉的 `FileNotFoundError`，改為視為「尚無報告」回傳空清單；(6) `render_table()` 資料列欄位數與表頭不符時（如儲存格內含 `|` 字元）會造成欄位錯位，改為自動補齊/截斷對齊表頭；(7) `web/build.py` 6 個函式皆缺少 CLAUDE.md 規定的一行 docstring，已全數補上。全部修復後重新以本機 build+deploy 驗證正常運作，未發現回歸

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
