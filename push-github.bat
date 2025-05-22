@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 设置颜色代码
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "RESET=[0m"

echo %GREEN%开始上传代码到GitHub...%RESET%

:: 检查git是否安装
where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo %RED%错误: 未找到git命令，请确保已安装Git并添加到系统PATH中%RESET%
    pause
    exit /b 1
)

:: 检查是否在git仓库中
git rev-parse --is-inside-work-tree >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo %RED%错误: 当前目录不是git仓库%RESET%
    pause
    exit /b 1
)

:: 获取当前分支名
for /f "tokens=*" %%a in ('git rev-parse --abbrev-ref HEAD') do set "CURRENT_BRANCH=%%a"

:: 显示当前分支
echo %YELLOW%当前分支: %CURRENT_BRANCH%%RESET%

:: 拉取最新代码
echo %GREEN%正在拉取最新代码...%RESET%
git pull origin %CURRENT_BRANCH%
if %ERRORLEVEL% neq 0 (
    echo %RED%拉取代码失败，请检查网络连接或仓库状态%RESET%
    pause
    exit /b 1
)

:: 添加所有更改
echo %GREEN%正在添加更改...%RESET%
git add .

:: 获取提交信息
set /p COMMIT_MSG="更新主程序界面，添加测试功能"

:: 提交更改
echo %GREEN%正在提交更改...%RESET%
git commit -m "%COMMIT_MSG%"
if %ERRORLEVEL% neq 0 (
    echo %RED%提交失败，请检查是否有更改需要提交%RESET%
    pause
    exit /b 1
)

:: 推送到远程仓库
echo %GREEN%正在推送到远程仓库...%RESET%
git push origin %CURRENT_BRANCH%
if %ERRORLEVEL% neq 0 (
    echo %RED%推送失败，请检查网络连接或仓库权限%RESET%
    pause
    exit /b 1
)

echo %GREEN%代码上传成功！%RESET%
echo %YELLOW%分支: %CURRENT_BRANCH%%RESET%
echo %YELLOW%提交信息: %COMMIT_MSG%%RESET%

pause 