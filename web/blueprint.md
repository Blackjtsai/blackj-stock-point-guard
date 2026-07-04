# Blueprint — WEB（前台 Dashboard）（UC-BJSPG 3.2）

> 版本：v0.1 ／ 最後更新：2026-07-04

## 技術棧

| 層 | 技術 |
|---|---|
| 框架 | 無（純 HTML/CSS + 少量原生 JS） |
| 樣式 | 手寫 CSS，RWD（flexbox/grid，無需額外框架） |
| 部署 | GitHub Pages（部署路徑待 Layer 3 定案，見 `docs/design/ARCHITECTURE.md` 待確認事項） |

## 目錄結構

```
web/
├── blueprint.md
└── [待 Layer 3 實作後補充：index.html、style.css 等]
```

## 對外介面

| 路由 | 說明 |
|---|---|
| 首頁 | 依日期列出已產出報告（08:30/12:30/21:30），簡單列表，最新在最上 |

## 當前 Layer 狀態

| Layer | UC 範圍 | 狀態 |
|---|---|---|
| Layer 3 | UC-BJSPG 3.2.1 ～ 3.2.3 | ⏳ |

## 關鍵業務約束

- 不做日曆選擇器，維持簡單列表
- 不需要新報告通知機制
- GitHub repo 為 Public，股票代號不隱碼，直接顯示真實代號/名稱
- Layer 3 開始前需先定案 GitHub Pages 部署方式（root vs `/docs` vs `gh-pages` 分支 + Actions），因為 `docs/` 已作專案文件用途
