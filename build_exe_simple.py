#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版PyInstaller打包脚本
"""

import os
import subprocess
import shutil

def build_exe():
    """打包exe文件"""
    print("🔨 开始打包智能Windows键鼠录制工具...")
    print("=" * 50)
    
    # 创建dist目录
    if not os.path.exists("dist"):
        os.makedirs("dist")
    
    # 简化的PyInstaller命令
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=智能录制工具",
        "--clean",
        "qt_recorder.py"
    ]
    
    print("📦 执行打包命令...")
    print(" ".join(cmd))
    print("-" * 50)
    
    try:
        # 执行打包命令
        result = subprocess.run(cmd, check=True)
        
        if result.returncode == 0:
            print("✅ 打包成功！")
            
            # 复制exe文件到dist目录
            if os.path.exists("dist/智能录制工具.exe"):
                print("📁 输出文件位置: dist/智能录制工具.exe")
                
                # 创建启动脚本
                create_launcher()
                
                print("🎉 打包完成！")
                return True
            else:
                print("❌ 未找到生成的exe文件")
                return False
                
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败！错误代码: {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ 打包过程中出现错误: {str(e)}")
        return False

def create_launcher():
    """创建启动脚本"""
    print("📝 创建启动脚本...")
    
    launcher_content = '''@echo off
chcp 65001 >nul
title 智能Windows键鼠录制工具
echo.
echo ==========================================
echo    智能Windows键鼠录制工具
echo ==========================================
echo.
echo 正在启动程序...
echo.

REM 启动程序
"智能录制工具.exe"

echo.
echo 程序已退出
pause
'''
    
    try:
        with open("dist/启动程序.bat", "w", encoding="utf-8") as f:
            f.write(launcher_content)
        print("✅ 已创建启动脚本: dist/启动程序.bat")
    except Exception as e:
        print(f"❌ 创建启动脚本失败: {str(e)}")

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
        print("\n" + "=" * 50)
        print("🎉 打包完成！")
        print("=" * 50)
        print("📁 输出目录: dist/")
        print("📄 主程序: 智能录制工具.exe")
        print("📄 启动脚本: 启动程序.bat")
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