# 配置管理

import os


# 爬取配置
CRAWL_CONFIG = {
    "base_url": "https://www.pixivision.net/zh/",
    "illustration_url": "https://www.pixivision.net/zh/c/illustration",  # 插画特辑页面
    "page_range": (1, 3),  # 爬取页码范围
    "timeout": 30,
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    },
}


def get_wechat_config():
    """获取微信配置，优先从环境变量读取，其次从配置文件读取"""
    # 从环境变量读取
    app_id = os.environ.get("WECHAT_APP_ID", "")
    app_secret = os.environ.get("WECHAT_APP_SECRET", "")

    # 如果环境变量没有设置，尝试从配置文件读取
    if not app_id or not app_secret:
        config_file = "wechat_config.json"
        if os.path.exists(config_file):
            try:
                import json

                with open(config_file, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                    app_id = config_data.get("app_id", app_id)
                    app_secret = config_data.get("app_secret", app_secret)
            except Exception as e:
                print(f"[WARNING] 读取微信配置文件失败: {e}")

    return {
        "app_id": app_id,
        "app_secret": app_secret,
        "token_file": "data/wechat_token.json",
        "api_urls": {
            "access_token": "https://api.weixin.qq.com/cgi-bin/token",
            "upload_image": "https://api.weixin.qq.com/cgi-bin/media/uploadimg",
            "upload_media": "https://api.weixin.qq.com/cgi-bin/media/upload",
            "add_material": "https://api.weixin.qq.com/cgi-bin/material/add_material",
            "add_draft": "https://api.weixin.qq.com/cgi-bin/draft/add",
            "send_all": "https://api.weixin.qq.com/cgi-bin/message/mass/sendall",
        },
    }


# 微信配置
WECHAT_CONFIG = get_wechat_config()


# 存储配置
STORE_CONFIG = {
    "data_dir": "data",
    "illustrations_file": "data/illustrations.json",
    "temp_images_dir": "data/temp_images",
}


def set_wechat_credentials(app_id, app_secret, save_to_file=False):
    """
    设置微信公众号凭证

    Args:
        app_id: 微信公众号AppID
        app_secret: 微信公众号AppSecret
        save_to_file: 是否保存到配置文件
    """
    # 更新当前配置
    WECHAT_CONFIG["app_id"] = app_id
    WECHAT_CONFIG["app_secret"] = app_secret

    # 设置环境变量（当前进程有效）
    os.environ["WECHAT_APP_ID"] = app_id
    os.environ["WECHAT_APP_SECRET"] = app_secret

    # 保存到配置文件
    if save_to_file:
        try:
            import json

            with open("wechat_config.json", "w", encoding="utf-8") as f:
                json.dump(
                    {"app_id": app_id, "app_secret": app_secret},
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
            print(f"[INFO] 微信配置已保存到 wechat_config.json")
        except Exception as e:
            print(f"[ERROR] 保存微信配置文件失败: {e}")
