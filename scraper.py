#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
scraper.py - レビュー収集モジュール（試作版）
Bing検索からレビュー要約を収集
"""

import os
import time
import requests
from bs4 import BeautifulSoup


def scrape_reviews(isbn_or_title, logger):
    """
    Bing検索から書評・レビューを収集し、要約テキストを生成
    
    Args:
        isbn_or_title: ISBNまたは書籍タイトル
        logger: ロガー
    
    Returns:
        str: 保存先ファイルパス
    
    Raises:
        Exception: Bing検索失敗時
    """
    logger.info(f"レビュー収集開始: {isbn_or_title}")
    
    # 保存先ディレクトリ作成
    review_dir = "data/reviews"
    if not os.path.exists(review_dir):
        os.makedirs(review_dir)
    
    # 保存先ファイルパス
    review_path = os.path.join(review_dir, f"review_{isbn_or_title}.txt")
    
    # Bing検索URL生成
    search_query = f"{isbn_or_title} 書評 レビュー"
    search_url = f"https://www.bing.com/search?q={search_query}"
    
    logger.info(f"Bing検索: {search_url}")
    
    # User-Agent設定（ブラウザ偽装）
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    
    try:
        # Bing検索実行
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # HTML解析
        soup = BeautifulSoup(response.text, 'lxml')
        
        # 検索結果のリンクを抽出（試作版：簡易実装）
        results = []
        
        # Bing検索結果のセレクタ（class="b_algo"）
        search_results = soup.find_all('li', class_='b_algo', limit=10)
        
        logger.info(f"検索結果: {len(search_results)}件")
        
        for i, result in enumerate(search_results, 1):
            try:
                # タイトルとURL抽出
                title_tag = result.find('h2')
                if not title_tag:
                    continue
                
                link_tag = title_tag.find('a')
                if not link_tag:
                    continue
                
                url = link_tag.get('href', '')
                title = title_tag.get_text(strip=True)
                
                # スニペット（説明文）抽出
                snippet_tag = result.find('p')
                snippet = snippet_tag.get_text(strip=True) if snippet_tag else ''
                
                results.append({
                    'number': i,
                    'title': title,
                    'url': url,
                    'snippet': snippet
                })
                
                logger.info(f"  [{i}] {title}")
                
            except Exception as e:
                logger.warning(f"検索結果の解析エラー: {e}")
                continue
        
        # レビュー要約テキスト生成
        if len(results) == 0:
            logger.info("レビューがありませんでした")
            review_text = "※ レビューが見つかりませんでした\n\n"
            review_text += f"検索クエリ: {search_query}\n"
            review_text += "手動でレビューを追加してください。"
        else:
            review_text = f"書籍レビュー要約 - {isbn_or_title}\n"
            review_text += "="*50 + "\n\n"
            review_text += f"検索クエリ: {search_query}\n"
            review_text += f"収集日時: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            review_text += f"検索結果件数: {len(results)}件\n\n"
            review_text += "="*50 + "\n\n"
            
            for result in results:
                review_text += f"【{result['number']}】 {result['title']}\n"
                review_text += f"URL: {result['url']}\n"
                review_text += f"要約: {result['snippet']}\n"
                review_text += "-"*50 + "\n\n"
            
            review_text += "="*50 + "\n"
            review_text += "※ 上記はBing検索結果のスニペットです\n"
            review_text += "※ ChatGPT/Perplexityで記事生成時に参考にしてください\n"
        
        # ファイル保存
        with open(review_path, 'w', encoding='utf-8') as f:
            f.write(review_text)
        
        logger.info(f"レビューを保存しました: {review_path}")
        
        return review_path
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Bing検索失敗: {e}")
        raise Exception(f"Bing検索エラー: {e}")


def scrape_review_detail(url, logger):
    """
    個別のレビューサイトから詳細を取得（将来拡張用）
    
    Args:
        url: レビューサイトのURL
        logger: ロガー
    
    Returns:
        str: レビュー本文
    """
    # 将来的にAmazon、読書メーター等から詳細レビューを取得
    # 現在は未実装（試作版ではスニペットのみ）
    logger.info(f"詳細取得（未実装）: {url}")
    return ""


if __name__ == '__main__':
    # テスト実行用
    import logging
    
    logger = logging.getLogger('test')
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))
    logger.addHandler(handler)
    
    # テスト
    test_isbn = "9784295404811"  # 例：『伝わる文章の書き方教室』
    result_path = scrape_reviews(test_isbn, logger)
    print(f"\n保存先: {result_path}")
