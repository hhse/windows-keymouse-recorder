import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import time
import threading
import pyautogui
import keyboard
import mouse
from datetime import datetime
import pynput
from pynput import mouse as pynput_mouse, keyboard as pynput_keyboard

class AdvancedKeyMouseRecorder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("高级Windows键鼠录制工具")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # 录制状态变量
        self.is_recording = False
        self.is_playing = False
        self.recorded_actions = []
        self.recording_thread = None
        self.playing_thread = None
        self.start_time = 0
        
        # 热键设置
        self.record_hotkey = "f9"
        self.play_hotkey = "f10"
        self.stop_hotkey = "f11"
        
        # 设置pyautogui安全设置
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.01
        
        self.setup_ui()
        self.setup_hotkeys()
        
    def setup_ui(self):
        # 主标题
        title_label = tk.Label(self.root, text="高级Windows键鼠录制工具", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 状态显示
        self.status_label = tk.Label(self.root, text="状态: 待机", font=("Arial", 12))
        self.status_label.pack(pady=5)
        
        # 热键信息
        hotkey_frame = tk.Frame(self.root)
        hotkey_frame.pack(pady=5)
        
        hotkey_label = tk.Label(hotkey_frame, text="热键控制:", font=("Arial", 10, "bold"))
        hotkey_label.pack(side=tk.LEFT, padx=5)
        
        hotkey_info = tk.Label(hotkey_frame, text=f"F9: 开始/停止录制 | F10: 开始/停止回放 | F11: 紧急停止", 
                              font=("Arial", 9))
        hotkey_info.pack(side=tk.LEFT, padx=5)
        
        # 按钮框架
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        # 第一行按钮
        row1_frame = tk.Frame(button_frame)
        row1_frame.pack(pady=5)
        
        self.record_button = tk.Button(row1_frame, text="开始录制 (F9)", 
                                     command=self.toggle_recording,
                                     bg="#ff6b6b", fg="white", 
                                     font=("Arial", 11), width=15)
        self.record_button.pack(side=tk.LEFT, padx=5)
        
        self.play_button = tk.Button(row1_frame, text="开始回放 (F10)", 
                                   command=self.toggle_playing,
                                   bg="#4ecdc4", fg="white", 
                                   font=("Arial", 11), width=15)
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        # 第二行按钮
        row2_frame = tk.Frame(button_frame)
        row2_frame.pack(pady=5)
        
        save_button = tk.Button(row2_frame, text="保存录制", 
                              command=self.save_recording,
                              bg="#45b7d1", fg="white", 
                              font=("Arial", 11), width=15)
        save_button.pack(side=tk.LEFT, padx=5)
        
        load_button = tk.Button(row2_frame, text="加载录制", 
                              command=self.load_recording,
                              bg="#96ceb4", fg="white", 
                              font=("Arial", 11), width=15)
        load_button.pack(side=tk.LEFT, padx=5)
        
        # 第三行按钮
        row3_frame = tk.Frame(button_frame)
        row3_frame.pack(pady=5)
        
        clear_button = tk.Button(row3_frame, text="清空录制", 
                               command=self.clear_recording,
                               bg="#feca57", fg="white", 
                               font=("Arial", 11), width=15)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        settings_button = tk.Button(row3_frame, text="设置", 
                                  command=self.show_settings,
                                  bg="#a55eea", fg="white", 
                                  font=("Arial", 11), width=15)
        settings_button.pack(side=tk.LEFT, padx=5)
        
        # 统计信息
        stats_frame = tk.Frame(self.root)
        stats_frame.pack(pady=10)
        
        self.stats_label = tk.Label(stats_frame, text="录制统计: 0 个操作", font=("Arial", 10))
        self.stats_label.pack()
        
        # 信息显示区域
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # 录制信息
        info_label = tk.Label(info_frame, text="录制信息:", font=("Arial", 10, "bold"))
        info_label.pack(anchor=tk.W, padx=10)
        
        self.info_text = tk.Text(info_frame, height=10, width=60)
        self.info_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = tk.Scrollbar(self.info_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.info_text.yview)
        
    def setup_hotkeys(self):
        # 设置全局热键
        keyboard.add_hotkey(self.record_hotkey, self.toggle_recording)
        keyboard.add_hotkey(self.play_hotkey, self.toggle_playing)
        keyboard.add_hotkey(self.stop_hotkey, self.emergency_stop)
        
    def emergency_stop(self):
        """紧急停止所有操作"""
        self.is_recording = False
        self.is_playing = False
        self.record_button.config(text="开始录制 (F9)", bg="#ff6b6b")
        self.play_button.config(text="开始回放 (F10)", bg="#4ecdc4")
        self.status_label.config(text="状态: 紧急停止")
        self.info_text.insert(tk.END, "紧急停止所有操作\n")
        
    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
            
    def start_recording(self):
        self.is_recording = True
        self.recorded_actions = []
        self.start_time = time.time()
        self.record_button.config(text="停止录制 (F9)", bg="#ff4757")
        self.status_label.config(text="状态: 录制中...")
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, "开始录制...\n")
        
        # 在新线程中开始录制
        self.recording_thread = threading.Thread(target=self.record_actions)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
    def stop_recording(self):
        self.is_recording = False
        self.record_button.config(text="开始录制 (F9)", bg="#ff6b6b")
        self.status_label.config(text="状态: 录制完成")
        duration = time.time() - self.start_time
        self.info_text.insert(tk.END, f"录制完成，共录制 {len(self.recorded_actions)} 个操作，耗时 {duration:.2f} 秒\n")
        self.update_stats()
        
    def record_actions(self):
        # 使用pynput进行更精确的录制
        with pynput_mouse.Listener(on_click=self.on_mouse_click, on_move=self.on_mouse_move) as mouse_listener:
            with pynput_keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release) as keyboard_listener:
                while self.is_recording:
                    time.sleep(0.001)
                    
    def on_mouse_click(self, x, y, button, pressed):
        if not self.is_recording:
            return False
            
        current_time = time.time() - self.start_time
        action = {
            'type': 'mouse_click',
            'x': x,
            'y': y,
            'button': str(button),
            'pressed': pressed,
            'time': current_time
        }
        
        self.recorded_actions.append(action)
        self.info_text.insert(tk.END, f"鼠标点击: {button} {'按下' if pressed else '释放'} at ({x}, {y})\n")
        self.info_text.see(tk.END)
        self.update_stats()
        
    def on_mouse_move(self, x, y):
        if not self.is_recording:
            return
            
        # 只记录重要的移动（避免过多数据）
        if len(self.recorded_actions) == 0 or \
           (self.recorded_actions[-1]['type'] == 'mouse_move' and 
            abs(self.recorded_actions[-1]['x'] - x) + abs(self.recorded_actions[-1]['y'] - y) < 10):
            return
            
        current_time = time.time() - self.start_time
        action = {
            'type': 'mouse_move',
            'x': x,
            'y': y,
            'time': current_time
        }
        
        self.recorded_actions.append(action)
        
    def on_key_press(self, key):
        if not self.is_recording:
            return True
            
        current_time = time.time() - self.start_time
        action = {
            'type': 'key_press',
            'key': str(key),
            'time': current_time
        }
        
        self.recorded_actions.append(action)
        self.info_text.insert(tk.END, f"按键按下: {key}\n")
        self.info_text.see(tk.END)
        self.update_stats()
        
    def on_key_release(self, key):
        if not self.is_recording:
            return True
            
        current_time = time.time() - self.start_time
        action = {
            'type': 'key_release',
            'key': str(key),
            'time': current_time
        }
        
        self.recorded_actions.append(action)
        
    def toggle_playing(self):
        if not self.is_playing:
            self.start_playing()
        else:
            self.stop_playing()
            
    def start_playing(self):
        if not self.recorded_actions:
            messagebox.showwarning("警告", "没有可回放的操作！")
            return
            
        self.is_playing = True
        self.play_button.config(text="停止回放 (F10)", bg="#ff4757")
        self.status_label.config(text="状态: 回放中...")
        self.info_text.insert(tk.END, "开始回放...\n")
        
        # 在新线程中开始回放
        self.playing_thread = threading.Thread(target=self.play_actions)
        self.playing_thread.daemon = True
        self.playing_thread.start()
        
    def stop_playing(self):
        self.is_playing = False
        self.play_button.config(text="开始回放 (F10)", bg="#4ecdc4")
        self.status_label.config(text="状态: 回放完成")
        self.info_text.insert(tk.END, "回放完成\n")
        
    def play_actions(self):
        if not self.recorded_actions:
            return
            
        # 给用户3秒准备时间
        for i in range(3, 0, -1):
            if not self.is_playing:
                return
            self.info_text.insert(tk.END, f"回放将在 {i} 秒后开始...\n")
            self.info_text.see(tk.END)
            time.sleep(1)
            
        self.info_text.insert(tk.END, "开始回放操作...\n")
        
        last_time = 0
        for i, action in enumerate(self.recorded_actions):
            if not self.is_playing:
                break
                
            try:
                # 计算时间延迟
                if i > 0:
                    delay = action['time'] - last_time
                    if delay > 0:
                        time.sleep(delay)
                last_time = action['time']
                
                if action['type'] == 'mouse_click':
                    if action['pressed']:
                        if 'Button.left' in action['button']:
                            pyautogui.mouseDown(action['x'], action['y'])
                        elif 'Button.right' in action['button']:
                            pyautogui.mouseDown(action['x'], action['y'], button='right')
                    else:
                        if 'Button.left' in action['button']:
                            pyautogui.mouseUp(action['x'], action['y'])
                        elif 'Button.right' in action['button']:
                            pyautogui.mouseUp(action['x'], action['y'], button='right')
                            
                elif action['type'] == 'mouse_move':
                    pyautogui.moveTo(action['x'], action['y'])
                    
                elif action['type'] == 'key_press':
                    key = action['key'].replace("'", "")
                    if key.startswith('Key.'):
                        key = key[4:]  # 移除 'Key.' 前缀
                    pyautogui.keyDown(key)
                    
                elif action['type'] == 'key_release':
                    key = action['key'].replace("'", "")
                    if key.startswith('Key.'):
                        key = key[4:]  # 移除 'Key.' 前缀
                    pyautogui.keyUp(key)
                    
            except Exception as e:
                self.info_text.insert(tk.END, f"回放出错: {str(e)}\n")
                
        self.stop_playing()
        
    def update_stats(self):
        self.stats_label.config(text=f"录制统计: {len(self.recorded_actions)} 个操作")
        
    def save_recording(self):
        if not self.recorded_actions:
            messagebox.showwarning("警告", "没有可保存的录制！")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.recorded_actions, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("成功", f"录制已保存到: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
                
    def load_recording(self):
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.recorded_actions = json.load(f)
                messagebox.showinfo("成功", f"录制已加载: {filename}")
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(tk.END, f"已加载 {len(self.recorded_actions)} 个操作\n")
                self.update_stats()
            except Exception as e:
                messagebox.showerror("错误", f"加载失败: {str(e)}")
                
    def clear_recording(self):
        self.recorded_actions = []
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, "录制已清空\n")
        self.update_stats()
        messagebox.showinfo("成功", "录制已清空")
        
    def show_settings(self):
        # 创建设置窗口
        settings_window = tk.Toplevel(self.root)
        settings_window.title("设置")
        settings_window.geometry("300x200")
        settings_window.resizable(False, False)
        
        # 热键设置
        tk.Label(settings_window, text="热键设置:", font=("Arial", 12, "bold")).pack(pady=10)
        
        tk.Label(settings_window, text="录制热键:").pack()
        record_entry = tk.Entry(settings_window)
        record_entry.insert(0, self.record_hotkey)
        record_entry.pack()
        
        tk.Label(settings_window, text="回放热键:").pack()
        play_entry = tk.Entry(settings_window)
        play_entry.insert(0, self.play_hotkey)
        play_entry.pack()
        
        def save_settings():
            self.record_hotkey = record_entry.get()
            self.play_hotkey = play_entry.get()
            # 重新设置热键
            keyboard.unhook_all()
            self.setup_hotkeys()
            messagebox.showinfo("成功", "设置已保存")
            settings_window.destroy()
            
        save_button = tk.Button(settings_window, text="保存设置", command=save_settings)
        save_button.pack(pady=10)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AdvancedKeyMouseRecorder()
    app.run() 