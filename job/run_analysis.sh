#!/bin/bash
# ============================================================
# 檔案名稱：run_analysis.sh
# 中文名稱：排程分析執行腳本
# 功能說明：由 launchd 於排定時間呼叫，執行 claude headless 分析，附加延續數據表，若有檔案異動則 commit + push，並觸發前台網頁部署
# 所屬模組：job/
# 建立日期：2026-07-04
# 修改日期：2026-07-06
# 開發者　：Claude Code
# ============================================================
#
# 用法：run_analysis.sh PRE|MID|POST
#
# 行為約定（見 docs/requirements/需求.md 第 4 節）：
# - claude 執行失敗（含訂閱額度不足）→ 記錄 log 後直接結束，不重試
# - 找不到對應 prompt 檔 → 記錄 log 後直接結束（Layer 2 完成前的預期狀況）
# - 沒有任何檔案異動 → 不 commit
#
# 權限設計（見 docs/decisions/ADR-001-headless-permissions.md）：
# 無人值守執行，分兩層限制：
# 1. --tools 硬白名單，完全不含 Bash、Agent 等會執行指令或衍生子任務的工具
# 2. --allowedTools 對 Write/Edit 限定只能動 reports/ 與 job/inbox/，對 WebFetch
#    限定只能打信任網域清單。Read/Grep/Glob/WebSearch 經實測無法有效路徑限定，
#    視為可讀但不可外流：唯一的資料外流管道（WebFetch）鎖在信任網域，
#    即使 Read 讀到非預期內容也送不出去。
# git commit/push 由本腳本自己執行，不假手 claude。

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

TRUSTED_FETCH_DOMAINS="WebFetch(domain:tw.stock.yahoo.com) WebFetch(domain:finance.yahoo.com) WebFetch(domain:www.twse.com.tw)"

claude -p "$(cat "$PROMPT_FILE")" \
  --tools "WebSearch,WebFetch,Read,Write,Edit,Glob,Grep" \
  --allowedTools "Write(./reports/**) Edit(./reports/**) Edit(./job/inbox/**) ${TRUSTED_FETCH_DOMAINS}" \
  >> "$LOG_FILE" 2>&1
CLAUDE_EXIT=$?

if [ "$CLAUDE_EXIT" -ne 0 ]; then
  echo "claude 執行失敗（exit ${CLAUDE_EXIT}），本次不重試，直接結束" >> "$LOG_FILE"
  exit 0
fi

# 決定性附加「延續數據表」（見 job/append_continuity_table.py、ADR-005），
# 不假手 claude 排版；用檔名比對今天的報告，不寫死 HHMM（時段觸發時間可能調整）
TODAY_REPORT_DIR="$PROJECT_DIR/reports/$(date '+%Y-%m-%d')"
REPORT_FILE=$(ls -t "$TODAY_REPORT_DIR"/*"_${REPORT_TYPE}.md" 2>/dev/null | head -1)
if [ -n "$REPORT_FILE" ]; then
  python3 "$PROJECT_DIR/job/append_continuity_table.py" "$REPORT_FILE" >> "$LOG_FILE" 2>&1
  if [ $? -ne 0 ]; then
    echo "append_continuity_table.py 執行失敗，該份報告本次無延續數據表" >> "$LOG_FILE"
  fi
else
  echo "找不到今天的 ${REPORT_TYPE} 報告檔案，略過延續數據表附加" >> "$LOG_FILE"
fi

PUSHED=0
if [ -n "$(git status --porcelain)" ]; then
  git add -A
  git commit -m "job: ${REPORT_TYPE} 報告 $(date '+%Y-%m-%d %H:%M')" >> "$LOG_FILE" 2>&1
  if git push >> "$LOG_FILE" 2>&1; then
    PUSHED=1
  else
    echo "git push 失敗，本次不重試；略過網頁部署避免公開網頁顯示尚未推送成功的內容" >> "$LOG_FILE"
  fi
else
  echo "無檔案異動，略過 commit" >> "$LOG_FILE"
  PUSHED=1
fi

# 報告更新後，同步重建並部署前台網頁（UC-BJSPG 3.2.3，見 web/deploy.sh）
# 僅在「本次無異動」或「push 成功」時才部署，避免 push 失敗時網頁顯示未同步到 GitHub 的內容
if [ "$PUSHED" -eq 1 ]; then
  bash "$PROJECT_DIR/web/deploy.sh" >> "$LOG_FILE" 2>&1
  DEPLOY_EXIT=$?
  if [ "$DEPLOY_EXIT" -ne 0 ]; then
    echo "web/deploy.sh 執行失敗（exit ${DEPLOY_EXIT}），本次網頁未更新，不重試" >> "$LOG_FILE"
  fi
fi

echo "===== $(date '+%Y-%m-%d %H:%M:%S') 執行結束 =====" >> "$LOG_FILE"
