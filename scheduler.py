"""
任务调度模块
负责定时执行新闻聚合和推送任务
"""

import asyncio
import schedule
import time
import logging
from datetime import datetime, timedelta
from typing import Optional
import threading
from config import Config
from news_aggregator import NewsAggregator
from discord_bot import send_daily_news_digest

logger = logging.getLogger(__name__)

class NewsScheduler:
    """新闻任务调度器"""
    
    def __init__(self):
        """初始化调度器"""
        self.aggregator = NewsAggregator()
        self.is_running = False
        self.scheduler_thread = None
        
        # 调度配置
        self.daily_time = Config.SCHEDULE_CONFIG['daily_time']
        self.timezone = Config.SCHEDULE_CONFIG['timezone']
        self.retry_attempts = Config.SCHEDULE_CONFIG['retry_attempts']
        self.retry_delay = Config.SCHEDULE_CONFIG['retry_delay']
    
    def start(self):
        """启动调度器"""
        if self.is_running:
            logger.warning('⚠️ 调度器已经在运行')
            return
        
        self.is_running = True
        
        # 设置每日定时任务
        schedule.every().day.at(self.daily_time).do(self.run_daily_news_task)
        
        # 启动调度器线程
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info(f'✅ 新闻调度器已启动，每天 {self.daily_time} 推送新闻')
        logger.info(f'🌍 时区: {self.timezone}')
    
    def stop(self):
        """停止调度器"""
        self.is_running = False
        schedule.clear()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        logger.info('🛑 新闻调度器已停止')
    
    def _run_scheduler(self):
        """运行调度器循环"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
            except Exception as e:
                logger.error(f'调度器运行时出错: {e}')
                time.sleep(60)
    
    def run_daily_news_task(self):
        """执行每日新闻任务"""
        logger.info('📅 开始执行每日新闻任务')
        
        # 在新的事件循环中运行异步任务
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            success = loop.run_until_complete(self._send_daily_news_with_retry())
            if success:
                logger.info('✅ 每日新闻任务执行成功')
            else:
                logger.error('❌ 每日新闻任务执行失败')
        except Exception as e:
            logger.error(f'每日新闻任务执行异常: {e}')
        finally:
            loop.close()
    
    async def _send_daily_news_with_retry(self) -> bool:
        """带重试机制的发送新闻"""
        for attempt in range(self.retry_attempts):
            try:
                logger.info(f'🔄 尝试发送新闻简报 (第 {attempt + 1} 次)')
                
                # 获取新闻简报
                news_digest = await self.aggregator.get_daily_digest()
                
                if not news_digest or not news_digest.get('categories'):
                    logger.warning('⚠️ 没有找到相关新闻')
                    return True  # 没有新闻也算成功
                
                # 发送到Discord
                success = await send_daily_news_digest(news_digest)
                
                if success:
                    logger.info('✅ 新闻简报发送成功')
                    return True
                else:
                    logger.error(f'❌ 新闻简报发送失败 (第 {attempt + 1} 次)')
                    
            except Exception as e:
                logger.error(f'发送新闻简报时出错 (第 {attempt + 1} 次): {e}')
            
            # 如果不是最后一次尝试，等待重试
            if attempt < self.retry_attempts - 1:
                logger.info(f'⏳ 等待 {self.retry_delay} 秒后重试...')
                await asyncio.sleep(self.retry_delay)
        
        logger.error('❌ 所有重试都失败了')
        return False
    
    def add_test_task(self, delay_minutes: int = 1):
        """添加测试任务（用于调试）"""
        run_time = (datetime.now() + timedelta(minutes=delay_minutes)).strftime('%H:%M')
        schedule.every().day.at(run_time).do(self.run_daily_news_task)
        logger.info(f'🧪 已添加测试任务，将在 {run_time} 执行')
    
    def get_next_run_time(self) -> Optional[datetime]:
        """获取下次运行时间"""
        jobs = schedule.jobs
        if not jobs:
            return None
        
        next_job = min(jobs, key=lambda job: job.next_run)
        return next_job.next_run
    
    def get_status(self) -> dict:
        """获取调度器状态"""
        return {
            'is_running': self.is_running,
            'daily_time': self.daily_time,
            'timezone': self.timezone,
            'next_run': self.get_next_run_time().isoformat() if self.get_next_run_time() else None,
            'total_jobs': len(schedule.jobs)
        }

# 全局调度器实例
scheduler_instance = None

def get_scheduler():
    """获取调度器实例"""
    global scheduler_instance
    if scheduler_instance is None:
        scheduler_instance = NewsScheduler()
    return scheduler_instance

def start_scheduler():
    """启动调度器"""
    scheduler = get_scheduler()
    scheduler.start()

def stop_scheduler():
    """停止调度器"""
    scheduler = get_scheduler()
    scheduler.stop()

if __name__ == '__main__':
    # 测试调度器
    import signal
    import sys
    
    def signal_handler(sig, frame):
        print('\n🛑 正在停止调度器...')
        stop_scheduler()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    print('🚀 启动新闻调度器...')
    start_scheduler()
    
    # 添加测试任务（1分钟后执行）
    scheduler = get_scheduler()
    scheduler.add_test_task(1)
    
    print('⏰ 调度器正在运行，按 Ctrl+C 停止')
    
    try:
        while True:
            time.sleep(60)
            # 显示状态
            status = scheduler.get_status()
            print(f"📊 状态: 运行中={status['is_running']}, 下次运行={status['next_run']}")
    except KeyboardInterrupt:
        pass
