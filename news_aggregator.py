"""
新闻聚合器模块
负责从多个源获取、过滤和分类新闻
"""

import requests
import feedparser
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import newspaper
from urllib.parse import urljoin, urlparse
import re
from config import Config
from tavily_search import get_tavily_searcher
from simple_translator import get_simple_translator

logger = logging.getLogger(__name__)

class NewsArticle:
    """新闻文章类"""
    
    def __init__(self, title: str, url: str, summary: str = '', 
                 published_date: Optional[datetime] = None, 
                 source: str = '', category: str = ''):
        self.title = title
        self.url = url
        self.summary = summary
        self.published_date = published_date
        self.source = source
        self.category = category
        self.relevance_score = 0.0
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'title': self.title,
            'url': self.url,
            'summary': self.summary,
            'translated_title': getattr(self, 'translated_title', self.title),
            'translated_summary': getattr(self, 'translated_summary', self.summary),
            'detailed_summary': getattr(self, 'detailed_summary', self.summary),
            'published_date': self.published_date.isoformat() if self.published_date else None,
            'source': self.source,
            'category': self.category,
            'relevance_score': self.relevance_score
        }

class NewsAggregator:
    """新闻聚合器类"""
    
    def __init__(self):
        """初始化新闻聚合器"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 新闻源配置
        self.news_sources = Config.NEWS_SOURCES
        self.filter_config = Config.FILTER_CONFIG
        
        # Tavily搜索器
        self.tavily_searcher = get_tavily_searcher()
        
        # 翻译器
        self.translator = get_simple_translator()
    
    async def get_daily_digest(self) -> Dict:
        """获取每日新闻简报"""
        logger.info('🔄 开始获取每日新闻简报')
        
        all_articles = {}
        hours_back = self.filter_config['hours_back']
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        # 遍历每个分类
        for category, config in self.news_sources.items():
            logger.info(f'📡 获取 {category} 分类新闻')
            category_articles = []
            
            # 从RSS源获取新闻
            if 'rss_feeds' in config:
                rss_articles = await self.get_rss_news(config['rss_feeds'], category, cutoff_time)
                category_articles.extend(rss_articles)
            
            # 从NewsAPI获取新闻
            if 'newsapi_keywords' in config and Config.NEWS_API_KEY:
                api_articles = await self.get_newsapi_news(config['newsapi_keywords'], category, cutoff_time)
                category_articles.extend(api_articles)
            
            # 从Tavily搜索获取新闻
            if Config.TAVILY_API_KEY:
                tavily_articles = await self.get_tavily_news(category, cutoff_time)
                category_articles.extend(tavily_articles)
            
            # 过滤和排序文章
            filtered_articles = self.filter_articles(category_articles, category)
            sorted_articles = sorted(filtered_articles, key=lambda x: x.relevance_score, reverse=True)
            
            # 翻译和增强文章内容
            enhanced_articles = await self.enhance_articles(sorted_articles)
            
            # 限制每个分类的文章数量
            max_articles = self.filter_config['max_articles_per_category']
            all_articles[category] = enhanced_articles[:max_articles]
        
        # 生成摘要
        digest = self.format_digest(all_articles)
        logger.info(f'✅ 新闻简报生成完成，共 {len(all_articles)} 个分类')
        
        return digest
    
    async def get_rss_news(self, rss_feeds: List[str], category: str, cutoff_time: datetime) -> List[NewsArticle]:
        """从RSS源获取新闻"""
        articles = []
        
        for feed_url in rss_feeds:
            try:
                logger.info(f'📡 获取RSS源: {feed_url}')
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries:
                    # 检查发布时间
                    published_date = self.parse_published_date(entry)
                    if published_date and published_date < cutoff_time:
                        continue
                    
                    # 创建文章对象
                    article = NewsArticle(
                        title=entry.title,
                        url=entry.link,
                        summary=getattr(entry, 'summary', ''),
                        published_date=published_date,
                        source=feed.feed.title,
                        category=category
                    )
                    
                    # 计算相关性分数
                    article.relevance_score = self.calculate_relevance_score(article, category)
                    
                    if article.relevance_score >= self.filter_config['min_relevance_score']:
                        articles.append(article)
                        
            except Exception as e:
                logger.error(f'获取RSS源 {feed_url} 时出错: {e}')
        
        return articles
    
    async def get_newsapi_news(self, keywords: List[str], category: str, cutoff_time: datetime) -> List[NewsArticle]:
        """从NewsAPI获取新闻"""
        articles = []
        
        if not Config.NEWS_API_KEY:
            logger.warning('NewsAPI密钥未配置，跳过NewsAPI')
            return articles
        
        base_url = 'https://newsapi.org/v2/everything'
        
        for keyword in keywords:
            try:
                logger.info(f'🔍 搜索NewsAPI关键词: {keyword}')
                
                # 构建查询参数
                params = {
                    'q': keyword,
                    'apiKey': Config.NEWS_API_KEY,
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'from': cutoff_time.isoformat(),
                    'pageSize': 20
                }
                
                response = self.session.get(base_url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                for article_data in data.get('articles', []):
                    # 检查发布时间
                    published_date = self.parse_published_date(article_data)
                    if published_date and published_date < cutoff_time:
                        continue
                    
                    # 创建文章对象
                    article = NewsArticle(
                        title=article_data['title'],
                        url=article_data['url'],
                        summary=article_data.get('description', ''),
                        published_date=published_date,
                        source=article_data.get('source', {}).get('name', ''),
                        category=category
                    )
                    
                    # 计算相关性分数
                    article.relevance_score = self.calculate_relevance_score(article, category)
                    
                    if article.relevance_score >= self.filter_config['min_relevance_score']:
                        articles.append(article)
                        
            except Exception as e:
                logger.error(f'搜索NewsAPI关键词 {keyword} 时出错: {e}')
        
        return articles
    
    async def get_tavily_news(self, category: str, cutoff_time: datetime) -> List[NewsArticle]:
        """从Tavily搜索获取新闻"""
        articles = []
        
        try:
            if category == 'apple':
                tavily_results = await self.tavily_searcher.search_apple_news()
            elif category == 'ai':
                tavily_results = await self.tavily_searcher.search_ai_news()
            elif category == 'llm':
                tavily_results = await self.tavily_searcher.search_llm_news()
            else:
                return articles
            
            for result in tavily_results:
                # 检查发布时间
                published_date = None
                if result.get('published_date'):
                    try:
                        published_date = datetime.fromisoformat(result['published_date'].replace('Z', '+00:00'))
                        if published_date and published_date < cutoff_time:
                            continue
                    except:
                        pass
                
                # 创建文章对象
                article = NewsArticle(
                    title=result.get('title', ''),
                    url=result.get('url', ''),
                    summary=result.get('summary', ''),
                    published_date=published_date,
                    source=result.get('source', 'Tavily Search'),
                    category=category
                )
                
                # 使用Tavily的相关性分数
                article.relevance_score = result.get('relevance_score', 0.5)
                
                articles.append(article)
                
        except Exception as e:
            logger.error(f'从Tavily获取 {category} 新闻时出错: {e}')
        
        return articles
    
    async def enhance_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """增强文章内容（翻译和获取详细摘要）"""
        enhanced_articles = []
        
        for article in articles:
            try:
                # 翻译标题和摘要
                translation_result = await self.translator.translate_news_article(
                    article.title, 
                    article.summary
                )
                
                # 获取完整内容摘要
                full_content = await self.get_article_content(article.url)
                if full_content:
                    # 提取更详细的摘要（前200字符）
                    if len(full_content) > 200:
                        detailed_summary = full_content[:200] + "..."
                    else:
                        detailed_summary = full_content
                    
                    # 翻译详细摘要
                    translated_detailed = await self.translator.translate_text(detailed_summary, 'zh')
                    
                    # 更新文章信息
                    article.translated_title = translation_result['translated_title']
                    article.translated_summary = translation_result['translated_summary']
                    article.detailed_summary = translated_detailed
                    article.original_content = full_content[:500]  # 保存前500字符
                else:
                    # 如果无法获取完整内容，使用现有摘要
                    article.translated_title = translation_result['translated_title']
                    article.translated_summary = translation_result['translated_summary']
                    article.detailed_summary = translation_result['translated_summary']
                
                enhanced_articles.append(article)
                
            except Exception as e:
                logger.error(f'增强文章内容失败: {e}')
                # 如果增强失败，保留原文章
                enhanced_articles.append(article)
        
        return enhanced_articles
    
    async def get_article_content(self, url: str) -> Optional[str]:
        """获取文章完整内容"""
        try:
            import newspaper
            from newspaper import Article
            
            article = Article(url)
            article.download()
            article.parse()
            
            if article.text:
                return article.text.strip()
            return None
            
        except Exception as e:
            logger.error(f'获取文章内容失败 {url}: {e}')
            return None
    
    def parse_published_date(self, entry) -> Optional[datetime]:
        """解析发布日期"""
        date_formats = [
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%d %H:%M:%S',
            '%a, %d %b %Y %H:%M:%S %Z'
        ]
        
        # 尝试不同的日期字段
        date_fields = ['published', 'pubDate', 'published_parsed', 'date']
        
        for field in date_fields:
            if hasattr(entry, field):
                date_value = getattr(entry, field)
                
                if isinstance(date_value, datetime):
                    return date_value
                elif isinstance(date_value, str):
                    for fmt in date_formats:
                        try:
                            return datetime.strptime(date_value, fmt)
                        except ValueError:
                            continue
                elif isinstance(date_value, tuple) and len(date_value) >= 6:
                    try:
                        return datetime(*date_value[:6])
                    except (ValueError, TypeError):
                        continue
        
        return None
    
    def calculate_relevance_score(self, article: NewsArticle, category: str) -> float:
        """计算文章相关性分数"""
        score = 0.0
        
        # 获取分类关键词
        category_config = self.news_sources.get(category, {})
        keywords = category_config.get('search_keywords', [])
        
        # 标题和摘要文本
        text = (article.title + ' ' + article.summary).lower()
        
        # 关键词匹配
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in text:
                score += 1.0
        
        # 标题中的关键词权重更高
        title_lower = article.title.lower()
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in title_lower:
                score += 0.5
        
        # 标准化分数
        max_possible_score = len(keywords) * 1.5
        if max_possible_score > 0:
            score = score / max_possible_score
        
        return min(score, 1.0)
    
    def filter_articles(self, articles: List[NewsArticle], category: str) -> List[NewsArticle]:
        """过滤文章"""
        filtered = []
        
        for article in articles:
            # 检查排除关键词
            exclude_keywords = self.filter_config['exclude_keywords']
            text = (article.title + ' ' + article.summary).lower()
            
            if any(keyword.lower() in text for keyword in exclude_keywords):
                continue
            
            # 检查相关性分数
            if article.relevance_score < self.filter_config['min_relevance_score']:
                continue
            
            # 去重（基于URL）
            if any(existing.url == article.url for existing in filtered):
                continue
            
            filtered.append(article)
        
        return filtered
    
    def format_digest(self, articles_by_category: Dict[str, List[NewsArticle]]) -> Dict:
        """格式化新闻简报"""
        digest = {
            'title': Config.MESSAGE_FORMAT['title'],
            'description': f'过去{self.filter_config["hours_back"]}小时的科技新闻汇总',
            'categories': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # 转换文章为字典格式
        for category, articles in articles_by_category.items():
            digest['categories'][category] = [article.to_dict() for article in articles]
        
        return digest
    
    async def get_article_content(self, url: str) -> Optional[str]:
        """获取文章完整内容"""
        try:
            article = newspaper.Article(url)
            article.download()
            article.parse()
            return article.text
        except Exception as e:
            logger.error(f'获取文章内容失败 {url}: {e}')
            return None

if __name__ == '__main__':
    # 测试代码
    import asyncio
    
    async def test_aggregator():
        aggregator = NewsAggregator()
        digest = await aggregator.get_daily_digest()
        
        print('=== 新闻简报 ===')
        print(f"标题: {digest['title']}")
        print(f"描述: {digest['description']}")
        print(f"时间: {digest['timestamp']}")
        
        for category, articles in digest['categories'].items():
            print(f"\n=== {category.upper()} ===")
            for i, article in enumerate(articles, 1):
                print(f"{i}. {article['title']}")
                print(f"   相关性: {article['relevance_score']:.2f}")
                print(f"   来源: {article['source']}")
    
    asyncio.run(test_aggregator())
