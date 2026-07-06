# ADR-005：延續股價與限價區間資料 — 擴充 state.json，不改 build.py 讀即時狀態

> 狀態：已採納
> 日期：2026-07-06
> 決策者：黑暗傑客（Eason Tsai）／Claude Code

## 背景

Layer 3 新增前台「重點摘要」lightbox 後（見 `web/build.py` 的 `render_summary_modal`），使用者發現只有 08:30 PRE 報告的摘要卡片有完整的收盤價與金字塔限價區間，12:30 MID 報告只有價格沒有限價區間，21:30 POST 報告兩者都沒有。根本原因是報告內容本身：PRE 會完整計算並寫出這兩項數據，MID 只複核不重算，POST 的籌碼表甚至不含股價欄位。

使用者希望三種報告類型的重點摘要都能穩定顯示這兩項數據，並請我提出設計方向。

## 選項

| 選項 | 優點 | 缺點 |
|---|---|---|
| A. `web/build.py` 直接讀取「當下的」`reports/state.json`（即時狀態）作為所有報告頁面的資料來源 | 實作最簡單，不用改 job prompts | **會破壞歷史正確性**：`build.py` 每次 `deploy.sh` 執行都會重建全部歷史頁面（見效率面的既有設計），若都讀「當下」的 `state.json`，隔天 PRE 一覆寫，昨天所有報告頁面重建時會被灌入「今天」的數字，等於竄改了已發佈報告的歷史內容 |
| B. 擴充 `reports/state.json` 新增 `last_price`／`limit_range` 欄位，MID/POST 的 prompt 讀取後**寫進該次報告自己的 Markdown 內文**（新增「延續數據表」區塊），`build.py` 繼續只讀每份報告自己的文字內容 | 每份報告的 HTML 永遠對應「當時寫入該報告檔案的文字」，重建歷史頁面時內容不變，正確性不受影響；同時 `state.json` 只是 job 端「轉述用」的資料來源，不是前台的即時資料源 | 需要修改三份 job prompts 與 SDD 6.3 報告欄位規範，範圍比選項 A 大 |

## 決策

選擇 **選項 B**。

理由：`web/build.py` 是把 `reports/` 底下**已經寫死的歷史 Markdown 檔案**轉成靜態 HTML，這個轉換過程必須是幂等的（同一份報告檔案永遠轉出同樣的 HTML）。選項 A 會讓「歷史報告頁面顯示的內容」隨著 `state.json` 之後被覆寫而改變，等同於竄改已發佈的歷史紀錄，違反報告作為每日紀錄的基本定位。選項 B 把 `state.json` 限定在「job 產生下一份報告時的參考資料」這個角色，不讓它成為前台渲染的資料源，正確性與現有 `web/deploy.sh`「每次全量重建」的設計相容。

後果：
- `reports/state.json` 每檔股票新增 `last_price`（最近查證收盤價）、`limit_range`（金字塔限價低接第一批區間）兩個欄位；`docs/design/SDD.md` 新增第 6.5 節定義此欄位與「延續數據表」報告格式規範（v0.5→v0.6）。
- `job/prompts/PRE.md`：計算完限價後，把 `last_price`／`limit_range` 一併寫回 `state.json`，並在報告文末新增「延續數據表」。
- `job/prompts/MID.md`、`POST.md`：文末固定附上「延續數據表」，資料可以是本次重新查到的價格，也可以是延續 `state.json` 的既有快照值（需標明是延續還是本次重新查證，不算違反資料正確性鐵律）；若本次有查到新報價或建議調整，同步更新 `state.json`。
- `web/build.py` 新增 `extract_continuity_table()` 優先讀取這張新格式表格；找不到（相容 2026-07-04 尚未套用此規範的既有 3 份報告）才 fallback 到原本逐段落最佳猜測的 `extract_stock_detail()`。
- 手動回填 `reports/state.json` 現有 4 檔股票的 `last_price`／`limit_range`，數字直接取自 `0830_PRE.md` 已公開內容，非推算值。
- **代價**：MID/POST 的 prompt 多了一個固定輸出區塊，headless 執行時多一點點 token 成本；換來前台重點摘要在三種報告類型下都有一致、可靠的資料可顯示。
