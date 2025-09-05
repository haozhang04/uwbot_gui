#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水下机器人控制界面主程序
模块化设计，包含控制界面、参数界面、设置界面
"""

import sys
import os
import json
import threading 
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QDesktopWidget
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

# 添加messages目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'messages'))
from robot_data import get_robot_data

# 导入各个模块
from ui_modules.control_mode.status.status_display import StatusDisplayWidget
from ui_modules.control_mode.status.main_status_bar import MainStatusBar
from ui_modules.control_mode.motion.motion_control import MotionControlWidget
from ui_modules.control_mode.camera import DualCameraWidget
from ui_modules.param_mode.parameters_view import ParametersViewWidget
from ui_modules.log_mode.log_view import LogViewWidget
from LCM.lcm import LCMInterface



class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.robot_data = get_robot_data()
        self.lcm = LCMInterface()
        self.config = self.load_config()
        self.uptime_counter = 0.0  # 独立的运行时间计数器
        self.init_lcm()  # 初始化LCM通信线程
        self.setup_logging()  # 初始化日志系统
        self.init_ui()
        self.setup_timer()

    def init_lcm(self):
        """初始化LCM通信"""
        self.lcm.lcm_stop_flag = False #开启lcm
        self.lcm.receiveData()
        # 创建新线程运行LCM接收循环
        self.lcm_thread = threading.Thread(target=self.lcm.handle_receive, daemon=True)
        self.lcm_thread.start()
        self.robot_data.state = self.lcm.state_simple
        # 添加100Hz LCM数据发送定时器
        self.lcm_send_timer = QTimer()
        self.lcm_send_timer.timeout.connect(self.lcm.send_data_once)
        self.lcm_send_timer.start(10)  # 10ms = 100Hz

    def load_config(self):
        """加载配置文件"""
        config_file = os.path.join(os.path.dirname(__file__), 'config', 'ui_config.json')
        default_config = {
            "window": {
                "remember_size": True,
                "remember_position": True,
                "start_maximized": True,
                "start_fullscreen": False,
                "always_on_top": False
            }
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 合并默认配置，确保所有键都存在
                if "window" not in config:
                    config["window"] = default_config["window"].copy()
                else:
                    for key in default_config["window"]:
                        if key not in config["window"]:
                            config["window"][key] = default_config["window"][key]
                return config
        except Exception as e:
            print(f"加载配置失败: {e}")
        return default_config
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("水下机器人控制系统")
        
        # 获取屏幕尺寸
        desktop = QDesktopWidget()
        screen_rect = desktop.screenGeometry()
        screen_width = screen_rect.width()
        screen_height = screen_rect.height()
        
        # 根据配置设置窗口模式
        window_config = self.config.get("window", {})
        
        if window_config.get("start_fullscreen", False):
            # 全屏模式
            self.showFullScreen()
        elif window_config.get("start_maximized", True):
            # 最大化模式
            self.setWindowState(Qt.WindowMaximized)
        else:
            # 普通窗口模式
            self.resize(1200, 800)
            # 居中显示
            self.move((screen_width - 1200) // 2, (screen_height - 800) // 2)
        
        # 设置置顶属性
        if window_config.get("always_on_top", False):
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.show()
        
        # 存储屏幕尺寸供后续使用
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 设置应用程序样式 - 现代白色风格
        self.setStyleSheet("""
            QMainWindow {
                background-color: #fafafa;
                color: #2c3e50;
                font-family: 'Microsoft YaHei UI', 'Segoe UI', sans-serif;
            }
            QTabWidget::pane {
                border: 2px solid #e8eaed;
                background-color: #ffffff;
                border-radius: 12px;
                padding: 8px;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                background-color: #ffffff;
                color: #5f6368;
                padding: 8px 16px;
                margin: 1px 1px;
                border-radius: 6px;
                min-width: 80px;
                border: 1px solid #e8eaed;
                font-weight: 600;
                font-size: 12px;
            }
            QTabBar::tab:selected {
                background-color: #1976d2;
                color: #ffffff;
                border: 2px solid #1976d2;
            }
            QTabBar::tab:hover {
                background-color: #f1f3f4;
                border: 2px solid #1976d2;
                color: #1976d2;
            }
        """)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)
        
        # 创建标题
        title_label = QLabel("水下机器人控制系统")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Microsoft YaHei UI", 20, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #1976d2, stop:1 #42a5f5);
                padding: 10px;
                border-radius: 12px;
                margin-bottom: 5px;
                font-size: 18px;
                font-weight: 700;
                letter-spacing: 1px;
            }
        """)
        main_layout.addWidget(title_label)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)  # 移至上方
        self.tab_widget.setMovable(False)
        self.tab_widget.setTabsClosable(False)
        # 连接标签页切换信号以优化性能
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        main_layout.addWidget(self.tab_widget)
        
        # 创建主界面状态栏
        self.main_status_bar = MainStatusBar(self.robot_data)
        main_layout.addWidget(self.main_status_bar)
        
        # 创建四个主要界面
        self.create_control_interface()
        self.create_parameters_interface()

        self.create_log_interface()
        
    def create_control_interface(self):
        """创建控制界面"""
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)  # 改回垂直布局
        control_layout.setContentsMargins(20, 20, 20, 20)
        control_layout.setSpacing(20)
        
        # 创建上部分的水平布局（状态显示和相机）
        top_layout = QHBoxLayout()
        top_layout.setSpacing(20)
        
        # 模块1：机器人状态显示（左上，占4/10）
        self.status_widget = StatusDisplayWidget(self.robot_data)
        top_layout.addWidget(self.status_widget, 5)
        
        # 模块2：双相机控制（右上，占6/10）
        self.camera_widget = DualCameraWidget(self.robot_data)
        top_layout.addWidget(self.camera_widget, 7)
        
        # 创建上部分容器
        top_widget = QWidget()
        top_widget.setLayout(top_layout)
        
        # 模块3：机器人运动控制（下部分，占满整个宽度）
        self.motion_widget = MotionControlWidget(self.robot_data)
        
        # 添加到主布局：上部分5/10，下部分5/10
        control_layout.addWidget(top_widget, 7)
        control_layout.addWidget(self.motion_widget, 6)
        
        self.tab_widget.addTab(control_widget, "🎮 控制")
        
    def create_parameters_interface(self):
        """创建参数界面"""
        self.parameters_widget = ParametersViewWidget(self.robot_data)
        self.tab_widget.addTab(self.parameters_widget, "⚙️ 参数")
        

        
    def create_log_interface(self):
        """创建日志界面"""
        # 导入日志模块
        from ui_modules.log_mode.log_view import LogViewWidget
        self.log_widget = LogViewWidget()
        self.tab_widget.addTab(self.log_widget, "📋 日志")
        
    def setup_timer(self):
        """设置定时器用于数据更新"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(200)  # 200ms更新一次，减少CPU占用
        
    def on_tab_changed(self, index):
        """标签页切换时的处理"""
        # 暂停非活动标签页的定时器以提升性能
        if hasattr(self, 'parameters_widget'):
            if index == 1:  # 参数界面
                self.parameters_widget.update_timer.start(300)
            else:
                self.parameters_widget.update_timer.stop()
    
    def update_data(self):
        """更新数据显示"""
        # 更新系统运行时间
        self.uptime_counter += 0.2  # 每200ms增加0.2秒
        self.robot_data.update_uptime(self.uptime_counter)
        
        # 始终更新主状态栏
        if hasattr(self, 'main_status_bar'):
            self.main_status_bar.update_display()
        
        # 只更新当前活动标签页的数据
        current_tab = self.tab_widget.currentIndex()
        
        # 控制界面 (index 0) - 始终更新状态和运动控制
        if current_tab == 0:
            if hasattr(self, 'status_widget'):
                self.status_widget.update_display()
            if hasattr(self, 'motion_widget'):
                self.motion_widget.update_display()
        
        # 双相机模块自行处理更新
        # 参数界面的更新由其自己的定时器处理
            
    def closeEvent(self, event):
        """关闭事件处理"""
        self.update_timer.stop()
        # 停止所有子模块的定时器
        if hasattr(self, 'parameters_widget') and hasattr(self.parameters_widget, 'update_timer'):
            self.parameters_widget.update_timer.stop()
        if hasattr(self, 'dual_camera_widget'):
            self.dual_camera_widget.close()
        event.accept()
    
    def setup_logging(self):
        """初始化日志系统"""
        # 创建一个临时的LogViewWidget实例来初始化日志系统
        temp_log_widget = LogViewWidget()
        # 日志系统已经在LogViewWidget的__init__中初始化了

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("水下机器人控制系统")
    app.setApplicationVersion("1.0.0")
    
    # 设置字体
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()