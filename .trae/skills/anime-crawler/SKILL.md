---
name: "anime-crawler"
description: "爬取多个动漫资讯网站和新番信息，执行爬取->提取->整理->整合流程。Invoke when user wants to crawl anime news and seasonal anime information."
---

# 动漫资讯爬虫 Skill

本 Skill 用于爬取多个动漫资讯网站和新番信息，执行完整的处理流程，将原始数据转化为结构化的动漫资讯报告。

## 支持的网站

### 资讯网站
- **梦域动漫**: https://www.moelove.cn/
- **AniFun**: https://anifun.cn/ (可能需要特殊处理)
- **HotACG**: https://www.hotacg.com/

### 新番信息
- **長門番堂**: https://yuc.wiki/ (新番播送信息)

## 工作流程

整个处理流程分为四个阶段：

```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌───────────┐
│  Crawl  │ -> │ Extract  │ -> │ Organize │ -> │ Integrate │
│  爬取   │    │  提取    │    │  整理    │    │  整合     │
└─────────┘    └──────────┘    └──────────┘    └───────────┘
```

### 1. Crawl（爬取）
- **脚本**: `scripts/crawl.py`
- **功能**: 爬取多个动漫网站的原始 HTML 内容
- **输出**: `data/raw/` 目录下的 HTML 文件

### 2. Extract（提取）
- **脚本**: `scripts/extract.py`
- **功能**: 解析 HTML，提取文章标题、链接、发布时间等信息
- **输出**: `data/extracted/` 目录下的 JSON 文件

### 3. Organize（整理）
- **脚本**: `scripts/organize.py`
- **功能**: 对提取的数据进行清洗、去重、分类和格式化
- **输出**: `data/organized/` 目录下的 JSON 文件

### 4. Integrate（整合）
- **脚本**: `scripts/integrate.py`
- **功能**: 整合所有来源的信息，生成综合报告
- **输出**: `data/integrated/` 目录下的 Markdown 报告

## 快速开始

### 安装依赖

```bash
cd .trae/skills/anime-crawler/scripts
pip install -r requirements.txt
```

### 运行完整流程

```bash
# 方法1：逐个执行
python scripts/crawl.py
python scripts/extract.py
python scripts/organize.py
python scripts/integrate.py

# 方法2：一键执行完整流程
python scripts/run_pipeline.py
```

## 目录结构

```
.trae/skills/anime-crawler/
├── SKILL.md                    # 本文件
├── scripts/
│   ├── requirements.txt        # Python 依赖
│   ├── crawl.py               # 爬取脚本
│   ├── extract.py             # 提取脚本
│   ├── organize.py            # 整理脚本
│   ├── integrate.py           # 整合脚本
│   └── run_pipeline.py        # 一键运行完整流程
└── data/                      # 数据输出目录（自动创建）
    ├── raw/                   # 原始 HTML
    ├── extracted/             # 提取的 JSON 数据
    ├── organized/             # 整理后的数据
    └── integrated/            # 整合报告
```

## 数据格式

### 提取后的文章格式 (JSON)

```json
{
  "articles": [
    {
      "title": "文章标题",
      "url": "https://example.com/article",
      "summary": "文章摘要",
      "published_at": "2024-01-15T10:30:00",
      "source": "moelove.cn",
      "category": "资讯",
      "read_count": 1000
    }
  ],
  "metadata": {
    "crawled_at": "2024-01-15T12:00:00",
    "total_count": 30,
    "source": "moelove.cn"
  }
}
```

### 新番信息格式 (JSON)

```json
{
  "anime_list": [
    {
      "title": "动画标题",
      "url": "https://yuc.wiki/xxx",
      "air_time": "2024-07-01",
      "broadcast_time": "每周一 23:30",
      "status": "即将开播",
      "season": "2024年7月"
    }
  ],
  "metadata": {
    "crawled_at": "2024-01-15T12:00:00",
    "total_count": 50,
    "source": "yuc.wiki"
  }
}
```

## 配置选项

各脚本支持以下环境变量或命令行参数：

- `WEBSITES`: 要爬取的网站列表（逗号分隔，默认全部）
- `OUTPUT_DIR`: 输出目录（默认: data/）
- `TIMEOUT`: 请求超时时间（默认: 30秒）
- `MAX_RETRIES`: 最大重试次数（默认: 3）

## 注意事项

1. 请遵守各网站的 robots.txt 和爬虫协议
2. 建议设置适当的请求间隔，避免对服务器造成压力
3. 爬取的数据仅供个人学习研究使用
