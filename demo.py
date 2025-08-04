#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows键鼠录制工具演示脚本
演示如何使用录制工具进行自动化操作
"""

import time
import pyautogui
import json

def demo_basic_usage():
    """演示基本用法"""
    print("=" * 50)
    print("Windows键鼠录制工具演示")
    print("=" * 50)
    
    print("\n1. 启动录制工具:")
    print("   python start.py")
    print("   选择版本 1-3")
    
    print("\n2. 录制操作:")
    print("   - 点击'开始录制'按钮或按F9")
    print("   - 执行您要录制的操作")
    print("   - 再次点击按钮或按F9停止录制")
    
    print("\n3. 回放操作:")
    print("   - 点击'开始回放'按钮或按F10")
    print("   - 程序会倒计时3秒后开始回放")
    print("   - 可以随时按F11紧急停止")
    
    print("\n4. 保存和加载:")
    print("   - 使用'保存录制'保存为JSON文件")
    print("   - 使用'加载录制'从文件加载")
    
    print("\n5. 热键说明:")
    print("   - F9: 开始/停止录制")
    print("   - F10: 开始/停止回放")
    print("   - F11: 紧急停止")

def demo_automation_examples():
    """演示自动化示例"""
    print("\n" + "=" * 50)
    print("自动化操作示例")
    print("=" * 50)
    
    examples = [
        {
            "name": "文件操作自动化",
            "description": "自动打开文件、复制、粘贴等操作",
            "steps": [
                "打开文件管理器",
                "导航到目标文件夹",
                "选择文件",
                "复制文件",
                "粘贴到目标位置"
            ]
        },
        {
            "name": "网页操作自动化",
            "description": "自动填写表单、点击按钮等",
            "steps": [
                "打开浏览器",
                "导航到目标网页",
                "填写表单字段",
                "点击提交按钮",
                "等待页面加载"
            ]
        },
        {
            "name": "软件操作自动化",
            "description": "自动执行软件中的重复操作",
            "steps": [
                "打开目标软件",
                "执行重复性操作",
                "保存结果",
                "关闭软件"
            ]
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['name']}")
        print(f"   描述: {example['description']}")
        print("   步骤:")
        for j, step in enumerate(example['steps'], 1):
            print(f"      {j}. {step}")

def demo_safety_tips():
    """演示安全提示"""
    print("\n" + "=" * 50)
    print("安全使用提示")
    print("=" * 50)
    
    tips = [
        "1. 录制前确保目标窗口位置正确",
        "2. 关闭不必要的程序，避免干扰",
        "3. 测试操作流程，确保可重复执行",
        "4. 准备好紧急停止方法 (F11)",
        "5. 先在安全环境中测试",
        "6. 定期备份重要的录制文件",
        "7. 给录制文件起有意义的名字",
        "8. 注意操作的时间间隔合理性"
    ]
    
    for tip in tips:
        print(f"   {tip}")

def demo_troubleshooting():
    """演示故障排除"""
    print("\n" + "=" * 50)
    print("常见问题解决")
    print("=" * 50)
    
    problems = [
        {
            "problem": "程序无法启动",
            "solution": "检查Python版本和依赖包安装"
        },
        {
            "problem": "录制不准确",
            "solution": "使用高级版或PyQt6版，提供更精确的录制"
        },
        {
            "problem": "回放时位置不对",
            "solution": "确保目标窗口位置与录制时一致"
        },
        {
            "problem": "热键不响应",
            "solution": "检查是否有其他程序占用了热键"
        },
        {
            "problem": "程序崩溃",
            "solution": "使用F11紧急停止，然后重新启动"
        }
    ]
    
    for i, item in enumerate(problems, 1):
        print(f"{i}. 问题: {item['problem']}")
        print(f"   解决: {item['solution']}")
        print()

def main():
    """主函数"""
    demo_basic_usage()
    demo_automation_examples()
    demo_safety_tips()
    demo_troubleshooting()
    
    print("\n" + "=" * 50)
    print("演示完成！")
    print("现在可以开始使用录制工具了。")
    print("=" * 50)

if __name__ == "__main__":
    main() 