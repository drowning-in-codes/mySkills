# Build Skills - 实用的 Skills 仓库

这是一个收集和整理各种实用 Skills 的仓库，旨在帮助开发者快速构建自动化工作流程。

## 📁 仓库结构

```
build_skills/
├── README.md                          # 本文件
└── .trae/skills/                      # Skills 目录
    └── hn-crawler/                    # HN 资讯爬虫 Skill
        ├── SKILL.md                   # Skill 定义文档
        └── scripts/                   # 处理脚本
            ├── crawl.py               # 爬取脚本
            ├── extract.py             # 提取脚本
            ├── organize.py            # 整理脚本
            ├── summarize.py           # 总结脚本
            ├── run_pipeline.py        # 一键运行脚本
            └── requirements.txt       # 依赖文件
```

## 🚀 现有 Skills

### 1. HN Crawler - HN 资讯爬虫

爬取 [hn.aimaker.dev](https://hn.aimaker.dev/) 网站资讯，执行完整的 **爬取 -> 提取 -> 整理 -> 总结** 流程。

#### 功能特点

- 🌐 **智能爬取**: 支持 HTTP 请求重试机制，自动处理网络异常
- 🔍 **灵活提取**: 支持多种 HTML 结构，自动识别文章元素
- 🏷️ **自动分类**: 根据标题和 URL 智能分类（AI、Programming、Startup 等）
- 🧹 **数据清洗**: 自动去重、过滤、标准化处理
- 📊 **丰富报告**: 生成包含热门话题、分类统计、阅读建议的 Markdown 报告
- ⚙️ **灵活配置**: 支持环境变量和命令行参数

#### 快速开始

```bash
# 进入 skill 目录
cd .trae/skills/hn-crawler/scripts

# 安装依赖
pip install -r requirements.txt

# 运行完整流程
python run_pipeline.py
```

### 2. Anime Crawler - 动漫资讯爬虫

爬取多个动漫资讯网站和新番信息，执行完整的 **爬取 -> 提取 -> 整理 -> 整合** 流程。

#### 支持的网站

- **资讯网站**: 梦域动漫 (moelove.cn)、AniFun (anifun.cn)、HotACG (hotacg.com)
- **新番信息**: 長門番堂 (yuc.wiki)

#### 功能特点

- 🌐 **多站点爬取**: 同时爬取多个动漫相关网站
- 🎬 **新番信息**: 专门提取新番播送时间和状态
- 🔍 **智能提取**: 针对不同网站的结构进行优化
- 📊 **综合报告**: 整合资讯和新番信息，生成统一报告
- ⚙️ **灵活配置**: 支持选择特定网站进行爬取

#### 快速开始

```bash
# 进入 skill 目录
cd .trae/skills/anime-crawler/scripts

# 安装依赖
pip install -r requirements.txt

# 运行完整流程
python run_pipeline.py

# 只爬取特定网站
python run_pipeline.py --websites moelove,yuc
```

#### 工作流程

```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌───────────┐
│  Crawl  │ -> │ Extract  │ -> │ Organize │ -> │ Integrate │
│  爬取   │    │  提取    │    │  整理    │    │  整合     │
└─────────┘    └──────────┘    └──────────┘    └───────────┘
     │               │               │               │
     ▼               ▼               ▼               ▼
data/raw/      data/extracted/  data/organized/  data/integrated/
*.html          *.json           *.json           *.md
```

#### 输出示例

**数据概览**:
- 新闻总数: 45
- 新番总数: 68

**热门资讯**:
- 《地狱老师》新 PV 与视觉图公开 主题曲信息释出
- 《海贼王》真人剧第二季公开乔巴影像，2026年上线

**新番信息**:
- **即将开播**: 2025年7月新番 15 部
- **正在放送**: 2025年4月新番 28 部

### 3. Pixivision Wechat - 插画爬取与微信上传

爬取 [Pixivision](https://www.pixivision.net/zh/) 网站插画，并通过微信公众平台接口上传图片、创建草稿并群发消息。

#### 功能特点

- 🌐 **智能爬取**: 支持爬取插画列表和指定插画详情
- 🎨 **图片处理**: 自动下载和处理插画图片
- 💾 **数据存储**: 将插画信息存储到 JSON 文件
- 📱 **微信集成**: 完整的微信公众平台接口集成
- 🔒 **Token 管理**: 自动管理 Access Token 过期和刷新
- ⚙️ **灵活配置**: 支持命令行参数和配置文件

#### 支持的微信接口

- **素材上传**: 永久素材、临时素材、图文消息内图片
- **草稿管理**: 新增草稿
- **消息群发**: 根据标签群发消息

#### 快速开始

```bash
# 进入 skill 目录
cd .trae/skills/pixivision-wechat/scripts

# 安装依赖
pip install -r requirements.txt

# 配置微信参数（在 config.py 中设置 app_id 和 app_secret）

# 爬取插画列表
python run_pipeline.py --crawl --pages 1-3

# 爬取指定插画
python run_pipeline.py --crawl --url https://www.pixivision.net/zh/a/11497

# 上传到微信
python run_pipeline.py --upload --illustration 11497

# 创建草稿
python run_pipeline.py --draft --illustration 11497

# 群发消息
python run_pipeline.py --send --draft_id 123456
```

#### 工作流程

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

## 🛠️ 如何添加新 Skill

1. 在 `.trae/skills/` 目录下创建新的 skill 目录
2. 创建 `SKILL.md` 文件，包含以下内容：
   - Skill 名称和描述
   - 使用方法
   - 配置选项
3. 添加必要的脚本和配置文件
4. 更新本 README.md 添加新 Skill 的说明

### Skill 目录结构规范

```
.trae/skills/<skill-name>/
├── SKILL.md              # 必须：Skill 定义文档
├── README.md             # 可选：详细说明文档
└── scripts/              # 可选：处理脚本
    ├── *.py
    └── requirements.txt
```

### SKILL.md 格式

```markdown
---
name: "skill-name"
description: "简短描述，说明功能和使用场景"
---

# Skill 标题

详细说明...

## 使用方法

...

## 配置选项

...
```

## 📋 环境要求

- Python 3.8+
- pip

## 🤝 贡献指南

欢迎提交新的 Skills 或改进现有 Skills！

1. Fork 本仓库
2. 创建你的 Skill 分支
3. 添加或修改 Skills
4. 提交 Pull Request

## 📄 许可证

MIT License

## 🙏 致谢

感谢所有贡献者！

---

*让自动化工作更简单* ✨
