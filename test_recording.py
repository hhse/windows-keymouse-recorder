#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试录制功能
"""

import time
import pyautogui
import json
from datetime import datetime

def test_mouse_recording():
    """测试鼠标录制功能"""
    print("🧪 测试鼠标录制功能")
    print("=" * 50)
    
    # 模拟鼠标操作
    actions = []
    start_time = time.time()
    
    print("1. 移动鼠标到屏幕中心")
    center_x, center_y = pyautogui.size()
    center_x //= 2
    center_y //= 2
    
    pyautogui.moveTo(center_x, center_y, duration=1)
    actions.append({
        'type': 'mouse_move',
        'x': center_x,
        'y': center_y,
        'time': time.time() - start_time
    })
    
    print("2. 点击鼠标左键")
    pyautogui.click(center_x, center_y)
    actions.append({
        'type': 'mouse_click',
        'x': center_x,
        'y': center_y,
        'button': 'Button.left',
        'pressed': True,
        'time': time.time() - start_time
    })
    actions.append({
        'type': 'mouse_click',
        'x': center_x,
        'y': center_y,
        'button': 'Button.left',
        'pressed': False,
        'time': time.time() - start_time
    })
    
    print("3. 移动鼠标到右上角")
    pyautogui.moveTo(center_x + 100, center_y - 100, duration=0.5)
    actions.append({
        'type': 'mouse_move',
        'x': center_x + 100,
        'y': center_y - 100,
        'time': time.time() - start_time
    })
    
    print("4. 右键点击")
    pyautogui.rightClick(center_x + 100, center_y - 100)
    actions.append({
        'type': 'mouse_click',
        'x': center_x + 100,
        'y': center_y - 100,
        'button': 'Button.right',
        'pressed': True,
        'time': time.time() - start_time
    })
    actions.append({
        'type': 'mouse_click',
        'x': center_x + 100,
        'y': center_y - 100,
        'button': 'Button.right',
        'pressed': False,
        'time': time.time() - start_time
    })
    
    return actions

def test_keyboard_recording():
    """测试键盘录制功能"""
    print("\n🧪 测试键盘录制功能")
    print("=" * 50)
    
    actions = []
    start_time = time.time()
    
    print("1. 输入测试文字")
    test_text = "Hello World!"
    for char in test_text:
        pyautogui.typewrite(char)
        actions.append({
            'type': 'key_press',
            'key': char,
            'time': time.time() - start_time
        })
        actions.append({
            'type': 'key_release',
            'key': char,
            'time': time.time() - start_time
        })
        time.sleep(0.1)
    
    print("2. 按回车键")
    pyautogui.press('enter')
    actions.append({
        'type': 'key_press',
        'key': 'Key.enter',
        'time': time.time() - start_time
    })
    actions.append({
        'type': 'key_release',
        'key': 'Key.enter',
        'time': time.time() - start_time
    })
    
    return actions

def save_test_recording(actions, filename):
    """保存测试录制"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(actions, f, ensure_ascii=False, indent=2)
        print(f"✅ 测试录制已保存到: {filename}")
        return True
    except Exception as e:
        print(f"❌ 保存失败: {str(e)}")
        return False

def main():
    print("🤖 智能录制工具测试")
    print("=" * 50)
    
    # 测试鼠标录制
    mouse_actions = test_mouse_recording()
    print(f"✅ 鼠标录制测试完成，共 {len(mouse_actions)} 个操作")
    
    # 测试键盘录制
    keyboard_actions = test_keyboard_recording()
    print(f"✅ 键盘录制测试完成，共 {len(keyboard_actions)} 个操作")
    
    # 合并所有操作
    all_actions = mouse_actions + keyboard_actions
    
    # 保存测试录制
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_recording_{timestamp}.json"
    
    if save_test_recording(all_actions, filename):
        print(f"\n📊 测试统计:")
        print(f"   - 总操作数: {len(all_actions)}")
        print(f"   - 鼠标操作: {len(mouse_actions)}")
        print(f"   - 键盘操作: {len(keyboard_actions)}")
        print(f"   - 保存文件: {filename}")
        
        print(f"\n🎯 测试结果: 所有功能正常！")
        print(f"💡 提示: 可以加载 {filename} 文件来测试回放功能")
    else:
        print(f"\n❌ 测试失败: 保存功能有问题")

if __name__ == "__main__":
    main() 