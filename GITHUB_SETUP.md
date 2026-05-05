# GitHub仓库设置指南

## 🐙 创建GitHub仓库

### 方法1：通过GitHub网页创建（推荐）

1. **登录GitHub**
   - 访问 https://github.com
   - 使用您的GitHub账号登录

2. **创建新仓库**
   - 点击右上角的 "+" 号
   - 选择 "New repository"

3. **配置仓库信息**
   ```
   Repository name: tech-news-bot
   Description: 科技新闻简报系统 - 自动推送苹果、AI、LLM新闻到Discord
   Visibility: Private（私有）或 Public（公开）
   Don't initialize with README（因为我们已有文件）
   ```

4. **创建仓库**
   - 点击 "Create repository"

### 方法2：使用GitHub CLI

```bash
# 安装GitHub CLI（如果未安装）
# Windows: winget install GitHub.cli
# Ubuntu: sudo apt install gh

# 登录GitHub
gh auth login

# 创建仓库
gh repo create tech-news-bot --private --description "科技新闻简报系统"
```

## 📤 推送代码到GitHub

### 在Windows项目目录执行：

```bash
# 初始化Git仓库
git init

# 添加所有文件
git add .

# 提交代码
git commit -m "Initial commit: 科技新闻简报系统"

# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/tech-news-bot.git

# 推送到GitHub
git push -u origin main
```

### 替换YOUR_USERNAME
将 `YOUR_USERNAME` 替换为您的GitHub用户名。

## 🔗 更新部署脚本

创建仓库后，您的仓库URL将是：
```
https://github.com/YOUR_USERNAME/tech-news-bot.git
```

然后在Ubuntu服务器上使用：
```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/tech-news-bot/main/one_click_deploy.sh | sudo bash
```

## 📋 完整部署流程

1. **创建GitHub仓库**
2. **推送代码**
3. **在Ubuntu服务器执行**：
   ```bash
   curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/tech-news-bot/main/one_click_deploy.sh | sudo bash
   ```

## 🎯 仓库URL示例

假设您的GitHub用户名是 `brian7939`，那么：
- 仓库URL: `https://github.com/brian7939/tech-news-bot.git`
- 原始文件URL: `https://raw.githubusercontent.com/brian7939/tech-news-bot/main/`

## 📝 更新部署脚本中的URL

创建仓库后，我需要更新 `one_click_deploy.sh` 中的默认URL。

## 🔒 私有仓库注意事项

如果创建私有仓库：
- 确保Ubuntu服务器有访问权限
- 可能需要配置GitHub Personal Access Token

## 🚀 验证部署

部署完成后验证：
```bash
# 检查服务状态
docker-compose ps

# 健康检查
curl http://localhost:8000/health

# 查看日志
docker-compose logs -f
```
