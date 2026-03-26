#!/usr/bin/env python3
"""
提取脚本 - 从 HTML 中解析动漫资讯和新番信息
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup


DEFAULT_OUTPUT_DIR = "data/extracted"


# 网站提取器配置
EXTRACTORS = {
    "moelove": {
        "name": "梦域动漫",
        "type": "news",
        "extract_func": "extract_moelove_news"
    },
    "anifun": {
        "name": "AniFun",
        "type": "news",
        "extract_func": "extract_generic_news"
    },
    "hotacg": {
        "name": "HotACG",
        "type": "news",
        "extract_func": "extract_generic_news"
    },
    "yuc": {
        "name": "長門番堂",
        "type": "anime",
        "extract_func": "extract_yuc_anime"
    }
}


def parse_date(date_str: str) -> Optional[str]:
    """解析日期字符串"""
    if not date_str:
        return None
    
    # 梦域动漫的日期格式: 2025-06-10
    date_patterns = [
        (r'\d{4}-\d{2}-\d{2}', "%Y-%m-%d"),
        (r'\d{4}/\d{2}/\d{2}', "%Y/%m/%d"),
        (r'\d{2}/\d{2}/\d{4}', "%m/%d/%Y"),
    ]
    
    for pattern, format_str in date_patterns:
        match = re.search(pattern, date_str)
        if match:
            try:
                date = datetime.strptime(match.group(0), format_str)
                return date.isoformat()
            except ValueError:
                continue
    
    return date_str.strip()


def parse_read_count(read_str: str) -> int:
    """解析阅读数"""
    if not read_str:
        return 0
    
    # 提取数字
    numbers = re.findall(r'\d+', read_str.replace(',', ''))
    return int(numbers[0]) if numbers else 0


def extract_moelove_news(html_content: str, base_url: str = "https://www.moelove.cn/") -> List[Dict[str, Any]]:
    """
    提取梦域动漫的新闻
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    articles = []
    
    # 梦域动漫的文章结构
    article_elements = soup.select('.post')
    
    for element in article_elements:
        article = {}
        
        try:
            # 标题和链接
            title_elem = element.select_one('h2 a') or element.select_one('a[href]')
            if title_elem:
                article['title'] = title_elem.get_text(strip=True)
                href = title_elem.get('href', '')
                article['url'] = urljoin(base_url, href)
            else:
                continue
            
            # 摘要
            summary_elem = element.select_one('.entry-summary')
            if summary_elem:
                article['summary'] = summary_elem.get_text(strip=True)
            
            # 日期
            date_elem = element.select_one('.entry-date')
            if date_elem:
                article['published_at'] = parse_date(date_elem.get_text())
            
            # 分类
            category_elem = element.select_one('.entry-category a')
            if category_elem:
                article['category'] = category_elem.get_text(strip=True)
            else:
                article['category'] = "资讯"
            
            # 阅读数
            read_elem = element.select_one('.read-count')
            if read_elem:
                article['read_count'] = parse_read_count(read_elem.get_text())
            else:
                # 从文本中提取阅读数
                text = element.get_text()
                read_match = re.search(r'阅读\((\d+\.?\d*)\s*[Kk]?\)', text)
                if read_match:
                    read_str = read_match.group(1)
                    if 'k' in text.lower() or 'K' in text:
                        article['read_count'] = int(float(read_str) * 1000)
                    else:
                        article['read_count'] = int(read_str)
                else:
                    article['read_count'] = 0
            
            # 来源
            article['source'] = "moelove.cn"
            article['extracted_at'] = datetime.now().isoformat()
            
            if article.get('title') and article.get('url'):
                articles.append(article)
                
        except Exception as e:
            print(f"[Extract] 解析梦域动漫文章时出错: {e}", file=sys.stderr)
            continue
    
    return articles


def extract_generic_news(html_content: str, base_url: str) -> List[Dict[str, Any]]:
    """
    通用新闻提取器
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    articles = []
    
    # 尝试多种常见的文章选择器
    selectors = [
        '.article', '.post', '.news-item', 'article', 
        '.entry', '.item', '.blog-post'
    ]
    
    article_elements = []
    for selector in selectors:
        elements = soup.select(selector)
        if elements:
            article_elements = elements
            break
    
    # 如果没有找到，尝试从链接中提取
    if not article_elements:
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            text = link.get_text(strip=True)
            href = link.get('href', '')
            if len(text) > 10 and href.startswith('http'):
                parent = link.find_parent(['div', 'article', 'li'])
                if parent and parent not in article_elements:
                    article_elements.append(parent)
    
    for element in article_elements:
        article = {}
        
        try:
            # 标题和链接
            title_elem = element.find('a', href=True)
            if title_elem:
                article['title'] = title_elem.get_text(strip=True)
                article['url'] = title_elem.get('href', '')
            else:
                continue
            
            # 日期
            date_elem = element.find(['time', 'span'], class_=re.compile(r'date|time'))
            if date_elem:
                article['published_at'] = parse_date(date_elem.get_text())
            
            # 分类
            category_elem = element.find(['span', 'a'], class_=re.compile(r'category|tag'))
            if category_elem:
                article['category'] = category_elem.get_text(strip=True)
            else:
                article['category'] = "资讯"
            
            # 摘要
            summary_elem = element.find(['p', 'div'], class_=re.compile(r'summary|excerpt'))
            if summary_elem:
                article['summary'] = summary_elem.get_text(strip=True)
            
            # 阅读数
            read_elem = element.find(['span', 'div'], class_=re.compile(r'read|view'))
            if read_elem:
                article['read_count'] = parse_read_count(read_elem.get_text())
            else:
                article['read_count'] = 0
            
            # 来源
            article['source'] = base_url.split('/')[2]
            article['extracted_at'] = datetime.now().isoformat()
            
            if article.get('title') and article.get('url'):
                articles.append(article)
                
        except Exception as e:
            print(f"[Extract] 解析通用新闻时出错: {e}", file=sys.stderr)
            continue
    
    return articles


def extract_yuc_anime(html_content: str, base_url: str = "https://yuc.wiki/") -> List[Dict[str, Any]]:
    """
    提取長門番堂的新番信息
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    anime_list = []
    
    # 尝试提取新番信息
    # 由于网站可能使用动态加载，这里提供通用提取逻辑
    
    # 查找可能的动画信息元素
    potential_elements = soup.find_all(['div', 'li', 'article'])
    
    for element in potential_elements:
        anime = {}
        
        try:
            # 标题和链接
            title_elem = element.find('a', href=True)
            if title_elem:
                anime['title'] = title_elem.get_text(strip=True)
                anime['url'] = urljoin(base_url, title_elem.get('href', ''))
            else:
                continue
            
            # 时间信息
            time_elem = element.find(['time', 'span'], text=re.compile(r'\d{4}|\d{2}:\d{2}|每周|放送'))
            if time_elem:
                time_text = time_elem.get_text(strip())
                if '放送' in time_text or '每周' in time_text:
                    anime['broadcast_time'] = time_text
                else:
                    anime['air_time'] = parse_date(time_text)
            
            # 状态
            status_elem = element.find(['span', 'div'], text=re.compile(r'开播|放送|更新'))
            if status_elem:
                anime['status'] = status_elem.get_text(strip())
            else:
                anime['status'] = "未知"
            
            # 季度信息
            season_elem = element.find(['span', 'div'], text=re.compile(r'\d{4}年\d{1,2}月'))
            if season_elem:
                anime['season'] = season_elem.get_text(strip())
            else:
                # 尝试从标题或URL中提取
                text = element.get_text()
                season_match = re.search(r'\d{4}年\d{1,2}月', text)
                if season_match:
                    anime['season'] = season_match.group(0)
                else:
                    anime['season'] = "未知"
            
            # 来源
            anime['source'] = "yuc.wiki"
            anime['extracted_at'] = datetime.now().isoformat()
            
            if anime.get('title') and anime.get('url'):
                anime_list.append(anime)
                
        except Exception as e:
            print(f"[Extract] 解析新番信息时出错: {e}", file=sys.stderr)
            continue
    
    return anime_list


def extract_from_file(file_path: Path) -> Dict[str, Any]:
    """
    从文件中提取信息
    
    Args:
        file_path: 文件路径
        
    Returns:
        提取的数据
    """
    filename = file_path.name
    
    # 从文件名中识别网站
    website_key = None
    for key in EXTRACTORS.keys():
        if key in filename:
            website_key = key
            break
    
    if not website_key:
        print(f"[Extract] 无法识别文件 {filename} 对应的网站", file=sys.stderr)
        return {}
    
    extractor_info = EXTRACTORS[website_key]
    
    print(f"[Extract] 处理 {extractor_info['name']} 文件: {filename}")
    
    # 读取文件
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # 根据网站类型选择提取函数
    if extractor_info['type'] == "news":
        if website_key == "moelove":
            items = extract_moelove_news(html_content)
        else:
            base_url = next((w['url'] for w in EXTRACTORS.values() if w['name'] == extractor_info['name']), "")
            items = extract_generic_news(html_content, base_url)
    elif extractor_info['type'] == "anime":
        items = extract_yuc_anime(html_content)
    else:
        items = []
    
    print(f"[Extract] 成功提取 {len(items)} 条信息")
    
    # 构建返回数据
    data = {
        "items": items,
        "metadata": {
            "extracted_at": datetime.now().isoformat(),
            "total_count": len(items),
            "source": extractor_info['name'],
            "source_url": next((w['url'] for w in EXTRACTORS.values() if w['name'] == extractor_info['name']), ""),
            "file_path": str(file_path)
        }
    }
    
    return data


def save_extracted_data(data: Dict[str, Any], output_dir: str, website_key: str) -> Path:
    """
    保存提取的数据
    
    Args:
        data: 提取的数据
        output_dir: 输出目录
        website_key: 网站标识符
        
    Returns:
        保存的文件路径
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{website_key}_{data['metadata'].get('source', 'unknown')}_{timestamp}.json"
    file_path = output_path / filename
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"[Extract] 数据已保存到: {file_path}")
    
    return file_path


def main():
    parser = argparse.ArgumentParser(
        description="从 HTML 文件中提取动漫资讯和新番信息"
    )
    parser.add_argument(
        "input_files",
        nargs="*",
        help="输入 HTML 文件路径（默认从 data/raw/ 目录查找最新文件）"
    )
    parser.add_argument(
        "--output-dir",
        default=os.getenv("OUTPUT_DIR", DEFAULT_OUTPUT_DIR),
        help=f"输出目录 (默认: {DEFAULT_OUTPUT_DIR})"
    )
    
    args = parser.parse_args()
    
    try:
        # 确定输入文件
        if args.input_files:
            input_paths = [Path(p) for p in args.input_files]
        else:
            # 查找最新的 HTML 文件
            raw_dir = Path("data/raw")
            if raw_dir.exists():
                html_files = sorted(raw_dir.glob("*.html"), key=lambda p: p.stat().st_mtime, reverse=True)
                if html_files:
                    input_paths = html_files
                    print(f"[Extract] 找到 {len(input_paths)} 个 HTML 文件")
                else:
                    print("[Extract] 错误: 未找到 HTML 文件", file=sys.stderr)
                    return 1
            else:
                print("[Extract] 错误: data/raw/ 目录不存在", file=sys.stderr)
                return 1
        
        saved_files = []
        
        # 处理每个文件
        for input_path in input_paths:
            print(f"\n[Extract] 处理文件: {input_path}")
            
            # 提取数据
            data = extract_from_file(input_path)
            
            if not data or not data.get('items'):
                print(f"[Extract] 警告: 未从 {input_path} 提取到数据", file=sys.stderr)
                continue
            
            # 识别网站
            website_key = None
            filename = input_path.name
            for key in EXTRACTORS.keys():
                if key in filename:
                    website_key = key
                    break
            
            if not website_key:
                website_key = "unknown"
            
            # 保存数据
            output_path = save_extracted_data(data, args.output_dir, website_key)
            saved_files.append(output_path)
        
        print(f"\n[Extract] 完成！成功处理 {len(saved_files)} 个文件")
        
        # 输出文件路径供其他脚本使用
        for file_path in saved_files:
            print(f"OUTPUT_FILE:{file_path}")
        
        return 0
        
    except Exception as e:
        print(f"[Extract] 错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
