"""
新闻格式化和摘要模块
负责生成新闻摘要和格式化输出
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
import re
from config import Config

logger = logging.getLogger(__name__)

class NewsFormatter:
    """新闻格式化器"""
    
    def __init__(self):
        """初始化格式化器"""
        self.max_summary_length = Config.MESSAGE_FORMAT['max_summary_length']
        self.include_emojis = Config.MESSAGE_FORMAT['include_emojis']
        self.categories_order = Config.MESSAGE_FORMAT['categories_order']
        
        # 分类图标
        self.category_emojis = {
            'apple': '🍎',
            'ai': '🤖',
            'llm': '🧠'
        }
        
        # 分类显示名称
        self.category_names = {
            'apple': '苹果产品动态',
            'ai': 'AI技术发展',
            'llm': '大语言模型'
        }
    
    def format_news_digest(self, news_data: Dict) -> Dict:
        """格式化新闻简报"""
        formatted_digest = {
            'title': self._format_title(news_data.get('title', '🤖 科技新闻简报')),
            'description': news_data.get('description', ''),
            'timestamp': news_data.get('timestamp', datetime.now().isoformat()),
            'categories': {},
            'summary': self._generate_overall_summary(news_data.get('categories', {}))
        }
        
        # 格式化每个分类的新闻
        categories = news_data.get('categories', {})
        
        # 按配置的顺序排序分类
        ordered_categories = []
        for cat in self.categories_order:
            if cat in categories:
                ordered_categories.append(cat)
        
        # 添加未在配置中的分类
        for cat in categories:
            if cat not in ordered_categories:
                ordered_categories.append(cat)
        
        for category in ordered_categories:
            articles = categories[category]
            if articles:
                formatted_digest['categories'][category] = self._format_category_articles(category, articles)
        
        return formatted_digest
    
    def _format_title(self, title: str) -> str:
        """格式化标题"""
        if self.include_emojis:
            return f"🤖 {title}"
        return title
    
    def _format_category_articles(self, category: str, articles: List[Dict]) -> List[Dict]:
        """格式化分类文章"""
        formatted_articles = []
        
        emoji = self.category_emojis.get(category, '📰')
        category_name = self.category_names.get(category, category.title())
        
        for article in articles:
            formatted_article = {
                'title': self._clean_title(article.get('title', '')),
                'url': article.get('url', ''),
                'summary': self._generate_article_summary(article.get('summary', ''), article.get('title', '')),
                'source': article.get('source', ''),
                'published_date': self._format_date(article.get('published_date')),
                'relevance_score': article.get('relevance_score', 0),
                'category_emoji': emoji,
                'category_name': category_name
            }
            
            formatted_articles.append(formatted_article)
        
        return formatted_articles
    
    def _clean_title(self, title: str) -> str:
        """清理标题"""
        if not title:
            return "无标题"
        
        # 移除多余的空白字符
        title = re.sub(r'\s+', ' ', title.strip())
        
        # 移除常见的广告词汇
        ad_words = ['[广告]', '[Sponsored]', 'Advertisement', 'Sponsored']
        for word in ad_words:
            title = title.replace(word, '').strip()
        
        return title
    
    def _generate_article_summary(self, summary: str, title: str) -> str:
        """生成文章摘要"""
        if not summary:
            # 如果没有摘要，使用标题的一部分
            return title[:self.max_summary_length] + '...' if len(title) > self.max_summary_length else title
        
        # 清理摘要
        summary = re.sub(r'\s+', ' ', summary.strip())
        
        # 移除HTML标签
        summary = re.sub(r'<[^>]+>', '', summary)
        
        # 移除常见的广告词汇
        ad_words = ['点击查看更多', 'Read more', 'Click here', '广告']
        for word in ad_words:
            summary = summary.replace(word, '').strip()
        
        # 限制长度
        if len(summary) > self.max_summary_length:
            summary = summary[:self.max_summary_length].rsplit(' ', 1)[0] + '...'
        
        return summary
    
    def _format_date(self, date_str: Optional[str]) -> str:
        """格式化日期"""
        if not date_str:
            return ''
        
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date_obj.strftime('%m-%d %H:%M')
        except:
            return date_str
    
    def _generate_overall_summary(self, categories: Dict) -> str:
        """生成整体摘要"""
        total_articles = sum(len(articles) for articles in categories.values())
        category_count = len(categories)
        
        summary_parts = []
        
        if category_count > 0:
            category_names = []
            for category in categories.keys():
                if category in self.category_names:
                    category_names.append(self.category_names[category])
            
            if category_names:
                summary_parts.append(f"涵盖{', '.join(category_names)}等{category_count}个领域")
        
        if total_articles > 0:
            summary_parts.append(f"共{total_articles}条重要资讯")
        
        if summary_parts:
            return ' | '.join(summary_parts)
        
        return "今日科技新闻汇总"
    
    def format_discord_message(self, news_data: Dict) -> str:
        """格式化Discord消息（纯文本格式）"""
        formatted_data = self.format_news_digest(news_data)
        
        message_parts = []
        
        # 标题
        message_parts.append(f"**{formatted_data['title']}**")
        message_parts.append(f"📅 {self._format_date(formatted_data['timestamp'])}")
        message_parts.append(f"📊 {formatted_data['summary']}")
        message_parts.append("")
        
        # 分类新闻
        for category, articles in formatted_data['categories'].items():
            if not articles:
                continue
            
            emoji = self.category_emojis.get(category, '📰')
            category_name = self.category_names.get(category, category.title())
            
            message_parts.append(f"**{emoji} {category_name}**")
            
            for i, article in enumerate(articles[:3], 1):  # 最多显示3篇
                title = article['title']
                url = article['url']
                summary = article['summary']
                
                if url:
                    message_parts.append(f"{i}. **[{title}]({url})**")
                else:
                    message_parts.append(f"{i}. **{title}**")
                
                if summary:
                    message_parts.append(f"   {summary}")
                
                message_parts.append("")
        
        # 页脚
        message_parts.append("---")
        message_parts.append("🤖 由科技新闻机器人自动推送")
        
        return "\n".join(message_parts)
    
    def generate_summary_with_ai(self, articles: List[Dict], category: str) -> Optional[str]:
        """使用AI生成摘要（如果配置了OpenAI）"""
        if not Config.OPENAI_API_KEY:
            return None
        
        try:
            import openai
            
            # 准备文章文本
            articles_text = ""
            for i, article in enumerate(articles[:5], 1):  # 最多处理5篇文章
                articles_text += f"{i}. {article.get('title', '')}\n"
                articles_text += f"   {article.get('summary', '')}\n\n"
            
            # 构建提示
            category_name = self.category_names.get(category, category)
            prompt = f"""
请为以下{category_name}领域的新闻生成一个简洁的摘要（不超过100字）：

{articles_text}

摘要应该：
1. 突出最重要的信息
2. 语言简洁明了
3. 保持客观中立
4. 使用中文回复
"""
            
            # 调用OpenAI API
            response = openai.ChatCompletion.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个专业的新闻摘要助手，擅长提炼关键信息。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            logger.error(f"使用AI生成摘要时出错: {e}")
            return None

# 全局格式化器实例
formatter_instance = None

def get_formatter():
    """获取格式化器实例"""
    global formatter_instance
    if formatter_instance is None:
        formatter_instance = NewsFormatter()
    return formatter_instance

if __name__ == '__main__':
    # 测试格式化器
    test_news_data = {
        'title': '科技新闻简报',
        'description': '测试新闻简报',
        'timestamp': datetime.now().isoformat(),
        'categories': {
            'apple': [
                {
                    'title': '苹果发布新款iPhone 15',
                    'url': 'https://example.com/iphone15',
                    'summary': '苹果公司今天发布了新款iPhone 15，配备了更强大的A17芯片和改进的摄像头系统。',
                    'source': 'TechCrunch',
                    'published_date': datetime.now().isoformat(),
                    'relevance_score': 0.9
                }
            ],
            'ai': [
                {
                    'title': 'OpenAI发布GPT-5',
                    'url': 'https://example.com/gpt5',
                    'summary': 'OpenAI宣布发布GPT-5，性能比前代提升显著。',
                    'source': 'AI News',
                    'published_date': datetime.now().isoformat(),
                    'relevance_score': 0.85
                }
            ]
        }
    }
    
    formatter = get_formatter()
    formatted = formatter.format_news_digest(test_news_data)
    
    print("=== 格式化结果 ===")
    print(f"标题: {formatted['title']}")
    print(f"摘要: {formatted['summary']}")
    print("\n=== Discord消息 ===")
    print(formatter.format_discord_message(test_news_data))
