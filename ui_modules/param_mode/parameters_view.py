#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参数界面主模块
3模块横向布局：CMD控制 | STATE状态 | 绘图显示
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QLabel, 
    QGroupBox, QPushButton, QScrollArea, QSpinBox, QDoubleSpinBox,
    QCheckBox, QFrame
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import logging

# 导入子模块
from .plot_display import PlotDisplayWidget
from .data_display import CmdDataDisplayWidget, StateDataDisplayWidget

class ParametersViewWidget(QWidget):
    """参数界面主组件 - 3模块横向布局"""
    
    def __init__(self, robot_data):
        super().__init__()
        self.robot_data = robot_data
        self.init_ui()
        
        # 设置定时器更新数据
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(self.robot_data.uptime)  # 使用统一的uptime参数，20ms更新一次
    
    def init_ui(self):
        """初始化用户界面 - 3模块横向布局"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 创建主分割器 - 横向分割
        main_splitter = QSplitter(Qt.Horizontal)
        
        # 左一模块：CMD控制参数 (30%)
        self.cmd_display = CmdDataDisplayWidget(self.robot_data)
        self.cmd_display.parameterChanged.connect(self.on_parameter_changed)
        self.cmd_display.plotSelectionChanged.connect(self.on_plot_selection_changed)
        
        # 左二模块：STATE状态参数 (30%)
        self.state_display = StateDataDisplayWidget(self.robot_data)
        self.state_display.parameterChanged.connect(self.on_state_parameter_changed)
        # 连接plot选择信号
        for group_name, group_widget in self.state_display.parameter_groups.items():
            group_widget.plotSelectionChanged.connect(self.on_plot_selection_changed)
        
        # 右边模块：绘图显示 (40%)
        plot_container = self.create_plot_module()
        
        # 添加到分割器
        main_splitter.addWidget(self.cmd_display)
        main_splitter.addWidget(self.state_display)
        main_splitter.addWidget(plot_container)
        
        # 设置比例 3.5:3.5:3
        main_splitter.setSizes([600, 600, 800])
        
        layout.addWidget(main_splitter)
        
        # 设置整体样式
        self.setStyleSheet("""
            ParametersViewWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            }
        """)
    

    
    def create_plot_module(self):
        """创建绘图显示模块"""
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border: 1px solid #e9ecef;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.plot_display = PlotDisplayWidget(self.robot_data)
        layout.addWidget(self.plot_display)
        
        return container
    
    def on_parameter_changed(self, group_name, param_name, value):
        """处理参数变更"""
        try:
            if self.robot_data:
                # 获取CMD数据对象
                cmd_data = self.robot_data.get_cmd_data()
                
                # 根据组名和参数名更新对应的数据
                if group_name == "cmd_floating_mode":
                    floating_cmd = cmd_data.cmd_floating_mode
                    if param_name == "cmd_floating_vel_x":
                        floating_cmd.cmd_floating_vel_x = float(value)
                    elif param_name == "cmd_floating_vel_y":
                        floating_cmd.cmd_floating_vel_y = float(value)
                    elif param_name == "cmd_floating_vel_z":
                        floating_cmd.cmd_floating_vel_z = float(value)
                    elif param_name == "cmd_floating_angular_roll":
                        floating_cmd.cmd_floating_angular_roll = float(value)
                    elif param_name == "cmd_floating_angular_yaw":
                        floating_cmd.cmd_floating_angular_yaw = float(value)
                    elif param_name == "cmd_floating_angular_pitch":
                        floating_cmd.cmd_floating_angular_pitch = float(value)
                    elif param_name == "cmd_depth_hold":
                        floating_cmd.cmd_depth_hold = int(value)
                    elif param_name == "cmd_target_depth":
                        floating_cmd.cmd_target_depth = float(value)
                    elif param_name == "cmd_floating_heading_hold":
                        floating_cmd.cmd_floating_heading_hold = int(value)
                    elif param_name == "cmd_target_roll":
                        floating_cmd.cmd_target_roll = float(value)
                    elif param_name == "cmd_target_yaw":
                        floating_cmd.cmd_target_yaw = float(value)
                    elif param_name == "cmd_target_pitch":
                        floating_cmd.cmd_target_pitch = float(value)
                        
                elif group_name == "cmd_wheel_mode":
                    wheel_cmd = cmd_data.cmd_wheel_mode
                    if param_name == "cmd_wheel_linear_vel":
                        wheel_cmd.cmd_wheel_linear_vel = float(value)
                    elif param_name == "cmd_wheel_angular_vel":
                        wheel_cmd.cmd_wheel_angular_vel = float(value)
                    elif param_name == "cmd_wheel_heading_hold":
                        wheel_cmd.cmd_wheel_heading_hold = int(value)
                    elif param_name == "cmd_target_heading":
                        wheel_cmd.cmd_target_heading = float(value)
                        
                elif group_name == "cmd_electromagnet":
                    electromagnet_cmd = cmd_data.cmd_electromagnet
                    if param_name == "cmd_electromagnet_enable":
                        electromagnet_cmd.cmd_electromagnet_enable = int(value)
                    elif param_name == "cmd_electromagnet_voltage":
                        electromagnet_cmd.cmd_electromagnet_voltage = int(value)
                        
                elif group_name == "cmd_brush":
                    brush_cmd = cmd_data.cmd_brush
                    if param_name == "cmd_brush_enable":
                        brush_cmd.cmd_brush_enable = int(value)
                    elif param_name == "cmd_brush_power":
                        brush_cmd.cmd_brush_power = int(value)
                    elif param_name == "cmd_water_enable":
                        brush_cmd.cmd_water_enable = int(value)
                    elif param_name == "cmd_water_flow":
                        brush_cmd.cmd_water_flow = int(value)
                        
                elif group_name == "cmd_camera":
                    camera_cmd = cmd_data.cmd_camera
                    if param_name == "cmd_camera_enable[0]":
                        if len(camera_cmd.cmd_camera_enable) > 0:
                            camera_cmd.cmd_camera_enable[0] = int(value)
                    elif param_name == "cmd_camera_enable[1]":
                        if len(camera_cmd.cmd_camera_enable) > 1:
                            camera_cmd.cmd_camera_enable[1] = int(value)
                    elif param_name == "cmd_camera_zoom[0]":
                        if len(camera_cmd.cmd_camera_zoom) > 0:
                            camera_cmd.cmd_camera_zoom[0] = int(value)
                    elif param_name == "cmd_camera_zoom[1]":
                        if len(camera_cmd.cmd_camera_zoom) > 1:
                            camera_cmd.cmd_camera_zoom[1] = int(value)
                    elif param_name == "cmd_camera_record[0]":
                        if len(camera_cmd.cmd_camera_record) > 0:
                            camera_cmd.cmd_camera_record[0] = int(value)
                    elif param_name == "cmd_camera_record[1]":
                        if len(camera_cmd.cmd_camera_record) > 1:
                            camera_cmd.cmd_camera_record[1] = int(value)
                    elif param_name == "cmd_camera_snapshot[0]":
                        if len(camera_cmd.cmd_camera_snapshot) > 0:
                            camera_cmd.cmd_camera_snapshot[0] = int(value)
                    elif param_name == "cmd_camera_snapshot[1]":
                        if len(camera_cmd.cmd_camera_snapshot) > 1:
                            camera_cmd.cmd_camera_snapshot[1] = int(value)
                
                print(f"参数已更新: {group_name}.{param_name} = {value}")
                # 记录控制参数变更到日志
                logging.info(f"控制参数变更: {group_name}.{param_name} = {value}")
                
        except Exception as e:
            print(f"更新参数失败: {group_name}.{param_name} = {value}, 错误: {e}")
            # 记录参数更新失败到日志
            logging.error(f"控制参数更新失败: {group_name}.{param_name} = {value}, 错误: {e}")
    
    def on_state_parameter_changed(self, group_name, param_name, value):
        """处理状态参数变更"""
        try:
            if not self.robot_data:
                return
                
            state_data = self.robot_data.get_state_data()
            if not state_data:
                return
                
            # 根据组名和参数名更新对应的状态数据
            if group_name == "robot_status":
                robot_state = state_data.state_robot
                if param_name == "sta_position_x":
                    robot_state.sta_position_x = float(value)
                elif param_name == "sta_position_y":
                    robot_state.sta_position_y = float(value)
                elif param_name == "sta_position_z":
                    robot_state.sta_position_z = float(value)
                elif param_name == "sta_roll":
                    robot_state.sta_roll = float(value)
                elif param_name == "sta_pitch":
                    robot_state.sta_pitch = float(value)
                elif param_name == "sta_yaw":
                    robot_state.sta_yaw = float(value)
                    
            elif group_name == "floating_status":
                floating_state = state_data.state_floating_mode
                if param_name == "sta_floating_vel_x":
                    floating_state.sta_floating_vel_x = float(value)
                elif param_name == "sta_floating_vel_y":
                    floating_state.sta_floating_vel_y = float(value)
                elif param_name == "sta_floating_vel_z":
                    floating_state.sta_floating_vel_z = float(value)
                elif param_name == "sta_floating_angular_x":
                    floating_state.sta_floating_angular_x = float(value)
                elif param_name == "sta_floating_angular_y":
                    floating_state.sta_floating_angular_y = float(value)
                elif param_name == "sta_floating_angular_z":
                    floating_state.sta_floating_angular_z = float(value)
                elif param_name.startswith("sta_thruster_power["):
                    index = int(param_name.split('[')[1].split(']')[0])
                    if 0 <= index < len(floating_state.sta_thruster_power):
                        floating_state.sta_thruster_power[index] = float(value)
                elif param_name.startswith("sta_thruster_temp["):
                    index = int(param_name.split('[')[1].split(']')[0])
                    if 0 <= index < len(floating_state.sta_thruster_temp):
                        floating_state.sta_thruster_temp[index] = float(value)
                        
            elif group_name == "wheel_status":
                wheel_state = state_data.state_wheel_mode
                if param_name == "sta_wheel_linear_vel":
                    wheel_state.sta_wheel_linear_vel = float(value)
                elif param_name == "sta_wheel_angular_vel":
                    wheel_state.sta_wheel_angular_vel = float(value)
                elif param_name.startswith("sta_motor_data["):
                    index = int(param_name.split('[')[1].split(']')[0])
                    if 0 <= index < len(wheel_state.sta_motor_data):
                        wheel_state.sta_motor_data[index] = float(value)
                elif param_name.startswith("sta_motor_temp["):
                    index = int(param_name.split('[')[1].split(']')[0])
                    if 0 <= index < len(wheel_state.sta_motor_temp):
                        wheel_state.sta_motor_temp[index] = float(value)
                        
            elif group_name == "electromagnet_status":
                electromagnet_state = state_data.state_electromagnet
                if param_name == "sta_electromagnet_enable":
                    electromagnet_state.sta_electromagnet_enable = int(value)
                elif param_name == "sta_electromagnet_voltage":
                    electromagnet_state.sta_electromagnet_voltage = int(value)
                    
            elif group_name == "brush_status":
                brush_state = state_data.state_brush
                if param_name == "sta_brush_enable":
                    brush_state.sta_brush_enable = int(value)
                elif param_name == "sta_brush_power":
                    brush_state.sta_brush_power = int(value)
                elif param_name == "sta_water_enable":
                    brush_state.sta_water_enable = int(value)
                elif param_name == "sta_water_flow":
                    brush_state.sta_water_flow = int(value)
                    
            elif group_name == "system_status":
                system_state = state_data.state_system
                if param_name == "sta_system_voltage":
                    system_state.sta_system_voltage = float(value)
                elif param_name == "sta_system_current":
                    system_state.sta_system_current = float(value)
                elif param_name == "sta_system_power":
                    system_state.sta_system_power = float(value)
                elif param_name == "sta_comm_status":
                    system_state.sta_comm_status = int(value)
                elif param_name == "sta_comm_latency":
                    system_state.sta_comm_latency = int(value)
                elif param_name == "sta_packet_loss":
                    system_state.sta_packet_loss = int(value)
                elif param_name == "sta_leak_detected":
                    system_state.sta_leak_detected = int(value)
                elif param_name == "sta_uptime":
                    # uptime是只读参数，由系统自动更新，不允许手动修改
                    print(f"警告: sta_uptime是只读参数，忽略手动修改请求: {value}")
                    return
            
            # print(f"状态参数已更新: {group_name}.{param_name} = {value}")
            
        except Exception as e:
            print(f"更新状态参数失败: {group_name}.{param_name} = {value}, 错误: {e}")
    
    def on_plot_selection_changed(self, group_name, param_name, plot_index):
        """处理plot选择变化"""
        if plot_index == 0:  # "-- 不显示 --"
            # 清除所有图表中该参数的显示
            for i in range(4):
                if self.plot_display.plot_widget.plot_assignments[i] == f"{group_name}.{param_name}":
                    self.plot_display.plot_widget.set_plot_parameter(i, None)
        else:
            # 设置参数显示在指定图表
            plot_idx = plot_index - 1  # 转换为0-3的索引
            full_param_name = f"{group_name}.{param_name}"
            self.plot_display.plot_widget.set_plot_parameter(plot_idx, full_param_name)
    
    def update_display(self):
        """更新显示数据"""
        try:
            # 更新CMD控制参数显示
            self.cmd_display.update_display()
            
            # 更新STATE状态参数显示
            self.state_display.update_display()
            
            # 更新plot数据
            self.update_plot_data()
            
            # 更新绘图显示
            self.plot_display.update_display()
            
        except Exception as e:
            print(f"更新显示数据失败: {e}")
    
    def update_plot_data(self):
        """更新绘图数据"""
        if not self.robot_data:
            return
            
        try:
            # 更新状态数据
            state_data = self.robot_data.get_state_data()
            if state_data:
                # 遍历所有状态参数组，将数据传递给plot_widget
                for group_name, group_widget in self.state_display.parameter_groups.items():
                    # 根据组名获取对应的状态数据对象
                    if group_name == "robot_status":
                        group_obj = state_data.state_robot
                    elif group_name == "floating_status":
                        group_obj = state_data.state_floating_mode
                    elif group_name == "wheel_status":
                        group_obj = state_data.state_wheel_mode
                    elif group_name == "electromagnet_status":
                        group_obj = state_data.state_electromagnet
                    elif group_name == "brush_status":
                        group_obj = state_data.state_brush
                    elif group_name == "system_status":
                        group_obj = state_data.state_system
                    else:
                        continue
                        
                    # 遍历参数并更新数据
                    for param_name in group_widget.parameters.keys():
                        if hasattr(group_obj, param_name):
                            value = getattr(group_obj, param_name)
                            full_param_name = f"{group_name}.{param_name}"
                            self.plot_display.plot_widget.update_data(full_param_name, value)
            
            # 更新CMD数据
            cmd_data = self.robot_data.get_cmd_data()
            if cmd_data:
                # 遍历所有CMD参数组，将数据传递给plot_widget
                for group_name, group_widget in self.cmd_display.parameter_groups.items():
                    # 根据组名获取对应的CMD数据对象
                    if group_name == "cmd_floating_mode":
                        group_obj = cmd_data.cmd_floating_mode
                    elif group_name == "cmd_wheel_mode":
                        group_obj = cmd_data.cmd_wheel_mode
                    elif group_name == "cmd_electromagnet":
                        group_obj = cmd_data.cmd_electromagnet
                    elif group_name == "cmd_brush":
                        group_obj = cmd_data.cmd_brush
                    elif group_name == "cmd_camera":
                        group_obj = cmd_data.cmd_camera
                    else:
                        continue
                        
                    # 遍历参数并更新数据
                    for param_name in group_widget.parameters.keys():
                        if hasattr(group_obj, param_name):
                            value = getattr(group_obj, param_name)
                            full_param_name = f"{group_name}.{param_name}"
                            self.plot_display.plot_widget.update_data(full_param_name, value)
                        elif '[' in param_name and ']' in param_name:
                            # 处理数组参数，如 cmd_camera_enable[0]
                            base_name = param_name.split('[')[0]
                            index_str = param_name.split('[')[1].split(']')[0]
                            try:
                                index = int(index_str)
                                if hasattr(group_obj, base_name):
                                    array_attr = getattr(group_obj, base_name)
                                    if isinstance(array_attr, list) and 0 <= index < len(array_attr):
                                        value = array_attr[index]
                                        full_param_name = f"{group_name}.{param_name}"
                                        self.plot_display.plot_widget.update_data(full_param_name, value)
                            except (ValueError, IndexError):
                                continue
                        
        except Exception as e:
            print(f"更新绘图数据失败: {e}")