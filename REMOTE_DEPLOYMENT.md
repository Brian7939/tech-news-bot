# 远程部署指南

## 🌐 在内网Ubuntu小主机上部署科技新闻简报服务

本指南帮助您将项目部署到内网的另一台Ubuntu服务器上。

## 📋 部署准备

### 1. 确认目标服务器信息

```bash
# 在目标Ubuntu服务器上执行以下命令确认环境
uname -a                    # 确认系统架构（应该是x86_64）
lsb_release -a              # 确认Ubuntu版本
docker --version             # 确认Docker是否已安装
```

### 2. 准备传输文件

在当前Windows机器上，将项目文件打包：

```bash
# 创建部署包
tar -czf tech-news-bot-deploy.tar.gz \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.log' \
    --exclude='.env' \
    --exclude='test_*.py' \
    --exclude='*_test.py' \
    .

# 验证打包内容
tar -tzf tech-news-bot-deploy.tar.gz | head -20
```

## 🚀 部署方式选择

### 方式1：SCP传输（推荐）

如果目标服务器可以通过SSH访问：

```bash
# 传输部署包到目标服务器
scp tech-news-bot-deploy.tar.gz user@target-server:/home/user/

# SSH登录到目标服务器
ssh user@target-server

# 在目标服务器上执行以下命令
cd /home/user
tar -xzf tech-news-bot-deploy.tar.gz
sudo mkdir -p /opt/tech-news-bot
sudo cp -r * /opt/tech-news-bot/
sudo chown -R $USER:$USER /opt/tech-news-bot
cd /opt/tech-news-bot
```

### 方式2：U盘/移动存储传输

如果目标服务器无法通过网络访问：

```bash
# 1. 在Windows上：
# 将tech-news-bot-deploy.tar.gz复制到U盘

# 2. 在Ubuntu服务器上：
sudo mkdir -p /opt/tech-news-bot
cd /opt/tech-news-bot
# 从U盘复制并解压文件
sudo cp /media/usb/tech-news-bot-deploy.tar.gz .
tar -xzf tech-news-bot-deploy.tar.gz
sudo chown -R $USER:$USER .
```

### 方式3：Git仓库传输

如果目标服务器可以访问Git仓库：

```bash
# 在目标服务器上：
git clone <your-repo-url> /opt/tech-news-bot
cd /opt/tech-news-bot
```

## 🔧 目标服务器配置

### 1. 安装Docker（如果未安装）

```bash
# 更新包列表
sudo apt update

# 安装Docker
sudo apt install -y docker.io docker-compose

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 将用户添加到docker组
sudo usermod -aG docker $USER

# 重新登录以使权限生效
newgrp docker

# 验证安装
docker --version
docker-compose --version
```

### 2. 配置环境变量

```bash
cd /opt/tech-news-bot

# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
nano .env
```

**必须配置的变量：**

```bash
# Discord Webhook URL（从Discord获取）
DISCORD_WEBHOOK_URL=https://discordapp.com/api/webhooks/YOUR_WEBHOOK_URL

# API密钥
NEWS_API_KEY=7f118b9d6e8b41db8587f830316be0c3
TAVILY_API_KEY=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
DEEPSEEK_API_KEY=sk-f5bc8b18f7684859aaeba35dd9203d6c

# 时区设置
TIMEZONE=Asia/Shanghai
DEBUG=false
```

### 3. 创建必要目录

```bash
# 创建日志和数据目录
mkdir -p logs data

# 设置权限
chmod 755 logs data
```

## 🚀 启动服务

### 1. 构建和启动

```bash
cd /opt/tech-news-bot

# 构建Docker镜像
docker-compose build

# 启动服务（后台运行）
docker-compose up -d

# 查看启动日志
docker-compose logs -f
```

### 2. 验证部署

```bash
# 检查容器状态
docker-compose ps

# 检查健康状态
curl http://localhost:8000/health

# 预期响应：
{
  "status": "healthy",
  "timestamp": "2026-05-05T18:27:00Z",
  "version": "1.0.0",
  "services": {
    "discord_webhook": true,
    "news_api": true,
    "tavily_api": true,
    "deepseek_api": true
  }
}
```

## 📊 监控和管理

### 1. 日常管理

```bash
# 查看服务状态
docker-compose ps

# 查看实时日志
docker-compose logs -f tech-news-bot

# 重启服务
docker-compose restart

# 停止服务
docker-compose down
```

### 2. 更新部署

```bash
# 方式1：重新传输文件
# 在Windows上重新打包并传输
# 然后在Ubuntu上：
cd /opt/tech-news-bot
docker-compose down
# 解压新文件覆盖
docker-compose build --no-cache
docker-compose up -d

# 方式2：使用Git（推荐）
cd /opt/tech-news-bot
git pull
docker-compose build
docker-compose up -d
```

### 3. 定期维护

```bash
# 清理Docker资源
docker system prune -f

# 查看磁盘使用
df -h

# 查看容器资源使用
docker stats tech-news-bot
```

## 🔧 网络配置

### 1. 防火墙设置

如果Ubuntu服务器启用了防火墙：

```bash
# 允许Docker通信
sudo ufw allow 8000/tcp  # 健康检查端口

# 如果需要外部访问健康检查
sudo ufw allow from 192.168.0.0/16 to any port 8000
```

### 2. 内网访问测试

从同一内网的其他机器测试：

```bash
# 替换为实际IP地址
curl http://192.168.1.100:8000/health
```

## 🚨 故障排除

### 常见问题及解决方案

1. **Docker构建失败**
   ```bash
   # 检查Docker服务状态
   sudo systemctl status docker
   
   # 检查磁盘空间
   df -h
   
   # 清理Docker缓存
   docker system prune -a
   ```

2. **容器启动失败**
   ```bash
   # 查看详细错误
   docker-compose logs tech-news-bot
   
   # 检查环境变量
   docker-compose config
   ```

3. **API连接问题**
   ```bash
   # 测试网络连接
   docker-compose exec tech-news-bot curl -I https://api.discord.com
   docker-compose exec tech-news-bot curl -I https://newsapi.org
   ```

4. **权限问题**
   ```bash
   # 修复文件权限
   sudo chown -R $USER:$USER /opt/tech-news-bot
   chmod +x /opt/tech-news-bot/*.py
   ```

## 📱 移动端管理

### 使用手机管理（通过SSH）

```bash
# 在手机上安装Termius或类似SSH客户端
# 连接到服务器
ssh user@target-server

# 常用命令
docker-compose ps
docker-compose logs --tail=50
curl http://localhost:8000/health
```

## 🔄 自动化脚本

创建启动脚本 `start-service.sh`：

```bash
#!/bin/bash
cd /opt/tech-news-bot

echo "🔄 启动科技新闻简报服务..."

# 检查Docker状态
if ! systemctl is-active --quiet docker; then
    echo "启动Docker服务..."
    sudo systemctl start docker
fi

# 构建并启动
docker-compose build
docker-compose up -d

# 等待启动
sleep 10

# 检查健康状态
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 服务启动成功！"
else
    echo "❌ 服务启动失败，请检查日志"
    docker-compose logs --tail=20
fi
```

使用方法：
```bash
chmod +x start-service.sh
./start-service.sh
```

## 📞 支持

部署完成后，您可以通过以下方式验证服务：

1. **健康检查**: `curl http://localhost:8000/health`
2. **Discord接收**: 检查是否收到测试消息
3. **日志监控**: `docker-compose logs -f`

如有问题，请检查：
- 网络连接
- API密钥配置
- Docker服务状态
- 系统资源使用
