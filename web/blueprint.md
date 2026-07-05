# Blueprint — WEB（前台 Dashboard）（UC-BJSPG 3.2）

> 版本：v0.3 ／ 最後更新：2026-07-05

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
| 報告頁 | 單篇報告轉出的 HTML，含「回首頁」連結 |

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
