"""
测试Discord Webhook功能
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from discord_webhook import get_webhook
from config import Config

async def test_webhook():
    """测试Webhook功能"""
    print("🧪 开始测试Discord Webhook...")
    
    if not Config.DISCORD_WEBHOOK_URL:
        print("❌ Discord Webhook URL未配置")
        return False
    
    webhook = get_webhook(Config.DISCORD_WEBHOOK_URL)
    
    # 测试消息
    test_data = {
        'title': '🧪 测试消息',
        'description': '这是一条测试消息，用于验证Discord Webhook是否正常工作',
        'categories': {
            'apple': [
                {
                    'title': '测试苹果新闻',
                    'url': 'https://example.com/apple',
                    'summary': '这是一条测试的苹果新闻摘要',
                    'relevance_score': 1.0
                }
            ],
            'ai': [
                {
                    'title': '测试AI新闻',
                    'url': 'https://example.com/ai',
                    'summary': '这是一条测试的AI新闻摘要',
                    'relevance_score': 0.9
                }
            ]
        }
    }
    
    try:
        success = await webhook.send_news_digest(test_data)
        
        if success:
            print("✅ Webhook测试成功！")
            print("📱 请检查您的Discord频道是否收到测试消息")
            return True
        else:
            print("❌ Webhook测试失败")
            return False
            
    except Exception as e:
        print(f"❌ Webhook测试异常: {e}")
        return False

if __name__ == '__main__':
    asyncio.run(test_webhook())
