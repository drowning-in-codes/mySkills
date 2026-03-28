#!/usr/bin/env python3
"""爬取脚本"""

import os
import time
import requests
from bs4 import BeautifulSoup
from config import CRAWL_CONFIG, STORE_CONFIG


def crawl_list(pages=None):
    """爬取插画列表"""
    if pages:
        start_page, end_page = pages
    else:
        start_page, end_page = CRAWL_CONFIG["page_range"]

    illustrations = []

    for page in range(start_page, end_page + 1):
        # 使用插画特辑页面 URL
        url = f"{CRAWL_CONFIG['illustration_url']}?p={page}"
        print(f"[INFO] 正在爬取插画特辑页面: {url}")

        try:
            response = requests.get(
                url, headers=CRAWL_CONFIG["headers"], timeout=CRAWL_CONFIG["timeout"]
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")

            # 提取插画信息
            for item in soup.select("li.article-card-container"):
                try:
                    # 提取标题
                    title_elem = item.select_one("h2.arc__title a")
                    title = title_elem.text.strip() if title_elem else ""

                    # 提取链接
                    link = title_elem["href"] if title_elem else ""
                    if link and not link.startswith("http"):
                        link = f"https://www.pixivision.net{link}"

                    # 提取缩略图
                    thumbnail_elem = item.select_one("div._thumbnail")
                    thumbnail_url = ""
                    if thumbnail_elem and "style" in thumbnail_elem.attrs:
                        style = thumbnail_elem["style"]
                        import re

                        match = re.search(r"url\((.*?)\)", style)
                        if match:
                            thumbnail_url = match.group(1).strip("'\"")

                    # 提取标签
                    tags = []
                    for tag_elem in item.select(
                        "ul._tag-list li.tls__list-item-container div.tls__list-item"
                    ):
                        tag = tag_elem.text.strip()
                        if tag:
                            tags.append(tag)

                    # 提取日期
                    date_elem = item.select_one("time._date")
                    date = date_elem.text.strip() if date_elem else ""

                    illustrations.append(
                        {
                            "title": title,
                            "url": link,
                            "thumbnail": thumbnail_url,
                            "tags": tags,
                            "date": date,
                        }
                    )
                except Exception as e:
                    print(f"[ERROR] 提取插画信息失败: {e}")

            time.sleep(3)  # 增加延迟，避免被网站限制

        except Exception as e:
            print(f"[ERROR] 爬取页面失败: {e}")

    return illustrations


def crawl_illustration(url):
    """爬取指定插画详情"""
    print(f"[INFO] 正在爬取插画详情: {url}")

    try:
        response = requests.get(
            url, headers=CRAWL_CONFIG["headers"], timeout=CRAWL_CONFIG["timeout"]
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        # 提取标题
        title = ""
        title_elem = soup.select_one("h1")
        if not title_elem:
            title_elem = soup.select_one("h2.arc__title")
        if title_elem:
            title = title_elem.text.strip()

        # 提取标签
        tags = []
        # 尝试不同的标签选择器
        tag_selectors = [
            "ul._tag-list li.tls__list-item-container div.tls__list-item",
            ".tag",
            'a[href*="/t/"]',
        ]

        for selector in tag_selectors:
            if tags:
                break
            for tag_elem in soup.select(selector):
                try:
                    tag = tag_elem.text.strip()
                    if tag and tag not in tags:
                        tags.append(tag)
                except:
                    pass

        # 提取图片
        images = []
        # 尝试不同的图片选择器
        img_selectors = [
            'img[src*="img-original"]',
            'img[src*=".png"], img[src*=".jpg"], img[src*=".jpeg"]',
            'div._thumbnail[style*="background-image"]',
        ]

        for selector in img_selectors:
            for img_elem in soup.select(selector):
                try:
                    if "src" in img_elem.attrs:
                        src = img_elem["src"]
                        if src.startswith("//"):
                            src = f"https:{src}"
                        if src not in images:
                            images.append(src)
                    elif "style" in img_elem.attrs:
                        # 从背景图片中提取
                        style = img_elem["style"]
                        import re

                        match = re.search(r"url\((.*?)\)", style)
                        if match:
                            src = match.group(1).strip("'\"")
                            if src.startswith("//"):
                                src = f"https:{src}"
                            if src not in images:
                                images.append(src)
                except:
                    pass

        # 提取描述
        description = ""
        # 尝试不同的描述选择器
        desc_selectors = [
            ".article-content",
            ".arc__content",
            'div[class*="content"]',
            "p",
        ]

        for selector in desc_selectors:
            if description:
                break
            for elem in soup.select(selector):
                text = elem.text.strip()
                if text and len(text) > 50:  # 确保是有意义的描述
                    description = text
                    break

        # 如果还是没有找到描述，尝试组合多个段落
        if not description:
            desc_parts = []
            for p in soup.select("p"):
                text = p.text.strip()
                if text:
                    desc_parts.append(text)
            if desc_parts:
                description = " ".join(desc_parts[:5])  # 取前5个段落

        # 提取插画ID
        illustration_id = url.split("/")[-1] if url.split("/")[-1].isdigit() else ""

        return {
            "id": illustration_id,
            "title": title,
            "url": url,
            "tags": tags,
            "images": images,
            "description": description.strip(),
        }

    except Exception as e:
        print(f"[ERROR] 爬取插画详情失败: {e}")
        return None


def download_image(url, save_path):
    """下载图片"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, "wb") as f:
            f.write(response.content)

        return True
    except Exception as e:
        print(f"[ERROR] 下载图片失败: {e}")
        return False


if __name__ == "__main__":
    # 测试爬取列表
    illustrations = crawl_list((1, 2))
    print(f"爬取到 {len(illustrations)} 个插画")

    # 测试爬取单个插画
    if illustrations:
        detail = crawl_illustration(illustrations[0]["url"])
        print(f"插画详情: {detail}")
