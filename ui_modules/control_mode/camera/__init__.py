#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
相机控制子模块
包含相机线程、视频录制、单相机组件和双相机组件功能
"""

from .camera_thread import CameraThread
from .video_recorder import VideoRecorder
from .camera_widget import CameraWidget
from .dual_camera_widget import DualCameraWidget

__all__ = ['CameraThread', 'VideoRecorder', 'CameraWidget', 'DualCameraWidget']