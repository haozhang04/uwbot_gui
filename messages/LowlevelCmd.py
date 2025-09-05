#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水下机器人低级控制命令数据结构
包含浮游模式、轮式模式、电磁铁、清洗、相机等功能的控制命令
"""
from dataclasses import dataclass, field
from typing import List

"""浮游模式控制命令"""
@dataclass
class cmd_floating_mode:
    # 浮游模式控制###############################################
    cmd_floating_vel_x: float = 0.0  # X方向线速度 (m/s)
    cmd_floating_vel_y: float = 0.0  # Y方向线速度 (m/s)
    cmd_floating_vel_z: float = 0.0  # Z方向线速度 (m/s)
    cmd_floating_angular_roll: float = 0.0  # 横滚角度 (rad)
    cmd_floating_angular_yaw: float = 0.0  # 航向角度 (rad)
    cmd_floating_angular_pitch: float = 0.0  # 俯仰角度 (rad)
    
    # 深度控制
    cmd_depth_hold: int = 0  # 定深功能: 0-关闭, 1-开启
    cmd_target_depth: float = 0.0  # 目标深度 (m)
    
    # 定航控制
    cmd_floating_heading_hold: int = 0  # 定向功能: 0-关闭, 1-开启
    cmd_target_roll: float = 0.0  # 目标横滚角 (rad)
    cmd_target_yaw: float = 0.0  # 目标航向角 (rad)
    cmd_target_pitch: float = 0.0  # 目标俯仰角 (rad)
    # 浮游模式控制###############################################

"""轮式模式控制命令"""
@dataclass
class cmd_wheel_mode:
    # 轮式模式控制###############################################
    cmd_wheel_linear_vel: float = 0.0  # 线速度 (m/s)
    cmd_wheel_angular_vel: float = 0.0  # 角速度 (rad/s)
    
    # 轮式定航控制
    cmd_wheel_heading_hold: int = 0  # 定向功能: 0-关闭, 1-开启
    cmd_target_heading: float = 0.0  # 目标方向 (rad)
    # 轮式模式控制###############################################

"""电磁铁功能控制"""
@dataclass
class cmd_electromagnet:
    cmd_electromagnet_enable: int = 0  # 电磁铁状态: 0-关闭, 1-开启
    cmd_electromagnet_voltage: int = 0  # 电磁铁电压: 0-100%

"""清洗功能控制"""
@dataclass
class cmd_brush:
    cmd_brush_power: int = 0  # 滚刷功率: 0-100%
    cmd_brush_enable: int = 0  # 滚刷开关: 0-关闭, 1-开启
    cmd_water_flow: int = 0  # 水流强度: 0-100%
    cmd_water_enable: int = 0  # 水流开关: 0-关闭, 1-开启

"""相机功能控制"""
@dataclass
class cmd_camera:
    cmd_camera_enable: List[int] = field(default_factory=lambda: [0, 0])  # 相机开关: [前置, 后置] 0-关闭, 1-开启
    cmd_camera_zoom: List[int] = field(default_factory=lambda: [0, 0])  # 相机缩放: [前置, 后置] 0-100%
    cmd_camera_record: List[int] = field(default_factory=lambda: [0, 0])  # 录制功能: [前置, 后置] 0-停止, 1-开始
    cmd_camera_record_time: List[int] = field(default_factory=lambda: [0, 0])  # 录制功能: [前置, 后置] 0-停止, 1-开始
    cmd_camera_snapshot: List[int] = field(default_factory=lambda: [0, 0])  # 截图功能: [前置, 后置] 0-无操作, 1-截图
    cmd_storage_path: List[str] = field(default_factory=lambda: ["", ""])  # 储存路径
    cmd_camera_path: List[str] = field(default_factory=lambda: ["", ""])  # 储存名称

@dataclass
class LowlevelCmd:
    """机器人控制结构体"""
    cmd_floating_mode: cmd_floating_mode = field(default_factory=cmd_floating_mode)
    cmd_wheel_mode: cmd_wheel_mode = field(default_factory=cmd_wheel_mode)
    cmd_electromagnet: cmd_electromagnet = field(default_factory=cmd_electromagnet)
    cmd_brush: cmd_brush = field(default_factory=cmd_brush)
    cmd_camera: cmd_camera = field(default_factory=cmd_camera)



