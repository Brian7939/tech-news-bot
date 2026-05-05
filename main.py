"""
科技新闻简报系统主程序
整合所有模块，提供完整的新闻推送服务
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime
from typing import Optional
from config import Config, validate_config
from scheduler import start_scheduler, stop_scheduler, get_scheduler
from discord_bot import start_bot, stop_bot
from health_server import start_health_server
from news_aggregator import NewsAggregator
from news_formatter import get_formatter

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class NewsBotSystem:
    """新闻机器人系统主类"""
    
    def __init__(self):
        """初始化系统"""
        self.is_running = False
        self.discord_bot = None
        self.scheduler = None
        
        # 验证配置
        if not validate_config():
            logger.error('❌ 配置验证失败，系统无法启动')
            sys.exit(1)
        
        logger.info('✅ 配置验证通过')
    
    async def start(self):
        """启动系统"""
        if self.is_running:
            logger.warning('⚠️ 系统已经在运行')
            return
        
        try:
            await start_system()
            self.is_running = True
            logger.info('✅ 系统启动完成')
            
            # 显示系统状态
            await self.show_system_status()
            
        except Exception as e:
            logger.error(f'❌ 系统启动失败: {e}')
            await self.stop()
            sys.exit(1)
    
    async def _start_discord_bot(self):
        """启动Discord机器人"""
        try:
            await self.discord_bot.start()
        except Exception as e:
            logger.error(f'Discord机器人启动失败: {e}')
            raise
    
    async def stop(self):
        """停止系统"""
        if not self.is_running:
            return
        
        logger.info('🛑 正在停止科技新闻简报系统')
        
        try:
            # 停止调度器
            if self.scheduler:
                stop_scheduler()
                logger.info('✅ 调度器已停止')
            
            # 停止Discord机器人
            if self.discord_bot:
                await self.discord_bot.stop()
                logger.info('✅ Discord机器人已停止')
            
            self.is_running = False
            logger.info('✅ 系统已完全停止')
            
        except Exception as e:
            logger.error(f'❌ 系统停止时出错: {e}')
    
    async def show_system_status(self):
        """显示系统状态"""
        try:
            # 调度器状态
            scheduler_status = self.scheduler.get_status() if self.scheduler else {}
            
            # Discord机器人状态
            discord_status = {
                'connected': self.discord_bot.client.is_ready() if self.discord_bot else False,
                'channel_id': Config.DISCORD_CHANNEL_ID
            }
            
            # 新闻源状态
            aggregator = NewsAggregator()
            news_sources_count = len(aggregator.news_sources)
            
            print('\n' + '='*50)
            print('🤖 科技新闻简报系统状态')
            print('='*50)
            print(f'📅 调度器状态: {"运行中" if scheduler_status.get("is_running") else "已停止"}')
            print(f'⏰ 每日推送时间: {scheduler_status.get("daily_time", "N/A")}')
            print(f'🌍 时区: {scheduler_status.get("timezone", "N/A")}')
            print(f'📱 Discord机器人: {"已连接" if discord_status.get("connected") else "未连接"}')
            print(f'💬 目标频道ID: {discord_status.get("channel_id", "N/A")}')
            print(f'📡 新闻源数量: {news_sources_count}')
            
            if scheduler_status.get("next_run"):
                print(f'⏱️ 下次推送: {scheduler_status["next_run"]}')
            
            print('='*50)
            
        except Exception as e:
            logger.error(f'显示系统状态时出错: {e}')
    
    async def test_news_fetch(self):
        """测试新闻获取功能"""
        logger.info('🧪 开始测试新闻获取功能')
        
        try:
            aggregator = NewsAggregator()
            formatter = get_formatter()
            
            # 获取新闻
            news_digest = await aggregator.get_daily_digest()
            
            if news_digest:
                # 格式化新闻
                formatted_news = formatter.format_news_digest(news_digest)
                
                print('\n📰 测试新闻简报:')
                print(f'标题: {formatted_news["title"]}')
                print(f'摘要: {formatted_news["summary"]}')
                print(f'时间: {formatted_news["timestamp"]}')
                
                for category, articles in formatted_news['categories'].items():
                    print(f'\n{category.upper()}:')
                    for i, article in enumerate(articles[:2], 1):
                        print(f'  {i}. {article["title"]}')
                        print(f'     {article["summary"][:100]}...')
                
                logger.info('✅ 新闻获取测试成功')
                return True
            else:
                logger.warning('⚠️ 没有获取到新闻')
                return False
                
        except Exception as e:
            logger.error(f'❌ 新闻获取测试失败: {e}')
            return False
    
    async def send_test_message(self):
        """发送测试消息到Discord"""
        logger.info('🧪 发送测试消息到Discord')
        
        try:
            test_data = {
                'title': '🧪 测试消息',
                'description': '这是一条测试消息，用于验证Discord机器人是否正常工作',
                'timestamp': asyncio.get_event_loop().time(),
                'categories': {
                    'apple': [
                        {
                            'title': '测试苹果新闻',
                            'url': 'https://example.com',
                            'summary': '这是一条测试的苹果新闻',
                            'source': '测试源',
                            'published_date': None,
                            'relevance_score': 1.0
                        }
                    ]
                }
            }
            
            success = await self.discord_bot.send_news_digest(test_data)
            
            if success:
                logger.info('✅ 测试消息发送成功')
            else:
                logger.error('❌ 测试消息发送失败')
            
            return success
            
        except Exception as e:
            logger.error(f'❌ 发送测试消息时出错: {e}')
            return False

# 全局系统实例
system_instance = None

def get_system():
    """获取系统实例"""
    global system_instance
    if system_instance is None:
        system_instance = NewsBotSystem()
    return system_instance

async def main():
    """主函数"""
    system = get_system()
    
    # 设置信号处理器
    def signal_handler(sig, frame):
        logger.info('🛑 收到停止信号，正在关闭系统...')
        asyncio.create_task(system.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'test':
            logger.info('🧪 运行测试模式')
            await system.test_news_fetch()
            await system.send_test_message()
            return
        elif command == 'status':
            await system.show_system_status()
            return
        elif command == 'help':
            print_help()
            return
    
    # 启动系统
    await system.start()

def print_help():
    """显示帮助信息"""
    print('🤖 科技新闻简报系统')
    print('')
    print('用法:')
    print('  python main.py           - 启动系统')
    print('  python main.py test      - 运行测试')
    print('  python main.py status    - 显示系统状态')
    print('  python main.py help      - 显示帮助信息')
    print('')
    print('功能:')
    print('• 🍎 苹果产品动态')
    print('• 🤖 AI技术发展')
    print('• 🧠 大语言模型动态')
    print('• ⏰ 每天中午12点自动推送')
    print('• 💬 Discord机器人推送')

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n👋 再见！')
    except Exception as e:
        logger.error(f'❌ 程序异常退出: {e}')
        sys.exit(1)
