# 📚 bookpost - Book Review Auto Poster

書籍レビュー記事の自動投稿システム。ISBN入力から書籍情報取得、レビュー収集、記事生成補助、WordPress投稿までを半自動化します。

## ✨ 特徴

- 📖 **ISBN入力だけで書籍情報取得**（Google Books API）
- 🔍 **レビュー自動収集**（Bing検索スクレイピング）
- ✍️ **AI記事生成補助**（ChatGPT/Perplexity連携）
- 🖼️ **画像自動アップロード**（WordPress REST API）
- 📝 **下書き自動投稿**（カテゴリ・タグ自動設定）
- 🆓 **完全無料運用可能**（無料APIのみ使用）

## 🎯 対象ユーザー

- 読書ブログを運営している方
- 書評記事を定期的に投稿したい方
- WordPressサイトを持っている方
- Python実行環境がある方（Windows推奨）

## 📋 前提条件

| 項目 | 要件 |
|------|------|
| OS | Windows 11（推奨）、macOS、Linux |
| Python | 3.13以降 |
| WordPress | REST API有効、アプリケーションパスワード設定済み |
| 外部サービス | ChatGPT/Perplexity（無料版可）、Bing Image Creator |

## 🚀 セットアップ

### 1. リポジトリクローン

```bash
git clone https://github.com/tomo4559/bookpost.git
cd bookpost
```

### 2. 仮想環境作成（推奨）

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 依存パッケージインストール

```bash
pip install -r requirements.txt
```

### 4. 設定ファイル作成

```bash
# Windowsの場合
copy config.json.example config.json

# macOS/Linuxの場合
cp config.json.example config.json
```

`config.json` を編集して以下を設定：

```json
{
  "wp_url": "https://your-site.com/wp-json/wp/v2/posts",
  "wp_user": "your_username",
  "wp_app_password": "xxxx xxxx xxxx xxxx xxxx xxxx",
  "wp_category_id": 123,
  "wp_default_tags": ["読書", "書評"]
}
```

#### WordPress設定方法

**アプリケーションパスワード取得**:
1. WordPress管理画面 → ユーザー → プロフィール
2. 「アプリケーションパスワード」セクションで新規作成
3. 生成されたパスワードを `config.json` の `wp_app_password` に貼付

**カテゴリID取得**:
1. WordPress管理画面 → 投稿 → カテゴリー
2. 「読書レビュー」カテゴリをクリック
3. ブラウザURLの `tag_ID=XXX` の部分が `wp_category_id`

### 5. データディレクトリ作成

```bash
# Windows
mkdir data\books data\reviews data\outputs data\images data\logs

# macOS/Linux
mkdir -p data/{books,reviews,outputs,images,logs}
```

## 📖 使い方

### 基本ワークフロー（所要時間: 約60分）

#### Step1: 書籍選定（手動・15分）
AmazonやGoogle Booksで書籍を選び、ISBN-13を取得

#### Step2: 書籍情報・レビュー収集（自動・10分）
```bash
python main.py fetch --isbn 9784123456789
```

**実行内容**:
- Google Books APIから書籍情報取得
- `/data/books/book_9784123456789.json` に保存
- Bing検索からレビュー収集
- `/data/reviews/review_9784123456789.txt` に保存

#### Step3: 記事生成（手動・15分）
1. `/data/reviews/review_9784123456789.txt` を開く
2. ChatGPT/Perplexityに以下を入力:

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

---
{レビュー要約をここに貼付}
```

3. 出力されたMarkdownを `/data/outputs/article_9784123456789.md` に保存

#### Step4: 画像生成（手動・10分）
Bing Image Creator、Canva、Leonardo.aiなどで画像を生成し、
`/data/images/thumbnail_9784123456789.png` に保存（PNG形式、2MB以下）

#### Step5: WordPress投稿（自動・10分）
```bash
python main.py post --isbn 9784123456789
```

**実行内容**:
- Markdown → HTML変換
- 画像を自動アップロード（WordPress REST API）
- 記事を下書き投稿
- カテゴリ・タグ自動設定

投稿後、WordPress管理画面で下書きを確認して公開ボタンをクリック

## 📂 ディレクトリ構成

```
bookpost/
├── main.py                    # メイン実行ファイル
├── scraper.py                 # レビュー収集モジュール
├── config.json                # WordPress接続設定
├── requirements.txt           # 依存パッケージ
├── README.md                  # 本ファイル
├── docs/                      # ドキュメント
│   ├── systemZentei.md        # システム前提
│   ├── unyoFlow.md            # 運用フロー
│   ├── folder.md              # フォルダ構成
│   └── api.md                 # API仕様書
└── data/                      # データ保存（Git除外）
    ├── books/                 # 書籍情報キャッシュ
    ├── reviews/               # レビュー要約
    ├── outputs/               # 生成記事
    ├── images/                # サムネイル画像
    └── logs/                  # 実行ログ
```

## 🔧 コマンドリファレンス

### 書籍情報取得＋レビュー収集
```bash
python main.py fetch --isbn <ISBN-13>
```

**例**:
```bash
python main.py fetch --isbn 9784123456789
```

### WordPress投稿
```bash
python main.py post --isbn <ISBN-13>
```

**例**:
```bash
python main.py post --isbn 9784123456789
```

## 📝 ISBN形式

- **推奨**: ISBN-13（ハイフンなし） - `9784123456789`
- **対応**: ISBN-13（ハイフンあり） - `978-4-123-45678-9`
- **対応**: ISBN-10 - `4123456789`（自動でISBN-13に変換）

## ⚠️ 注意事項

### セキュリティ
- ❌ `config.json` は**絶対にGitにコミットしない**
- ✅ `.gitignore` で除外済み
- ✅ `config.json.example` をテンプレートとして使用

### API制限
- **Google Books API**: 1日1000リクエスト（無認証）
- **1日1冊運用なら問題なし**
- キャッシュ機能で重複リクエスト回避

### WordPress投稿
- **常に下書き保存**（自動公開なし）
- 内容確認後、手動で公開
- カテゴリ・タグは自動設定

### 画像
- **PNG形式のみ対応**
- **2MB以下**（超過時は自動リサイズ）

## 🐛 トラブルシューティング

### 「ModuleNotFoundError」が出る
```bash
pip install -r requirements.txt
```

### 「該当するISBNが見つかりませんでした」
1. ISBNの入力ミスを確認
2. ISBN-10とISBN-13の両方を試す
3. 手動で `/data/books/book_{isbn}.json` を作成

### 「WordPress認証失敗」
1. WordPress管理画面でアプリケーションパスワード再発行
2. `config.json` を更新

### 「レビューがありませんでした」
1. Amazonレビューなどを手動コピー
2. `/data/reviews/review_{isbn}.txt` に保存

### ログ確認
```bash
# Windows
type data\logs\app.log

# macOS/Linux
cat data/logs/app.log

# エラーのみ抽出（PowerShell）
Select-String -Path data\logs\app.log -Pattern "ERROR"
```

## 📊 パフォーマンス

| 処理 | 所要時間 |
|------|----------|
| 書籍情報取得 | 5秒 |
| レビュー収集 | 30-60秒 |
| 記事生成 | 2秒 |
| WordPress投稿 | 5-10秒 |
| **合計** | **約1-2分** |

## 🔄 更新履歴

| バージョン | 日付 | 変更内容 |
|------------|------|----------|
| 1.0.0 | 2024-10-24 | 初版リリース |
| 1.1.0 | 2024-10-24 | 仕様確定版 |

## 📚 ドキュメント

- [システム前提](docs/systemZentei.md): 開発環境・API構成
- [運用フロー](docs/unyoFlow.md): 詳細な実行手順
- [フォルダ構成](docs/folder.md): ディレクトリ構造
- [API仕様書](docs/api.md): 関数仕様・エラー処理

## 🤝 コントリビューション

Issue・Pull Requestは大歓迎です！

1. このリポジトリをFork
2. Feature Branchを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をCommit (`git commit -m '[add] amazing feature'`)
4. BranchをPush (`git push origin feature/amazing-feature`)
5. Pull Requestを作成

## 📄 ライセンス

MIT License

## 👤 作者

**tomo4559**
- GitHub: [@tomo4559](https://github.com/tomo4559)
- Website: [freetomo.com](https://freetomo.com/)

## 🙏 謝辞

- Google Books API
- WordPress REST API
- Python Community

---

**Happy Book Reviewing! 📚✨**
