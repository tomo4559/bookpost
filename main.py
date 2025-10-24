#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
bookpost - Book Review Auto Poster
メインプログラム（試作版：WordPress投稿前まで）
"""

import os
import sys
import json
import logging
import argparse
import requests
from pathlib import Path

# scraper.pyから関数をインポート
from scraper import scrape_reviews


def setup_logger(name="bookpost", log_file="data/logs/app.log"):
    """
    ログ設定の初期化
    
    Args:
        name: ロガー名
        log_file: ログファイルパス
    
    Returns:
        logging.Logger: 設定済みロガー
    """
    # ログディレクトリ作成
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # ロガー設定
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 既存のハンドラーをクリア（重複防止）
    if logger.handlers:
        logger.handlers.clear()
    
    # フォーマット設定
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
    
    # ファイルハンドラー
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # コンソールハンドラー
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def normalize_isbn(isbn):
    """
    ISBNを13桁ハイフンなし形式に統一
    
    Args:
        isbn: ISBN文字列（10桁または13桁、ハイフンあり/なし）
    
    Returns:
        str: ISBN-13（ハイフンなし13桁）
    
    Raises:
        ValueError: ISBNが10桁でも13桁でもない場合
    """
    # ハイフン・スペース削除
    isbn_clean = isbn.replace('-', '').replace(' ', '')
    
    if len(isbn_clean) == 13:
        # すでにISBN-13
        return isbn_clean
    elif len(isbn_clean) == 10:
        # ISBN-10 → ISBN-13変換
        isbn13 = '978' + isbn_clean[:-1]  # 先頭に978を追加、チェックディジット削除
        
        # チェックディジット再計算
        check_digit = calculate_isbn13_check_digit(isbn13)
        return isbn13 + str(check_digit)
    else:
        raise ValueError(f"無効なISBN形式: {isbn}（10桁または13桁である必要があります）")


def calculate_isbn13_check_digit(isbn12):
    """
    ISBN-13のチェックディジットを計算
    
    Args:
        isbn12: ISBN-13の最初の12桁
    
    Returns:
        int: チェックディジット（0-9）
    """
    total = 0
    for i, digit in enumerate(isbn12):
        weight = 1 if i % 2 == 0 else 3
        total += int(digit) * weight
    
    check_digit = (10 - (total % 10)) % 10
    return check_digit


def fetch_book_data(isbn, logger):
    """
    Google Books APIから書籍情報を取得し、キャッシュに保存
    
    Args:
        isbn: ISBN-13（ハイフンなし）
        logger: ロガー
    
    Returns:
        dict: 書籍情報
    
    Raises:
        ValueError: ISBNが見つからない場合
        Exception: API通信エラー
    """
    # ISBNを正規化
    isbn_normalized = normalize_isbn(isbn)
    logger.info(f"ISBN正規化: {isbn} → {isbn_normalized}")
    
    # キャッシュファイルパス
    cache_dir = "data/books"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    
    cache_path = os.path.join(cache_dir, f"book_{isbn_normalized}.json")
    
    # キャッシュがあれば読み込み
    if os.path.exists(cache_path):
        logger.info(f"キャッシュから読み込み: {cache_path}")
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # Google Books API呼び出し
    logger.info(f"Google Books APIから取得中: ISBN={isbn_normalized}")
    api_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn_normalized}"
    
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'items' not in data or len(data['items']) == 0:
            logger.error(f"該当するISBNが見つかりませんでした: {isbn_normalized}")
            raise ValueError(f"該当するISBNが見つかりませんでした: {isbn_normalized}")
        
        # 書籍情報を抽出
        volume_info = data['items'][0]['volumeInfo']
        book_data = {
            'isbn': isbn_normalized,
            'title': volume_info.get('title', ''),
            'authors': volume_info.get('authors', []),
            'publisher': volume_info.get('publisher', ''),
            'published_date': volume_info.get('publishedDate', ''),
            'description': volume_info.get('description', ''),
            'page_count': volume_info.get('pageCount', 0),
            'categories': volume_info.get('categories', []),
            'image_url': volume_info.get('imageLinks', {}).get('thumbnail', ''),
            'language': volume_info.get('language', 'ja')
        }
        
        logger.info(f"書籍情報を取得しました: {book_data['title']}")
        
        # キャッシュに保存
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(book_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"キャッシュに保存しました: {cache_path}")
        
        return book_data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"APIエラー: {e}")
        raise Exception(f"Google Books API通信エラー: {e}")


def cmd_fetch(args, logger):
    """
    fetchコマンドの実行
    書籍情報取得 + レビュー収集
    
    Args:
        args: コマンドライン引数
        logger: ロガー
    """
    isbn = args.isbn
    logger.info(f"=== fetch開始: ISBN={isbn} ===")
    
    try:
        # 1. 書籍情報取得
        book_data = fetch_book_data(isbn, logger)
        isbn_normalized = book_data['isbn']
        
        # 2. レビュー収集
        logger.info("レビュー収集を開始します...")
        review_path = scrape_reviews(isbn_normalized, logger)
        
        logger.info(f"=== fetch完了 ===")
        logger.info(f"書籍情報: data/books/book_{isbn_normalized}.json")
        logger.info(f"レビュー: {review_path}")
        
        print("\n" + "="*50)
        print("✅ 書籍情報とレビューの取得が完了しました")
        print("="*50)
        print(f"📖 書籍名: {book_data['title']}")
        print(f"✍️  著者: {', '.join(book_data['authors'])}")
        print(f"📅 出版日: {book_data['published_date']}")
        print(f"📄 レビュー保存先: {review_path}")
        print("\n次のステップ:")
        print("1. ChatGPT/Perplexityで記事を生成")
        print(f"   入力: {review_path}")
        print(f"   出力: data/outputs/article_{isbn_normalized}.md")
        print("2. 画像を生成")
        print(f"   出力: data/images/thumbnail_{isbn_normalized}.png")
        print(f"3. 投稿コマンドを実行")
        print(f"   python main.py post --isbn {isbn_normalized}")
        
    except Exception as e:
        logger.error(f"fetchエラー: {e}")
        print(f"\n❌ エラーが発生しました: {e}")
        sys.exit(1)


def cmd_post(args, logger):
    """
    postコマンドの実行（試作版：ファイル確認のみ）
    記事生成準備 + ファイル確認
    
    Args:
        args: コマンドライン引数
        logger: ロガー
    """
    isbn = normalize_isbn(args.isbn)
    logger.info(f"=== post開始（試作版）: ISBN={isbn} ===")
    
    try:
        # 必要なファイルの存在確認
        book_path = f"data/books/book_{isbn}.json"
        article_path = f"data/outputs/article_{isbn}.md"
        image_path = f"data/images/thumbnail_{isbn}.png"
        
        # 書籍情報確認
        if not os.path.exists(book_path):
            raise FileNotFoundError(f"書籍情報が見つかりません: {book_path}")
        
        with open(book_path, 'r', encoding='utf-8') as f:
            book_data = json.load(f)
        
        logger.info(f"✅ 書籍情報: {book_path}")
        
        # 記事ファイル確認
        if not os.path.exists(article_path):
            raise FileNotFoundError(f"記事ファイルが見つかりません: {article_path}\n"
                                    f"ChatGPT/Perplexityで記事を生成してください")
        
        with open(article_path, 'r', encoding='utf-8') as f:
            article_content = f.read()
        
        logger.info(f"✅ 記事ファイル: {article_path} ({len(article_content)}文字)")
        
        # 画像ファイル確認
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"画像ファイルが見つかりません: {image_path}\n"
                                    f"Bing Image Creator等で画像を生成してください")
        
        # 画像サイズチェック
        image_size_mb = os.path.getsize(image_path) / (1024 * 1024)
        logger.info(f"✅ 画像ファイル: {image_path} ({image_size_mb:.2f}MB)")
        
        if image_size_mb > 2:
            logger.warning(f"⚠️  画像サイズが2MBを超えています: {image_size_mb:.2f}MB")
            logger.info("（本番実装時は自動リサイズします）")
        
        # 結果表示
        print("\n" + "="*50)
        print("✅ 投稿準備ファイルの確認が完了しました")
        print("="*50)
        print(f"📖 書籍名: {book_data['title']}")
        print(f"✍️  著者: {', '.join(book_data['authors'])}")
        print(f"📄 記事文字数: {len(article_content)}文字")
        print(f"🖼️  画像サイズ: {image_size_mb:.2f}MB")
        print("\n確認完了したファイル:")
        print(f"  ✅ {book_path}")
        print(f"  ✅ {article_path}")
        print(f"  ✅ {image_path}")
        print("\n【試作版】WordPress投稿機能は未実装です")
        print("次のフェーズで実装します")
        
        logger.info("=== post確認完了 ===")
        
    except FileNotFoundError as e:
        logger.error(f"ファイルエラー: {e}")
        print(f"\n❌ {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"postエラー: {e}")
        print(f"\n❌ エラーが発生しました: {e}")
        sys.exit(1)


def main():
    """メイン関数"""
    # ロガー初期化
    logger = setup_logger()
    
    # コマンドライン引数パーサー
    parser = argparse.ArgumentParser(
        description='bookpost - Book Review Auto Poster (試作版)',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='実行コマンド')
    
    # fetchコマンド
    parser_fetch = subparsers.add_parser(
        'fetch',
        help='書籍情報取得 + レビュー収集'
    )
    parser_fetch.add_argument(
        '--isbn',
        required=True,
        help='ISBN-13（ハイフンあり/なし可）'
    )
    
    # postコマンド
    parser_post = subparsers.add_parser(
        'post',
        help='記事生成準備 + ファイル確認（試作版）'
    )
    parser_post.add_argument(
        '--isbn',
        required=True,
        help='ISBN-13（ハイフンあり/なし可）'
    )
    
    # 引数解析
    args = parser.parse_args()
    
    # コマンド実行
    if args.command == 'fetch':
        cmd_fetch(args, logger)
    elif args.command == 'post':
        cmd_post(args, logger)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
