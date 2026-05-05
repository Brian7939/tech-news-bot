"""
简单翻译模块
使用requests直接调用DeepSeek API，无需openai库
"""

import asyncio
import logging
import requests
import json
from typing import Optional
from config import Config

logger = logging.getLogger(__name__)

class SimpleTranslator:
    """简单翻译器"""
    
    def __init__(self):
        """初始化翻译器"""
        self.deepseek_api_key = Config.DEEPSEEK_API_KEY
        self.deepseek_model = Config.DEEPSEEK_MODEL
        self.base_url = "https://api.deepseek.com"
    
    async def translate_text(self, text: str, target_lang: str = 'zh') -> Optional[str]:
        """翻译文本"""
        if not self.deepseek_api_key:
            logger.warning("DeepSeek API密钥未配置，跳过翻译")
            return text
        
        try:
            # 检测是否需要翻译
            if self._is_chinese(text) and target_lang == 'zh':
                return text
            if not self._is_chinese(text) and target_lang == 'en':
                return text
            
            # 构建翻译提示
            if target_lang == 'zh':
                prompt = f"请将以下英文新闻内容翻译成中文，保持专业性和准确性，不要添加额外解释：\n\n{text}"
            else:
                prompt = f"Please translate the following Chinese news content to English, maintaining professionalism and accuracy:\n\n{text}"
            
            # 调用DeepSeek API
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.deepseek_model,
                "messages": [
                    {
                        "role": "system", 
                        "content": "你是一个专业的新闻翻译专家，擅长在中英文之间进行准确、自然的翻译。"
                    },
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2000,
                "temperature": 0.1
            }
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: requests.post(f"{self.base_url}/chat/completions", 
                                    headers=headers, 
                                    json=data, 
                                    timeout=30)
            )
            
            if response.status_code == 200:
                result = response.json()
                translated_text = result['choices'][0]['message']['content'].strip()
                logger.info(f'✅ 翻译完成: {len(text)} -> {len(translated_text)} 字符')
                return translated_text
            else:
                logger.error(f'❌ API调用失败: {response.status_code} - {response.text}')
                return text
            
        except Exception as e:
            logger.error(f'❌ 翻译失败: {e}')
            return text  # 翻译失败时返回原文
    
    def _is_chinese(self, text: str) -> bool:
        """检测文本是否包含中文"""
        chinese_char_count = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        total_chars = len(text.replace(' ', '').replace('\n', ''))
        
        if total_chars == 0:
            return False
        
        # 如果中文字符占比超过20%，认为是中文
        return (chinese_char_count / total_chars) > 0.2
    
    async def translate_news_article(self, title: str, summary: str, content: str = "") -> dict:
        """翻译整篇新闻文章"""
        try:
            # 翻译标题
            translated_title = await self.translate_text(title, 'zh')
            
            # 翻译摘要
            translated_summary = await self.translate_text(summary, 'zh')
            
            # 翻译内容（如果提供）
            translated_content = await self.translate_text(content, 'zh') if content else ""
            
            return {
                'original_title': title,
                'translated_title': translated_title,
                'original_summary': summary,
                'translated_summary': translated_summary,
                'original_content': content,
                'translated_content': translated_content
            }
            
        except Exception as e:
            logger.error(f'❌ 翻译新闻文章失败: {e}')
            return {
                'original_title': title,
                'translated_title': title,
                'original_summary': summary,
                'translated_summary': summary,
                'original_content': content,
                'translated_content': content
            }

# 全局翻译器实例
translator_instance = None

def get_simple_translator():
    """获取简单翻译器实例"""
    global translator_instance
    if translator_instance is None:
        translator_instance = SimpleTranslator()
    return translator_instance

if __name__ == '__main__':
    # 测试代码
    async def test_translator():
        translator = get_simple_translator()
        
        # 测试英文翻译
        test_text = "Apple announces new M3 chip with 40% performance improvement"
        translated = await translator.translate_text(test_text, 'zh')
        print(f"原文: {test_text}")
        print(f"译文: {translated}")
        
        # 测试中文翻译
        test_text2 = "苹果发布新款M3芯片，性能提升40%"
        translated2 = await translator.translate_text(test_text2, 'en')
        print(f"\n原文: {test_text2}")
        print(f"译文: {translated2}")
    
    asyncio.run(test_translator())
