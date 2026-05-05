"""
交互式新闻模块
提供新闻深入分析的交互功能
"""

import asyncio
import logging
import json
from typing import Dict, Optional
from datetime import datetime
from news_analyzer import get_news_analyzer
from discord_webhook import get_webhook
from config import Config

logger = logging.getLogger(__name__)

class InteractiveNews:
    """交互式新闻系统"""
    
    def __init__(self):
        """初始化交互系统"""
        self.analyzer = get_news_analyzer()
        self.webhook_url = Config.DISCORD_WEBHOOK_URL
        self.pending_analyses = {}  # 存储待分析的新闻
    
    async def create_forum_post(self, news_data: Dict) -> Optional[str]:
        """创建论坛帖子（模拟）"""
        """实际使用时，这需要通过Discord API创建论坛话题"""
        try:
            # 这里应该调用Discord API创建论坛话题
            # 由于Webhook限制，我们返回一个模拟的帖子ID
            post_id = f"news_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 存储新闻数据
            self.pending_analyses[post_id] = news_data
            
            logger.info(f'📝 创建论坛帖子: {post_id}')
            return post_id
            
        except Exception as e:
            logger.error(f'❌ 创建论坛帖子失败: {e}')
            return None
    
    async def send_news_with_interaction(self, news_data: Dict) -> bool:
        """发送带交互功能的新闻"""
        try:
            # 创建基础新闻消息
            webhook = get_webhook(self.webhook_url)
            
            # 为每个新闻添加交互按钮（通过反应）
            await self.send_news_with_reactions(news_data)
            
            return True
            
        except Exception as e:
            logger.error(f'❌ 发送交互式新闻失败: {e}')
            return False
    
    async def send_news_with_reactions(self, news_data: Dict):
        """发送带反应的新闻消息"""
        """由于Webhook限制，我们使用特殊格式的消息来模拟交互"""
        
        categories = news_data.get('categories', {})
        
        for category, articles in categories.items():
            if not articles:
                continue
            
            # 发送分类标题
            category_emojis = {
                'apple': '🍎',
                'ai': '🤖',
                'llm': '🧠'
            }
            
            emoji = category_emojis.get(category, '📰')
            category_names = {
                'apple': '苹果产品动态',
                'ai': 'AI技术发展',
                'llm': '大语言模型'
            }
            
            category_name = category_names.get(category, category.title())
            
            # 发送分类消息
            await self.send_category_message(emoji, category_name, articles)
    
    async def send_category_message(self, emoji: str, category_name: str, articles: list):
        """发送分类消息"""
        webhook = get_webhook(self.webhook_url)
        
        for i, article in enumerate(articles, 1):
            title = article.get('title', '')
            url = article.get('url', '')
            summary = article.get('summary', '')[:150] + '...' if len(article.get('summary', '')) > 150 else article.get('summary', '')
            
            # 创建带交互提示的消息
            message_content = f"""
{emoji} **{category_name} - 第{i}条**

**标题**: {title}
**链接**: {url}
**摘要**: {summary}

---
💡 **想要深入分析这条新闻？**
回复 `分析{i}` 或 `analyze{i}` 获取专业解读
🔍 搜索更多相关信息
📊 获取市场影响分析
            """
            
            # 发送消息
            payload = {
                "username": "科技新闻机器人",
                "content": message_content,
                "avatar_url": "https://via.placeholder.com/96/00ff00/000000?text=🤖"
            }
            
            try:
                import requests
                response = requests.post(
                    self.webhook_url,
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                response.raise_for_status()
                
                # 存储新闻索引
                post_id = f"{category_name}_{i}"
                self.pending_analyses[post_id] = article
                
            except Exception as e:
                logger.error(f'❌ 发送分类消息失败: {e}')
    
    async def handle_analysis_request(self, request_text: str, user_context: Dict = None) -> bool:
        """处理分析请求"""
        try:
            # 解析请求
            analysis_id = self.parse_analysis_request(request_text)
            
            if not analysis_id:
                return False
            
            # 获取新闻数据
            news_data = self.pending_analyses.get(analysis_id)
            if not news_data:
                await self.send_error_message(f"找不到编号为 {analysis_id} 的新闻")
                return False
            
            # 执行深入分析
            logger.info(f'🔍 开始分析新闻: {analysis_id}')
            analysis_result = await self.analyzer.deep_analyze_news(
                news_data.get('title', ''),
                news_data.get('url', '')
            )
            
            # 发送分析结果
            await self.send_analysis_result(analysis_result, analysis_id)
            
            return True
            
        except Exception as e:
            logger.error(f'❌ 处理分析请求失败: {e}')
            await self.send_error_message(f"分析过程中出现错误: {str(e)}")
            return False
    
    def parse_analysis_request(self, request_text: str) -> Optional[str]:
        """解析分析请求"""
        request_text = request_text.lower().strip()
        
        # 匹配 "分析1", "analyze1", "deep1" 等格式
        import re
        
        patterns = [
            r'分析(\d+)',
            r'analyze(\d+)',
            r'deep(\d+)',
            r'深入(\d+)',
            r'detail(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, request_text)
            if match:
                return match.group(1)
        
        return None
    
    async def send_analysis_result(self, analysis_result: Dict, analysis_id: str):
        """发送分析结果"""
        webhook = get_webhook(self.webhook_url)
        
        # 格式化分析结果
        embed = self.analyzer.format_analysis_for_discord(analysis_result)
        
        payload = {
            "username": "科技新闻分析专家",
            "embeds": [embed],
            "avatar_url": "https://via.placeholder.com/96/ff6600/000000?text=🔍"
        }
        
        try:
            import requests
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            
            logger.info(f'✅ 分析结果已发送: {analysis_id}')
            
        except Exception as e:
            logger.error(f'❌ 发送分析结果失败: {e}')
    
    async def send_error_message(self, error_text: str):
        """发送错误消息"""
        webhook = get_webhook(self.webhook_url)
        
        payload = {
            "username": "科技新闻机器人",
            "content": f"❌ {error_text}",
            "avatar_url": "https://via.placeholder.com/96/ff0000/000000?text=❌"
        }
        
        try:
            import requests
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            
        except Exception as e:
            logger.error(f'❌ 发送错误消息失败: {e}')
    
    def get_usage_guide(self) -> str:
        """获取使用指南"""
        return """
🤖 **科技新闻深入分析使用指南**

**基本命令:**
• `分析1` 或 `analyze1` - 分析第1条新闻
• `分析2` 或 `analyze2` - 分析第2条新闻
• 以此类推...

**分析内容包括:**
📊 市场影响分析
🔧 技术意义解读
🔮 未来发展展望
👥 关键玩家识别
📰 相关新闻聚合

**示例:**
用户: `分析1`
机器人: [发送详细分析报告]

**注意事项:**
• 分析基于AI模型，仅供参考
• 建议结合多方信息进行判断
• 如有错误，请及时反馈
        """

# 全局交互系统实例
interactive_instance = None

def get_interactive_news():
    """获取交互式新闻系统实例"""
    global interactive_instance
    if interactive_instance is None:
        interactive_instance = InteractiveNews()
    return interactive_instance

if __name__ == '__main__':
    # 测试代码
    async def test_interactive():
        interactive = get_interactive_news()
        
        # 测试分析请求解析
        test_requests = [
            "分析1",
            "analyze2", 
            "deep3",
            "深入分析4",
            "invalid request"
        ]
        
        for request in test_requests:
            result = interactive.parse_analysis_request(request)
            print(f"请求: {request} -> 解析结果: {result}")
        
        # 显示使用指南
        print(interactive.get_usage_guide())
    
    asyncio.run(test_interactive())
