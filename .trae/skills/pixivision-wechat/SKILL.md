# Pixivision 插画爬取与微信上传 Skill

## 🎯 功能描述

本 Skill 实现从 Pixivision 网站爬取插画信息，并通过微信公众平台接口上传图片、创建草稿并群发消息的完整流程。

## 🚀 工作流程

```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌─────────────┐    ┌──────────┐
│  Crawl  │ -> │ Extract  │ -> │  Store   │ -> │ WeChat Auth │ -> │  Upload  │
│  爬取   │    │  提取    │    │  存储    │    │  微信认证   │    │  上传    │
└─────────┘    └──────────┘    └──────────┘    └─────────────┘    └──────────┘
     │               │               │               │               │
     ▼               ▼               ▼               ▼               ▼
爬取插画列表     提取插画信息     存储到JSON     获取Access Token  上传到微信
                    │                                   │
                    ▼                                   ▼
            爬取指定插画详情                      新增草稿并群发
```

## 🔧 技术实现

### 1. 爬取功能

- **网站**：`https://www.pixivision.net/zh/`
- **爬取参数**：
  - 页码范围（通过 `p` 参数控制）
  - 支持爬取指定插画URL（如 `https://www.pixivision.net/zh/a/11497`）
- **提取信息**：
  - 插画名称
  - 标签（tags）
  - 对应URL
  - 图片链接
  - 介绍信息

### 2. 存储功能

- **存储格式**：JSON 文件
- **存储位置**：`data/` 目录
- **存储内容**：
  - 插画列表数据
  - 单个插画详情
  - 微信 Access Token（带过期时间）

### 3. 微信接口功能

- **认证**：
  - 支持设置 appid 和 app secret
  - 自动获取和刷新 Access Token（7200秒有效期）

- **素材上传**：
  - 永久素材：`https://api.weixin.qq.com/cgi-bin/material/add_material`
  - 临时素材：`https://api.weixin.qq.com/cgi-bin/media/upload`
  - 图文消息内图片：`https://api.weixin.qq.com/cgi-bin/media/uploadimg`

- **草稿管理**：
  - 新增草稿：`https://api.weixin.qq.com/cgi-bin/draft/add`

- **消息群发**：
  - 根据标签群发：`https://api.weixin.qq.com/cgi-bin/message/mass/sendall`

## 📁 目录结构

```
pixivision-wechat/
├── SKILL.md                  # 本文件
└── scripts/
    ├── crawl.py              # 爬取脚本
    ├── extract.py            # 提取脚本
    ├── store.py              # 存储脚本
    ├── wechat.py             # 微信接口
    ├── config.py             # 配置管理
    ├── requirements.txt      # 依赖
    └── run_pipeline.py       # 主流程
```

## ⚙️ 配置说明

### 1. 微信公众号凭证配置

支持多种方式设置微信公众号 AppID 和 AppSecret：

#### 方式一：命令行设置（推荐）

```bash
# 同时设置 AppID 和 AppSecret，并保存到配置文件
python run_pipeline.py --set-appid "your_app_id" --set-secret "your_app_secret" --save-config

# 只设置 AppID
python run_pipeline.py --set-appid "your_app_id"

# 只设置 AppSecret
python run_pipeline.py --set-secret "your_app_secret"

# 查看当前配置状态
python run_pipeline.py --show-config
```

#### 方式二：配置文件

复制 `wechat_config.example.json` 为 `wechat_config.json`，然后填入您的凭证：

```json
{
  "app_id": "your_app_id_here",
  "app_secret": "your_app_secret_here"
}
```

#### 方式三：环境变量

设置环境变量 `WECHAT_APP_ID` 和 `WECHAT_APP_SECRET`：

```bash
# Windows PowerShell
$env:WECHAT_APP_ID = "your_app_id"
$env:WECHAT_APP_SECRET = "your_app_secret"

# Linux/Mac
export WECHAT_APP_ID="your_app_id"
export WECHAT_APP_SECRET="your_app_secret"
```

### 2. 运行参数

```bash
# 查看当前配置状态
python run_pipeline.py --show-config

# 爬取指定页码范围
python run_pipeline.py --crawl --pages 1-5

# 爬取指定插画
python run_pipeline.py --crawl --url https://www.pixivision.net/zh/a/11448

# 上传到微信（需要先配置微信凭证）
python run_pipeline.py --upload --illustration 11448

# 新增草稿（需要先配置微信凭证）
python run_pipeline.py --draft --illustration 11448

# 群发消息（需要先配置微信凭证）
python run_pipeline.py --send --draft_id 123456
```

### 3. 优先级说明

配置的读取优先级为：
1. **环境变量**（最高优先级）
2. **命令行设置**（当前进程有效）
3. **配置文件**（wechat_config.json）
4. **config.py 默认值**

## 📦 依赖安装

```bash
# 进入 skill 目录
cd .trae/skills/pixivision-wechat/scripts

# 安装依赖
pip install -r requirements.txt
```

## 🎨 输出示例

### 1. 爬取结果（data/illustrations.json）

```json
{
  "11497": {
    "title": "初音未来插画特辑",
    "url": "https://www.pixivision.net/zh/a/11497",
    "tags": ["初音未来", "VOCALOID", "插画"],
    "images": [
      "https://i.pximg.net/img-original/img/2024/03/01/12/00/00/11497_01.png",
      "https://i.pximg.net/img-original/img/2024/03/01/12/00/00/11497_02.png"
    ],
    "description": "诞生自语音合成软件「VOCALOID」系列的虚拟歌手初音未来..."
  }
}
```

### 2. 微信上传结果

```
[INFO] 正在获取 Access Token...
[INFO] Access Token 获取成功，有效期至: 2026-03-29 12:00:00
[INFO] 正在上传图片到微信...
[INFO] 图片上传成功，media_id: 1234567890
[INFO] 正在创建草稿...
[INFO] 草稿创建成功，draft_id: 7890123456
[INFO] 正在群发消息...
[INFO] 消息群发成功，msg_id: 9876543210
```

## 🔒 安全注意事项

1. **不要将 app_id 和 app_secret 硬编码在代码中**
2. **不要将包含 token 的文件提交到版本控制系统**
3. **定期更新 Access Token**
4. **遵守 Pixivision 网站的 robots.txt 规则**
5. **合理控制爬取频率，避免对目标网站造成压力**
