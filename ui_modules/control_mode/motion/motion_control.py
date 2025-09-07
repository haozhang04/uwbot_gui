#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器人运动控制模块
包含浮游模式、轮式模式、清洗功能的控制界面
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QFrame, QGroupBox, QScrollArea, QSlider, QPushButton, 
    QDoubleSpinBox, QSpinBox, QCheckBox, QButtonGroup, QRadioButton
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette
import math
import logging
from .keyboard_control import KeyboardController, KeyboardControlWidget

class MotionControlWidget(QWidget):
    """机器人运动控制组件"""
    
    def __init__(self, robot_data):
        super().__init__()
        self.robot_data = robot_data
        
        # 初始化紧急停止状态
        self.emergency_stop = False
        
        # 初始化键盘控制器
        self.keyboard_controller = KeyboardController(self)
        
        self.init_ui()
        self.setup_shortcuts()
        self.setup_real_time_feedback()
        self.setup_keyboard_control()
        
    def init_ui(self):
        """初始化用户界面"""
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #f5f5f5;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #c1c1c1;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #1976d2;
            }
        """)
        
        # 创建内容组件
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        
        # 内容布局 - 保持水平布局，增大垂直间距
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(11, 11, 11, 11)
        content_layout.setSpacing(14)
        
        # 设置样式 - 现代白色风格
        self.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                border: 2px solid #e8eaed;
                border-radius: 10px;
                margin-top: 10px;
                background-color: #ffffff;
                color: #2c3e50;
                padding-top: 14px;
                font-family: 'Microsoft YaHei UI', sans-serif;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 12px 0 12px;
                color: #1976d2;
                font-size: 14px;
                font-weight: 700;
                background-color: #ffffff;
            }
            QLabel {
                color: #333333;
                padding: 3px;
                font-size: 11px;
                min-height: 16px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #dee2e6;
                height: 10px;
                background: #f8f9fa;
                margin: 2px 0;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: #007bff;
                border: 1px solid #0056b3;
                width: 19px;
                margin: -6px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: #0056b3;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 19px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 11px;
                min-height: 28px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QPushButton:checked {
                background-color: #28a745;
            }
            QDoubleSpinBox, QSpinBox {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #ced4da;
                padding: 8px;
                border-radius: 5px;
                font-size: 11px;
                min-height: 24px;
            }
            QDoubleSpinBox:focus, QSpinBox:focus {
                border: 2px solid #007bff;
            }
            QCheckBox {
                color: #333333;
                font-size: 11px;
                padding: 4px;
                min-height: 20px;
            }
            QCheckBox::indicator:checked {
                background-color: #007bff;
                border: 1px solid #0056b3;
            }
            QRadioButton {
                color: #333333;
                font-size: 11px;
                padding: 4px;
                min-height: 20px;
            }
            QRadioButton::indicator:checked {
                background-color: #007bff;
                border: 1px solid #0056b3;
            }
        """)
        
        # 创建左侧浮游模式控制区域
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(11)
        
        # 创建右侧轮式和清洗模式控制区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(11)
        
        # 添加各个控制组到对应区域
        self.create_floating_control_group(left_layout)
        self.create_navigation_control_group(left_layout)
        
        self.create_wheel_control_group(right_layout)
        self.create_wheel_navigation_control_group(right_layout)
        self.create_brush_control_group(right_layout)
        
        # 添加键盘控制组件
        self.keyboard_control_widget = KeyboardControlWidget(self.keyboard_controller)
        right_layout.addWidget(self.keyboard_control_widget)
        
        # 创建状态指示器（在所有组件创建后）
        self.create_status_indicators()
        
        # 添加弹性空间
        left_layout.addStretch()
        right_layout.addStretch()
        
        # 将左右区域添加到主布局，比例为1:1
        content_layout.addWidget(left_widget, 1)
        content_layout.addWidget(right_widget, 1)
        
    def create_floating_control_group(self, parent_layout):
        """创建浮游模式控制组"""
        self.floating_group = QGroupBox("🌊 浮游模式控制")
        layout = QGridLayout(self.floating_group)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 16, 12, 12)
        
        # 线速度控制（带输入验证）
        self.vel_x_slider = QSlider(Qt.Horizontal)
        self.vel_x_slider.setRange(-100, 100)
        self.vel_x_slider.setValue(0)
        self.vel_x_spinbox = QDoubleSpinBox()
        self.vel_x_spinbox.setRange(-2.0, 2.0)
        self.vel_x_spinbox.setSingleStep(0.1)
        self.vel_x_spinbox.setDecimals(2)
        self.vel_x_spinbox.setToolTip("X线速度范围: -2.0 ~ 2.0 m/s")
        self.vel_x_spinbox.setStyleSheet("QDoubleSpinBox { border: 2px solid #28a745; }")
        
        self.vel_y_slider = QSlider(Qt.Horizontal)
        self.vel_y_slider.setRange(-100, 100)
        self.vel_y_slider.setValue(0)
        self.vel_y_spinbox = QDoubleSpinBox()
        self.vel_y_spinbox.setRange(-2.0, 2.0)
        self.vel_y_spinbox.setSingleStep(0.1)
        self.vel_y_spinbox.setDecimals(2)
        self.vel_y_spinbox.setToolTip("Y线速度范围: -2.0 ~ 2.0 m/s")
        self.vel_y_spinbox.setStyleSheet("QDoubleSpinBox { border: 2px solid #28a745; }")
        
        self.vel_z_slider = QSlider(Qt.Horizontal)
        self.vel_z_slider.setRange(-100, 100)
        self.vel_z_slider.setValue(0)
        self.vel_z_spinbox = QDoubleSpinBox()
        self.vel_z_spinbox.setRange(-2.0, 2.0)
        self.vel_z_spinbox.setSingleStep(0.1)
        self.vel_z_spinbox.setDecimals(2)
        self.vel_z_spinbox.setToolTip("Z线速度范围: -2.0 ~ 2.0 m/s")
        self.vel_z_spinbox.setStyleSheet("QDoubleSpinBox { border: 2px solid #28a745; }")
        
        # 角度控制（带输入验证）
        self.ang_roll_slider = QSlider(Qt.Horizontal)
        self.ang_roll_slider.setRange(-180, 180)
        self.ang_roll_slider.setValue(0)
        self.ang_roll_spinbox = QDoubleSpinBox()
        self.ang_roll_spinbox.setRange(-180.0, 180.0)
        self.ang_roll_spinbox.setSingleStep(1.0)
        self.ang_roll_spinbox.setDecimals(1)
        self.ang_roll_spinbox.setToolTip("横滚角度范围: -180.0 ~ 180.0 °")
        self.ang_roll_spinbox.setStyleSheet("QDoubleSpinBox { border: 2px solid #ffc107; }")
        
        self.ang_yaw_slider = QSlider(Qt.Horizontal)
        self.ang_yaw_slider.setRange(-180, 180)
        self.ang_yaw_slider.setValue(0)
        self.ang_yaw_spinbox = QDoubleSpinBox()
        self.ang_yaw_spinbox.setRange(-180.0, 180.0)
        self.ang_yaw_spinbox.setSingleStep(1.0)
        self.ang_yaw_spinbox.setDecimals(1)
        self.ang_yaw_spinbox.setToolTip("偏航角度范围: -180.0 ~ 180.0 °")
        self.ang_yaw_spinbox.setStyleSheet("QDoubleSpinBox { border: 2px solid #ffc107; }")
        
        self.ang_pitch_slider = QSlider(Qt.Horizontal)
        self.ang_pitch_slider.setRange(-180, 180)
        self.ang_pitch_slider.setValue(0)
        self.ang_pitch_spinbox = QDoubleSpinBox()
        self.ang_pitch_spinbox.setRange(-180.0, 180.0)
        self.ang_pitch_spinbox.setSingleStep(1.0)
        self.ang_pitch_spinbox.setDecimals(1)
        self.ang_pitch_spinbox.setToolTip("俯仰角度范围: -180.0 ~ 180.0 °")
        self.ang_pitch_spinbox.setStyleSheet("QDoubleSpinBox { border: 2px solid #ffc107; }")
        
        # 深度控制（带输入验证）
        self.depth_hold_checkbox = QCheckBox("定深功能")
        self.target_depth_spinbox = QDoubleSpinBox()
        self.target_depth_spinbox.setRange(0.0, 100.0)
        self.target_depth_spinbox.setSingleStep(0.1)
        self.target_depth_spinbox.setDecimals(2)
        self.target_depth_spinbox.setToolTip("目标深度范围: 0.0 ~ 100.0 m")
        self.target_depth_spinbox.setStyleSheet("QDoubleSpinBox { border: 2px solid #17a2b8; }")
        
        # 定航控制
        self.heading_hold_checkbox = QCheckBox("定向功能")
        self.target_roll_spinbox = QDoubleSpinBox()
        self.target_roll_spinbox.setRange(-180.0, 180.0)
        self.target_roll_spinbox.setSingleStep(1.0)
        self.target_roll_spinbox.setDecimals(1)
        
        self.target_yaw_spinbox = QDoubleSpinBox()
        self.target_yaw_spinbox.setRange(-180.0, 180.0)
        self.target_yaw_spinbox.setSingleStep(1.0)
        self.target_yaw_spinbox.setDecimals(1)
        
        self.target_pitch_spinbox = QDoubleSpinBox()
        self.target_pitch_spinbox.setRange(-180.0, 180.0)
        self.target_pitch_spinbox.setSingleStep(1.0)
        self.target_pitch_spinbox.setDecimals(1)
        
        # 连接信号
        self.vel_x_slider.valueChanged.connect(lambda v: self.vel_x_spinbox.setValue(v/20.0))
        self.vel_x_spinbox.valueChanged.connect(lambda v: self.vel_x_slider.setValue(int(v*20)))
        self.vel_y_slider.valueChanged.connect(lambda v: self.vel_y_spinbox.setValue(v/20.0))
        self.vel_y_spinbox.valueChanged.connect(lambda v: self.vel_y_slider.setValue(int(v*20)))
        self.vel_z_slider.valueChanged.connect(lambda v: self.vel_z_spinbox.setValue(v/20.0))
        self.vel_z_spinbox.valueChanged.connect(lambda v: self.vel_z_slider.setValue(int(v*20)))
        
        self.ang_roll_slider.valueChanged.connect(lambda v: self.ang_roll_spinbox.setValue(v))
        self.ang_roll_spinbox.valueChanged.connect(lambda v: self.ang_roll_slider.setValue(int(v)))
        self.ang_yaw_slider.valueChanged.connect(lambda v: self.ang_yaw_spinbox.setValue(v))
        self.ang_yaw_spinbox.valueChanged.connect(lambda v: self.ang_yaw_slider.setValue(int(v)))
        self.ang_pitch_slider.valueChanged.connect(lambda v: self.ang_pitch_spinbox.setValue(v))
        self.ang_pitch_spinbox.valueChanged.connect(lambda v: self.ang_pitch_slider.setValue(int(v)))
        
        # 连接数据更新信号
        self.vel_x_spinbox.valueChanged.connect(self.update_floating_commands)
        self.vel_y_spinbox.valueChanged.connect(self.update_floating_commands)
        self.vel_z_spinbox.valueChanged.connect(self.update_floating_commands)
        self.ang_roll_spinbox.valueChanged.connect(self.update_floating_commands)
        self.ang_yaw_spinbox.valueChanged.connect(self.update_floating_commands)
        self.ang_pitch_spinbox.valueChanged.connect(self.update_floating_commands)
        self.depth_hold_checkbox.toggled.connect(self.update_floating_commands)
        self.target_depth_spinbox.valueChanged.connect(self.update_floating_commands)
        self.heading_hold_checkbox.toggled.connect(self.update_floating_commands)
        self.target_roll_spinbox.valueChanged.connect(self.update_floating_commands)
        self.target_yaw_spinbox.valueChanged.connect(self.update_floating_commands)
        self.target_pitch_spinbox.valueChanged.connect(self.update_floating_commands)
        
        # 创建3行2列的网格布局
        # 第一行：X线速度和横滚角度
        layout.addWidget(QLabel("X线速度:"), 0, 0)
        layout.addWidget(self.vel_x_slider, 0, 1)
        layout.addWidget(self.vel_x_spinbox, 0, 2)
        layout.addWidget(QLabel("m/s"), 0, 3)
        
        layout.addWidget(QLabel("横滚角度:"), 0, 4)
        layout.addWidget(self.ang_roll_slider, 0, 5)
        layout.addWidget(self.ang_roll_spinbox, 0, 6)
        layout.addWidget(QLabel("°"), 0, 7)
        
        # 第二行：Y线速度和偏航角度
        layout.addWidget(QLabel("Y线速度:"), 1, 0)
        layout.addWidget(self.vel_y_slider, 1, 1)
        layout.addWidget(self.vel_y_spinbox, 1, 2)
        layout.addWidget(QLabel("m/s"), 1, 3)
        
        layout.addWidget(QLabel("偏航角度:"), 1, 4)
        layout.addWidget(self.ang_yaw_slider, 1, 5)
        layout.addWidget(self.ang_yaw_spinbox, 1, 6)
        layout.addWidget(QLabel("°"), 1, 7)
        
        # 第三行：Z线速度和俯仰角度
        layout.addWidget(QLabel("Z线速度:"), 2, 0)
        layout.addWidget(self.vel_z_slider, 2, 1)
        layout.addWidget(self.vel_z_spinbox, 2, 2)
        layout.addWidget(QLabel("m/s"), 2, 3)
        
        layout.addWidget(QLabel("俯仰角度:"), 2, 4)
        layout.addWidget(self.ang_pitch_slider, 2, 5)
        layout.addWidget(self.ang_pitch_spinbox, 2, 6)
        layout.addWidget(QLabel("°"), 2, 7)
        
        # 定深和定航控件已移至独立的导航控制组
        
        # 添加快捷操作按钮区域
        self.create_floating_quick_buttons(layout)
        
        parent_layout.addWidget(self.floating_group)
    
    def create_navigation_control_group(self, parent_layout):
        """创建导航控制组（定深定航）"""
        self.navigation_group = QGroupBox("🧭 浮游导航控制")
        layout = QGridLayout(self.navigation_group)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 16, 12, 12)
        
        # 定深控制
        self.depth_hold_checkbox = QCheckBox("定深开关")
        self.depth_hold_checkbox.setToolTip("启用/禁用深度保持功能")
        self.depth_hold_checkbox.setStyleSheet("QCheckBox { font-weight: bold; }")
        
        self.target_depth_spinbox = QDoubleSpinBox()
        self.target_depth_spinbox.setRange(0.0, 50.0)
        self.target_depth_spinbox.setSingleStep(0.1)
        self.target_depth_spinbox.setDecimals(2)
        self.target_depth_spinbox.setToolTip("目标深度范围: 0.0 ~ 50.0 m")
        self.target_depth_spinbox.setStyleSheet("QDoubleSpinBox { border: 2px solid #17a2b8; }")
        
        # 定航控制
        self.heading_hold_checkbox = QCheckBox("定航开关")
        self.heading_hold_checkbox.setToolTip("启用/禁用航向保持功能")
        self.heading_hold_checkbox.setStyleSheet("QCheckBox { font-weight: bold; }")
        
        # 目标角度控件
        self.target_roll_spinbox = QDoubleSpinBox()
        self.target_roll_spinbox.setRange(-180.0, 180.0)
        self.target_roll_spinbox.setSingleStep(1.0)
        self.target_roll_spinbox.setDecimals(1)
        self.target_roll_spinbox.setToolTip("目标横滚角范围: -180.0 ~ 180.0°")
        self.target_roll_spinbox.setStyleSheet("QDoubleSpinBox { border: 2px solid #ffc107; }")
        
        self.target_yaw_spinbox = QDoubleSpinBox()
        self.target_yaw_spinbox.setRange(-180.0, 180.0)
        self.target_yaw_spinbox.setSingleStep(1.0)
        self.target_yaw_spinbox.setDecimals(1)
        self.target_yaw_spinbox.setToolTip("目标偏航角范围: -180.0 ~ 180.0°")
        self.target_yaw_spinbox.setStyleSheet("QDoubleSpinBox { border: 2px solid #ffc107; }")
        
        self.target_pitch_spinbox = QDoubleSpinBox()
        self.target_pitch_spinbox.setRange(-180.0, 180.0)
        self.target_pitch_spinbox.setSingleStep(1.0)
        self.target_pitch_spinbox.setDecimals(1)
        self.target_pitch_spinbox.setToolTip("目标俯仰角范围: -180.0 ~ 180.0°")
        self.target_pitch_spinbox.setStyleSheet("QDoubleSpinBox { border: 2px solid #ffc107; }")
        
        # 布局安排 - 2行布局
        # 第一行：定深开关和目标深度
        layout.addWidget(self.depth_hold_checkbox, 0, 0)
        layout.addWidget(QLabel("目标深度:"), 0, 1)
        layout.addWidget(self.target_depth_spinbox, 0, 2)
        layout.addWidget(QLabel("m"), 0, 3)
        
        # 第二行：定航开关和目标角度
        layout.addWidget(self.heading_hold_checkbox, 1, 0)
        layout.addWidget(QLabel("横滚角:"), 1, 1)
        layout.addWidget(self.target_roll_spinbox, 1, 2)
        layout.addWidget(QLabel("°"), 1, 3)
        layout.addWidget(QLabel("偏航角:"), 1, 4)
        layout.addWidget(self.target_yaw_spinbox, 1, 5)
        layout.addWidget(QLabel("°"), 1, 6)
        layout.addWidget(QLabel("俯仰角:"), 1, 7)
        layout.addWidget(self.target_pitch_spinbox, 1, 8)
        layout.addWidget(QLabel("°"), 1, 9)
        
        # 连接信号
        self.depth_hold_checkbox.toggled.connect(self.update_floating_commands)
        self.target_depth_spinbox.valueChanged.connect(self.update_floating_commands)
        self.heading_hold_checkbox.toggled.connect(self.update_floating_commands)
        self.target_roll_spinbox.valueChanged.connect(self.update_floating_commands)
        self.target_yaw_spinbox.valueChanged.connect(self.update_floating_commands)
        self.target_pitch_spinbox.valueChanged.connect(self.update_floating_commands)
        
        parent_layout.addWidget(self.navigation_group)
    
    def create_floating_quick_buttons(self, layout):
        """创建浮游模式快捷操作按钮"""
        # 创建按钮容器
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 12, 0, 4)
        button_layout.setSpacing(12)
        
        # 停止所有运动按钮
        self.stop_all_btn = QPushButton("🛑 停止所有")
        self.stop_all_btn.setToolTip("立即停止所有运动")
        self.stop_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                min-height: 40px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.stop_all_btn.clicked.connect(self.stop_all_motion)
        
        # 水平悬停按钮
        self.hover_btn = QPushButton("🎯 水平悬停")
        self.hover_btn.setToolTip("设置为水平悬停状态")
        self.hover_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                min-height: 40px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.hover_btn.clicked.connect(self.set_hover_mode)
        
        # 快速上浮按钮
        self.ascend_btn = QPushButton("⬆️ 快速上浮")
        self.ascend_btn.setToolTip("以最大速度上浮")
        self.ascend_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                min-height: 40px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        self.ascend_btn.clicked.connect(self.quick_ascend)
        
        # 快速下潜按钮
        self.descend_btn = QPushButton("⬇️ 快速下潜")
        self.descend_btn.setToolTip("以最大速度下潜")
        self.descend_btn.setStyleSheet("""
            QPushButton {
                background-color: #6f42c1;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                min-height: 40px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5a32a3;
            }
        """)
        self.descend_btn.clicked.connect(self.quick_descend)
        
        # 添加按钮到布局
        button_layout.addWidget(self.stop_all_btn)
        button_layout.addWidget(self.hover_btn)
        button_layout.addWidget(self.ascend_btn)
        button_layout.addWidget(self.descend_btn)
        button_layout.addStretch()
        
        # 将按钮容器添加到主布局
        layout.addWidget(button_frame, 10, 0, 1, 4)
        
    def create_wheel_control_group(self, parent_layout):
        """创建轮式模式控制组"""
        self.wheel_group = QGroupBox("🚗 轮式模式控制")
        layout = QGridLayout(self.wheel_group)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 16, 12, 12)
        
        # 线速度控制（带输入验证）
        self.wheel_linear_slider = QSlider(Qt.Horizontal)
        self.wheel_linear_slider.setRange(-100, 100)
        self.wheel_linear_slider.setValue(0)
        self.wheel_linear_spinbox = QDoubleSpinBox()
        self.wheel_linear_spinbox.setRange(-1.5, 1.5)
        self.wheel_linear_spinbox.setSingleStep(0.1)
        self.wheel_linear_spinbox.setDecimals(2)
        self.wheel_linear_spinbox.setToolTip("轮式线速度范围: -1.5 ~ 1.5 m/s")
        self.wheel_linear_spinbox.setStyleSheet("QDoubleSpinBox { border: 2px solid #28a745; }")
        
        # 角速度控制（带输入验证）
        self.wheel_angular_slider = QSlider(Qt.Horizontal)
        self.wheel_angular_slider.setRange(-100, 100)
        self.wheel_angular_slider.setValue(0)
        self.wheel_angular_spinbox = QDoubleSpinBox()
        self.wheel_angular_spinbox.setRange(-3.14, 3.14)
        self.wheel_angular_spinbox.setSingleStep(0.1)
        self.wheel_angular_spinbox.setDecimals(2)
        self.wheel_angular_spinbox.setToolTip("轮式角速度范围: -3.14 ~ 3.14 rad/s")
        self.wheel_angular_spinbox.setStyleSheet("QDoubleSpinBox { border: 2px solid #ffc107; }")
        
        # 定向功能已移至独立的轮式定向控制组
        
        # 连接信号
        self.wheel_linear_slider.valueChanged.connect(lambda v: self.wheel_linear_spinbox.setValue(v/20.0))
        self.wheel_linear_spinbox.valueChanged.connect(lambda v: self.wheel_linear_slider.setValue(int(v*20)))
        self.wheel_angular_slider.valueChanged.connect(lambda v: self.wheel_angular_spinbox.setValue(v/31.4))
        self.wheel_angular_spinbox.valueChanged.connect(lambda v: self.wheel_angular_slider.setValue(int(v*31.4)))
        
        # 连接数据更新信号
        self.wheel_linear_spinbox.valueChanged.connect(self.update_wheel_commands)
        self.wheel_angular_spinbox.valueChanged.connect(self.update_wheel_commands)
        
        # 1行2列布局：线速度和角速度并排
        layout.addWidget(QLabel("线速度:"), 0, 0)
        layout.addWidget(self.wheel_linear_slider, 0, 1)
        layout.addWidget(self.wheel_linear_spinbox, 0, 2)
        layout.addWidget(QLabel("m/s"), 0, 3)
        
        layout.addWidget(QLabel("角速度:"), 0, 4)
        layout.addWidget(self.wheel_angular_slider, 0, 5)
        layout.addWidget(self.wheel_angular_spinbox, 0, 6)
        layout.addWidget(QLabel("rad/s"), 0, 7)
        
        parent_layout.addWidget(self.wheel_group)
    
    def create_wheel_navigation_control_group(self, parent_layout):
        """创建轮式定向控制组"""
        self.wheel_navigation_group = QGroupBox("🧭 轮式定向控制")
        layout = QGridLayout(self.wheel_navigation_group)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 16, 12, 12)
        
        # 定向控制
        self.wheel_heading_hold_checkbox = QCheckBox("定向开关")
        self.wheel_heading_hold_checkbox.setToolTip("启用/禁用轮式定向功能")
        self.wheel_heading_hold_checkbox.setStyleSheet("QCheckBox { font-weight: bold; }")
        
        self.wheel_target_heading_spinbox = QDoubleSpinBox()
        self.wheel_target_heading_spinbox.setRange(-180.0, 180.0)
        self.wheel_target_heading_spinbox.setSingleStep(1.0)
        self.wheel_target_heading_spinbox.setDecimals(1)
        self.wheel_target_heading_spinbox.setToolTip("目标方向范围: -180.0 ~ 180.0°")
        self.wheel_target_heading_spinbox.setStyleSheet("QDoubleSpinBox { border: 2px solid #ffc107; }")
        
        # 连接数据更新信号
        self.wheel_heading_hold_checkbox.toggled.connect(self.update_wheel_commands)
        self.wheel_target_heading_spinbox.valueChanged.connect(self.update_wheel_commands)
        
        # 布局安排 - 1行布局
        layout.addWidget(self.wheel_heading_hold_checkbox, 0, 0)
        layout.addWidget(QLabel("目标方向:"), 0, 1)
        layout.addWidget(self.wheel_target_heading_spinbox, 0, 2)
        layout.addWidget(QLabel("°"), 0, 3)
        
        parent_layout.addWidget(self.wheel_navigation_group)
        
    def create_brush_control_group(self, parent_layout):
        """创建清洗功能控制组"""
        group = QGroupBox("🧽 清洗功能控制")
        layout = QGridLayout(group)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 16, 12, 12)
        
        # 滚刷控制（带输入验证）
        self.brush_enable_checkbox = QCheckBox("滚刷开关")
        self.brush_enable_checkbox.setStyleSheet("QCheckBox { font-weight: bold; }")
        self.brush_power_slider = QSlider(Qt.Horizontal)
        self.brush_power_slider.setRange(0, 100)
        self.brush_power_slider.setValue(0)
        self.brush_power_spinbox = QSpinBox()
        self.brush_power_spinbox.setRange(0, 100)
        self.brush_power_spinbox.setSuffix("%")
        self.brush_power_spinbox.setToolTip("滚刷功率范围: 0 ~ 100%")
        self.brush_power_spinbox.setStyleSheet("QSpinBox { border: 2px solid #dc3545; }")
        
        # 水流控制（带输入验证）
        self.water_enable_checkbox = QCheckBox("水流开关")
        self.water_enable_checkbox.setStyleSheet("QCheckBox { font-weight: bold; }")
        self.water_flow_slider = QSlider(Qt.Horizontal)
        self.water_flow_slider.setRange(0, 100)
        self.water_flow_slider.setValue(0)
        self.water_flow_spinbox = QSpinBox()
        self.water_flow_spinbox.setRange(0, 100)
        self.water_flow_spinbox.setSuffix("%")
        self.water_flow_spinbox.setToolTip("水流强度范围: 0 ~ 100%")
        self.water_flow_spinbox.setStyleSheet("QSpinBox { border: 2px solid #17a2b8; }")
        
        # 连接信号
        self.brush_power_slider.valueChanged.connect(self.brush_power_spinbox.setValue)
        self.brush_power_spinbox.valueChanged.connect(self.brush_power_slider.setValue)
        self.water_flow_slider.valueChanged.connect(self.water_flow_spinbox.setValue)
        self.water_flow_spinbox.valueChanged.connect(self.water_flow_slider.setValue)
        
        # 连接数据更新信号
        self.brush_enable_checkbox.toggled.connect(self.update_brush_commands)
        self.brush_power_spinbox.valueChanged.connect(self.update_brush_commands)
        self.water_enable_checkbox.toggled.connect(self.update_brush_commands)
        self.water_flow_spinbox.valueChanged.connect(self.update_brush_commands)
        
        # 1行2列布局：滚刷控制和水流控制并排
        layout.addWidget(self.brush_enable_checkbox, 0, 0)
        layout.addWidget(QLabel("滚刷功率:"), 0, 1)
        layout.addWidget(self.brush_power_slider, 0, 2)
        layout.addWidget(self.brush_power_spinbox, 0, 3)
        
        # 添加空白间距
        spacer = QWidget()
        spacer.setFixedWidth(20)
        layout.addWidget(spacer, 0, 4)
        
        layout.addWidget(self.water_enable_checkbox, 0, 5)
        layout.addWidget(QLabel("水流强度:"), 0, 6)
        layout.addWidget(self.water_flow_slider, 0, 7)
        layout.addWidget(self.water_flow_spinbox, 0, 8)
        
        parent_layout.addWidget(group)
        
    def setup_shortcuts(self):
        """设置快捷键"""
        # 快捷键已通过按钮实现，此方法保留用于未来扩展
        pass
    
    # 浮游模式快捷操作方法
    def stop_all_motion(self):
        """停止所有运动"""
        logging.info("执行停止所有运动")
        self.vel_x_spinbox.setValue(0.0)
        self.vel_y_spinbox.setValue(0.0)
        self.vel_z_spinbox.setValue(0.0)
        self.ang_roll_spinbox.setValue(0.0)
        self.ang_yaw_spinbox.setValue(0.0)
        self.ang_pitch_spinbox.setValue(0.0)
    
    def set_hover_mode(self):
        """设置水平悬停模式"""
        logging.info("设置水平悬停模式")
        # 停止所有线速度和角速度
        self.vel_x_spinbox.setValue(0.0)
        self.vel_y_spinbox.setValue(0.0)
        self.vel_z_spinbox.setValue(0.0)
        self.ang_roll_spinbox.setValue(0.0)
        self.ang_yaw_spinbox.setValue(0.0)
        self.ang_pitch_spinbox.setValue(0.0)
        
        # 启用定深和定向功能
        self.depth_hold_checkbox.setChecked(True)
        self.heading_hold_checkbox.setChecked(True)
        
        # 设置目标姿态为水平
        self.target_roll_spinbox.setValue(0.0)
        self.target_pitch_spinbox.setValue(0.0)
    
    def quick_ascend(self):
        """快速上浮"""
        logging.info("执行快速上浮")
        # 停止其他运动
        self.vel_x_spinbox.setValue(0.0)
        self.vel_y_spinbox.setValue(0.0)
        self.ang_roll_spinbox.setValue(0.0)
        self.ang_yaw_spinbox.setValue(0.0)
        self.ang_pitch_spinbox.setValue(0.0)
        
        # 设置最大上浮速度
        self.vel_z_spinbox.setValue(2.0)  # 最大上浮速度
        
        # 启用定向功能保持水平
        self.heading_hold_checkbox.setChecked(True)
        self.target_roll_spinbox.setValue(0.0)
        self.target_pitch_spinbox.setValue(0.0)
    
    def quick_descend(self):
        """快速下潜"""
        logging.info("执行快速下潜")
        # 停止其他运动
        self.vel_x_spinbox.setValue(0.0)
        self.vel_y_spinbox.setValue(0.0)
        self.ang_roll_spinbox.setValue(0.0)
        self.ang_yaw_spinbox.setValue(0.0)
        self.ang_pitch_spinbox.setValue(0.0)
        
        # 设置最大下潜速度
        self.vel_z_spinbox.setValue(-2.0)  # 最大下潜速度
        
        # 启用定向功能保持水平
        self.heading_hold_checkbox.setChecked(True)
        self.target_roll_spinbox.setValue(0.0)
        self.target_pitch_spinbox.setValue(0.0)
    
        
    def setup_real_time_feedback(self):
        """设置实时反馈"""
        # 设置定时器用于更新状态显示
        from PyQt5.QtCore import QTimer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_indicators)
        self.status_timer.start(self.robot_data.app_dt)  # 使用统一的app_dt参数，50Hz更新一次
        
        logging.info("实时状态反馈系统已启动")
    
    def create_status_indicators(self):
        """创建状态指示器"""
        # 在浮游模式组中添加状态标签
        if hasattr(self, 'floating_group'):
            # 创建状态容器
            status_frame = QFrame()
            status_layout = QHBoxLayout(status_frame)
            status_layout.setContentsMargins(3, 3, 3, 3)
            status_layout.setSpacing(4)
            
            # 浮游模式状态标签
            self.floating_status_label = QLabel("🟢 浮游模式就绪")
            self.floating_status_label.setStyleSheet("""
                QLabel {
                    color: #28a745;
                    font-weight: bold;
                    background-color: #d4edda;
                    padding: 2px 6px;
                    border-radius: 3px;
                    border: 1px solid #c3e6cb;
                }
            """)
            
            # 速度指示器
            self.velocity_indicator = QLabel("速度: 0.0 m/s")
            self.velocity_indicator.setStyleSheet("""
                QLabel {
                    color: #17a2b8;
                    font-weight: bold;
                    background-color: #d1ecf1;
                    padding: 2px 6px;
                    border-radius: 3px;
                    border: 1px solid #bee5eb;
                }
            """)
            
            # 深度状态指示器
            self.depth_status_label = QLabel("深度控制: 关闭")
            self.depth_status_label.setStyleSheet("""
                QLabel {
                    color: #6c757d;
                    font-weight: bold;
                    background-color: #f8f9fa;
                    padding: 2px 6px;
                    border-radius: 3px;
                    border: 1px solid #dee2e6;
                }
            """)
            
            status_layout.addWidget(self.floating_status_label)
            status_layout.addWidget(self.velocity_indicator)
            status_layout.addWidget(self.depth_status_label)
            status_layout.addStretch()
            
            # 将状态容器添加到浮游模式组的布局中
            floating_layout = self.floating_group.layout()
            floating_layout.addWidget(status_frame, 11, 0, 1, 4)
        
        # 在轮式模式组中添加状态标签
        if hasattr(self, 'wheel_group'):
            # 创建轮式状态容器
            wheel_status_frame = QFrame()
            wheel_status_layout = QHBoxLayout(wheel_status_frame)
            wheel_status_layout.setContentsMargins(3, 3, 3, 3)
            wheel_status_layout.setSpacing(4)
            
            # 轮式模式状态标签
            self.wheel_status_label = QLabel("🟢 轮式模式就绪")
            self.wheel_status_label.setStyleSheet("""
                QLabel {
                    color: #28a745;
                    font-weight: bold;
                    background-color: #d4edda;
                    padding: 2px 6px;
                    border-radius: 3px;
                    border: 1px solid #c3e6cb;
                }
            """)
            
            # 轮式速度指示器
            self.wheel_velocity_indicator = QLabel("线速度: 0.0 m/s | 角速度: 0.0 rad/s")
            self.wheel_velocity_indicator.setStyleSheet("""
                QLabel {
                    color: #fd7e14;
                    font-weight: bold;
                    background-color: #fff3cd;
                    padding: 2px 6px;
                    border-radius: 3px;
                    border: 1px solid #ffeaa7;
                }
            """)
            
            wheel_status_layout.addWidget(self.wheel_status_label)
            wheel_status_layout.addWidget(self.wheel_velocity_indicator)
            wheel_status_layout.addStretch()
            
            # 将状态容器添加到轮式模式组的布局中
            wheel_layout = self.wheel_group.layout()
            wheel_layout.addWidget(wheel_status_frame, 4, 0, 1, 4)
    
    def update_status_indicators(self):
        """更新状态指示器"""
        try:
            # 更新浮游模式状态
            if hasattr(self, 'floating_status_label'):
                # 检查是否有运动
                vel_x = self.vel_x_spinbox.value()
                vel_y = self.vel_y_spinbox.value()
                vel_z = self.vel_z_spinbox.value()
                ang_roll = self.ang_roll_spinbox.value()
                ang_yaw = self.ang_yaw_spinbox.value()
                ang_pitch = self.ang_pitch_spinbox.value()
                
                total_velocity = abs(vel_x) + abs(vel_y) + abs(vel_z)
                total_angular = abs(ang_roll) + abs(ang_yaw) + abs(ang_pitch)
                
                if self.emergency_stop:
                    self.floating_status_label.setText("🛑 紧急停止已激活")
                    self.floating_status_label.setStyleSheet("""
                        QLabel {
                            color: #dc3545;
                            font-weight: bold;
                            background-color: #f8d7da;
                            padding: 4px 8px;
                            border-radius: 4px;
                            border: 1px solid #f5c6cb;
                        }
                    """)
                elif total_velocity > 0.1 or total_angular > 0.1:
                    self.floating_status_label.setText("🔄 浮游模式运行中")
                    self.floating_status_label.setStyleSheet("""
                        QLabel {
                            color: #007bff;
                            font-weight: bold;
                            background-color: #cce7ff;
                            padding: 4px 8px;
                            border-radius: 4px;
                            border: 1px solid #99d3ff;
                        }
                    """)
                else:
                    self.floating_status_label.setText("🟢 浮游模式就绪")
                    self.floating_status_label.setStyleSheet("""
                        QLabel {
                            color: #28a745;
                            font-weight: bold;
                            background-color: #d4edda;
                            padding: 4px 8px;
                            border-radius: 4px;
                            border: 1px solid #c3e6cb;
                        }
                    """)
                
                # 更新速度指示器
                if hasattr(self, 'velocity_indicator'):
                    self.velocity_indicator.setText(f"速度: {total_velocity:.2f} m/s")
                
                # 更新深度控制状态
                if hasattr(self, 'depth_status_label'):
                    if self.depth_hold_checkbox.isChecked():
                        target_depth = self.target_depth_spinbox.value()
                        self.depth_status_label.setText(f"定深: {target_depth:.1f}m")
                        self.depth_status_label.setStyleSheet("""
                            QLabel {
                                color: #17a2b8;
                                font-weight: bold;
                                background-color: #d1ecf1;
                                padding: 4px 8px;
                                border-radius: 4px;
                                border: 1px solid #bee5eb;
                            }
                        """)
                    else:
                        self.depth_status_label.setText("深度控制: 关闭")
                        self.depth_status_label.setStyleSheet("""
                            QLabel {
                                color: #6c757d;
                                font-weight: bold;
                                background-color: #f8f9fa;
                                padding: 4px 8px;
                                border-radius: 4px;
                                border: 1px solid #dee2e6;
                            }
                        """)
            
            # 更新轮式模式状态
            if hasattr(self, 'wheel_status_label'):
                wheel_linear = self.wheel_linear_spinbox.value()
                wheel_angular = self.wheel_angular_spinbox.value()
                
                if abs(wheel_linear) > 0.1 or abs(wheel_angular) > 0.1:
                    self.wheel_status_label.setText("🔄 轮式模式运行中")
                    self.wheel_status_label.setStyleSheet("""
                        QLabel {
                            color: #007bff;
                            font-weight: bold;
                            background-color: #cce7ff;
                            padding: 4px 8px;
                            border-radius: 4px;
                            border: 1px solid #99d3ff;
                        }
                    """)
                else:
                    self.wheel_status_label.setText("🟢 轮式模式就绪")
                    self.wheel_status_label.setStyleSheet("""
                        QLabel {
                            color: #28a745;
                            font-weight: bold;
                            background-color: #d4edda;
                            padding: 4px 8px;
                            border-radius: 4px;
                            border: 1px solid #c3e6cb;
                        }
                    """)
                
                # 更新轮式速度指示器
                if hasattr(self, 'wheel_velocity_indicator'):
                    self.wheel_velocity_indicator.setText(
                        f"线速度: {wheel_linear:.2f} m/s | 角速度: {wheel_angular:.2f} rad/s"
                    )
                    
        except Exception as e:
            logging.error(f"更新状态指示器时出错: {e}")
        
    def setup_keyboard_control(self):
        """设置键盘控制"""
        # 连接键盘控制器的信号到相应的控制函数
        self.keyboard_controller.velocity_changed.connect(self.on_keyboard_velocity_changed)
        self.keyboard_controller.emergency_stop.connect(self.emergency_stop_action)
    
    def on_keyboard_velocity_changed(self, param_name, value):
        """处理键盘控制的速度变化"""
        # 根据参数名更新对应的控制组件
        if param_name == 'vel_x':
            self.vel_x_spinbox.setValue(value)
        elif param_name == 'vel_y':
            self.vel_y_spinbox.setValue(value)
        elif param_name == 'vel_z':
            self.vel_z_spinbox.setValue(value)
        elif param_name == 'ang_roll':
            self.ang_roll_spinbox.setValue(value)
        elif param_name == 'ang_yaw':
            self.ang_yaw_spinbox.setValue(value)
        elif param_name == 'ang_pitch':
            self.ang_pitch_spinbox.setValue(value)
        elif param_name == 'wheel_linear_vel':
            self.wheel_linear_spinbox.setValue(value)
        elif param_name == 'wheel_angular_vel':
            self.wheel_angular_spinbox.setValue(value)
        
        logging.debug(f"键盘控制更新界面: {param_name} = {value}")
    
    def emergency_stop_action(self):
        """紧急停止动作"""
        logging.warning("执行紧急停止")
        self.emergency_stop = True
        
        # 立即停止所有运动
        self.vel_x_spinbox.setValue(0.0)
        self.vel_y_spinbox.setValue(0.0)
        self.vel_z_spinbox.setValue(0.0)
        self.ang_roll_spinbox.setValue(0.0)
        self.ang_yaw_spinbox.setValue(0.0)
        self.ang_pitch_spinbox.setValue(0.0)
        
        # 停止轮式模式运动
        self.wheel_linear_spinbox.setValue(0.0)
        self.wheel_angular_spinbox.setValue(0.0)
        
        # 显示紧急停止状态
        if hasattr(self, 'floating_status_label'):
            self.floating_status_label.setText("🛑 紧急停止已激活")
            self.floating_status_label.setStyleSheet("color: #dc3545; font-weight: bold; background-color: #f8d7da; padding: 2px 6px; border-radius: 3px;")
             
    def update_floating_commands(self):
        """更新浮游模式命令"""
        cmd_data = self.robot_data.get_cmd_data()
        floating_cmd = cmd_data.cmd_floating_mode
        
        floating_cmd.cmd_floating_vel_x = self.vel_x_spinbox.value()
        floating_cmd.cmd_floating_vel_y = self.vel_y_spinbox.value()
        floating_cmd.cmd_floating_vel_z = self.vel_z_spinbox.value()
        floating_cmd.cmd_floating_angular_roll = math.radians(self.ang_roll_spinbox.value())
        floating_cmd.cmd_floating_angular_yaw = math.radians(self.ang_yaw_spinbox.value())
        floating_cmd.cmd_floating_angular_pitch = math.radians(self.ang_pitch_spinbox.value())
        
        floating_cmd.cmd_depth_hold = 1 if self.depth_hold_checkbox.isChecked() else 0
        floating_cmd.cmd_target_depth = self.target_depth_spinbox.value()
        
        floating_cmd.cmd_floating_heading_hold = 1 if self.heading_hold_checkbox.isChecked() else 0
        floating_cmd.cmd_target_roll = math.radians(self.target_roll_spinbox.value())
        floating_cmd.cmd_target_yaw = math.radians(self.target_yaw_spinbox.value())
        floating_cmd.cmd_target_pitch = math.radians(self.target_pitch_spinbox.value())
        
        # 记录浮游模式参数变更到日志
        logging.info(f"浮游模式参数更新: vel_x={floating_cmd.cmd_floating_vel_x}, vel_y={floating_cmd.cmd_floating_vel_y}, vel_z={floating_cmd.cmd_floating_vel_z}, ang_roll={floating_cmd.cmd_floating_angular_roll}, ang_yaw={floating_cmd.cmd_floating_angular_yaw}, ang_pitch={floating_cmd.cmd_floating_angular_pitch}, depth_hold={floating_cmd.cmd_depth_hold}, target_depth={floating_cmd.cmd_target_depth}")
        
    def update_wheel_commands(self):
        """更新轮式模式命令"""
        cmd_data = self.robot_data.get_cmd_data()
        wheel_cmd = cmd_data.cmd_wheel_mode
        
        wheel_cmd.cmd_wheel_linear_vel = self.wheel_linear_spinbox.value()
        wheel_cmd.cmd_wheel_angular_vel = self.wheel_angular_spinbox.value()
        
        wheel_cmd.cmd_wheel_heading_hold = 1 if self.wheel_heading_hold_checkbox.isChecked() else 0
        wheel_cmd.cmd_target_heading = math.radians(self.wheel_target_heading_spinbox.value())
        
        # 记录轮式模式参数变更到日志
        logging.info(f"轮式模式参数更新: linear_vel={wheel_cmd.cmd_wheel_linear_vel}, angular_vel={wheel_cmd.cmd_wheel_angular_vel}, heading_hold={wheel_cmd.cmd_wheel_heading_hold}, target_heading={wheel_cmd.cmd_target_heading}")
        
    def update_brush_commands(self):
        """更新清洗功能命令"""
        cmd_data = self.robot_data.get_cmd_data()
        brush_cmd = cmd_data.cmd_brush
        
        brush_cmd.cmd_brush_enable = 1 if self.brush_enable_checkbox.isChecked() else 0
        brush_cmd.cmd_brush_power = self.brush_power_spinbox.value()
        
        brush_cmd.cmd_water_enable = 1 if self.water_enable_checkbox.isChecked() else 0
        brush_cmd.cmd_water_flow = self.water_flow_spinbox.value()
        
        # 记录清洗功能参数变更到日志
        logging.info(f"清洗功能参数更新: brush_enable={brush_cmd.cmd_brush_enable}, brush_power={brush_cmd.cmd_brush_power}, water_enable={brush_cmd.cmd_water_enable}, water_flow={brush_cmd.cmd_water_flow}")
        
    def update_display(self):
        """更新显示数据"""
        cmd_data = self.robot_data.get_cmd_data()
        
        # 更新浮游模式显示
        floating_cmd = cmd_data.cmd_floating_mode
        self.vel_x_spinbox.blockSignals(True)
        self.vel_x_spinbox.setValue(floating_cmd.cmd_floating_vel_x)
        self.vel_x_spinbox.blockSignals(False)
        
        self.vel_y_spinbox.blockSignals(True)
        self.vel_y_spinbox.setValue(floating_cmd.cmd_floating_vel_y)
        self.vel_y_spinbox.blockSignals(False)
        
        self.vel_z_spinbox.blockSignals(True)
        self.vel_z_spinbox.setValue(floating_cmd.cmd_floating_vel_z)
        self.vel_z_spinbox.blockSignals(False)
        
        self.ang_roll_spinbox.blockSignals(True)
        self.ang_roll_spinbox.setValue(math.degrees(floating_cmd.cmd_floating_angular_roll))
        self.ang_roll_spinbox.blockSignals(False)
        
        self.ang_yaw_spinbox.blockSignals(True)
        self.ang_yaw_spinbox.setValue(math.degrees(floating_cmd.cmd_floating_angular_yaw))
        self.ang_yaw_spinbox.blockSignals(False)
        
        self.ang_pitch_spinbox.blockSignals(True)
        self.ang_pitch_spinbox.setValue(math.degrees(floating_cmd.cmd_floating_angular_pitch))
        self.ang_pitch_spinbox.blockSignals(False)
        
        # 更新浮游导航控制显示
        self.depth_hold_checkbox.blockSignals(True)
        self.depth_hold_checkbox.setChecked(floating_cmd.cmd_depth_hold == 1)
        self.depth_hold_checkbox.blockSignals(False)
        
        self.target_depth_spinbox.blockSignals(True)
        self.target_depth_spinbox.setValue(floating_cmd.cmd_target_depth)
        self.target_depth_spinbox.blockSignals(False)
        
        self.heading_hold_checkbox.blockSignals(True)
        self.heading_hold_checkbox.setChecked(floating_cmd.cmd_floating_heading_hold == 1)
        self.heading_hold_checkbox.blockSignals(False)
        
        self.target_roll_spinbox.blockSignals(True)
        self.target_roll_spinbox.setValue(math.degrees(floating_cmd.cmd_target_roll))
        self.target_roll_spinbox.blockSignals(False)
        
        self.target_yaw_spinbox.blockSignals(True)
        self.target_yaw_spinbox.setValue(math.degrees(floating_cmd.cmd_target_yaw))
        self.target_yaw_spinbox.blockSignals(False)
        
        self.target_pitch_spinbox.blockSignals(True)
        self.target_pitch_spinbox.setValue(math.degrees(floating_cmd.cmd_target_pitch))
        self.target_pitch_spinbox.blockSignals(False)
        
        # 更新轮式模式显示
        wheel_cmd = cmd_data.cmd_wheel_mode
        self.wheel_linear_spinbox.blockSignals(True)
        self.wheel_linear_spinbox.setValue(wheel_cmd.cmd_wheel_linear_vel)
        self.wheel_linear_spinbox.blockSignals(False)
        
        self.wheel_angular_spinbox.blockSignals(True)
        self.wheel_angular_spinbox.setValue(wheel_cmd.cmd_wheel_angular_vel)
        self.wheel_angular_spinbox.blockSignals(False)
        
        # 更新轮式定向控制显示
        self.wheel_heading_hold_checkbox.blockSignals(True)
        self.wheel_heading_hold_checkbox.setChecked(wheel_cmd.cmd_wheel_heading_hold == 1)
        self.wheel_heading_hold_checkbox.blockSignals(False)
        
        self.wheel_target_heading_spinbox.blockSignals(True)
        self.wheel_target_heading_spinbox.setValue(math.degrees(wheel_cmd.cmd_target_heading))
        self.wheel_target_heading_spinbox.blockSignals(False)
        
        # 更新清洗功能显示
        brush_cmd = cmd_data.cmd_brush
        self.brush_enable_checkbox.blockSignals(True)
        self.brush_enable_checkbox.setChecked(brush_cmd.cmd_brush_enable == 1)
        self.brush_enable_checkbox.blockSignals(False)
        
        self.brush_power_spinbox.blockSignals(True)
        self.brush_power_spinbox.setValue(brush_cmd.cmd_brush_power)
        self.brush_power_spinbox.blockSignals(False)
        
        self.water_enable_checkbox.blockSignals(True)
        self.water_enable_checkbox.setChecked(brush_cmd.cmd_water_enable == 1)
        self.water_enable_checkbox.blockSignals(False)
        
        self.water_flow_spinbox.blockSignals(True)
        self.water_flow_spinbox.setValue(brush_cmd.cmd_water_flow)
        self.water_flow_spinbox.blockSignals(False)