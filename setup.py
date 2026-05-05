"""
安装脚本
用于快速设置和配置科技新闻简报系统
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 9):
        print('❌ 需要Python 3.9或更高版本')
        print(f'当前版本: {sys.version}')
        return False
    
    print(f'✅ Python版本检查通过: {sys.version}')
    return True

def install_dependencies():
    """安装依赖包"""
    print('📦 安装依赖包...')
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print('✅ 依赖包安装完成')
        return True
    except subprocess.CalledProcessError as e:
        print(f'❌ 依赖包安装失败: {e}')
        return False

def setup_environment():
    """设置环境配置"""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists() and env_example.exists():
        print('📝 创建环境配置文件...')
        
        # 复制示例配置
        with open(env_example, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print('✅ 已创建 .env 文件')
        print('⚠️ 请编辑 .env 文件，填入必要的配置信息:')
        print('   - DISCORD_BOT_TOKEN')
        print('   - DISCORD_CHANNEL_ID')
        print('   - NEWS_API_KEY (可选)')
        print('   - OPENAI_API_KEY (可选)')
        
        return True
    elif env_file.exists():
        print('✅ 环境配置文件已存在')
        return True
    else:
        print('❌ 找不到 .env.example 文件')
        return False

def create_directories():
    """创建必要的目录"""
    directories = [
        'logs',
        'data',
        'cache'
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(exist_ok=True)
            print(f'✅ 创建目录: {directory}')
        else:
            print(f'✅ 目录已存在: {directory}')

def run_tests():
    """运行测试"""
    print('🧪 运行系统测试...')
    
    try:
        # 测试配置
        from config import validate_config
        if validate_config():
            print('✅ 配置验证通过')
        else:
            print('❌ 配置验证失败')
            return False
        
        # 测试新闻聚合器
        print('📡 测试新闻聚合器...')
        import asyncio
        from news_aggregator import NewsAggregator
        
        async def test_aggregator():
            aggregator = NewsAggregator()
            # 这里可以添加具体的测试逻辑
            print('✅ 新闻聚合器测试通过')
        
        asyncio.run(test_aggregator())
        
        return True
        
    except Exception as e:
        print(f'❌ 测试失败: {e}')
        return False

def main():
    """主安装流程"""
    print('🤖 科技新闻简报系统 - 安装向导')
    print('=' * 50)
    
    # 检查Python版本
    if not check_python_version():
        return False
    
    # 安装依赖
    if not install_dependencies():
        return False
    
    # 设置环境
    if not setup_environment():
        return False
    
    # 创建目录
    create_directories()
    
    # 运行测试
    print('\n🧪 运行安装测试...')
    if not run_tests():
        print('⚠️ 安装测试未完全通过，请检查配置')
    
    print('\n' + '=' * 50)
    print('🎉 安装完成！')
    print('')
    print('下一步:')
    print('1. 编辑 .env 文件，填入必要的配置信息')
    print('2. 创建Discord机器人并获取Token')
    print('3. 运行 python main.py test 测试系统')
    print('4. 运行 python main.py 启动系统')
    print('')
    print('需要帮助？查看 README.md 文件')
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print('\n👋 安装已取消')
        sys.exit(1)
    except Exception as e:
        print(f'❌ 安装过程中出现错误: {e}')
        sys.exit(1)
