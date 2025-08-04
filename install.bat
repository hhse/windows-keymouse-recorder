@echo off
chcp 65001 >nul
title 安装依赖包
echo.
echo ==========================================
echo    正在安装依赖包...
echo ==========================================
echo.

echo 正在安装 PyQt6...
pip install PyQt6

echo.
echo 正在安装 pyautogui...
pip install pyautogui

echo.
echo 正在安装 keyboard...
pip install keyboard

echo.
echo 正在安装 mouse...
pip install mouse

echo.
echo 正在安装 pynput...
pip install pynput

echo.
echo ==========================================
echo    安装完成！
echo ==========================================
echo.
echo 现在可以运行 "启动录制工具.bat" 来启动程序
echo.
pause 