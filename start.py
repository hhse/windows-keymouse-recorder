#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

def main():
    print("=" * 50)
    print("Windows键鼠录制工具")
    print("=" * 50)
    print("请选择要启动的版本:")
    print("1. 基础版 (Tkinter界面)")
    print("2. 高级版 (Tkinter界面)")
    print("3. PyQt6版 (现代化界面)")
    print("4. 退出")
    print("-" * 50)
    
    while True:
        try:
            choice = input("请输入选择 (1-4): ").strip()
            
            if choice == "1":
                print("启动基础版...")
                from keymouse_recorder import KeyMouseRecorder
                app = KeyMouseRecorder()
                app.run()
                break
            elif choice == "2":
                print("启动高级版...")
                from advanced_recorder import AdvancedKeyMouseRecorder
                app = AdvancedKeyMouseRecorder()
                app.run()
                break
            elif choice == "3":
                print("启动PyQt6版...")
                from qt_recorder import main as qt_main
                qt_main()
                break
            elif choice == "4":
                print("退出程序")
                break
            else:
                print("无效选择，请输入 1、2、3 或 4")
                
        except KeyboardInterrupt:
            print("\n程序被用户中断")
            break
        except Exception as e:
            print(f"启动出错: {e}")
            break

if __name__ == "__main__":
    main() 