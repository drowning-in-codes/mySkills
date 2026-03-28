#!/usr/bin/env python3
"""微信接口脚本"""

import requests
import os
import json
from config import WECHAT_CONFIG, STORE_CONFIG
from store import save_wechat_token, load_wechat_token


def get_access_token():
    """获取微信 Access Token"""
    # 先尝试加载本地存储的 token
    token_data = load_wechat_token()
    if token_data and 'access_token' in token_data:
        return token_data['access_token']
    
    # 如果没有或已过期，重新获取
    if not WECHAT_CONFIG['app_id'] or not WECHAT_CONFIG['app_secret']:
        print("[ERROR] 请在 config.py 中设置 app_id 和 app_secret")
        return None
    
    url = WECHAT_CONFIG['api_urls']['access_token']
    params = {
        'grant_type': 'client_credential',
        'appid': WECHAT_CONFIG['app_id'],
        'secret': WECHAT_CONFIG['app_secret']
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        if 'access_token' in data:
            save_wechat_token(data)
            return data['access_token']
        else:
            print(f"[ERROR] 获取 Access Token 失败: {data}")
            return None
    
    except Exception as e:
        print(f"[ERROR] 获取 Access Token 失败: {e}")
        return None


def upload_image(image_path):
    """上传图片到微信"""
    access_token = get_access_token()
    if not access_token:
        return None
    
    url = WECHAT_CONFIG['api_urls']['upload_image']
    params = {'access_token': access_token}
    
    try:
        with open(image_path, 'rb') as f:
            files = {'media': f}
            response = requests.post(url, params=params, files=files, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            if 'url' in data:
                print(f"[INFO] 图片上传成功，URL: {data['url']}")
                return data['url']
            else:
                print(f"[ERROR] 图片上传失败: {data}")
                return None
    
    except Exception as e:
        print(f"[ERROR] 图片上传失败: {e}")
        return None


def upload_media(image_path, media_type='image'):
    """上传临时素材"""
    access_token = get_access_token()
    if not access_token:
        return None
    
    url = WECHAT_CONFIG['api_urls']['upload_media']
    params = {
        'access_token': access_token,
        'type': media_type
    }
    
    try:
        with open(image_path, 'rb') as f:
            files = {'media': f}
            response = requests.post(url, params=params, files=files, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            if 'media_id' in data:
                print(f"[INFO] 临时素材上传成功，media_id: {data['media_id']}")
                return data['media_id']
            else:
                print(f"[ERROR] 临时素材上传失败: {data}")
                return None
    
    except Exception as e:
        print(f"[ERROR] 临时素材上传失败: {e}")
        return None


def add_material(image_path, media_type='image'):
    """上传永久素材"""
    access_token = get_access_token()
    if not access_token:
        return None
    
    url = WECHAT_CONFIG['api_urls']['add_material']
    params = {
        'access_token': access_token,
        'type': media_type
    }
    
    try:
        with open(image_path, 'rb') as f:
            files = {'media': f}
            response = requests.post(url, params=params, files=files, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            if 'media_id' in data:
                print(f"[INFO] 永久素材上传成功，media_id: {data['media_id']}")
                return data['media_id']
            else:
                print(f"[ERROR] 永久素材上传失败: {data}")
                return None
    
    except Exception as e:
        print(f"[ERROR] 永久素材上传失败: {e}")
        return None


def add_draft(title, content, cover_media_id=None, author=''):
    """新增草稿"""
    access_token = get_access_token()
    if not access_token:
        return None
    
    url = WECHAT_CONFIG['api_urls']['add_draft']
    params = {'access_token': access_token}
    
    data = {
        'articles': [{
            'title': title,
            'content': content,
            'author': author
        }]
    }
    
    if cover_media_id:
        data['articles'][0]['thumb_media_id'] = cover_media_id
    
    try:
        response = requests.post(url, params=params, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        if 'media_id' in result:
            print(f"[INFO] 草稿创建成功，media_id: {result['media_id']}")
            return result['media_id']
        else:
            print(f"[ERROR] 草稿创建失败: {result}")
            return None
    
    except Exception as e:
        print(f"[ERROR] 草稿创建失败: {e}")
        return None


def send_all(media_id, is_to_all=True, tag_id=None):
    """群发消息"""
    access_token = get_access_token()
    if not access_token:
        return None
    
    url = WECHAT_CONFIG['api_urls']['send_all']
    params = {'access_token': access_token}
    
    data = {
        'filter': {
            'is_to_all': is_to_all
        },
        'msgtype': 'mpnews',
        'mpnews': {
            'media_id': media_id
        }
    }
    
    if tag_id and not is_to_all:
        data['filter']['tag_id'] = tag_id
    
    try:
        response = requests.post(url, params=params, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        if 'msg_id' in result:
            print(f"[INFO] 消息群发成功，msg_id: {result['msg_id']}")
            return result['msg_id']
        else:
            print(f"[ERROR] 消息群发失败: {result}")
            return None
    
    except Exception as e:
        print(f"[ERROR] 消息群发失败: {e}")
        return None


if __name__ == '__main__':
    # 测试获取 Access Token
    token = get_access_token()
    print(f"Access Token: {token}")
    
    # 注意：实际使用时需要先设置 app_id 和 app_secret
    # 并且需要有图片文件用于测试
