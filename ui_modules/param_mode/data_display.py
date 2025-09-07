#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据显示模块
包含CMD控制参数和STATE状态参数的显示组件
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QGroupBox, QScrollArea, QSpinBox, QDoubleSpinBox,
    QCheckBox, QFrame, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class ParameterWidget(QWidget):
    """单个参数显示组件"""
    valueChanged = pyqtSignal(str, object)  # 参数名, 新值
    
    def __init__(self, param_name, display_name, value, unit="", param_type="float", editable=True):
        super().__init__()
        self.param_name = param_name
        self.display_name = display_name
        self.unit = unit
        self.param_type = param_type
        self.editable = editable
        self.init_ui()
        self.set_value(value)
        
    def init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(8)
        
        # 参数名称标签
        name_label = QLabel(self.display_name + ":")
        name_label.setMinimumWidth(120)
        name_label.setStyleSheet("""
            QLabel {
                color: #495057;
                font-weight: bold;
                font-size: 11px;
            }
        """)
        layout.addWidget(name_label)
        
        # 值输入控件
        if self.param_type == "bool":
            self.value_widget = QCheckBox()
            self.value_widget.setEnabled(self.editable)
            if self.editable:
                self.value_widget.stateChanged.connect(self.on_value_changed)
        elif self.param_type == "int":
            self.value_widget = QSpinBox()
            self.value_widget.setRange(-999999, 999999)
            self.value_widget.setEnabled(self.editable)
            if self.editable:
                self.value_widget.valueChanged.connect(self.on_value_changed)
        elif self.param_type == "float":
            self.value_widget = QDoubleSpinBox()
            self.value_widget.setRange(-999999.0, 999999.0)
            self.value_widget.setDecimals(3)
            self.value_widget.setEnabled(self.editable)
            if self.editable:
                self.value_widget.valueChanged.connect(self.on_value_changed)
        else:  # string or other
            self.value_widget = QLineEdit()
            self.value_widget.setEnabled(self.editable)
            if self.editable:
                self.value_widget.textChanged.connect(self.on_value_changed)
        
        self.value_widget.setStyleSheet("""
            QSpinBox, QDoubleSpinBox, QLineEdit {
                background-color: #ffffff;
                border: 1px solid #ced4da;
                border-radius: 3px;
                padding: 2px 6px;
                min-width: 80px;
            }
            QSpinBox:focus, QDoubleSpinBox:focus, QLineEdit:focus {
                border-color: #007bff;
            }
            QSpinBox:disabled, QDoubleSpinBox:disabled, QLineEdit:disabled {
                background-color: #f8f9fa;
                color: #6c757d;
            }
            QCheckBox {
                font-size: 11px;
            }
        """)
        
        layout.addWidget(self.value_widget)
        
        # 单位标签
        if self.unit:
            unit_label = QLabel(self.unit)
            unit_label.setStyleSheet("""
                QLabel {
                    color: #6c757d;
                    font-size: 10px;
                    min-width: 30px;
                }
            """)
            layout.addWidget(unit_label)
        
        layout.addStretch()
        
    def set_value(self, value):
        """设置值"""
        if self.param_type == "bool":
            self.value_widget.setChecked(bool(value))
        elif self.param_type == "int":
            self.value_widget.setValue(int(value))
        elif self.param_type == "float":
            self.value_widget.setValue(float(value))
        else:
            self.value_widget.setText(str(value))
    
    def get_value(self):
        """获取值"""
        if self.param_type == "bool":
            return self.value_widget.isChecked()
        elif self.param_type in ["int", "float"]:
            return self.value_widget.value()
        else:
            return self.value_widget.text()
    
    def on_value_changed(self):
        """值改变回调"""
        if self.editable:
            self.valueChanged.emit(self.param_name, self.get_value())


class ParameterTableWidget(QWidget):
    """参数表格显示组件"""
    parameterChanged = pyqtSignal(str, str, object)  # 组名, 参数名, 新值
    plotSelectionChanged = pyqtSignal(str, str, int)  # 组名, 参数名, plot索引
    
    def __init__(self, group_name, title, editable=False):
        super().__init__()
        self.group_name = group_name
        self.title = title
        self.editable = editable
        self.parameters = {}  # 存储参数信息
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # 创建组框
        self.group_box = QGroupBox(self.title)
        self.group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: #495057;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: #f8f9fa;
            }
        """)
        
        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(4)  # 参数名、值、单位、plot选择
        self.table.setHorizontalHeaderLabels(["参数名称", "数值", "单位", "Plot选择"])
        
        # 设置表格样式
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e9ecef;
                background-color: #ffffff;
                alternate-background-color: #f8f9fa;
                selection-background-color: #007bff;
                selection-color: #ffffff;
                border: 1px solid #dee2e6;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #007bff;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #f1f3f4;
                padding: 8px;
                border: 1px solid #dee2e6;
                font-weight: bold;
            }
        """)
        
        # 设置表格属性
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.setColumnWidth(3, 100)  # Plot选择列固定宽度100px
        
        # 设置表格大小策略，使其能够扩展填充空间
        from PyQt5.QtWidgets import QSizePolicy
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.table.setMinimumHeight(150)  # 设置最小高度
        
        # 禁用垂直滚动条，让表格完全展开
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 连接信号
        self.table.itemChanged.connect(self.on_item_changed)
        
        group_layout = QVBoxLayout(self.group_box)
        group_layout.setContentsMargins(10, 15, 10, 10)
        group_layout.addWidget(self.table)
        
        layout.addWidget(self.group_box)
        
    def add_parameter(self, param_name, display_name, value, unit="", param_type="float", editable=None):
        """添加参数"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # 存储参数信息
        self.parameters[param_name] = {
            'display_name': display_name,
            'param_type': param_type,
            'unit': unit,
            'row': row
        }
        
        # 参数名称（不可编辑）
        name_item = QTableWidgetItem(display_name)
        name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, 0, name_item)
        
        # 参数值（根据editable设置是否可编辑）
        value_item = QTableWidgetItem(str(value))
        # 如果指定了editable参数，使用它；否则使用self.editable
        param_editable = editable if editable is not None else self.editable
        if not param_editable:
            value_item.setFlags(value_item.flags() & ~Qt.ItemIsEditable)
        value_item.setData(Qt.UserRole, param_name)  # 存储参数名
        self.table.setItem(row, 1, value_item)
        
        # 单位（不可编辑）
        unit_item = QTableWidgetItem(unit)
        unit_item.setFlags(unit_item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, 2, unit_item)
        
        # Plot选择下拉框
        plot_combo = QComboBox()
        plot_combo.addItems(["-- 不显示 --", "图表 1", "图表 2", "图表 3", "图表 4"])
        plot_combo.setCurrentIndex(0)  # 默认不显示
        plot_combo.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 2px 6px;
                font-size: 12px;
            }
            QComboBox:hover {
                border-color: #007bff;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #6c757d;
                margin-right: 4px;
            }
        """)
        plot_combo.currentIndexChanged.connect(lambda index, pname=param_name: self.on_plot_selection_changed(pname, index))
        self.table.setCellWidget(row, 3, plot_combo)
        
        # 自动调整表格高度以显示所有行
        self.adjust_table_height()
    
    def adjust_table_height(self):
        """自动调整表格高度以显示所有行"""
        if self.table.rowCount() > 0:
            # 计算所有行的总高度
            total_height = 0
            
            # 添加表头高度
            total_height += self.table.horizontalHeader().height()
            
            # 添加所有行的高度
            for i in range(self.table.rowCount()):
                total_height += self.table.rowHeight(i)
            
            # 添加一些边距
            total_height += 10
            
            # 设置表格的固定高度
            self.table.setFixedHeight(total_height)
        
    def update_parameter(self, param_name, value):
        """更新参数值"""
        if param_name in self.parameters:
            row = self.parameters[param_name]['row']
            item = self.table.item(row, 1)
            if item:
                # 对于只读参数（如sta_uptime），暂时阻止信号发射以避免触发警告
                if not (item.flags() & Qt.ItemIsEditable):
                    self.table.blockSignals(True)
                    item.setText(str(value))
                    self.table.blockSignals(False)
                else:
                    item.setText(str(value))
    
    def get_parameter_value(self, param_name):
        """获取参数值"""
        if param_name in self.parameters:
            row = self.parameters[param_name]['row']
            item = self.table.item(row, 1)
            if item:
                param_type = self.parameters[param_name]['param_type']
                try:
                    if param_type == "int":
                        return int(item.text())
                    elif param_type == "float":
                        return float(item.text())
                    elif param_type == "bool":
                        return bool(int(item.text()))
                    else:
                        return item.text()
                except ValueError:
                    return 0
        return None
    
    def on_item_changed(self, item):
        """表格项改变时的处理"""
        if item.column() == 1:  # 只处理值列的改变
            param_name = item.data(Qt.UserRole)
            if param_name and param_name in self.parameters:
                param_type = self.parameters[param_name]['param_type']
                try:
                    if param_type == "int":
                        value = int(item.text())
                    elif param_type == "float":
                        value = float(item.text())
                    elif param_type == "bool":
                        value = bool(int(item.text()))
                    else:
                        value = item.text()
                    
                    self.parameterChanged.emit(self.group_name, param_name, value)
                except ValueError:
                    # 如果转换失败，恢复原值
                    item.setText("0")
    
    def on_plot_selection_changed(self, param_name, plot_index):
        """Plot选择变化回调"""
        self.plotSelectionChanged.emit(self.group_name, param_name, plot_index)


class CmdDataDisplayWidget(QWidget):
    """CMD控制参数显示组件"""
    parameterChanged = pyqtSignal(str, str, object)  # 组名, 参数名, 新值
    plotSelectionChanged = pyqtSignal(str, str, int)  # 组名, 参数名, 图表索引
    
    def __init__(self, robot_data=None):
        super().__init__()
        self.robot_data = robot_data
        self.parameter_groups = {}
        self.init_ui()
        self.setup_parameters()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 标题
        title_label = QLabel("🎮 控制命令参数")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #495057; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # 滚动区域 - 整体可滚动，但各模块表格完全展开
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(15)
        self.scroll_layout.setContentsMargins(5, 5, 5, 5)
        
        scroll_area.setWidget(self.scroll_widget)
        layout.addWidget(scroll_area, 1)  # 设置拉伸因子为1，使滚动区域铺满剩余空间
        
    def setup_parameters(self):
        """设置参数组"""
        # 浮游模式控制
        floating_group = ParameterTableWidget("cmd_floating_mode", "🏊 浮游模式控制", True)
        floating_group.add_parameter("cmd_floating_vel_x", "Linear Velocity X", 0.0, "m/s", "float")
        floating_group.add_parameter("cmd_floating_vel_y", "Linear Velocity Y", 0.0, "m/s", "float")
        floating_group.add_parameter("cmd_floating_vel_z", "Linear Velocity Z", 0.0, "m/s", "float")
        floating_group.add_parameter("cmd_floating_angular_roll", "Angular Roll", 0.0, "rad", "float")
        floating_group.add_parameter("cmd_floating_angular_yaw", "Angular Yaw", 0.0, "rad", "float")
        floating_group.add_parameter("cmd_floating_angular_pitch", "Angular Pitch", 0.0, "rad", "float")
        # 深度控制
        floating_group.add_parameter("cmd_depth_hold", "Depth Hold Enable", 0, "", "int")
        floating_group.add_parameter("cmd_target_depth", "Target Depth", 0.0, "m", "float")
        # 定航控制
        floating_group.add_parameter("cmd_floating_heading_hold", "Heading Hold Enable", 0, "", "int")
        floating_group.add_parameter("cmd_target_roll", "Target Roll", 0.0, "rad", "float")
        floating_group.add_parameter("cmd_target_yaw", "Target Yaw", 0.0, "rad", "float")
        floating_group.add_parameter("cmd_target_pitch", "Target Pitch", 0.0, "rad", "float")
        floating_group.parameterChanged.connect(self.parameterChanged.emit)
        floating_group.plotSelectionChanged.connect(self.plotSelectionChanged.emit)
        self.parameter_groups["cmd_floating_mode"] = floating_group
        self.scroll_layout.addWidget(floating_group)
        
        # 轮式模式控制
        wheel_group = ParameterTableWidget("cmd_wheel_mode", "🚗 轮式模式控制", True)
        wheel_group.add_parameter("cmd_wheel_linear_vel", "Linear Velocity", 0.0, "m/s", "float")
        wheel_group.add_parameter("cmd_wheel_angular_vel", "Angular Velocity", 0.0, "rad/s", "float")
        # 轮式定航控制
        wheel_group.add_parameter("cmd_wheel_heading_hold", "Heading Hold Enable", 0, "", "int")
        wheel_group.add_parameter("cmd_target_heading", "Target Heading", 0.0, "rad", "float")
        wheel_group.parameterChanged.connect(self.parameterChanged.emit)
        wheel_group.plotSelectionChanged.connect(self.plotSelectionChanged.emit)
        self.parameter_groups["cmd_wheel_mode"] = wheel_group
        self.scroll_layout.addWidget(wheel_group)
        
        # 电磁铁控制
        electromagnet_group = ParameterTableWidget("cmd_electromagnet", "🧲 电磁铁控制", True)
        electromagnet_group.add_parameter("cmd_electromagnet_enable", "Electromagnet Enable", 0, "", "int")
        electromagnet_group.add_parameter("cmd_electromagnet_voltage", "Electromagnet Voltage", 0, "%", "int")
        electromagnet_group.parameterChanged.connect(self.parameterChanged.emit)
        electromagnet_group.plotSelectionChanged.connect(self.plotSelectionChanged.emit)
        self.parameter_groups["cmd_electromagnet"] = electromagnet_group
        self.scroll_layout.addWidget(electromagnet_group)
        
        # 清洗功能控制
        brush_group = ParameterTableWidget("cmd_brush", "🧽 清洗功能控制", True)
        brush_group.add_parameter("cmd_brush_enable", "Brush Status", 0, "", "int")
        brush_group.add_parameter("cmd_brush_power", "Brush Power", 0, "%", "int")
        brush_group.add_parameter("cmd_water_enable", "Water Flow Status", 0, "", "int")
        brush_group.add_parameter("cmd_water_flow", "Water Flow Rate", 0, "%", "int")
        brush_group.parameterChanged.connect(self.parameterChanged.emit)
        brush_group.plotSelectionChanged.connect(self.plotSelectionChanged.emit)
        self.parameter_groups["cmd_brush"] = brush_group
        self.scroll_layout.addWidget(brush_group)
        
        # 相机控制
        camera_group = ParameterTableWidget("cmd_camera", "📷 相机控制", True)
        camera_group.add_parameter("cmd_camera_enable[0]", "Front Camera Enable", 0, "", "int")
        camera_group.add_parameter("cmd_camera_enable[1]", "Rear Camera Enable", 0, "", "int")
        camera_group.add_parameter("cmd_camera_zoom[0]", "Front Camera Zoom", 0, "%", "int")
        camera_group.add_parameter("cmd_camera_zoom[1]", "Rear Camera Zoom", 0, "%", "int")
        camera_group.add_parameter("cmd_camera_record[0]", "Front Camera Record", 0, "", "int")
        camera_group.add_parameter("cmd_camera_record[1]", "Rear Camera Record", 0, "", "int")
        camera_group.add_parameter("cmd_camera_snapshot[0]", "Front Camera Snapshot", 0, "", "int")
        camera_group.add_parameter("cmd_camera_snapshot[1]", "Rear Camera Snapshot", 0, "", "int")
        camera_group.parameterChanged.connect(self.parameterChanged.emit)
        camera_group.plotSelectionChanged.connect(self.plotSelectionChanged.emit)
        self.parameter_groups["cmd_camera"] = camera_group
        self.scroll_layout.addWidget(camera_group)
        
        self.scroll_layout.addStretch()
        
    def update_display(self):
        """更新显示数据"""
        if not self.robot_data:
            return
            
        try:
            cmd_data = self.robot_data.get_cmd_data()
            
            # 更新浮游模式控制
            floating_cmd = cmd_data.cmd_floating_mode
            floating_group = self.parameter_groups["cmd_floating_mode"]
            floating_group.update_parameter("cmd_floating_vel_x", floating_cmd.cmd_floating_vel_x)
            floating_group.update_parameter("cmd_floating_vel_y", floating_cmd.cmd_floating_vel_y)
            floating_group.update_parameter("cmd_floating_vel_z", floating_cmd.cmd_floating_vel_z)
            floating_group.update_parameter("cmd_floating_angular_roll", floating_cmd.cmd_floating_angular_roll)
            floating_group.update_parameter("cmd_floating_angular_yaw", floating_cmd.cmd_floating_angular_yaw)
            floating_group.update_parameter("cmd_floating_angular_pitch", floating_cmd.cmd_floating_angular_pitch)
            # 深度控制
            floating_group.update_parameter("cmd_depth_hold", floating_cmd.cmd_depth_hold)
            floating_group.update_parameter("cmd_target_depth", floating_cmd.cmd_target_depth)
            # 定航控制
            floating_group.update_parameter("cmd_floating_heading_hold", floating_cmd.cmd_floating_heading_hold)
            floating_group.update_parameter("cmd_target_roll", floating_cmd.cmd_target_roll)
            floating_group.update_parameter("cmd_target_yaw", floating_cmd.cmd_target_yaw)
            floating_group.update_parameter("cmd_target_pitch", floating_cmd.cmd_target_pitch)
            
            # 更新轮式模式控制
            wheel_cmd = cmd_data.cmd_wheel_mode
            wheel_group = self.parameter_groups["cmd_wheel_mode"]
            wheel_group.update_parameter("cmd_wheel_linear_vel", wheel_cmd.cmd_wheel_linear_vel)
            wheel_group.update_parameter("cmd_wheel_angular_vel", wheel_cmd.cmd_wheel_angular_vel)
            # 轮式定航控制
            wheel_group.update_parameter("cmd_wheel_heading_hold", wheel_cmd.cmd_wheel_heading_hold)
            wheel_group.update_parameter("cmd_target_heading", wheel_cmd.cmd_target_heading)
            
            # 更新电磁铁控制
            electromagnet_cmd = cmd_data.cmd_electromagnet
            electromagnet_group = self.parameter_groups["cmd_electromagnet"]
            electromagnet_group.update_parameter("cmd_electromagnet_enable", electromagnet_cmd.cmd_electromagnet_enable)
            electromagnet_group.update_parameter("cmd_electromagnet_voltage", electromagnet_cmd.cmd_electromagnet_voltage)
            
            # 更新清洗功能控制
            brush_cmd = cmd_data.cmd_brush
            brush_group = self.parameter_groups["cmd_brush"]
            brush_group.update_parameter("cmd_brush_enable", brush_cmd.cmd_brush_enable)
            brush_group.update_parameter("cmd_brush_power", brush_cmd.cmd_brush_power)
            brush_group.update_parameter("cmd_water_enable", brush_cmd.cmd_water_enable)
            brush_group.update_parameter("cmd_water_flow", brush_cmd.cmd_water_flow)
            
            # 更新相机控制
            camera_cmd = cmd_data.cmd_camera
            camera_group = self.parameter_groups["cmd_camera"]
            if len(camera_cmd.cmd_camera_enable) >= 2:
                camera_group.update_parameter("cmd_camera_enable[0]", camera_cmd.cmd_camera_enable[0])
                camera_group.update_parameter("cmd_camera_enable[1]", camera_cmd.cmd_camera_enable[1])
            if len(camera_cmd.cmd_camera_zoom) >= 2:
                camera_group.update_parameter("cmd_camera_zoom[0]", camera_cmd.cmd_camera_zoom[0])
                camera_group.update_parameter("cmd_camera_zoom[1]", camera_cmd.cmd_camera_zoom[1])
            if len(camera_cmd.cmd_camera_record) >= 2:
                camera_group.update_parameter("cmd_camera_record[0]", camera_cmd.cmd_camera_record[0])
                camera_group.update_parameter("cmd_camera_record[1]", camera_cmd.cmd_camera_record[1])
            if len(camera_cmd.cmd_camera_snapshot) >= 2:
                camera_group.update_parameter("cmd_camera_snapshot[0]", camera_cmd.cmd_camera_snapshot[0])
                camera_group.update_parameter("cmd_camera_snapshot[1]", camera_cmd.cmd_camera_snapshot[1])
                
        except Exception as e:
            print(f"更新CMD数据失败: {e}")


class StateDataDisplayWidget(QWidget):
    """STATE状态参数显示组件"""
    parameterChanged = pyqtSignal(str, str, object)  # 组名, 参数名, 新值
    
    def __init__(self, robot_data=None):
        super().__init__()
        self.robot_data = robot_data
        self.parameter_groups = {}
        self.init_ui()
        self.setup_parameters()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 标题
        title_label = QLabel("📊 状态反馈参数")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #495057; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # 滚动区域 - 整体可滚动，但各模块表格完全展开
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(15)
        self.scroll_layout.setContentsMargins(5, 5, 5, 5)
        
        scroll_area.setWidget(self.scroll_widget)
        layout.addWidget(scroll_area)
        
    def setup_parameters(self):
        """设置参数组 - 分模块显示状态参数"""
        
        # 机器人状态参数组
        robot_group = ParameterTableWidget("robot_status", "🤖 机器人状态", True)
        robot_group.add_parameter("sta_position_x", "Position X", 0.0, "m", "float")
        robot_group.add_parameter("sta_position_y", "Position Y", 0.0, "m", "float")
        robot_group.add_parameter("sta_position_z", "Position Z (Depth)", 0.0, "m", "float")
        robot_group.add_parameter("sta_roll", "Roll Angle", 0.0, "rad", "float")
        robot_group.add_parameter("sta_pitch", "Pitch Angle", 0.0, "rad", "float")
        robot_group.add_parameter("sta_yaw", "Yaw Angle", 0.0, "rad", "float")
        self.parameter_groups["robot_status"] = robot_group
        self.scroll_layout.addWidget(robot_group)
        
        # 添加分隔线
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.HLine)
        separator1.setFrameShadow(QFrame.Sunken)
        separator1.setStyleSheet("QFrame { color: #dee2e6; margin: 10px 0; }")
        self.scroll_layout.addWidget(separator1)
        
        # 浮游模式状态参数组
        floating_group = ParameterTableWidget("floating_status", "🏊 浮游模式状态", True)
        floating_group.add_parameter("sta_floating_vel_x", "Linear Velocity X", 0.0, "m/s", "float")
        floating_group.add_parameter("sta_floating_vel_y", "Linear Velocity Y", 0.0, "m/s", "float")
        floating_group.add_parameter("sta_floating_vel_z", "Linear Velocity Z", 0.0, "m/s", "float")
        floating_group.add_parameter("sta_floating_angular_x", "Angular Velocity X", 0.0, "rad/s", "float")
        floating_group.add_parameter("sta_floating_angular_y", "Angular Velocity Y", 0.0, "rad/s", "float")
        floating_group.add_parameter("sta_floating_angular_z", "Angular Velocity Z", 0.0, "rad/s", "float")
        # 推进器功率和温度（数组参数）
        for i in range(4):
            floating_group.add_parameter(f"sta_thruster_power[{i}]", f"Thruster {i+1} Power", 0.0, "%", "float")
            floating_group.add_parameter(f"sta_thruster_temp[{i}]", f"Thruster {i+1} Temperature", 0.0, "°C", "float")
        self.parameter_groups["floating_status"] = floating_group
        self.scroll_layout.addWidget(floating_group)
        
        # 添加分隔线
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        separator2.setStyleSheet("QFrame { color: #dee2e6; margin: 10px 0; }")
        self.scroll_layout.addWidget(separator2)
        
        # 轮式模式状态参数组
        wheel_group = ParameterTableWidget("wheel_status", "🚗 轮式模式状态", True)
        wheel_group.add_parameter("sta_wheel_linear_vel", "Linear Velocity", 0.0, "m/s", "float")
        wheel_group.add_parameter("sta_wheel_angular_vel", "Angular Velocity", 0.0, "rad/s", "float")
        # 电机数据和温度（数组参数）
        motor_names = ["Steering Angle", "Motor 1 Speed", "Motor 2 Speed"]
        motor_units = ["rad", "m/s", "m/s"]
        for i in range(3):
            wheel_group.add_parameter(f"sta_motor_data[{i}]", f"{motor_names[i]}", 0.0, motor_units[i], "float")
            wheel_group.add_parameter(f"sta_motor_temp[{i}]", f"Motor {i+1} Temperature", 0.0, "°C", "float")
        self.parameter_groups["wheel_status"] = wheel_group
        self.scroll_layout.addWidget(wheel_group)
        
        # 添加分隔线
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.HLine)
        separator3.setFrameShadow(QFrame.Sunken)
        separator3.setStyleSheet("QFrame { color: #dee2e6; margin: 10px 0; }")
        self.scroll_layout.addWidget(separator3)
        
        # 电磁铁状态参数组
        electromagnet_group = ParameterTableWidget("electromagnet_status", "🧲 电磁铁状态", True)
        electromagnet_group.add_parameter("sta_electromagnet_enable", "Electromagnet Status", 0, "", "int")
        electromagnet_group.add_parameter("sta_electromagnet_voltage", "Electromagnet Voltage", 0, "%", "int")
        self.parameter_groups["electromagnet_status"] = electromagnet_group
        self.scroll_layout.addWidget(electromagnet_group)
        
        # 添加分隔线
        separator4 = QFrame()
        separator4.setFrameShape(QFrame.HLine)
        separator4.setFrameShadow(QFrame.Sunken)
        separator4.setStyleSheet("QFrame { color: #dee2e6; margin: 10px 0; }")
        self.scroll_layout.addWidget(separator4)
        
        # 清洗功能状态参数组
        brush_group = ParameterTableWidget("brush_status", "🧽 清洗功能状态", True)
        brush_group.add_parameter("sta_brush_enable", "Brush Status", 0, "", "int")
        brush_group.add_parameter("sta_brush_power", "Brush Power", 0, "%", "int")
        brush_group.add_parameter("sta_water_enable", "Water Flow Status", 0, "", "int")
        brush_group.add_parameter("sta_water_flow", "Water Flow Rate", 0, "%", "int")
        self.parameter_groups["brush_status"] = brush_group
        self.scroll_layout.addWidget(brush_group)
        
        # 添加分隔线
        separator5 = QFrame()
        separator5.setFrameShape(QFrame.HLine)
        separator5.setFrameShadow(QFrame.Sunken)
        separator5.setStyleSheet("QFrame { color: #dee2e6; margin: 10px 0; }")
        self.scroll_layout.addWidget(separator5)
        
        # 系统状态参数组
        system_group = ParameterTableWidget("system_status", "⚙️ 系统状态", True)
        system_group.add_parameter("sta_system_voltage", "System Voltage", 0.0, "V", "float")
        system_group.add_parameter("sta_system_current", "System Current", 0.0, "A", "float")
        system_group.add_parameter("sta_system_power", "System Power", 0.0, "W", "float")
        system_group.add_parameter("sta_comm_status", "Communication Status", 0, "", "int")
        system_group.add_parameter("sta_send_time", "Communication Latency", 0, "ms", "int")
        system_group.add_parameter("sta_packet_loss", "Packet Loss Count", 0, "", "int")
        system_group.add_parameter("sta_leak_detected", "Leak Detection", 0, "", "int")
        system_group.add_parameter("sta_uptime", "System Uptime", 0, "s", "int", editable=False)
        self.parameter_groups["system_status"] = system_group
        self.scroll_layout.addWidget(system_group)
        
        # 连接所有参数组的信号
        robot_group.parameterChanged.connect(self.parameterChanged.emit)
        floating_group.parameterChanged.connect(self.parameterChanged.emit)
        wheel_group.parameterChanged.connect(self.parameterChanged.emit)
        electromagnet_group.parameterChanged.connect(self.parameterChanged.emit)
        brush_group.parameterChanged.connect(self.parameterChanged.emit)
        system_group.parameterChanged.connect(self.parameterChanged.emit)
        
        self.scroll_layout.addStretch()
        
    def update_display(self):
        """更新显示数据"""
        if not self.robot_data:
            return
            
        try:
            state_data = self.robot_data.get_state_data()
            
            # 更新机器人状态
            robot_state = state_data.state_robot
            robot_group = self.parameter_groups["robot_status"]
            robot_group.update_parameter("sta_position_x", robot_state.sta_position_x)
            robot_group.update_parameter("sta_position_y", robot_state.sta_position_y)
            robot_group.update_parameter("sta_position_z", robot_state.sta_position_z)
            robot_group.update_parameter("sta_roll", robot_state.sta_roll)
            robot_group.update_parameter("sta_pitch", robot_state.sta_pitch)
            robot_group.update_parameter("sta_yaw", robot_state.sta_yaw)
            
            # 更新浮游模式状态
            floating_state = state_data.state_floating_mode
            floating_group = self.parameter_groups["floating_status"]
            floating_group.update_parameter("sta_floating_vel_x", floating_state.sta_floating_vel_x)
            floating_group.update_parameter("sta_floating_vel_y", floating_state.sta_floating_vel_y)
            floating_group.update_parameter("sta_floating_vel_z", floating_state.sta_floating_vel_z)
            floating_group.update_parameter("sta_floating_angular_x", floating_state.sta_floating_angular_x)
            floating_group.update_parameter("sta_floating_angular_y", floating_state.sta_floating_angular_y)
            floating_group.update_parameter("sta_floating_angular_z", floating_state.sta_floating_angular_z)
            
            # 更新推进器数据
            for i in range(min(4, len(floating_state.sta_thruster_power))):
                floating_group.update_parameter(f"sta_thruster_power[{i}]", floating_state.sta_thruster_power[i])
            for i in range(min(4, len(floating_state.sta_thruster_temp))):
                floating_group.update_parameter(f"sta_thruster_temp[{i}]", floating_state.sta_thruster_temp[i])
            
            # 更新轮式模式状态
            wheel_state = state_data.state_wheel_mode
            wheel_group = self.parameter_groups["wheel_status"]
            wheel_group.update_parameter("sta_wheel_linear_vel", wheel_state.sta_wheel_linear_vel)
            wheel_group.update_parameter("sta_wheel_angular_vel", wheel_state.sta_wheel_angular_vel)
            
            # 更新电机数据
            for i in range(min(3, len(wheel_state.sta_motor_data))):
                wheel_group.update_parameter(f"sta_motor_data[{i}]", wheel_state.sta_motor_data[i])
            for i in range(min(3, len(wheel_state.sta_motor_temp))):
                wheel_group.update_parameter(f"sta_motor_temp[{i}]", wheel_state.sta_motor_temp[i])
            
            # 更新电磁铁状态
            electromagnet_state = state_data.state_electromagnet
            electromagnet_group = self.parameter_groups["electromagnet_status"]
            electromagnet_group.update_parameter("sta_electromagnet_enable", electromagnet_state.sta_electromagnet_enable)
            electromagnet_group.update_parameter("sta_electromagnet_voltage", electromagnet_state.sta_electromagnet_voltage)
            
            # 更新清洗功能状态
            brush_state = state_data.state_brush
            brush_group = self.parameter_groups["brush_status"]
            brush_group.update_parameter("sta_brush_enable", brush_state.sta_brush_enable)
            brush_group.update_parameter("sta_brush_power", brush_state.sta_brush_power)
            brush_group.update_parameter("sta_water_enable", brush_state.sta_water_enable)
            brush_group.update_parameter("sta_water_flow", brush_state.sta_water_flow)
            
            # 更新系统状态
            system_state = state_data.state_system
            system_group = self.parameter_groups["system_status"]
            system_group.update_parameter("sta_system_voltage", system_state.sta_system_voltage)
            system_group.update_parameter("sta_system_current", system_state.sta_system_current)
            system_group.update_parameter("sta_system_power", system_state.sta_system_power)
            system_group.update_parameter("sta_comm_status", system_state.sta_comm_status)
            system_group.update_parameter("sta_send_time", system_state.sta_send_time)
            system_group.update_parameter("sta_packet_loss", system_state.sta_packet_loss)
            system_group.update_parameter("sta_leak_detected", system_state.sta_leak_detected)
            system_group.update_parameter("sta_uptime", system_state.sta_uptime)
                
        except Exception as e:
            print(f"更新STATE数据失败: {e}")