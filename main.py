#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
bookpost - Book Review Auto Poster
メインプログラム（統合版）
"""

import os
import sys
import json
import logging
import argparse
import requests
import time
from bs4 import BeautifulSoup
from pathlib import Path

print("プログラム起動...")  # デバッグ用

def setup_logger(name="bookpost", log_file="data/logs/app.log"):
    """ログ設定の初期化"""
    print(f"ロガー初期化: {log_file}")
    
    # ログディレクトリ作成
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f"ログディレクトリ作成: {log_dir}")
    
    # ロガー設定
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 既存のハンドラーをクリア
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
    """ISBNを13桁ハイフンなし形式に統一"""
    isbn_clean = isbn.replace('-', '').replace(' ', '')
    
    if len(isbn_clean) == 13:
        return isbn_clean
    elif len(isbn_clean) == 10:
        isbn13 = '978' + isbn_clean[:-1]
        check_digit = calculate_isbn13_check_digit(isbn13)
        return isbn13 + str(check_digit)
    else:
        raise ValueError(f"無効なISBN形式: {isbn}")


def calculate_isbn13_check_digit(isbn12):
    """ISBN-13のチェックディジットを計算"""
    total = 0
    for i, digit in enumerate(isbn12):
        weight = 1 if i % 2 == 0 else 3
        total += int(digit) * weight
    check_digit = (10 - (total % 10)) % 10
    return check_digit


def fetch_book_data(isbn, logger):
    """Google Books APIから書籍情報を取得"""
    isbn_normalized = normalize_isbn(isbn)
    logger.info(f"ISBN正規化: {isbn} → {isbn_normalized}")
    
    # キャッシュディレクトリ作成
    cache_dir = "data/books"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
        logger.info(f"ディレクトリ作成: {cache_dir}")
    
    cache_path = os.path.join(cache_dir, f"book_{isbn_normalized}.json")
    
    # キャッシュ確認
    if os.path.exists(cache_path):
        logger.info(f"キャッシュから読み込み: {cache_path}")
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # Google Books API呼び出し
    logger.info(f"Google Books APIから取得: ISBN={isbn_normalized}")
    api_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn_normalized}"
    
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'items' not in data or len(data['items']) == 0:
            logger.error(f"該当するISBNが見つかりませんでした: {isbn_normalized}")
            raise ValueError(f"該当するISBNが見つかりませんでした")
        
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
        
        logger.info(f"書籍情報取得: {book_data['title']}")
        
        # キャッシュ保存
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(book_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"キャッシュ保存: {cache_path}")
        return book_data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"APIエラー: {e}")
        raise Exception(f"Google Books API通信エラー: {e}")


def scrape_amazon_reviews(isbn, logger):
    """AmazonからISBN検索してレビュー取得"""
    logger.info(f"Amazon商品ページからレビュー取得: ISBN={isbn}")
    
    # AmazonのISBN検索URL
    amazon_url = f"https://www.amazon.co.jp/s?k={isbn}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
    }
    
    results = []
    
    try:
        # Amazon検索ページにアクセス
        logger.info(f"Amazon検索: {amazon_url}")
        response = requests.get(amazon_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # 最初の商品リンクを取得
        product_link = soup.find('a', class_='a-link-normal s-no-outline')
        if product_link:
            product_url = 'https://www.amazon.co.jp' + product_link.get('href', '')
            logger.info(f"商品ページ発見: {product_url}")
            
            # 商品ページにアクセス
            time.sleep(1)  # 負荷軽減
            response = requests.get(product_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # レビューセクションを探す
            review_elements = soup.find_all('div', {'data-hook': 'review'}, limit=5)
            
            for i, review in enumerate(review_elements, 1):
                try:
                    # レビュータイトル
                    title_elem = review.find('a', {'data-hook': 'review-title'})
                    title = title_elem.get_text(strip=True) if title_elem else ''
                    
                    # 評価
                    rating_elem = review.find('i', {'data-hook': 'review-star-rating'})
                    rating = rating_elem.get_text(strip=True) if rating_elem else ''
                    
                    # レビュー本文
                    body_elem = review.find('span', {'data-hook': 'review-body'})
                    body = body_elem.get_text(strip=True) if body_elem else ''
                    
                    if title or body:
                        results.append({
                            'number': i,
                            'source': 'Amazon',
                            'title': title,
                            'rating': rating,
                            'content': body,
                            'url': product_url
                        })
                        logger.info(f"  [Amazon-{i}] {title[:30]}...")
                        
                except Exception as e:
                    logger.warning(f"Amazonレビュー解析エラー: {e}")
                    continue
        
    except Exception as e:
        logger.warning(f"Amazon取得エラー: {e}")
    
    return results


def scrape_google_search(search_term, logger):
    """Google検索からレビューサイト情報を取得"""
    logger.info(f"Google検索: {search_term}")
    
    search_query = f"{search_term} 書評 レビュー"
    # Google検索URL（User-Agentを設定しないとブロックされる）
    search_url = f"https://www.google.com/search?q={search_query}&hl=ja"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
    }
    
    results = []
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Google検索結果（通常の検索結果）
        search_results = soup.find_all('div', class_='g', limit=10)
        
        logger.info(f"Google検索結果: {len(search_results)}件")
        
        for i, result in enumerate(search_results, 1):
            try:
                # タイトルとリンク
                title_elem = result.find('h3')
                if not title_elem:
                    continue
                
                link_elem = result.find('a')
                if not link_elem:
                    continue
                
                url = link_elem.get('href', '')
                title = title_elem.get_text(strip=True)
                
                # スニペット
                snippet_elem = result.find('div', class_='VwiC3b')
                if not snippet_elem:
                    snippet_elem = result.find('span', class_='aCOpRe')
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                
                results.append({
                    'number': i,
                    'source': 'Google',
                    'title': title,
                    'url': url,
                    'snippet': snippet
                })
                
                logger.info(f"  [Google-{i}] {title[:50]}...")
                
            except Exception as e:
                logger.warning(f"Google検索結果解析エラー: {e}")
                continue
        
    except Exception as e:
        logger.warning(f"Google検索エラー: {e}")
    
    return results


def scrape_reviews(isbn, search_term, logger):
    """Google検索 + Amazon商品ページからレビュー収集（2段階）"""
    logger.info(f"レビュー収集開始（2段階取得）: {search_term}")
    
    # 保存先ディレクトリ作成
    review_dir = "data/reviews"
    if not os.path.exists(review_dir):
        os.makedirs(review_dir)
        logger.info(f"ディレクトリ作成: {review_dir}")
    
    review_path = os.path.join(review_dir, f"review_{isbn}.txt")
    
    all_results = []
    
    # Phase 1: Google検索
    logger.info("Phase 1: Google検索からレビューサイト情報取得")
    google_results = scrape_google_search(search_term, logger)
    all_results.extend(google_results)
    
    # Phase 2: Amazon直接取得
    time.sleep(2)  # 負荷軽減
    logger.info("Phase 2: Amazon商品ページからレビュー取得")
    amazon_results = scrape_amazon_reviews(isbn, logger)
    all_results.extend(amazon_results)
    
    # レビューテキスト生成
    if len(all_results) == 0:
        logger.info("レビューがありませんでした")
        review_text = "※ レビューが見つかりませんでした\n\n"
        review_text += f"書籍: {search_term}\n"
        review_text += f"ISBN: {isbn}\n"
        review_text += f"収集日時: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        review_text += "【対処方法】\n"
        review_text += "1. Amazon等で手動検索してレビューをコピー\n"
        review_text += "2. このファイルに直接貼り付けて保存\n"
        review_text += "3. ChatGPT/Perplexityで記事生成時に使用\n"
    else:
        review_text = f"書籍レビュー要約\n"
        review_text += "="*70 + "\n"
        review_text += f"書籍: {search_term}\n"
        review_text += f"ISBN: {isbn}\n"
        review_text += f"収集日時: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        review_text += f"収集件数: {len(all_results)}件（Google: {len(google_results)}件, Amazon: {len(amazon_results)}件）\n"
        review_text += "="*70 + "\n\n"
        
        for result in all_results:
            if result['source'] == 'Google':
                review_text += f"【{result['number']}】 {result['title']}\n"
                review_text += f"出典: Google検索結果\n"
                review_text += f"URL: {result['url']}\n"
                review_text += f"要約: {result['snippet']}\n"
            else:  # Amazon
                review_text += f"【{result['number']}】 {result['title']}\n"
                review_text += f"出典: Amazon カスタマーレビュー\n"
                review_text += f"評価: {result['rating']}\n"
                review_text += f"内容: {result['content'][:200]}...\n"
                review_text += f"URL: {result['url']}\n"
            
            review_text += "-"*70 + "\n\n"
        
        review_text += "="*70 + "\n"
        review_text += "※ 上記はGoogle検索結果とAmazonレビューの要約です\n"
        review_text += "※ ChatGPT/Perplexityで記事生成時に参考にしてください\n"
    
    # ファイル保存
    with open(review_path, 'w', encoding='utf-8') as f:
        f.write(review_text)
    
    logger.info(f"レビュー保存: {review_path} ({len(all_results)}件)")
    return review_path


def cmd_fetch(args, logger):
    """fetchコマンド実行"""
    isbn = args.isbn
    logger.info(f"=== fetch開始: ISBN={isbn} ===")
    print(f"\n📚 書籍情報取得開始: ISBN={isbn}")
    
    try:
        # 書籍情報取得
        print("1. Google Books APIから書籍情報を取得中...")
        book_data = fetch_book_data(isbn, logger)
        isbn_normalized = book_data['isbn']
        print(f"   ✅ 取得完了: {book_data['title']}")
        
        # レビュー収集（書籍タイトルで検索）
        print("2. Bing検索からレビューを収集中...")
        search_term = f"{book_data['title']} {' '.join(book_data.get('authors', []))}"
        review_path = scrape_reviews(isbn_normalized, search_term, logger)
        print(f"   ✅ 収集完了: {review_path}")
        
        logger.info("=== fetch完了 ===")
        
        print("\n" + "="*60)
        print("✅ 書籍情報とレビューの取得が完了しました")
        print("="*60)
        print(f"📖 書籍名: {book_data['title']}")
        print(f"✍️  著者: {', '.join(book_data['authors'])}")
        print(f"📅 出版日: {book_data['published_date']}")
        print(f"📄 レビュー: {review_path}")
        print("\n次のステップ:")
        print("1. ChatGPT/Perplexityで記事を生成")
        print(f"   入力: {review_path}")
        print(f"   出力: data/outputs/article_{isbn_normalized}.md")
        print("2. 画像を生成")
        print(f"   出力: data/images/thumbnail_{isbn_normalized}.png")
        
    except Exception as e:
        logger.error(f"fetchエラー: {e}")
        print(f"\n❌ エラー: {e}")
        sys.exit(1)


def cmd_post(args, logger):
    """postコマンド実行（試作版）"""
    isbn = normalize_isbn(args.isbn)
    logger.info(f"=== post開始: ISBN={isbn} ===")
    print(f"\n📝 投稿準備確認: ISBN={isbn}")
    
    try:
        book_path = f"data/books/book_{isbn}.json"
        article_path = f"data/outputs/article_{isbn}.md"
        image_path = f"data/images/thumbnail_{isbn}.png"
        
        # ファイル確認
        print("ファイル確認中...")
        
        if not os.path.exists(book_path):
            raise FileNotFoundError(f"書籍情報が見つかりません: {book_path}")
        
        with open(book_path, 'r', encoding='utf-8') as f:
            book_data = json.load(f)
        print(f"  ✅ 書籍情報: {book_path}")
        
        if not os.path.exists(article_path):
            raise FileNotFoundError(f"記事ファイルが見つかりません: {article_path}")
        
        with open(article_path, 'r', encoding='utf-8') as f:
            article_content = f.read()
        print(f"  ✅ 記事: {article_path} ({len(article_content)}文字)")
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"画像ファイルが見つかりません: {image_path}")
        
        image_size_mb = os.path.getsize(image_path) / (1024 * 1024)
        print(f"  ✅ 画像: {image_path} ({image_size_mb:.2f}MB)")
        
        if image_size_mb > 2:
            print(f"  ⚠️  画像が2MB超過: {image_size_mb:.2f}MB")
        
        print("\n" + "="*60)
        print("✅ 投稿準備ファイルの確認完了")
        print("="*60)
        print(f"📖 書籍名: {book_data['title']}")
        print("【試作版】WordPress投稿機能は次フェーズで実装")
        
        logger.info("=== post確認完了 ===")
        
    except FileNotFoundError as e:
        logger.error(f"ファイルエラー: {e}")
        print(f"\n❌ {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"postエラー: {e}")
        print(f"\n❌ エラー: {e}")
        sys.exit(1)


def main():
    """メイン関数"""
    print("main()関数開始")  # デバッグ
    
    # ロガー初期化
    logger = setup_logger()
    logger.info("プログラム起動")
    
    # 引数パーサー
    parser = argparse.ArgumentParser(description='bookpost - Book Review Auto Poster')
    subparsers = parser.add_subparsers(dest='command', help='コマンド')
    
    # fetchコマンド
    parser_fetch = subparsers.add_parser('fetch', help='書籍情報取得')
    parser_fetch.add_argument('--isbn', required=True, help='ISBN-13')
    
    # postコマンド
    parser_post = subparsers.add_parser('post', help='投稿準備確認')
    parser_post.add_argument('--isbn', required=True, help='ISBN-13')
    
    # 引数解析
    args = parser.parse_args()
    print(f"コマンド: {args.command}")  # デバッグ
    
    # コマンド実行
    if args.command == 'fetch':
        cmd_fetch(args, logger)
    elif args.command == 'post':
        cmd_post(args, logger)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    print("スクリプト実行開始")  # デバッグ
    main()
    print("スクリプト実行終了")  # デバッグ