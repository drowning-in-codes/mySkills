#!/usr/bin/env python3
"""
整理脚本 - 对提取的动漫资讯和新番信息进行清洗、去重、分类和格式化
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from collections import defaultdict


DEFAULT_OUTPUT_DIR = "data/organized"


def clean_title(title: str) -> str:
    """清理标题，移除多余空白和特殊字符"""
    if not title:
        return ""
    
    # 移除多余空白
    title = re.sub(r'\s+', ' ', title).strip()
    
    # 移除常见的垃圾字符
    title = title.replace('\n', ' ').replace('\t', ' ')
    
    # 限制长度
    if len(title) > 200:
        title = title[:197] + "..."
    
    return title


def clean_url(url: str) -> str:
    """清理 URL，移除跟踪参数"""
    if not url:
        return ""
    
    # 移除常见的跟踪参数
    tracking_params = [
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
        'fbclid', 'gclid', 'ref', 'source', 'campaign'
    ]
    
    # 简单处理，实际应用中可能需要 urllib.parse
    for param in tracking_params:
        url = re.sub(rf'[?&]{param}=[^&]*', '', url)
    
    # 清理末尾的 ? 和 &
    url = url.rstrip('?&')
    
    return url


def normalize_category(category: str) -> str:
    """标准化分类名称"""
    category_map = {
        '资讯': '资讯',
        '新闻': '资讯',
        '漫展': '漫展',
        '漫画': '漫画',
        '动画': '动画',
        '番剧': '动画',
        '新番': '动画',
        '游戏': '游戏',
        '周边': '周边',
        'cosplay': 'Cosplay',
        'cos': 'Cosplay',
        '其他': '其他',
    }
    
    normalized = category_map.get(category, category)
    return normalized if normalized else "其他"


def deduplicate_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    对项目进行去重
    
    策略：
    1. 基于 URL 精确去重
    2. 基于标题相似度去重（可选）
    """
    seen_urls: Set[str] = set()
    seen_titles: Set[str] = set()
    unique_items = []
    
    for item in items:
        url = item.get('url', '').strip().lower()
        title = item.get('title', '').strip().lower()
        
        # URL 去重
        if url in seen_urls:
            continue
        
        # 标题去重（完全匹配）
        if title in seen_titles:
            continue
        
        seen_urls.add(url)
        seen_titles.add(title)
        unique_items.append(item)
    
    return unique_items


def filter_items(items: List[Dict[str, Any]], min_read_count: int = 0) -> List[Dict[str, Any]]:
    """
    过滤项目
    
    Args:
        items: 项目列表
        min_read_count: 最小阅读数阈值
    """
    filtered = []
    
    for item in items:
        # 必须有标题和 URL
        if not item.get('title') or not item.get('url'):
            continue
        
        # 标题不能太短
        if len(item['title']) < 5:
            continue
        
        # 阅读数过滤
        if item.get('read_count', 0) < min_read_count:
            continue
        
        filtered.append(item)
    
    return filtered


def sort_news_items(items: List[Dict[str, Any]], sort_by: str = "read_count") -> List[Dict[str, Any]]:
    """
    对新闻项目进行排序
    
    Args:
        items: 项目列表
        sort_by: 排序字段 (read_count, date, title)
    """
    if sort_by == "read_count":
        return sorted(items, key=lambda x: x.get('read_count', 0), reverse=True)
    elif sort_by == "date":
        # 按日期排序
        def get_date_key(item):
            date = item.get('published_at')
            if date:
                return date
            return "1970-01-01T00:00:00"  # 默认为最早日期
        return sorted(items, key=get_date_key, reverse=True)
    elif sort_by == "title":
        return sorted(items, key=lambda x: x.get('title', ''))
    else:
        return items


def sort_anime_items(items: List[Dict[str, Any]], sort_by: str = "air_time") -> List[Dict[str, Any]]:
    """
    对新番项目进行排序
    
    Args:
        items: 项目列表
        sort_by: 排序字段 (air_time, title, status)
    """
    if sort_by == "air_time":
        # 按播出时间排序
        def get_air_time_key(item):
            air_time = item.get('air_time')
            if air_time:
                return air_time
            return "1970-01-01"  # 默认为最早日期
        return sorted(items, key=get_air_time_key)
    elif sort_by == "title":
        return sorted(items, key=lambda x: x.get('title', ''))
    elif sort_by == "status":
        # 按状态排序
        status_order = {"已开播": 0, "即将开播": 1, "未开播": 2, "未知": 3}
        def get_status_key(item):
            status = item.get('status', '未知')
            return status_order.get(status, 3)
        return sorted(items, key=get_status_key)
    else:
        return items


def categorize_news_items(items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """按分类对新闻项目进行分组"""
    categories = defaultdict(list)
    
    for item in items:
        category = item.get('category', '其他')
        category = normalize_category(category)
        categories[category].append(item)
    
    return dict(categories)


def categorize_anime_items(items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """按季度对新番项目进行分组"""
    seasons = defaultdict(list)
    
    for item in items:
        season = item.get('season', '未知')
        seasons[season].append(item)
    
    return dict(seasons)


def enrich_news_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """丰富新闻项目信息"""
    enriched = item.copy()
    
    # 清理标题
    enriched['title'] = clean_title(item.get('title', ''))
    
    # 清理 URL
    enriched['url'] = clean_url(item.get('url', ''))
    
    # 标准化分类
    enriched['category'] = normalize_category(item.get('category', '其他'))
    
    # 确保数值字段
    enriched['read_count'] = int(item.get('read_count', 0) or 0)
    
    # 添加整理时间戳
    enriched['organized_at'] = datetime.now().isoformat()
    
    return enriched


def enrich_anime_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """丰富新番项目信息"""
    enriched = item.copy()
    
    # 清理标题
    enriched['title'] = clean_title(item.get('title', ''))
    
    # 清理 URL
    enriched['url'] = clean_url(item.get('url', ''))
    
    # 确保状态
    enriched['status'] = item.get('status', '未知')
    
    # 确保季度信息
    enriched['season'] = item.get('season', '未知')
    
    # 添加整理时间戳
    enriched['organized_at'] = datetime.now().isoformat()
    
    return enriched


def organize_news_items(items: List[Dict[str, Any]], min_read_count: int = 0) -> Dict[str, Any]:
    """
    整理新闻数据
    
    Args:
        items: 原始新闻列表
        min_read_count: 最小阅读数阈值
        
    Returns:
        整理后的数据结构
    """
    print(f"[Organize] 开始整理 {len(items)} 条新闻...")
    
    # 1. 丰富和清理每条新闻
    enriched = [enrich_news_item(item) for item in items]
    print(f"[Organize] 数据清理完成")
    
    # 2. 过滤
    filtered = filter_items(enriched, min_read_count)
    print(f"[Organize] 过滤后剩余 {len(filtered)} 条新闻")
    
    # 3. 去重
    unique = deduplicate_items(filtered)
    print(f"[Organize] 去重后剩余 {len(unique)} 条新闻")
    
    # 4. 排序
    sorted_items = sort_news_items(unique, "read_count")
    
    # 5. 分类
    categorized = categorize_news_items(sorted_items)
    print(f"[Organize] 分类统计: {dict((k, len(v)) for k, v in categorized.items())}")
    
    # 6. 生成统计信息
    stats = {
        "total_items": len(sorted_items),
        "categories": {cat: len(items) for cat, items in categorized.items()},
        "top_sources": get_top_sources(sorted_items, 10),
        "read_count_distribution": get_read_count_distribution(sorted_items),
        "organized_at": datetime.now().isoformat(),
    }
    
    result = {
        "items": sorted_items,
        "by_category": categorized,
        "statistics": stats,
        "metadata": {
            "original_count": len(items),
            "filtered_count": len(filtered),
            "final_count": len(sorted_items),
            "min_read_count": min_read_count,
            "type": "news"
        }
    }
    
    return result


def organize_anime_items(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    整理新番数据
    
    Args:
        items: 原始新番列表
        
    Returns:
        整理后的数据结构
    """
    print(f"[Organize] 开始整理 {len(items)} 条新番信息...")
    
    # 1. 丰富和清理每条新番
    enriched = [enrich_anime_item(item) for item in items]
    print(f"[Organize] 数据清理完成")
    
    # 2. 去重
    unique = deduplicate_items(enriched)
    print(f"[Organize] 去重后剩余 {len(unique)} 条新番信息")
    
    # 3. 排序
    sorted_items = sort_anime_items(unique, "air_time")
    
    # 4. 分类
    categorized = categorize_anime_items(sorted_items)
    print(f"[Organize] 季度统计: {dict((k, len(v)) for k, v in categorized.items())}")
    
    # 5. 生成统计信息
    stats = {
        "total_items": len(sorted_items),
        "seasons": {season: len(items) for season, items in categorized.items()},
        "status_distribution": get_status_distribution(sorted_items),
        "organized_at": datetime.now().isoformat(),
    }
    
    result = {
        "items": sorted_items,
        "by_season": categorized,
        "statistics": stats,
        "metadata": {
            "original_count": len(items),
            "final_count": len(sorted_items),
            "type": "anime"
        }
    }
    
    return result


def get_top_sources(items: List[Dict[str, Any]], n: int = 10) -> List[Dict[str, Any]]:
    """获取主要来源网站统计"""
    source_counts = defaultdict(lambda: {"count": 0, "total_read_count": 0})
    
    for item in items:
        source = item.get('source', 'Unknown')
        source_counts[source]["count"] += 1
        source_counts[source]["total_read_count"] += item.get('read_count', 0)
    
    # 转换为列表并排序
    sources = [
        {"name": name, **data}
        for name, data in source_counts.items()
    ]
    sources.sort(key=lambda x: x["count"], reverse=True)
    
    return sources[:n]


def get_read_count_distribution(items: List[Dict[str, Any]]) -> Dict[str, int]:
    """获取阅读数分布"""
    distribution = {
        "high (1000+)": 0,
        "medium (100-999)": 0,
        "low (0-99)": 0,
    }
    
    for item in items:
        read_count = item.get('read_count', 0)
        if read_count >= 1000:
            distribution["high (1000+)"] += 1
        elif read_count >= 100:
            distribution["medium (100-999)"] += 1
        else:
            distribution["low (0-99)"] += 1
    
    return distribution


def get_status_distribution(items: List[Dict[str, Any]]) -> Dict[str, int]:
    """获取新番状态分布"""
    distribution = defaultdict(int)
    
    for item in items:
        status = item.get('status', '未知')
        distribution[status] += 1
    
    return dict(distribution)


def save_organized_data(data: Dict[str, Any], output_dir: str, data_type: str) -> Path:
    """保存整理后的数据"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{data_type}_organized_{timestamp}.json"
    file_path = output_path / filename
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"[Organize] 数据已保存到: {file_path}")
    
    return file_path


def main():
    parser = argparse.ArgumentParser(
        description="整理和清洗动漫资讯和新番信息"
    )
    parser.add_argument(
        "input_files",
        nargs="*",
        help="输入 JSON 文件路径（默认从 data/extracted/ 目录查找最新文件）"
    )
    parser.add_argument(
        "--output-dir",
        default=os.getenv("OUTPUT_DIR", DEFAULT_OUTPUT_DIR),
        help=f"输出目录 (默认: {DEFAULT_OUTPUT_DIR})"
    )
    parser.add_argument(
        "--min-read-count",
        type=int,
        default=0,
        help="最小阅读数阈值 (默认: 0)"
    )
    
    args = parser.parse_args()
    
    try:
        # 确定输入文件
        if args.input_files:
            input_paths = [Path(p) for p in args.input_files]
        else:
            # 查找最新的 JSON 文件
            extracted_dir = Path("data/extracted")
            if extracted_dir.exists():
                json_files = sorted(extracted_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
                if json_files:
                    input_paths = json_files
                    print(f"[Organize] 找到 {len(input_paths)} 个 JSON 文件")
                else:
                    print("[Organize] 错误: 未找到 JSON 文件", file=sys.stderr)
                    return 1
            else:
                print("[Organize] 错误: data/extracted/ 目录不存在", file=sys.stderr)
                return 1
        
        # 按类型分组
        news_items = []
        anime_items = []
        
        for input_path in input_paths:
            print(f"[Organize] 正在读取: {input_path}")
            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            items = data.get("items", [])
            source = data.get("metadata", {}).get("source", "")
            
            # 区分新闻和新番
            if "yuc" in str(input_path) or "番" in source:
                anime_items.extend(items)
            else:
                news_items.extend(items)
        
        saved_files = []
        
        # 处理新闻
        if news_items:
            print("\n[Organize] 处理新闻数据...")
            news_data = organize_news_items(news_items, args.min_read_count)
            news_path = save_organized_data(news_data, args.output_dir, "news")
            saved_files.append(news_path)
        
        # 处理新番
        if anime_items:
            print("\n[Organize] 处理新番数据...")
            anime_data = organize_anime_items(anime_items)
            anime_path = save_organized_data(anime_data, args.output_dir, "anime")
            saved_files.append(anime_path)
        
        if not saved_files:
            print("[Organize] 错误: 没有找到可处理的数据", file=sys.stderr)
            return 1
        
        print(f"\n[Organize] 完成！成功处理 {len(saved_files)} 个数据文件")
        
        # 输出文件路径供其他脚本使用
        for file_path in saved_files:
            print(f"OUTPUT_FILE:{file_path}")
        
        return 0
        
    except Exception as e:
        print(f"[Organize] 错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
