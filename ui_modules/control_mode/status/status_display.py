#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器人状态显示模块
显示机器人的位置、姿态、速度、推进器、电机、系统状态等信息
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QFrame, QGroupBox, QScrollArea, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize, QRectF
from PyQt5.QtGui import QFont, QPalette, QPainter
from PyQt5.QtSvg import QSvgRenderer
import math
import os
from pathlib import Path

class RotatingSvgWidget(QWidget):
    """用于显示并根据角度旋转的SVG绘制组件"""
    def __init__(self, svg_path: str, size: QSize = QSize(120, 120), parent=None):
        super().__init__(parent)
        self._renderer = None
        self._angle_deg = 0.0
        self._size = size
        self.setFixedSize(self._size)
        self.set_svg(svg_path)

    def set_svg(self, svg_path: str):
        if svg_path and os.path.exists(svg_path):
            self._renderer = QSvgRenderer(svg_path)
            self.update()
        else:
            self._renderer = None
            self.update()

    def set_angle(self, angle_deg: float):
        if abs(angle_deg - self._angle_deg) > 0.01:
            self._angle_deg = angle_deg
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        if not self._renderer or not self._renderer.isValid():
            # 无资源时画一个占位圆圈
            painter.setPen(Qt.gray)
            painter.drawEllipse(2, 2, self.width()-4, self.height()-4)
            return
        # 以中心旋转
        cx, cy = self.width() / 2.0, self.height() / 2.0
        painter.translate(cx, cy)
        painter.rotate(self._angle_deg)
        painter.translate(-cx, -cy)
        # 将SVG等比渲染至当前区域
        self._renderer.render(painter, QRectF(self.rect()))
        painter.end()

class CompositeHsiWidget(QWidget):
    """复合HSI组件：固定背景 + 旋转前景"""
    def __init__(self, background_path: str, foreground_path: str, size: QSize = QSize(120, 120), parent=None):
        super().__init__(parent)
        self._background_renderer = None
        self._foreground_renderer = None
        self._angle_deg = 0.0
        self._size = size
        self.setFixedSize(self._size)
        self.set_background(background_path)
        self.set_foreground(foreground_path)

    def set_background(self, svg_path: str):
        if svg_path and os.path.exists(svg_path):
            self._background_renderer = QSvgRenderer(svg_path)
            self.update()
        else:
            self._background_renderer = None
            self.update()

    def set_foreground(self, svg_path: str):
        if svg_path and os.path.exists(svg_path):
            self._foreground_renderer = QSvgRenderer(svg_path)
            self.update()
        else:
            self._foreground_renderer = None
            self.update()

    def set_angle(self, angle_deg: float):
        if abs(angle_deg - self._angle_deg) > 0.01:
            self._angle_deg = angle_deg
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # 绘制固定背景
        if self._background_renderer and self._background_renderer.isValid():
            self._background_renderer.render(painter, QRectF(self.rect()))
        
        # 绘制旋转前景
        if self._foreground_renderer and self._foreground_renderer.isValid():
            cx, cy = self.width() / 2.0, self.height() / 2.0
            painter.translate(cx, cy)
            painter.rotate(self._angle_deg)
            painter.translate(-cx, -cy)
            self._foreground_renderer.render(painter, QRectF(self.rect()))
        
        # 如果都没有资源，画占位圆圈
        if (not self._background_renderer or not self._background_renderer.isValid()) and \
           (not self._foreground_renderer or not self._foreground_renderer.isValid()):
            painter.setPen(Qt.gray)
            painter.drawEllipse(2, 2, self.width()-4, self.height()-4)
        
        painter.end()

class CompositeAdiWidget(QWidget):
    """复合ADI组件：多层固定背景 + 旋转前景"""
    def __init__(self, back_path: str, face_path: str, ring_path: str, case_path: str, size: QSize = QSize(120, 120), parent=None):
        super().__init__(parent)
        self._back_renderer = None
        self._face_renderer = None
        self._ring_renderer = None
        self._case_renderer = None
        self._angle_deg = 0.0
        self._size = size
        self.setFixedSize(self._size)
        self.set_back(back_path)
        self.set_face(face_path)
        self.set_ring(ring_path)
        self.set_case(case_path)

    def set_back(self, svg_path: str):
        if svg_path and os.path.exists(svg_path):
            self._back_renderer = QSvgRenderer(svg_path)
            self.update()
        else:
            self._back_renderer = None
            self.update()

    def set_face(self, svg_path: str):
        if svg_path and os.path.exists(svg_path):
            self._face_renderer = QSvgRenderer(svg_path)
            self.update()
        else:
            self._face_renderer = None
            self.update()

    def set_ring(self, svg_path: str):
        if svg_path and os.path.exists(svg_path):
            self._ring_renderer = QSvgRenderer(svg_path)
            self.update()
        else:
            self._ring_renderer = None
            self.update()

    def set_case(self, svg_path: str):
        if svg_path and os.path.exists(svg_path):
            self._case_renderer = QSvgRenderer(svg_path)
            self.update()
        else:
            self._case_renderer = None
            self.update()

    def set_angle(self, angle_deg: float):
        if abs(angle_deg - self._angle_deg) > 0.01:
            self._angle_deg = angle_deg
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # 按层次顺序绘制固定背景
        if self._back_renderer and self._back_renderer.isValid():
            self._back_renderer.render(painter, QRectF(self.rect()))
        
        if self._face_renderer and self._face_renderer.isValid():
            self._face_renderer.render(painter, QRectF(self.rect()))
        
        if self._ring_renderer and self._ring_renderer.isValid():
            self._ring_renderer.render(painter, QRectF(self.rect()))
        
        # 绘制旋转前景（case）
        if self._case_renderer and self._case_renderer.isValid():
            cx, cy = self.width() / 2.0, self.height() / 2.0
            painter.translate(cx, cy)
            painter.rotate(self._angle_deg)
            painter.translate(-cx, -cy)
            self._case_renderer.render(painter, QRectF(self.rect()))
        
        # 如果都没有资源，画占位圆圈
        if (not self._back_renderer or not self._back_renderer.isValid()) and \
           (not self._face_renderer or not self._face_renderer.isValid()) and \
           (not self._ring_renderer or not self._ring_renderer.isValid()) and \
           (not self._case_renderer or not self._case_renderer.isValid()):
            painter.setPen(Qt.gray)
            painter.drawEllipse(2, 2, self.width()-4, self.height()-4)
        
        painter.end()

class StatusDisplayWidget(QWidget):
    """机器人状态显示组件"""
    
    def __init__(self, robot_data):
        super().__init__()
        self.robot_data = robot_data
        self.init_ui()
        
    def _resource_path(self, rel_path: str) -> str:
        """智能定位资源路径: 优先cwd相对路径, 不存在则基于项目根(相对当前文件上上上级)"""
        # 相对工作目录
        cand1 = os.path.abspath(rel_path)
        if os.path.exists(cand1):
            return cand1
        # 基于当前文件定位工程根
        proj_root = Path(__file__).resolve().parents[3] if len(Path(__file__).resolve().parents) >= 4 else Path(__file__).resolve().parents[-1]
        cand2 = str((proj_root / rel_path.replace("\\", "/")).resolve())
        return cand2
        
    def init_ui(self):
        """初始化用户界面"""
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 创建内容组件
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        
        # 内容布局
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(1)  # 减少垂直间距
        
        # 设置样式 - 白色现代风格
        self.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                border: none;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: #ffffff;
                color: #333333;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #007bff;
                font-size: 14px;
                font-weight: 700;
            }
            QLabel {
                color: #333333;
                padding: 4px;
                font-size: 12px;
            }
            .value-label {
                color: #28a745;
                font-weight: 700;
                font-size: 13px;
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                padding: 6px 8px;
            }
            .unit-label {
                color: #6c757d;
                font-size: 11px;
                font-weight: 500;
            }
        """)
        
        # 创建紧凑的上部状态组
        compact_layout = QHBoxLayout()
        compact_layout.setSpacing(4)  # 减少水平间距
        
        # 左列状态组
        left_column = QVBoxLayout()
        left_column.setSpacing(6)  # 适中的左列间距
        
        # 创建机器人状态组容器
        robot_status_widget = QWidget()
        robot_status_layout = QVBoxLayout(robot_status_widget)
        robot_status_layout.setContentsMargins(0, 0, 0, 0)
        self.create_robot_status_group(robot_status_layout)
        
        # 创建浮游状态组容器
        floating_status_widget = QWidget()
        floating_status_layout = QVBoxLayout(floating_status_widget)
        floating_status_layout.setContentsMargins(0, 0, 0, 0)
        self.create_floating_status_group(floating_status_layout)
        
        # 添加到左列布局，设置权重为1/3
        left_column.addWidget(robot_status_widget, 2)  # 2权重
        left_column.addWidget(floating_status_widget, 5)  # 5权重
        
        # 右列状态组
        right_column = QVBoxLayout()
        right_column.setSpacing(3)  # 减少右列间距
        
        # 创建姿态视觉组容器
        attitude_visual_widget = QWidget()
        attitude_visual_layout = QVBoxLayout(attitude_visual_widget)
        attitude_visual_layout.setContentsMargins(0, 0, 0, 0)
        self.create_attitude_visual_group(attitude_visual_layout)
        
        # 创建轮式状态组容器
        wheel_status_widget = QWidget()
        wheel_status_layout = QVBoxLayout(wheel_status_widget)
        wheel_status_layout.setContentsMargins(0, 0, 0, 0)
        self.create_wheel_status_group(wheel_status_layout)
        
        # 添加到右列布局，设置权重为5/3
        right_column.addWidget(attitude_visual_widget, 5)  # 5份权重
        right_column.addWidget(wheel_status_widget, 3)    # 3份权重
        # 右列不再放置电磁铁与清洗组，它们将作为底部行统一展示
        
        # 创建左右列容器
        left_widget = QWidget()
        left_widget.setLayout(left_column)
        right_widget = QWidget()
        right_widget.setLayout(right_column)
        
        compact_layout.addWidget(left_widget, 4)  # 左侧占4份
        compact_layout.addWidget(right_widget, 6)  # 右侧占6份
        
        # 添加紧凑布局到主布局
        compact_widget = QWidget()
        compact_widget.setLayout(compact_layout)
        content_layout.addWidget(compact_widget, 8)  # 上部分占8份
        
        # 底部分隔线
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
        content_layout.addWidget(sep)
        
        # 底部功能行（电磁铁 & 清洗）
        self.create_bottom_feature_rows(content_layout)  # 底部占3份（通过权重自动分配）
        
        # 系统状态信息已移动到主界面底部状态栏
        
    def create_robot_status_group(self, parent_layout):
        """创建机器人状态组（两行：第一行X/Y/深度，第二行姿态角）"""
        group = QGroupBox("机器人状态")
        layout = QGridLayout(group)

        # 位置信息
        self.pos_x_label = QLabel("0.00")
        self.pos_y_label = QLabel("0.00")
        self.pos_z_label = QLabel("0.00")

        # 姿态信息
        self.roll_label = QLabel("0.00")
        self.pitch_label = QLabel("0.00")
        self.yaw_label = QLabel("0.00")

        # 统一样式
        for label in [self.pos_x_label, self.pos_y_label, self.pos_z_label,
                      self.roll_label, self.pitch_label, self.yaw_label]:
            label.setProperty("class", "value-label")
            label.setAlignment(Qt.AlignRight)

        # 第一行：X/Y/深度
        layout.addWidget(QLabel("X坐标:"), 0, 0)
        layout.addWidget(self.pos_x_label, 0, 1)
        layout.addWidget(QLabel("m"), 0, 2)

        layout.addWidget(QLabel("Y坐标:"), 0, 3)
        layout.addWidget(self.pos_y_label, 0, 4)
        layout.addWidget(QLabel("m"), 0, 5)

        layout.addWidget(QLabel("深度:"), 0, 6)
        layout.addWidget(self.pos_z_label, 0, 7)
        layout.addWidget(QLabel("m"), 0, 8)

        # 第二行：Roll/Pitch/Yaw
        layout.addWidget(QLabel("横滚角:"), 1, 0)
        layout.addWidget(self.roll_label, 1, 1)
        layout.addWidget(QLabel("°"), 1, 2)

        layout.addWidget(QLabel("俯仰角:"), 1, 3)
        layout.addWidget(self.pitch_label, 1, 4)
        layout.addWidget(QLabel("°"), 1, 5)

        layout.addWidget(QLabel("偏航角:"), 1, 6)
        layout.addWidget(self.yaw_label, 1, 7)
        layout.addWidget(QLabel("°"), 1, 8)

        parent_layout.addWidget(group)
        
    def create_attitude_visual_group(self, parent_layout):
        """创建姿态可视化组(ADI: roll, HSI: yaw)"""
        group = QGroupBox("姿态可视化")
        layout = QHBoxLayout(group)
        layout.setSpacing(12)
        # 资源路径
        adi_back_path = self._resource_path("resource/images/adi/adi_back.svg")
        adi_face_path = self._resource_path("resource/images/adi/adi_face.svg")
        adi_ring_path = self._resource_path("resource/images/adi/adi_ring.svg")
        adi_case_path = self._resource_path("resource/images/adi/adi_case.svg")
        
        hsi_face_path = self._resource_path("resource/images/hsi/hsi_face.svg")
        hsi_case_path = self._resource_path("resource/images/hsi/hsi_case.svg")
        # ADI (roll) - 使用复合组件：多层固定背景 + 旋转前景
        adi_col = QVBoxLayout()
        adi_title = QLabel("横滚")
        adi_title.setStyleSheet("color:#6c757d;font-weight:600;")
        self.adi_widget = CompositeAdiWidget(adi_back_path, adi_face_path, adi_ring_path, adi_case_path, QSize(120,120))
        self.adi_value_label = QLabel("0.0°")
        self.adi_value_label.setProperty("class", "value-label")
        self.adi_value_label.setAlignment(Qt.AlignCenter)
        adi_col.addWidget(adi_title, 0, Qt.AlignHCenter)
        adi_col.addWidget(self.adi_widget, 0, Qt.AlignHCenter)
        adi_col.addWidget(self.adi_value_label, 0, Qt.AlignHCenter)
        # HSI (yaw) - 使用复合组件：固定背景 + 旋转前景
        hsi_col = QVBoxLayout()
        hsi_title = QLabel("偏航")
        hsi_title.setStyleSheet("color:#6c757d;font-weight:600;")
        self.hsi_widget = CompositeHsiWidget(hsi_face_path, hsi_case_path, QSize(120,120))
        self.hsi_value_label = QLabel("0.0°")
        self.hsi_value_label.setProperty("class", "value-label")
        self.hsi_value_label.setAlignment(Qt.AlignCenter)
        hsi_col.addWidget(hsi_title, 0, Qt.AlignHCenter)
        hsi_col.addWidget(self.hsi_widget, 0, Qt.AlignHCenter)
        hsi_col.addWidget(self.hsi_value_label, 0, Qt.AlignHCenter)
        # 添加到组
        col1 = QWidget(); col1.setLayout(adi_col)
        col2 = QWidget(); col2.setLayout(hsi_col)
        layout.addWidget(col1)
        layout.addWidget(col2)
        parent_layout.addWidget(group)
        
    def create_floating_status_group(self, parent_layout):
        """创建浮游模式状态组（隐藏推进器温度显示）"""
        group = QGroupBox("浮游模式状态")
        layout = QGridLayout(group)

        # 速度状态
        self.float_vel_x_label = QLabel("0.00")
        self.float_vel_y_label = QLabel("0.00")
        self.float_vel_z_label = QLabel("0.00")
        self.float_ang_x_label = QLabel("0.00")
        self.float_ang_y_label = QLabel("0.00")
        self.float_ang_z_label = QLabel("0.00")

        # 推进器状态
        self.thruster_power_labels = [QLabel("0.0") for _ in range(4)]
        self.thruster_temp_labels = [QLabel("25.0") for _ in range(4)]  # 仅保留数据，不加入布局

        # 样式
        for label in ([self.float_vel_x_label, self.float_vel_y_label, self.float_vel_z_label,
                       self.float_ang_x_label, self.float_ang_y_label, self.float_ang_z_label] +
                      self.thruster_power_labels):
            label.setProperty("class", "value-label")
            label.setAlignment(Qt.AlignRight)

        # 速度信息
        layout.addWidget(QLabel("X线速度:"), 0, 0)
        layout.addWidget(self.float_vel_x_label, 0, 1)
        layout.addWidget(QLabel("m/s"), 0, 2)

        layout.addWidget(QLabel("Y线速度:"), 1, 0)
        layout.addWidget(self.float_vel_y_label, 1, 1)
        layout.addWidget(QLabel("m/s"), 1, 2)

        layout.addWidget(QLabel("Z线速度:"), 2, 0)
        layout.addWidget(self.float_vel_z_label, 2, 1)
        layout.addWidget(QLabel("m/s"), 2, 2)

        layout.addWidget(QLabel("X角速度:"), 0, 3)
        layout.addWidget(self.float_ang_x_label, 0, 4)
        layout.addWidget(QLabel("rad/s"), 0, 5)

        layout.addWidget(QLabel("Y角速度:"), 1, 3)
        layout.addWidget(self.float_ang_y_label,1, 4)
        layout.addWidget(QLabel("rad/s"), 1, 5)

        layout.addWidget(QLabel("Z角速度:"), 2, 3)
        layout.addWidget(self.float_ang_z_label, 2, 4)
        layout.addWidget(QLabel("rad/s"), 2, 5)
       
        # 第2行：电机数据（同一行3项）
        floating_motor_names = ["前涵推", "右涵推", "后涵推", "左涵推"]

        # 推进器功率（2x2 排列）
        for i in range(4):
            row = 3 + i // 2
            col_offset = (i % 2) * 3
            layout.addWidget(QLabel(floating_motor_names[i]), row, col_offset)
            layout.addWidget(self.thruster_power_labels[i], row, col_offset + 1)
            layout.addWidget(QLabel("%"), row, col_offset + 2)

        parent_layout.addWidget(group)
        
    def create_wheel_status_group(self, parent_layout):
        """创建轮式模式状态组（三行两列：第1列速度信息；第2列电机数据；隐藏电机温度）"""
        group = QGroupBox("轮式模式状态")
        layout = QGridLayout(group)
        layout.setHorizontalSpacing(4)
        layout.setVerticalSpacing(3)
        layout.setContentsMargins(8, 8, 8, 8)

        # 速度状态
        self.wheel_linear_vel_label = QLabel("0.00")
        self.wheel_angular_vel_label = QLabel("0.00")

        # 电机状态（仅数据，隐藏温度）
        self.motor_data_labels = [QLabel("0.0") for _ in range(3)]
        self.motor_temp_labels = [QLabel("25.0") for _ in range(3)]  # 保留数据，不加入布局

        # 统一样式
        for label in ([self.wheel_linear_vel_label, self.wheel_angular_vel_label] + self.motor_data_labels):
            label.setProperty("class", "value-label")
            label.setAlignment(Qt.AlignRight)

        # 第1列：速度信息（垂直排列）
        # 第1行：线速度
        layout.addWidget(QLabel("线速度:"), 0, 0)
        layout.addWidget(self.wheel_linear_vel_label, 0, 1)
        layout.addWidget(QLabel("m/s"), 0, 2)
        
        # 第2行：角速度
        layout.addWidget(QLabel("角速度:"), 1, 0)
        layout.addWidget(self.wheel_angular_vel_label, 1, 1)
        layout.addWidget(QLabel("rad/s"), 1, 2)
        
        # 第2列：电机数据（垂直排列）
        wheel_motor_names = ["舵机角度", "左电机速度", "右电机速度"]
        wheel_motor_units = ["°", "m/s", "m/s"]
        
        # 第1行：舵机角度
        layout.addWidget(QLabel(f"{wheel_motor_names[0]}:"), 0, 3)
        layout.addWidget(self.motor_data_labels[0], 0, 4)
        layout.addWidget(QLabel(wheel_motor_units[0]), 0, 5)
        
        # 第2行：左电机速度
        layout.addWidget(QLabel(f"{wheel_motor_names[1]}:"), 1, 3)
        layout.addWidget(self.motor_data_labels[1], 1, 4)
        layout.addWidget(QLabel(wheel_motor_units[1]), 1, 5)
        
        # 第3行：右电机速度
        layout.addWidget(QLabel(f"{wheel_motor_names[2]}:"), 2, 3)
        layout.addWidget(self.motor_data_labels[2], 2, 4)
        layout.addWidget(QLabel(wheel_motor_units[2]), 2, 5)

        parent_layout.addWidget(group)
        
    def create_bottom_feature_rows(self, parent_layout: QVBoxLayout):
        """在页面底部创建功能行: 电磁铁 与 清洗（优化显示）"""
        group = QGroupBox("其他功能状态")
        vbox = QVBoxLayout(group)
        vbox.setSpacing(4)
        vbox.setContentsMargins(8, 8, 8, 8)

        # 电磁铁行
        em_row = QHBoxLayout(); em_row.setSpacing(12)
        em_title = QLabel("电磁铁")
        em_title.setStyleSheet("color:#6c757d;font-weight:600;")
        self.electromagnet_enable_label = QLabel("关闭")
        self.electromagnet_voltage_label = QLabel("0")
        for lbl in [self.electromagnet_enable_label, self.electromagnet_voltage_label]:
            lbl.setProperty("class", "value-label")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFixedHeight(28)
        em_row.addWidget(em_title)
        em_row.addSpacing(6)
        em_row.addWidget(QLabel("状态"))
        em_row.addWidget(self.electromagnet_enable_label)
        em_row.addSpacing(12)
        em_row.addWidget(QLabel("电压"))
        em_row.addWidget(self.electromagnet_voltage_label)
        em_row.addWidget(QLabel("%"))
        em_row.addStretch(1)

        # 清洗行
        br_row = QHBoxLayout(); br_row.setSpacing(12)
        br_title = QLabel("清   洗")
        br_title.setStyleSheet("color:#6c757d;font-weight:600;")
        self.brush_power_label = QLabel("0")
        self.brush_enable_label = QLabel("关闭")
        self.water_flow_label = QLabel("0")
        self.water_enable_label = QLabel("关闭")
        for lbl in [self.brush_power_label, self.brush_enable_label, self.water_flow_label, self.water_enable_label]:
            lbl.setProperty("class", "value-label")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFixedHeight(28)
        br_row.addWidget(br_title)
        br_row.addSpacing(6)
        br_row.addWidget(QLabel("状态"))
        br_row.addWidget(self.brush_enable_label)

        br_row.addSpacing(12)        
        br_row.addWidget(QLabel("功率"))
        br_row.addWidget(self.brush_power_label)
        br_row.addWidget(QLabel("%"))

        br_row.addSpacing(12)
        br_row.addWidget(QLabel("水流"))
        br_row.addWidget(self.water_enable_label)

        br_row.addSpacing(12)
        br_row.addWidget(QLabel("强度"))
        br_row.addWidget(self.water_flow_label)
        br_row.addWidget(QLabel("%"))
        
        br_row.addStretch(1)

        vbox.addLayout(em_row)
        vbox.addLayout(br_row)
        parent_layout.addWidget(group, 2)  # 底部功能区占3份
        
    def _set_badge_style(self, label: QLabel, enabled: bool):
        """为开关状态设置醒目的徽章样式"""
        if enabled:
            label.setStyleSheet(
                "color:#ffffff;background-color:#28a745;border:1px solid #28a745;"
                "border-radius:6px;padding:6px 8px;font-weight:700;"
            )
        else:
            label.setStyleSheet(
                "color:#495057;background-color:#e9ecef;border:1px solid #dee2e6;"
                "border-radius:6px;padding:6px 8px;font-weight:700;"
            )
        
    def update_display(self):
        """更新显示数据"""
        state_data = self.robot_data.get_state_data()
        
        # 更新机器人状态
        robot_state = state_data.state_robot
        self.pos_x_label.setText(f"{robot_state.sta_position_x:.2f}")
        self.pos_y_label.setText(f"{robot_state.sta_position_y:.2f}")
        self.pos_z_label.setText(f"{robot_state.sta_position_z:.2f}")
        roll_deg = math.degrees(robot_state.sta_roll)
        yaw_deg = math.degrees(robot_state.sta_yaw)
        self.roll_label.setText(f"{roll_deg:.1f}")
        self.pitch_label.setText(f"{math.degrees(robot_state.sta_pitch):.1f}")
        self.yaw_label.setText(f"{yaw_deg:.1f}")
        # 更新可视化
        if hasattr(self, 'adi_widget'):
            self.adi_widget.set_angle(roll_deg)
            self.adi_value_label.setText(f"{roll_deg:.1f}°")
        if hasattr(self, 'hsi_widget'):
            # HSI通常顺时针为正, 若与实际期望相反可取负号
            self.hsi_widget.set_angle(yaw_deg)
            self.hsi_value_label.setText(f"{yaw_deg:.1f}°")
        
        # 更新浮游模式状态
        floating_state = state_data.state_floating_mode
        self.float_vel_x_label.setText(f"{floating_state.sta_floating_vel_x:.2f}")
        self.float_vel_y_label.setText(f"{floating_state.sta_floating_vel_y:.2f}")
        self.float_vel_z_label.setText(f"{floating_state.sta_floating_vel_z:.2f}")
        self.float_ang_x_label.setText(f"{floating_state.sta_floating_angular_x:.2f}")
        self.float_ang_y_label.setText(f"{floating_state.sta_floating_angular_y:.2f}")
        self.float_ang_z_label.setText(f"{floating_state.sta_floating_angular_z:.2f}")
        
        # 更新推进器状态
        for i, (power_label, temp_label) in enumerate(zip(self.thruster_power_labels, self.thruster_temp_labels)):
            if hasattr(floating_state.sta_thruster_power, '__getitem__') and i < len(floating_state.sta_thruster_power):
                power_label.setText(f"{floating_state.sta_thruster_power[i]:.1f}")
            else:
                power_label.setText("0.0")
            if hasattr(floating_state.sta_thruster_temp, '__getitem__') and i < len(floating_state.sta_thruster_temp):
                temp_label.setText(f"{floating_state.sta_thruster_temp[i]:.1f}")
            else:
                temp_label.setText("25.0")
        
        # 更新轮式模式状态
        wheel_state = state_data.state_wheel_mode
        self.wheel_linear_vel_label.setText(f"{wheel_state.sta_wheel_linear_vel:.2f}")
        self.wheel_angular_vel_label.setText(f"{wheel_state.sta_wheel_angular_vel:.2f}")
        
        # 更新电机状态
        for i, (data_label, temp_label) in enumerate(zip(self.motor_data_labels, self.motor_temp_labels)):
            if hasattr(wheel_state.sta_motor_data, '__getitem__') and i < len(wheel_state.sta_motor_data):
                # 舵机角度需要从弧度转换为度数
                if i == 0:  # 舵机角度
                    angle_deg = math.degrees(wheel_state.sta_motor_data[i])
                    data_label.setText(f"{angle_deg:.1f}")
                else:
                    data_label.setText(f"{wheel_state.sta_motor_data[i]:.1f}")
            else:
                data_label.setText("0.0")
            if hasattr(wheel_state.sta_motor_temp, '__getitem__') and i < len(wheel_state.sta_motor_temp):
                temp_label.setText(f"{wheel_state.sta_motor_temp[i]:.1f}")
            else:
                temp_label.setText("25.0")
        
        # 更新电磁铁状态 (底部行)
        electromagnet_state = state_data.state_electromagnet
        em_on = bool(electromagnet_state.sta_electromagnet_enable)
        self.electromagnet_enable_label.setText("开启" if em_on else "关闭")
        self._set_badge_style(self.electromagnet_enable_label, em_on)
        self.electromagnet_voltage_label.setText(f"{electromagnet_state.sta_electromagnet_voltage}")
        # 更新清洗功能状态 (底部行)
        brush_state = state_data.state_brush
        self.brush_power_label.setText(f"{brush_state.sta_brush_power}")
        br_on = bool(brush_state.sta_brush_enable)
        self.brush_enable_label.setText("开启" if br_on else "关闭")
        self._set_badge_style(self.brush_enable_label, br_on)
        self.water_flow_label.setText(f"{brush_state.sta_water_flow}")
        wt_on = bool(brush_state.sta_water_enable)
        self.water_enable_label.setText("开启" if wt_on else "关闭")
        self._set_badge_style(self.water_enable_label, wt_on)
        
        # 系统状态信息由主界面底部状态栏统一更新显示
        
