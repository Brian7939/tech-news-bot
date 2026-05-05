"""
Discord机器人模块
用于发送科技新闻简报到Discord频道
"""

import discord
import asyncio
import logging
from datetime import datetime
from typing import List, Dict
from config import Config

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsDiscordBot:
    """新闻Discord机器人类"""
    
    def __init__(self):
        """初始化Discord机器人"""
        intents = discord.Intents.default()
        intents.message_content = True
        
        self.client = discord.Client(intents=intents)
        self.channel_id = Config.DISCORD_CHANNEL_ID
        
        # 设置事件处理器
        self.setup_events()
    
    def setup_events(self):
        """设置Discord事件处理器"""
        
        @self.client.event
        async def on_ready():
            """机器人启动事件"""
            logger.info(f'✅ 机器人已登录: {self.client.user}')
            logger.info(f'📱 目标频道ID: {self.channel_id}')
        
        @self.client.event
        async def on_message(message):
            """消息接收事件"""
            if message.author == self.client.user:
                return
            
            # 处理命令
            if message.content.startswith('!news'):
                await self.handle_news_command(message)
            elif message.content.startswith('!help'):
                await self.handle_help_command(message)
    
    async def handle_news_command(self, message):
        """处理新闻命令"""
        try:
            await message.channel.send('🔄 正在获取最新科技新闻...')
            # 这里会调用新闻聚合器
            from news_aggregator import NewsAggregator
            aggregator = NewsAggregator()
            news_digest = await aggregator.get_daily_digest()
            
            if news_digest:
                await self.send_news_digest(news_digest)
            else:
                await message.channel.send('❌ 今天没有找到相关新闻')
                
        except Exception as e:
            logger.error(f'处理新闻命令时出错: {e}')
            await message.channel.send('❌ 获取新闻时出现错误')
    
    async def handle_help_command(self, message):
        """处理帮助命令"""
        help_text = """
🤖 **科技新闻机器人帮助**

**可用命令:**
• `!news` - 获取最新科技新闻简报
• `!help` - 显示此帮助信息

**功能特点:**
• 🍎 苹果产品动态
• 🤖 AI技术发展
• 🧠 大语言模型动态
• ⏰ 每天中午12点自动推送

**反馈和建议:**
请联系管理员提出改进建议
        """
        await message.channel.send(help_text)
    
    async def send_news_digest(self, news_data: Dict):
        """发送新闻简报到Discord频道"""
        try:
            channel = self.client.get_channel(self.channel_id)
            if not channel:
                logger.error(f'找不到频道ID: {self.channel_id}')
                return False
            
            # 创建嵌入消息
            embed = self.create_news_embed(news_data)
            
            await channel.send(embed=embed)
            logger.info('✅ 新闻简报发送成功')
            return True
            
        except Exception as e:
            logger.error(f'发送新闻简报时出错: {e}')
            return False
    
    def create_news_embed(self, news_data: Dict) -> discord.Embed:
        """创建新闻嵌入消息"""
        embed = discord.Embed(
            title=news_data.get('title', '🤖 科技新闻简报'),
            description=news_data.get('description', '每日科技新闻汇总'),
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        # 添加分类新闻
        categories = news_data.get('categories', {})
        category_emojis = {
            'apple': '🍎',
            'ai': '🤖', 
            'llm': '🧠'
        }
        
        for category_name, articles in categories.items():
            if articles and category_name in category_emojis:
                emoji = category_emojis[category_name]
                field_name = f'{emoji} {self.get_category_display_name(category_name)}'
                
                # 格式化文章列表
                article_text = ''
                for i, article in enumerate(articles[:3], 1):  # 最多显示3篇
                    title = article.get('title', '无标题')
                    url = article.get('url', '')
                    summary = article.get('summary', '')[:100] + '...' if len(article.get('summary', '')) > 100 else article.get('summary', '')
                    
                    if url:
                        article_text += f'**{i}. [{title}]({url})**\n{summary}\n\n'
                    else:
                        article_text += f'**{i}. {title}**\n{summary}\n\n'
                
                if article_text:
                    embed.add_field(
                        name=field_name,
                        value=article_text[:1024],  # Discord字段限制
                        inline=False
                    )
        
        # 添加页脚
        embed.set_footer(text=f'📅 {datetime.now().strftime("%Y-%m-%d %H:%M")} | 🤖 科技新闻机器人')
        
        return embed
    
    def get_category_display_name(self, category: str) -> str:
        """获取分类显示名称"""
        display_names = {
            'apple': '苹果产品动态',
            'ai': 'AI技术发展',
            'llm': '大语言模型'
        }
        return display_names.get(category, category)
    
    async def start(self):
        """启动机器人"""
        try:
            if not Config.DISCORD_BOT_TOKEN:
                logger.error('❌ Discord机器人Token未配置')
                return False
            
            await self.client.start(Config.DISCORD_BOT_TOKEN)
            return True
            
        except Exception as e:
            logger.error(f'启动机器人时出错: {e}')
            return False
    
    async def stop(self):
        """停止机器人"""
        await self.client.close()
        logger.info('🛑 机器人已停止')

# 单例模式
bot_instance = None

def get_bot():
    """获取机器人实例"""
    global bot_instance
    if bot_instance is None:
        bot_instance = NewsDiscordBot()
    return bot_instance

async def send_daily_news_digest(news_data: Dict):
    """发送每日新闻简报（供调度器调用）"""
    bot = get_bot()
    return await bot.send_news_digest(news_data)

if __name__ == '__main__':
    # 测试运行
    bot = get_bot()
    asyncio.run(bot.start())
