#!/usr/bin/env python3
"""
整合脚本 - 整合所有来源的动漫资讯和新番信息，生成综合报告
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict


DEFAULT_OUTPUT_DIR = "data/integrated"


def load_organized_data(input_files: List[Path]) -> Dict[str, Any]:
    """
    加载整理后的数据
    
    Args:
        input_files: 输入文件路径列表
        
    Returns:
        整合后的数据
    """
    news_data = None
    anime_data = None
    
    for file_path in input_files:
        print(f"[Integrate] 正在读取: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        data_type = data.get("metadata", {}).get("type")
        if data_type == "news":
            news_data = data
        elif data_type == "anime":
            anime_data = data
    
    return {
        "news": news_data,
        "anime": anime_data
    }


def generate_news_summary(news_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成新闻摘要
    
    Args:
        news_data: 新闻数据
        
    Returns:
        新闻摘要
    """
    if not news_data:
        return {}
    
    items = news_data.get("items", [])
    stats = news_data.get("statistics", {})
    
    # 热门新闻（按阅读数排序）
    top_news = items[:10]
    
    # 按分类统计
    categories = news_data.get("by_category", {})
    
    # 来源统计
    top_sources = stats.get("top_sources", [])
    
    return {
        "total_news": len(items),
        "top_news": top_news,
        "categories": categories,
        "top_sources": top_sources,
        "read_count_distribution": stats.get("read_count_distribution", {}),
        "latest_news": sorted(items, key=lambda x: x.get("published_at", "1970-01-01"), reverse=True)[:5]
    }


def generate_anime_summary(anime_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成新番摘要
    
    Args:
        anime_data: 新番数据
        
    Returns:
        新番摘要
    """
    if not anime_data:
        return {}
    
    items = anime_data.get("items", [])
    stats = anime_data.get("statistics", {})
    
    # 按季度分类
    by_season = anime_data.get("by_season", {})
    
    # 即将开播的新番
    upcoming_anime = [item for item in items if "即将" in item.get("status", "") or "未开播" in item.get("status", "")]
    upcoming_anime.sort(key=lambda x: x.get("air_time", "9999-12-31"))
    
    # 已开播的新番
    ongoing_anime = [item for item in items if "已开播" in item.get("status", "") or "放送中" in item.get("status", "")]
    
    return {
        "total_anime": len(items),
        "by_season": by_season,
        "upcoming_anime": upcoming_anime[:10],
        "ongoing_anime": ongoing_anime[:10],
        "status_distribution": stats.get("status_distribution", {})
    }


def generate_integrated_report(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成综合报告
    
    Args:
        data: 整合后的数据
        
    Returns:
        综合报告
    """
    news_data = data.get("news")
    anime_data = data.get("anime")
    
    news_summary = generate_news_summary(news_data)
    anime_summary = generate_anime_summary(anime_data)
    
    report = {
        "report_title": "动漫资讯综合报告",
        "generated_at": datetime.now().isoformat(),
        "news_summary": news_summary,
        "anime_summary": anime_summary,
        "overview": {
            "total_news": news_summary.get("total_news", 0),
            "total_anime": anime_summary.get("total_anime", 0),
            "last_updated": datetime.now().isoformat()
        }
    }
    
    return report


def generate_markdown_report(report: Dict[str, Any]) -> str:
    """
    生成 Markdown 格式的报告
    
    Args:
        report: 综合报告
        
    Returns:
        Markdown 内容
    """
    lines = []
    
    # 标题
    lines.append(f"# {report['report_title']}")
    lines.append("")
    lines.append(f"**生成时间**: {report['generated_at'][:19]}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # 概览
    overview = report.get("overview", {})
    lines.append("## 📊 数据概览")
    lines.append("")
    lines.append(f"- **新闻总数**: {overview.get('total_news', 0)}")
    lines.append(f"- **新番总数**: {overview.get('total_anime', 0)}")
    lines.append("")
    
    # 新闻摘要
    news_summary = report.get("news_summary", {})
    if news_summary:
        lines.append("## 📰 动漫资讯")
        lines.append("")
        
        # 热门新闻
        top_news = news_summary.get("top_news", [])
        if top_news:
            lines.append("### 🔥 热门资讯")
            lines.append("")
            for i, news in enumerate(top_news[:5], 1):
                lines.append(f"{i}. **[{news.get('title', '')}]({news.get('url', '')})**")
                lines.append(f"   - 来源: {news.get('source', '')} | 阅读: {news.get('read_count', 0)} | 分类: {news.get('category', '')}")
                if news.get('summary'):
                    lines.append(f"   - 摘要: {news.get('summary')[:100]}...")
                lines.append("")
        
        # 最新新闻
        latest_news = news_summary.get("latest_news", [])
        if latest_news:
            lines.append("### 🆕 最新资讯")
            lines.append("")
            for news in latest_news[:5]:
                lines.append(f"- **[{news.get('title', '')}]({news.get('url', '')})**")
                lines.append(f"  - 来源: {news.get('source', '')} | 发布时间: {news.get('published_at', '')}")
                lines.append("")
        
        # 分类统计
        categories = news_summary.get("categories", {})
        if categories:
            lines.append("### 📂 资讯分类")
            lines.append("")
            for category, items in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
                lines.append(f"- **{category}**: {len(items)} 条")
            lines.append("")
        
        # 来源统计
        top_sources = news_summary.get("top_sources", [])
        if top_sources:
            lines.append("### 🔗 主要来源")
            lines.append("")
            for source in top_sources[:5]:
                lines.append(f"- **{source.get('name', '')}**: {source.get('count', 0)} 条资讯")
            lines.append("")
    
    # 新番摘要
    anime_summary = report.get("anime_summary", {})
    if anime_summary:
        lines.append("## 🎬 新番信息")
        lines.append("")
        
        # 即将开播
        upcoming_anime = anime_summary.get("upcoming_anime", [])
        if upcoming_anime:
            lines.append("### 📅 即将开播")
            lines.append("")
            for anime in upcoming_anime[:5]:
                lines.append(f"- **[{anime.get('title', '')}]({anime.get('url', '')})**")
                lines.append(f"  - 季度: {anime.get('season', '')} | 状态: {anime.get('status', '')}")
                if anime.get('broadcast_time'):
                    lines.append(f"  - 放送时间: {anime.get('broadcast_time')}")
                lines.append("")
        
        # 已开播
        ongoing_anime = anime_summary.get("ongoing_anime", [])
        if ongoing_anime:
            lines.append("### 🔄 正在放送")
            lines.append("")
            for anime in ongoing_anime[:5]:
                lines.append(f"- **[{anime.get('title', '')}]({anime.get('url', '')})**")
                lines.append(f"  - 季度: {anime.get('season', '')} | 状态: {anime.get('status', '')}")
                if anime.get('broadcast_time'):
                    lines.append(f"  - 放送时间: {anime.get('broadcast_time')}")
                lines.append("")
        
        # 季度统计
        by_season = anime_summary.get("by_season", {})
        if by_season:
            lines.append("### 📆 季度分布")
            lines.append("")
            for season, items in sorted(by_season.items()):
                lines.append(f"- **{season}**: {len(items)} 部")
            lines.append("")
        
        # 状态分布
        status_distribution = anime_summary.get("status_distribution", {})
        if status_distribution:
            lines.append("### 📊 状态分布")
            lines.append("")
            for status, count in status_distribution.items():
                lines.append(f"- **{status}**: {count} 部")
            lines.append("")
    
    # 页脚
    lines.append("---")
    lines.append("")
    lines.append("*本报告由 Anime Crawler Skill 自动生成*")
    
    return "\n".join(lines)


def save_integrated_report(report: Dict[str, Any], output_dir: str) -> Path:
    """
    保存整合报告
    
    Args:
        report: 综合报告
        output_dir: 输出目录
        
    Returns:
        保存的文件路径
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 保存 JSON 格式
    json_filename = f"integrated_report_{timestamp}.json"
    json_path = output_path / json_filename
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"[Integrate] JSON 报告已保存到: {json_path}")
    
    # 保存 Markdown 格式
    md_filename = f"integrated_report_{timestamp}.md"
    md_path = output_path / md_filename
    
    markdown_content = generate_markdown_report(report)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    print(f"[Integrate] Markdown 报告已保存到: {md_path}")
    
    return md_path


def main():
    parser = argparse.ArgumentParser(
        description="整合动漫资讯和新番信息，生成综合报告"
    )
    parser.add_argument(
        "input_files",
        nargs="*",
        help="输入 JSON 文件路径（默认从 data/organized/ 目录查找最新文件）"
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
            # 查找最新的整理后 JSON 文件
            organized_dir = Path("data/organized")
            if organized_dir.exists():
                json_files = sorted(organized_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
                if json_files:
                    input_paths = json_files
                    print(f"[Integrate] 找到 {len(input_paths)} 个整理后文件")
                else:
                    print("[Integrate] 错误: 未找到整理后的数据文件", file=sys.stderr)
                    return 1
            else:
                print("[Integrate] 错误: data/organized/ 目录不存在", file=sys.stderr)
                return 1
        
        # 加载数据
        print("[Integrate] 加载整理后的数据...")
        data = load_organized_data(input_paths)
        
        # 生成综合报告
        print("[Integrate] 生成综合报告...")
        report = generate_integrated_report(data)
        
        # 保存报告
        output_path = save_integrated_report(report, args.output_dir)
        
        print("\n[Integrate] 完成！")
        print(f"[Integrate] 报告文件: {output_path}")
        print(f"OUTPUT_FILE:{output_path}")
        
        return 0
        
    except Exception as e:
        print(f"[Integrate] 错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
