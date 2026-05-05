"""
科技新闻简报系统主程序
"""
 
import asyncio
import logging
import signal
import sys
 
# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
 
logger = logging.getLogger(__name__)
 
from config import Config, validate_config
from scheduler import start_scheduler, stop_scheduler, get_scheduler
from health_server import start_health_server
from discord_webhook import DiscordWebhook
 
class NewsBot:
    """新闻机器人主类"""
    
    def __init__(self):
        self.scheduler = None
        self.webhook = DiscordWebhook(Config.DISCORD_WEBHOOK_URL)
        self.running = False
    
    async def start(self):
        """启动机器人"""
        try:
            logger.info('🚀 启动科技新闻简报系统...')
            
            # 启动健康检查服务器
            await start_health_server()
            
            # 启动调度器
            self.scheduler = start_scheduler()
            
            self.running = True
            logger.info('✅ 科技新闻简报系统启动成功')
            
            # 保持运行
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f'❌ 系统启动失败: {e}')
            raise
    
    async def stop(self):
        """停止机器人"""
        try:
            logger.info('🛑 正在停止科技新闻简报系统...')
            
            self.running = False
            
            # 停止调度器
            if self.scheduler:
                stop_scheduler()
            
            logger.info('✅ 科技新闻简报系统已停止')
            
        except Exception as e:
            logger.error(f'❌ 系统停止失败: {e}')
    
    async def test_news(self):
        """测试新闻功能"""
        try:
            logger.info('🧪 测试新闻功能...')
            
            from news_aggregator import NewsAggregator
            aggregator = NewsAggregator()
            
            # 获取新闻简报
            news_digest = await aggregator.get_daily_digest()
            
            if news_digest and news_digest.get('categories'):
                logger.info('✅ 新闻获取成功')
                
                # 发送到Discord
                success = await self.webhook.send_news_digest(news_digest)
                
                if success:
                    logger.info('✅ 测试推送完成')
                else:
                    logger.error('❌ 测试推送失败')
            else:
                logger.warning('⚠️ 没有获取到相关新闻')
                
        except Exception as e:
            logger.error(f'❌ 测试失败: {e}')
 
# 全局机器人实例
bot = None
 
def signal_handler(signum, frame):
    """信号处理器"""
    logger.info(f'收到信号 {signum}，正在停止服务...')
    if bot:
        asyncio.create_task(bot.stop())
 
async def main():
    """主函数"""
    global bot
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 创建机器人实例
    bot = NewsBot()
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            await bot.test_news()
        else:
            logger.error(f'未知参数: {sys.argv[1]}')
    else:
        # 启动系统
        await bot.start()
 
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('👋 用户中断，正在退出...')
    except Exception as e:
        logger.error(f'❌ 系统异常: {e}')
        sys.exit(1)
