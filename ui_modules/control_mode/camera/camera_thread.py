#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
相机线程模块
负责相机数据采集和模拟画面生成
"""

import cv2
import numpy as np
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal

# 导入配置文件
from config.uwbot_config import CAMERA_CONFIG

class CameraThread(QThread):
    """相机线程类"""
    frame_ready = pyqtSignal(np.ndarray, int)  # 帧数据, 相机ID
    
    def __init__(self, camera_id, use_rtsp=True):
        super().__init__()
        self.camera_id = camera_id
        self.use_rtsp = use_rtsp
        self.running = False
        self.cap = None
        
        # 配置RTSP流地址
        if self.use_rtsp:
            self.rtsp_url = f"{CAMERA_CONFIG.RTSP_BASE_URL}{camera_id}"
        else:
            self.rtsp_url = None
        
    def start_camera(self):
        """启动相机"""
        self.running = True
        self.start()
        
    def stop_camera(self):
        """停止相机"""
        self.running = False
        if self.cap:
            self.cap.release()
        self.quit()
        self.wait()
        
    def run(self):
        """线程运行函数"""
        # 尝试打开相机，添加更好的错误处理
        try:
            # 根据配置选择打开方式
            if self.use_rtsp:
                print(f"尝试通过RTSP流打开相机 {self.camera_id}: {self.rtsp_url}")
                self.cap = cv2.VideoCapture(self.rtsp_url)
            else:
                print(f"尝试通过OpenCV直接打开相机 {self.camera_id}")
                self.cap = cv2.VideoCapture(self.camera_id)
            
            # 检查摄像头是否成功打开
            if not self.cap.isOpened():
                if self.use_rtsp:
                    print(f"警告: 无法打开RTSP流 {self.rtsp_url}，使用模拟画面")
                    self.generate_mock_frames()
                    return
                else:
                    print(f"警告: 无法打开摄像头 {self.camera_id}，使用模拟画面")
                    self.generate_mock_frames()
                    return
            
            # 设置相机参数：使用配置文件中的分辨率和帧率
            if self.cap.isOpened():
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_CONFIG.DEFAULT_WIDTH)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_CONFIG.DEFAULT_HEIGHT)
                self.cap.set(cv2.CAP_PROP_FPS, CAMERA_CONFIG.DEFAULT_FPS)
                print(f"相机 {self.camera_id} 设置参数: {CAMERA_CONFIG.DEFAULT_WIDTH}x{CAMERA_CONFIG.DEFAULT_HEIGHT}@{CAMERA_CONFIG.DEFAULT_FPS}fps")
            
            # 尝试读取一帧来验证摄像头是否正常工作
            ret, test_frame = self.cap.read()
            if not ret:
                if self.use_rtsp:
                    print(f"警告: RTSP流 {self.rtsp_url} 无法读取画面，使用模拟画面")
                    self.cap.release()
                    self.generate_mock_frames()
                    return
                else:
                    print(f"警告: 摄像头 {self.camera_id} 无法读取画面，使用模拟画面")
                    self.cap.release()
                    self.generate_mock_frames()
                    return
        except Exception as e:
            print(f"警告: 摄像头 {self.camera_id} 初始化失败: {e}，使用模拟画面")
            self.generate_mock_frames()
            return
            
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.frame_ready.emit(frame, self.camera_id)
            self.msleep(CAMERA_CONFIG.MOCK_FRAME_INTERVAL)  # 使用配置的帧间隔
            
    def generate_mock_frames(self):
        """生成模拟相机画面"""
        while self.running:
            # 创建模拟画面 (使用配置的分辨率)
            frame = np.zeros((CAMERA_CONFIG.MOCK_FRAME_HEIGHT, CAMERA_CONFIG.MOCK_FRAME_WIDTH, 3), dtype=np.uint8)
            
            # 添加渐变背景
            for i in range(CAMERA_CONFIG.MOCK_FRAME_HEIGHT):
                # 确保颜色值在0-255范围内
                red_val = min(255, max(0, int(i/4)))
                blue_val = min(255, max(0, int(255-i/4)))
                frame[i, :] = [red_val, 50, blue_val]
                
            # 添加文字信息 (适应配置的分辨率)
            camera_text = f"Camera {self.camera_id + 1}"
            resolution_text = f"{CAMERA_CONFIG.MOCK_FRAME_WIDTH}x{CAMERA_CONFIG.MOCK_FRAME_HEIGHT}@{CAMERA_CONFIG.DEFAULT_FPS}fps"
            time_text = datetime.now().strftime("%H:%M:%S")
            
            cv2.putText(frame, camera_text, (600, 350), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 4)
            cv2.putText(frame, resolution_text, (600, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
            cv2.putText(frame, time_text, (700, 550), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
            cv2.putText(frame, "Mock Camera Feed", (650, 600), cv2.FONT_HERSHEY_SIMPLEX, 2, (200, 200, 200), 3)
            
            # 添加移动的圆形 (适应配置的分辨率)
            import time
            t = time.time()
            x = int(CAMERA_CONFIG.MOCK_FRAME_WIDTH//2 + 400 * np.sin(t))  # 中心x
            y = int(CAMERA_CONFIG.MOCK_FRAME_HEIGHT//2 + 200 * np.cos(t * 1.5))  # 中心y
            cv2.circle(frame, (x, y), 40, (0, 255, 255), -1)
            
            self.frame_ready.emit(frame, self.camera_id)
            self.msleep(CAMERA_CONFIG.MOCK_FRAME_INTERVAL)  # 使用配置的帧间隔