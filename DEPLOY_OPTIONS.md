# 部署选项说明

## 🚀 部署方式选择

由于安全考虑，我无法直接通过SSH连接到您的服务器，但我为您提供了多种自动化部署方案：

### 方式1：一键部署脚本（推荐）

**在目标Ubuntu服务器上执行：**

```bash
# 下载一键部署脚本
curl -fsSL https://raw.githubusercontent.com/your-repo/tech-news-bot/main/one_click_deploy.sh -o deploy.sh

# 或者手动上传 one_click_deploy.sh 文件

# 执行一键部署
sudo bash deploy.sh
```

**脚本特性：**
- ✅ 自动检查系统环境
- ✅ 自动安装Docker和Docker Compose
- ✅ 自动创建应用目录
- ✅ 自动下载项目文件
- ✅ 引导配置环境变量
- ✅ 自动构建和启动服务
- ✅ 自动验证部署结果

### 方式2：打包部署

**在当前Windows机器上：**

```bash
# 运行打包脚本
./deploy_package.sh

# 生成部署包：tech-news-bot-deploy_YYYYMMDD_HHMMSS.tar.gz
```

**传输到目标服务器：**

```bash
# 使用SCP传输
scp tech-news-bot-deploy_*.tar.gz user@server:/home/user/

# 或使用其他方式（U盘、网络共享等）
```

**在目标服务器上：**

```bash
# 解压并运行
tar -xzf tech-news-bot-deploy_*.tar.gz
cd tech-news-bot-deploy_*
./quick_start.sh
```

### 方式3：Git仓库部署

**如果您有Git仓库：**

```bash
# 在目标服务器上克隆
git clone https://github.com/your-repo/tech-news-bot.git /opt/tech-news-bot
cd /opt/tech-news-bot

# 配置环境变量
cp .env.example .env
nano .env

# 启动服务
docker-compose up -d
```

### 方式4：手动分步部署

参考 `REMOTE_DEPLOYMENT.md` 中的详细步骤。

## 🔧 环境变量配置

无论选择哪种方式，都需要配置以下环境变量：

```bash
# 必须配置
DISCORD_WEBHOOK_URL=https://discordapp.com/api/webhooks/YOUR_WEBHOOK_URL
NEWS_API_KEY=7f118b9d6e8b41db8587f830316be0c3
TAVILY_API_KEY=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
DEEPSEEK_API_KEY=sk-f5bc8b18f7684859aaeba35dd9203d6c

# 可选配置
TIMEZONE=Asia/Shanghai
DEBUG=false
```

## 📋 目标服务器要求

- **系统**: Ubuntu 18.04 或更高版本
- **架构**: x86_64 (推荐)
- **内存**: 至少 512MB
- **存储**: 至少 2GB 可用空间
- **网络**: 可访问Discord API和相关服务

## 🌐 网络配置

如果目标服务器有防火墙：

```bash
# 允许健康检查端口
sudo ufw allow 8000/tcp

# 如果需要外部访问健康检查
sudo ufw allow from 192.168.0.0/16 to any port 8000
```

## 📊 部署验证

部署完成后，执行以下命令验证：

```bash
# 检查服务状态
docker-compose ps

# 健康检查
curl http://localhost:8000/health

# 查看日志
docker-compose logs -f

# 测试新闻推送
python test_translation.py
```

## 🆘 故障排除

### 常见问题

1. **Docker安装失败**
   ```bash
   # 手动安装Docker
   sudo apt update
   sudo apt install -y docker.io docker-compose
   ```

2. **权限问题**
   ```bash
   # 将用户添加到docker组
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. **网络连接问题**
   ```bash
   # 测试网络连接
   curl -I https://discord.com
   curl -I https://newsapi.org
   ```

4. **内存不足**
   ```bash
   # 创建swap文件
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

## 📞 技术支持

如果遇到问题：

1. **检查日志**: `docker-compose logs --tail=50`
2. **验证配置**: `docker-compose config`
3. **检查资源**: `docker stats`
4. **查看文档**: 参考 `DOCKER_DEPLOYMENT.md` 和 `REMOTE_DEPLOYMENT.md`

## 🎯 推荐方案

对于大多数用户，我推荐使用**方式1：一键部署脚本**，因为它：

- 🔄 自动化程度最高
- 🛡️ 包含完整的错误检查
- 📋 提供清晰的指导
- ✅ 自动验证部署结果

只需要在目标服务器上运行一个命令，即可完成整个部署过程！
