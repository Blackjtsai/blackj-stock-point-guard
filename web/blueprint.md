# Blueprint — WEB（前台 Dashboard）（UC-BJSPG 3.2）

> 版本：v0.4 ／ 最後更新：2026-07-06

## 技術棧

| 層 | 技術 |
|---|---|
| 框架 | 無（純 HTML/CSS，無 JS） |
| 樣式 | 手寫 CSS，RWD（flexbox，表格 `overflow-x:auto`，支援淺色/深色模式） |
| 建置 | `web/build.py`（純 Python 標準函式庫，不依賴 pandoc/pip 套件），掃描 `reports/*.md` 轉出靜態 HTML |
| 部署 | `web/deploy.sh` → 獨立 `gh-pages` orphan branch → GitHub Pages 從該 branch root 發布 |

## 目錄結構

```
web/
├── blueprint.md
├── build.py     # Markdown → HTML 轉換 + 產生 index.html（UC-BJSPG 3.2.1/3.2.2）
└── deploy.sh    # build 後 push 到 gh-pages branch（UC-BJSPG 3.2.3）
```

輸出（部署到 `gh-pages` branch，不進 `main`）：

```
index.html                       # 首頁，依日期新到舊列出報告連結
{YYYY-MM-DD}/{HHMM}_{TYPE}.html  # 各報告轉出的頁面
```

## 對外介面

| 路由 | 說明 |
|---|---|
| 首頁 | 依日期列出已產出報告（PRE/MID/POST），簡單列表，最新在最上 |
| 報告頁 | 單篇報告轉出的 HTML，含「回首頁」連結；上方另有「📊 重點摘要」按鈕 |

## 重點摘要 lightbox（2026-07-06 新增）

- 純 CSS checkbox-hack 實作（隱藏 checkbox + label 觸發），維持「無 JS」設計原則
- 內容來源：該報告自己的「建議動作彙整表」（代號/名稱/建議動作/備註）+「延續數據表」（收盤價/第一批限價，見 SDD.md 6.5、ADR-005）
- 擷取邏輯（`web/build.py`）：`extract_stock_summary()` 找建議動作彙整表；`extract_continuity_table()` 優先找新格式延續數據表；找不到（相容 2026-07-04 尚未套用 6.5 規範的舊報告）才 fallback 到 `extract_stock_detail()` 逐段落最佳猜測擷取
- 建議動作徽章顏色：金字塔低接＝綠、觀望看戲＝灰、高位停利變現＝紅
- 資料完全來自該報告自己的已寫死文字內容，不讀即時的 `reports/state.json`（避免歷史頁面重建時被之後的狀態覆寫，見 ADR-005）；擷取不到的欄位一律省略，不臆測填值

## 部署機制

- `job/run_analysis.sh` 每次報告 commit/push 後自動呼叫 `web/deploy.sh`
- `web/deploy.sh` 用獨立 git worktree（`.gh-pages-worktree/`，已 gitignore）操作 `gh-pages` branch，不影響 `main` 的工作目錄
- `gh-pages` 為 orphan branch（與 `main` 無共同歷史），只含建置後的靜態檔案，因此與 `docs/`（專案文件）不衝突
- 詳見 `docs/design/ARCHITECTURE.md` 的「前台網頁部署機制」章節

## 當前 Layer 狀態

| Layer | UC 範圍 | 狀態 |
|---|---|---|
| Layer 3 | UC-BJSPG 3.2.1 ～ 3.2.3 | ✅ 已上線：https://blackjtsai.github.io/blackj-stock-point-guard/ |

## 關鍵業務約束

- 不做日曆選擇器，維持簡單列表
- 不需要新報告通知機制
- GitHub repo 為 Public，股票代號不隱碼，直接顯示真實代號/名稱
- Markdown 轉換僅支援本專案報告實際會用到的語法（標題、粗體、行內反引號、表格、清單、blockquote、水平線），不追求通用 Markdown 相容性
