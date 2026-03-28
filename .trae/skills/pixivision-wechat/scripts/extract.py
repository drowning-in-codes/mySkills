#!/usr/bin/env python3
"""提取脚本"""

import re


def extract_illustration_id(url):
    """从URL中提取插画ID"""
    match = re.search(r'/a/(\d+)', url)
    return match.group(1) if match else ''


def extract_tags(text):
    """从文本中提取标签"""
    # 简单的标签提取逻辑，可根据实际情况调整
    tags = []
    # 这里可以根据实际页面结构调整提取逻辑
    return tags


def clean_text(text):
    """清理文本"""
    if not text:
        return ''
    
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    # 移除首尾空白
    text = text.strip()
    
    return text


def validate_image_url(url):
    """验证图片URL"""
    if not url:
        return False
    
    # 检查是否是有效的图片URL
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    for ext in image_extensions:
        if ext in url.lower():
            return True
    
    return False


def process_illustration_data(data):
    """处理插画数据"""
    if not data:
        return None
    
    # 清理数据
    processed_data = {
        'id': data.get('id', ''),
        'title': clean_text(data.get('title', '')),
        'url': data.get('url', ''),
        'tags': [clean_text(tag) for tag in data.get('tags', []) if clean_text(tag)],
        'images': [img for img in data.get('images', []) if validate_image_url(img)],
        'description': clean_text(data.get('description', ''))
    }
    
    # 如果没有ID，从URL中提取
    if not processed_data['id'] and processed_data['url']:
        processed_data['id'] = extract_illustration_id(processed_data['url'])
    
    return processed_data


if __name__ == '__main__':
    # 测试数据
    test_data = {
        'url': 'https://www.pixivision.net/zh/a/11497',
        'title': '  初音未来插画特辑  ',
        'tags': ['  初音未来  ', 'VOCALOID', '', '  插画  '],
        'images': [
            'https://i.pximg.net/img-original/img/2024/03/01/12/00/00/11497_01.png',
            'invalid_url',
            'https://i.pximg.net/img-original/img/2024/03/01/12/00/00/11497_02.jpg'
        ],
        'description': '  诞生自语音合成软件「VOCALOID」系列的虚拟歌手初音未来...  '
    }
    
    processed = process_illustration_data(test_data)
    print(f"处理后的数据: {processed}")
