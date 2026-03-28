#!/usr/bin/env python3
"""存储脚本"""

import os
import json
import time
from config import STORE_CONFIG


def ensure_data_dir():
    """确保数据目录存在"""
    os.makedirs(STORE_CONFIG['data_dir'], exist_ok=True)
    os.makedirs(STORE_CONFIG['temp_images_dir'], exist_ok=True)


def save_illustrations(illustrations):
    """保存插画数据"""
    ensure_data_dir()
    
    # 读取现有数据
    existing_data = load_illustrations()
    
    # 更新数据
    for illustration in illustrations:
        if isinstance(illustration, dict) and 'id' in illustration:
            existing_data[illustration['id']] = illustration
    
    # 保存数据
    with open(STORE_CONFIG['illustrations_file'], 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
    
    print(f"[INFO] 保存了 {len(illustrations)} 个插画数据")
    return existing_data


def load_illustrations():
    """加载插画数据"""
    ensure_data_dir()
    
    if os.path.exists(STORE_CONFIG['illustrations_file']):
        try:
            with open(STORE_CONFIG['illustrations_file'], 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] 加载插画数据失败: {e}")
    
    return {}


def save_wechat_token(token_data):
    """保存微信 Access Token"""
    ensure_data_dir()
    
    token_data['expires_at'] = time.time() + 7200  # 7200秒有效期
    
    with open(STORE_CONFIG['data_dir'] + '/wechat_token.json', 'w', encoding='utf-8') as f:
        json.dump(token_data, f, ensure_ascii=False, indent=2)
    
    print(f"[INFO] 保存了 Access Token，有效期至: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(token_data['expires_at']))}")


def load_wechat_token():
    """加载微信 Access Token"""
    token_file = STORE_CONFIG['data_dir'] + '/wechat_token.json'
    
    if os.path.exists(token_file):
        try:
            with open(token_file, 'r', encoding='utf-8') as f:
                token_data = json.load(f)
                
                # 检查是否过期
                if time.time() < token_data.get('expires_at', 0):
                    return token_data
                else:
                    print("[INFO] Access Token 已过期")
        except Exception as e:
            print(f"[ERROR] 加载 Access Token 失败: {e}")
    
    return None


def get_illustration_by_id(illustration_id):
    """根据ID获取插画数据"""
    illustrations = load_illustrations()
    return illustrations.get(illustration_id)


def get_illustration_by_url(url):
    """根据URL获取插画数据"""
    illustrations = load_illustrations()
    for illustration in illustrations.values():
        if illustration.get('url') == url:
            return illustration
    return None


if __name__ == '__main__':
    # 测试存储功能
    test_data = [
        {
            'id': '11497',
            'title': '初音未来插画特辑',
            'url': 'https://www.pixivision.net/zh/a/11497',
            'tags': ['初音未来', 'VOCALOID', '插画'],
            'images': ['https://i.pximg.net/img-original/img/2024/03/01/12/00/00/11497_01.png'],
            'description': '诞生自语音合成软件「VOCALOID」系列的虚拟歌手初音未来...'
        }
    ]
    
    save_illustrations(test_data)
    loaded = load_illustrations()
    print(f"加载的数据: {loaded}")
    
    # 测试获取功能
    illustration = get_illustration_by_id('11497')
    print(f"根据ID获取: {illustration}")
