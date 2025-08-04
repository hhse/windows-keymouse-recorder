#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyInstaller打包脚本
将智能Windows键鼠录制工具打包成exe文件
"""

import os
import sys
import subprocess
import shutil
from datetime import datetime

def build_exe():
    """打包exe文件"""
    print("🔨 开始打包智能Windows键鼠录制工具...")
    print("=" * 50)
    
    # 创建dist目录
    if not os.path.exists("dist"):
        os.makedirs("dist")
    
    # 创建build目录
    if not os.path.exists("build"):
        os.makedirs("build")
    
    # PyInstaller命令
    cmd = [
        "pyinstaller",
        "--onefile",                    # 打包成单个exe文件
        "--windowed",                   # 无控制台窗口
        "--name=智能录制工具",           # 程序名称
        "--icon=icon.ico",              # 图标文件（如果有的话）
        "--add-data=README.md;.",       # 包含README文件
        "--add-data=LICENSE;.",         # 包含LICENSE文件
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=pyautogui",
        "--hidden-import=keyboard",
        "--hidden-import=mouse",
        "--hidden-import=pynput",
        "--hidden-import=pynput.mouse",
        "--hidden-import=pynput.keyboard",
        "--hidden-import=threading",
        "--hidden-import=json",
        "--hidden-import=time",
        "--hidden-import=datetime",
        "--clean",                      # 清理临时文件
        "qt_recorder.py"               # 主程序文件
    ]
    
    print("📦 执行打包命令...")
    print(" ".join(cmd))
    print("-" * 50)
    
    try:
        # 执行打包命令
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 打包成功！")
            print("📁 输出文件位置: dist/智能录制工具.exe")
            
            # 复制相关文件到dist目录
            copy_files_to_dist()
            
            print("🎉 打包完成！")
            return True
        else:
            print("❌ 打包失败！")
            print("错误信息:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 打包过程中出现错误: {str(e)}")
        return False

def copy_files_to_dist():
    """复制相关文件到dist目录"""
    print("📋 复制相关文件...")
    
    files_to_copy = [
        "README.md",
        "LICENSE",
        "install.bat",
        "启动智能录制工具.bat"
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            try:
                shutil.copy2(file, "dist/")
                print(f"✅ 已复制: {file}")
            except Exception as e:
                print(f"⚠️ 复制失败: {file} - {str(e)}")

def create_installer_script():
    """创建安装脚本"""
    print("📝 创建安装脚本...")
    
    installer_content = '''@echo off
chcp 65001 >nul
title 智能Windows键鼠录制工具 - 安装程序
echo.
echo ==========================================
echo    智能Windows键鼠录制工具 - 安装程序
echo ==========================================
echo.
echo 正在检查系统环境...
echo.

REM 检查是否以管理员身份运行
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ 已以管理员身份运行
) else (
    echo ⚠️ 建议以管理员身份运行以获得最佳体验
    echo 某些功能可能需要管理员权限
    echo.
)

echo.
echo 正在启动程序...
echo.
echo 提示: 首次运行可能需要几秒钟时间
echo.

REM 启动程序
"智能录制工具.exe"

echo.
echo 程序已退出
pause
'''
    
    try:
        with open("dist/启动程序.bat", "w", encoding="utf-8") as f:
            f.write(installer_content)
        print("✅ 已创建启动脚本: dist/启动程序.bat")
    except Exception as e:
        print(f"❌ 创建启动脚本失败: {str(e)}")

def create_readme_for_exe():
    """为exe版本创建README"""
    print("📝 创建exe版本说明文档...")
    
    readme_content = '''# 智能Windows键鼠录制工具 - exe版本

## 🚀 快速开始

### 系统要求
- Windows 10/11
- 建议以管理员身份运行（获得最佳体验）

### 使用方法
1. 双击 `启动程序.bat` 或直接运行 `智能录制工具.exe`
2. 按F9开始录制
3. 执行要录制的操作
4. 再次按F9停止录制
5. 按F10开始回放

### 热键说明
- **F9**: 开始/停止录制
- **F10**: 开始/停止回放
- **F11**: 紧急停止

## 🎯 功能特色

- 🎬 精确录制鼠标键盘操作
- ▶️ 智能回放功能
- 🎨 暗黑主题界面
- 🧠 自动保存和循环回放
- 🛡️ 安全保护机制

## 📁 文件说明

- `智能录制工具.exe` - 主程序
- `启动程序.bat` - 启动脚本
- `README.md` - 详细说明
- `LICENSE` - 许可证文件

## ⚠️ 注意事项

1. 首次运行可能需要几秒钟时间
2. 建议以管理员身份运行以获得最佳体验
3. 某些杀毒软件可能会误报，请添加信任
4. 仅用于合法的自动化操作

## 🛡️ 安全提醒

- 本工具仅用于合法的自动化操作
- 请勿用于游戏作弊或其他违规行为
- 使用前请确保符合相关法律法规

---

**作者**: 木木iOS分享  
**版本**: v1.1.0  
**技术栈**: Python + PyQt6 + pyautogui + pynput
'''
    
    try:
        with open("dist/README_exe.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
        print("✅ 已创建exe版本说明: dist/README_exe.md")
    except Exception as e:
        print(f"❌ 创建说明文档失败: {str(e)}")

def main():
    """主函数"""
    print("🤖 智能Windows键鼠录制工具 - exe打包程序")
    print("=" * 50)
    
    # 检查必要文件
    if not os.path.exists("qt_recorder.py"):
        print("❌ 错误: 找不到主程序文件 qt_recorder.py")
        return False
    
    # 开始打包
    if build_exe():
        # 创建安装脚本
        create_installer_script()
        
        # 创建说明文档
        create_readme_for_exe()
        
        print("\n" + "=" * 50)
        print("🎉 打包完成！")
        print("=" * 50)
        print("📁 输出目录: dist/")
        print("📄 主程序: 智能录制工具.exe")
        print("📄 启动脚本: 启动程序.bat")
        print("📄 说明文档: README_exe.md")
        print("\n💡 提示:")
        print("1. 可以将dist目录打包分发给用户")
        print("2. 用户只需双击启动程序.bat即可运行")
        print("3. 建议以管理员身份运行以获得最佳体验")
        
        return True
    else:
        print("\n❌ 打包失败，请检查错误信息")
        return False

if __name__ == "__main__":
    main() 