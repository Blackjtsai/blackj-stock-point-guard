# ADR-008：排程完成推播通知管道

> 狀態：已採納
> 日期：2026-08-10
> 決策者：Eason Tsai（黑暗傑客）

## 背景

使用者不一定會主動盯著 GitHub Pages，希望每次排程（PRE/MID/POST）成功發布報告後，手機能收到推播通知並附上報告直達連結。原本 `web/blueprint.md` 明訂「不需要新報告通知機制」，本次決策推翻該條舊規範。

## 選項

| 選項 | 優點 | 缺點 |
|---|---|---|
| LINE Notify | 使用者熟悉的介面 | **已於 2025-03-31 正式關閉，不可用** |
| LINE Messaging API | 使用者熟悉的 App | 需另建 LINE Official Account + Messaging API channel，設定門檻高，且 Channel Access Token 需另外保密存放 |
| ntfy.sh | 免帳號、免 Token，設定 5 分鐘內完成，`curl` 一行即可推播 | 使用者需額外安裝一個新 App；topic 名稱本質上是「知道就能發」的準密鑰，需妥善保管避免外洩 |

## 決策

選擇 **ntfy.sh**，用隨機字串 topic（`bjspg-dd8b923e`）取代帳密/Token。

理由：本專案定位是單人使用、簡單維運（見 CLAUDE.md「Simplicity First」），LINE Messaging API 的設定與長期維護成本（Official Account、channel、webhook 取得 userId）不成比例；ntfy.sh 免帳號、免後端維運，且推播內容本身不含敏感資訊（只有公開報告的連結，repo 本來就是 Public），topic 外洩的最大風險只是被亂發垃圾通知，可隨時换新 topic 因應，風險可控。

**topic 名稱存放位置**：`job/notify.local.json`（`.gitignore` 排除、不進版控），比照 `job/holdings.local.json`（ADR-006）的既有模式。

**執行位置的額外決策**：發現本機備援腳本（`job/run_analysis_local_backup.sh`）呼叫 `claude -p` 時 `--allowedTools` 未授權 Bash（見 ADR-001），若把推播邏輯只寫在 `job/prompts/*.md` 交給 LLM 執行 `curl`，本機備援路徑下不會真的執行——與 git commit/push、`append_continuity_table.py` 是同一類問題。因此推播邏輯**兩處都寫**：
- `job/prompts/*.md`：供雲端 Routine（LLM 本身有完整 Bash 權限，自行 git commit/push，見 ADR-007）使用
- `job/run_analysis_local_backup.sh`：本機備援路徑的確定性執行，不假手 LLM（與 ADR-001／ADR-005 精神一致），且只在本次真的產生新 commit 並成功 push 時才推播，避免「無異動」情況下重複推播舊連結

`job/notify.local.json` 不存在時兩處都直接跳過，不視為錯誤（沿用 ADR-006 「本機專用檔案缺席時降級為原邏輯」設計）。

後果：雲端 Routine 因為 `notify.local.json` 未進版控、沙盒內不存在該檔案，實際上永遠不會從雲端路徑發出通知，只有本機備援路徑（此檔案實體存在於磁碟）會真的推播——這是已知且接受的行為，非 bug。
