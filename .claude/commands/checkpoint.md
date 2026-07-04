# /checkpoint

執行對話檢查點。整理重點、記錄經驗、同步文件、commit 所有變動。

> **規範原則**：「執行步驟的判斷條件」必須寫在此檔案的步驟說明裡，不能只存 memory。
> Memory 是提示，規範才是約束。發現判斷條件有缺漏時，同步更新此檔，不只記 feedback。

---

## 步驟

### 1. 對話重點摘要 → docs/CHANGELOG.md

先讀取 `docs/CHANGELOG.md` 最後一筆的時間戳（`## YYYY-MM-DD` 或 `## YYYY-MM-DD 標題`）。
只摘要**該時間戳之後**發生的事項，append 一筆新紀錄：

```
## YYYY-MM-DD 標題

- 做了什麼（決策、實作、修改）
- 遇到什麼問題或誤判
- 確認了什麼規範或方向
```

> 若本次對話是首次執行 checkpoint，摘要整段對話，並先建立 `docs/CHANGELOG.md`。

---

### 2. 經驗記錄 → Memory

檢查本次對話（上一筆 checkpoint 之後）是否有值得記錄的經驗：

- 錯誤或誤判 → `feedback` memory
- 使用者偏好或習慣 → `user` memory
- 專案決策或背景 → `project` memory
- 架構取捨 / 設計決策分析類討論且尚未問過是否保存 → 主動詢問；既有決策延伸理由優先補進 ADR，新脈絡則寫入 memory
- 通用性決策 → 額外詢問是否同步更新到全域 `universal.md`
- 無新資訊 → 明確說明「本次無新增 memory」

**Memory 淘汰檢查（Layer 完成時觸發）**：

讀取 `docs/TODO.md`，判斷本次對話是否有某個 Layer 從未完成變為全部 `[x]`：

- **有 Layer 剛完成** → 掃描專案 memory 目錄中所有 `project_*.md`，逐一判斷是否已落地或仍是活的決策背景，提議刪除已落地者，等使用者確認後才刪
- **無 Layer 剛完成** → 說明「本次無 Layer 完成，略過 memory 淘汰檢查」

---

### 3. 檢查 CLAUDE.md 與 .claude/commands/

**`docs/design/SDD.md`**：本次對話若有 Layer 驗收完成、新模組或 UC 狀態變動 → 同步更新對應章節與版本記錄；無變動則說明原因。

**根目錄 `CLAUDE.md`**：有新規範補入、有舊規範推翻則修正；無變動說明原因。

**`.claude/commands/*.md`**：對照 CLAUDE.md 核心模組，確認 skill 描述是否仍正確。

**`docs/INTRO.md`**：對外介面、目錄結構、系統元數據有變動時同步更新，並更新「最後更新」日期；無變動則說明原因。

**`docs/decisions/`**：本次對話若有重大架構決策（技術選型、GitHub Pages 部署方式定案等）→ 新增 `ADR-{N:03d}-{slug}.md`；無決策則說明「本次無新增 ADR」。

各項結論必須明確回覆「需要更新 → 已更新」或「無需更動 → 原因」。

---

### 4. 檢查 docs/design/ARCHITECTURE.md

- 有新模組或服務 → 更新 Mermaid 圖
- 有 Layer 驗收完成 → 更新 Layer 狀態表
- 無需更動 → 說明原因

---

### 5. 檢查 docs/SETUP.md

若本次對話確認或新增了環境工具、排程設定，同步更新狀態欄。

---

### 6. 檢查 docs/design/TASK.md

列出 `docs/TODO.md` 中所有 `## Layer` 標題，對照 `docs/design/TASK.md` 是否都有對應條目：
- 有缺漏 → 補寫缺漏的 Layer 條目，完成後才繼續
- 有調整 → 同步更新
- 無缺漏且無調整 → 說明「TASK.md 無需更動」

---

### 7. 更新有異動的 Workload Blueprint.md

掃描本次對話中有檔案異動的 `job/`、`web/` 目錄，逐一確認：

| 判斷條件 | 動作 |
|---|---|
| 該 workload 目錄下有新增/修改/刪除檔案 | 更新 `{workload}/blueprint.md` |
| Layer 驗收完成 | 更新「當前 Layer 狀態」表，狀態標記 ✅ |
| 以上皆無 | 說明「{workload}/blueprint.md 無需更動」 |

---

### 8. Code Review

先看本次變動的檔案清單，自動選擇等級：

**`high`**（任一條件符合）：報告產出邏輯（避免捏造數字的規則）有異動、`state.json` 結構變動、新增排程時間點或大規模重構

**`medium`**：前台 HTML/CSS、文件、設定檔調整

執行 `/code-review <選定等級>`，並說明選擇原因：
- 有 CONFIRMED / PLAUSIBLE findings → 修完再繼續
- 全部 REFUTED 或無 findings → 說明「code review 無問題」，繼續

---

### 9. 更新 docs/TODO.md

- 已完成項目標記 `[x]`
- 新增本次發現的待辦項目

---

### 10. Git Commit + Push

```bash
git add <changed files>
git commit -m "checkpoint: <一句話描述本次主要變動>"
git push
```

直接 commit 並 push，不需等使用者確認。
