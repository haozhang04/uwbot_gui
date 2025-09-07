from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
import math
import time

class MainStatusBar(QWidget):
    """主界面底部系统状态栏"""
    
    def __init__(self, robot_data):
        super().__init__()
        self.robot_data = robot_data
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 3, 15, 3)
        layout.setSpacing(10)
        
        # 预置样式（正常/警告/错误）
        self.ok_style = """
            QLabel {
                color: #28a745;
                font-weight: 600;
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 2px 6px;
                min-width: 40px;
            }
        """
        self.warn_style = """
            QLabel {
                color: #fd7e14;
                font-weight: 600;
                background-color: #fff3cd;
                border: 1px solid #ffeeba;
                border-radius: 3px;
                padding: 2px 6px;
                min-width: 40px;
            }
        """
        self.error_style = """
            QLabel {
                color: #dc3545;
                font-weight: 600;
                background-color: #f8d7da;
                border: 1px solid #f5c6cb;
                border-radius: 3px;
                padding: 2px 6px;
                min-width: 40px;
            }
        """
        
        # 设置整体样式
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-top: 1px solid #e9ecef;
                font-size: 10px;
                color: #495057;
                max-height: 30px;
                min-height: 30px;
            }
            QLabel {
                color: #495057;
                font-size: 10px;
                padding: 2px 4px;
                background-color: transparent;
            }
        """)
        
        # 创建状态标签（使用简洁图标+名称）
        self.voltage_label = QLabel("🔋 电压: --")
        self.current_label = QLabel("🔌 电流: --")
        self.power_label = QLabel("⚡ 功耗: --")
        self.comm_label = QLabel("📡 通信: --")
        self.latency_label = QLabel("🕑 延迟: --")
        self.packet_loss_label = QLabel("📉 丢包: --")
        self.leak_label = QLabel("💧 漏水: --")
        self.uptime_label = QLabel("⏱️ 运行: --")
        
        for label in [
            self.voltage_label, self.current_label, self.power_label,
            self.comm_label, self.latency_label, self.packet_loss_label,
            self.leak_label, self.uptime_label
        ]:
            label.setStyleSheet(self.ok_style)
            label.setAlignment(Qt.AlignCenter)
        
        # 提示信息（Tooltips）
        self.voltage_label.setToolTip("系统供电电压（V）：低于阈值将提示警告/错误")
        self.current_label.setToolTip("系统电流（A）")
        self.power_label.setToolTip("系统功耗（W）")
        self.comm_label.setToolTip("通信状态：0=断开，1=正常，2=延迟高，3=不稳定")
        self.latency_label.setToolTip("通信延迟（ms）：>100ms 警告，>300ms 错误")
        self.packet_loss_label.setToolTip("丢包率（%）：>1% 警告，>5% 错误")
        self.leak_label.setToolTip("漏水检测：检测到漏水将高亮提示")
        self.uptime_label.setToolTip("系统持续运行时长")
        
        # 分隔符样式
        sep_style = "color: #adb5bd; padding: 0 2px; background: transparent;"
        def sep():
            s = QLabel("   |   ")
            s.setStyleSheet(sep_style)
            return s
        
        # 添加到布局（分组：电气 | 通信 | 安全 · 运行）
        layout.addWidget(self.voltage_label)
        layout.addWidget(self.current_label)
        layout.addWidget(self.power_label)
        layout.addWidget(sep())
        layout.addWidget(self.comm_label)
        layout.addWidget(self.latency_label)
        layout.addWidget(self.packet_loss_label)
        layout.addWidget(sep())
        layout.addWidget(self.leak_label)
        layout.addWidget(self.uptime_label)
        layout.addStretch()  # 添加弹性空间
        
        # 键盘控制说明
        layout.addWidget(sep())
        keyboard_help_label = QLabel("键盘控制: WASD移动 QE升降 JL转向 空格急停 鼠标悬停查看详细信息")
        keyboard_help_label.setStyleSheet("""
            QLabel {
                color: #495057;
                font-size: 9px;
                background-color: transparent;
                border: none;
                padding: 0 4px;
            }
        """)
        keyboard_help_label.setToolTip("""
浮游模式: W前进 S后退 A左移 D右移 Q上升 E下降
          J左转 L右转 I抬头 K低头 U左滚 O右滚
轮式模式: ↑前进 ↓后退 ←左转 →右转
紧急操作: 空格键急停
注意: 需要点击界面获得焦点""")
        layout.addWidget(keyboard_help_label)
        
        # 版本信息置于最右侧
        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 9px;
                font-style: italic;
                background-color: transparent;
                border: none;
            }
        """)
        layout.addWidget(version_label)
    
    def _set_status_style(self, label: QLabel, level: str):
        """根据等级应用样式: normal/warning/error"""
        if level == "error":
            label.setStyleSheet(self.error_style)
        elif level == "warning":
            label.setStyleSheet(self.warn_style)
        else:
            label.setStyleSheet(self.ok_style)
    
    def _format_uptime(self, seconds: int) -> str:
        """将秒格式化为人性化字符串，如 1h 3m 5s"""
        try:
            s = int(max(0, seconds))
        except Exception:
            s = 0
        d, rem = divmod(s, 86400)
        h, rem = divmod(rem, 3600)
        m, s = divmod(rem, 60)
        parts = []
        if d: parts.append(f"{d}d")
        if h: parts.append(f"{h}h")
        if m: parts.append(f"{m}m")
        if not parts:  # 小于1分钟
            parts.append(f"{s}s")
        return " ".join(parts)
    
    def update_display(self):
        """更新显示数据"""
        try:
            state_data = self.robot_data.get_state_data()
            system_state = state_data.state_system
            
            # 数值
            voltage = float(getattr(system_state, 'sta_system_voltage', 0.0))
            current = float(getattr(system_state, 'sta_system_current', 0.0))
            power = float(getattr(system_state, 'sta_system_power', 0.0))
            comm_status_code = int(getattr(system_state, 'sta_comm_status', 0))
            # sta_send_time是发送时间戳(Unix纪元毫秒数)，需要计算实际延迟
            send_time = int(getattr(system_state, 'sta_send_time', 0))
            if send_time > 0:
                current_time = int(time.time() * 1000)  # 当前时间戳(ms)
                latency = current_time - send_time  # 计算延迟
                # print(f"send_time: {send_time}, current_time: {current_time}, latency: {latency}")
                # 防止负值或异常大值
                if latency < 0 or latency > 500:  # 超过0.5秒认为异常
                    latency = -1
            else:
                latency = -1  # 无效数据
            packet_loss = int(getattr(system_state, 'sta_packet_loss', 0))
            leak = int(getattr(system_state, 'sta_leak_detected', 0))
            uptime = int(getattr(system_state, 'sta_uptime', 0))
            
            # 电气显示及阈值着色（假设48V系统）
            self.voltage_label.setText(f"🔋 电压: {voltage:.1f}V")
            # 阈值：>=44 正常，42-44 警告，<42 错误
            if voltage < 42.0:
                self._set_status_style(self.voltage_label, "error")
            elif voltage < 44.0:
                self._set_status_style(self.voltage_label, "warning")
            else:
                self._set_status_style(self.voltage_label, "normal")
            
            self.current_label.setText(f"🔌 电流: {current:.1f}A")
            self._set_status_style(self.current_label, "normal")
            
            self.power_label.setText(f"⚡ 功耗: {power:.1f}W")
            self._set_status_style(self.power_label, "normal")
            
            # 通信状态映射
            comm_map = {0: "断开", 1: "正常", 2: "延迟高", 3: "不稳定"}
            comm_text = comm_map.get(comm_status_code, "未知")
            self.comm_label.setText(f"📡 通信: {comm_text}")
            if comm_status_code == 0:
                self._set_status_style(self.comm_label, "error")
            elif comm_status_code in (2, 3):
                self._set_status_style(self.comm_label, "warning")
            else:
                self._set_status_style(self.comm_label, "normal")
            
            # 延迟与丢包阈值着色
            if latency == -1:
                self.latency_label.setText("🕑 延迟: 无效")
                self._set_status_style(self.latency_label, "error")
            else:
                self.latency_label.setText(f"🕑 延迟: {latency}ms")
                if latency > 300:
                    self._set_status_style(self.latency_label, "error")
                elif latency > 100:
                    self._set_status_style(self.latency_label, "warning")
                else:
                    self._set_status_style(self.latency_label, "normal")
            
            if packet_loss == -1:
                self.packet_loss_label.setText("📉 丢包: 无效")
                self._set_status_style(self.packet_loss_label, "error")
            else:
                self.packet_loss_label.setText(f"📉 丢包: {packet_loss}%")
                if packet_loss > 5:
                    self._set_status_style(self.packet_loss_label, "error")
                elif packet_loss > 1:
                    self._set_status_style(self.packet_loss_label, "warning")
                else:
                    self._set_status_style(self.packet_loss_label, "normal")
            
            # 漏水检测
            if leak == -1:
                self.leak_label.setText("💧 漏水: 无效")
                self._set_status_style(self.leak_label, "error")
            elif leak:
                self.leak_label.setText("💧 漏水: 检测到漏水")
                self._set_status_style(self.leak_label, "error")
            else:
                self.leak_label.setText("💧 漏水: 正常")
                self._set_status_style(self.leak_label, "normal")
            
            # 运行时间（人性化显示）
            if uptime == -1:
                self.uptime_label.setText("⏱️ 运行: 无效")
                self._set_status_style(self.uptime_label, "error")
            else:
                self.uptime_label.setText(f"⏱️ 运行: {self._format_uptime(uptime)}")
                self._set_status_style(self.uptime_label, "normal")
            
        except Exception as e:
            print(f"状态栏更新错误: {e}")