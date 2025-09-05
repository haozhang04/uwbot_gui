#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水下机器人数据结构定义
"""
from LowlevelState import LowlevelState
from LowlevelCmd import LowlevelCmd

class RobotDataManager:
    """机器人数据管理器"""
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RobotDataManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.cmd = LowlevelCmd()
            self.state = LowlevelState()
            self._initialized = True
    
    def get_cmd_data(self):
        """获取命令数据"""
        return self.cmd
    
    def get_state_data(self):
        """获取状态数据"""
        return self.state
    
    def update_uptime(self, uptime):
        """更新系统运行时间"""
        self.state.state_system.sta_uptime = uptime
    
    def reset_commands(self):
        """重置所有命令"""
        self.cmd = LowlevelCmd()
    
    def set_camera_enable(self, camera_index, enable):
        """设置相机开关"""
        if 0 <= camera_index < len(self.cmd.cmd_camera.cmd_camera_enable):
            self.cmd.cmd_camera.cmd_camera_enable[camera_index] = enable
    
    def set_camera_zoom(self, camera_index, zoom_level):
        """设置相机缩放"""
        if 0 <= camera_index < len(self.cmd.cmd_camera.cmd_camera_zoom):
            self.cmd.cmd_camera.cmd_camera_zoom[camera_index] = zoom_level
    
    def set_camera_record(self, camera_index, record):
        """设置相机录制"""
        if 0 <= camera_index < len(self.cmd.cmd_camera.cmd_camera_record):
            self.cmd.cmd_camera.cmd_camera_record[camera_index] = record
    
    def trigger_camera_snapshot(self, camera_index):
        """触发相机截图"""
        if 0 <= camera_index < len(self.cmd.cmd_camera.cmd_camera_snapshot):
            self.cmd.cmd_camera.cmd_camera_snapshot[camera_index] = 1
    
    def get_camera_cmd(self):
        """获取相机命令状态"""
        return self.cmd.cmd_camera

# 全局函数接口
def get_robot_data():
    """获取机器人数据管理器实例"""
    return RobotDataManager()

def get_cmd_data():
    """获取命令数据"""
    return RobotDataManager().get_cmd_data()

def get_state_data():
    """获取状态数据"""
    return RobotDataManager().get_state_data()
    
    