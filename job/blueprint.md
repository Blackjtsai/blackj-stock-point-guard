# Blueprint — JOB（排程分析）（UC-BJSPG 3.5）

> 版本：v0.14 ／ 最後更新：2026-08-13

## 技術棧

| 層 | 技術 |
|---|---|
| 執行引擎 | Claude Code 雲端 Routines（claude.ai/code agentic session，見 ADR-007） |
| 觸發 | claude.ai/code Routines（`BJSPG-PRE-0800`／`BJSPG-MID-1230`／`BJSPG-POST-2130`，Weekdays）；本機 `launchd`（3 個 plist）＋ `run_analysis.sh` 為原始設計，已停用，見 ADR-007 |
| 資料來源 | WebFetch（證交所、Yahoo 奇摩股市、財經新聞等公開頁面） |
| 狀態儲存 | `reports/state.json`（每檔股票含 `name`／`last_action`／`last_action_time`／`last_report`／`pending_rebuy`／`last_price`／`limit_range`，後兩者為 2026-07-06 新增，見 ADR-005） |

## 目錄結構

```
job/
├── blueprint.md
├── run_analysis.sh          # 【已停用，見 ADR-007】原 launchd 呼叫的統一入口，帶 PRE|MID|POST 參數；含 --tools/--allowedTools 權限限制（見 ADR-001）；claude -p 成功後呼叫 append_continuity_table.py，報告 commit/push 後觸發 web/deploy.sh 更新前台網頁。實際排程已改為雲端 Routines，git commit/push 與呼叫 web/deploy.sh 的責任改寫進各 `prompts/*.md`
├── append_continuity_table.py  # 決定性附加「延續數據表」到報告檔案末尾，讀 state.json + watchlist.json，不假手 LLM 排版（見 ADR-005、SDD 6.5）
├── watchlist.json           # 關注股清單（15 檔），使用者手動編輯新增/移除標的；與 plan.json 代號須一致
├── plan.json                # 個人操盤計劃：每檔波段目標價/回補區間/PG戰術/分組（進版控，非查證值），供 PG Lightbox 儀表板呈現（見 SDD 6.8、ADR-009）；波段目標價可由老大授權以技術面（TWSE/TPEx 日 K 前波高低）代設，標「技術推估非查證」（見 ADR-010）
├── holdings.local.json      # 【本機專用，未進版控，見 .gitignore】真實持股成本價快照，使用者手動維護、排程唯讀，供護盾續抱規則使用（見 SDD 6.6）
├── cash.local.json          # 【本機專用，未進版控，見 .gitignore】現金水庫/防禦底牌，供 PG Lightbox 儀表板頂部；公開頁一律打碼，僅 BJSPG_LOCAL_PREVIEW=1 本機顯真數字（見 SDD 6.8、ADR-009）
├── notify.local.json        # 【本機專用，未進版控，見 .gitignore】ntfy.sh topic 名稱，供排程完成推播通知使用（見 SDD 6.7、ADR-008）
├── notify.sh                 # 排程完成推播通知，雲端 Routine 與本機備援共用實作（2026-08-11 新增，見 SDD 6.7、ADR-008）
├── launchd/                 # 【已停用，見 ADR-007】plist 原始檔，原註冊在 ~/Library/LaunchAgents/，僅存檔案作歷史紀錄
│   ├── com.blackjtsai.bjspg.pre.plist   (平日 08:00)
│   ├── com.blackjtsai.bjspg.mid.plist   (平日 12:30)
│   └── com.blackjtsai.bjspg.post.plist  (平日 21:30)
├── prompts/                 # 各時段分析 prompt，餵給雲端 Routines 執行；皆含「資料正確性鐵律」與「版本控制」段落（自行 git commit/push + web/deploy.sh，失敗即結束不重試，見 ADR-007）；只需把 last_price/limit_range 寫進 state.json，延續數據表由 append_continuity_table.py 決定性附加，不需自己排版；2026-08-13 補 PG 語氣強化/Zero Noise（缺資料隱藏 B 段、聚焦 3~5 檔）/波段目標價僅取 plan.json/報告末尾附 Lightbox 按鈕（見 SDD 6.3、6.8、ADR-009）
│   ├── PRE.md               # 已實際跑過（含 2026-07-06 正式交易日排程），計算完限價後寫回 state.json 的 last_price/limit_range；2026-08-10 新增排程完成通知步驟（見 SDD 6.7）
│   ├── MID.md                # 已於 2026-07-04 手動驗證執行一次（休市無新資料），正式交易日情境待 Layer 4；2026-08-10 新增排程完成通知步驟
│   └── POST.md               # 2026-07-06 21:30 正式交易日執行遇雲端 sandbox 網路故障，報告遺失（見 ADR-007），正式交易日情境待 Layer 4 重新驗證；2026-08-10 新增排程完成通知步驟
├── inbox/
│   └── links.md             # 使用者手動貼 YouTube/新聞連結，21:30 POST 讀取分析後標記已處理
├── run_analysis_local_backup.sh  # 本機臨時備援排程入口（見 docs/SETUP.md）；2026-08-11 修訂：git commit 確認成功才視為有新異動（修正誤發推播風險），push 成功後呼叫 job/notify.sh 推播（不假手 claude，因該路徑 `--allowedTools` 未授權 Bash，見 ADR-008）
└── logs/                    # 執行 log，不進版控
```

## 對外介面

無對外 API。輸出為寫入 `reports/{YYYY-MM-DD}/{HHMM}_{PRE|MID|POST}.md` 的 Markdown 檔案，以及更新 `reports/state.json`。

## 當前 Layer 狀態

| Layer | UC 範圍 | 狀態 |
|---|---|---|
| Layer 1 | UC-BJSPG 3.1.2（排程骨架，現為雲端 Routines，見 ADR-007） | ✅ |
| Layer 2 | UC-BJSPG 3.5.1 ～ 3.5.7（三時段分析邏輯） | ⏳ PRE 已於 2026-07-04（手動）與 2026-07-06（正式交易日）各實跑一次；MID 僅手動驗證過休市情境；POST 於 2026-07-06 21:30 正式交易日執行時遇雲端 sandbox 網路故障，報告遺失（見 ADR-007），正式交易日情境待 Layer 4 全面重新驗證 |

## 關鍵業務約束

- 三個時段任務內容不同（見 `docs/design/SDD.md` 第 6.4 節），不可共用同一份 prompt 而不區分
- 資料抓不到或多來源矛盾時，必須標示「資料未取得／來源不一致」，禁止用推測值填充
- 個股報價主來源＝ TWSE MIS 官方 API（Bash curl 批次 + python 解析，省 token 零幻覺），WebFetch Yahoo 為 fallback；日 K 前波高低用 TWSE STOCK_DAY／TPEx tradingStock（見 SDD 6.2、ADR-010）。報價與「籌碼數據」分開：籌碼仍走個股頁
- 查詢 TWSE 融資融券／三大法人資料時，禁止查未篩選代號的全市場總表（`MI_MARGN`、`T86`、`TWT44U` 整份清單，實測不支援單一代號篩選），一律改用個股專屬頁面查詢，主來源失敗時改查第二個個股專屬來源，**兩者皆失敗也只能標示「資料未取得」，任何情況下都不得回退查詢全市場總表**（見 `docs/design/SDD.md` 第 6.2 節、ADR-003）
- 報告提及除權除息日期／股利數字，必須先用 TWSE 官方除權除息預告表 API 查證，禁止憑訓練知識或沿用舊報告數字斷言（見 `docs/design/SDD.md` 第 6.2 節）
- 每份報告固定包含 `[CASH_WARNING]` 警語，且只給限價建議、不給市價單追價建議
- 回補提示僅根據 `reports/state.json` 記錄的系統自身建議歷史推算，不代表使用者真實持股；但 `holdings.local.json` 有記錄的代號，其「高位停利變現」建議時機另受護盾續抱規則約束（見 `docs/design/SDD.md` 第 6.6 節），兩者不衝突：前者是回補提示的資料來源限制，後者是停利建議本身的節流閥
- 排程觸發改為 claude.ai/code 雲端 Routines（`BJSPG-PRE-0800`／`BJSPG-MID-1230`／`BJSPG-POST-2130`，Weekdays），僅平日觸發；本機 `launchd`（3 個 plist，`StartCalendarInterval` 皆為 Weekday 1～5 陣列）為原始設計，已停用（見 ADR-007）
- git commit/push 失敗（含網路錯誤、GitHub App 權限不足等）時，Routine 必須直接結束，不重試、不深入除錯（見 ADR-007），避免佔用大量 tool call 卡在原地
- 排程完成通知（ntfy.sh，見 SDD 6.7、ADR-008）只在真的產生新 commit 且 push 成功時才發送；`job/notify.local.json` 不存在時直接跳過，不視為錯誤；雲端 Routine 因該檔案未進版控、沙盒內不存在，實際上只有本機備援路徑會真的推播，此為已知且接受的行為
