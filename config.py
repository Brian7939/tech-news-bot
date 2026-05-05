"""
新闻简报系统配置文件
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """系统配置类"""
    
    # Discord配置
    DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID', 0))
    DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
    
    # NewsAPI配置
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    
    # Tavily API配置
    TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
    
    # OpenAI配置（可选）
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    # DeepSeek API配置
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
    
    # 系统配置
    TIMEZONE = os.getenv('TIMEZONE', 'Asia/Shanghai')
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    
    # 新闻源配置
    NEWS_SOURCES = {
        'apple': {
            'newsapi_keywords': ['Apple', 'iPhone', 'iPad', 'Mac', 'iOS', 'macOS'],
            'rss_feeds': [
                'https://www.apple.com/newsroom/rss-feed.rss',
                'https://9to5mac.com/feed/',
                'https://www.macrumors.com/feed/',
                'https://appleinsider.com/rss/all'
            ],
            'search_keywords': ['Apple product', 'iPhone', 'iPad', 'MacBook', 'iOS', 'macOS']
        },
        'ai': {
            'newsapi_keywords': ['Artificial Intelligence', 'AI', 'Machine Learning', 'Deep Learning'],
            'rss_feeds': [
                'https://techcrunch.com/category/artificial-intelligence/feed/',
                'https://venturebeat.com/ai/feed/',
                'https://www.artificialintelligence-news.com/feed/',
                'https://www.theverge.com/ai-artificial-intelligence/rss/index.xml'
            ],
            'search_keywords': ['AI technology', 'artificial intelligence', 'machine learning', 'deep learning']
        },
        'llm': {
            'newsapi_keywords': ['Large Language Model', 'LLM', 'GPT', 'ChatGPT', 'Claude', 'Llama'],
            'rss_feeds': [
                'https://arxiv.org/list/cs.CL/recentrss',  # NLP/LLM论文
                'https://huggingface.co/blog/feed.xml',
                'https://openai.com/blog/rss.xml',
                'https://www.anthropic.com/news/rss'
            ],
            'search_keywords': ['large language model', 'LLM', 'local LLM', 'open source LLM', 'GPT', 'ChatGPT', 'Llama', 'Claude']
        }
    }
    
    # 新闻过滤配置
    FILTER_CONFIG = {
        'min_relevance_score': 0.6,  # 最低相关性分数
        'max_articles_per_category': 5,  # 每个分类最大文章数
        'exclude_keywords': ['advertisement', 'sponsored', 'press release template'],
        'required_languages': ['en', 'zh'],  # 支持的语言
        'hours_back': 24  # 获取过去24小时的新闻
    }
    
    # 消息格式配置
    MESSAGE_FORMAT = {
        'title': '🤖 科技新闻简报',
        'timezone': 'Asia/Shanghai',
        'max_summary_length': 200,  # 摘要最大字符数
        'include_emojis': True,
        'categories_order': ['apple', 'ai', 'llm']
    }
    
    # 调度配置
    SCHEDULE_CONFIG = {
        'daily_time': '12:00',  # 每天推送时间
        'timezone': 'Asia/Shanghai',
        'retry_attempts': 3,  # 失败重试次数
        'retry_delay': 300  # 重试延迟（秒）
    }

# 验证必要的配置
def validate_config():
    """验证必要的配置项"""
    required_configs = [
        ('DISCORD_BOT_TOKEN', Config.DISCORD_BOT_TOKEN),
        ('DISCORD_CHANNEL_ID', Config.DISCORD_CHANNEL_ID),
    ]
    
    missing_configs = []
    for name, value in required_configs:
        if not value:
            missing_configs.append(name)
    
    if missing_configs:
        print(f"❌ 缺少必要的配置项: {', '.join(missing_configs)}")
        print("请检查 .env 文件中的配置")
        return False
    
    return True

if __name__ == '__main__':
    if validate_config():
        print("✅ 配置验证通过")
    else:
        print("❌ 配置验证失败")
