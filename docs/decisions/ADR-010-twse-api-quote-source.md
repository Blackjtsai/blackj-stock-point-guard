# ADR-010：個股報價改用 TWSE 官方 API 為主來源，波段目標價授權以技術面設定

> 狀態：已採納
> 日期：2026-08-13
> 決策者：黑暗傑客（Eason Tsai）／Claude Code

## 背景

2026-08-13 首次實跑新格式 PRE 報告時，用 WebFetch 打 `tw.stock.yahoo.com` 個股頁查 15 檔報價，發生兩類問題：

1. **摘要模型串欄/幻覺**：聯鈞(3450) 回傳「最新 5103／昨收 507」自相矛盾；光聖/金居/聯茂數字與 plan.json 參考價差 6~17 倍。第二來源 `finance.yahoo.com` 連續 503。當下依鐵律誤標 4 檔「資料未取得」。
2. **事後查證翻案**：改用 TWSE MIS 官方即時報價 API 交叉驗證，發現 Yahoo 數字其實正確（光聖真的 1595），差很多是因為 **plan.json 參考價本身過時**，不是 Yahoo 幻覺（唯一真幻覺是聯鈞「5103」串欄，但「507」正確）。

同時，老大授權由系統（LLM）代設光聖/聯鈞/金居/聯茂 4 檔的波段目標價（老大自陳「我不知道」），與 SDD 6.3「LLM 不得自造波段目標價」原則直接衝突，需明確處理邊界。

## 決策

### 1. 報價來源改制
- **個股報價主來源改為 TWSE MIS 官方即時報價 JSON API**：`https://mis.twse.com.tw/stock/api/getStockInfo.jsp`，Bash `curl` 批次一次抓完整份 watchlist + `python3` 決定性解析。理由：(a) 省 token（1 次 curl vs 15 次 WebFetch）；(b) 零摘要模型幻覺（決定性 JSON）；(c) 可批次。
- **WebFetch `tw.stock.yahoo.com` 個股頁降為 fallback**（Bash 不可用或 API 失敗才用）。
- **日 K 前波高低**：上市用 TWSE `STOCK_DAY`、上櫃用 TPEx `tradingStock`。
- **籌碼數據（融資融券／法人）不適用**：MIS 報價 API 無此資料，仍依 ADR-003 走個股專屬頁、禁全市場總表。

### 2. 「差很多 ≠ 資料可疑」原則
數字與既有參考值差很大時，第一步是換權威來源（TWSE API）查證，而非預設新數字錯。只有多來源皆失敗/矛盾才標「資料未取得」。既有參考值本身可能過時（本次 plan.json 即是）。

### 3. 波段目標價授權以技術面設定（SDD 6.3 例外的延伸）
老大可授權系統代設波段目標價，但**必須以真實技術面數據為依據**（TWSE/TPEx 日 K 的前波高當目標壓力、前波低當低接鐵板），不得憑訓練知識或臆測喊價；已創新高無壓力者才用整數關量測並標明。所有代設值一律標「技術推估非查證」，與 live 查證現價分區呈現。

## 影響

- `job/prompts/{PRE,MID,POST}.md`、`docs/design/SDD.md` §6.2、`CLAUDE.md` 已更新報價來源優先序與查證原則。
- 待驗證：雲端 Routine 沙盒能否 curl `mis.twse.com.tw`／`www.tpex.org.tw`；不能則自動降級回 WebFetch Yahoo（已設計），需實跑確認降級是否成功（見 TODO Layer 5）。
- plan.json 15 檔目標值到齊（迎廣除息修正 + 4 檔技術面）。

## 未解風險

- 降級路徑（雲端不能 curl → WebFetch Yahoo）尚未在雲端實跑驗證。
- 波段目標價的「技術面代設」仍是主觀判斷的近似，僅供參考；老大保留隨時覆寫權。
