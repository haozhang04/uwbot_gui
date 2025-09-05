import sys
import logging
from PyQt5.QtCore import QObject, QTimer, pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel, QFrame, QTextEdit
from PyQt5.QtGui import QKeyEvent
"""
浮游模式控制:
  移动控制: W(前进) S(后退) A(左移) D(右移) Q(上升) E(下降)
  旋转控制: J(左转) L(右转) I(抬头) K(低头) U(左滚) O(右滚)

轮式模式控制:
  方向键: ↑(前进) ↓(后退) ←(左转) →(右转)

紧急操作: 空格键(急停)

注意: 启用键盘控制后，需要点击界面获得焦点才能响应按键
"""
class KeyboardController(QObject):
    """键盘控制器类"""
    
    # 信号定义
    velocity_changed = pyqtSignal(str, float)  # 参数名, 新值
    emergency_stop = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.enabled = False
        self.step_size = 0.1  # 每次按键的增量
        
        # 当前速度值
        self.velocities = {
            'vel_x': 0.0,
            'vel_y': 0.0, 
            'vel_z': 0.0,
            'ang_roll': 0.0,
            'ang_yaw': 0.0,
            'ang_pitch': 0.0,
            'wheel_linear_vel': 0.0,
            'wheel_angular_vel': 0.0
        }
        
        # 速度限制
        self.velocity_limits = {
            'vel_x': (-2.0, 2.0),
            'vel_y': (-2.0, 2.0),
            'vel_z': (-2.0, 2.0),
            'ang_roll': (-180, 180),
            'ang_yaw': (-180, 180),
            'ang_pitch': (-180, 180),
            'wheel_linear_vel': (-2.0, 2.0),
            'wheel_angular_vel': (-3.14, 3.14)
        }
        
        # 按键映射
        self.key_mappings = {
            # 浮游模式控制
            Qt.Key_W: ('vel_x', self.step_size),      # 前进
            Qt.Key_S: ('vel_x', -self.step_size),     # 后退
            Qt.Key_A: ('vel_y', -self.step_size),     # 左移
            Qt.Key_D: ('vel_y', self.step_size),      # 右移
            Qt.Key_Q: ('vel_z', self.step_size),      # 上升
            Qt.Key_E: ('vel_z', -self.step_size),     # 下降
            Qt.Key_J: ('ang_yaw', -5.0),   # 左转
            Qt.Key_L: ('ang_yaw', 5.0),    # 右转
            Qt.Key_I: ('ang_pitch', 5.0),  # 抬头
            Qt.Key_K: ('ang_pitch', -5.0), # 低头
            Qt.Key_U: ('ang_roll', -5.0),  # 左滚
            Qt.Key_O: ('ang_roll', 5.0),   # 右滚
            # 轮式模式控制
            Qt.Key_Up: ('wheel_linear_vel', self.step_size),     # 轮式前进
            Qt.Key_Down: ('wheel_linear_vel', -self.step_size),  # 轮式后退
            Qt.Key_Left: ('wheel_angular_vel', -self.step_size), # 轮式左转
            Qt.Key_Right: ('wheel_angular_vel', self.step_size), # 轮式右转
        }
        
        # 设置定时器用于持续按键检测
        self.key_timer = QTimer()
        self.key_timer.timeout.connect(self.process_continuous_keys)
        self.pressed_keys = set()
        
        logging.info("键盘控制器初始化完成")
    
    def set_enabled(self, enabled):
        """设置键盘控制是否启用"""
        self.enabled = enabled
        if enabled:
            self.key_timer.start(50)  # 50ms间隔处理按键
            logging.info("键盘控制已启用")
        else:
            self.key_timer.stop()
            self.pressed_keys.clear()
            logging.info("键盘控制已禁用")
    
    def handle_key_press(self, key):
        """处理按键按下事件"""
        if not self.enabled:
            return False
            
        # 空格键急停
        if key == Qt.Key_Space:
            self.emergency_stop_action()
            return True
            
        # 添加到持续按键集合
        if key in self.key_mappings:
            self.pressed_keys.add(key)
            return True
            
        return False
    
    def handle_key_release(self, key):
        """处理按键释放事件"""
        if not self.enabled:
            return False
            
        # 从持续按键集合中移除
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)
            return True
            
        return False
    
    def process_continuous_keys(self):
        """处理持续按下的按键"""
        if not self.enabled or not self.pressed_keys:
            return
            
        for key in self.pressed_keys:
            if key in self.key_mappings:
                param_name, delta = self.key_mappings[key]
                self.update_velocity(param_name, delta)
    
    def update_velocity(self, param_name, delta):
        """更新速度值"""
        if param_name not in self.velocities:
            return
            
        # 计算新值
        new_value = self.velocities[param_name] + delta
        
        # 应用限制
        min_val, max_val = self.velocity_limits[param_name]
        new_value = max(min_val, min(max_val, new_value))
        
        # 更新值并发送信号
        if abs(new_value - self.velocities[param_name]) > 1e-6:
            self.velocities[param_name] = new_value
            self.velocity_changed.emit(param_name, new_value)
            logging.debug(f"键盘控制更新 {param_name}: {new_value:.2f}")
    
    def emergency_stop_action(self):
        """紧急停止动作"""
        logging.warning("键盘控制触发紧急停止")
        
        # 清零所有速度
        for param_name in self.velocities:
            self.velocities[param_name] = 0.0
            self.velocity_changed.emit(param_name, 0.0)
        
        # 清除按键状态
        self.pressed_keys.clear()
        
        # 发送紧急停止信号
        self.emergency_stop.emit()
    
    def reset_velocities(self):
        """重置所有速度为零"""
        for param_name in self.velocities:
            self.velocities[param_name] = 0.0
            self.velocity_changed.emit(param_name, 0.0)
        logging.info("键盘控制速度已重置")
    
    def set_step_size(self, step_size):
        """设置步长"""
        self.step_size = max(0.01, min(1.0, step_size))
        # 更新按键映射中的步长
        for key, (param, _) in self.key_mappings.items():
            if param.startswith('vel_'):
                sign = 1 if self.key_mappings[key][1] > 0 else -1
                self.key_mappings[key] = (param, sign * self.step_size)
        logging.info(f"键盘控制步长设置为: {self.step_size}")


class KeyboardControlWidget(QWidget):
    """键盘控制界面组件"""
    
    def __init__(self, keyboard_controller, parent=None):
        super().__init__(parent)
        self.keyboard_controller = keyboard_controller
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("🎮 键盘直接控制")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                padding: 5px;
            }
        """)
        layout.addWidget(title_label)
        
        # 控制开关
        control_frame = QFrame()
        control_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        control_layout = QHBoxLayout(control_frame)
        
        self.enable_checkbox = QCheckBox("启用键盘控制")
        self.enable_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 12px;
                font-weight: 600;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #6c757d;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #28a745;
                border-radius: 3px;
                background-color: #28a745;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }
        """)
        
        self.status_label = QLabel("🔴 未启用")
        self.status_label.setStyleSheet("color: #dc3545; font-weight: 600;")
        
        control_layout.addWidget(self.enable_checkbox)
        control_layout.addStretch()
        control_layout.addWidget(self.status_label)
        
        layout.addWidget(control_frame)
    
    def setup_connections(self):
        """设置信号连接"""
        self.enable_checkbox.toggled.connect(self.on_enable_toggled)
    
    def on_enable_toggled(self, checked):
        """处理启用开关切换"""
        self.keyboard_controller.set_enabled(checked)
        
        if checked:
            self.status_label.setText("🟢 已启用")
            self.status_label.setStyleSheet("color: #28a745; font-weight: 600;")
            self.setFocus()  # 获取焦点以接收按键事件
        else:
            self.status_label.setText("🔴 未启用")
            self.status_label.setStyleSheet("color: #dc3545; font-weight: 600;")
    
    def keyPressEvent(self, event: QKeyEvent):
        """处理按键按下事件"""
        if self.keyboard_controller.handle_key_press(event.key()):
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event: QKeyEvent):
        """处理按键释放事件"""
        if self.keyboard_controller.handle_key_release(event.key()):
            event.accept()
        else:
            super().keyReleaseEvent(event)
    
    def focusInEvent(self, event):
        """获得焦点时的处理"""
        super().focusInEvent(event)
        if self.enable_checkbox.isChecked():
            logging.debug("键盘控制组件获得焦点")
    
    def focusOutEvent(self, event):
        """失去焦点时的处理"""
        super().focusOutEvent(event)
        # 清除所有按键状态
        self.keyboard_controller.pressed_keys.clear()
        logging.debug("键盘控制组件失去焦点")