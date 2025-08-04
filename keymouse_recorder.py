import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import time
import threading
import pyautogui
import keyboard
import mouse
from datetime import datetime

class KeyMouseRecorder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Windows键鼠录制工具")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # 录制状态变量
        self.is_recording = False
        self.is_playing = False
        self.recorded_actions = []
        self.recording_thread = None
        self.playing_thread = None
        
        # 设置pyautogui安全设置
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.01
        
        self.setup_ui()
        
    def setup_ui(self):
        # 主标题
        title_label = tk.Label(self.root, text="Windows键鼠录制工具", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 状态显示
        self.status_label = tk.Label(self.root, text="状态: 待机", font=("Arial", 12))
        self.status_label.pack(pady=5)
        
        # 按钮框架
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        # 录制按钮
        self.record_button = tk.Button(button_frame, text="开始录制", 
                                     command=self.toggle_recording,
                                     bg="#ff6b6b", fg="white", 
                                     font=("Arial", 12), width=15)
        self.record_button.pack(pady=5)
        
        # 回放按钮
        self.play_button = tk.Button(button_frame, text="开始回放", 
                                   command=self.toggle_playing,
                                   bg="#4ecdc4", fg="white", 
                                   font=("Arial", 12), width=15)
        self.play_button.pack(pady=5)
        
        # 保存按钮
        save_button = tk.Button(button_frame, text="保存录制", 
                              command=self.save_recording,
                              bg="#45b7d1", fg="white", 
                              font=("Arial", 12), width=15)
        save_button.pack(pady=5)
        
        # 加载按钮
        load_button = tk.Button(button_frame, text="加载录制", 
                              command=self.load_recording,
                              bg="#96ceb4", fg="white", 
                              font=("Arial", 12), width=15)
        load_button.pack(pady=5)
        
        # 清空按钮
        clear_button = tk.Button(button_frame, text="清空录制", 
                               command=self.clear_recording,
                               bg="#feca57", fg="white", 
                               font=("Arial", 12), width=15)
        clear_button.pack(pady=5)
        
        # 信息显示区域
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=20, fill=tk.BOTH, expand=True)
        
        # 录制信息
        info_label = tk.Label(info_frame, text="录制信息:", font=("Arial", 10, "bold"))
        info_label.pack(anchor=tk.W, padx=10)
        
        self.info_text = tk.Text(info_frame, height=8, width=50)
        self.info_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = tk.Scrollbar(self.info_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.info_text.yview)
        
    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
            
    def start_recording(self):
        self.is_recording = True
        self.recorded_actions = []
        self.record_button.config(text="停止录制", bg="#ff4757")
        self.status_label.config(text="状态: 录制中...")
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, "开始录制...\n")
        
        # 在新线程中开始录制
        self.recording_thread = threading.Thread(target=self.record_actions)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
    def stop_recording(self):
        self.is_recording = False
        self.record_button.config(text="开始录制", bg="#ff6b6b")
        self.status_label.config(text="状态: 录制完成")
        self.info_text.insert(tk.END, f"录制完成，共录制 {len(self.recorded_actions)} 个操作\n")
        
    def record_actions(self):
        start_time = time.time()
        
        # 监听鼠标事件
        mouse.hook(self.on_mouse_event)
        # 监听键盘事件
        keyboard.hook(self.on_keyboard_event)
        
        while self.is_recording:
            time.sleep(0.01)
            
        # 停止监听
        mouse.unhook_all()
        keyboard.unhook_all()
        
    def on_mouse_event(self, event):
        if not self.is_recording:
            return
            
        current_time = time.time()
        action = {
            'type': 'mouse',
            'event': event.name,
            'time': current_time,
            'position': pyautogui.position()
        }
        
        if hasattr(event, 'button'):
            action['button'] = event.button
            
        self.recorded_actions.append(action)
        self.info_text.insert(tk.END, f"鼠标事件: {event.name} at {action['position']}\n")
        self.info_text.see(tk.END)
        
    def on_keyboard_event(self, event):
        if not self.is_recording:
            return
            
        current_time = time.time()
        action = {
            'type': 'keyboard',
            'event': event.name,
            'key': event.name,
            'time': current_time
        }
        
        self.recorded_actions.append(action)
        self.info_text.insert(tk.END, f"键盘事件: {event.name}\n")
        self.info_text.see(tk.END)
        
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
        self.play_button.config(text="停止回放", bg="#ff4757")
        self.status_label.config(text="状态: 回放中...")
        self.info_text.insert(tk.END, "开始回放...\n")
        
        # 在新线程中开始回放
        self.playing_thread = threading.Thread(target=self.play_actions)
        self.playing_thread.daemon = True
        self.playing_thread.start()
        
    def stop_playing(self):
        self.is_playing = False
        self.play_button.config(text="开始回放", bg="#4ecdc4")
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
        
        for i, action in enumerate(self.recorded_actions):
            if not self.is_playing:
                break
                
            try:
                if action['type'] == 'mouse':
                    if action['event'] == 'click':
                        pyautogui.click(action['position'])
                    elif action['event'] == 'move':
                        pyautogui.moveTo(action['position'])
                    elif action['event'] == 'right':
                        pyautogui.rightClick(action['position'])
                    elif action['event'] == 'double':
                        pyautogui.doubleClick(action['position'])
                        
                elif action['type'] == 'keyboard':
                    if action['event'] == 'down':
                        pyautogui.keyDown(action['key'])
                    elif action['event'] == 'up':
                        pyautogui.keyUp(action['key'])
                        
                # 添加小延迟
                time.sleep(0.05)
                
            except Exception as e:
                self.info_text.insert(tk.END, f"回放出错: {str(e)}\n")
                
        self.stop_playing()
        
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
            except Exception as e:
                messagebox.showerror("错误", f"加载失败: {str(e)}")
                
    def clear_recording(self):
        self.recorded_actions = []
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, "录制已清空\n")
        messagebox.showinfo("成功", "录制已清空")
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = KeyMouseRecorder()
    app.run() 