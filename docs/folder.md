# 📁 bookpost プロジェクト フォルダ構成

## 全体構成
```
bookpost/
├── main.py                    # メイン実行ファイル
├── scraper.py                 # レビュー収集モジュール
├── config.json                # WordPress接続設定（API情報）
├── requirements.txt           # Python依存パッケージ一覧
├── README.md                  # プロジェクト説明
├── .gitignore                 # Git除外設定
│
├── docs/                      # ドキュメント類
│   ├── systemZentei.md        # システム前提
│   ├── unyoFlow.md            # 運用フロー図
│   └── folderStructure.md     # フォルダ構成（本ファイル）
│
├── data/                      # データ保存ディレクトリ
│   ├── reviews/               # 収集したレビュー要約
│   │   └── review_[ISBN].txt
│   ├── outputs/               # 生成した記事（Markdown）
│   │   └── article_[ISBN].md
│   └── images/                # サムネイル画像
│       └── thumbnail_[ISBN].png
│
└── tests/                     # テストコード（任意）
    └── test_main.py
```

---

## 各ファイル・ディレクトリの役割

### ルートディレクトリ

| ファイル名 | 役割 | 使用タイミング |
|------------|------|----------------|
| `main.py` | メインプログラム。書籍情報取得、レビュー収集、記事生成、WordPress投稿を統括 | 毎回実行 |
| `scraper.py` | Bing検索からレビュー要約を収集するモジュール | main.pyから呼び出し |
| `config.json` | WordPress接続情報（`wp_url`, `wp_user`, `wp_app_password`）を保存 | 初回設定 |
| `requirements.txt` | 必要なPythonパッケージ一覧（`requests`, `beautifulsoup4`など） | 環境構築時 |
| `README.md` | プロジェクト概要、セットアップ手順、使用方法 | 参照用 |
| `.gitignore` | Git管理対象外ファイル指定（`config.json`, `data/`など） | Git利用時 |

### `/docs/` - ドキュメント

| ファイル名 | 内容 |
|------------|------|
| `systemZentei.md` | 開発環境、API構成、WordPress設定などシステム前提 |
| `unyoFlow.md` | 運用フロー図（作業手順、実行コマンド、AIプロンプト） |
| `folderStructure.md` | フォルダ構成説明（本ファイル） |

### `/data/` - データ保存

| ディレクトリ | 保存内容 | ファイル命名規則 |
|--------------|----------|------------------|
| `/data/reviews/` | Bing検索で収集したレビュー要約テキスト | `review_[ISBN].txt` |
| `/data/outputs/` | ChatGPT/Perplexityで生成した記事（Markdown） | `article_[ISBN].md` |
| `/data/images/` | Bing Image Creator/Canvaで作成したサムネイル画像 | `thumbnail_[ISBN].png` |

**注意**：`/data/` ディレクトリは `.gitignore` に追加し、Gitにコミットしないこと

---

## 実行コマンドと対応ファイル

| 実行コマンド | 呼び出される関数 | 入力 | 出力 |
|--------------|------------------|------|------|
| `python main.py fetch --isbn [ISBN]` | `fetch_book_data()` | ISBN | 書籍情報（著者、出版社、概要） |
| （上記コマンド実行時に自動） | `scrape_reviews()` | ISBN/タイトル | `/data/reviews/review_[ISBN].txt` |
| `python main.py post --isbn [ISBN]` | `generate_post()` | `/data/outputs/article_[ISBN].md` + `/data/images/thumbnail_[ISBN].png` | WordPress投稿本文 |
| （上記コマンド実行時に自動） | `post_to_wp()` | Markdown本文+画像 | WordPress記事（公開済） |

---

## セットアップ手順

### 1. リポジトリクローン
```bash
git clone https://github.com/tomo4559/bookpost.git
cd bookpost
```

### 2. 仮想環境作成（推奨）
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. 依存パッケージインストール
```bash
pip install -r requirements.txt
```

### 4. 設定ファイル作成
`config.json` を作成し、以下の内容を記入：
```json
{
  "wp_url": "https://freetomo.com/wp-json/wp/v2/posts",
  "wp_user": "your_username",
  "wp_app_password": "your_app_password"
}
```

### 5. データディレクトリ作成
```bash
mkdir data\reviews data\outputs data\images
```

---

## 運用時のディレクトリ利用例

### 書籍情報取得 → レビュー収集
```bash
python main.py fetch --isbn 9784123456789
```
→ `/data/reviews/review_9784123456789.txt` に保存

### 記事生成・投稿（手動で記事と画像を準備後）
1. `/data/outputs/article_9784123456789.md` を配置
2. `/data/images/thumbnail_9784123456789.png` を配置
3. 実行：
```bash
python main.py post --isbn 9784123456789
```
→ WordPressに自動投稿

---

## 注意事項
- `config.json` は **Gitにコミットしない**（`.gitignore`に追加）
- `/data/` 配下のファイルも **Gitにコミットしない**
- API キーや認証情報は環境変数またはconfig.jsonで管理
- 無料APIプランの制限に注意（Google Books API、Bing Search）
- ChatGPT/Perplexityは手動操作（OpenAI APIは不使用）
