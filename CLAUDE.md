# BLACKJ-STOCK-POINT-GUARD — 專案規範 (CLAUDE.md)

---

# 一、通用規範

## Claude 行為規範（Karpathy Coding Guidelines）

- **Think Before Coding**：有假設或模糊地帶，先說出來對齊，不要默默實作
- **Simplicity First**：只寫解決當前問題最少的程式碼，不預留「未來可能用到」的抽象
- **Surgical Changes**：只動必要的地方，不順手重構周邊不相關的程式碼
- **Goal-Driven Execution**：每個任務完成前，先定義可驗證的成功標準，達到才繼續

## 不問已知規範

有合理預設答案時直接執行，不問。只有在真正有歧義且無法從上下文推斷時才提問。

## 文件資料夾管理規範

- `docs/design/` — 設計類（需求分析、SDD、架構等規劃文件）
- `docs/requirements/` — 需求來源（原始需求文件、優化指示文件）
- **滾動式調整**：資料夾結構不清楚時，自動提醒使用者討論調整，不自行亂動

### 為什麼不用單一 CONTEXT.md

「專案 context」刻意依讀者情境拆分到不同文件（`ARCHITECTURE.md` 現況、ADR 決策原因、`TODO.md` 進度、`TASK.md` 驗收條件），而非集中成一份 CONTEXT.md——好處是各司其職、邊界清楚，代價是抓全貌要讀多份，靠下方「專案開場問候規範」的固定組裝順序補回。此為 **BlackJ-Tsai 工作流** 的核心精神，詳見全域 `universal.md`。

## 檔案異動盤查規範

資料夾或檔案位置變動時，主動盤查：Import 路徑、設定檔引用、CLAUDE.md 目錄結構區塊、測試路徑。
異動影響超過 1 個檔案時，先列受影響清單讓使用者確認，再動手。

## 自動記憶規範

- **錯誤經驗**：對話中發生錯誤或誤判，立即寫入專案 memory 目錄，類型 `feedback`
- **系統藍圖**：實作新模組前，必須先產出或更新 `ARCHITECTURE.md` 的 Mermaid 架構圖
- **經驗性討論**：對話中出現架構取捨、設計決策分析類的討論，該段落告一段落時主動詢問是否保存
- **通用規範升級**：若某項設計決策判斷不限於本專案、具通用性，主動詢問是否同步更新到全域 `universal.md`

## Todo 管理規範

- **唯一來源**：進度以 `docs/TODO.md` 為準，不以記憶體或 TodoWrite 工具為準
- 每個 Layer 開始前，先在 `docs/design/TASK.md` 列出驗收條件，再在 `docs/TODO.md` 展開細項，再動手
- **TASK.md gate**：`docs/TODO.md` 出現新 Layer，但 `docs/design/TASK.md` 無對應條目 → 停下來，先補寫 TASK.md，使用者確認後才繼續
- 每完成一項，立即更新 `docs/TODO.md`（`[ ]` → `[x]`），不批次更新
- 上一 Layer 所有項目 `[x]` 才能開新 Layer
- TodoWrite 工具只用於當前對話同步顯示，以 `docs/TODO.md` 為準

## 專案開場問候規範

使用者輸入 `hi` / `Hi` / `HI` 時，依序執行：

0. **環境檢查** — 讀取 `docs/SETUP.md`，逐項列出就緒 ✅ / 未完成 ❌
1. **打招呼** — 問候使用者，開頭加一行標籤：「（本專案採用 BlackJ-Tsai 工作流）」
2. **專案任務說明** — 一段話說明此專案的目的與階段
3. **Claude 技能清單** — 列出目前可執行的任務，固定包含 `/checkpoint`（每次對話結束前執行）
4. **目前進度** — 讀取 `docs/TODO.md`，對照 `docs/design/ARCHITECTURE.md` 的 Layer 驗收表
5. **可對外服務** — 說明哪些報告 / 前台頁面目前已可使用

## 程式碼註解規範

每支程式碼檔案（空白佔位檔除外）都必須包含：

**1. 檔案 header（最頂端）**

```
# ============================================================
# 檔案名稱：xxx
# 中文名稱：（繁體中文說明）
# 功能說明：（一行說清楚此檔的職責）
# 所屬模組：（對應的模組或資料夾）
# 建立日期：YYYY-MM-DD
# 修改日期：YYYY-MM-DD
# 開發者　：（開發者名稱）
# ============================================================
```

**2. 每個函式 / 方法的說明**：一行說明「做什麼、回傳什麼、特殊條件」，不重複函式名已說明的事。

## 測試規範（Error Path）

本專案沒有傳統意義上的單元測試套件（核心邏輯是 Claude Code 於排程時即席分析，非固定演算法）。驗收改以 **Layer 4 端對端整合測試** 取代：實際跑三個排程時間點，確認報告產出、狀態檔更新、git push、前台顯示皆正確，並涵蓋以下 error path：

1. 資料抓不到 / 來源矛盾 → 報告該欄位明確標示「資料未取得」，不得捏造數字
2. 排程觸發時電腦未開機／未登入 → 該次排程直接跳過，不重試不報錯
3. 排程觸發時 Claude 訂閱用量不足 → 該次排程失敗即結束，不重試

## 資料表設計規範

**不適用**。本專案不使用資料庫，資料僅以 Markdown 報告檔（`reports/`）與一份輕量狀態檔（`reports/state.json`）儲存。

---

# 二、業務邏輯規範

## 專案快照

**BLACKJ-STOCK-POINT-GUARD（黑暗傑客股市控球後衛，代號 BJSPG）**
個人使用的台股現股買賣建議輔助系統。本機排程於每日固定時間點呼叫 Claude Code 分析公開市場資料，產出買賣建議報告，並透過靜態網頁前台瀏覽歷史紀錄。不連接券商、不自動下單，所有決策由使用者本人執行。

參考文件：
- `docs/design/SDD.md` — 系統設計說明書（含 UC 清單）
- `docs/design/TASK.md` — 各 Layer 驗收條件
- `docs/requirements/需求.md` — 需求規格（最新版）

## 技術棧

| 層 | 技術 |
|---|---|
| 執行引擎 | Claude Code CLI（headless，`claude -p`），使用者自己的訂閱額度 |
| 排程 | macOS `launchd`（3 個 plist：08:30 / 12:30 / 21:30） |
| 資料儲存 | Markdown 報告檔 + `reports/state.json` |
| 前台 | 純 HTML / CSS / 少量原生 JS，無框架，RWD |
| 版控與部署 | Git + GitHub Pages |
| GitHub Repo | https://github.com/Blackjtsai/blackj-stock-point-guard.git（Public） |

## 必備技能

- `/checkpoint` — **必備**，每次對話結束前執行（commit + push + 累積開發經驗）
- `/checkservice` — 本專案無需。沒有常駐 Web server / DB / Queue，`launchd` 排程註冊一次後自行觸發，就緒狀態直接查 `docs/SETUP.md`

## 實作順序（嚴格遵守，未驗收不動下一層）

| Layer | 名稱 | UC 範圍 |
|---|---|---|
| Layer 1 | 環境建置與排程骨架 | UC-BJSPG 3.1.1 ～ 3.1.3 |
| Layer 2 | 分析與報告產出邏輯 | UC-BJSPG 3.5.1 ～ 3.5.6 |
| Layer 3 | 前台 Dashboard | UC-BJSPG 3.2.1 ～ 3.2.3 |
| Layer 4 | 端對端整合測試 | 全部 UC |

## 開發慣例

### UC 編號規範

格式：`UC-BJSPG {大類}.{子層}.{子子層}`

| 大類 | 類別 |
|---|---|
| 3.1 | 基礎建設 |
| 3.2 | WEB（前台） |
| 3.5 | JOB（排程分析） |

- UC 清單完整定義在 `docs/design/SDD.md` 的 `## UC 清單` 章節
- commit message 格式：`feat: UC-BJSPG {大類}.x.x [功能名稱]`
- 跨 UC 引用格式：`呼叫 [UC-BJSPG {大類}.x.x]`

### 報告產出規則（核心業務邏輯）

- 每次排程執行必須依 `docs/requirements/需求.md` 第 7 節欄位規範（A 總經底座 / B 個股籌碼表 / C 建議動作 / D 資金警語與回補提示）產出 Markdown 報告
- 報告檔名固定格式：`reports/{YYYY-MM-DD}/{HHMM}_{PRE|MID|POST}.md`
- 資料抓不到或多來源矛盾時，該欄位標示「資料未取得／來源不一致」，禁止用推測值或記憶中的舊數字填充
- 每份報告固定包含 `[CASH_WARNING]` 警語

## 關鍵業務約束

- 不碰選擇權，只做現股部位判斷
- 不連接券商 API，不追蹤真實庫存與真實 T+2 交割款，所有建議僅供參考
- 不自動下單，只出建議
- 只給限價（Limit Order）建議，不給市價單追價建議
- GitHub repo 為 Public，且股票代號不做隱碼處理（使用者已確認接受此取捨）

## 測試規範（專案特有）

繼承通用測試規範（上方第一部分）。Layer 4 端對端整合測試為主要驗收手段，見上方「測試規範（Error Path）」三條 error path。

## 專案目錄結構

```
blackj-stock-point-guard/
├── CLAUDE.md
├── .gitignore
├── .claude/
│   └── commands/
│       └── checkpoint.md
├── docs/
│   ├── INTRO.md
│   ├── TODO.md
│   ├── SETUP.md
│   ├── requirements/       # 需求來源文件
│   │   ├── 需求.md
│   │   ├── 需求-原始構想.md
│   │   └── 優改.md
│   ├── design/
│   │   ├── ARCHITECTURE.md
│   │   ├── TASK.md
│   │   └── SDD.md
│   └── decisions/
│       └── ADR-000-template.md
├── job/
│   └── blueprint.md        # 排程分析邏輯（UC-BJSPG 3.5）
├── web/
│   └── blueprint.md        # 前台 Dashboard（UC-BJSPG 3.2）
└── reports/                # Layer 2 開始後才產生，報告與 state.json
```
