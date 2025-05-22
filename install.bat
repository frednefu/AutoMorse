@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 正在检查conda环境...

:: 检查是否安装了conda
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误：未找到conda，请先安装Anaconda或Miniconda
    pause
    exit /b 1
)

:: 检查automorse环境是否存在
call conda env list | findstr /C:"automorse" >nul
if %errorlevel% equ 0 (
    echo automorse环境已存在，正在更新...
    call conda activate automorse
    if %errorlevel% neq 0 (
        echo 激活conda环境失败
        pause
        exit /b 1
    )
) else (
    echo 正在创建新的conda环境...
    call conda create -n automorse python=3.9 -y
    if %errorlevel% neq 0 (
        echo 创建conda环境失败
        pause
        exit /b 1
    )
    call conda activate automorse
    if %errorlevel% neq 0 (
        echo 激活conda环境失败
        pause
        exit /b 1
    )
)

:: 安装依赖
echo 正在安装/更新依赖包...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 安装依赖包失败
    pause
    exit /b 1
)

echo 安装/更新完成！
pause 