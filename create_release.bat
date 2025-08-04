@echo off
chcp 65001 >nul
title 创建发布包
echo.
echo ==========================================
echo    创建智能录制工具发布包
echo ==========================================
echo.

REM 创建发布目录
if not exist "release" mkdir release

echo 正在复制文件到发布目录...

REM 复制exe文件
copy "dist\智能录制工具.exe" "release\"

REM 复制启动脚本
copy "dist\启动程序.bat" "release\"

REM 复制说明文档
copy "README.md" "release\"

REM 复制许可证
copy "LICENSE" "release\"

REM 创建使用说明
echo 正在创建使用说明...

(
echo # 智能Windows键鼠录制工具 - 使用说明
echo.
echo ## 🚀 快速开始
echo.
echo ### 系统要求
echo - Windows 10/11
echo - 建议以管理员身份运行（获得最佳体验）
echo.
echo ### 使用方法
echo 1. 双击 `启动程序.bat` 或直接运行 `智能录制工具.exe`
echo 2. 按F9开始录制
echo 3. 执行要录制的操作
echo 4. 再次按F9停止录制
echo 5. 按F10开始回放
echo.
echo ### 热键说明
echo - **F9**: 开始/停止录制
echo - **F10**: 开始/停止回放
echo - **F11**: 紧急停止
echo.
echo ## 🎯 功能特色
echo.
echo - 🎬 精确录制鼠标键盘操作
echo - ▶️ 智能回放功能
echo - 🎨 暗黑主题界面
echo - 🧠 自动保存和循环回放
echo - 🛡️ 安全保护机制
echo.
echo ## ⚠️ 注意事项
echo.
echo 1. 首次运行可能需要几秒钟时间
echo 2. 建议以管理员身份运行以获得最佳体验
echo 3. 某些杀毒软件可能会误报，请添加信任
echo 4. 仅用于合法的自动化操作
echo.
echo ## 🛡️ 安全提醒
echo.
echo - 本工具仅用于合法的自动化操作
echo - 请勿用于游戏作弊或其他违规行为
echo - 使用前请确保符合相关法律法规
echo.
echo ---
echo.
echo **作者**: 木木iOS分享  
echo **版本**: v1.1.0  
echo **技术栈**: Python + PyQt6 + pyautogui + pynput
) > "release\使用说明.txt"

echo ✅ 已创建使用说明: release\使用说明.txt

REM 创建版本信息
echo 正在创建版本信息...

(
echo 智能Windows键鼠录制工具
echo =========================
echo.
echo 版本: v1.1.0
echo 作者: 木木iOS分享
echo 技术栈: Python + PyQt6 + pyautogui + pynput
echo 完成时间: 2024年8月4日
echo.
echo 功能特性:
echo - 🎬 精确录制鼠标键盘操作
echo - ▶️ 智能回放功能
echo - 🎨 暗黑主题界面
echo - 🧠 自动保存和循环回放
echo - 🛡️ 安全保护机制
echo.
echo 文件说明:
echo - 智能录制工具.exe - 主程序
echo - 启动程序.bat - 启动脚本
echo - 使用说明.txt - 详细使用说明
echo - README.md - 项目说明
echo - LICENSE - 许可证文件
) > "release\版本信息.txt"

echo ✅ 已创建版本信息: release\版本信息.txt

echo.
echo ==========================================
echo 🎉 发布包创建完成！
echo ==========================================
echo.
echo 📁 发布目录: release\
echo 📄 主程序: 智能录制工具.exe
echo 📄 启动脚本: 启动程序.bat
echo 📄 使用说明: 使用说明.txt
echo 📄 版本信息: 版本信息.txt
echo.
echo 💡 提示:
echo 1. 可以将release目录打包分发给用户
echo 2. 用户只需双击启动程序.bat即可运行
echo 3. 建议以管理员身份运行以获得最佳体验
echo.
pause 