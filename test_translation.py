"""
测试翻译功能的新闻简报
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from news_aggregator import NewsAggregator
from discord_webhook import get_webhook
from config import Config

async def test_translation_news():
    print('🔄 测试带翻译功能的新闻简报...')
    
    try:
        # 获取新闻
        aggregator = NewsAggregator()
        news_digest = await aggregator.get_daily_digest()
        
        if news_digest and news_digest.get('categories'):
            print(f'✅ 获取到新闻简报，包含 {len(news_digest["categories"])} 个分类')
            
            # 显示翻译后的新闻内容
            for category, articles in news_digest['categories'].items():
                print(f'\n📂 {category.upper()}: {len(articles)} 条新闻')
                for i, article in enumerate(articles, 1):
                    print(f'  {i}. 标题: {article.get("translated_title", article.get("title", "无标题"))}')
                    print(f'     摘要: {article.get("detailed_summary", article.get("translated_summary", article.get("summary", "")))[:150]}...')
                    print(f'     来源: {article["source"]}')
                    print(f'     相关性: {article["relevance_score"]:.2f}')
            
            # 发送到Discord
            if Config.DISCORD_WEBHOOK_URL:
                webhook = get_webhook(Config.DISCORD_WEBHOOK_URL)
                success = await webhook.send_news_digest(news_digest)
                
                if success:
                    print('\n✅ 翻译版新闻简报发送成功！')
                else:
                    print('\n❌ 新闻简报发送失败')
            else:
                print('\n⚠️ Discord Webhook URL未配置，跳过发送')
        else:
            print('⚠️ 没有获取到相关新闻')
            
    except Exception as e:
        print(f'❌ 执行新闻简报任务时出错: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_translation_news())
