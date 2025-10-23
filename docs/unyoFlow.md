# 🔁 運用フロー図（Book Review Auto Poster）

| No | 実施時刻 | 作業名 | 作業概要 | 自動/手動 | 稼働環境 | PGM名 | 関数名 | 使用AI | 入力 | 出力 | AIに流すプロンプト | 実行コマンド |
|----|-----------|---------|-----------|------------|-----------|--------|----------|----------|--------|--------|--------------------|----------------|
| 1 | 9:00 | 新刊・話題書の確認 | 手動で1冊を選定（AmazonやGoogle Booksなど） | 手動 | ブラウザ | - | - | - | Web検索 | 書籍タイトル・ISBN-13 | - | - |
| 2 | 9:15 | 書籍情報を登録 | 選んだ本のISBN-13を main.py に入力して実行 | 自動 | Windows | main.py | fetch_book_data() | - | ISBN-13（ハイフンなし） | `/data/books/book_{isbn}.json` | - | `python main.py fetch --isbn 9784123456789` |
| 3 | 9:20 | 書籍レビュー収集 | Bing検索からレビュー要約を自動収集（スクレイピング） | 自動 | Windows | scraper.py | scrape_reviews() | - | ISBN-13 | `/data/reviews/review_{isbn}.txt` | - | （No2実行時に自動実行） |
| 4a | 9:30 | 要約＋学び＋考察生成（文章AI） | ChatGPTやPerplexityにレビュー要約を渡して記事素材を生成 | 手動（半自動） | ブラウザ | - | - | ChatGPT / Perplexity | `/data/reviews/review_{isbn}.txt` | `/data/outputs/article_{isbn}.md` | 「以下のレビュー要約をもとに、読者が学びを得られる本の紹介記事をMarkdown形式で作ってください。文体は落ち着いた大人向け、約800〜1200文字。」 | ChatGPTなどに貼付 → 出力を `/data/outputs/article_{isbn}.md` に保存 |
| 4b | 9:35 | サムネイル画像生成 | Bing Image CreatorやCanvaなどで紹介用サムネイルを作成 | 手動（半自動） | ブラウザ | - | - | Bing Image Creator / Canva / Leonardo.ai | 書籍タイトル、テーマ | `/data/images/thumbnail_{isbn}.png` | 「『{書籍タイトル}』という本の紹介記事用のサムネイルを作成。テーマは○○、落ち着いた雰囲気、文字入り。」 | 画像ツールに入力 → 出力を `/data/images/thumbnail_{isbn}.png` に保存（PNG形式、2MB以下） |
| 5 | 9:45 | 記事生成 | 要約テキストと画像をMarkdown → HTML変換し、WordPress投稿データ作成 | 自動 | Windows | main.py | generate_post() | - | `/data/outputs/article_{isbn}.md` + `/data/images/thumbnail_{isbn}.png` + `/data/books/book_{isbn}.json` | WordPress投稿データ（JSON） | - | `python main.py post --isbn 9784123456789` |
| 6 | 9:55 | 投稿実行 | WordPress REST APIで本文＋画像をdraft（下書き）投稿 | 自動 | Windows | main.py | post_to_wp() | - | 投稿データ（JSON）＋画像ファイル | WordPress記事（下書き保存） | - | （No5実行時に自動実行） |

---

## フロー補足説明

### No.1: 新刊・話題書の確認
- **作業者**: 運用担当者
- **選定基準**: 新刊、ベストセラー、話題書、専門書など
- **確認サイト**: Amazon、Google Books、出版社サイトなど
- **取得情報**: 書籍タイトル、**ISBN-13**（ハイフンあり/なしどちらでもOK）

### No.2: 書籍情報を登録
- **実行内容**:
  1. Google Books APIから書籍情報取得
  2. ISBN-10入力時は自動でISBN-13に変換
  3. `/data/books/book_{isbn}.json` にキャッシュ保存
- **エラー時**: ログ出力「該当するISBNが見つかりませんでした」

### No.3: 書籍レビュー収集
- **実行内容**:
  1. Bing検索で「{isbn} 書評 レビュー」を検索
  2. 上位10件のサイトからレビューテキストをスクレイピング
  3. `/data/reviews/review_{isbn}.txt` に保存
- **対象サイト例**: Amazon、読書メーター、ブクログ、はてなブックマークなど
- **エラー時**: ログ出力「レビューがありませんでした」（空ファイル保存）

### No.4a: 要約＋学び＋考察生成
- **使用AI**: ChatGPT（無料版可）、Perplexity、Claude など
- **プロンプト例**:
```
以下のレビュー要約をもとに、読者が学びを得られる本の紹介記事を
Markdown形式で作ってください。

【構成】
# {書籍タイトル}
## この本の概要
## 読んで得られる3つの学び
## 誰におすすめか
## まとめ

【条件】
- 文体: 落ち着いた大人向け
- 文字数: 800〜1200文字
- 引用は「>」で表現

---
{レビュー要約テキストをここに貼付}
```
- **保存方法**: AI出力をコピー → `/data/outputs/article_{isbn}.md` に手動保存

### No.4b: サムネイル画像生成
- **使用ツール**: Bing Image Creator（無料）、Canva、Leonardo.ai など
- **プロンプト例**:
```
「{書籍タイトル}」という本の紹介記事用のサムネイル画像を作成。
テーマは{ビジネス/自己啓発/小説など}、落ち着いた雰囲気、
書籍タイトル文字入り、16:9比率。
```
- **保存方法**: 生成画像をダウンロード → `/data/images/thumbnail_{isbn}.png` に保存
- **注意事項**: 
  - PNG形式必須
  - 2MB以下（超過時は自動リサイズ）

### No.5: 記事生成
- **実行内容**:
  1. `/data/outputs/article_{isbn}.md` 読み込み
  2. Markdown → HTML変換（markdownライブラリ使用）
  3. `/data/images/thumbnail_{isbn}.png` 読み込み（サイズチェック）
  4. `/data/books/book_{isbn}.json` から書籍情報読み込み
  5. WordPress投稿データ生成
     - title: 書籍タイトル
     - content: HTML本文
     - status: "draft"
     - categories: config.jsonのwp_category_id
     - tags: 書籍名・著者名から自動生成
- **エラー時**: ファイル未存在時はログ出力して中断

### No.6: 投稿実行
- **実行内容**:
  1. 画像アップロード（WordPress REST API）
     - エンドポイント: `/wp-json/wp/v2/media`
     - 認証: Basic（user + app_password）
     - レスポンスからmedia_id取得
  2. 記事投稿（WordPress REST API）
     - エンドポイント: `/wp-json/wp/v2/posts`
     - featured_media: 上記のmedia_id
     - status: "draft"（下書き）
  3. 投稿URLをログ出力
- **エラー時**: ログ出力「記事投稿失敗: {詳細}」

---

## 実行例（完全フロー）

### Step1: 書籍選定（手動）
```
Amazon で新刊チェック → ISBN-13取得: 9784123456789
```

### Step2: 書籍情報取得＋レビュー収集（自動）
```bash
python main.py fetch --isbn 9784123456789
```
**出力**:
```
[2024-10-24 09:15:32] INFO: 書籍情報を取得しました: サンプル書籍
[2024-10-24 09:15:35] INFO: キャッシュに保存しました: /data/books/book_9784123456789.json
[2024-10-24 09:20:12] INFO: レビューを収集しました: /data/reviews/review_9784123456789.txt
```

### Step3: 記事生成（手動）
1. `/data/reviews/review_9784123456789.txt` を開く
2. ChatGPTにプロンプト＋レビュー要約を貼付
3. 出力されたMarkdownを `/data/outputs/article_9784123456789.md` に保存

### Step4: 画像生成（手動）
1. Bing Image Creator でプロンプト入力
2. 生成画像を `/data/images/thumbnail_9784123456789.png` に保存

### Step5: WordPress投稿（自動）
```bash
python main.py post --isbn 9784123456789
```
**出力**:
```
[2024-10-24 09:45:23] INFO: 記事を生成しました
[2024-10-24 09:45:28] INFO: 画像をアップロードしました: media_id=456
[2024-10-24 09:45:35] INFO: WordPressに投稿しました（下書き）: https://freetomo.com/?p=12345
```

---

## タイムライン（想定所要時間）

| 時間帯 | 作業 | 所要時間 |
|--------|------|----------|
| 9:00-9:15 | 書籍選定（手動） | 15分 |
| 9:15-9:25 | 書籍情報＋レビュー収集（自動） | 10分 |
| 9:25-9:40 | 記事生成（ChatGPT手動操作） | 15分 |
| 9:40-9:50 | 画像生成（手動操作） | 10分 |
| 9:50-10:00 | WordPress投稿（自動） | 10分 |
| **合計** | | **60分** |

---

## エラー対応フロー

### エラー1: 「該当するISBNが見つかりませんでした」
**原因**: Google Books APIに書籍情報なし
**対応**: 
1. ISBNの入力ミスを確認
2. 別のISBN（ISBN-10 ↔ ISBN-13）で再試行
3. それでもダメなら手動で書籍情報を作成

### エラー2: 「レビューがありませんでした」
**原因**: Bing検索でレビューサイトが見つからない
**対応**: 
1. 手動でAmazonレビューなどをコピー
2. `/data/reviews/review_{isbn}.txt` に手動保存
3. No.4aに進む

### エラー3: 「記事ファイルが見つかりません」
**原因**: `/data/outputs/article_{isbn}.md` が未作成
**対応**: 
1. No.4aの手順を再確認
2. ファイル名が `article_{isbn}.md` と一致しているか確認

### エラー4: 「画像ファイルが見つかりません」
**原因**: `/data/images/thumbnail_{isbn}.png` が未作成
**対応**: 
1. No.4bの手順を再確認
2. ファイル名が `thumbnail_{isbn}.png` と一致しているか確認
3. PNG形式で保存されているか確認

### エラー5: 「WordPress認証失敗」
**原因**: config.jsonの認証情報が不正
**対応**: 
1. WordPress管理画面でアプリケーションパスワード再発行
2. config.jsonの `wp_user`, `wp_app_password` を更新

---

## 運用Tips

### Tip1: 複数冊を連続処理したい場合
```bash
# 書籍A
python main.py fetch --isbn 9784111111111
# → 手動で記事・画像作成
python main.py post --isbn 9784111111111

# 書籍B
python main.py fetch --isbn 9784222222222
# → 手動で記事・画像作成
python main.py post --isbn 9784222222222
```

### Tip2: 下書き投稿後の確認
1. WordPress管理画面にログイン
2. 投稿 → 下書き一覧を確認
3. 内容確認後、手動で「公開」ボタンをクリック

### Tip3: ログ確認
```bash
# 最新ログを確認
type data\logs\app.log

# エラーのみ抽出（PowerShell）
Select-String -Path data\logs\app.log -Pattern "ERROR"
```

---

## バージョン情報
| バージョン | 日付 | 変更内容 |
|------------|------|----------|
| 1.0.0 | 2024-10-24 | 初版リリース |
| 1.1.0 | 2024-10-24 | 仕様確定版（ISBN-13統一、draft投稿、エラーフロー追加） |
