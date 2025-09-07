#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UWBot配置文件
按照文件/模块分类的配置结构
"""

import os

# =============================================================================
# 主程序配置 (main.py)
# =============================================================================
class MainConfig:
    """主程序配置"""
    # 应用程序信息
    APP_NAME = "水下机器人控制系统"
    APP_VERSION = "1.0.0"
    WINDOW_TITLE = "水下机器人控制系统"
    
    # 定时器配置
    UPDATE_TIMER_INTERVAL = 20  # ms, 50Hz

# =============================================================================
# 相机配置 (ui_modules/control_mode/camera/)
# =============================================================================
class CameraConfig:
    """相机配置"""
    # 相机基本参数
    DEFAULT_WIDTH = 1920
    DEFAULT_HEIGHT = 1080
    DEFAULT_FPS = 30
    
    # RTSP流配置
    RTSP_CAMERA_0_URL = "rtsp://192.168.2.66:8554/mystream0"
    RTSP_CAMERA_1_URL = "rtsp://192.168.2.66:8554/mystream1"
    RTSP_BASE_URL = "rtsp://192.168.2.66:8554/mystream"

    # 相机打开方式
    USE_RTSP = True
    
    # 相机ID配置
    CAMERA_0_ID = 0
    CAMERA_1_ID = 1
    MAX_CAMERA_COUNT = 2
    
    # Mock帧配置
    MOCK_FRAME_INTERVAL = 33  # ms，约30fps
    MOCK_FRAME_WIDTH = 1920
    MOCK_FRAME_HEIGHT = 1080
    
    # 文件路径配置
    DEFAULT_SCREENSHOT_DIR = "camera_data/camera{}_screenshots"
    DEFAULT_RECORDING_DIR = "camera_data/camera{}_recordings"

# =============================================================================
# 视频录制配置 (ui_modules/control_mode/camera/video_recorder.py)
# =============================================================================
class VideoConfig:
    """视频录制配置"""
    # 录制参数
    DEFAULT_FPS = 30.0
    DEFAULT_CODEC = 'XVID'
    DEFAULT_QUALITY = 0.8
    
    # 文件配置
    DEFAULT_OUTPUT_DIR = "recordings"
    DEFAULT_FILE_FORMAT = "recording_%Y%m%d_%H%M%S.mp4"
    FILENAME_FORMAT = "%Y%m%d_%H%M%S"
    
    # 录制分辨率
    RECORD_WIDTH = 1920
    RECORD_HEIGHT = 1080

# =============================================================================
# 运动控制配置 (ui_modules/control_mode/motion/motion_control.py)
# =============================================================================
class MotionControlConfig:
    """运动控制配置"""
    # 安全限制
    EMERGENCY_STOP_ENABLED = True
    MAX_DEPTH = 50.0  # m
    MIN_DEPTH = 0.0   # m
    
    # 速度限制
    MAX_LINEAR_VELOCITY = 2.0  # m/s
    MAX_ANGULAR_VELOCITY = 1.0  # rad/s
    VELOCITY_STEP = 0.1
    CONTROL_UPDATE_RATE = 50  # Hz
    
    # 布局配置
    LAYOUT_SPACING = 20
    LAYOUT_MARGINS = 20

# =============================================================================
# 键盘控制配置 (ui_modules/control_mode/motion/keyboard_control.py)
# =============================================================================
class KeyboardControlConfig:
    """键盘控制配置"""
    # 按键增量
    LINEAR_STEP = 0.1  # m/s
    ANGULAR_STEP = 5.0  # degrees
    WHEEL_LINEAR_STEP = 0.1  # m/s
    WHEEL_ANGULAR_STEP = 0.1  # rad/s
    
    # 键盘控制步长
    DEFAULT_STEP_SIZE = 0.1
    
    # 定时器间隔
    KEY_TIMER_INTERVAL = 50  # ms
    
    # 速度限制
    VELOCITY_LIMITS = {
        'vel_x': (-2.0, 2.0),
        'vel_y': (-2.0, 2.0),
        'vel_z': (-2.0, 2.0),
        'ang_roll': (-180, 180),
        'ang_yaw': (-180, 180),
        'ang_pitch': (-180, 180),
        'wheel_linear_vel': (-2.0, 2.0),
        'wheel_angular_vel': (-2.0, 2.0)
    }
    
    # 默认速度值
    DEFAULT_VELOCITIES = {
        'vel_x': 0.0,
        'vel_y': 0.0,
        'vel_z': 0.0,
        'ang_roll': 0.0,
        'ang_yaw': 0.0,
        'ang_pitch': 0.0,
        'wheel_linear_vel': 0.0,
        'wheel_angular_vel': 0.0
    }

# =============================================================================
# 主状态栏配置 (ui_modules/control_mode/status/main_status_bar.py)
# =============================================================================
class MainStatusBarConfig:
    """主状态栏配置"""
    
    # 电压阈值
    VOLTAGE_WARNING_THRESHOLD = 44.0  # V
    VOLTAGE_ERROR_THRESHOLD = 40.0    # V
    
    # 通信状态阈值
    LATENCY_WARNING_THRESHOLD = 100   # ms
    LATENCY_ERROR_THRESHOLD = 300     # ms
    PACKET_LOSS_WARNING_THRESHOLD = 1.0  # %
    PACKET_LOSS_ERROR_THRESHOLD = 5.0    # %

# =============================================================================
# 日志配置 (ui_modules/log_mode/log_view.py)
# =============================================================================
class LogConfig:
    """日志配置"""
    # 日志级别
    DEFAULT_LOG_LEVEL = "INFO"
    
    # 日志文件
    DEFAULT_LOG_FOLDER = "logs"
    DEFAULT_LOG_FILE = "uwbot.log"
    
    # 显示配置
    MAX_DISPLAY_LINES = 1000
    AUTO_SCROLL = True
    AUTO_REFRESH = True
    REFRESH_INTERVAL = 1000  # ms
    
    # 字体配置
    FONT_FAMILY = "Consolas"
    FONT_SIZE = 9
    
    # 格式配置
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# =============================================================================
# 机器人数据配置 (messages/robot_data.py)
# =============================================================================
class RobotDataConfig:
    """机器人数据配置"""
    # 定时器间隔
    APP_DT = 20  # ms, 50Hz
    
    # 数据历史配置
    MAX_DATA_HISTORY = 1000
    DATA_VALIDATION_ENABLED = True
    
    # 状态更新配置
    STATE_UPDATE_THRESHOLD = 0.001
    COMMAND_UPDATE_THRESHOLD = 0.001
# =============================================================================
# 配置管理器
# =============================================================================
class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.main = MainConfig()
        self.camera = CameraConfig()
        self.video = VideoConfig()
        self.motion_control = MotionControlConfig()
        self.keyboard_control = KeyboardControlConfig()
        self.main_status_bar = MainStatusBarConfig()
        self.log = LogConfig()
        self.robot_data = RobotDataConfig()
    
    def get_config_dict(self):
        """获取所有配置的字典形式"""
        return {
            'main': self._class_to_dict(self.main),
            'camera': self._class_to_dict(self.camera),
            'video': self._class_to_dict(self.video),
            'motion_control': self._class_to_dict(self.motion_control),
            'keyboard_control': self._class_to_dict(self.keyboard_control),
            'main_status_bar': self._class_to_dict(self.main_status_bar),
            'log': self._class_to_dict(self.log),
            'robot_data': self._class_to_dict(self.robot_data),
        }
    
    def _class_to_dict(self, cls):
        """将类属性转换为字典"""
        return {key: value for key, value in cls.__dict__.items() 
                if not key.startswith('_') and not callable(value)}

# =============================================================================
# 全局配置实例
# =============================================================================
config = ConfigManager()

# 便捷访问
MAIN_CONFIG = config.main
CAMERA_CONFIG = config.camera
VIDEO_CONFIG = config.video
MOTION_CONTROL_CONFIG = config.motion_control
KEYBOARD_CONTROL_CONFIG = config.keyboard_control
MAIN_STATUS_BAR_CONFIG = config.main_status_bar
LOG_CONFIG = config.log
ROBOT_DATA_CONFIG = config.robot_data

if __name__ == "__main__":
    # 测试配置
    print("UWBot配置文件加载成功")
    print(f"应用程序: {MAIN_CONFIG.APP_NAME} v{MAIN_CONFIG.APP_VERSION}")
    print(f"相机默认分辨率: {CAMERA_CONFIG.DEFAULT_WIDTH}x{CAMERA_CONFIG.DEFAULT_HEIGHT}")
    print(f"相机默认帧率: {CAMERA_CONFIG.DEFAULT_FPS}")
    print(f"相机RTSP URL: {CAMERA_CONFIG.RTSP_BASE_URL}")
    print(f"日志级别: {LOG_CONFIG.DEFAULT_LOG_LEVEL}")