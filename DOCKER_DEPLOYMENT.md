# Docker部署指南

## 🐳 使用Docker部署科技新闻简报服务

本指南将帮助您在Ubuntu Server上使用Docker部署科技新闻简报服务。

## 📋 前置要求

### 1. 安装Docker和Docker Compose

```bash
# 更新包列表
sudo apt update

# 安装必要的包
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# 添加Docker官方GPG密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加Docker仓库
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 将用户添加到docker组
sudo usermod -aG docker $USER

# 重新登录以使组权限生效
newgrp docker
```

### 2. 验证安装

```bash
docker --version
docker-compose --version
```

## 🚀 部署步骤

### 1. 准备项目文件

将项目文件复制到您的Ubuntu服务器：

```bash
# 创建项目目录
mkdir -p /opt/tech-news-bot
cd /opt/tech-news-bot

# 复制项目文件（使用scp或git）
# 方式1: 使用scp
scp -r /path/to/project/* user@server:/opt/tech-news-bot/

# 方式2: 使用git（如果项目在git仓库中）
git clone <your-repo-url> .
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
cp .env.example .env
nano .env
```

配置以下关键变量：

```bash
# Discord配置（二选一）
DISCORD_WEBHOOK_URL=https://discordapp.com/api/webhooks/YOUR_WEBHOOK_URL

# API配置
NEWS_API_KEY=your_newsapi_key
TAVILY_API_KEY=your_tavily_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key

# 时区设置
TIMEZONE=Asia/Shanghai
```

### 3. 构建和启动服务

```bash
# 构建Docker镜像
docker-compose build

# 启动服务（后台运行）
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 4. 验证部署

```bash
# 检查容器状态
docker-compose ps

# 检查健康状态
curl http://localhost:8000/health

# 查看实时日志
docker-compose logs -f tech-news-bot
```

## 🛠️ 管理命令

### 启动服务
```bash
docker-compose up -d
```

### 停止服务
```bash
docker-compose down
```

### 重启服务
```bash
docker-compose restart
```

### 查看日志
```bash
# 实时日志
docker-compose logs -f

# 最近100行日志
docker-compose logs --tail=100
```

### 更新服务
```bash
# 拉取最新代码
git pull

# 重新构建镜像
docker-compose build --no-cache

# 重启服务
docker-compose up -d
```

## 📊 监控和维护

### 1. 健康检查

```bash
# 检查服务状态
curl http://localhost:8000/health

# 预期响应
{
  "status": "healthy",
  "timestamp": "2026-05-05T18:23:00Z",
  "version": "1.0.0",
  "services": {
    "discord_webhook": true,
    "news_api": true,
    "tavily_api": true,
    "deepseek_api": true
  }
}
```

### 2. 日志管理

日志文件会持久化到 `./logs` 目录：

```bash
# 查看应用日志
tail -f logs/news_bot.log

# 清理旧日志（保留最近7天）
find logs/ -name "*.log" -mtime +7 -delete
```

### 3. 资源监控

```bash
# 查看容器资源使用情况
docker stats tech-news-bot

# 查看磁盘使用情况
df -h
```

## 🔧 故障排除

### 常见问题

1. **容器启动失败**
   ```bash
   # 查看详细错误信息
   docker-compose logs tech-news-bot
   
   # 检查环境变量配置
   docker-compose config
   ```

2. **API密钥错误**
   ```bash
   # 验证环境变量
   docker-compose exec tech-news-bot env | grep API
   ```

3. **网络连接问题**
   ```bash
   # 测试网络连接
   docker-compose exec tech-news-bot curl -I https://api.discord.com
   ```

4. **内存不足**
   ```bash
   # 增加swap空间
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

### 调试模式

启用调试模式：

```bash
# 修改.env文件
DEBUG=true

# 重启服务
docker-compose restart
```

## 📈 性能优化

### 1. 资源限制

在 `docker-compose.yml` 中调整资源限制：

```yaml
deploy:
  resources:
    limits:
      memory: 1G      # 根据实际内存调整
      cpus: '1.0'     # 根据CPU核心数调整
```

### 2. 自动重启

配置自动重启策略：

```yaml
restart: unless-stopped
```

### 3. 日志轮转

配置日志轮转：

```bash
# 创建logrotate配置
sudo nano /etc/logrotate.d/tech-news-bot

# 内容：
/opt/tech-news-bot/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 app app
}
```

## 🔒 安全建议

1. **保护环境变量文件**
   ```bash
   chmod 600 .env
   ```

2. **使用非root用户运行**
   ```bash
   # Dockerfile中已配置非root用户
   ```

3. **定期更新**
   ```bash
   # 定期更新Docker镜像
   docker-compose pull
   docker-compose up -d
   ```

## 📞 支持

如果遇到问题，请检查：

1. Docker和Docker Compose版本
2. 环境变量配置
3. 网络连接
4. 系统资源使用情况

更多帮助请查看项目文档或提交Issue。
