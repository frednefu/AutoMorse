@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion



echo 正在启动AutoMorse...

:: 激活conda环境
call conda activate automorse
if %errorlevel% neq 0 (
    echo 错误：激活conda环境失败
    pause
    exit /b 1
)

:: 启动主程序
python src/main.py
if %errorlevel% neq 0 (
    echo 程序运行出错
    pause
    exit /b 1
) 