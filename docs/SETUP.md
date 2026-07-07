# SETUP — BLACKJ-STOCK-POINT-GUARD

> 環境部署清單，逐項確認就緒。就緒 ✅ / 未完成 ❌

## 環境工具

| 項目 | 版本需求 | 安裝指令 | 狀態 |
|---|---|---|---|
| Claude Code 雲端 Routines | claude.ai/code 已建立 3 個 Routine（`BJSPG-PRE-0800`／`BJSPG-MID-1230`／`BJSPG-POST-2130`，Weekdays） | claude.ai/code → Routines | ✅ |
| Git | SSH 憑證（`~/.ssh/id_ed25519_github`），可直接 push | `ssh -T git@github.com` | ✅ |
| GitHub Repo | Public repo 已建立，本機已 push 初始 commit | git@github.com:Blackjtsai/blackj-stock-point-guard.git | ✅ |
| GitHub App 整合權限 | Routine 用的 GitHub App 需要 `Contents: Read and write`（目前僅 Read-only，push 會 403，見 ADR-007） | GitHub → Settings → Applications | ❌ |
| GitHub Pages | Source: Deploy from a branch → `gh-pages` / `/(root)`，已上線 | https://blackjtsai.github.io/blackj-stock-point-guard/ | ✅ |

> 本機 macOS `launchd` + headless `claude -p`（`job/run_analysis.sh`）為原始設計，已停用，見 ADR-007；相關檔案僅存作歷史紀錄，不再需要保持就緒。

## 安裝步驟（全部已完成）

1. ~~本機 `git init`，設定 remote~~ — 已完成，remote 使用 SSH：`git@github.com:Blackjtsai/blackj-stock-point-guard.git`
2. ~~建立 claude.ai/code 的 3 個 Routine~~ — 已建立，Weekdays 觸發
3. ~~（原始設計，已停用）建立 3 個本機 `launchd` plist、`launchctl load` 註冊~~ — 見 `job/launchd/`，ADR-007 後不再使用

## 待辦（見 ADR-007）

- [ ] 到 GitHub 網頁，把 Routine 用的 GitHub App 整合權限從 Read-only 改成 **Contents: Read and write**，否則 `git push` 網路故障時，MCP push 這條備援路徑也無法作為替代方案
- [ ] 雲端 Routine 網路/權限問題修好後，記得停用或刪除下方「本機臨時備援排程」，避免跟雲端 Routine 同一時段重複執行、重複 commit

## 本機臨時備援排程（2026-07-07 新增，見 ADR-007）

2026-07-06/07 雲端 Routine 同時撞上 sandbox 網路故障與 GitHub App 唯讀權限，PRE 之後的 MID/POST 皆卡住。在雲端問題修好前，於這台 Windows 機器（`D:\_claude-project\blackj-stock-point-guard`）額外註冊 3 個 **Windows工作排程器（Task Scheduler）** 任務作臨時備援，平日觸發：

| 任務名稱 | 時間 | 對應腳本 |
|---|---|---|
| `BJSPG_PRE_Backup` | 平日 08:00 | `job/run_analysis_local_backup.sh PRE` |
| `BJSPG_MID_Backup` | 平日 12:30 | `job/run_analysis_local_backup.sh MID` |
| `BJSPG_POST_Backup` | 平日 21:30 | `job/run_analysis_local_backup.sh POST` |

**前提**：這台電腦必須開機（不需登入使用者互動，Task Scheduler 預設可背景執行）。查詢/管理：

```powershell
Get-ScheduledTask -TaskName "BJSPG_*_Backup"
Unregister-ScheduledTask -TaskName "BJSPG_PRE_Backup","BJSPG_MID_Backup","BJSPG_POST_Backup" -Confirm:$false  # 雲端修好後移除用
```

執行 log 位置：`job/logs/{PRE,MID,POST}.log`（不進版控）。`job/run_analysis_local_backup.sh` 與已停用的 `job/run_analysis.sh` 差異：路徑改為自動偵測（可跨機器搬），`python3` 在此機器上是 Microsoft Store 空殼指令會靜默失敗，已加上偵測後降級用 `python` 的邏輯。

## GitHub Pages（已設定完成）

2026-07-05 使用者已於 GitHub 網頁完成設定（Source: Deploy from a branch → `gh-pages` / `/(root)`），並以 WebFetch 確認首頁正確顯示 2026-07-04 三份報告連結。之後每次雲端 Routine 執行完會自動更新 `gh-pages` branch 內容（見 `job/prompts/*.md` 版本控制段落），網頁跟著自動刷新，不需要重複設定。

## 服務啟動

本專案無需常駐服務。claude.ai/code 的 Routines 註冊一次後由 Claude 平台在指定時間自動觸發，無需使用者電腦保持開機在線，也無需每次對話手動啟動。

排程執行狀況可到 claude.ai/code 的 Routines 側欄查看每次執行紀錄；本機不再有 `job/logs/*.log`（僅停用前的歷史紀錄）。
