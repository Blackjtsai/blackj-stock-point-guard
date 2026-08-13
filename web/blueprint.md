# Blueprint — WEB（前台 Dashboard）（UC-BJSPG 3.2）

> 版本：v0.6 ／ 最後更新：2026-08-13

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
| 首頁 | 依日期列出已產出報告（PRE/MID/POST），簡單列表，最新在最上；含常駐 PG Lightbox 儀表板按鈕 |
| 報告頁 | 單篇報告轉出的 HTML，含「回首頁」連結；上方另有「📊 重點摘要」與「🔍 PG 股票回補與關注 Lightbox 儀表板」按鈕 |

## 重點摘要 lightbox（2026-07-06 新增，同日修訂擷取機制）

- 純 CSS checkbox-hack 實作（隱藏 checkbox + label 觸發），維持「無 JS」設計原則
- 內容來源：該報告自己的「建議動作彙整表」（代號/名稱/建議動作/備註）+ `job/append_continuity_table.py` 決定性附加的「延續數據表」（收盤價/第一批限價，見 SDD.md 6.5、ADR-005）
- 擷取邏輯（`web/build.py`）：`extract_stock_summary()` 找建議動作彙整表；`extract_continuity_table()` 直接 `json.loads()` 解析附加在報告末尾的 `<!-- BJSPG_CONTINUITY: {...} --> ` 機器可讀註解；找不到（相容尚未套用此機制的舊報告）才 fallback 到 `extract_stock_detail()` 逐段落最佳猜測擷取
- 建議動作徽章顏色：金字塔低接＝綠、觀望看戲＝灰、高位停利變現＝紅
- 資料完全來自該報告自己的已寫死文字內容，不讀即時的 `reports/state.json`（避免歷史頁面重建時被之後的狀態覆寫，見 ADR-005）；擷取不到的欄位一律省略，不臆測填值
- `markdown_to_html()` 會略過單行 HTML 註解（`<!-- ... -->`），所以機器可讀的 JSON 註解不會顯示在頁面上

## PG 股票回補與關注 Lightbox 儀表板（2026-08-13 新增，見 SDD.md 6.8、ADR-009）

- 純 CSS checkbox-hack 實作（獨立於「重點摘要」的第二組 toggle：`pg-toggle`），維持「無 JS」原則；每份報告頁與首頁都掛「🔍 開啟 PG 股票回補與關注 Lightbox 儀表板」按鈕
- `render_pg_dashboard(project_dir)` 三資料源：`job/plan.json`（目標價/回補區間/PG戰術/分組，非查證計劃值）、`reports/state.json`（`last_price` live 現價、建議動作）、`job/cash.local.json`（現金水庫，本機專用）
- 「參考價」優先取 state.json 的 `last_price`，缺才 fallback plan.json 的 `ref_price`；15 檔依 `group` 分兩組（待回補功臣股／平價戰隊）出表
- **隱私閘門**：`_mask_amount()` 對現金/持股金額預設打碼（`NT$ ●●●,●●●`），僅環境變數 `BJSPG_LOCAL_PREVIEW=1` 時渲染真數字；`web/deploy.sh` 不設此旗標，確保公開產物永遠打碼
- 與「重點摘要 lightbox」不同：重點摘要讀「該報告自己寫死的文字」；PG 儀表板讀「專案當下的 plan.json/state.json/cash.local.json」——是全景操盤計劃，非單日快照，故各歷史頁面呈現的是建置當下的最新計劃（可接受，屬全景性質）

## 部署機制

- `job/run_analysis.sh` 每次報告 commit/push 後自動呼叫 `web/deploy.sh`
- `web/deploy.sh` 用獨立 git worktree（`.gh-pages-worktree/`，已 gitignore）操作 `gh-pages` branch，不影響 `main` 的工作目錄
- `gh-pages` 為 orphan branch（與 `main` 無共同歷史），只含建置後的靜態檔案，因此與 `docs/`（專案文件）不衝突
- 詳見 `docs/design/ARCHITECTURE.md` 的「前台網頁部署機制」章節

## 當前 Layer 狀態

| Layer | UC 範圍 | 狀態 |
|---|---|---|
| Layer 3 | UC-BJSPG 3.2.1 ～ 3.2.3 | ✅ 已上線：https://blackjtsai.github.io/blackj-stock-point-guard/ |
| Layer 5 | SDD 6.8、ADR-009（PG Lightbox 儀表板） | ⏳ 實作完成，待排程實跑驗證現價帶入與打碼 |

## 關鍵業務約束

- 不做日曆選擇器，維持簡單列表
- 前端本身不需要內建通知 UI（無 bell icon / toast）；**外部推播通知**（排程完成後手機收到提醒）改由 `job/` 負責，見 `job/blueprint.md`、SDD.md 6.7、ADR-008（2026-08-10 新增，推翻本行原「不需要新報告通知機制」的舊決策）
- GitHub repo 為 Public，股票代號不隱碼，直接顯示真實代號/名稱；但**真實現金水位/持股金額屬敏感資訊，公開頁一律打碼**（見 PG 儀表板隱私閘門、ADR-009）
- Markdown 轉換僅支援本專案報告實際會用到的語法（標題、粗體、行內反引號、表格、清單、blockquote、水平線），不追求通用 Markdown 相容性
