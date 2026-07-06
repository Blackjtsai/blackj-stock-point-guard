# ADR-007：排程執行機制改為 Claude Code 雲端 Routines（取代本機 launchd）

> 狀態：已採納
> 日期：2026-07-07
> 決策者：黑暗傑客（Eason Tsai）／Claude Code

## 背景

原始設計（ADR-001、`docs/SETUP.md`、`job/blueprint.md`）是本機 macOS `launchd` 於 08:00/12:30/21:30 觸發 `job/run_analysis.sh`，由該 shell 腳本呼叫 `claude -p`（工具硬白名單，不含 Bash/git）分析，腳本本身在 claude 執行完後負責 `git commit/push`。

實際運作已全面改用 **claude.ai/code 的雲端 Routines**（側欄 `BJSPG-PRE-0800`／`BJSPG-MID-1230`／`BJSPG-POST-2130`，Weekdays），三個時段皆是，`run_analysis.sh`／`job/launchd/*.plist` 已無實際作用，但文件從未同步更新，此落差直到 2026-07-06 21:30 POST 執行卡住才被發現。

雲端 Routine 是完整的 agentic session，工具權限模型跟 ADR-001 設計的本機硬白名單完全不同：它自己判斷要不要用 Bash/git，且執行環境是獨立 sandbox，有兩個 ADR-001 沒設計進去的新故障點：
1. Sandbox 自身的網路 proxy 會間歇性對外連線回 403（WebFetch／curl／`git push` 走同一個 proxy，一起故障）。
2. Repo 上安裝的 GitHub App 整合預設只有讀取權限，`push_files`／`create_or_update_file` 回 403 "not accessible by integration"，MCP 這條路徑本來就走不通，跟網路狀態無關。

2026-07-06 21:30 POST 撞上第 1 點，Routine 沒有「快速判斷失敗、乾淨結束」的指示，於是自行展開一連串除錯（檢查 SSH 簽名、測試 GitHub MCP 權限、多次重試連線），耗費大量 tool call 後仍卡住，留下一個已簽名但無法 push 的孤兒 commit；2026-07-06 21:30 POST 報告確定遺失，無法復原。

## 選項

| 選項 | 優點 | 缺點 |
|---|---|---|
| 改回本機 launchd + `run_analysis.sh` | 用使用者自己電腦的網路與既有 git 帳號，不會遇到 sandbox proxy／GitHub App 唯讀權限這兩個新故障點；ADR-001 的工具權限防線維持有效 | 需要 Mac 在三個排定時間都保持開機在線，這正是當初放棄本機模式、全面切去雲端 Routines 的原因 |
| 維持雲端 Routines，直接補強 | 不需要人顧電腦在線；三個時段已經都在用，不用重新搬家 | 仍依賴雲端 sandbox 網路穩定度，這塊管不到，只能做到「失敗時乾淨結束」，無法保證「以後絕對不會卡住」 |

## 決策

選擇 **維持雲端 Routines 為正式排程機制，補強兩處已知故障點**：

1. **GitHub App 整合權限**：由使用者自行到 GitHub 網頁（該 App 安裝設定的 Repository permissions）把 `Contents` 從 Read-only 改成 **Read and write**。這件事在 Claude Code 權限範圍外，只能由 repo 擁有者手動操作，不是本次 ADR 能直接完成的項目，記錄在 `docs/TODO.md` 待辦。
2. **`job/prompts/{PRE,MID,POST}.md` 新增「版本控制」段落**：因為外層 `run_analysis.sh` 已經不是實際執行路徑，git commit/push 這個責任必須寫進 prompt 本身，明確要求 Routine 完成報告後自行 `git add -A && git commit && git push`；push 失敗時比照 ADR-001／`run_analysis.sh` 原本「不重試」的精神——**不深入除錯（不查 GPG 簽名、不測試 MCP 權限、不嘗試改道其他 push 管道）、不重試、直接結束**，留下本地 commit 原地不動，下次排程觸發時會接續處理，不需要當下解決。

## 後果

- **ADR-001 的安全假設已被架空**：ADR-001 選擇硬白名單、排除 Bash/git 的理由是「即使 WebFetch 抓到惡意埋藏指令的網頁內容，也無法逃逸到檔案系統以外或執行任意指令」。雲端 Routine 現在確實需要 Bash/git 能力才能自己 commit/push，等於把 ADR-001 刻意擋掉的能力還了回去，prompt injection 防線在雲端 Routines 環境下不再成立。這是本次決策引入的新風險缺口，本 ADR 只記錄，不在此解決；需要另外找時間重新評估雲端 Routine 的工具權限設計。
- `job/run_analysis.sh`、`job/launchd/*.plist` 視為**已停用**，保留在 repo 作歷史紀錄，不再是實際執行路徑；`docs/SETUP.md`／`job/blueprint.md`／`docs/design/ARCHITECTURE.md` 同步改寫反映雲端 Routines 現況。
- 網路 403 本身是雲端 sandbox 基礎設施問題，這次決策**無法保證以後絕對不會卡住**，只能保證卡住時乾淨結束、不留孤兒 commit、不浪費 tool call 原地除錯——下次排程會自動接續，最多損失一次報告，不會累積卡死。
- 2026-07-06 21:30 POST 報告確認遺失，不回溯補產出（見對話決議，不追）。
