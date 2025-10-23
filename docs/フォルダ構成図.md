# 📁 フォルダ構成図（Book Review Auto Poster）

## 概要
本システムは、選定した書籍のレビュー収集から記事生成・WordPress投稿までを半自動で行う構成です。  
`main.py` を中心に、AI生成結果やレビュー情報を `/data/` 以下に整理して管理します。

bookpost/
├─ main.py # メインスクリプト（各処理関数を統合）
├─ config.json # APIキー・WordPress情報・設定値などを保持
│
├─ /data/
│ ├─ /reviews/ # 書籍レビュー要約（Bingスクレイピング結果）
│ │ └─ review_[ISBN].txt
│ ├─ /outputs/ # ChatGPT/Perplexityで生成した記事本文（Markdown）
│ │ └─ article_[ISBN].md
│ ├─ /images/ # サムネイル画像（Canva/Bing Image Creator）
│ │ └─ thumbnail_[ISBN].png
│ └─ /logs/ # 実行ログ・エラーログ
│
└─ /utils/
├─ fetcher.py # 書籍情報取得処理（Amazon/GoogleBooks API対応）
├─ scraper.py # レビュー収集（Bingなど）
├─ formatter.py # Markdown整形処理
└─ wordpress.py # WordPress REST API投稿機能

markdown
コードをコピーする

## 備考
- `/data/` 以下はISBN単位で統一命名（`[ISBN]` 置換形式）
- AI生成（文章・画像）はすべて手動出力→上記フォルダへ保存
- main.py から関数単位で自動呼び出し（fetch→scrape→generate→post）