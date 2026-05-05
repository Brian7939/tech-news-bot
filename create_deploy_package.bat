@echo off
echo 📦 开始创建部署包...

REM 设置变量
set TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%
set PACKAGE_NAME=tech-news-bot-deploy_%TIMESTAMP%.tar.gz

REM 创建临时目录
if exist temp_deploy rmdir /s /q temp_deploy
mkdir temp_deploy

echo 📋 复制必要文件...

REM 复制核心文件
copy *.py temp_deploy\
copy *.yml temp_deploy\
copy *.yaml temp_deploy\
copy requirements.txt temp_deploy\
copy .env.example temp_deploy\
copy DOCKER_DEPLOYMENT.md temp_deploy\
copy REMOTE_DEPLOYMENT.md temp_deploy\
copy DEPLOY_OPTIONS.md temp_deploy\
copy README.md temp_deploy\

REM 复制配置目录
if exist config xcopy /e /i config temp_deploy\config\

REM 创建部署脚本
echo @echo off > temp_deploy\deploy.bat
echo echo 🚀 开始部署科技新闻简报服务... >> temp_deploy\deploy.bat
echo. >> temp_deploy\deploy.bat
echo REM 检查管理员权限 >> temp_deploy\deploy.bat
echo net session ^>nul 2^>^&1 >> temp_deploy\deploy.bat
echo if %%errorlevel%% neq 0 ( >> temp_deploy\deploy.bat
echo     echo 请以管理员身份运行此脚本 >> temp_deploy\deploy.bat
echo     pause >> temp_deploy\deploy.bat
echo     exit /b 1 >> temp_deploy\deploy.bat
echo ^) >> temp_deploy\deploy.bat
echo. >> temp_deploy\deploy.bat
echo REM 创建应用目录 >> temp_deploy\deploy.bat
echo if not exist "C:\opt\tech-news-bot" mkdir "C:\opt\tech-news-bot" >> temp_deploy\deploy.bat
echo cd /d C:\opt\tech-news-bot >> temp_deploy\deploy.bat
echo. >> temp_deploy\deploy.bat
echo REM 复制文件 >> temp_deploy\deploy.bat
echo xcopy /e /i /y ..\temp_deploy\*.* . >> temp_deploy\deploy.bat
echo. >> temp_deploy\deploy.bat
echo echo ✅ 文件复制完成 >> temp_deploy\deploy.bat
echo echo 📝 请配置环境变量： >> temp_deploy\deploy.bat
echo echo    copy .env.example .env >> temp_deploy\deploy.bat
echo echo    notepad .env >> temp_deploy\deploy.bat
echo. >> temp_deploy\deploy.bat
echo echo 🐳 然后运行Docker部署： >> temp_deploy\deploy.bat
echo echo    docker-compose build >> temp_deploy\deploy.bat
echo echo    docker-compose up -d >> temp_deploy\deploy.bat

REM 创建说明文件
echo 科技新闻简报服务 - Windows部署说明 > temp_deploy\DEPLOY_INSTRUCTIONS.txt
echo. >> temp_deploy\deploy.bat
echo 文件说明： >> temp_deploy\DEPLOY_INSTRUCTIONS.txt
echo - *.py: Python源代码文件 >> temp_deploy\DEPLOY_INSTRUCTIONS.txt
echo - docker-compose.yml: Docker编排配置 >> temp_deploy\DEPLOY_INSTRUCTIONS.txt
echo - Dockerfile: Docker镜像构建配置 >> temp_deploy\DEPLOY_INSTRUCTIONS.txt
echo - requirements.txt: Python依赖列表 >> temp_deploy\DEPLOY_INSTRUCTIONS.txt
echo - .env.example: 环境变量模板 >> temp_deploy\DEPLOY_INSTRUCTIONS.txt
echo - deploy.bat: Windows部署脚本 >> temp_deploy\DEPLOY_INSTRUCTIONS.txt
echo - *.md: 文档文件 >> temp_deploy\DEPLOY_INSTRUCTIONS.txt
echo. >> temp_deploy\DEPLOY_INSTRUCTIONS.txt
echo 部署步骤： >> temp_deploy\DEPLOY_INSTRUCTIONS.txt
echo 1. 将此文件夹复制到Ubuntu服务器 >> temp_deploy\DEPLOY_INSTRUCTIONS.txt
echo 2. 在Ubuntu服务器上运行: sudo bash local_deploy.sh >> temp_deploy\DEPLOY_INSTRUCTIONS.txt
echo 3. 按提示配置环境变量 >> temp_deploy\DEPLOY_INSTRUCTIONS.txt
echo 4. 等待自动部署完成 >> temp_deploy\DEPLOY_INSTRUCTIONS.txt

echo 🗜️ 压缩文件...

REM 使用tar压缩（如果可用）或使用zip
where tar >nul 2>nul
if %errorlevel% equ 0 (
    tar --exclude='__pycache__' --exclude='*.pyc' --exclude='*.log' --exclude='.git' --exclude='test_*.py' --exclude='*_test.py' -czf %PACKAGE_NAME% -C temp_deploy .
    echo ✅ 使用tar压缩完成
) else (
    REM 使用zip作为备选方案
    powershell Compress-Archive -Path temp_deploy\* -DestinationPath %PACKAGE_NAME:.tar.gz=%.zip%
    set PACKAGE_NAME=%PACKAGE_NAME:.tar.gz=%.zip%
    echo ✅ 使用zip压缩完成
)

REM 清理临时目录
rmdir /s /q temp_deploy

echo ✅ 打包完成！
echo 📦 包文件: %PACKAGE_NAME%
echo 📏 文件大小: 
for %%I in (%PACKAGE_NAME%) do echo %%~zI 字节
echo.
echo 📋 下一步操作：
echo 1. 将 %PACKAGE_NAME% 传输到目标Ubuntu服务器
echo 2. 在Ubuntu服务器上解压: tar -xzf tech-news-bot-deploy_*.tar.gz
echo 3. 运行部署脚本: sudo bash local_deploy.sh
echo.
echo 🌐 或参考 REMOTE_DEPLOYMENT.md 进行详细部署

pause
