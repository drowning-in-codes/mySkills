#!/usr/bin/env python3
"""
一键运行完整流程脚本

执行完整的爬取 -> 提取 -> 整理 -> 整合流程
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime


# 脚本路径
SCRIPTS_DIR = Path(__file__).parent
CRAWL_SCRIPT = SCRIPTS_DIR / "crawl.py"
EXTRACT_SCRIPT = SCRIPTS_DIR / "extract.py"
ORGANIZE_SCRIPT = SCRIPTS_DIR / "organize.py"
INTEGRATE_SCRIPT = SCRIPTS_DIR / "integrate.py"


def run_script(script_path: Path, args: list = None) -> tuple:
    """
    运行单个脚本
    
    Args:
        script_path: 脚本路径
        args: 额外参数
        
    Returns:
        (returncode, output_file)
    """
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    
    print(f"\n{'='*60}")
    print(f"运行: {script_path.name}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # 打印输出
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        # 解析输出文件路径
        output_files = []
        for line in result.stdout.split('\n'):
            if line.startswith('OUTPUT_FILE:'):
                output_files.append(line.replace('OUTPUT_FILE:', '').strip())
        
        return result.returncode, output_files
        
    except Exception as e:
        print(f"运行脚本时出错: {e}", file=sys.stderr)
        return 1, []


def run_pipeline(
    websites: List[str] = None,
    min_read_count: int = 0,
    skip_crawl: bool = False,
    skip_extract: bool = False,
    skip_organize: bool = False,
    skip_integrate: bool = False,
    input_files: List[str] = None,
) -> int:
    """
    运行完整流程
    
    Args:
        websites: 要爬取的网站列表
        min_read_count: 最小阅读数阈值
        skip_crawl: 跳过爬取步骤
        skip_extract: 跳过提取步骤
        skip_organize: 跳过整理步骤
        skip_integrate: 跳过整合步骤
        input_files: 输入文件（用于跳过某些步骤时）
        
    Returns:
        退出码
    """
    start_time = datetime.now()
    
    print("\n" + "="*60)
    print("Anime Crawler Skill - 完整流程")
    print("="*60)
    print(f"开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    if websites:
        print(f"目标网站: {', '.join(websites)}")
    print("="*60)
    
    current_files = input_files or []
    
    # Step 1: Crawl
    if not skip_crawl:
        crawl_args = []
        if websites:
            crawl_args.extend(["--websites", ",".join(websites)])
        
        returncode, output_files = run_script(CRAWL_SCRIPT, crawl_args)
        if returncode != 0:
            print("\n[Pipeline] ❌ 爬取步骤失败", file=sys.stderr)
            return 1
        current_files = output_files
        print("\n[Pipeline] ✅ 爬取完成")
    else:
        print("\n[Pipeline] ⏭️ 跳过爬取步骤")
    
    # Step 2: Extract
    if not skip_extract:
        extract_args = current_files
        
        returncode, output_files = run_script(EXTRACT_SCRIPT, extract_args)
        if returncode != 0:
            print("\n[Pipeline] ❌ 提取步骤失败", file=sys.stderr)
            return 1
        current_files = output_files
        print("\n[Pipeline] ✅ 提取完成")
    else:
        print("\n[Pipeline] ⏭️ 跳过提取步骤")
    
    # Step 3: Organize
    if not skip_organize:
        organize_args = current_files.copy()
        if min_read_count > 0:
            organize_args.extend(["--min-read-count", str(min_read_count)])
        
        returncode, output_files = run_script(ORGANIZE_SCRIPT, organize_args)
        if returncode != 0:
            print("\n[Pipeline] ❌ 整理步骤失败", file=sys.stderr)
            return 1
        current_files = output_files
        print("\n[Pipeline] ✅ 整理完成")
    else:
        print("\n[Pipeline] ⏭️ 跳过整理步骤")
    
    # Step 4: Integrate
    if not skip_integrate:
        integrate_args = current_files
        
        returncode, output_files = run_script(INTEGRATE_SCRIPT, integrate_args)
        if returncode != 0:
            print("\n[Pipeline] ❌ 整合步骤失败", file=sys.stderr)
            return 1
        current_files = output_files
        print("\n[Pipeline] ✅ 整合完成")
    else:
        print("\n[Pipeline] ⏭️ 跳过整合步骤")
    
    # 完成
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "="*60)
    print("流程完成！")
    print("="*60)
    print(f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总耗时: {duration:.2f} 秒")
    if current_files:
        print(f"最终输出: {current_files[-1]}")
    print("="*60)
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="一键运行 Anime Crawler 完整流程",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 运行完整流程
  python run_pipeline.py
  
  # 指定要爬取的网站
  python run_pipeline.py --websites moelove,yuc
  
  # 只运行提取后的步骤（跳过爬取）
  python run_pipeline.py --skip-crawl --input-files data/raw/moelove_news_xxx.html
  
  # 只运行整合步骤
  python run_pipeline.py --skip-crawl --skip-extract --skip-organize \
    --input-files data/organized/news_organized_xxx.json data/organized/anime_organized_xxx.json
  
  # 过滤低分资讯
  python run_pipeline.py --min-read-count 100
        """
    )
    
    parser.add_argument(
        "--websites",
        default=os.getenv("WEBSITES", "moelove,anifun,hotacg,yuc"),
        help="要爬取的网站列表（逗号分隔，默认: moelove,anifun,hotacg,yuc"))
    parser.add_argument(
        "--min-read-count",
        type=int,
        default=0,
        help="最小阅读数阈值 (默认: 0)"
    )
    parser.add_argument(
        "--skip-crawl",
        action="store_true",
        help="跳过爬取步骤"
    )
    parser.add_argument(
        "--skip-extract",
        action="store_true",
        help="跳过提取步骤"
    )
    parser.add_argument(
        "--skip-organize",
        action="store_true",
        help="跳过整理步骤"
    )
    parser.add_argument(
        "--skip-integrate",
        action="store_true",
        help="跳过整合步骤"
    )
    parser.add_argument(
        "--input-files",
        nargs="*",
        help="输入文件路径（用于跳过某些步骤时）"
    )
    
    args = parser.parse_args()
    
    # 检查是否所有步骤都被跳过
    if all([args.skip_crawl, args.skip_extract, args.skip_organize, args.skip_integrate]):
        print("错误: 所有步骤都被跳过，没有什么可做的", file=sys.stderr)
        return 1
    
    # 解析网站列表
    websites = [w.strip() for w in args.websites.split(",") if w.strip()]
    if not websites:
        websites = ["moelove", "anifun", "hotacg", "yuc"]
    
    return run_pipeline(
        websites=websites,
        min_read_count=args.min_read_count,
        skip_crawl=args.skip_crawl,
        skip_extract=args.skip_extract,
        skip_organize=args.skip_organize,
        skip_integrate=args.skip_integrate,
        input_files=args.input_files,
    )


if __name__ == "__main__":
    sys.exit(main())
