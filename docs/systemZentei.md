# ⚙️ システム前提

## 開発・運用環境
| 項目 | 内容 |
|------|------|
| OS | Windows 11 |
| Pythonバージョン | 3.13 |
| 実行方法 | コマンドプロンプトまたはPowerShell |
| 実行頻度 | 手動（1冊選定ごと） |

---

## 外部サービス・API構成
| 区分 | サービス名 | 用途 | 接続方法 |
|------|-------------|------|-----------|
| 書籍情報取得 | Google Books API | ISBN・書誌情報の取得 | main.py → fetch_book_data() |
| レビュー収集 | Bing Search | 書評要約の収集 | scraper.py |
| 記事生成 | ChatGPT / Perplexity | レビュー要約からMarkdown記事生成 | 手動（ブラウザ貼付） |
| 画像生成 | Bing Image Creator / Canva / Leonardo.ai | 記事用サムネイル画像生成 | 手動（ブラウザ操作） |
| 投稿処理 | WordPress REST API | 記事本文＋画像投稿 | main.py → post_to_wp() |

---

## WordPress設定
| 項目 | 内容 |
|------|------|
| 投稿サイト | https://freetomo.com/ |
| 投稿カテゴリ | 読書レビュー |
| 投稿形式 | Markdown（自動変換して投稿） |
| 接続方式 | REST API + アプリケーションパスワード |
| 設定ファイル | `config.json` に保存（例：`wp_url`, `wp_user`, `wp_app_password`） |

---

## 注意点
- API課金はすべて無料プランを利用（ChatGPT以外も可）
- OpenAI APIは使用せず、手動操作でAIにプロンプトを投入
- 出力結果（.md / .png）は `/data/` 配下に必ず保存
- WordPress投稿は main.py 実行時に自動投稿まで完結
