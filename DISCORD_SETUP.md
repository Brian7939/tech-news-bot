# Discord机器人设置指南

本指南将帮助您创建和配置Discord机器人，用于发送科技新闻简报。

## 步骤1: 创建Discord应用

1. 访问 [Discord Developer Portal](https://discord.com/developers/applications)
2. 点击 "New Application" 按钮
3. 输入应用名称（例如："科技新闻机器人"）
4. 点击 "Create"

## 步骤2: 创建机器人

1. 在左侧菜单中点击 "Bot"
2. 点击 "Add Bot" 按钮
3. 确认创建机器人
4. 复制机器人的 **Token**（这个很重要，请妥善保管）

## 步骤3: 配置机器人权限

1. 在机器人设置页面，点击 "Reset Token" 查看完整Token
2. 勾选以下权限：
   - **MESSAGE CONTENT INTENT**: 允许机器人读取消息内容
   - **SERVER MEMBERS INTENT**: 读取服务器成员信息（可选）

## 步骤4: 邀请机器人到服务器

1. 在左侧菜单中点击 "OAuth2" -> "URL Generator"
2. 选择以下权限：
   - **bot**: 基础机器人权限
   - **Send Messages**: 发送消息
   - **Embed Links**: 发送嵌入消息
   - **Read Message History**: 读取消息历史
3. 复制生成的邀请链接
4. 在浏览器中打开链接，选择要添加机器人的服务器
5. 授权机器人加入服务器

## 步骤5: 获取频道ID

1. 在Discord中，右键点击目标频道
2. 选择 "复制频道ID"（如果看不到此选项，需要在Discord设置中启用开发者模式）
3. 或者使用以下方法获取频道ID：
   - 在Discord设置中启用开发者模式
   - 右键点击频道，选择"复制频道ID"

## 步骤6: 配置环境变量

编辑项目根目录下的 `.env` 文件：

```env
# Discord配置
DISCORD_BOT_TOKEN=你的机器人Token
DISCORD_CHANNEL_ID=你的频道ID

# 其他配置...
```

## 步骤7: 测试机器人

1. 运行测试命令：
```bash
python main.py test
```

2. 在Discord中发送 `!help` 测试机器人响应

## 常见问题

### Q: 机器人没有响应
**A:** 检查以下几点：
- Token是否正确
- 机器人是否有发送消息的权限
- 频道ID是否正确

### Q: 找不到频道ID
**A:** 
1. 在Discord用户设置中启用"开发者模式"
2. 右键点击频道，选择"复制频道ID"

### Q: 机器人无法连接
**A:** 
1. 检查网络连接
2. 确认Token没有过期
3. 检查Discord服务器状态

### Q: 权限不足错误
**A:** 
1. 确保机器人有发送消息的权限
2. 检查频道是否限制了机器人发言
3. 确认机器人角色权限设置

## 安全建议

1. **不要分享Token**: Token是机器人的密码，不要分享给任何人
2. **定期更换Token**: 如果怀疑Token泄露，及时重置
3. **限制权限**: 只给机器人必要的权限
4. **使用环境变量**: 不要在代码中硬编码Token

## 高级配置

### 自定义命令前缀
可以在 `discord_bot.py` 中修改命令前缀：

```python
# 将 !news 改为其他前缀
if message.content.startswith('/news'):
```

### 自定义消息格式
可以在 `news_formatter.py` 中自定义消息格式和样式。

### 添加更多功能
可以扩展 `discord_bot.py` 添加更多Discord命令和功能。

---

如果遇到问题，请查看日志文件 `news_bot.log` 获取详细错误信息。
