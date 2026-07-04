#!/bin/bash
# ============================================================
# 檔案名稱：run_analysis.sh
# 中文名稱：排程分析執行腳本
# 功能說明：由 launchd 於排定時間呼叫，執行 claude headless 分析，若有檔案異動則 commit + push
# 所屬模組：job/
# 建立日期：2026-07-04
# 修改日期：2026-07-04
# 開發者　：Claude Code
# ============================================================
#
# 用法：run_analysis.sh PRE|MID|POST
#
# 行為約定（見 docs/requirements/需求.md 第 4 節）：
# - claude 執行失敗（含訂閱額度不足）→ 記錄 log 後直接結束，不重試
# - 找不到對應 prompt 檔 → 記錄 log 後直接結束（Layer 2 完成前的預期狀況）
# - 沒有任何檔案異動 → 不 commit

set -uo pipefail

PROJECT_DIR="/Users/blackjtsai/Documents/blackj-stock-point-guard"
REPORT_TYPE="${1:?用法：run_analysis.sh PRE|MID|POST}"
PROMPT_FILE="$PROJECT_DIR/job/prompts/${REPORT_TYPE}.md"
LOG_DIR="$PROJECT_DIR/job/logs"
LOG_FILE="$LOG_DIR/${REPORT_TYPE}.log"

mkdir -p "$LOG_DIR"
cd "$PROJECT_DIR" || exit 1

echo "===== $(date '+%Y-%m-%d %H:%M:%S') 開始執行 ${REPORT_TYPE} =====" >> "$LOG_FILE"

if [ ! -f "$PROMPT_FILE" ]; then
  echo "找不到 prompt 檔：$PROMPT_FILE，略過本次執行" >> "$LOG_FILE"
  exit 0
fi

claude -p "$(cat "$PROMPT_FILE")" >> "$LOG_FILE" 2>&1
CLAUDE_EXIT=$?

if [ "$CLAUDE_EXIT" -ne 0 ]; then
  echo "claude 執行失敗（exit ${CLAUDE_EXIT}），本次不重試，直接結束" >> "$LOG_FILE"
  exit 0
fi

if [ -n "$(git status --porcelain)" ]; then
  git add -A
  git commit -m "job: ${REPORT_TYPE} 報告 $(date '+%Y-%m-%d %H:%M')" >> "$LOG_FILE" 2>&1
  git push >> "$LOG_FILE" 2>&1
else
  echo "無檔案異動，略過 commit" >> "$LOG_FILE"
fi

echo "===== $(date '+%Y-%m-%d %H:%M:%S') 執行結束 =====" >> "$LOG_FILE"
