# 🔁 運用フロー図（Book Review Auto Poster）

| No | 実施時刻 | 作業名 | 作業概要 | 自動/手動 | 稼働環境 | PGM名 | 関数名 | 使用AI | 入力 | 出力 | AIに流すプロンプト | 実行コマンド |
|----|-----------|---------|-----------|------------|-----------|--------|----------|----------|--------|--------|--------------------|----------------|
| 1 | 9:00 | 新刊・話題書の確認 | 手動で1冊を選定（AmazonやGoogle Booksなど） | 手動 | ブラウザ | - | - | - | Web検索 | 書籍タイトル・ISBN | - | - |
| 2 | 9:15 | 書籍情報を登録 | 選んだ本のタイトル・ISBNを main.py に入力 | 手動 | Windows | main.py | fetch_book_data() | - | タイトル・ISBN | 書籍情報（著者、出版社、概要） | - | `python main.py fetch --isbn [ISBN]` |
| 3 | 9:20 | 書籍レビュー収集 | Bing検索からレビュー要約を自動収集 | 自動 | Windows | main.py | scrape_reviews() | - | ISBNまたはタイトル | `/data/reviews/review_[ISBN].txt` | - | （No2実行時に自動実行） |
| 4a | 9:30 | 要約＋学び＋考察生成（文章AI） | ChatGPTやPerplexityにレビュー要約を渡して記事素材を生成 | 手動（半自動） | ブラウザ | - | - | ChatGPT / Perplexity | `/data/reviews/review_[ISBN].txt` | `/data/outputs/article_[ISBN].md` | 「以下のレビュー要約をもとに、読者が学びを得られる本の紹介記事をMarkdown形式で作ってください。文体は落ち着いた大人向け、約800〜1200文字。」 | ChatGPTなどに貼付 → 出力を `/data/outputs/article_[ISBN].md` に保存 |
| 4b | 9:35 | サムネイル画像生成 | Bing Image CreatorやCanvaなどで紹介用サムネイルを作成 | 手動（半自動） | ブラウザ | - | - | Bing Image Creator / Canva / Leonardo.ai | 書籍タイトル、テーマ | `/data/images/thumbnail_[ISBN].png` | 「『{書籍タイトル}』という本の紹介記事用のサムネイルを作成。テーマは○○、落ち着いた雰囲気、文字入り。」 | 画像ツールに入力 → 出力を `/data/images/thumbnail_[ISBN].png` に保存 |
| 5 | 9:45 | 記事生成 | 要約テキストと画像をMarkdown形式に整形 | 手動（実行） | Windows | main.py | generate_post() | - | `/data/outputs/article_[ISBN].md` + `/data/images/thumbnail_[ISBN].png` | WordPress投稿本文（Markdown） | - | `python main.py post --isbn [ISBN]` |
| 6 | 9:55 | 投稿実行 | WordPress REST APIで本文＋画像を投稿 | 自動 | Windows | main.py | post_to_wp() | - | Markdown本文＋画像ファイル | WordPress記事（公開済） | - | （No5実行時に自動実行） |
