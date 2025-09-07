#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
相机组件模块
包含单个相机的UI界面和控制逻辑
"""

import os
import cv2
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QGroupBox, QPushButton, QLineEdit, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QPixmap, QImage

from .camera_thread import CameraThread
from .video_recorder import VideoRecorder

class CameraWidget(QWidget):
    """单个相机组件"""
    
    def __init__(self, title, camera_id, robot_data, screen_width=1920, screen_height=1080, use_rtsp=True):
        super().__init__()
        self.title = title
        self.camera_id = camera_id
        self.robot_data = robot_data
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.use_rtsp = use_rtsp  # 相机打开方式：True-RTSP流，False-OpenCV直接打开
        self.camera_thread = None
        self.recorder = VideoRecorder()
        self.current_frame = None
        
        # 默认保存路径
        self.screenshot_path = f"camera_data/camera{camera_id + 1}_screenshots"
        self.recording_path = f"camera_data/camera{camera_id + 1}_recordings"
        
        # 确保目录存在
        os.makedirs(self.screenshot_path, exist_ok=True)
        os.makedirs(self.recording_path, exist_ok=True)
        
        self.init_ui()
        self.start_camera()
        
    def init_ui(self):
        """初始化用户界面"""
        # 创建主容器
        container = QGroupBox(self.title)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(15, 20, 15, 15)
        container_layout.setSpacing(15)
        
        # 视频显示区域
        self.video_label = QLabel()
        # 根据屏幕尺寸动态设置相机画面尺寸
        min_width = int(self.screen_width * 0.25)  # 屏幕宽度的25%
        min_height = int(min_width * 0.75)  # 保持4:3比例
        max_width = int(self.screen_width * 0.4)   # 屏幕宽度的40%
        max_height = int(max_width * 0.75)  # 保持4:3比例
        
        self.video_label.setMinimumSize(min_width, min_height)
        self.video_label.setMaximumSize(max_width, max_height)
        self.video_label.setScaledContents(True)
        self.video_label.setStyleSheet("""
            QLabel {
                border: 3px solid #e8eaed;
                background-color: #f5f5f5;
                border-radius: 12px;
                color: #666666;
                font-size: 16px;
                font-weight: 600;
            }
        """)
        self.video_label.setText("📹 相机启动中...")
        self.video_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.video_label)
        
        # 控制按钮区域
        control_layout = QHBoxLayout()
        control_layout.setSpacing(12)
        
        # 截图按钮
        self.screenshot_btn = QPushButton("📸 截图")
        self.screenshot_btn.setMinimumSize(100, 40)
        self.screenshot_btn.clicked.connect(self.take_screenshot)
        
        # 录制按钮
        self.record_btn = QPushButton("🎥 开始录制")
        self.record_btn.setMinimumSize(100, 40)
        self.record_btn.setCheckable(True)
        self.record_btn.clicked.connect(self.toggle_recording)
        
        # 设置按钮
        self.settings_btn = QPushButton("⚙️ 设置")
        self.settings_btn.setMinimumSize(80, 40)
        self.settings_btn.clicked.connect(self.show_settings_dialog)
        
        # 录制状态指示器
        self.record_status = QLabel("⚫ 未录制")
        self.record_status.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 14px;
                font-weight: 600;
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 8px;
            }
        """)
        
        control_layout.addWidget(self.screenshot_btn)
        control_layout.addWidget(self.record_btn)
        control_layout.addWidget(self.settings_btn)
        control_layout.addStretch()
        control_layout.addWidget(self.record_status)
        
        container_layout.addLayout(control_layout)
        
        # 将容器添加到主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)
        
        # 设置现代白色风格样式
        self.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #2c3e50;
                border: 2px solid #e8eaed;
                padding: 10px 16px;
                border-radius: 10px;
                font-weight: 600;
                font-size: 14px;
                font-family: 'Microsoft YaHei UI', sans-serif;
            }
            QPushButton:hover {
                background-color: #f8f9ff;
                border-color: #1976d2;
                color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #1976d2;
                color: #ffffff;
                border-color: #1565c0;
            }
            QPushButton:checked {
                background-color: #f44336;
                color: #ffffff;
                border-color: #d32f2f;
            }
            QPushButton:checked:hover {
                background-color: #e53935;
            }
            QGroupBox {
                font-weight: 600;
                border: 2px solid #e8eaed;
                border-radius: 16px;
                margin-top: 12px;
                background-color: #ffffff;
                color: #2c3e50;
                padding-top: 20px;
                font-family: 'Microsoft YaHei UI', sans-serif;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 12px 0 12px;
                color: #1976d2;
                font-size: 16px;
                font-weight: 700;
                background-color: #ffffff;
            }
        """)
        
    def start_camera(self):
        """启动相机"""
        if self.camera_thread is None:
            self.camera_thread = CameraThread(self.camera_id, self.use_rtsp)
            self.camera_thread.frame_ready.connect(self.update_frame)
            self.camera_thread.start_camera()
            
    def stop_camera(self):
        """停止相机"""
        if self.camera_thread:
            self.camera_thread.stop_camera()
            self.camera_thread = None
            
    @pyqtSlot(object, int)
    def update_frame(self, frame, camera_id):
        """更新视频帧"""
        if camera_id == self.camera_id:
            self.current_frame = frame.copy()
            
            # 如果正在录制，写入帧
            if self.recorder.is_recording():
                self.recorder.write_frame(frame)
            
            # 转换为Qt格式并显示
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            
            # 缩放到合适大小
            scaled_pixmap = pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.video_label.setPixmap(scaled_pixmap)
            
    def take_screenshot(self):
        """截图功能"""
        if self.current_frame is not None:
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.screenshot_path, f"camera{self.camera_id + 1}_{timestamp}.jpg")
            
            # 保存截图
            success = cv2.imwrite(filename, self.current_frame)
            
            if success:
                QMessageBox.information(self, "截图成功", f"截图已保存到:\n{filename}")
                
                # 更新相机数据
                cmd_data = self.robot_data.get_cmd_data()
                if hasattr(cmd_data, 'cmd_camera'):
                    if self.camera_id == 0:
                        cmd_data.cmd_camera.cmd_camera_snapshot[0] = 1
                    else:
                        cmd_data.cmd_camera.cmd_camera_snapshot[1] = 1
            else:
                QMessageBox.warning(self, "截图失败", "无法保存截图文件")
        else:
            QMessageBox.warning(self, "截图失败", "没有可用的视频帧")
            
    def toggle_recording(self):
        """切换录制状态"""
        if self.record_btn.isChecked():
            self.start_recording()
        else:
            self.stop_recording()
            
    def start_recording(self):
        """开始录制"""
        if self.current_frame is not None:
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.recording_path, f"camera{self.camera_id + 1}_{timestamp}.avi")
            
            # 获取帧尺寸
            h, w = self.current_frame.shape[:2]
            frame_size = (w, h)
            
            # 开始录制
            if self.recorder.start_recording(filename, frame_size):
                self.record_btn.setText("🛑 停止录制")
                self.record_status.setText("🔴 录制中...")
                self.record_status.setStyleSheet("""
                    QLabel {
                        color: #f44336;
                        font-size: 14px;
                        font-weight: 600;
                        padding: 8px;
                        background-color: #ffebee;
                        border-radius: 8px;
                    }
                """)
                
                # 更新相机数据
                cmd_data = self.robot_data.get_cmd_data()
                if hasattr(cmd_data, 'cmd_camera'):
                    if self.camera_id == 0:
                        cmd_data.cmd_camera.cmd_camera_record[0] = 1
                    else:
                        cmd_data.cmd_camera.cmd_camera_record[1] = 1
            else:
                self.record_btn.setChecked(False)
                QMessageBox.warning(self, "录制失败", "无法启动视频录制")
        else:
            self.record_btn.setChecked(False)
            QMessageBox.warning(self, "录制失败", "没有可用的视频帧")
            
    def stop_recording(self):
        """停止录制"""
        filename = self.recorder.stop_recording()
        self.record_btn.setText("🎥 开始录制")
        self.record_status.setText("⚫ 未录制")
        self.record_status.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 14px;
                font-weight: 600;
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 8px;
            }
        """)
        
        # 更新相机数据
        cmd_data = self.robot_data.get_cmd_data()
        if hasattr(cmd_data, 'cmd_camera'):
            if self.camera_id == 0:
                cmd_data.cmd_camera.cmd_camera_record[0] = 0
            else:
                cmd_data.cmd_camera.cmd_camera_record[1] = 0
            
        if filename:
            QMessageBox.information(self, "录制完成", f"视频已保存到:\n{filename}")
            
    def show_settings_dialog(self):
        """显示设置对话框"""
        from PyQt5.QtWidgets import QDialog
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"📹 {self.title} - 设置")
        dialog.setFixedSize(500, 300)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                color: #2c3e50;
                font-family: 'Microsoft YaHei UI', sans-serif;
            }
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #2c3e50;
                padding: 5px;
            }
            QLineEdit {
                background-color: #f8f9fa;
                color: #2c3e50;
                border: 2px solid #e8eaed;
                padding: 10px;
                border-radius: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #1976d2;
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #ffffff;
                color: #2c3e50;
                border: 2px solid #e8eaed;
                padding: 8px 16px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #f8f9ff;
                border-color: #1976d2;
                color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #1976d2;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: 600;
                border: 2px solid #e8eaed;
                border-radius: 12px;
                margin-top: 15px;
                background-color: #ffffff;
                color: #2c3e50;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #1976d2;
                font-size: 16px;
                font-weight: 700;
                background-color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 路径设置组
        path_group = QGroupBox("📁 保存路径设置")
        path_layout = QGridLayout(path_group)
        path_layout.setSpacing(12)
        path_layout.setContentsMargins(15, 20, 15, 15)
        
        # 截图路径
        path_layout.addWidget(QLabel("📸 截图路径:"), 0, 0)
        screenshot_path_edit = QLineEdit(self.screenshot_path)
        path_layout.addWidget(screenshot_path_edit, 0, 1)
        screenshot_browse_btn = QPushButton("📂 浏览")
        screenshot_browse_btn.clicked.connect(lambda: self.browse_path(screenshot_path_edit, "选择截图保存路径", True))
        path_layout.addWidget(screenshot_browse_btn, 0, 2)
        
        # 录制路径
        path_layout.addWidget(QLabel("🎥 录制路径:"), 1, 0)
        recording_path_edit = QLineEdit(self.recording_path)
        path_layout.addWidget(recording_path_edit, 1, 1)
        recording_browse_btn = QPushButton("📂 浏览")
        recording_browse_btn.clicked.connect(lambda: self.browse_path(recording_path_edit, "选择录制保存路径", False))
        path_layout.addWidget(recording_browse_btn, 1, 2)
        
        layout.addWidget(path_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("💾 保存")
        save_btn.clicked.connect(lambda: self.save_settings(screenshot_path_edit.text(), recording_path_edit.text(), dialog))
        
        cancel_btn = QPushButton("❌ 取消")
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    def browse_path(self, line_edit, title, is_screenshot):
        """浏览路径"""
        current_path = line_edit.text() if line_edit.text() else (self.screenshot_path if is_screenshot else self.recording_path)
        path = QFileDialog.getExistingDirectory(self, title, current_path)
        if path:
            line_edit.setText(path)
    
    def save_settings(self, screenshot_path, recording_path, dialog):
        """保存设置"""
        if screenshot_path:
            self.screenshot_path = screenshot_path
            os.makedirs(screenshot_path, exist_ok=True)
        
        if recording_path:
            self.recording_path = recording_path
            os.makedirs(recording_path, exist_ok=True)
        
        dialog.accept()
            

            
    def closeEvent(self, event):
        """关闭事件处理"""
        self.stop_camera()
        if self.recorder.is_recording():
            self.stop_recording()
        event.accept()