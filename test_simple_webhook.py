"""
简单测试Discord Webhook功能
"""

import requests
import json

def test_simple_webhook():
    """简单测试Webhook"""
    webhook_url = "https://discordapp.com/api/webhooks/1501126966835806248/_JDBw42YY7S30lQJhnKHngc21ULBC5WekgTtNqcg4RCn4YSA1p-kALfplcIfNdetPE1G"
    
    # 简单的文本消息（添加thread_name以支持论坛频道）
    payload = {
        "content": "🧪 测试消息：科技新闻机器人Webhook测试成功！",
        "username": "科技新闻机器人",
        "thread_name": "科技新闻测试"
    }
    
    try:
        print("🧪 发送测试消息到Discord...")
        response = requests.post(webhook_url, json=payload, timeout=30)
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 204:
            print("✅ Webhook测试成功！")
            return True
        else:
            print(f"❌ Webhook测试失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        return False

if __name__ == '__main__':
    test_simple_webhook()
