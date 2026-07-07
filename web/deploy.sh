#!/bin/bash
# ============================================================
# 檔案名稱：deploy.sh
# 中文名稱：前台網頁部署腳本
# 功能說明：呼叫 build.py 產生靜態網頁，並 push 到獨立的 gh-pages branch（GitHub Pages 部署來源）
# 所屬模組：web/（UC-BJSPG 3.2.3）
# 建立日期：2026-07-05
# 修改日期：2026-07-05
# 開發者　：Claude Code
# ============================================================
#
# 用法：web/deploy.sh
#
# 設計原則：
# - gh-pages 為 orphan branch，只放建置後的靜態檔案，與 main 的 docs/（專案文件）互不衝突
# - 用獨立的 git worktree（.gh-pages-worktree/，已加入 .gitignore）簽出 gh-pages branch，
#   不影響 main 分支目前的工作目錄
# - 沒有新內容（build 結果與上次相同）就不 commit，避免無意義的 push

set -uo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKTREE_DIR="$PROJECT_DIR/.gh-pages-worktree"

# Windows 的 python3 有時只是 Microsoft Store 的空殼指令，實測會靜默失敗；
# 找得到真正可執行的 python3 才用，否則退回 python（見 ADR-007 本機備援排程）
PYTHON_BIN="python3"
if ! python3 -c "" >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi

cd "$PROJECT_DIR" || exit 1

if ! git show-ref --verify --quiet refs/heads/gh-pages \
  && git ls-remote --exit-code --heads origin gh-pages >/dev/null 2>&1; then
  git fetch origin gh-pages:gh-pages
fi

if [ ! -d "$WORKTREE_DIR" ]; then
  if git show-ref --verify --quiet refs/heads/gh-pages; then
    git worktree add "$WORKTREE_DIR" gh-pages || exit 1
  else
    git worktree add --detach "$WORKTREE_DIR" || exit 1
    if ! (cd "$WORKTREE_DIR" && git checkout --orphan gh-pages && git rm -rf . >/dev/null); then
      echo "建立 gh-pages orphan branch 失敗，移除損毀的 worktree 後結束，不繼續 build/commit" >&2
      git worktree remove --force "$WORKTREE_DIR" 2>/dev/null
      exit 1
    fi
  fi
fi

"$PYTHON_BIN" "$PROJECT_DIR/web/build.py" "$WORKTREE_DIR" || {
  echo "web/build.py 執行失敗，略過本次 commit/push" >&2
  exit 1
}

cd "$WORKTREE_DIR" || exit 1

if [ -n "$(git status --porcelain)" ]; then
  git add -A
  git commit -m "web: 更新前台網頁 $(date '+%Y-%m-%d %H:%M')" >/dev/null
  if ! git push origin gh-pages; then
    echo "push gh-pages 失敗（可能 remote 已有分歧歷史），本次不重試" >&2
    exit 1
  fi
else
  echo "網頁內容無異動，略過 commit"
fi
