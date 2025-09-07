#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志界面模块
独立的日志显示和管理界面
"""

import os
import json
import logging
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QFrame, QGroupBox, QPushButton, QLineEdit, QComboBox,
    QCheckBox, QTextEdit, QFileDialog, QMessageBox, QScrollArea,
    QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont, QPalette, QColor, QTextCursor

class LogHandler(logging.Handler):
    """自定义日志处理器，用于将日志输出到GUI"""
    
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        
    def emit(self, record):
        """发送日志记录"""
        try:
            msg = self.format(record)
            # 在GUI线程中更新文本
            self.text_widget.append(msg)
            # 自动滚动到底部
            cursor = self.text_widget.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.text_widget.setTextCursor(cursor)
        except Exception:
            pass

class LogViewWidget(QWidget):
    """日志界面主组件"""
    
    def __init__(self):
        super().__init__()
        self.load_config()
        self.init_ui()
        self.setup_logging()
        
    def load_config(self):
        """加载日志配置"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "log_config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                # 加载配置
                self.log_folder = config.get("log_folder", "logs")
                self.log_file = os.path.join(self.log_folder, config["log_files"]["system"])
                self.max_log_lines = config["display_settings"]["max_display_lines"]
                self.log_level = config["log_settings"]["log_level"]
                self.log_format = config["log_settings"]["log_format"]
                self.date_format = config["log_settings"]["date_format"]
                self.auto_scroll_default = config["display_settings"]["auto_scroll"]
                self.auto_refresh_default = config["display_settings"]["auto_refresh"]
                self.refresh_interval = config["display_settings"]["refresh_interval_seconds"] * 1000
                self.font_family = config["display_settings"]["font_family"]
                self.font_size = config["display_settings"]["font_size"]
            else:
                # 默认配置
                self.log_folder = "logs"
                self.log_file = os.path.join(self.log_folder, "system.log")
                self.max_log_lines = 1000
                self.log_level = "INFO"
                self.log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                self.date_format = "%Y-%m-%d %H:%M:%S"
                self.auto_scroll_default = True
                self.auto_refresh_default = False
                self.refresh_interval = 5000
                self.font_family = "Consolas"
                self.font_size = 9
        except Exception as e:
            print(f"加载日志配置失败: {e}")
            # 使用默认配置
            self.log_folder = "logs"
            self.log_file = os.path.join(self.log_folder, "system.log")
            self.max_log_lines = 1000
            self.log_level = "INFO"
            self.log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            self.date_format = "%Y-%m-%d %H:%M:%S"
            self.auto_scroll_default = True
            self.auto_refresh_default = False
            self.refresh_interval = 5000
            self.font_family = "Consolas"
            self.font_size = 9
        
    def init_ui(self):
        """初始化用户界面"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # 标题区域
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(20, 15, 20, 15)
        
        title_label = QLabel("📋 系统日志")
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        # 快捷操作按钮
        clear_btn = QPushButton("🗑️ 清空日志")
        save_btn = QPushButton("💾 保存日志")
        refresh_btn = QPushButton("🔄 刷新")
        
        for btn in [clear_btn, save_btn, refresh_btn]:
            btn.setFixedSize(90, 35)
            btn.setStyleSheet(self.get_action_button_style())
        
        # 连接按钮信号
        clear_btn.clicked.connect(self.clear_logs)
        save_btn.clicked.connect(self.save_logs)
        refresh_btn.clicked.connect(self.refresh_logs)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(clear_btn)
        title_layout.addWidget(save_btn)
        title_layout.addWidget(refresh_btn)
        
        title_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: 1px solid #e9ecef;
                border-radius: 12px;
            }
        """)
        
        main_layout.addWidget(title_widget)
        
        # 创建日志控制组
        self.create_log_controls(main_layout)
        
        # 创建日志显示区域
        self.create_log_display(main_layout)
        
        # 设置整体样式
        self.setStyleSheet("""
            LogViewWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            }
        """)
        
    def create_log_controls(self, parent_layout):
        """创建日志控制组"""
        group = QGroupBox("📊 日志控制")
        layout = QGridLayout(group)
        
        # 日志级别过滤
        layout.addWidget(QLabel("日志级别:"), 0, 0)
        self.level_combo = QComboBox()
        self.level_combo.addItems(["全部", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_combo.currentTextChanged.connect(self.filter_logs)
        layout.addWidget(self.level_combo, 0, 1)
        
        # 搜索功能
        layout.addWidget(QLabel("搜索:"), 0, 2)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入关键词搜索...")
        self.search_edit.textChanged.connect(self.search_logs)
        layout.addWidget(self.search_edit, 0, 3)
        
        # 自动滚动
        self.auto_scroll_check = QCheckBox("自动滚动到底部")
        self.auto_scroll_check.setChecked(self.auto_scroll_default)
        layout.addWidget(self.auto_scroll_check, 1, 0, 1, 2)
        
        # 自动刷新
        refresh_text = f"自动刷新 ({self.refresh_interval//1000}秒)"
        self.auto_refresh_check = QCheckBox(refresh_text)
        self.auto_refresh_check.setChecked(self.auto_refresh_default)
        self.auto_refresh_check.toggled.connect(self.toggle_auto_refresh)
        layout.addWidget(self.auto_refresh_check, 1, 2, 1, 2)
        
        # 设置组样式
        group.setStyleSheet(self.get_group_style())
        parent_layout.addWidget(group)
        
    def create_log_display(self, parent_layout):
        """创建日志显示区域"""
        group = QGroupBox("📝 日志内容")
        layout = QVBoxLayout(group)
        
        # 日志文本显示
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont(self.font_family, self.font_size))
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
                color: #212529;
                selection-background-color: #007bff;
                selection-color: #ffffff;
            }
        """)
        
        layout.addWidget(self.log_text)
        
        # 状态栏
        status_layout = QHBoxLayout()
        self.status_label = QLabel("就绪")
        self.line_count_label = QLabel("行数: 0")
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.line_count_label)
        
        layout.addLayout(status_layout)
        
        # 设置组样式
        group.setStyleSheet(self.get_group_style())
        parent_layout.addWidget(group)
        
    def get_action_button_style(self):
        """获取操作按钮样式"""
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #28a745, stop:1 #1e7e34);
                border: none;
                border-radius: 8px;
                color: #ffffff;
                font-size: 11px;
                font-weight: 600;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #1e7e34, stop:1 #155724);
            }
            QPushButton:pressed {
                background: #155724;
            }
        """
    
    def get_group_style(self):
        """获取组样式"""
        return """
            QGroupBox {
                font-weight: 600;
                border: 1px solid #dee2e6;
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: #ffffff;
                color: #212529;
                font-size: 13px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 5px 12px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #28a745, stop:1 #1e7e34);
                color: #ffffff;
                border-radius: 6px;
                font-weight: 600;
            }
            QLabel {
                color: #495057;
                font-size: 12px;
                font-weight: 500;
            }
            QComboBox, QLineEdit {
                background-color: #ffffff;
                color: #495057;
                border: 1px solid #ced4da;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
            }
            QComboBox:focus, QLineEdit:focus {
                border-color: #28a745;
            }
            QCheckBox {
                color: #495057;
                font-size: 12px;
                font-weight: 500;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #ffffff;
                border: 2px solid #ced4da;
                border-radius: 4px;
            }
            QCheckBox::indicator:checked {
                background-color: #28a745;
                border: 2px solid #28a745;
                border-radius: 4px;
            }
        """
        
    def setup_logging(self):
        """设置日志系统"""
        # 确保日志文件夹存在
        os.makedirs(self.log_folder, exist_ok=True)
        
        # 设置日志格式
        formatter = logging.Formatter(
            self.log_format,
            datefmt=self.date_format
        )
        
        # 创建GUI日志处理器
        self.gui_handler = LogHandler(self.log_text)
        self.gui_handler.setFormatter(formatter)
        
        # 创建文件日志处理器
        self.file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        self.file_handler.setFormatter(formatter)
        
        # 获取根日志记录器
        self.logger = logging.getLogger()
        level = getattr(logging, self.log_level.upper(), logging.INFO)
        self.logger.setLevel(level)
        
        # 清除现有处理器并添加新的
        self.logger.handlers.clear()
        self.logger.addHandler(self.gui_handler)
        self.logger.addHandler(self.file_handler)
        
        # 设置自动刷新定时器
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_logs)
        
        # 加载现有日志
        self.load_existing_logs()
        
    def load_existing_logs(self):
        """加载现有日志文件"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # 只显示最后1000行
                    if len(lines) > self.max_log_lines:
                        lines = lines[-self.max_log_lines:]
                    
                    self.log_text.clear()
                    for line in lines:
                        self.log_text.append(line.rstrip())
                    
                    self.update_line_count()
                    
        except Exception as e:
            self.status_label.setText(f"加载日志失败: {str(e)}")
    
    def clear_logs(self):
        """清空日志"""
        reply = QMessageBox.question(
            self, '确认清空', 
            '确定要清空所有日志吗？此操作不可撤销。',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.log_text.clear()
            # 清空日志文件
            try:
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    f.write('')
                self.status_label.setText("日志已清空")
                self.update_line_count()
            except Exception as e:
                self.status_label.setText(f"清空失败: {str(e)}")
    
    def save_logs(self):
        """保存日志到文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, '保存日志', 
            f'system_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt',
            'Text files (*.txt);;All files (*.*)'
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                self.status_label.setText(f"日志已保存到: {file_path}")
            except Exception as e:
                self.status_label.setText(f"保存失败: {str(e)}")
    
    def refresh_logs(self):
        """刷新日志显示"""
        self.load_existing_logs()
        self.status_label.setText("日志已刷新")
    
    def filter_logs(self, level):
        """根据级别过滤日志"""
        # 这里可以实现日志级别过滤逻辑
        self.status_label.setText(f"过滤级别: {level}")
    
    def search_logs(self, text):
        """搜索日志内容"""
        if text:
            # 高亮搜索结果
            cursor = self.log_text.textCursor()
            cursor.movePosition(QTextCursor.Start)
            self.log_text.setTextCursor(cursor)
            
            if self.log_text.find(text):
                self.status_label.setText(f"找到: {text}")
            else:
                self.status_label.setText(f"未找到: {text}")
        else:
            self.status_label.setText("就绪")
    
    def toggle_auto_refresh(self, enabled):
        """切换自动刷新"""
        if enabled:
            self.refresh_timer.start(self.refresh_interval)
            self.status_label.setText(f"自动刷新已启用 ({self.refresh_interval//1000}秒)")
        else:
            self.refresh_timer.stop()
            self.status_label.setText("自动刷新已禁用")
    
    def update_line_count(self):
        """更新行数显示"""
        line_count = self.log_text.document().blockCount()
        self.line_count_label.setText(f"行数: {line_count}")
    
    def update_display(self):
        """更新显示数据"""
        self.update_line_count()
        
        # 自动滚动到底部
        if self.auto_scroll_check.isChecked():
            cursor = self.log_text.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.log_text.setTextCursor(cursor)