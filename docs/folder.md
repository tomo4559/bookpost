# 📁 bookpost プロジェクト フォルダ構成

## 全体構成
```
bookpost/
├── main.py                    # メイン実行ファイル
├── scraper.py                 # レビュー収集モジュール
├── config.json                # WordPress接続設定（API情報）
├── config.json.example        # 設定ファイルのテンプレート
├── requirements.txt           # Python依存パッケージ一覧
├── README.md                  # プロジェクト説明
├── .gitignore                 # Git除外設定
│
├── docs/                      # ドキュメント類
│   ├── systemZentei.md        # システム前提
│   ├── unyoFlow.md            # 運用フロー図
│   ├── folder.md              # フォルダ構成（本ファイル）
│   └── api.md                 # API仕様書
│
├── data/                      # データ保存ディレクトリ（Git除外）
│   ├── books/                 # 書籍情報キャッシュ
│   │   └── book_[ISBN].json
│   ├── reviews/               # 収集したレビュー要約
│   │   └── review_[ISBN].txt
│   ├── outputs/               # 生成した記事（Markdown）
│   │   └── article_[ISBN].md
│   ├── images/                # サムネイル画像
│   │   └── thumbnail_[ISBN].png
│   └── logs/                  # 実行ログ
│       └── app.log
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
| `scraper.py` | Bing検索からレビュー要約を収集するモジュール（scrape_reviews関数） | main.pyから呼び出し |
| `config.json` | WordPress接続情報（`wp_url`, `wp_user`, `wp_app_password`, `wp_category_id`）を保存 | 初回設定・参照 |
| `config.json.example` | 設定ファイルのテンプレート（Git管理用） | セットアップ時にコピー |
| `requirements.txt` | 必要なPythonパッケージ一覧（`requests`, `beautifulsoup4`, `markdown`, `Pillow`など） | 環境構築時 |
| `README.md` | プロジェクト概要、セットアップ手順、使用方法 | 参照用 |
| `.gitignore` | Git管理対象外ファイル指定（`config.json`, `data/`など） | Git利用時 |

### `/docs/` - ドキュメント

| ファイル名 | 内容 |
|------------|------|
| `systemZentei.md` | 開発環境、API構成、WordPress設定などシステム前提 |
| `unyoFlow.md` | 運用フロー図（作業手順、実行コマンド、AIプロンプト） |
| `folder.md` | フォルダ構成説明（本ファイル） |
| `api.md` | API仕様書（各関数の入出力・エラー処理詳細） |

### `/data/` - データ保存（Git除外）

| ディレクトリ | 保存内容 | ファイル命名規則 | 用途 |
|--------------|----------|------------------|------|
| `/data/books/` | 書籍情報キャッシュ（JSON） | `book_[ISBN].json` | Google Books APIリクエスト節約 |
| `/data/reviews/` | 収集したレビュー要約テキスト | `review_[ISBN].txt` | ChatGPT/Perplexity記事生成の素材 |
| `/data/outputs/` | 生成した記事（Markdown） | `article_[ISBN].md` | WordPress投稿用本文 |
| `/data/images/` | サムネイル画像（PNG、2MB以下） | `thumbnail_[ISBN].png` | アイキャッチ画像 |
| `/data/logs/` | 実行ログ（INFO/ERROR） | `app.log` | エラー追跡・デバッグ |

**重要**: `/data/` ディレクトリ全体を `.gitignore` に追加し、Gitにコミットしないこと

---

## main.py 関数構成

| 関数名 | 引数 | 戻り値 | 役割 |
|--------|------|--------|------|
| `fetch_book_data(isbn)` | ISBN-13文字列 | dict（書籍情報） | Google Books APIから書籍情報取得、キャッシュ保存 |
| `generate_post(isbn)` | ISBN-13文字列 | dict（投稿データ） | Markdown→HTML変換、WordPress投稿データ生成 |
| `post_to_wp(post_data, image_path)` | 投稿データ、画像パス | dict（レスポンス） | WordPress REST APIで記事＋画像投稿 |
| `normalize_isbn(isbn)` | ISBN文字列 | ISBN-13文字列 | ISBNを13桁ハイフンなし形式に統一 |
| `setup_logger(name, log_file)` | ロガー名、ログファイルパス | Logger | ログ設定初期化 |

**自動実行フロー**:
```
python main.py fetch --isbn XXX
  → fetch_book_data() 実行
  → scraper.scrape_reviews() 自動実行

python main.py post --isbn XXX
  → generate_post() 実行
  → post_to_wp() 自動実行
```

---

## scraper.py 関数構成

| 関数名 | 引数 | 戻り値 | 役割 |
|--------|------|--------|------|
| `scrape_reviews(isbn_or_title)` | ISBNまたはタイトル | str（保存先パス） | Bing検索からレビュー収集、テキスト保存 |

**実装方式**: Webスクレイピング（Bing Search API不使用）

---

## 実行コマンドと対応ファイル

| 実行コマンド | 呼び出される関数 | 入力ファイル | 出力ファイル |
|--------------|------------------|--------------|--------------|
| `python main.py fetch --isbn [ISBN]` | `fetch_book_data()`<br>`scrape_reviews()` | - | `/data/books/book_[ISBN].json`<br>`/data/reviews/review_[ISBN].txt` |
| `python main.py post --isbn [ISBN]` | `generate_post()`<br>`post_to_wp()` | `/data/outputs/article_[ISBN].md`<br>`/data/images/thumbnail_[ISBN].png`<br>`/data/books/book_[ISBN].json` | WordPress記事（下書き） |

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
```bash
# テンプレートをコピー
copy config.json.example config.json

# config.json を編集
```

**config.json 記入例**:
```json
{
  "wp_url": "https://freetomo.com/wp-json/wp/v2/posts",
  "wp_user": "your_username",
  "wp_app_password": "xxxx xxxx xxxx xxxx xxxx xxxx",
  "wp_category_id": 123
}
```

**WordPressアプリケーションパスワード取得方法**:
1. WordPress管理画面 → ユーザー → プロフィール
2. 「アプリケーションパスワード」セクションで新規作成
3. 生成されたパスワードをconfig.jsonに貼付

**カテゴリID取得方法**:
1. WordPress管理画面 → 投稿 → カテゴリー
2. 「読書レビュー」カテゴリをクリック
3. ブラウザURLの `tag_ID=XXX` がカテゴリID

### 5. データディレクトリ作成
```bash
mkdir data\books data\reviews data\outputs data\images data\logs
```

### 6. .gitignore設定確認
`.gitignore` に以下が含まれているか確認:
```
config.json
data/
__pycache__/
*.pyc
venv/
```

---

## 運用時のディレクトリ利用例

### 例1: 書籍情報取得 → レビュー収集
```bash
python main.py fetch --isbn 9784123456789
```

**生成されるファイル**:
- `/data/books/book_9784123456789.json`
- `/data/reviews/review_9784123456789.txt`

**ログ出力**:
```
[2024-10-24 09:15:32] INFO: 書籍情報を取得しました: サンプル書籍
[2024-10-24 09:20:12] INFO: レビューを収集しました
```

### 例2: 記事生成・投稿（手動準備後）

**準備**:
1. `/data/outputs/article_9784123456789.md` を手動作成（ChatGPT使用）
2. `/data/images/thumbnail_9784123456789.png` を手動作成（Bing Image Creator使用）

**実行**:
```bash
python main.py post --isbn 9784123456789
```

**動作**:
- Markdown → HTML変換
- 画像サイズチェック（2MB超えたらリサイズ）
- WordPress REST APIで画像アップロード
- 記事を下書き投稿
- カテゴリ・タグ自動設定

**ログ出力**:
```
[2024-10-24 09:45:23] INFO: 記事を生成しました
[2024-10-24 09:45:28] INFO: 画像をアップロードしました: media_id=456
[2024-10-24 09:45:35] INFO: WordPressに投稿しました（下書き）: https://freetomo.com/?p=12345
```

---

## ISBN形式仕様

### 対応形式
- **ISBN-13（ハイフンなし）**: `9784123456789` ← 推奨
- **ISBN-13（ハイフンあり）**: `978-4-123-45678-9` ← 自動変換
- **ISBN-10**: `4123456789` ← ISBN-13に自動変換

### 内部処理
すべて `normalize_isbn()` 関数でISBN-13（ハイフンなし）に統一

---

## エラーハンドリング

| エラー種別 | ログレベル | ログメッセージ | 対処法 |
|------------|------------|----------------|--------|
| 無効なISBN形式 | ERROR | 無効なISBN形式 | ISBN-10またはISBN-13で入力 |
| 該当ISBN未発見 | ERROR | 該当するISBNが見つかりませんでした | ISBNを確認、手動登録 |
| レビュー0件 | INFO | レビューがありませんでした | 手動でレビュー作成 |
| WordPress認証失敗 | ERROR | WordPress認証失敗 | config.json確認 |
| 画像アップロード失敗 | ERROR | 画像アップロード失敗: {詳細} | 画像形式・サイズ確認 |
| 記事投稿失敗 | ERROR | 記事投稿失敗: {詳細} | WordPress接続確認 |

**リトライ**: なし（エラー時は即座に停止、ログ出力のみ）

---

## 画像処理仕様

| 項目 | 仕様 |
|------|------|
| 対応形式 | PNG固定 |
| ファイルサイズ | 2MB以下 |
| 超過時の処理 | Pillowで自動リサイズ（アスペクト比維持） |
| リサイズ後のログ | `[INFO] 画像をリサイズしました` |

---

## ログ仕様

| 項目 | 内容 |
|------|------|
| 保存先 | `/data/logs/app.log` |
| ログレベル | INFO, ERROR |
| フォーマット | `[日時] レベル: メッセージ` |
| 出力先 | ファイル＋コンソール（両方） |
| ローテーション | なし（追記のみ） |

**ログ確認方法**:
```bash
# Windows
type data\logs\app.log

# エラーのみ抽出（PowerShell）
Select-String -Path data\logs\app.log -Pattern "ERROR"
```

---

## WordPress投稿仕様

| 項目 | 内容 |
|------|------|
| 投稿ステータス | **draft（下書き）固定** |
| カテゴリ | config.jsonの`wp_category_id` |
| タグ | 書籍名・著者名から自動生成 |
| アイキャッチ画像 | `thumbnail_[ISBN].png` を自動設定 |
| 本文形式 | Markdown → HTML自動変換 |

---

## 注意事項

### セキュリティ
- ❌ `config.json` は **絶対にGitにコミットしない**
- ✅ `config.json.example` のみをGitに含める
- ✅ `.gitignore` で `config.json` と `data/` を除外

### API制限
- Google Books API: 1日1000リクエスト（無認証）
- 1日1冊運用なら問題なし
- キャッシュ(`/data/books/`)で重複リクエスト回避

### スクレイピング
- User-Agent設定必須（ブラウザ偽装）
- 各サイトアクセス時に1秒待機（負荷軽減）
- robots.txt尊重

### データバックアップ
- `/data/` ディレクトリは定期的にバックアップ推奨
- 特に `/data/books/` と `/data/outputs/` は重要

---

## トラブルシューティング

### 問題1: 「ModuleNotFoundError: No module named 'requests'」
**原因**: 依存パッケージ未インストール
**解決**:
```bash
pip install -r requirements.txt
```

### 問題2: 「該当するISBNが見つかりませんでした」
**原因**: Google Books APIに書籍情報なし
**解決**:
1. ISBNの入力ミスを確認
2. ISBN-10とISBN-13の両方を試す
3. 手動で `/data/books/book_[ISBN].json` を作成

### 問題3: 「レビューがありませんでした」
**原因**: Bing検索でレビューサイトが見つからない
**解決**:
1. Amazonレビューなどを手動コピー
2. `/data/reviews/review_[ISBN].txt` に保存

### 問題4: 「WordPress認証失敗」
**原因**: config.jsonの認証情報が不正
**解決**:
1. WordPress管理画面でアプリケーションパスワード再発行
2. config.jsonを更新

### 問題5: 「画像ファイルが見つかりません」
**原因**: `/data/images/thumbnail_[ISBN].png` が未作成
**解決**:
1. ファイル名が正確か確認（ISBNが一致しているか）
2. PNG形式で保存されているか確認
3. `/data/images/` ディレクトリが存在するか確認

---

## 拡張性

### 将来的な機能追加案
1. **スケジュール実行**: タスクスケジューラで毎日自動実行
2. **バッチ処理**: 複数ISBNを一括処理
3. **GUI化**: TkinterやPyQt5でGUI作成
4. **データベース化**: SQLiteで書籍情報を一元管理
5. **API化**: Flask/FastAPIでWeb API提供
6. **通知機能**: 投稿完了時にメール/Slack通知

### 追加ディレクトリ案
```
bookpost/
├── ...
├── scripts/          # バッチスクリプト
│   └── daily_post.bat
├── templates/        # 記事テンプレート
│   └── article_template.md
└── database/         # SQLiteデータベース
    └── bookpost.db
```

---

## 開発ガイドライン

### コーディング規約
- Python: PEP 8準拠
- 関数名: snake_case
- クラス名: PascalCase
- 定数: UPPER_SNAKE_CASE
- コメント: 日本語可（関数のdocstringは必須）

### Git運用
- mainブランチ: 安定版
- developブランチ: 開発版
- feature/*ブランチ: 機能追加
- コミットメッセージ: `[add/fix/update] 内容`

### テスト
```bash
# テスト実行（将来的に追加）
python -m pytest tests/
```

---

## パフォーマンス

### 実行時間目安
| 処理 | 所要時間 |
|------|----------|
| fetch（書籍情報取得） | 5秒 |
| fetch（レビュー収集） | 30-60秒 |
| post（記事生成） | 2秒 |
| post（WordPress投稿） | 5-10秒 |
| **合計** | **約1-2分** |

### ボトルネック
- レビュー収集（スクレイピング）: 各サイトアクセスで1秒待機
- 改善案: 並行処理（multiprocessing/asyncio）

---

## 依存パッケージ詳細

### requirements.txt
```txt
# HTTP通信・API
requests>=2.31.0

# HTMLスクレイピング
beautifulsoup4>=4.12.0
lxml>=4.9.0

# Markdown → HTML変換
markdown>=3.5.0

# 画像処理（サイズチェック・リサイズ）
Pillow>=10.0.0
```

### 各パッケージの用途
- **requests**: Google Books API、WordPress REST API通信
- **beautifulsoup4**: HTML解析（レビュー収集）
- **lxml**: HTMLパーサー（高速化）
- **markdown**: Markdown → HTML変換（WordPress投稿用）
- **Pillow**: 画像サイズチェック、2MB超過時のリサイズ

---

## ファイル命名規則

### ISBNの使用
すべてのファイル名に **ISBN-13（ハイフンなし13桁）** を使用

**例**:
```
ISBN入力: 978-4-123-45678-9
↓ normalize_isbn()で変換
内部処理: 9784123456789
↓
ファイル名:
- book_9784123456789.json
- review_9784123456789.txt
- article_9784123456789.md
- thumbnail_9784123456789.png
```

### 命名パターン
| ファイル種別 | パターン | 例 |
|--------------|----------|-----|
| 書籍情報 | `book_[ISBN].json` | `book_9784123456789.json` |
| レビュー | `review_[ISBN].txt` | `review_9784123456789.txt` |
| 記事 | `article_[ISBN].md` | `article_9784123456789.md` |
| 画像 | `thumbnail_[ISBN].png` | `thumbnail_9784123456789.png` |

---

## config.json 詳細仕様

### 必須項目
```json
{
  "wp_url": "https://freetomo.com/wp-json/wp/v2/posts",
  "wp_user": "your_username",
  "wp_app_password": "xxxx xxxx xxxx xxxx xxxx xxxx",
  "wp_category_id": 123
}
```

### オプション項目（将来的に追加可能）
```json
{
  "wp_url": "https://freetomo.com/wp-json/wp/v2/posts",
  "wp_user": "your_username",
  "wp_app_password": "xxxx xxxx xxxx xxxx xxxx xxxx",
  "wp_category_id": 123,
  "wp_default_tags": ["読書", "書評"],
  "google_books_api_key": null,
  "bing_search_api_key": null,
  "max_review_sites": 10,
  "image_max_size_mb": 2,
  "scraping_delay_seconds": 1
}
```

---

## バージョン情報

| バージョン | 日付 | 変更内容 |
|------------|------|----------|
| 1.0.0 | 2024-10-24 | 初版リリース |
| 1.1.0 | 2024-10-24 | 仕様確定版（API認証、ISBN形式、エラーハンドリング、ログ管理追加） |

---

## 関連ドキュメント

- [システム前提](systemZentei.md): 開発環境・API構成
- [運用フロー](unyoFlow.md): 実行手順・タイムライン
- [API仕様書](api.md): 各関数の詳細仕様

---

## ライセンス

MIT License（任意で追加）

---

## 連絡先

プロジェクト管理者: [GitHub - tomo4559](https://github.com/tomo4559)
