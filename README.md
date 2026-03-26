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

#### 详细用法

```bash
# 运行完整流程
python run_pipeline.py

# 指定目标 URL
python run_pipeline.py --url https://hn.aimaker.dev/

# 过滤低分文章（只保留分数 >= 50 的）
python run_pipeline.py --min-score 50

# 跳过爬取，从已有 HTML 开始
python run_pipeline.py --skip-crawl --input-file data/raw/hn_aimaker_xxx.html

# 只运行总结步骤
python run_pipeline.py --skip-crawl --skip-extract --skip-organize \
    --input-file data/organized/articles_organized_xxx.json
```

#### 工作流程

```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌───────────┐
│  Crawl  │ -> │ Extract  │ -> │ Organize │ -> │ Summarize │
│  爬取   │    │  提取    │    │  整理    │    │  总结     │
└─────────┘    └──────────┘    └──────────┘    └───────────┘
     │               │               │               │
     ▼               ▼               ▼               ▼
data/raw/      data/extracted/  data/organized/  data/summary/
*.html          *.json           *.json           *.md
```

#### 输出示例

**数据概览**:
- 文章总数: 30
- 总热度: 2847
- 总评论数: 523
- 平均热度: 94.9

**热门话题**:
- 🔥 AI (12 篇文章, 总热度: 1250)
- 💻 Programming (8 篇文章, 总热度: 680)
- 🚀 Startup (5 篇文章, 总热度: 520)

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
