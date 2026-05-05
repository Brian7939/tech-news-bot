#!/bin/bash

# 科技新闻简报服务 - 部署打包脚本
# 用于将项目文件打包以便传输到远程服务器

echo "📦 开始打包科技新闻简报服务..."

# 设置变量
PACKAGE_NAME="tech-news-bot-deploy"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FULL_PACKAGE_NAME="${PACKAGE_NAME}_${TIMESTAMP}.tar.gz"

# 创建临时目录
TEMP_DIR="./temp_deploy"
rm -rf $TEMP_DIR
mkdir -p $TEMP_DIR

echo "📋 复制必要文件..."

# 复制核心文件
cp -r *.py $TEMP_DIR/
cp -r *.yml $TEMP_DIR/
cp -r *.yaml $TEMP_DIR/
cp requirements.txt $TEMP_DIR/
cp .env.example $TEMP_DIR/
cp DOCKER_DEPLOYMENT.md $TEMP_DIR/
cp REMOTE_DEPLOYMENT.md $TEMP_DIR/
cp README.md $TEMP_DIR/

# 复制配置文件
cp -r config $TEMP_DIR/ 2>/dev/null || echo "⚠️ config目录不存在，跳过"

# 创建部署脚本
cat > $TEMP_DIR/deploy.sh << 'EOF'
#!/bin/bash

# 远程部署脚本
echo "🚀 开始部署科技新闻简报服务..."

# 检查权限
if [ "$EUID" -ne 0 ]; then
    echo "请使用sudo运行此脚本"
    exit 1
fi

# 创建应用目录
APP_DIR="/opt/tech-news-bot"
mkdir -p $APP_DIR

# 复制文件
cp -r * $APP_DIR/
cd $APP_DIR

# 设置权限
chown -R $SUDO_USER:$SUDO_USER $APP_DIR
chmod +x *.py

echo "✅ 文件复制完成"
echo "📝 请配置环境变量："
echo "   cd $APP_DIR"
echo "   cp .env.example .env"
echo "   nano .env"
echo ""
echo "🐳 然后运行Docker部署："
echo "   docker-compose build"
echo "   docker-compose up -d"
echo ""
echo "🏥 验证部署："
echo "   curl http://localhost:8000/health"
EOF

chmod +x $TEMP_DIR/deploy.sh

# 创建快速启动脚本
cat > $TEMP_DIR/quick_start.sh << 'EOF'
#!/bin/bash

# 快速启动脚本
echo "⚡ 快速启动科技新闻简报服务..."

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 检查环境变量
if [ ! -f ".env" ]; then
    echo "📝 配置环境变量..."
    cp .env.example .env
    echo "请编辑 .env 文件配置您的API密钥"
    nano .env
    read -p "配置完成后按回车继续..."
fi

# 启动服务
echo "🐳 构建并启动服务..."
docker-compose build
docker-compose up -d

# 等待启动
echo "⏳ 等待服务启动..."
sleep 15

# 验证部署
if curl -f http://localhost:8000/health &> /dev/null; then
    echo "✅ 服务启动成功！"
    echo "📊 健康检查: curl http://localhost:8000/health"
    echo "📝 查看日志: docker-compose logs -f"
else
    echo "❌ 服务启动失败，请检查日志："
    docker-compose logs --tail=20
fi
EOF

chmod +x $TEMP_DIR/quick_start.sh

# 创建说明文件
cat > $TEMP_DIR/DEPLOY_INSTRUCTIONS.txt << 'EOF'
科技新闻简报服务 - 部署说明
================================

文件说明：
- *.py: Python源代码文件
- docker-compose.yml: Docker编排配置
- Dockerfile: Docker镜像构建配置
- requirements.txt: Python依赖列表
- .env.example: 环境变量模板
- deploy.sh: 系统级部署脚本（需要sudo）
- quick_start.sh: 快速启动脚本
- *.md: 文档文件

部署步骤：

方式1：快速部署（推荐）
----------------------
1. 解压文件到目标目录
2. 运行: ./quick_start.sh
3. 按提示配置环境变量
4. 等待自动部署完成

方式2：手动部署
--------------
1. 解压文件: tar -xzf tech-news-bot-deploy_*.tar.gz
2. 进入目录: cd tech-news-bot-deploy_*
3. 配置环境: cp .env.example .env && nano .env
4. 安装Docker（如果未安装）
5. 构建服务: docker-compose build
6. 启动服务: docker-compose up -d

环境变量配置：
--------------
必须配置的变量：
- DISCORD_WEBHOOK_URL: Discord Webhook地址
- NEWS_API_KEY: NewsAPI密钥
- TAVILY_API_KEY: Tavily API密钥  
- DEEPSEEK_API_KEY: DeepSeek API密钥

可选配置：
- TIMEZONE: 时区（默认Asia/Shanghai）
- DEBUG: 调试模式（默认false）

验证部署：
--------
健康检查: curl http://localhost:8000/health
查看日志: docker-compose logs -f
重启服务: docker-compose restart

技术支持：
--------
详细文档请参考：
- DOCKER_DEPLOYMENT.md: Docker部署详细指南
- REMOTE_DEPLOYMENT.md: 远程部署指南
EOF

echo "🗜️ 压缩文件..."

# 排除不必要的文件
tar --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='*.log' \
    --exclude='.git' \
    --exclude='test_*.py' \
    --exclude='*_test.py' \
    --exclude='temp_deploy' \
    -czf $FULL_PACKAGE_NAME \
    -C $TEMP_DIR \
    .

# 清理临时目录
rm -rf $TEMP_DIR

echo "✅ 打包完成！"
echo "📦 包文件: $FULL_PACKAGE_NAME"
echo "📏 文件大小: $(du -h $FULL_PACKAGE_NAME | cut -f1)"
echo ""
echo "📋 下一步操作："
echo "1. 将 $FULL_PACKAGE_NAME 传输到目标服务器"
echo "2. 在目标服务器上解压: tar -xzf $FULL_PACKAGE_NAME"
echo "3. 运行部署脚本: ./quick_start.sh"
echo ""
echo "🌐 或参考 REMOTE_DEPLOYMENT.md 进行详细部署"
