#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水下机器人低级状态数据结构
包含浮游模式、轮式模式、电磁铁、清洗等功能的状态数据
"""

from dataclasses import dataclass, field
from typing import List

"""机器人状态"""
@dataclass
class state_robot:
    # 位置和姿态
    sta_position_x: float = 0.0  # X坐标 (m)
    sta_position_y: float = 0.0  # Y坐标 (m)
    sta_position_z: float = 0.0  # Z坐标/深度 (m)
    sta_roll: float = 0.0  # 横滚角 (rad)
    sta_pitch: float = 0.0  # 俯仰角 (rad)
    sta_yaw: float = 0.0 # 偏航角 (rad)

"""浮游模式状态"""
@dataclass
class state_floating_mode:
    #速度状态
    sta_floating_vel_x: float = 0.0  # X方向线速度 (m/s)
    sta_floating_vel_y: float = 0.0  # Y方向线速度 (m/s)
    sta_floating_vel_z: float = 0.0  # Z方向线速度 (m/s)
    sta_floating_angular_x: float = 0.0  # X轴角速度 (rad/s)
    sta_floating_angular_y: float = 0.0  # Y轴角速度 (rad/s)
    sta_floating_angular_z: float = 0.0  # Z轴角速度 (rad/s)

    # 推进器状态
    sta_thruster_power: List[float] = field(default_factory=lambda: [0.0] * 4)  # 4个推进器功率百分比
    sta_thruster_temp: List[float] = field(default_factory=lambda: [25.0] * 4)  # 4个推进器温度

"""轮式模式状态"""
@dataclass
class state_wheel_mode:
    #速度状态
    sta_wheel_linear_vel: float = 0.0  # 线速度 (m/s)
    sta_wheel_angular_vel: float = 0.0  # 角速度 (rad/s)
    
    # 电机状态
    sta_motor_data: List[float] = field(default_factory=lambda: [0.0] * 3)  # 3个电机数据 0-舵机角度 (°), 1-1号电机速度 (m/s), 2-1号电机速度(m/s)
    sta_motor_temp: List[float] = field(default_factory=lambda: [25.0] * 3)  # 3个电机温度

"""电磁铁状态"""
@dataclass
class state_electromagnet:
    sta_electromagnet_enable: int = -1  # 电磁铁状态: 0-关闭, 1-开启
    sta_electromagnet_voltage: int = 0  # 电磁铁电压: 0-100%

"""清洗功能控制"""
@dataclass
class state_brush:
    sta_brush_enable: int = -1  # 滚刷开关: 0-关闭, 1-开启
    sta_brush_power: int = 0  # 滚刷功率: 0-100%

    sta_water_enable: int = -1  # 水流开关: 0-关闭, 1-开启
    sta_water_flow: int = 0  # 水流强度: 0-100%

"""系统状态"""
@dataclass
class state_system:
    sta_system_voltage: float = -1.0  # 电压 (V)
    sta_system_current: float = -1.0  #电流 (A)
    sta_system_power: float =-1.0  # 功耗 (W)

    sta_comm_status: int = -1  # 通信状态: 0-断开, 1-正常, 2-延迟高, 3-不稳定
    sta_communication_status: int = 1  # 通信状态别名，兼容性
    sta_send_time: int = -1  # 通信延迟 (ms) 传输来的是发送的时间戳,需要由当前时间，计算延迟
    sta_packet_loss: int = 0  # 丢包计数

    sta_leak_detected: int = -1  # 漏水检测: 0-正常, 1-检测到漏水
    sta_uptime: int = 0  # 系统运行时间 (s)

@dataclass
class LowlevelState:
    """机器人状态结构体"""
    state_robot: state_robot = field(default_factory=state_robot)
    state_floating_mode: state_floating_mode = field(default_factory=state_floating_mode)
    state_wheel_mode: state_wheel_mode = field(default_factory=state_wheel_mode)
    state_electromagnet: state_electromagnet = field(default_factory=state_electromagnet)
    state_brush: state_brush = field(default_factory=state_brush)
    state_system: state_system = field(default_factory=state_system)
    
    