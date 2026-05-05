"""
简单的健康检查服务器
用于Docker健康检查
"""

import asyncio
import logging
from aiohttp import web
import json

logger = logging.getLogger(__name__)

class HealthServer:
    """健康检查服务器"""
    
    def __init__(self):
        self.app = web.Application()
        self.setup_routes()
    
    def setup_routes(self):
        """设置路由"""
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_get('/', self.root)
    
    async def health_check(self, request):
        """健康检查端点"""
        try:
            # 检查关键组件状态
            from config import Config
            
            status = {
                'status': 'healthy',
                'timestamp': '2026-05-05T18:23:00Z',
                'version': '1.0.0',
                'services': {
                    'discord_webhook': bool(Config.DISCORD_WEBHOOK_URL),
                    'news_api': bool(Config.NEWS_API_KEY),
                    'tavily_api': bool(Config.TAVILY_API_KEY),
                    'deepseek_api': bool(Config.DEEPSEEK_API_KEY)
                }
            }
            
            return web.json_response(status, status=200)
            
        except Exception as e:
            logger.error(f'健康检查失败: {e}')
            return web.json_response(
                {'status': 'unhealthy', 'error': str(e)}, 
                status=503
            )
    
    async def root(self, request):
        """根路径"""
        return web.json_response({
            'service': 'Tech News Bot',
            'status': 'running',
            'endpoints': {
                'health': '/health',
                'info': '/'
            }
        })
    
    async def start_server(self, port=8000):
        """启动服务器"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        
        logger.info(f'🏥 健康检查服务器启动在端口 {port}')
        return runner

# 全局实例
health_server = None

async def start_health_server(port=8000):
    """启动健康检查服务器"""
    global health_server
    if health_server is None:
        health_server = HealthServer()
    return await health_server.start_server(port)

if __name__ == '__main__':
    async def main():
        server = await start_health_server()
        try:
            # 保持服务器运行
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info('🛑 停止健康检查服务器')
            await server.cleanup()
    
    asyncio.run(main())
