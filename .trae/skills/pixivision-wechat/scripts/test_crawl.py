#!/usr/bin/env python3
"""测试爬取功能"""

import requests
from crawl import crawl_list, crawl_illustration
from extract import process_illustration_data
from store import save_illustrations, load_illustrations


def test_connection():
    """测试网络连接"""
    print("=== 测试网络连接 ===")
    # 测试插画特辑页面
    url = "https://www.pixivision.net/zh/c/illustration"
    try:
        response = requests.get(url, timeout=30)
        print(f"连接状态码: {response.status_code}")
        if response.status_code == 200:
            print("连接成功！")
            return True
        else:
            print(f"连接失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"连接失败: {e}")
        return False


def test_crawl_list():
    """测试爬取列表"""
    print("=== 测试爬取列表 ===")
    print("开始爬取第1页...")
    illustrations = crawl_list((1, 1))  # 只爬取第一页
    print(f"爬取完成，共找到 {len(illustrations)} 个插画")

    if illustrations:
        print("\n找到的插画:")
        for i, item in enumerate(illustrations[:3]):  # 只显示前3个
            print(f"\n{ i+1 }. {item['title']}")
            print(f"   URL: {item['url']}")
            print(f"   缩略图: {item['thumbnail']}")
            print(f"   标签: {', '.join(item['tags'])}")
            print(f"   日期: {item['date']}")
    else:
        print("没有找到任何插画，可能是选择器不匹配或网站结构变化")

    return illustrations


def test_crawl_illustration(url):
    """测试爬取单个插画"""
    print(f"\n=== 测试爬取插画详情: {url} ===")
    data = crawl_illustration(url)

    if data:
        print("爬取成功！")
        processed = process_illustration_data(data)
        if processed:
            print(f"标题: {processed['title']}")
            print(f"URL: {processed['url']}")
            print(f"标签: {', '.join(processed['tags'])}")
            print(f"图片数量: {len(processed['images'])}")
            print(f"描述: {processed['description'][:100]}...")  # 只显示前100个字符
            return processed
        else:
            print("数据处理失败")
    else:
        print("爬取失败")

    return None


def test_store():
    """测试存储功能"""
    print("\n=== 测试存储功能 ===")
    # 先爬取一些数据
    illustrations = crawl_list((1, 1))
    if illustrations:
        print(f"开始处理 {len(illustrations)} 个插画...")
        # 处理数据
        processed = []
        for item in illustrations:
            detail = crawl_illustration(item["url"])
            if detail:
                processed_data = process_illustration_data(detail)
                if processed_data:
                    processed.append(processed_data)

        if processed:
            print(f"处理完成，共 {len(processed)} 个有效数据")
            # 保存数据
            saved = save_illustrations(processed)
            print(f"保存了 {len(saved)} 个插画数据")

            # 加载数据
            loaded = load_illustrations()
            print(f"加载了 {len(loaded)} 个插画数据")

            # 显示一个示例
            if loaded:
                illustration_id = list(loaded.keys())[0]
                print(f"\n示例数据: {loaded[illustration_id]['title']}")
        else:
            print("没有有效数据可存储")
    else:
        print("没有爬取到数据")


def main():
    """主测试函数"""
    print("开始测试 Pixivision 爬取功能...")
    print("=" * 50)

    try:
        # 测试网络连接
        if not test_connection():
            print("网络连接失败，无法继续测试")
            return

        # 测试1: 爬取列表
        illustrations = test_crawl_list()

        # 测试2: 爬取单个插画
        if illustrations:
            test_crawl_illustration(illustrations[0]["url"])

        # 测试3: 测试存储
        test_store()

    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 50)
    print("测试完成！")


if __name__ == "__main__":
    main()
