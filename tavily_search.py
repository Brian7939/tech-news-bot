"""
Tavily搜索模块
使用Tavily API进行网页搜索和内容提取
"""

import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from config import Config

logger = logging.getLogger(__name__)

class TavilySearcher:
    """Tavily搜索器"""
    
    def __init__(self):
        """初始化搜索器"""
        self.api_key = Config.TAVILY_API_KEY
        self.base_url = "https://api.tavily.com"
        
        if not self.api_key:
            logger.warning("⚠️ Tavily API密钥未配置")
    
    async def search_tech_news(self, query: str, hours_back: int = 24) -> List[Dict]:
        """搜索科技新闻"""
        if not self.api_key:
            logger.warning("Tavily API密钥未配置，跳过搜索")
            return []
        
        try:
            # 构建搜索参数
            payload = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": "basic",
                "include_answer": False,
                "include_raw_content": True,
                "max_results": 10,
                "include_domains": [
                    "techcrunch.com",
                    "venturebeat.com",
                    "arstechnica.com",
                    "theverge.com",
                    "wired.com",
                    "9to5mac.com",
                    "macrumors.com",
                    "appleinsider.com",
                    "arxiv.org",
                    "huggingface.co",
                    "openai.com",
                    "anthropic.com"
                ],
                "days": max(1, hours_back // 24)  # 转换为天数
            }
            
            response = requests.post(f"{self.base_url}/search", json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for result in data.get("results", []):
                # 解析发布时间
                published_date = self._parse_published_date(result.get("published_date"))
                
                # 检查是否在时间范围内
                if published_date and published_date < datetime.now() - timedelta(hours=hours_back):
                    continue
                
                article = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "summary": result.get("content", "")[:500],  # 限制摘要长度
                    "source": self._extract_domain(result.get("url", "")),
                    "published_date": published_date.isoformat() if published_date else None,
                    "relevance_score": result.get("score", 0.0)
                }
                
                articles.append(article)
            
            logger.info(f"✅ Tavily搜索完成，找到 {len(articles)} 篇文章")
            return articles
            
        except Exception as e:
            logger.error(f"❌ Tavily搜索失败: {e}")
            return []
    
    async def search_apple_news(self) -> List[Dict]:
        """搜索苹果相关新闻"""
        queries = [
            "Apple iPhone iPad Mac news product launch",
            "Apple iOS macOS update release",
            "Apple WWDC event announcement"
        ]
        
        all_articles = []
        for query in queries:
            articles = await self.search_tech_news(query)
            all_articles.extend(articles)
        
        # 去重
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article["url"] not in seen_urls:
                seen_urls.add(article["url"])
                unique_articles.append(article)
        
        return unique_articles
    
    async def search_ai_news(self) -> List[Dict]:
        """搜索AI相关新闻"""
        queries = [
            "artificial intelligence AI breakthrough research",
            "machine learning deep learning development",
            "AI technology news innovation"
        ]
        
        all_articles = []
        for query in queries:
            articles = await self.search_tech_news(query)
            all_articles.extend(articles)
        
        # 去重
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article["url"] not in seen_urls:
                seen_urls.add(article["url"])
                unique_articles.append(article)
        
        return unique_articles
    
    async def search_llm_news(self) -> List[Dict]:
        """搜索大语言模型相关新闻"""
        queries = [
            "large language model LLM GPT ChatGPT news",
            "open source local LLM development",
            "Llama Claude Mistral model release"
        ]
        
        all_articles = []
        for query in queries:
            articles = await self.search_tech_news(query)
            all_articles.extend(articles)
        
        # 去重
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article["url"] not in seen_urls:
                seen_urls.add(article["url"])
                unique_articles.append(article)
        
        return unique_articles
    
    def _parse_published_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """解析发布日期"""
        if not date_str:
            return None
        
        try:
            # 尝试解析ISO格式日期
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            # 尝试其他常见格式
            import re
            from dateutil.parser import parse
            
            try:
                return parse(date_str)
            except:
                return None
    
    def _extract_domain(self, url: str) -> str:
        """从URL提取域名"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return "Unknown"

# 全局搜索器实例
tavily_instance = None

def get_tavily_searcher():
    """获取Tavily搜索器实例"""
    global tavily_instance
    if tavily_instance is None:
        tavily_instance = TavilySearcher()
    return tavily_instance

if __name__ == '__main__':
    # 测试代码
    import asyncio
    
    async def test_tavily():
        searcher = get_tavily_searcher()
        
        print("🔍 测试苹果新闻搜索...")
        apple_news = await searcher.search_apple_news()
        print(f"找到 {len(apple_news)} 篇苹果新闻")
        
        if apple_news:
            print(f"示例: {apple_news[0]['title']}")
        
        print("\n🔍 测试AI新闻搜索...")
        ai_news = await searcher.search_ai_news()
        print(f"找到 {len(ai_news)} 篇AI新闻")
        
        if ai_news:
            print(f"示例: {ai_news[0]['title']}")
    
    asyncio.run(test_tavily())
