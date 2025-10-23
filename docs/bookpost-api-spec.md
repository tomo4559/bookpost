# 📘 API仕様書

## 概要
本ドキュメントは bookpost プロジェクトの各関数の詳細仕様を定義します。

---

## main.py

### 1. fetch_book_data(isbn: str) -> dict

**用途**: Google Books APIから書籍情報を取得し、キャッシュに保存

**引数**:
| 引数名 | 型 | 必須 | 説明 | 例 |
|--------|-----|------|------|-----|
| isbn | str | ✓ | ISBN-13（ハイフンなし） | "9784123456789" |

**戻り値**:
```json
{
  "isbn": "9784123456789",
  "title": "サンプル書籍",
  "authors": ["著者名1", "著者名2"],
  "publisher": "出版社名",
  "published_date": "2024-01-15",
  "description": "書籍の説明文...",
  "page_count": 320,
  "categories": ["ビジネス", "自己啓発"],
  "image_url": "https://books.google.com/...",
  "language": "ja"
}
```

**処理フロー**:
```
1. ISBNを正規化（ハイフン削除、ISBN-10→13変換）
2. キャッシュファイル確認（/data/books/book_{isbn}.json）
   - 存在する → キャッシュから読み込み、return
3. Google Books API呼び出し
   - URL: https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}
   - 認証: 不要（無料枠）
4. レスポンス解析
   - items[0].volumeInfo から必要情報抽出
5. キャッシュファイルに保存
6. 書籍情報をreturn
```

**エラーハンドリング**:
| エラー種別 | 条件 | 処理 | ログ出力 |
|------------|------|------|----------|
| ISBN不正 | 桁数が10でも13でもない | raise ValueError | ERROR: 無効なISBN形式 |
| API通信エラー | requests.exceptions発生 | raise Exception | ERROR: APIエラー: {詳細} |
| 書籍未発見 | items が空 | raise ValueError | ERROR: 該当するISBNが見つかりませんでした |

**依存関係**:
- `requests`
- `json`
- `os`
- `logging`

**使用例**:
```python
book_data = fetch_book_data("9784123456789")
print(f"書籍名: {book_data['title']}")
```

---

### 2. generate_post(isbn: str) -> dict

**用途**: Markdown記事と画像を読み込み、WordPress投稿用データを生成

**引数**:
| 引数名 | 型 | 必須 | 説明 | 例 |
|--------|-----|------|------|-----|
| isbn | str | ✓ | ISBN-13（ハイフンなし） | "9784123456789" |

**戻り値**:
```json
{
  "title": "記事タイトル",
  "content": "<p>HTML変換後の本文...</p>",
  "status": "draft",
  "categories": [123],
  "tags": [456, 789],
  "featured_media": null
}
```

**処理フロー**:
```
1. 書籍情報読み込み（/data/books/book_{isbn}.json）
2. Markdown記事読み込み（/data/outputs/article_{isbn}.md）
3. 画像ファイル確認（/data/images/thumbnail_{isbn}.png）
   - 存在チェック
   - ファイルサイズチェック（2MB以下）
   - 超過時はPillowでリサイズ
4. Markdown → HTML変換（markdownライブラリ使用）
5. WordPress投稿データ生成
   - title: 書籍タイトル
   - content: HTML本文
   - status: "draft"
   - categories: config.jsonから取得
   - tags: 書籍名・著者名から自動生成
6. 投稿データをreturn
```

**エラーハンドリング**:
| エラー種別 | 条件 | 処理 | ログ出力 |
|------------|------|------|----------|
| 書籍情報なし | book_{isbn}.jsonが存在しない | raise FileNotFoundError | ERROR: 書籍情報が見つかりません |
| 記事ファイルなし | article_{isbn}.mdが存在しない | raise FileNotFoundError | ERROR: 記事ファイルが見つかりません |
| 画像ファイルなし | thumbnail_{isbn}.pngが存在しない | raise FileNotFoundError | ERROR: 画像ファイルが見つかりません |
| 画像サイズ超過 | 2MB超 | 自動リサイズ | INFO: 画像をリサイズしました |

**依存関係**:
- `markdown`
- `Pillow`
- `json`
- `os`
- `logging`

**使用例**:
```python
post_data = generate_post("9784123456789")
print(f"投稿タイトル: {post_data['title']}")
```

---

### 3. post_to_wp(post_data: dict, image_path: str) -> dict

**用途**: WordPress REST APIで記事と画像を投稿

**引数**:
| 引数名 | 型 | 必須 | 説明 | 例 |
|--------|-----|------|------|-----|
| post_data | dict | ✓ | 投稿データ | generate_post()の戻り値 |
| image_path | str | ✓ | 画像ファイルパス | "/data/images/thumbnail_XXX.png" |

**戻り値**:
```json
{
  "id": 12345,
  "link": "https://freetomo.com/2024/10/sample-post/",
  "status": "draft",
  "title": {"rendered": "記事タイトル"}
}
```

**処理フロー**:
```
1. config.json読み込み（WordPress接続情報）
2. 画像アップロード
   - POST https://freetomo.com/wp-json/wp/v2/media
   - Content-Type: image/png
   - Authorization: Basic認証（user + app_password）
   - レスポンスからmedia_idを取得
3. 投稿データにmedia_id設定
   - post_data['featured_media'] = media_id
4. 記事投稿
   - POST https://freetomo.com/wp-json/wp/v2/posts
   - Content-Type: application/json
   - Authorization: Basic認証
5. レスポンスをreturn
```

**エラーハンドリング**:
| エラー種別 | 条件 | 処理 | ログ出力 |
|------------|------|------|----------|
| 認証エラー | 401 Unauthorized | raise Exception | ERROR: WordPress認証失敗 |
| 画像アップロード失敗 | 4xx/5xxエラー | raise Exception | ERROR: 画像アップロード失敗: {詳細} |
| 投稿失敗 | 4xx/5xxエラー | raise Exception | ERROR: 記事投稿失敗: {詳細} |

**依存関係**:
- `requests`
- `json`
- `base64`
- `logging`

**使用例**:
```python
post_data = generate_post("9784123456789")
image_path = "data/images/thumbnail_9784123456789.png"
result = post_to_wp(post_data, image_path)
print(f"投稿URL: {result['link']}")
```

---

## scraper.py

### 4. scrape_reviews(isbn_or_title: str) -> str

**用途**: Bing検索から書評・レビューを収集し、要約テキストを生成

**引数**:
| 引数名 | 型 | 必須 | 説明 | 例 |
|--------|-----|------|------|-----|
| isbn_or_title | str | ✓ | ISBNまたは書籍タイトル | "9784123456789" or "サンプル書籍" |

**戻り値**:
```python
"/data/reviews/review_{isbn}.txt"  # 保存先ファイルパス
```

**処理フロー**:
```
1. Bing検索URL生成
   - https://www.bing.com/search?q={isbn_or_title}+書評+レビュー
2. requests.get()でHTML取得
   - User-Agent設定（ブラウザ偽装）
   - timeout=10秒
3. BeautifulSoupでHTML解析
   - 検索結果のリンクを抽出（上位10件）
4. 各リンクにアクセスしてレビューテキスト収集
   - Amazon、読書メーターなどのサイトから本文抽出
   - 各サイト1秒待機（負荷軽減）
5. 収集したレビューを結合
6. /data/reviews/review_{isbn}.txt に保存
7. ファイルパスをreturn
```

**エラーハンドリング**:
| エラー種別 | 条件 | 処理 | ログ出力 |
|------------|------|------|----------|
| Bing接続エラー | timeout/接続失敗 | raise Exception | ERROR: Bing検索失敗 |
| レビュー0件 | 抽出結果が空 | 空ファイル保存 | INFO: レビューがありませんでした |
| HTML解析エラー | BeautifulSoup失敗 | 部分的にスキップ | WARNING: 一部サイトの解析失敗 |

**依存関係**:
- `requests`
- `beautifulsoup4`
- `lxml`
- `time`
- `logging`

**使用例**:
```python
from scraper import scrape_reviews

review_path = scrape_reviews("9784123456789")
print(f"レビュー保存先: {review_path}")
```

---

## ユーティリティ関数

### 5. normalize_isbn(isbn: str) -> str

**用途**: ISBNを13桁ハイフンなし形式に統一

**引数**:
| 引数名 | 型 | 必須 | 説明 | 例 |
|--------|-----|------|------|-----|
| isbn | str | ✓ | ISBN（任意の形式） | "978-4-123-45678-9" |

**戻り値**:
```python
"9784123456789"  # 13桁ハイフンなし
```

**処理フロー**:
```
1. ハイフン・スペース削除
2. 桁数チェック
   - 13桁 → そのままreturn
   - 10桁 → ISBN-13に変換
     - 先頭に"978"を追加
     - チェックディジット再計算
     - 変換後の13桁をreturn
   - その他 → raise ValueError
```

**エラーハンドリング**:
| エラー種別 | 条件 | 処理 | ログ出力 |
|------------|------|------|----------|
| 桁数不正 | 10桁でも13桁でもない | raise ValueError | ERROR: 無効なISBN形式 |

---

### 6. setup_logger(name: str, log_file: str) -> logging.Logger

**用途**: ログ設定の初期化

**引数**:
| 引数名 | 型 | 必須 | 説明 | 例 |
|--------|-----|------|------|-----|
| name | str | ✓ | ロガー名 | "bookpost" |
| log_file | str | ✓ | ログファイルパス | "/data/logs/app.log" |

**戻り値**:
```python
<logging.Logger object>
```

**処理フロー**:
```
1. ロガー生成（logging.getLogger）
2. ログレベル設定（INFO）
3. ハンドラー設定
   - FileHandler: ログファイル出力
   - StreamHandler: コンソール出力
4. フォーマット設定
   - "[%(asctime)s] %(levelname)s: %(message)s"
5. ロガーをreturn
```

**使用例**:
```python
logger = setup_logger("bookpost", "data/logs/app.log")
logger.info("処理開始")
logger.error("エラー発生")
```

---

## コマンドライン引数

### fetch コマンド

**書式**:
```bash
python main.py fetch --isbn <ISBN>
```

**動作**:
1. `fetch_book_data(isbn)` 実行
2. `scrape_reviews(isbn)` 実行
3. 完了メッセージ表示

**出力例**:
```
[2024-10-24 09:20:15] INFO: 書籍情報を取得しました: サンプル書籍
[2024-10-24 09:20:18] INFO: レビューを収集しました: /data/reviews/review_9784123456789.txt
```

---

### post コマンド

**書式**:
```bash
python main.py post --isbn <ISBN>
```

**動作**:
1. `generate_post(isbn)` 実行
2. `post_to_wp(post_data, image_path)` 実行
3. 投稿URLを表示

**出力例**:
```
[2024-10-24 09:55:32] INFO: 記事を生成しました
[2024-10-24 09:55:45] INFO: WordPressに投稿しました: https://freetomo.com/2024/10/sample-post/
```

---

## config.json 仕様

**ファイルパス**: `/config.json`

**形式**:
```json
{
  "wp_url": "https://freetomo.com/wp-json/wp/v2/posts",
  "wp_user": "your_username",
  "wp_app_password": "xxxx xxxx xxxx xxxx xxxx xxxx",
  "wp_category_id": 123,
  "wp_default_tags": ["読書", "書評"]
}
```

**項目説明**:
| キー | 型 | 必須 | 説明 | 例 |
|------|-----|------|------|-----|
| wp_url | string | ✓ | WordPress REST API URL | "https://freetomo.com/wp-json/wp/v2/posts" |
| wp_user | string | ✓ | WordPressユーザー名 | "admin" |
| wp_app_password | string | ✓ | アプリケーションパスワード | "xxxx xxxx xxxx xxxx" |
| wp_category_id | int | ✓ | 投稿カテゴリID（読書レビュー） | 123 |
| wp_default_tags | array | - | デフォルトタグ（任意） | ["読書", "書評"] |

---

## ディレクトリ構成（データファイル）

### /data/books/
**内容**: 書籍情報キャッシュ
```
book_9784123456789.json
book_9784987654321.json
```

### /data/reviews/
**内容**: 収集したレビュー要約
```
review_9784123456789.txt
review_9784987654321.txt
```

### /data/outputs/
**内容**: 生成した記事（Markdown）
```
article_9784123456789.md
article_9784987654321.md
```

### /data/images/
**内容**: サムネイル画像
```
thumbnail_9784123456789.png
thumbnail_9784987654321.png
```

### /data/logs/
**内容**: 実行ログ
```
app.log  # 全てのログが追記される
```

---

## 外部API仕様

### Google Books API

**エンドポイント**:
```
GET https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}
```

**認証**: なし（無料枠）

**レスポンス例**:
```json
{
  "items": [
    {
      "volumeInfo": {
        "title": "サンプル書籍",
        "authors": ["著者名"],
        "publisher": "出版社",
        "publishedDate": "2024-01-15",
        "description": "説明文...",
        "pageCount": 320,
        "categories": ["ビジネス"],
        "imageLinks": {
          "thumbnail": "https://..."
        },
        "language": "ja"
      }
    }
  ]
}
```

---

### WordPress REST API

#### 画像アップロード

**エンドポイント**:
```
POST https://freetomo.com/wp-json/wp/v2/media
```

**ヘッダー**:
```
Content-Type: image/png
Content-Disposition: attachment; filename="thumbnail.png"
Authorization: Basic {base64(user:app_password)}
```

**レスポンス例**:
```json
{
  "id": 456,
  "source_url": "https://freetomo.com/wp-content/uploads/2024/10/thumbnail.png"
}
```

#### 記事投稿

**エンドポイント**:
```
POST https://freetomo.com/wp-json/wp/v2/posts
```

**ヘッダー**:
```
Content-Type: application/json
Authorization: Basic {base64(user:app_password)}
```

**リクエストボディ**:
```json
{
  "title": "記事タイトル",
  "content": "<p>本文...</p>",
  "status": "draft",
  "categories": [123],
  "tags": [456, 789],
  "featured_media": 456
}
```

**レスポンス例**:
```json
{
  "id": 12345,
  "link": "https://freetomo.com/2024/10/sample-post/",
  "status": "draft"
}
```

---

## エラーコード一覧

| コード | 説明 | 対処法 |
|--------|------|--------|
| E001 | 無効なISBN形式 | ISBN-10またはISBN-13の形式で入力 |
| E002 | 該当するISBNが見つかりませんでした | ISBNを確認、または手動で書籍情報を登録 |
| E003 | レビューがありませんでした | 手動でレビュー要約を作成 |
| E004 | WordPress認証失敗 | config.jsonの認証情報を確認 |
| E005 | 画像アップロード失敗 | 画像ファイルサイズ・形式を確認 |
| E006 | 記事投稿失敗 | WordPress接続・権限を確認 |

---

## バージョン情報

| バージョン | 日付 | 変更内容 |
|------------|------|----------|
| 1.0.0 | 2024-10-24 | 初版リリース |
