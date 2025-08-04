import sys
import json
import time
import threading
import pyautogui
import keyboard
import mouse
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                             QFileDialog, QMessageBox, QFrame, QProgressBar,
                             QSpinBox, QGroupBox, QCheckBox, QTabWidget, QSlider)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QPixmap

class RecordingThread(QThread):
    """录制线程"""
    action_recorded = pyqtSignal(dict)
    status_updated = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.start_time = 0
        self.last_mouse_pos = None
        
    def run(self):
        self.is_recording = True
        self.start_time = time.time()
        self.last_mouse_pos = pyautogui.position()
        
        # 使用更精确的录制方法
        self.record_mouse_movement()
        
    def stop(self):
        self.is_recording = False
        
    def record_mouse_movement(self):
        """录制鼠标移动和点击"""
        while self.is_recording:
            try:
                current_pos = pyautogui.position()
                
                # 检测鼠标移动
                if self.last_mouse_pos != current_pos:
                    current_time = time.time() - self.start_time
                    action = {
                        'type': 'mouse_move',
                        'x': current_pos[0],
                        'y': current_pos[1],
                        'time': current_time
                    }
                    self.action_recorded.emit(action)
                    self.last_mouse_pos = current_pos
                
                time.sleep(0.01)  # 10ms采样率
                
            except Exception as e:
                self.status_updated.emit(f"录制错误: {str(e)}")
                
        # 停止监听
        mouse.unhook_all()
        keyboard.unhook_all()

class PlayingThread(QThread):
    """回放线程"""
    progress_updated = pyqtSignal(int)
    action_completed = pyqtSignal(str)
    playback_finished = pyqtSignal()
    
    def __init__(self, actions, repeat_count=1):
        super().__init__()
        self.actions = actions
        self.repeat_count = repeat_count
        self.is_playing = False
        
    def run(self):
        self.is_playing = True
        
        # 倒计时
        for i in range(3, 0, -1):
            if not self.is_playing:
                return
            self.action_completed.emit(f"回放将在 {i} 秒后开始...")
            time.sleep(1)
            
        self.action_completed.emit("开始回放操作...")
        
        for repeat in range(self.repeat_count):
            if not self.is_playing:
                break
                
            self.action_completed.emit(f"第 {repeat + 1} 次回放")
            
            last_time = 0
            for i, action in enumerate(self.actions):
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
                        
                    # 更新进度
                    progress = int((i + 1) / len(self.actions) * 100)
                    self.progress_updated.emit(progress)
                    
                except Exception as e:
                    self.action_completed.emit(f"回放出错: {str(e)}")
                    
            if repeat < self.repeat_count - 1:
                self.action_completed.emit("等待下一次回放...")
                time.sleep(1)
                
        self.action_completed.emit("回放完成")
        self.playback_finished.emit()
        
    def stop(self):
        self.is_playing = False

class KeyMouseRecorder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.recorded_actions = []
        self.recording_thread = None
        self.playing_thread = None
        
        # 设置pyautogui安全设置
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.01
        
        self.init_ui()
        self.setup_dark_theme()
        self.setup_hotkeys()
        
    def init_ui(self):
        self.setWindowTitle("智能Windows键鼠录制工具 - 暗黑版")
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton#record {
                background-color: #f44336;
            }
            QPushButton#record:hover {
                background-color: #da190b;
            }
            QPushButton#play {
                background-color: #2196F3;
            }
            QPushButton#play:hover {
                background-color: #0b7dda;
            }
            QTextEdit {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 6px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                color: #ffffff;
                background-color: #3c3c3c;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 2px solid #555555;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #3c3c3c;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50;
            }
            QProgressBar {
                border: 2px solid #555555;
                border-radius: 6px;
                text-align: center;
                background-color: #3c3c3c;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 4px;
            }
            QSpinBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 4px;
                padding: 4px;
            }
            QCheckBox {
                color: #ffffff;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #555555;
                border-radius: 3px;
                background-color: #3c3c3c;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                border-color: #4CAF50;
            }
        """)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 标题
        title_label = QLabel("🤖 智能Windows键鼠录制工具")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; color: #4CAF50; margin: 10px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # 状态栏
        self.status_label = QLabel("状态: 待机")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; color: #888888; margin: 5px;")
        main_layout.addWidget(self.status_label)
        
        # 创建标签页
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # 录制标签页
        recording_tab = self.create_recording_tab()
        tab_widget.addTab(recording_tab, "🎬 录制控制")
        
        # 回放标签页
        playback_tab = self.create_playback_tab()
        tab_widget.addTab(playback_tab, "▶️ 回放控制")
        
        # 智能设置标签页
        smart_tab = self.create_smart_tab()
        tab_widget.addTab(smart_tab, "🧠 智能设置")
        
        # 信息显示区域
        info_group = QGroupBox("📊 录制信息")
        info_layout = QVBoxLayout(info_group)
        
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(200)
        info_layout.addWidget(self.info_text)
        
        main_layout.addWidget(info_group)
        
    def setup_dark_theme(self):
        """设置暗黑主题"""
        app = QApplication.instance()
        app.setStyle('Fusion')
        
        # 设置暗黑调色板
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(43, 43, 43))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(60, 60, 60))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(60, 60, 60))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        app.setPalette(dark_palette)
        
    def create_recording_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 录制控制按钮
        button_layout = QHBoxLayout()
        
        self.record_button = QPushButton("🎬 开始录制")
        self.record_button.setObjectName("record")
        self.record_button.clicked.connect(self.toggle_recording)
        button_layout.addWidget(self.record_button)
        
        save_button = QPushButton("💾 保存录制")
        save_button.clicked.connect(self.save_recording)
        button_layout.addWidget(save_button)
        
        load_button = QPushButton("📂 加载录制")
        load_button.clicked.connect(self.load_recording)
        button_layout.addWidget(load_button)
        
        clear_button = QPushButton("🗑️ 清空录制")
        clear_button.clicked.connect(self.clear_recording)
        button_layout.addWidget(clear_button)
        
        layout.addLayout(button_layout)
        
        # 统计信息
        self.stats_label = QLabel("📈 录制统计: 0 个操作")
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.stats_label)
        
        return widget
        
    def create_playback_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 回放控制按钮
        button_layout = QHBoxLayout()
        
        self.play_button = QPushButton("▶️ 开始回放")
        self.play_button.setObjectName("play")
        self.play_button.clicked.connect(self.toggle_playing)
        button_layout.addWidget(self.play_button)
        
        layout.addLayout(button_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 回放设置
        settings_group = QGroupBox("⚙️ 回放设置")
        settings_layout = QVBoxLayout(settings_group)
        
        self.repeat_checkbox = QCheckBox("🔄 循环回放")
        settings_layout.addWidget(self.repeat_checkbox)
        
        repeat_layout = QHBoxLayout()
        repeat_layout.addWidget(QLabel("🔄 重复次数:"))
        self.repeat_spinbox = QSpinBox()
        self.repeat_spinbox.setRange(1, 100)
        self.repeat_spinbox.setValue(1)
        repeat_layout.addWidget(self.repeat_spinbox)
        repeat_layout.addStretch()
        settings_layout.addLayout(repeat_layout)
        
        layout.addWidget(settings_group)
        
        return widget
        
    def create_smart_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 热键设置
        hotkey_group = QGroupBox("⌨️ 热键设置")
        hotkey_layout = QVBoxLayout(hotkey_group)
        
        hotkey_info = QLabel("F9: 开始/停止录制\nF10: 开始/停止回放\nF11: 紧急停止")
        hotkey_layout.addWidget(hotkey_info)
        
        layout.addWidget(hotkey_group)
        
        # 智能设置
        smart_group = QGroupBox("🧠 智能功能")
        smart_layout = QVBoxLayout(smart_group)
        
        self.auto_save_checkbox = QCheckBox("💾 自动保存录制")
        self.auto_save_checkbox.setChecked(True)
        smart_layout.addWidget(self.auto_save_checkbox)
        
        self.smart_delay_checkbox = QCheckBox("⏱️ 智能延迟调整")
        self.smart_delay_checkbox.setChecked(True)
        smart_layout.addWidget(self.smart_delay_checkbox)
        
        self.auto_optimize_checkbox = QCheckBox("🔧 自动优化录制")
        self.auto_optimize_checkbox.setChecked(True)
        smart_layout.addWidget(self.auto_optimize_checkbox)
        
        layout.addWidget(smart_group)
        
        # 安全设置
        safety_group = QGroupBox("🛡️ 安全设置")
        safety_layout = QVBoxLayout(safety_group)
        
        self.failsafe_checkbox = QCheckBox("🚨 启用故障安全 (鼠标移到左上角停止)")
        self.failsafe_checkbox.setChecked(True)
        safety_layout.addWidget(self.failsafe_checkbox)
        
        layout.addWidget(safety_group)
        
        layout.addStretch()
        
        return widget
        
    def setup_hotkeys(self):
        # 设置全局热键
        keyboard.add_hotkey('f9', self.toggle_recording)
        keyboard.add_hotkey('f10', self.toggle_playing)
        keyboard.add_hotkey('f11', self.emergency_stop)
        
    def toggle_recording(self):
        if not hasattr(self, 'recording_thread') or not self.recording_thread or not self.recording_thread.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
            
    def start_recording(self):
        self.recorded_actions = []
        self.record_button.setText("⏹️ 停止录制")
        self.record_button.setStyleSheet("background-color: #ff4757;")
        self.status_label.setText("状态: 🎬 录制中...")
        self.info_text.clear()
        self.info_text.append("🎬 开始录制...")
        
        # 启动录制线程
        self.recording_thread = RecordingThread()
        self.recording_thread.action_recorded.connect(self.on_action_recorded)
        self.recording_thread.status_updated.connect(self.info_text.append)
        self.recording_thread.start()
        
        # 启动鼠标点击监听
        self.start_mouse_listener()
        
    def start_mouse_listener(self):
        """启动鼠标监听"""
        def on_click(x, y, button, pressed):
            if hasattr(self, 'recording_thread') and self.recording_thread and self.recording_thread.is_recording:
                current_time = time.time() - self.recording_thread.start_time
                action = {
                    'type': 'mouse_click',
                    'x': x,
                    'y': y,
                    'button': str(button),
                    'pressed': pressed,
                    'time': current_time
                }
                self.recording_thread.action_recorded.emit(action)
                
        def on_key_press(key):
            if hasattr(self, 'recording_thread') and self.recording_thread and self.recording_thread.is_recording:
                current_time = time.time() - self.recording_thread.start_time
                action = {
                    'type': 'key_press',
                    'key': str(key),
                    'time': current_time
                }
                self.recording_thread.action_recorded.emit(action)
                
        def on_key_release(key):
            if hasattr(self, 'recording_thread') and self.recording_thread and self.recording_thread.is_recording:
                current_time = time.time() - self.recording_thread.start_time
                action = {
                    'type': 'key_release',
                    'key': str(key),
                    'time': current_time
                }
                self.recording_thread.action_recorded.emit(action)
        
        # 启动监听
        import pynput
        self.mouse_listener = pynput.mouse.Listener(on_click=on_click)
        self.keyboard_listener = pynput.keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
        
        self.mouse_listener.start()
        self.keyboard_listener.start()
        
    def stop_recording(self):
        if self.recording_thread:
            self.recording_thread.stop()
            self.recording_thread.wait()
            
        # 停止监听
        if hasattr(self, 'mouse_listener'):
            self.mouse_listener.stop()
        if hasattr(self, 'keyboard_listener'):
            self.keyboard_listener.stop()
            
        self.record_button.setText("🎬 开始录制")
        self.record_button.setStyleSheet("")
        self.status_label.setText("状态: ✅ 录制完成")
        self.info_text.append(f"✅ 录制完成，共录制 {len(self.recorded_actions)} 个操作")
        self.update_stats()
        
        # 自动保存
        if self.auto_save_checkbox.isChecked():
            self.auto_save_recording()
        
    def auto_save_recording(self):
        """自动保存录制"""
        if self.recorded_actions:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"auto_save_{timestamp}.json"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.recorded_actions, f, ensure_ascii=False, indent=2)
                self.info_text.append(f"💾 自动保存到: {filename}")
            except Exception as e:
                self.info_text.append(f"❌ 自动保存失败: {str(e)}")
        
    def on_action_recorded(self, action):
        self.recorded_actions.append(action)
        
        if action['type'] == 'mouse_click':
            status = "按下" if action['pressed'] else "释放"
            self.info_text.append(f"🖱️ 鼠标点击: {action['button']} {status} at ({action['x']}, {action['y']})")
        elif action['type'] == 'mouse_move':
            self.info_text.append(f"🖱️ 鼠标移动: ({action['x']}, {action['y']})")
        elif action['type'] == 'key_press':
            self.info_text.append(f"⌨️ 按键按下: {action['key']}")
        elif action['type'] == 'key_release':
            self.info_text.append(f"⌨️ 按键释放: {action['key']}")
            
        self.update_stats()
        
    def toggle_playing(self):
        if not hasattr(self, 'playing_thread') or not self.playing_thread or not self.playing_thread.is_playing:
            self.start_playing()
        else:
            self.stop_playing()
            
    def start_playing(self):
        if not self.recorded_actions:
            QMessageBox.warning(self, "警告", "没有可回放的操作！")
            return
            
        repeat_count = self.repeat_spinbox.value() if self.repeat_checkbox.isChecked() else 1
        
        self.play_button.setText("⏹️ 停止回放")
        self.play_button.setStyleSheet("background-color: #ff4757;")
        self.status_label.setText("状态: ▶️ 回放中...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # 启动回放线程
        self.playing_thread = PlayingThread(self.recorded_actions, repeat_count)
        self.playing_thread.progress_updated.connect(self.progress_bar.setValue)
        self.playing_thread.action_completed.connect(self.info_text.append)
        self.playing_thread.playback_finished.connect(self.on_playback_finished)
        self.playing_thread.start()
        
    def stop_playing(self):
        if self.playing_thread:
            self.playing_thread.stop()
            self.playing_thread.wait()
            
        self.play_button.setText("▶️ 开始回放")
        self.play_button.setStyleSheet("")
        self.status_label.setText("状态: ✅ 回放完成")
        self.progress_bar.setVisible(False)
        
    def on_playback_finished(self):
        self.stop_playing()
        
    def emergency_stop(self):
        """紧急停止所有操作"""
        self.stop_recording()
        self.stop_playing()
        self.status_label.setText("状态: 🚨 紧急停止")
        self.info_text.append("🚨 紧急停止所有操作")
        
    def update_stats(self):
        self.stats_label.setText(f"📈 录制统计: {len(self.recorded_actions)} 个操作")
        
    def save_recording(self):
        if not self.recorded_actions:
            QMessageBox.warning(self, "警告", "没有可保存的录制！")
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "保存录制", "", "JSON files (*.json);;All files (*.*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.recorded_actions, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "成功", f"录制已保存到: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")
                
    def load_recording(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "加载录制", "", "JSON files (*.json);;All files (*.*)"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.recorded_actions = json.load(f)
                QMessageBox.information(self, "成功", f"录制已加载: {filename}")
                self.info_text.clear()
                self.info_text.append(f"📂 已加载 {len(self.recorded_actions)} 个操作")
                self.update_stats()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载失败: {str(e)}")
                
    def clear_recording(self):
        self.recorded_actions = []
        self.info_text.clear()
        self.info_text.append("🗑️ 录制已清空")
        self.update_stats()
        QMessageBox.information(self, "成功", "录制已清空")

def main():
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    window = KeyMouseRecorder()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 