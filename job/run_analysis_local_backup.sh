#!/bin/bash
# ============================================================
# 檔案名稱：run_analysis_local_backup.sh
# 中文名稱：本機備援排程執行腳本
# 功能說明：Windows Task Scheduler 呼叫，執行 claude headless 分析，附加延續數據表，
#           若有檔案異動則 commit + push，並觸發前台網頁部署。臨時備援雲端 Routines
#           （2026-07-06/07 雲端 sandbox 網路故障+GitHub App 唯讀權限雙重故障，見 ADR-007），
#           雲端 Routine 修好後應停用此排程，不要兩邊同時跑造成重複 commit。
# 所屬模組：job/
# 建立日期：2026-07-07
# 修改日期：2026-07-07
# 開發者　：Claude Code
# ============================================================
#
# 用法：run_analysis_local_backup.sh PRE|MID|POST
#
# 與 job/run_analysis.sh（原始 macOS launchd 版本，已停用）的差異：
# - PROJECT_DIR 用腳本自身位置推算，不寫死路徑，跨機器可搬
# - python3 在 Windows 上有時是 Microsoft Store 空殼指令會靜默失敗，改為偵測後降級用 python
# - 其餘行為約定、權限設計完全比照 run_analysis.sh／ADR-001，見該檔案註解

set -uo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_TYPE="${1:?用法：run_analysis_local_backup.sh PRE|MID|POST}"
PROMPT_FILE="$PROJECT_DIR/job/prompts/${REPORT_TYPE}.md"
LOG_DIR="$PROJECT_DIR/job/logs"
LOG_FILE="$LOG_DIR/${REPORT_TYPE}.log"

mkdir -p "$LOG_DIR"
cd "$PROJECT_DIR" || exit 1

PYTHON_BIN="python3"
if ! python3 -c "" >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi

echo "===== $(date '+%Y-%m-%d %H:%M:%S') 開始執行 ${REPORT_TYPE}（本機備援） =====" >> "$LOG_FILE"

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

TODAY_REPORT_DIR="$PROJECT_DIR/reports/$(date '+%Y-%m-%d')"
REPORT_FILE=$(ls -t "$TODAY_REPORT_DIR"/*"_${REPORT_TYPE}.md" 2>/dev/null | head -1)
if [ -n "$REPORT_FILE" ]; then
  "$PYTHON_BIN" "$PROJECT_DIR/job/append_continuity_table.py" "$REPORT_FILE" >> "$LOG_FILE" 2>&1
  if [ $? -ne 0 ]; then
    echo "append_continuity_table.py 執行失敗，該份報告本次無延續數據表" >> "$LOG_FILE"
  fi
else
  echo "找不到今天的 ${REPORT_TYPE} 報告檔案，略過延續數據表附加" >> "$LOG_FILE"
fi

PUSHED=0
COMMITTED=0
if [ -n "$(git status --porcelain)" ]; then
  git add -A
  git commit -m "job: ${REPORT_TYPE} 報告 $(date '+%Y-%m-%d %H:%M')" >> "$LOG_FILE" 2>&1
  COMMITTED=1
  if git push >> "$LOG_FILE" 2>&1; then
    PUSHED=1
  else
    echo "git push 失敗，本次不重試；略過網頁部署避免公開網頁顯示尚未推送成功的內容" >> "$LOG_FILE"
  fi
else
  echo "無檔案異動，略過 commit" >> "$LOG_FILE"
  PUSHED=1
fi

if [ "$PUSHED" -eq 1 ]; then
  bash "$PROJECT_DIR/web/deploy.sh" >> "$LOG_FILE" 2>&1
  DEPLOY_EXIT=$?
  if [ "$DEPLOY_EXIT" -ne 0 ]; then
    echo "web/deploy.sh 執行失敗（exit ${DEPLOY_EXIT}），本次網頁未更新，不重試" >> "$LOG_FILE"
  fi
fi

# 排程完成通知（見 SDD.md 6.7、ADR-008）：只有本次真的產生新 commit 且成功 push 才通知，
# 避免「無異動」情況下重複推播舊連結。確定性執行，不假手 claude（同 ADR-001/ADR-005 精神），
# 因為本機備援呼叫 claude 時 --allowedTools 未授權 Bash，prompt 內的推播指示對本機備援路徑不會真的執行。
if [ "$COMMITTED" -eq 1 ] && [ "$PUSHED" -eq 1 ]; then
  NOTIFY_FILE="$PROJECT_DIR/job/notify.local.json"
  if [ -f "$NOTIFY_FILE" ]; then
    NTFY_TOPIC=$("$PYTHON_BIN" -c "import json,sys; print(json.load(open(sys.argv[1])).get('ntfy_topic',''))" "$NOTIFY_FILE" 2>/dev/null)
    if [ -n "$NTFY_TOPIC" ]; then
      case "$REPORT_TYPE" in
        PRE) HHMM="0800" ;;
        MID) HHMM="1230" ;;
        POST) HHMM="2130" ;;
      esac
      REPORT_URL="https://blackjtsai.github.io/blackj-stock-point-guard/$(date '+%Y-%m-%d')/${HHMM}_${REPORT_TYPE}.html"
      if ! curl -s -H "Title: BJSPG ${HHMM} ${REPORT_TYPE} 報告已發布" -d "$REPORT_URL" "https://ntfy.sh/${NTFY_TOPIC}" >> "$LOG_FILE" 2>&1; then
        echo "ntfy 推播失敗，本次不重試" >> "$LOG_FILE"
      fi
    fi
  else
    echo "找不到 job/notify.local.json，略過推播通知" >> "$LOG_FILE"
  fi
fi

echo "===== $(date '+%Y-%m-%d %H:%M:%S') 執行結束 =====" >> "$LOG_FILE"
