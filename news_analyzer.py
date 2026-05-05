"""
新闻深入分析模块
提供多源搜索和专家级解读功能
"""

import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime
import json
from tavily_search import get_tavily_searcher
from config import Config

logger = logging.getLogger(__name__)

class NewsAnalyzer:
    """新闻分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.tavily_searcher = get_tavily_searcher()
        self.openai_api_key = Config.OPENAI_API_KEY
        self.deepseek_api_key = Config.DEEPSEEK_API_KEY
        self.deepseek_model = Config.DEEPSEEK_MODEL
    
    async def deep_analyze_news(self, news_title: str, news_url: str = "") -> Dict:
        """深入分析单个新闻"""
        logger.info(f'🔍 开始深入分析新闻: {news_title}')
        
        analysis_result = {
            'original_title': news_title,
            'original_url': news_url,
            'timestamp': datetime.now().isoformat(),
            'related_news': [],
            'expert_analysis': '',
            'market_impact': '',
            'future_outlook': '',
            'key_players': [],
            'technical_details': ''
        }
        
        try:
            # 1. 多源搜索相关新闻
            related_news = await self.search_related_news(news_title, news_url)
            analysis_result['related_news'] = related_news
            
            # 2. 生成专家分析
            if self.deepseek_api_key:
                expert_analysis = await self.generate_expert_analysis_deepseek(news_title, related_news)
                analysis_result.update(expert_analysis)
            elif self.openai_api_key:
                expert_analysis = await self.generate_expert_analysis(news_title, related_news)
                analysis_result.update(expert_analysis)
            else:
                analysis_result['expert_analysis'] = '⚠️ 需要配置DeepSeek或OpenAI API密钥以获取专家分析'
            
            logger.info('✅ 新闻深入分析完成')
            return analysis_result
            
        except Exception as e:
            logger.error(f'❌ 新闻分析失败: {e}')
            analysis_result['expert_analysis'] = f'分析过程中出现错误: {str(e)}'
            return analysis_result
    
    async def search_related_news(self, title: str, original_url: str = "") -> List[Dict]:
        """搜索相关新闻"""
        related_news = []
        
        try:
            # 构建搜索查询
            search_query = self.build_search_query(title)
            
            # 使用Tavily搜索
            search_results = await self.tavily_searcher.search_tech_news(search_query, hours_back=72)  # 搜索过去3天
            
            # 过滤掉原始新闻
            for result in search_results:
                if result['url'] != original_url:
                    related_news.append({
                        'title': result['title'],
                        'url': result['url'],
                        'summary': result['summary'],
                        'source': result['source'],
                        'relevance': result.get('relevance_score', 0.0)
                    })
            
            # 按相关性排序，最多返回10条
            related_news.sort(key=lambda x: x['relevance'], reverse=True)
            related_news = related_news[:10]
            
            logger.info(f'🔍 找到 {len(related_news)} 条相关新闻')
            return related_news
            
        except Exception as e:
            logger.error(f'❌ 搜索相关新闻失败: {e}')
            return []
    
    def build_search_query(self, title: str) -> str:
        """构建搜索查询"""
        # 提取关键词
        keywords = self.extract_keywords(title)
        
        # 构建查询
        if len(keywords) > 3:
            query = ' '.join(keywords[:3])  # 取前3个关键词
        else:
            query = ' '.join(keywords)
        
        # 添加相关词汇
        query += ' news analysis impact'
        
        return query
    
    def extract_keywords(self, title: str) -> List[str]:
        """从标题提取关键词"""
        # 简单的关键词提取逻辑
        import re
        
        # 移除常见停用词
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'among', 'is', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do',
            'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might',
            'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
            'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where',
            'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
            'other', 'some', 'such', 'only', 'own', 'same', 'so', 'than', 'too',
            'very', 'just', 'now', '说', '的', '了', '在', '是', '我', '有', '和',
            '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去'
        }
        
        # 分词并过滤
        words = re.findall(r'\b\w+\b', title.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords
    
    async def generate_expert_analysis(self, title: str, related_news: List[Dict]) -> Dict:
        """生成专家级分析"""
        try:
            import openai
            
            # 准备分析材料
            news_context = self.prepare_analysis_context(title, related_news)
            
            # 构建分析提示
            analysis_prompt = f"""
作为资深科技行业观察家，请对以下新闻进行深入分析：

**原始新闻标题**: {title}

**相关新闻报道**:
{news_context}

请从以下几个维度进行分析：

1. **市场影响**: 这条新闻对相关市场的影响
2. **技术意义**: 从技术角度分析其重要性
3. **行业趋势**: 反映了什么行业趋势
4. **关键玩家**: 涉及的主要公司和人物
5. **未来展望**: 对未来发展的预测
6. **投资建议**: 从投资者角度的建议

请以专业、客观的语调进行分析，每个维度控制在100字以内。使用中文回复。
"""
            
            # 调用OpenAI API
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: openai.ChatCompletion.create(
                    model=Config.OPENAI_MODEL,
                    messages=[
                        {
                            "role": "system", 
                            "content": "你是一位资深的科技行业观察家，拥有20年行业经验，擅长从多角度分析科技新闻的深层含义和市场影响。"
                        },
                        {"role": "user", "content": analysis_prompt}
                    ],
                    max_tokens=2048,
                    temperature=0.3
                )
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # 解析分析结果
            parsed_analysis = self.parse_analysis_result(analysis_text)
            
            return parsed_analysis
            
        except Exception as e:
            logger.error(f'❌ 生成专家分析失败: {e}')
            return {
                'expert_analysis': f'专家分析生成失败: {str(e)}',
                'market_impact': '',
                'future_outlook': '',
                'key_players': [],
                'technical_details': ''
            }
    
    async def generate_expert_analysis_deepseek(self, title: str, related_news: List[Dict]) -> Dict:
        """使用DeepSeek生成专家级分析"""
        try:
            import openai
            
            # 准备分析材料
            news_context = self.prepare_analysis_context(title, related_news)
            
            # 构建分析提示
            analysis_prompt = f"""
作为资深科技行业观察家，请对以下新闻进行深入分析：

**原始新闻标题**: {title}

**相关新闻报道**:
{news_context}

请从以下几个维度进行分析：

1. **市场影响**: 这条新闻对相关市场的影响
2. **技术意义**: 从技术角度分析其重要性
3. **行业趋势**: 反映了什么行业趋势
4. **关键玩家**: 涉及的主要公司和人物
5. **未来展望**: 对未来发展的预测
6. **投资建议**: 从投资者角度的建议

请以专业、客观的语调进行分析，每个维度控制在100字以内。使用中文回复。
"""
            
            # 调用DeepSeek API (使用OpenAI兼容接口)
            client = openai.OpenAI(
                api_key=self.deepseek_api_key,
                base_url="https://api.deepseek.com"
            )
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: client.chat.completions.create(
                    model=self.deepseek_model,
                    messages=[
                        {
                            "role": "system", 
                            "content": "你是一位资深的科技行业观察家，拥有20年行业经验，擅长从多角度分析科技新闻的深层含义和市场影响。"
                        },
                        {"role": "user", "content": analysis_prompt}
                    ],
                    max_tokens=2048,
                    temperature=0.3
                )
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # 解析分析结果
            parsed_analysis = self.parse_analysis_result(analysis_text)
            
            return parsed_analysis
            
        except Exception as e:
            logger.error(f'❌ 生成DeepSeek专家分析失败: {e}')
            return {
                'expert_analysis': f'DeepSeek专家分析生成失败: {str(e)}',
                'market_impact': '',
                'future_outlook': '',
                'key_players': [],
                'technical_details': ''
            }
    
    def prepare_analysis_context(self, title: str, related_news: List[Dict]) -> str:
        """准备分析上下文"""
        context = f"主新闻: {title}\n\n相关新闻:\n"
        
        for i, news in enumerate(related_news[:5], 1):  # 最多5条相关新闻
            context += f"{i}. {news['title']}\n"
            context += f"   来源: {news['source']}\n"
            context += f"   摘要: {news['summary'][:100]}...\n\n"
        
        return context
    
    def parse_analysis_result(self, analysis_text: str) -> Dict:
        """解析分析结果"""
        result = {
            'expert_analysis': analysis_text,
            'market_impact': '',
            'future_outlook': '',
            'key_players': [],
            'technical_details': ''
        }
        
        # 简单的文本解析逻辑
        lines = analysis_text.split('\n')
        current_section = ''
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 识别各个部分
            if '市场影响' in line or 'Market Impact' in line:
                current_section = 'market_impact'
                result[current_section] = line.split(':', 1)[-1].strip()
            elif '技术意义' in line or 'Technical' in line:
                current_section = 'technical_details'
                result[current_section] = line.split(':', 1)[-1].strip()
            elif '未来展望' in line or 'Future' in line:
                current_section = 'future_outlook'
                result[current_section] = line.split(':', 1)[-1].strip()
            elif '关键玩家' in line or 'Key Players' in line:
                current_section = 'key_players'
                # 提取公司/人物名称
                players = [p.strip() for p in line.split(':', 1)[-1].split(',')]
                result[current_section] = players
            elif current_section and line.startswith('-'):
                # 继续当前部分的内容
                if current_section in ['market_impact', 'future_outlook', 'technical_details']:
                    result[current_section] += ' ' + line.lstrip('- ').strip()
        
        # 如果解析失败，使用全文作为专家分析
        if not any(result.values()):
            result['expert_analysis'] = analysis_text
        
        return result
    
    def format_analysis_for_discord(self, analysis: Dict) -> Dict:
        """格式化分析结果为Discord消息"""
        embed = {
            "title": f"🔍 深入分析: {analysis['original_title'][:50]}...",
            "description": "资深科技观察家专业解读",
            "color": 15105570,  # 橙色
            "timestamp": analysis['timestamp'],
            "fields": []
        }
        
        # 添加分析字段
        if analysis.get('market_impact'):
            embed["fields"].append({
                "name": "📊 市场影响",
                "value": analysis['market_impact'][:1024],
                "inline": False
            })
        
        if analysis.get('technical_details'):
            embed["fields"].append({
                "name": "🔧 技术意义",
                "value": analysis['technical_details'][:1024],
                "inline": False
            })
        
        if analysis.get('future_outlook'):
            embed["fields"].append({
                "name": "🔮 未来展望",
                "value": analysis['future_outlook'][:1024],
                "inline": False
            })
        
        if analysis.get('key_players'):
            players_text = ', '.join(analysis['key_players'][:5])  # 最多5个
            embed["fields"].append({
                "name": "👥 关键玩家",
                "value": players_text,
                "inline": False
            })
        
        # 添加相关新闻
        if analysis.get('related_news'):
            related_text = ""
            for i, news in enumerate(analysis['related_news'][:3], 1):  # 最多3条
                related_text += f"**{i}. [{news['title']}]({news['url']})**\n"
                related_text += f"   {news['summary'][:80]}...\n\n"
            
            if related_text:
                embed["fields"].append({
                    "name": "📰 相关新闻",
                    "value": related_text[:1024],
                    "inline": False
                })
        
        return embed

# 全局分析器实例
analyzer_instance = None

def get_news_analyzer():
    """获取新闻分析器实例"""
    global analyzer_instance
    if analyzer_instance is None:
        analyzer_instance = NewsAnalyzer()
    return analyzer_instance

if __name__ == '__main__':
    # 测试代码
    async def test_analyzer():
        analyzer = get_news_analyzer()
        
        # 测试分析
        test_title = "苹果发布新款M3芯片MacBook Pro"
        analysis = await analyzer.deep_analyze_news(test_title)
        
        print("=== 新闻分析结果 ===")
        print(f"标题: {analysis['original_title']}")
        print(f"相关新闻: {len(analysis['related_news'])} 条")
        print(f"专家分析: {analysis['expert_analysis'][:100]}...")
        
        # 格式化Discord消息
        discord_embed = analyzer.format_analysis_for_discord(analysis)
        print(f"\n=== Discord嵌入消息 ===")
        print(f"标题: {discord_embed['title']}")
        print(f"字段数: {len(discord_embed['fields'])}")
    
    asyncio.run(test_analyzer())
