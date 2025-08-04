@echo off
chcp 65001 >nul
title Git初始化和GitHub上传
echo.
echo ==========================================
echo    Git初始化和GitHub上传脚本
echo ==========================================
echo.

echo 正在初始化Git仓库...
git init

echo.
echo 正在添加所有文件到Git...
git add .

echo.
echo 正在提交初始版本...
git commit -m "🎉 初始版本: 智能Windows键鼠录制工具

✨ 功能特性:
- 🎬 精确录制鼠标键盘操作
- ▶️ 智能回放功能
- 🎨 暗黑主题PyQt6界面
- 🧠 智能功能(自动保存、循环回放)
- 🛡️ 安全机制(F11紧急停止)

🛠️ 技术栈:
- Python + PyQt6 + pyautogui + pynput
- 多线程设计，精确时间控制
- 事件驱动架构，模块化设计

📝 作者: 木木iOS分享
📅 完成时间: 2024年8月4日"

echo.
echo ==========================================
echo    Git仓库初始化完成！
echo ==========================================
echo.
echo 接下来需要手动执行以下步骤:
echo.
echo 1. 在GitHub上创建新仓库
echo 2. 添加远程仓库:
echo    git remote add origin https://github.com/your-username/windows-keymouse-recorder.git
echo.
echo 3. 推送到GitHub:
echo    git branch -M main
echo    git push -u origin main
echo.
echo 4. 可选: 添加GitHub Pages或Wiki
echo.
echo 提示: 请将 'your-username' 替换为您的GitHub用户名
echo.
pause 