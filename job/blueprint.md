# Blueprint — JOB（排程分析）（UC-BJSPG 3.5）

> 版本：v0.2 ／ 最後更新：2026-07-04

## 技術棧

| 層 | 技術 |
|---|---|
| 執行引擎 | Claude Code CLI（headless，`claude -p`） |
| 觸發 | macOS `launchd`（3 個 plist） |
| 資料來源 | WebSearch / WebFetch（證交所、Yahoo 奇摩股市、財經新聞等公開頁面） |
| 狀態儲存 | `reports/state.json` |

## 目錄結構

```
job/
├── blueprint.md
├── run_analysis.sh          # launchd 呼叫的統一入口，帶 PRE|MID|POST 參數；含 --tools/--allowedTools 權限限制（見 ADR-001）
├── watchlist.json           # 關注股清單，使用者手動編輯新增/移除標的
├── launchd/                 # plist 原始檔（版控），實際註冊在 ~/Library/LaunchAgents/
│   ├── com.blackjtsai.bjspg.pre.plist   (08:30)
│   ├── com.blackjtsai.bjspg.mid.plist   (12:30)
│   └── com.blackjtsai.bjspg.post.plist  (21:30)
├── prompts/                 # 各時段分析 prompt，皆含「資料正確性鐵律」
│   ├── PRE.md               # 已實際跑過一次並成功產出報告
│   ├── MID.md                # 邏輯已寫完，尚未實際執行過
│   └── POST.md               # 邏輯已寫完，尚未實際執行過
├── inbox/
│   └── links.md             # 使用者手動貼 YouTube/新聞連結，21:30 POST 讀取分析後標記已處理
└── logs/                    # 執行 log，不進版控
```

## 對外介面

無對外 API。輸出為寫入 `reports/{YYYY-MM-DD}/{HHMM}_{PRE|MID|POST}.md` 的 Markdown 檔案，以及更新 `reports/state.json`。

## 當前 Layer 狀態

| Layer | UC 範圍 | 狀態 |
|---|---|---|
| Layer 1 | UC-BJSPG 3.1.2（launchd 排程骨架） | ✅ |
| Layer 2 | UC-BJSPG 3.5.1 ～ 3.5.7（三時段分析邏輯） | ⏳ PRE 已實跑驗證；MID/POST 邏輯已寫完但未實跑 |

## 關鍵業務約束

- 三個時段任務內容不同（見 `docs/requirements/需求.md` 第 4 節），不可共用同一份 prompt 而不區分
- 資料抓不到或多來源矛盾時，必須標示「資料未取得／來源不一致」，禁止用推測值填充
- 每份報告固定包含 `[CASH_WARNING]` 警語，且只給限價建議、不給市價單追價建議
- 回補提示僅根據 `reports/state.json` 記錄的系統自身建議歷史推算，不代表使用者真實持股
