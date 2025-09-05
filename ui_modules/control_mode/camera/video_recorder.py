#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频录制模块
负责视频录制功能的实现
"""

import cv2

class VideoRecorder:
    """视频录制类"""
    
    def __init__(self):
        self.writer = None
        self.recording = False
        self.filename = None
        
    def start_recording(self, filename, frame_size, fps=30):
        """开始录制"""
        try:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.writer = cv2.VideoWriter(filename, fourcc, fps, frame_size)
            self.recording = True
            self.filename = filename
            return True
        except Exception as e:
            print(f"录制启动失败: {e}")
            return False
            
    def write_frame(self, frame):
        """写入帧"""
        if self.recording and self.writer:
            self.writer.write(frame)
            
    def stop_recording(self):
        """停止录制"""
        if self.writer:
            self.writer.release()
            self.writer = None
        self.recording = False
        filename = self.filename
        self.filename = None
        return filename
    
    def is_recording(self):
        """检查是否正在录制"""
        return self.recording
    
    def get_current_filename(self):
        """获取当前录制文件名"""
        return self.filename