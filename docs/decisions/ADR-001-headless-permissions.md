# ADR-001：無人值守排程執行的工具權限範圍

> 狀態：已採納
> 日期：2026-07-04
> 決策者：黑暗傑客（Eason Tsai）／Claude Code

## 背景

`job/run_analysis.sh` 由 `launchd` 在 08:30/12:30/21:30 無人值守觸發 `claude -p` 執行分析。互動模式下 Claude 使用工具（上網、寫檔）時會跳出權限確認，但排程觸發時沒有人在場按確認，若不預先授權，執行會因無法取得確認而失敗（headless print 模式無 TTY，無法互動式詢問）。因此必須決定：預先開放的工具範圍要多大。

分析流程本身只需要「上網查公開資料」「讀寫報告與狀態檔」，用不到「執行系統指令」的能力。同時，WebFetch/WebSearch 會讀取不可信的公開網頁內容，存在 prompt injection 風險（惡意網頁埋藏文字，試圖誘導 LLM 執行非預期動作）。

## 選項

| 選項 | 優點 | 缺點 |
|---|---|---|
| `--dangerously-skip-permissions` 完全繞過權限檢查 | 設定最簡單 | CLI 官方說明明確標註「僅建議用於無網路的沙盒」，我們的情境恰好相反（需要上網）；一旦中 prompt injection，理論上能被誘導執行任意系統指令 |
| `--allowedTools` / `--disallowedTools` 白名單＋黑名單組合 | 語意直觀 | 實測發現即使不在 allowedTools 清單中，Agent、Skill、ToolSearch、ScheduleWakeup 等工具仍然可見／可能可呼叫，必須額外用 disallowedTools 逐一堵，容易漏掉（例如一開始漏掉 `Agent`，可能被拿來衍生子任務逃脫範圍） |
| `--tools` 硬白名單，直接取代整組內建工具 | 實測確認：只留下清單內工具，Bash、Agent、Skill、ToolSearch 等一律不存在，無 deferred 工具，範圍最乾淨可控 | 若未來需要新工具（例如要 Claude 自己 commit），要記得同步更新這個清單 |

## 決策

選擇 **`--tools "WebSearch,WebFetch,Read,Write,Edit,Glob,Grep"`**（硬白名單）。

理由：
- 實測驗證此參數會完全替換工具集，而非疊加在預設工具集之上，是三個選項中唯一能明確排除 Bash、Agent 等高風險工具的做法。
- git commit/push 交由 `job/run_analysis.sh`（外層 shell 腳本）在 claude 執行完之後處理，claude 本身完全不需要、也不會拿到指令執行能力。
- 即使 WebFetch/WebSearch 抓到惡意埋藏指令的網頁內容，最壞情況是報告內容被污染（例如寫出錯誤的分析結論），但無法逃逸到檔案系統以外或執行任意指令，影響範圍侷限在 `reports/` 底下的檔案內容。

後果：
- 之後若 Layer 2/3 需要新增工具能力（例如未來想讓 claude 自己處理 git 操作），必須同步更新 `job/run_analysis.sh` 裡的 `--tools` 清單，否則會被硬擋。
- WebSearch 工具本身限定美國地區結果，台股相關資料（證交所、融資融券）需靠 WebFetch 直接打官方網址取得，不能依賴 WebSearch 搜尋台灣網站。
