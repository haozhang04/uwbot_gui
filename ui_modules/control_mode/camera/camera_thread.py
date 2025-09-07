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

class CameraThread(QThread):
    """相机线程类"""
    frame_ready = pyqtSignal(np.ndarray, int)  # 帧数据, 相机ID
    
    def __init__(self, camera_id):
        super().__init__()
        self.camera_id = camera_id
        self.running = False
        self.cap = None
        
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
            self.cap = cv2.VideoCapture(self.camera_id)
            # 检查摄像头是否成功打开
            if not self.cap.isOpened():
                print(f"警告: 无法打开摄像头 {self.camera_id}，使用模拟画面")
                self.generate_mock_frames()
                return
            
            # 尝试读取一帧来验证摄像头是否正常工作
            ret, test_frame = self.cap.read()
            if not ret:
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
            self.msleep(33)  # 约30fps
            
    def generate_mock_frames(self):
        """生成模拟相机画面"""
        while self.running:
            # 创建模拟画面
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            
            # 添加渐变背景
            for i in range(480):
                frame[i, :] = [int(i/2), 50, int(255-i/2)]
                
            # 添加文字信息
            text = f"Camera {self.camera_id + 1}"
            time_text = datetime.now().strftime("%H:%M:%S")
            
            cv2.putText(frame, text, (250, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
            cv2.putText(frame, time_text, (220, 280), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, "Mock Camera Feed", (200, 350), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)
            
            # 添加移动的圆形
            import time
            t = time.time()
            x = int(320 + 200 * np.sin(t))
            y = int(240 + 100 * np.cos(t * 1.5))
            cv2.circle(frame, (x, y), 20, (0, 255, 255), -1)
            
            self.frame_ready.emit(frame, self.camera_id)
            self.msleep(33)  # 约30fps