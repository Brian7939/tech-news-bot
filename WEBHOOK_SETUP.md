# Discord Webhook设置指南

使用Webhook是推荐的方式，无需创建额外的机器人，可以直接在您现有的Discord服务器中接收新闻推送。

## 🎯 为什么选择Webhook？

- ✅ **无需额外机器人**: 不需要创建和管理新的Discord机器人
- ✅ **简单配置**: 只需要创建一个Webhook URL
- ✅ **独立运行**: 不会与您现有的openclaw机器人产生冲突
- ✅ **高效推送**: 直接发送消息到指定频道

## 📋 设置步骤

### 步骤1: 在Discord中创建Webhook

1. **打开您的Discord服务器**
2. **选择目标频道**（想要接收新闻的频道）
3. **点击频道旁边的齿轮图标**（频道设置）
4. **选择"集成"选项卡**
5. **点击"创建Webhook"**
6. **配置Webhook**:
   - **名称**: 科技新闻机器人
   - **头像**: 可选择上传机器人头像
   - **频道**: 确认是目标频道
7. **复制Webhook URL**
   - 格式类似: `https://discord.com/api/webhooks/1234567890/abcdefg-12345-hijklmnop`

### 步骤2: 配置环境变量

编辑项目根目录下的 `.env` 文件：

```env
# Discord Webhook配置
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/你的ID/你的令牌

# 其他配置保持不变...
NEWS_API_KEY=7f118b9d6e8b41db8587f830316be0c3
TAVILY_API_KEY=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
```

### 步骤3: 测试Webhook

```bash
# 测试Webhook功能
python discord_webhook.py

# 或者测试完整系统
python main.py test
```

## 🔧 高级配置

### 自定义Webhook名称和头像

在 `discord_webhook.py` 中可以修改：

```python
payload = {
    "username": "科技新闻机器人",  # 自定义名称
    "avatar_url": "https://your-avatar-url.com/image.png",  # 自定义头像
    "embeds": [embed]
}
```

### 多频道支持

如果需要发送到多个频道，可以：

1. 创建多个Webhook URL
2. 在 `.env` 中配置多个URL
3. 修改发送逻辑支持多频道

## 🛡️ 安全建议

1. **保护Webhook URL**: Webhook URL包含敏感信息，不要公开分享
2. **定期更换**: 如果怀疑Webhook泄露，可以重新创建
3. **限制权限**: Webhook只能在指定频道发送消息

## 🚀 使用方法

配置完成后，系统会：

1. **每天中午12点**自动获取新闻
2. **格式化消息**并生成美观的嵌入内容
3. **通过Webhook发送**到您指定的Discord频道
4. **无需机器人在线**，系统独立运行

## 📱 消息格式示例

Webhook发送的消息将包含：
- 🤖 **标题**: 科技新闻简报
- 📊 **摘要**: 今日新闻概览
- 🍎 **苹果动态**: 最新苹果产品新闻
- 🤖 **AI发展**: 人工智能最新进展
- 🧠 **LLM动态**: 大语言模型相关新闻

## 🔍 故障排除

### Q: Webhook没有发送消息
**A:** 检查以下几点：
- Webhook URL是否正确
- 网络连接是否正常
- 查看日志文件 `news_bot.log`

### Q: 消息格式不正确
**A:** 
- 检查Discord是否支持嵌入消息
- 确认频道权限设置

### Q: 如何更改发送时间
**A:** 在 `config.py` 中修改 `SCHEDULE_CONFIG['daily_time']`

---

使用Webhook是最简单高效的方案，您只需要几分钟就能完成配置！
