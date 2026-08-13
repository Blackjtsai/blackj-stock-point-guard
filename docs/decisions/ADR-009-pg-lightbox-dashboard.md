# ADR-009：PG 股票回補與關注 Lightbox 儀表板、波段目標價標籤化例外、現金水庫公開打碼

> 狀態：已採納
> 日期：2026-08-13
> 決策者：黑暗傑客（Eason Tsai）／Claude Code

## 背景

老大要求在每日報告下方提供一個精美的 Lightbox 燈箱儀表板，集中呈現「核心關注與回補對照矩陣」（15 檔，含波段目標價、回補區間、PG 戰術指令）與「大後方現金總水庫」（純現金 NT$970,571、防禦底牌 3045 台灣大哥大約 3.8 張），並將每日主報告精簡化（PG 語氣、Zero Noise、聚焦 3~5 檔）。

此需求與專案既有的兩條鐵律直接衝突，實作前先對齊：

1. **波段目標價 vs 資料正確性鐵律**：SDD §6.3 原文「未經查證的推測性『波段目標價』等數字一律禁止出現」。儀表板卻要求整欄波段目標價。
2. **公開曝光財務部位 vs 隱私原則**：repo 為 Public、GitHub Pages 公開，專案特意將 `holdings.local.json`/`notify.local.json` gitignore 就是為了不曝光部位。把真實現金水位與持股印上公開頁面與此原則正面矛盾。

## 決策

老大於對話中拍板三項方向：

1. **波段目標價：放寬鐵律，標籤化保留**。目標價/回補區間改由 `job/plan.json` 手動維護，定位為「非查證·個人操盤計劃」，明確標籤並與 live 查證現價分區塊呈現，不混入 A/B/C/D 查證欄位，LLM 不得在正文自行生成新目標價。查證欄位鐵律不變。
2. **現金/持股：敏感塊只進本機、公開頁打碼**。真實金額存 `job/cash.local.json`（`.gitignore` 排除）。公開 Lightbox 金額一律打碼（`NT$ ●●●,●●●`）；僅本機以 `BJSPG_LOCAL_PREVIEW=1` 執行 `build.py` 時渲染真數字，`deploy.sh` 不設此旗標，確保公開產物永遠打碼。
3. **watchlist 收斂為這 15 檔**（2421/2356/2609/0052/0056/00878/2330/6117/4533/1609/1514/6442/3450/8358/6213）。

主報告呈現層改為：PG 語氣強化、Zero Noise（資料缺漏隱藏 B 段大表、聚焦 3~5 檔）、結尾附 Lightbox 按鈕；但 `state.json` 與延續數據表仍全 watchlist 更新（前台需要）。

## 資料分工

| 檔案 | 進版控 | 內容 | 隱私 |
|---|---|---|---|
| `job/plan.json` | 是 | 目標價/回補區間/PG 戰術/分組/fallback 參考價 | 操盤計劃，可公開 |
| `reports/state.json` | 是 | live 現價、建議動作 | 查證數據，可公開 |
| `job/cash.local.json` | 否 | 現金水庫、防禦底牌、姿勢 | 本機專用，公開頁打碼 |

## 影響

- 新增 `job/plan.json`、`job/cash.local.json`（後者 gitignore）；`web/build.py` 新增 `render_pg_dashboard()` 與 `BJSPG_LOCAL_PREVIEW` 打碼閘門。
- SDD 新增 §6.8、§6.3 強化（Zero Noise + 目標價標籤化例外），版本升至 v0.13。
- 三個 `job/prompts/*.md` 加入 PG 語氣/Zero Noise/聚焦 3~5 檔/Lightbox 按鈕；watchlist 15 檔。

## 未解風險

- 打碼閘門靠「deploy.sh 不設環境變數」保證公開安全。若日後有人在本機設了 `BJSPG_LOCAL_PREVIEW=1` 後又手動把 build 產物 push，仍可能外洩——依賴流程紀律，非技術強制。目前單人使用，可接受。
