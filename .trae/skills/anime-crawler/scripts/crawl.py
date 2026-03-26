#!/usr/bin/env python3
"""
爬取脚本 - 获取多个动漫网站的原始 HTML 内容
"""

import os
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# 支持的网站配置
WEBSITES = {
    "moelove": {
        "name": "梦域动漫",
        "url": "https://www.moelove.cn/",
        "type": "news"
    },
    "anifun": {
        "name": "AniFun",
        "url": "https://anifun.cn/",
        "type": "news"
    },
    "hotacg": {
        "name": "HotACG",
        "url": "https://www.hotacg.com/",
        "type": "news"
    },
    "yuc": {
        "name": "長門番堂",
        "url": "https://yuc.wiki/",
        "type": "anime"
    }
}

DEFAULT_TIMEOUT = 30
DEFAULT_MAX_RETRIES = 3
DEFAULT_OUTPUT_DIR = "data/raw"


def create_session(max_retries: int = DEFAULT_MAX_RETRIES) -> requests.Session:
    """创建带有重试机制的 HTTP Session"""
    session = requests.Session()
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def crawl_website(
    url: str, 
    timeout: int = DEFAULT_TIMEOUT
) -> str:
    """
    爬取指定 URL 的网页内容
    
    Args:
        url: 目标 URL
        timeout: 请求超时时间
        
    Returns:
        网页 HTML 内容
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    session = create_session()
    
    print(f"[Crawl] 正在爬取: {url}")
    
    try:
        response = session.get(
            url,
            headers=headers,
            timeout=timeout,
            allow_redirects=True
        )
        response.raise_for_status()
        
        print(f"[Crawl] 成功获取页面，状态码: {response.status_code}")
        print(f"[Crawl] 内容长度: {len(response.text)} 字符")
        
        return response.text
        
    except requests.exceptions.RequestException as e:
        print(f"[Crawl] 爬取失败: {e}", file=sys.stderr)
        raise


def save_html(
    html_content: str, 
    output_dir: str, 
    website_key: str, 
    website_info: Dict[str, str]
) -> Path:
    """
    保存 HTML 内容到文件
    
    Args:
        html_content: HTML 内容
        output_dir: 输出目录
        website_key: 网站标识符
        website_info: 网站信息
        
    Returns:
        保存的文件路径
    """
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{website_key}_{website_info['type']}_{timestamp}.html"
    
    file_path = output_path / filename
    
    # 保存文件
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"[Crawl] HTML 已保存到: {file_path}")
    
    return file_path


def crawl_all_websites(
    websites: List[str],
    output_dir: str,
    timeout: int = DEFAULT_TIMEOUT
) -> List[Path]:
    """
    爬取所有指定的网站
    
    Args:
        websites: 要爬取的网站列表
        output_dir: 输出目录
        timeout: 请求超时时间
        
    Returns:
        保存的文件路径列表
    """
    saved_files = []
    
    for website_key in websites:
        if website_key not in WEBSITES:
            print(f"[Crawl] 警告: 未知网站: {website_key}", file=sys.stderr)
            continue
        
        website_info = WEBSITES[website_key]
        print(f"\n[Crawl] 开始爬取: {website_info['name']} ({website_info['url']})")
        
        try:
            html_content = crawl_website(website_info['url'], timeout)
            file_path = save_html(html_content, output_dir, website_key, website_info)
            saved_files.append(file_path)
            
            # 避免请求过快
            time.sleep(2)
            
        except Exception as e:
            print(f"[Crawl] 爬取 {website_info['name']} 失败: {e}", file=sys.stderr)
            continue
    
    return saved_files


def main():
    parser = argparse.ArgumentParser(
        description="爬取多个动漫网站内容"
    )
    parser.add_argument(
        "--websites",
        default=os.getenv("WEBSITES", ",".join(WEBSITES.keys())),
        help=f"要爬取的网站列表（逗号分隔，默认: {','.join(WEBSITES.keys())}")
    )
    parser.add_argument(
        "--output-dir",
        default=os.getenv("OUTPUT_DIR", DEFAULT_OUTPUT_DIR),
        help=f"输出目录 (默认: {DEFAULT_OUTPUT_DIR})"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=int(os.getenv("TIMEOUT", DEFAULT_TIMEOUT)),
        help=f"请求超时时间 (默认: {DEFAULT_TIMEOUT}秒)"
    )
    
    args = parser.parse_args()
    
    # 解析网站列表
    websites = [w.strip() for w in args.websites.split(",") if w.strip()]
    if not websites:
        websites = list(WEBSITES.keys())
    
    print(f"[Crawl] 准备爬取 {len(websites)} 个网站: {', '.join(websites)}")
    
    try:
        # 爬取所有网站
        saved_files = crawl_all_websites(websites, args.output_dir, args.timeout)
        
        print(f"\n[Crawl] 完成！成功爬取 {len(saved_files)} 个网站")
        
        # 输出文件路径供其他脚本使用
        for file_path in saved_files:
            print(f"OUTPUT_FILE:{file_path}")
        
        return 0
        
    except Exception as e:
        print(f"[Crawl] 错误: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
