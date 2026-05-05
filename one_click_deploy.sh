#!/bin/bash

# 科技新闻简报服务 - 一键部署脚本
# 适用于Ubuntu系统，自动完成所有部署步骤

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用sudo运行此脚本"
        echo "用法: sudo $0"
        exit 1
    fi
}

# 检查系统
check_system() {
    log_info "检查系统环境..."
    
    # 检查操作系统
    if ! grep -q "Ubuntu" /etc/os-release; then
        log_error "此脚本仅支持Ubuntu系统"
        exit 1
    fi
    
    log_success "系统检查通过"
}

# 安装Docker
install_docker() {
    log_info "检查并安装Docker..."
    
    if command -v docker &> /dev/null; then
        log_success "Docker已安装"
        docker --version
    else
        log_info "安装Docker..."
        
        # 更新包列表
        apt update
        
        # 安装必要的包
        apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
        
        # 添加Docker官方GPG密钥
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        
        # 添加Docker仓库
        echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # 安装Docker Engine
        apt update
        apt install -y docker-ce docker-ce-cli containerd.io
        
        # 启动Docker服务
        systemctl start docker
        systemctl enable docker
        
        log_success "Docker安装完成"
    fi
}

# 安装Docker Compose
install_docker_compose() {
    log_info "检查并安装Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        log_success "Docker Compose已安装"
        docker-compose --version
    else
        log_info "安装Docker Compose..."
        
        # 下载Docker Compose
        COMPOSE_VERSION="2.20.0"
        curl -L "https://github.com/docker/compose/releases/download/v${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        
        # 设置执行权限
        chmod +x /usr/local/bin/docker-compose
        
        log_success "Docker Compose安装完成"
    fi
}

# 创建应用目录
create_app_directory() {
    log_info "创建应用目录..."
    
    APP_DIR="/opt/tech-news-bot"
    mkdir -p $APP_DIR
    cd $APP_DIR
    
    # 创建日志和数据目录
    mkdir -p logs data
    
    log_success "应用目录创建完成: $APP_DIR"
}

# 下载项目文件
download_project() {
    log_info "下载项目文件..."
    
    # 从GitHub仓库克隆项目
    GIT_REPO_URL="https://github.com/Brian7939/tech-news-bot.git"
    log_info "从GitHub仓库克隆项目..."
    
    if git clone $GIT_REPO_URL .; then
        log_success "项目文件下载完成"
    else
        log_error "从GitHub克隆失败，尝试手动下载..."
        
        # 备选方案：直接下载单个文件
        BASE_URL="https://raw.githubusercontent.com/Brian7939/tech-news-bot/main"
        
        # 下载核心文件
        wget -O Dockerfile "$BASE_URL/Dockerfile"
        wget -O docker-compose.yml "$BASE_URL/docker-compose.yml"
        wget -O main.py "$BASE_URL/main.py"
        wget -O requirements.txt "$BASE_URL/requirements.txt"
        wget -O .env.example "$BASE_URL/.env.example"
        
        # 下载其他必要文件
        wget -O config.py "$BASE_URL/config.py"
        wget -O discord_webhook.py "$BASE_URL/discord_webhook.py"
        wget -O news_aggregator.py "$BASE_URL/news_aggregator.py"
        wget -O simple_translator.py "$BASE_URL/simple_translator.py"
        wget -O health_server.py "$BASE_URL/health_server.py"
        
        log_success "项目文件下载完成（使用备选方案）"
    fi
}

# 配置环境变量
configure_environment() {
    log_info "配置环境变量..."
    
    # 复制环境变量模板
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_success "已创建.env文件"
        else
            log_error ".env.example文件不存在"
            exit 1
        fi
    fi
    
    # 显示需要配置的变量
    log_info "需要配置以下环境变量："
    echo "=================================="
    cat .env.example
    echo "=================================="
    
    # 询问是否现在配置
    read -p "是否现在配置环境变量？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        nano .env
        log_success "环境变量配置完成"
    else
        log_warning "请稍后手动配置 .env 文件"
        log_info "配置命令: nano .env"
    fi
}

# 构建和启动服务
build_and_start() {
    log_info "构建Docker镜像..."
    
    # 构建镜像
    docker-compose build
    
    log_success "Docker镜像构建完成"
    
    log_info "启动服务..."
    
    # 启动服务
    docker-compose up -d
    
    log_success "服务启动完成"
}

# 验证部署
verify_deployment() {
    log_info "验证部署..."
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 检查容器状态
    if docker-compose ps | grep -q "Up"; then
        log_success "容器运行正常"
    else
        log_error "容器启动失败"
        docker-compose logs --tail=20
        exit 1
    fi
    
    # 健康检查
    log_info "执行健康检查..."
    if curl -f http://localhost:8000/health &> /dev/null; then
        log_success "健康检查通过"
        curl -s http://localhost:8000/health | python3 -m json.tool
    else
        log_error "健康检查失败"
        log_info "请检查日志: docker-compose logs"
        exit 1
    fi
}

# 显示部署信息
show_deployment_info() {
    log_success "🎉 部署完成！"
    echo
    echo "=================================="
    echo "科技新闻简报服务部署信息"
    echo "=================================="
    echo "应用目录: /opt/tech-news-bot"
    echo "健康检查: http://localhost:8000/health"
    echo "管理命令:"
    echo "  查看状态: docker-compose ps"
    echo "  查看日志: docker-compose logs -f"
    echo "  重启服务: docker-compose restart"
    echo "  停止服务: docker-compose down"
    echo "=================================="
    echo
    log_info "服务将在每天12:00自动推送新闻简报到Discord"
}

# 主函数
main() {
    echo "=================================="
    echo "科技新闻简报服务 - 一键部署"
    echo "=================================="
    echo
    
    check_root
    check_system
    install_docker
    install_docker_compose
    create_app_directory
    download_project
    configure_environment
    build_and_start
    verify_deployment
    show_deployment_info
}

# 运行主函数
main "$@"
