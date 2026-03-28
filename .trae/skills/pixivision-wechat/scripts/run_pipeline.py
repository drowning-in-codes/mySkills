#!/usr/bin/env python3
"""主流程脚本"""

import os
import argparse
from crawl import crawl_list, crawl_illustration, download_image
from extract import process_illustration_data
from store import save_illustrations, get_illustration_by_id, get_illustration_by_url
from wechat import upload_image, add_material, add_draft, send_all
from config import STORE_CONFIG, set_wechat_credentials, WECHAT_CONFIG


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Pixivision 插画爬取与微信上传工具")

    # 功能选择
    parser.add_argument("--crawl", action="store_true", help="爬取插画")
    parser.add_argument("--upload", action="store_true", help="上传到微信")
    parser.add_argument("--draft", action="store_true", help="创建草稿")
    parser.add_argument("--send", action="store_true", help="群发消息")

    # 爬取参数
    parser.add_argument("--pages", type=str, help="爬取页码范围，如 1-5")
    parser.add_argument("--url", type=str, help="爬取指定插画URL")

    # 操作参数
    parser.add_argument("--illustration", type=str, help="指定插画ID")
    parser.add_argument("--draft_id", type=str, help="指定草稿ID")

    # 微信配置参数
    parser.add_argument("--set-appid", type=str, help="设置微信公众号AppID")
    parser.add_argument("--set-secret", type=str, help="设置微信公众号AppSecret")
    parser.add_argument("--save-config", action="store_true", help="保存微信配置到文件")

    # 查看当前配置
    parser.add_argument(
        "--show-config", action="store_true", help="显示当前微信配置状态"
    )

    return parser.parse_args()


def run_crawl(args):
    """执行爬取任务"""
    if args.url:
        # 爬取指定插画
        data = crawl_illustration(args.url)
        if data:
            processed = process_illustration_data(data)
            if processed:
                save_illustrations([processed])
                print(f"[INFO] 爬取完成: {processed['title']}")
            else:
                print("[ERROR] 处理插画数据失败")
        else:
            print("[ERROR] 爬取插画失败")
    else:
        # 爬取列表
        pages = None
        if args.pages:
            try:
                start, end = map(int, args.pages.split("-"))
                pages = (start, end)
            except:
                print("[ERROR] 页码格式错误，应为 1-5 格式")
                return

        illustrations = crawl_list(pages)
        if illustrations:
            # 对每个插画进行详情爬取
            details = []
            for item in illustrations:
                detail = crawl_illustration(item["url"])
                if detail:
                    processed = process_illustration_data(detail)
                    if processed:
                        details.append(processed)

            if details:
                save_illustrations(details)
                print(f"[INFO] 爬取完成，共 {len(details)} 个插画")
            else:
                print("[ERROR] 没有成功爬取到插画详情")
        else:
            print("[ERROR] 没有爬取到插画列表")


def run_upload(args):
    """执行上传任务"""
    if not args.illustration:
        print("[ERROR] 请指定插画ID")
        return

    illustration = get_illustration_by_id(args.illustration)
    if not illustration:
        print(f"[ERROR] 找不到插画ID: {args.illustration}")
        return

    print(f"[INFO] 正在处理插画: {illustration['title']}")

    # 下载并上传图片
    uploaded_images = []
    for i, img_url in enumerate(illustration["images"][:5]):  # 限制上传数量
        img_name = f"{args.illustration}_{i}.jpg"
        img_path = os.path.join(STORE_CONFIG["temp_images_dir"], img_name)

        if download_image(img_url, img_path):
            print(f"[INFO] 下载图片成功: {img_path}")

            # 上传图片
            img_url = upload_image(img_path)
            if img_url:
                uploaded_images.append(img_url)

            # 上传为永久素材（封面用）
            if i == 0:  # 第一张作为封面
                cover_media_id = add_material(img_path)
                if cover_media_id:
                    print(f"[INFO] 封面素材上传成功，media_id: {cover_media_id}")
        else:
            print(f"[ERROR] 下载图片失败: {img_url}")

    if uploaded_images:
        print(f"[INFO] 成功上传 {len(uploaded_images)} 张图片")
        # 可以在这里保存上传后的图片URL
    else:
        print("[ERROR] 没有成功上传图片")


def run_draft(args):
    """执行创建草稿任务"""
    if not args.illustration:
        print("[ERROR] 请指定插画ID")
        return

    illustration = get_illustration_by_id(args.illustration)
    if not illustration:
        print(f"[ERROR] 找不到插画ID: {args.illustration}")
        return

    print(f"[INFO] 正在为插画创建草稿: {illustration['title']}")

    # 下载并上传封面图片
    cover_media_id = None
    if illustration["images"]:
        cover_url = illustration["images"][0]
        cover_path = os.path.join(
            STORE_CONFIG["temp_images_dir"], f"{args.illustration}_cover.jpg"
        )

        if download_image(cover_url, cover_path):
            cover_media_id = add_material(cover_path)
            if not cover_media_id:
                print("[WARNING] 封面上传失败，将使用默认封面")

    # 构建内容
    content = f"<h1>{illustration['title']}</h1>"
    content += f"<p>{illustration['description']}</p>"

    if illustration["tags"]:
        content += (
            "<p><strong>标签:</strong> " + ", ".join(illustration["tags"]) + "</p>"
        )

    # 插入图片
    for img_url in illustration["images"][:5]:  # 限制图片数量
        content += f'<img src="{img_url}" style="max-width:100%;" />'

    content += (
        f"<p><a href=\"{illustration['url']}\" target=\"_blank\">查看原文</a></p>"
    )

    # 创建草稿
    draft_id = add_draft(
        title=illustration["title"],
        content=content,
        cover_media_id=cover_media_id,
        author="Pixivision",
    )

    if draft_id:
        print(f"[INFO] 草稿创建成功，ID: {draft_id}")
    else:
        print("[ERROR] 草稿创建失败")


def run_send(args):
    """执行群发任务"""
    if not args.draft_id:
        print("[ERROR] 请指定草稿ID")
        return

    print(f"[INFO] 正在群发消息，草稿ID: {args.draft_id}")

    # 群发消息
    msg_id = send_all(args.draft_id)

    if msg_id:
        print(f"[INFO] 消息群发成功，消息ID: {msg_id}")
    else:
        print("[ERROR] 消息群发失败")


def main():
    """主函数"""
    args = parse_args()

    # 处理微信配置
    if args.set_appid and args.set_secret:
        set_wechat_credentials(args.set_appid, args.set_secret, args.save_config)
        print("[INFO] 微信凭证已设置")
        return

    # 只设置 AppID
    if args.set_appid:
        set_wechat_credentials(
            args.set_appid, WECHAT_CONFIG["app_secret"], args.save_config
        )
        print("[INFO] 微信 AppID 已设置")
        return

    # 只设置 AppSecret
    if args.set_secret:
        set_wechat_credentials(
            WECHAT_CONFIG["app_id"], args.set_secret, args.save_config
        )
        print("[INFO] 微信 AppSecret 已设置")
        return

    # 显示当前配置
    if args.show_config:
        print("=== 微信配置状态 ===")
        print(f"AppID: {'已设置' if WECHAT_CONFIG['app_id'] else '未设置'}")
        print(f"AppSecret: {'已设置' if WECHAT_CONFIG['app_secret'] else '未设置'}")
        print(
            f"配置文件: wechat_config.json {'存在' if os.path.exists('wechat_config.json') else '不存在'}"
        )
        return

    # 执行其他任务
    if args.crawl:
        run_crawl(args)
    elif args.upload:
        # 检查是否有微信凭证
        if not WECHAT_CONFIG["app_id"] or not WECHAT_CONFIG["app_secret"]:
            print("[ERROR] 请先设置微信凭证，使用 --set-appid 和 --set-secret 参数")
            return
        run_upload(args)
    elif args.draft:
        # 检查是否有微信凭证
        if not WECHAT_CONFIG["app_id"] or not WECHAT_CONFIG["app_secret"]:
            print("[ERROR] 请先设置微信凭证，使用 --set-appid 和 --set-secret 参数")
            return
        run_draft(args)
    elif args.send:
        # 检查是否有微信凭证
        if not WECHAT_CONFIG["app_id"] or not WECHAT_CONFIG["app_secret"]:
            print("[ERROR] 请先设置微信凭证，使用 --set-appid 和 --set-secret 参数")
            return
        run_send(args)
    else:
        print("请指定要执行的操作，使用 --help 查看帮助")


if __name__ == "__main__":
    main()
