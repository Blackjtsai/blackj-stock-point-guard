# SETUP — BLACKJ-STOCK-POINT-GUARD

> 環境部署清單，逐項確認就緒。就緒 ✅ / 未完成 ❌

## 環境工具

| 項目 | 版本需求 | 安裝指令 | 狀態 |
|---|---|---|---|
| macOS | 需支援 `launchd` | — | ✅ |
| Claude Code CLI | 已登入訂閱帳號（約 $20/月方案），headless 模式（`claude -p`）已驗證可用 | `claude --version` / `claude -p "..."` | ✅ |
| Git | SSH 憑證（`~/.ssh/id_ed25519_github`），可直接 push | `ssh -T git@github.com` | ✅ |
| GitHub Repo | Public repo 已建立，本機已 push 初始 commit | git@github.com:Blackjtsai/blackj-stock-point-guard.git | ✅ |

## 安裝步驟

1. ~~本機 `git init`，設定 remote~~ — 已完成，remote 使用 SSH：`git@github.com:Blackjtsai/blackj-stock-point-guard.git`
2. 確認 `claude` CLI 已登入使用者自己的訂閱帳號，可用 headless 模式執行（`claude -p "..."`）— 待確認
3. 建立 3 個 `launchd` plist（`~/Library/LaunchAgents/`），對應 08:30 / 12:30 / 21:30，各自呼叫排程分析流程
4. `launchctl load` 註冊排程

## 服務啟動

本專案無需常駐服務。`launchd` 排程註冊一次後由系統在指定時間自動觸發，無需每次對話手動啟動。

排程是否已註冊，可用以下指令確認：
```bash
launchctl list | grep bjspg
```
