# 🚀 Telegram Finance Express

Telegram Finance Express 是一个自动化财经新闻聚合与管理平台。它能实时从 Telegram 财经频道抓取新闻，通过智能去重、自动打标处理数据，并通过内置的 Web 面板提供搜索、筛选和可视化展示。

## 📋 功能特点

* **智能聚合**：自动监听 Telegram 频道，实时获取财经动态。
* **三层智能去重**：基于消息 ID、内容 Hash 及相似度计算，有效过滤重复资讯。
* **自动分类标签**：内置财经词典，自动为每条新闻提取“股票”、“基金”、“宏观”等标签。
* **可视化管理面板**：简洁的前端界面，支持全文搜索、多标签筛选、日期范围查看。
* **自动化维护**：内置定时任务，自动清理 7 天前旧数据，支持数据库备份。
* **生产就绪**：支持 Supervisor 进程管理与 Nginx 反向代理配置。

---

## 🛠️ 快速开始

### 1. 环境准备
确保已安装 Python 3.8+，并执行以下命令安装依赖：
```bash
pip install -r requirements.txt
```
2. 配置环境
创建 .env 文件并将你的 Telegram Bot Token 填入：
```bash
echo "TELEGRAM_BOT_TOKEN=your_bot_token_here" > .env
```
3. 运行程序
```bash
python main.py
```bash
程序启动后，Telegram 机器人将开始监听，同时在 http://localhost:5000 启动管理面板。
# 📂 项目结构
telegram_finance/
├── main.py              # 主程序入口
├── config.py            # 配置管理
├── database.py          # SQLite 数据库操作封装
├── deduplicator.py      # 智能去重算法模块
├── tagger.py            # 中文财经标签提取模块
├── telegram_bot.py      # Telegram 爬虫机器人逻辑
├── requirements.txt     # 依赖清单
├── .env                 # 环境变量配置
├── web/                 # Flask 后端与模板
└── finance_data.db      # 自动生成的数据库（SQLite）
```bash
## ⚙️ 自定义配置

你可以通过修改 `config.py` 文件来调整系统的核心运行参数：

* **`SIMILARITY_THRESHOLD`**: 去重相似度阈值（建议设置为 `0.75`，数值越高去重越严格）。
* **`DATA_RETENTION_DAYS`**: 数据保留天数（默认 `7` 天，超过期限的数据将自动清理）。
* **`MIN_CONTENT_LENGTH`**: 最小内容长度限制（过滤掉过短的无意义消息）。

---

## 🌐 API 文档摘要

系统内置了简洁的 RESTful API，方便你进行二次开发或对接前端：

| 接口路径 | 请求方法 | 功能描述 |
| :--- | :--- | :--- |
| `/api/news` | `GET` | 获取分页新闻列表 |
| `/api/search` | `GET` | 按关键词搜索新闻 |
| `/api/news/by-tag` | `GET` | 按标签筛选新闻 |
| `/api/filter` | `GET` | 多条件（时间/标签）组合筛选 |
| `/api/tags` | `GET` | 获取当前所有可用标签列表 |
| `/api/stats` | `GET` | 获取数据库总数与统计看板信息 |
| `/api/cleanup` | `POST` | 手动触发过期数据清理 |

# ⚖️ 许可证
本项目基于 MIT License 开源。
