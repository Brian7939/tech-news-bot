"""
Discord Webhook模块
使用Discord Webhook发送新闻简报，无需额外的机器人
"""

import requests
import logging
from datetime import datetime
from typing import Dict, Optional
import json
from config import Config

logger = logging.getLogger(__name__)

class DiscordWebhook:
    """Discord Webhook发送器"""
    
    def __init__(self, webhook_url: str):
        """初始化Webhook"""
        self.webhook_url = webhook_url
        self.session = requests.Session()
    
    async def send_news_digest(self, news_data: Dict) -> bool:
        """通过Webhook发送新闻简报"""
        try:
            # 创建嵌入消息
            embed = self.create_news_embed(news_data)
            
            # Webhook payload（添加thread_name支持论坛频道）
            payload = {
                "username": "科技新闻机器人",
                "avatar_url": "https://via.placeholder.com/96/00ff00/000000?text=🤖",
                "embeds": [embed],
                "thread_name": f"科技新闻简报 - {datetime.now().strftime('%m-%d %H:%M')}"
            }
            
            response = self.session.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            response.raise_for_status()
            logger.info('✅ 新闻简报通过Webhook发送成功')
            return True
            
        except Exception as e:
            logger.error(f'❌ Webhook发送失败: {e}')
            return False
    
    def create_news_embed(self, news_data: Dict) -> Dict:
        """创建Discord嵌入消息"""
        embed = {
            "title": news_data.get('title', '🤖 科技新闻简报'),
            "description": news_data.get('description', '每日科技新闻汇总'),
            "color": 5814783,  # 蓝色
            "timestamp": datetime.now().isoformat(),
            "footer": {
                "text": "🤖 由科技新闻机器人自动推送"
            }
        }
        
        # 添加分类新闻
        categories = news_data.get('categories', {})
        category_emojis = {
            'apple': '🍎',
            'ai': '🤖', 
            'llm': '🧠'
        }
        
        category_names = {
            'apple': '苹果产品动态',
            'ai': 'AI技术发展',
            'llm': '大语言模型'
        }
        
        fields = []
        
        for category_name, articles in categories.items():
            if articles and category_name in category_emojis:
                emoji = category_emojis[category_name]
                display_name = category_names.get(category_name, category_name.title())
                
                # 格式化文章列表
                article_text = ''
                for i, article in enumerate(articles[:3], 1):  # 最多显示3篇
                    title = article.get('translated_title', article.get('title', '无标题'))
                    url = article.get('url', '')
                    summary = article.get('detailed_summary', article.get('translated_summary', article.get('summary', '')))
                    
                    # 限制摘要长度
                    if len(summary) > 300:
                        summary = summary[:300] + '...'
                    
                    if url:
                        article_text += f'**{i}. [{title}]({url})**\n{summary}\n\n'
                    else:
                        article_text += f'**{i}. {title}**\n{summary}\n\n'
                
                if article_text:
                    fields.append({
                        "name": f'{emoji} {display_name}',
                        "value": article_text[:1024],  # Discord字段限制
                        "inline": False
                    })
        
        embed["fields"] = fields
        return embed
    
    async def send_test_message(self) -> bool:
        """发送测试消息"""
        test_data = {
            'title': '🧪 测试消息',
            'description': '这是一条测试消息，用于验证Webhook是否正常工作',
            'categories': {
                'apple': [
                    {
                        'title': '测试苹果新闻',
                        'url': 'https://example.com',
                        'summary': '这是一条测试的苹果新闻',
                        'relevance_score': 1.0
                    }
                ]
            }
        }
        
        return await self.send_news_digest(test_data)

# 全局Webhook实例
webhook_instance = None

def get_webhook(webhook_url: str):
    """获取Webhook实例"""
    global webhook_instance
    if webhook_instance is None:
        webhook_instance = DiscordWebhook(webhook_url)
    return webhook_instance

async def send_daily_news_digest_via_webhook(webhook_url: str, news_data: Dict) -> bool:
    """通过Webhook发送每日新闻简报（供调度器调用）"""
    webhook = get_webhook(webhook_url)
    return await webhook.send_news_digest(news_data)

if __name__ == '__main__':
    # 测试Webhook
    import asyncio
    
    async def test_webhook():
        # 请替换为实际的Webhook URL
        webhook_url = "YOUR_WEBHOOK_URL_HERE"
        
        webhook = get_webhook(webhook_url)
        success = await webhook.send_test_message()
        
        if success:
            print("✅ Webhook测试成功")
        else:
            print("❌ Webhook测试失败")
    
    # asyncio.run(test_webhook())
    print("请设置Webhook URL后运行测试")
