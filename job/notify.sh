#!/bin/bash
# ============================================================
# 檔案名稱：notify.sh
# 中文名稱：排程完成推播通知
# 功能說明：讀取 job/notify.local.json 取得 ntfy topic，依報告檔案路徑組出對應網址並推播；
#           notify.local.json 不存在或 topic 為空時靜默跳過，不視為錯誤。供本機備援 script 與
#           雲端 Routine（LLM 執行 Bash）共用一份實作，避免 URL 組字串、HHMM 對照、ASCII 編碼
#           規則分散在多個 prompt 檔各自維護（見 SDD.md 6.7、ADR-008）
# 所屬模組：job/
# 建立日期：2026-08-11
# 修改日期：2026-08-11
# 開發者　：Claude Code
# ============================================================
#
# 用法：notify.sh <report_file_path>，例如 notify.sh reports/2026-08-11/0800_PRE.md
# 呼叫方負責只在「真的有新 commit 且 push 成功」時才呼叫本 script（見 ADR-008），本 script 不重複判斷

set -uo pipefail

REPORT_FILE="${1:?用法：notify.sh <report_file_path>}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
NOTIFY_FILE="$PROJECT_DIR/job/notify.local.json"

if [ ! -f "$NOTIFY_FILE" ]; then
  echo "找不到 job/notify.local.json，略過推播通知"
  exit 0
fi

PYTHON_BIN="python3"
if ! python3 -c "" >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi

NTFY_TOPIC=$("$PYTHON_BIN" -c "import json,sys; print(json.load(open(sys.argv[1])).get('ntfy_topic',''))" "$NOTIFY_FILE" 2>/dev/null)
if [ -z "$NTFY_TOPIC" ]; then
  echo "job/notify.local.json 缺少 ntfy_topic，略過推播通知"
  exit 0
fi

# 日期/類型一律從實際寫入的報告檔案路徑解析，不重新呼叫 date——避免分析流程跨午夜時，
# 推播當下重算的日期跟報告實際寫入的日期不一致，連到 404 頁面
REPORT_DATE="$(basename "$(dirname "$REPORT_FILE")")"
REPORT_BASENAME="$(basename "$REPORT_FILE" .md)"
REPORT_TYPE="${REPORT_BASENAME#*_}"
REPORT_URL="https://blackjtsai.github.io/blackj-stock-point-guard/${REPORT_DATE}/${REPORT_BASENAME}.html"

# Title 與 body 一律純 ASCII：中文字元在部分 shell 環境下放 header 會亂碼、放 body 會被 ntfy
# 誤判成二進位檔案改用附件形式（實測發生過），穩妥起見不夾雜中文
if curl -s --max-time 10 --connect-timeout 5 \
  -H "Priority: urgent" \
  -H "Title: BJSPG ${REPORT_TYPE} Report Published" \
  -d "$REPORT_URL" \
  "https://ntfy.sh/${NTFY_TOPIC}" >/dev/null; then
  echo "ntfy 推播已送出：$REPORT_URL"
else
  echo "ntfy 推播失敗，本次不重試"
fi
