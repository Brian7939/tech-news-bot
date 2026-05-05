# 科技新闻简报系统

一个自动化的科技新闻聚合和Discord推送系统，每天中午12点发送过去24小时的科技新闻简报。

## 功能特点

- 🍎 **苹果产品动态**: 跟踪苹果公司最新产品发布、更新和新闻
- 🤖 **AI技术发展**: 聚合人工智能领域的最新进展
- 🧠 **大语言模型**: 特别关注本地模型和开源LLM动态
- ⏰ **定时推送**: 每天中午12点自动发送到Discord频道
- 📱 **Discord集成**: 通过Discord机器人推送格式化的新闻简报

## 系统架构

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   新闻API源     │    │   新闻聚合器     │    │   Discord机器人 │
│                 │    │                  │    │                 │
│ • NewsAPI       │───▶│ • 过滤和分类     │───▶│ • 格式化消息     │
│ • RSS源         │    │ • 去重和排序     │    │ • 定时发送       │
│ • 科技网站      │    │ • 摘要生成       │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   调度系统       │
                       │                  │
                       │ • Cron定时任务   │
                       │ • 错误处理       │
                       │ • 日志记录       │
                       └──────────────────┘
```

## 技术栈

- **Python 3.9+**: 主要编程语言
- **discord.py**: Discord机器人框架
- **requests**: HTTP请求库
- **feedparser**: RSS解析
- **schedule**: 任务调度
- **beautifulsoup4**: 网页内容解析
- **openai**: 新闻摘要生成（可选）

## 安装和配置

1. 克隆项目
```bash
git clone <repository-url>
cd tech-news-discord-bot
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入必要的API密钥
```

4. 运行系统
```bash
python main.py
```

## 配置说明

### Discord机器人配置
1. 在Discord Developer Portal创建应用
2. 创建机器人并获取Token
3. 将机器人邀请到服务器
4. 获取频道ID

### 新闻API配置
- NewsAPI: 注册获取API密钥
- RSS源: 配置关注的科技网站RSS地址
- 其他API: 根据需要配置

## 使用方法

系统会自动在每天中午12点推送新闻简报。也可以手动触发：

```python
from news_bot import NewsBot
bot = NewsBot()
await bot.send_daily_digest()
```

## 自定义配置

可以在 `config.py` 中修改：
- 新闻源配置
- 过滤关键词
- 推送时间
- 消息格式

## 许可证

MIT License
