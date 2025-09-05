#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双相机控制组件
包含两个相机的竖直排列布局
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSplitter
from PyQt5.QtCore import Qt
from .camera_widget import CameraWidget

class DualCameraWidget(QWidget):
    """双相机控制组件 - 水平排列"""
    
    def __init__(self, robot_data, screen_width=1920, screen_height=1080):
        super().__init__()
        self.robot_data = robot_data
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        # 创建主布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建水平分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #e8eaed;
                width: 6px;
                border-radius: 3px;
                margin: 0 2px;
            }
            QSplitter::handle:hover {
                background-color: #1976d2;
            }
        """)
        
        # 创建两个相机组件
        self.camera1_widget = CameraWidget("📹 前置相机", 0, self.robot_data)
        self.camera2_widget = CameraWidget("📹 后置相机", 1, self.robot_data)
        
        # 添加到分割器
        splitter.addWidget(self.camera1_widget)
        splitter.addWidget(self.camera2_widget)
        
        # 设置分割器比例 - 两个相机等高，增大尺寸
        splitter.setSizes([500, 500])
        
        # 添加到主布局
        main_layout.addWidget(splitter)
        
    def closeEvent(self, event):
        """关闭事件处理"""
        # 停止两个相机
        if hasattr(self, 'camera1_widget'):
            self.camera1_widget.stop_camera()
        if hasattr(self, 'camera2_widget'):
            self.camera2_widget.stop_camera()
        event.accept()