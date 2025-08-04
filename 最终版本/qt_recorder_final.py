import sys
import json
import time
import threading
import psutil
import gc
import pyautogui
import keyboard
import mouse
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                             QFileDialog, QMessageBox, QFrame, QProgressBar,
                             QSpinBox, QGroupBox, QCheckBox, QTabWidget, QSlider,
                             QComboBox, QLineEdit, QListWidget, QSplitter)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QMutex
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QPixmap

class PerformanceMonitor(QThread):
    """性能监控线程"""
    performance_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.is_monitoring = False
        
    def run(self):
        self.is_monitoring = True
        while self.is_monitoring:
            try:
                # 获取系统性能数据
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                memory_used = memory.used / (1024**3)  # GB
                
                performance_data = {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory_percent,
                    'memory_used_gb': round(memory_used, 2),
                    'timestamp': time.time()
                }
                
                self.performance_updated.emit(performance_data)
                time.sleep(2)  # 每2秒更新一次
                
            except Exception as e:
                print(f"性能监控错误: {e}")
                time.sleep(5)
                
    def stop(self):
        self.is_monitoring = False

class FinalRecordingThread(QThread):
    """最终版录制线程 - 完整修复和优化"""
    action_recorded = pyqtSignal(dict)
    status_updated = pyqtSignal(str)
    preview_updated = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.start_time = 0
        self.last_mouse_pos = None
        self.action_count = 0
        self.mutex = QMutex()
        
        # 性能优化参数
        self.sample_rate = 0.01  # 10ms采样率
        self.max_actions = 10000  # 最大动作数量限制
        
        # 条件录制参数
        self.target_window = None
        self.record_only_target = False
        self.record_mouse_moves = True
        self.record_keyboard = True
        
        # 监听器
        self.mouse_listener = None
        self.keyboard_listener = None
        
    def set_recording_conditions(self, target_window=None, record_only_target=False,
                               record_mouse_moves=True, record_keyboard=True):
        """设置录制条件"""
        self.target_window = target_window
        self.record_only_target = record_only_target
        self.record_mouse_moves = record_mouse_moves
        self.record_keyboard = record_keyboard
        
    def set_performance_settings(self, sample_rate=0.01, max_actions=10000):
        """设置性能参数"""
        self.sample_rate = sample_rate
        self.max_actions = max_actions
        
    def run(self):
        try:
            self.is_recording = True
            self.start_time = time.time()
            self.last_mouse_pos = pyautogui.position()
            self.action_count = 0
            
            self.status_updated.emit("开始录制...")
            self.preview_updated.emit("录制状态: 活跃")
            
            # 启动鼠标移动录制
            if self.record_mouse_moves:
                self.start_mouse_movement_recording()
            
            # 启动鼠标点击和键盘监听
            self.start_input_listeners()
            
            # 等待录制结束
            while self.is_recording:
                time.sleep(0.1)
                
        except Exception as e:
            self.error_occurred.emit(f"录制启动失败: {str(e)}")
            
    def start_mouse_movement_recording(self):
        """启动鼠标移动录制"""
        def record_mouse_movement():
            while self.is_recording:
                try:
                    current_pos = pyautogui.position()
                    
                    # 验证坐标
                    if current_pos is None or len(current_pos) != 2:
                        time.sleep(self.sample_rate)
                        continue
                    
                    x, y = current_pos
                    if x is None or y is None:
                        time.sleep(self.sample_rate)
                        continue
                    
                    # 检查目标窗口条件
                    if self.record_only_target and self.target_window:
                        active_window = self.get_active_window()
                        if active_window != self.target_window:
                            time.sleep(self.sample_rate)
                            continue
                    
                    # 检测鼠标移动
                    if self.last_mouse_pos != current_pos:
                        current_time = time.time() - self.start_time
                        action = {
                            'type': 'mouse_move',
                            'x': x,
                            'y': y,
                            'time': current_time
                        }
                        
                        self.mutex.lock()
                        self.action_recorded.emit(action)
                        self.action_count += 1
                        self.mutex.unlock()
                        
                        self.last_mouse_pos = current_pos
                        self.preview_updated.emit(f"鼠标移动到: ({x}, {y})")
                    
                    time.sleep(self.sample_rate)
                    
                except Exception as e:
                    self.error_occurred.emit(f"鼠标录制错误: {str(e)}")
                    time.sleep(0.1)
                    
        # 在独立线程中运行鼠标移动录制
        mouse_movement_thread = threading.Thread(target=record_mouse_movement, daemon=True)
        mouse_movement_thread.start()
        
    def start_input_listeners(self):
        """启动输入监听器"""
        try:
            from pynput import mouse, keyboard as kb
            
            def on_click(x, y, button, pressed):
                if not self.is_recording:
                    return
                    
                try:
                    # 验证坐标
                    if x is None or y is None:
                        return
                    
                    # 检查目标窗口条件
                    if self.record_only_target and self.target_window:
                        active_window = self.get_active_window()
                        if active_window != self.target_window:
                            return
                    
                    current_time = time.time() - self.start_time
                    action = {
                        'type': 'mouse_click',
                        'x': x,
                        'y': y,
                        'button': str(button),
                        'pressed': pressed,
                        'time': current_time
                    }
                    
                    self.mutex.lock()
                    self.action_recorded.emit(action)
                    self.action_count += 1
                    self.mutex.unlock()
                    
                    action_type = "按下" if pressed else "释放"
                    self.preview_updated.emit(f"鼠标{action_type}: ({x}, {y}) {button}")
                    
                except Exception as e:
                    self.error_occurred.emit(f"鼠标点击录制错误: {str(e)}")
                    
            def on_key_press(key):
                if not self.is_recording:
                    return
                    
                try:
                    # 检查目标窗口条件
                    if self.record_only_target and self.target_window:
                        active_window = self.get_active_window()
                        if active_window != self.target_window:
                            return
                    
                    current_time = time.time() - self.start_time
                    
                    # 处理特殊按键
                    if hasattr(key, 'char') and key.char:
                        key_str = key.char
                    elif hasattr(key, 'name') and key.name:
                        key_str = key.name
                    else:
                        key_str = str(key).replace("'", "")
                    
                    # 验证按键
                    if not key_str:
                        return
                    
                    action = {
                        'type': 'key_press',
                        'key': key_str,
                        'time': current_time
                    }
                    
                    self.mutex.lock()
                    self.action_recorded.emit(action)
                    self.action_count += 1
                    self.mutex.unlock()
                    
                    self.preview_updated.emit(f"按键: {key_str}")
                    
                except Exception as e:
                    self.error_occurred.emit(f"键盘录制错误: {str(e)}")
                    
            def on_key_release(key):
                if not self.is_recording:
                    return
                    
                try:
                    # 检查目标窗口条件
                    if self.record_only_target and self.target_window:
                        active_window = self.get_active_window()
                        if active_window != self.target_window:
                            return
                    
                    current_time = time.time() - self.start_time
                    
                    # 处理特殊按键
                    if hasattr(key, 'char') and key.char:
                        key_str = key.char
                    elif hasattr(key, 'name') and key.name:
                        key_str = key.name
                    else:
                        key_str = str(key).replace("'", "")
                    
                    # 验证按键
                    if not key_str:
                        return
                    
                    action = {
                        'type': 'key_release',
                        'key': key_str,
                        'time': current_time
                    }
                    
                    self.mutex.lock()
                    self.action_recorded.emit(action)
                    self.action_count += 1
                    self.mutex.unlock()
                    
                except Exception as e:
                    self.error_occurred.emit(f"键盘录制错误: {str(e)}")
                    
            # 启动监听器
            self.mouse_listener = mouse.Listener(on_click=on_click)
            self.keyboard_listener = kb.Listener(on_press=on_key_press, on_release=on_key_release)
            
            self.mouse_listener.start()
            self.keyboard_listener.start()
            
        except Exception as e:
            self.error_occurred.emit(f"输入监听器启动失败: {str(e)}")
            
    def get_active_window(self):
        """获取当前活动窗口"""
        try:
            import win32gui
            return win32gui.GetWindowText(win32gui.GetForegroundWindow())
        except:
            return None
            
    def stop(self):
        """停止录制"""
        self.is_recording = False
        self.status_updated.emit("录制已停止")
        self.preview_updated.emit("录制状态: 已停止")
        
        # 停止监听器
        try:
            if self.mouse_listener:
                self.mouse_listener.stop()
            if self.keyboard_listener:
                self.keyboard_listener.stop()
        except:
            pass

class FinalPlayingThread(QThread):
    """最终版回放线程 - 完整修复和优化"""
    progress_updated = pyqtSignal(int)
    action_completed = pyqtSignal(str)
    playback_finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, actions, repeat_count=1, speed_multiplier=1.0):
        super().__init__()
        self.actions = actions
        self.repeat_count = repeat_count
        self.speed_multiplier = speed_multiplier
        self.is_playing = False
        self.error_count = 0
        self.max_errors = 10
        
    def run(self):
        try:
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
                        # 计算延迟（应用速度倍数）
                        delay = (action['time'] - last_time) / self.speed_multiplier
                        if delay > 0:
                            time.sleep(delay)
                            
                        # 执行动作
                        self.execute_action(action)
                        
                        # 更新进度
                        progress = int((i + 1) / len(self.actions) * 100)
                        self.progress_updated.emit(progress)
                        
                        last_time = action['time']
                        
                    except Exception as e:
                        self.error_count += 1
                        error_msg = f"回放错误 (动作 {i+1}): {str(e)}"
                        self.error_occurred.emit(error_msg)
                        
                        if self.error_count >= self.max_errors:
                            self.error_occurred.emit("错误次数过多，停止回放")
                            break
                            
                        continue
                        
                if repeat < self.repeat_count - 1:
                    self.action_completed.emit("等待下一次回放...")
                    time.sleep(1)  # 减少等待时间
                    
            self.playback_finished.emit()
            
        except Exception as e:
            self.error_occurred.emit(f"回放线程错误: {str(e)}")
            self.playback_finished.emit()
            
    def execute_action(self, action):
        """执行单个动作"""
        try:
            if action['type'] == 'mouse_move':
                # 验证坐标
                x = action.get('x')
                y = action.get('y')
                if x is None or y is None:
                    self.action_completed.emit(f"跳过无效坐标的鼠标移动")
                    return
                    
                pyautogui.moveTo(x, y)
                self.action_completed.emit(f"鼠标移动到: ({x}, {y})")
                
            elif action['type'] == 'mouse_click':
                # 验证坐标
                x = action.get('x')
                y = action.get('y')
                if x is None or y is None:
                    self.action_completed.emit(f"跳过无效坐标的鼠标点击")
                    return
                    
                if action.get('pressed', False):
                    pyautogui.mouseDown(x, y)
                else:
                    pyautogui.mouseUp(x, y)
                self.action_completed.emit(f"鼠标点击: ({x}, {y})")
                
            elif action['type'] == 'key_press':
                # 处理特殊按键
                key = action.get('key', '')
                if not key:
                    self.action_completed.emit(f"跳过无效的按键")
                    return
                    
                # 处理特殊按键
                if key in ['ctrl', 'alt', 'shift', 'cmd', 'ctrl_l', 'ctrl_r', 'alt_l', 'alt_r', 'shift_l', 'shift_r']:
                    pyautogui.keyDown(key)
                else:
                    # 尝试直接按键
                    try:
                        pyautogui.press(key)
                    except:
                        # 如果失败，尝试keyDown
                        pyautogui.keyDown(key)
                self.action_completed.emit(f"按键: {key}")
                
            elif action['type'] == 'key_release':
                key = action.get('key', '')
                if not key:
                    self.action_completed.emit(f"跳过无效的按键释放")
                    return
                    
                # 处理特殊按键
                if key in ['ctrl', 'alt', 'shift', 'cmd', 'ctrl_l', 'ctrl_r', 'alt_l', 'alt_r', 'shift_l', 'shift_r']:
                    pyautogui.keyUp(key)
                self.action_completed.emit(f"释放按键: {key}")
                
        except Exception as e:
            raise Exception(f"执行动作失败: {str(e)}")
            
    def stop(self):
        """停止回放"""
        self.is_playing = False
        self.action_completed.emit("回放已停止")

class FinalKeyMouseRecorder(QMainWindow):
    """最终版键鼠录制工具"""
    
    def __init__(self):
        super().__init__()
        self.recording_thread = None
        self.playing_thread = None
        self.performance_monitor = None
        self.recorded_actions = []
        self.error_log = []
        
        self.init_ui()
        self.setup_dark_theme()
        self.setup_hotkeys()
        
        # 启动性能监控
        self.start_performance_monitor()
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("🤖 智能Windows键鼠录制工具 - 最终版")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧控制面板
        control_panel = self.create_control_panel()
        splitter.addWidget(control_panel)
        
        # 右侧预览面板
        preview_panel = self.create_preview_panel()
        splitter.addWidget(preview_panel)
        
        # 设置分割器比例
        splitter.setSizes([600, 600])
        
    def create_control_panel(self):
        """创建控制面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 录制控制组
        recording_group = QGroupBox("🎬 录制控制")
        recording_layout = QVBoxLayout(recording_group)
        
        # 录制按钮
        self.record_btn = QPushButton("🎬 开始录制")
        self.record_btn.clicked.connect(self.toggle_recording)
        recording_layout.addWidget(self.record_btn)
        
        # 条件录制设置
        conditions_group = QGroupBox("🎯 录制条件")
        conditions_layout = QVBoxLayout(conditions_group)
        
        # 目标窗口选择
        self.target_window_combo = QComboBox()
        self.target_window_combo.addItem("所有窗口")
        self.refresh_windows_btn = QPushButton("🔄 刷新窗口列表")
        self.refresh_windows_btn.clicked.connect(self.refresh_windows)
        conditions_layout.addWidget(QLabel("目标窗口:"))
        conditions_layout.addWidget(self.target_window_combo)
        conditions_layout.addWidget(self.refresh_windows_btn)
        
        # 录制选项
        self.record_only_target_cb = QCheckBox("仅录制目标窗口")
        self.record_mouse_moves_cb = QCheckBox("录制鼠标移动")
        self.record_mouse_moves_cb.setChecked(True)
        self.record_keyboard_cb = QCheckBox("录制键盘操作")
        self.record_keyboard_cb.setChecked(True)
        
        conditions_layout.addWidget(self.record_only_target_cb)
        conditions_layout.addWidget(self.record_mouse_moves_cb)
        conditions_layout.addWidget(self.record_keyboard_cb)
        
        recording_layout.addWidget(conditions_group)
        layout.addWidget(recording_group)
        
        # 回放控制组
        playback_group = QGroupBox("▶️ 回放控制")
        playback_layout = QVBoxLayout(playback_group)
        
        self.play_btn = QPushButton("▶️ 开始回放")
        self.play_btn.clicked.connect(self.toggle_playing)
        playback_layout.addWidget(self.play_btn)
        
        # 回放设置
        self.repeat_count_spin = QSpinBox()
        self.repeat_count_spin.setRange(1, 100)
        self.repeat_count_spin.setValue(1)
        playback_layout.addWidget(QLabel("重复次数:"))
        playback_layout.addWidget(self.repeat_count_spin)
        
        # 回放速度设置
        self.speed_multiplier_spin = QSpinBox()
        self.speed_multiplier_spin.setRange(1, 10)
        self.speed_multiplier_spin.setValue(1)
        self.speed_multiplier_spin.setSuffix("x")
        playback_layout.addWidget(QLabel("回放速度:"))
        playback_layout.addWidget(self.speed_multiplier_spin)
        
        layout.addWidget(playback_group)
        
        # 文件操作组
        file_group = QGroupBox("📁 文件操作")
        file_layout = QVBoxLayout(file_group)
        
        save_btn = QPushButton("💾 保存录制")
        save_btn.clicked.connect(self.save_recording)
        file_layout.addWidget(save_btn)
        
        load_btn = QPushButton("📂 加载录制")
        load_btn.clicked.connect(self.load_recording)
        file_layout.addWidget(load_btn)
        
        clear_btn = QPushButton("🗑️ 清空录制")
        clear_btn.clicked.connect(self.clear_recording)
        file_layout.addWidget(clear_btn)
        
        layout.addWidget(file_group)
        
        # 性能设置组
        performance_group = QGroupBox("⚡ 性能设置")
        performance_layout = QVBoxLayout(performance_group)
        
        # 采样率设置
        self.sample_rate_spin = QSpinBox()
        self.sample_rate_spin.setRange(1, 100)
        self.sample_rate_spin.setValue(10)
        self.sample_rate_spin.setSuffix(" ms")
        performance_layout.addWidget(QLabel("采样率:"))
        performance_layout.addWidget(self.sample_rate_spin)
        
        # 最大动作数
        self.max_actions_spin = QSpinBox()
        self.max_actions_spin.setRange(1000, 50000)
        self.max_actions_spin.setValue(10000)
        performance_layout.addWidget(QLabel("最大动作数:"))
        performance_layout.addWidget(self.max_actions_spin)
        
        layout.addWidget(performance_group)
        
        layout.addStretch()
        return panel
        
    def create_preview_panel(self):
        """创建预览面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 状态显示组
        status_group = QGroupBox("📊 实时状态")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #4CAF50;")
        status_layout.addWidget(self.status_label)
        
        # 性能监控
        self.cpu_label = QLabel("CPU: 0%")
        self.memory_label = QLabel("内存: 0% (0 GB)")
        status_layout.addWidget(self.cpu_label)
        status_layout.addWidget(self.memory_label)
        
        layout.addWidget(status_group)
        
        # 录制预览组
        preview_group = QGroupBox("👁️ 录制预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(150)
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)
        
        layout.addWidget(preview_group)
        
        # 错误日志组
        error_group = QGroupBox("⚠️ 错误日志")
        error_layout = QVBoxLayout(error_group)
        
        self.error_text = QTextEdit()
        self.error_text.setMaximumHeight(150)
        self.error_text.setReadOnly(True)
        error_layout.addWidget(self.error_text)
        
        layout.addWidget(error_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # 统计信息
        stats_group = QGroupBox("📈 统计信息")
        stats_layout = QVBoxLayout(stats_group)
        
        self.action_count_label = QLabel("动作数量: 0")
        self.duration_label = QLabel("录制时长: 0秒")
        self.error_count_label = QLabel("错误次数: 0")
        
        stats_layout.addWidget(self.action_count_label)
        stats_layout.addWidget(self.duration_label)
        stats_layout.addWidget(self.error_count_label)
        
        layout.addWidget(stats_group)
        
        return panel
        
    def setup_dark_theme(self):
        """设置暗黑主题"""
        self.setStyleSheet("""
            QMainWindow { background-color: #2b2b2b; color: #ffffff; }
            QGroupBox { 
                background-color: #3c3c3c; 
                border: 2px solid #555555; 
                border-radius: 8px; 
                margin-top: 10px; 
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }
            QPushButton { 
                background-color: #4CAF50; 
                color: white; 
                padding: 12px; 
                border-radius: 6px; 
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:pressed { background-color: #3d8b40; }
            QTextEdit { 
                background-color: #3c3c3c; 
                color: #ffffff; 
                border: 2px solid #555555; 
                border-radius: 6px; 
                padding: 8px;
            }
            QLabel { color: #ffffff; }
            QSpinBox { 
                background-color: #3c3c3c; 
                color: #ffffff; 
                border: 2px solid #555555; 
                border-radius: 4px; 
                padding: 4px;
            }
            QComboBox { 
                background-color: #3c3c3c; 
                color: #ffffff; 
                border: 2px solid #555555; 
                border-radius: 4px; 
                padding: 4px;
            }
            QCheckBox { color: #ffffff; }
            QProgressBar { 
                background-color: #3c3c3c; 
                border: 2px solid #555555; 
                border-radius: 4px;
            }
            QProgressBar::chunk { background-color: #4CAF50; border-radius: 2px; }
        """)
        
    def start_performance_monitor(self):
        """启动性能监控"""
        self.performance_monitor = PerformanceMonitor()
        self.performance_monitor.performance_updated.connect(self.update_performance_display)
        self.performance_monitor.start()
        
    def update_performance_display(self, data):
        """更新性能显示"""
        self.cpu_label.setText(f"CPU: {data['cpu_percent']}%")
        self.memory_label.setText(f"内存: {data['memory_percent']}% ({data['memory_used_gb']} GB)")
        
    def refresh_windows(self):
        """刷新窗口列表"""
        try:
            import win32gui
            
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    if window_text:
                        windows.append(window_text)
                return True
                
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            self.target_window_combo.clear()
            self.target_window_combo.addItem("所有窗口")
            for window in windows[:20]:  # 限制显示前20个窗口
                self.target_window_combo.addItem(window)
                
        except Exception as e:
            self.log_error(f"刷新窗口列表失败: {str(e)}")
            
    def setup_hotkeys(self):
        """设置热键"""
        try:
            keyboard.add_hotkey('f11', self.emergency_stop)
        except Exception as e:
            self.log_error(f"热键设置失败: {str(e)}")
            
    def toggle_recording(self):
        """切换录制状态"""
        if self.recording_thread and self.recording_thread.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
            
    def start_recording(self):
        """开始录制"""
        try:
            # 获取录制条件
            target_window = self.target_window_combo.currentText()
            if target_window == "所有窗口":
                target_window = None
                
            record_only_target = self.record_only_target_cb.isChecked()
            record_mouse_moves = self.record_mouse_moves_cb.isChecked()
            record_keyboard = self.record_keyboard_cb.isChecked()
            
            # 获取性能设置
            sample_rate = self.sample_rate_spin.value() / 1000.0
            max_actions = self.max_actions_spin.value()
            
            # 创建录制线程
            self.recording_thread = FinalRecordingThread()
            self.recording_thread.action_recorded.connect(self.on_action_recorded)
            self.recording_thread.status_updated.connect(self.update_status)
            self.recording_thread.preview_updated.connect(self.update_preview)
            self.recording_thread.error_occurred.connect(self.log_error)
            
            # 设置参数
            self.recording_thread.set_recording_conditions(
                target_window, record_only_target, record_mouse_moves, record_keyboard
            )
            self.recording_thread.set_performance_settings(sample_rate, max_actions)
            
            # 清空之前的数据
            self.recorded_actions = []
            self.error_log = []
            self.update_stats()
            
            # 启动录制
            self.recording_thread.start()
            
            # 更新UI
            self.record_btn.setText("⏹️ 停止录制")
            self.record_btn.setStyleSheet("background-color: #f44336;")
            
        except Exception as e:
            self.log_error(f"启动录制失败: {str(e)}")
            
    def stop_recording(self):
        """停止录制"""
        if self.recording_thread:
            self.recording_thread.stop()
            self.recording_thread.wait()
            
        # 更新UI
        self.record_btn.setText("🎬 开始录制")
        self.record_btn.setStyleSheet("")
        self.update_status("录制已停止")
        
    def toggle_playing(self):
        """切换回放状态"""
        if self.playing_thread and self.playing_thread.is_playing:
            self.stop_playing()
        else:
            self.start_playing()
            
    def start_playing(self):
        """开始回放"""
        if not self.recorded_actions:
            QMessageBox.warning(self, "警告", "没有可回放的操作！")
            return
            
        try:
            repeat_count = self.repeat_count_spin.value()
            speed_multiplier = self.speed_multiplier_spin.value()
            
            self.playing_thread = FinalPlayingThread(self.recorded_actions, repeat_count, speed_multiplier)
            self.playing_thread.progress_updated.connect(self.progress_bar.setValue)
            self.playing_thread.action_completed.connect(self.update_preview)
            self.playing_thread.playback_finished.connect(self.on_playback_finished)
            self.playing_thread.error_occurred.connect(self.log_error)
            
            self.playing_thread.start()
            
            # 更新UI
            self.play_btn.setText("⏹️ 停止回放")
            self.play_btn.setStyleSheet("background-color: #f44336;")
            
        except Exception as e:
            self.log_error(f"启动回放失败: {str(e)}")
            
    def stop_playing(self):
        """停止回放"""
        if self.playing_thread:
            self.playing_thread.stop()
            self.playing_thread.wait()
            
        # 更新UI
        self.play_btn.setText("▶️ 开始回放")
        self.play_btn.setStyleSheet("")
        
    def on_playback_finished(self):
        """回放完成"""
        self.play_btn.setText("▶️ 开始回放")
        self.play_btn.setStyleSheet("")
        self.progress_bar.setValue(0)
        self.update_status("回放完成")
        
    def on_action_recorded(self, action):
        """处理录制的动作"""
        self.recorded_actions.append(action)
        self.update_stats()
        
    def update_status(self, message):
        """更新状态显示"""
        self.status_label.setText(message)
        
    def update_preview(self, message):
        """更新预览显示"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.preview_text.append(f"[{current_time}] {message}")
        
        # 限制显示行数
        lines = self.preview_text.toPlainText().split('\n')
        if len(lines) > 50:
            self.preview_text.setPlainText('\n'.join(lines[-50:]))
            
    def log_error(self, error_message):
        """记录错误"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.error_text.append(f"[{current_time}] ❌ {error_message}")
        
        # 限制显示行数
        lines = self.error_text.toPlainText().split('\n')
        if len(lines) > 20:
            self.error_text.setPlainText('\n'.join(lines[-20:]))
            
    def update_stats(self):
        """更新统计信息"""
        self.action_count_label.setText(f"动作数量: {len(self.recorded_actions)}")
        
        if self.recorded_actions:
            duration = self.recorded_actions[-1]['time']
            self.duration_label.setText(f"录制时长: {duration:.1f}秒")
            
        error_count = len(self.error_log)
        self.error_count_label.setText(f"错误次数: {error_count}")
        
    def emergency_stop(self):
        """紧急停止"""
        self.stop_recording()
        self.stop_playing()
        self.update_status("⚠️ 紧急停止已触发")
        
    def save_recording(self):
        """保存录制"""
        if not self.recorded_actions:
            QMessageBox.warning(self, "警告", "没有可保存的录制！")
            return
            
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "保存录制", "", "JSON文件 (*.json)"
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.recorded_actions, f, ensure_ascii=False, indent=2)
                self.update_status(f"录制已保存到: {filename}")
                
        except Exception as e:
            self.log_error(f"保存录制失败: {str(e)}")
            
    def load_recording(self):
        """加载录制"""
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self, "加载录制", "", "JSON文件 (*.json)"
            )
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.recorded_actions = json.load(f)
                self.update_stats()
                self.update_status(f"录制已加载: {filename}")
                
        except Exception as e:
            self.log_error(f"加载录制失败: {str(e)}")
            
    def clear_recording(self):
        """清空录制"""
        self.recorded_actions = []
        self.update_stats()
        self.update_status("录制已清空")
        
    def closeEvent(self, event):
        """关闭事件"""
        # 停止所有线程
        if self.recording_thread:
            self.recording_thread.stop()
        if self.playing_thread:
            self.playing_thread.stop()
        if self.performance_monitor:
            self.performance_monitor.stop()
            
        event.accept()

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("智能Windows键鼠录制工具")
    app.setApplicationVersion("3.0")
    app.setOrganizationName("木木iOS分享")
    
    # 创建主窗口
    window = FinalKeyMouseRecorder()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 