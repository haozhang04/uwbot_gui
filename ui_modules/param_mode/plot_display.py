import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QCheckBox, QFrame, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from collections import defaultdict, deque
import numpy as np

# 设置matplotlib中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
# sudo apt-get install fonts-wqy-microhei fonts-noto-cjk

class PlotWidget(QWidget):
    def __init__(self, robot_data=None):
        super().__init__()
        self.robot_data = robot_data
        self.init_ui()
        self.init_data()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # 控制面板
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel)
        
        # 创建matplotlib图形
        self.figure = Figure(figsize=(12, 10))
        self.figure.patch.set_facecolor('#f8f9fa')
        
        # 创建4个子图，竖直排列
        self.axes = []
        for i in range(4):
            ax = self.figure.add_subplot(4, 1, i+1)
            ax.set_facecolor('#ffffff')
            ax.grid(True, alpha=0.3)
            ax.tick_params(colors='#495057')
            self.axes.append(ax)
        
        # 调整子图间距
        self.figure.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.1, hspace=0.4)
        
        # 创建画布
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # 设置样式
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
            }
        """)
        
    def create_control_panel(self):
        """创建控制面板"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        panel.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(8)
        
        # 标题
        title = QLabel("📈 多参数实时绘图")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet("color: #495057; margin-bottom: 5px;")
        layout.addWidget(title)
        
        # 控制按钮区域
        button_layout = QHBoxLayout()
        
        # 时间窗口选择
        time_label = QLabel("时间窗口:")
        time_label.setStyleSheet("color: #495057; font-weight: bold;")
        button_layout.addWidget(time_label)
        
        self.time_combo = QComboBox()
        self.time_combo.addItems(["最近10秒", "最近30秒", "最近1分钟", "最近5分钟", "全部数据"])
        self.time_combo.setCurrentText("最近30秒")
        self.time_combo.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 4px 8px;
                min-width: 100px;
            }
        """)
        button_layout.addWidget(self.time_combo)
        
        button_layout.addStretch()
        
        # 自动更新复选框
        self.auto_update_cb = QCheckBox("自动更新")
        self.auto_update_cb.setChecked(True)
        self.auto_update_cb.setStyleSheet("""
            QCheckBox {
                color: #495057;
                font-weight: bold;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
        """)
        button_layout.addWidget(self.auto_update_cb)
        
        # 保存按钮
        self.save_btn = QPushButton("💾 保存图表")
        self.save_btn.clicked.connect(self.save_plots)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        button_layout.addWidget(self.save_btn)
        
        # 清除数据按钮
        clear_btn = QPushButton("🗑️ 清除数据")
        clear_btn.clicked.connect(self.clear_data)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        
        return panel
    
    def init_data(self):
        """初始化数据结构"""
        self.parameter_data = defaultdict(lambda: {'times': deque(maxlen=1000), 'values': deque(maxlen=1000)})
        self.plot_assignments = [None, None, None, None]  # 4个图表当前显示的参数
        
        # 设置更新定时器
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_plot)
        # 使用统一的uptime参数，如果没有robot_data则使用默认值20ms
        uptime = self.robot_data.app_dt if self.robot_data else 50
        self.update_timer.start(uptime)  # 使用统一的uptime参数，20ms更新一次
        

    
    def update_data(self, param_name, value):
        """更新参数数据"""
        if isinstance(value, (int, float)):
            current_time = datetime.now()
            self.parameter_data[param_name]['times'].append(current_time)
            self.parameter_data[param_name]['values'].append(float(value))
    
    def set_plot_parameter(self, plot_index, param_name):
        """设置指定图表显示的参数"""
        if 0 <= plot_index < 4:
            if param_name == "-- 不显示 --" or param_name is None:
                self.plot_assignments[plot_index] = None
            else:
                self.plot_assignments[plot_index] = param_name
            self.update_plot()
    
    def get_time_window_seconds(self):
        """获取时间窗口秒数"""
        time_text = self.time_combo.currentText()
        if "10秒" in time_text:
            return 10
        elif "30秒" in time_text:
            return 30
        elif "1分钟" in time_text:
            return 60
        elif "5分钟" in time_text:
            return 300
        else:
            return None  # 全部数据
    
    def update_plot(self):
        """更新绘图"""
        if not self.auto_update_cb.isChecked():
            return
            
        try:
            current_time = datetime.now()
            time_window = self.get_time_window_seconds()
            
            # 清除所有子图
            for ax in self.axes:
                ax.clear()
                ax.set_facecolor('#ffffff')
                ax.grid(True, alpha=0.3)
                ax.tick_params(colors='#495057')
            
            # 为每个子图绘制对应的参数
            colors = ['#007bff', '#28a745', '#ffc107', '#dc3545']
            
            for i, param_name in enumerate(self.plot_assignments):
                if param_name and param_name in self.parameter_data:
                    data = self.parameter_data[param_name]
                    
                    if len(data['times']) > 0:
                        times = list(data['times'])
                        values = list(data['values'])
                        
                        # 时间窗口过滤
                        if time_window:
                            cutoff_time = current_time.timestamp() - time_window
                            filtered_data = [(t, v) for t, v in zip(times, values) 
                                           if t.timestamp() >= cutoff_time]
                            if filtered_data:
                                times, values = zip(*filtered_data)
                            else:
                                times, values = [], []
                        
                        if times and values:
                            # 绘制数据
                            self.axes[i].plot(times, values, color=colors[i], linewidth=2, alpha=0.8)
                            
                            # 设置标题和标签
                            self.axes[i].set_title(f"图表 {i+1}: {param_name}", 
                                                  fontsize=10, fontweight='bold', color='#495057')
                            self.axes[i].set_ylabel('数值', color='#495057')
                            
                            # 格式化时间轴
                            if len(times) > 1:
                                self.axes[i].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
                                self.axes[i].xaxis.set_major_locator(mdates.SecondLocator(interval=max(1, len(times)//5)))
                            
                            # 设置y轴范围
                            if len(values) > 1:
                                y_min, y_max = min(values), max(values)
                                y_range = y_max - y_min
                                if y_range > 0:
                                    self.axes[i].set_ylim(y_min - y_range*0.1, y_max + y_range*0.1)
                else:
                    # 显示空图表提示
                    self.axes[i].text(0.5, 0.5, f"图表 {i+1}\n请选择参数", 
                                    transform=self.axes[i].transAxes, 
                                    ha='center', va='center', 
                                    fontsize=12, color='#6c757d')
                    self.axes[i].set_title(f"图表 {i+1}: 未选择参数", 
                                          fontsize=10, fontweight='bold', color='#6c757d')
            
            # 同步时间轴（如果有多个图表有数据）
            active_axes = [ax for i, ax in enumerate(self.axes) 
                          if self.plot_assignments[i] and 
                          self.plot_assignments[i] in self.parameter_data and 
                          len(self.parameter_data[self.plot_assignments[i]]['times']) > 0]
            
            if len(active_axes) > 1:
                # 获取所有时间范围
                all_times = []
                for i, param_name in enumerate(self.plot_assignments):
                    if param_name and param_name in self.parameter_data:
                        times = list(self.parameter_data[param_name]['times'])
                        if time_window:
                            cutoff_time = current_time.timestamp() - time_window
                            times = [t for t in times if t.timestamp() >= cutoff_time]
                        all_times.extend(times)
                
                if all_times:
                    min_time, max_time = min(all_times), max(all_times)
                    for ax in active_axes:
                        ax.set_xlim(min_time, max_time)
            
            # 只在最后一个子图显示x轴标签
            for i, ax in enumerate(self.axes):
                if i < 3:
                    ax.set_xticklabels([])
                else:
                    ax.set_xlabel('时间', color='#495057')
            
            self.canvas.draw()
            
        except Exception as e:
            print(f"绘图更新失败: {e}")
    
    def save_plots(self):
        """保存图表到文件"""
        try:
            # 检查是否有选择的参数
            active_params = [param for param in self.plot_assignments if param]
            if not active_params:
                QMessageBox.warning(self, "警告", "请先选择要绘制的参数！")
                return
            
            # 创建保存目录
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 让用户选择保存目录
            save_dir = QFileDialog.getExistingDirectory(self, "选择保存目录")
            if not save_dir:
                return
            
            # 为每个参数创建子目录并保存
            saved_files = []
            for i, param_name in enumerate(self.plot_assignments):
                if param_name:
                    # 创建参数目录
                    param_dir = os.path.join(save_dir, f"{param_name}_{timestamp}")
                    os.makedirs(param_dir, exist_ok=True)
                    
                    # 保存单个图表
                    fig_single = Figure(figsize=(10, 6))
                    ax_single = fig_single.add_subplot(1, 1, 1)
                    
                    if param_name in self.parameter_data:
                        data = self.parameter_data[param_name]
                        if len(data['times']) > 0:
                            times = list(data['times'])
                            values = list(data['values'])
                            
                            ax_single.plot(times, values, color='#007bff', linewidth=2)
                            ax_single.set_title(f"{param_name}", fontsize=14, fontweight='bold')
                            ax_single.set_xlabel('时间')
                            ax_single.set_ylabel('数值')
                            ax_single.grid(True, alpha=0.3)
                            
                            # 格式化时间轴
                            ax_single.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
                    
                    # 保存图片
                    img_path = os.path.join(param_dir, f"{param_name}_{timestamp}.png")
                    fig_single.savefig(img_path, dpi=300, bbox_inches='tight')
                    
                    # 保存数据
                    if param_name in self.parameter_data:
                        data = self.parameter_data[param_name]
                        if len(data['times']) > 0:
                            data_path = os.path.join(param_dir, f"{param_name}_{timestamp}.txt")
                            with open(data_path, 'w', encoding='utf-8') as f:
                                f.write(f"# {param_name} 数据\n")
                                f.write("# 时间\t数值\n")
                                for t, v in zip(data['times'], data['values']):
                                    f.write(f"{t.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\t{v}\n")
                    
                    saved_files.append(param_dir)
            
            # 保存完整的4图组合
            if len(active_params) > 1:
                combined_path = os.path.join(save_dir, f"combined_plots_{timestamp}.png")
                self.figure.savefig(combined_path, dpi=300, bbox_inches='tight')
                saved_files.append(combined_path)
            
            QMessageBox.information(self, "保存成功", 
                                  f"图表已保存到:\n" + "\n".join(saved_files))
            
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"保存图表时出错: {str(e)}")
    
    def clear_data(self):
        """清除所有数据"""
        self.parameter_data.clear()
        for ax in self.axes:
            ax.clear()
            ax.set_facecolor('#ffffff')
            ax.grid(True, alpha=0.3)
        self.canvas.draw()

class PlotDisplayWidget(QWidget):
    def __init__(self, robot_data=None):
        super().__init__()
        self.robot_data = robot_data
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # 绘图组件
        self.plot_widget = PlotWidget(self.robot_data)
        layout.addWidget(self.plot_widget)
    
    def update_display(self):
        """更新显示数据"""
        if not self.robot_data:
            return
            
        try:
            # 更新状态数据
            state_data = self.robot_data.get_state_data()
            self.update_group_parameters("机器人状态", state_data.state_robot)
            self.update_group_parameters("浮游模式状态", state_data.state_floating_mode)
            self.update_group_parameters("轮式模式状态", state_data.state_wheel_mode)
            self.update_group_parameters("电磁铁状态", state_data.state_electromagnet)
            self.update_group_parameters("清洗功能状态", state_data.state_brush)
            self.update_group_parameters("系统状态", state_data.state_system)
            
            # 更新命令数据
            cmd_data = self.robot_data.get_cmd_data()
            self.update_group_parameters("浮游模式控制", cmd_data.cmd_floating_mode)
            self.update_group_parameters("轮式模式控制", cmd_data.cmd_wheel_mode)
            self.update_group_parameters("清洗功能控制", cmd_data.cmd_brush)
            self.update_group_parameters("相机控制", cmd_data.cmd_camera)
            
        except Exception as e:
            print(f"更新绘图数据失败: {e}")
            
    def update_group_parameters(self, group_name, group_data):
        """更新组参数"""
        for attr_name in dir(group_data):
            if not attr_name.startswith('_'):
                try:
                    value = getattr(group_data, attr_name)
                    if not callable(value):
                        # 获取参数信息
                        display_name, _, _ = self.get_parameter_info(attr_name)
                        full_param_name = f"{group_name} - {display_name}"
                        
                        # 参数已通过data_display.py的下拉框进行选择
                        
                        # 更新绘图数据
                        if isinstance(value, (int, float)):
                            self.plot_widget.update_data(full_param_name, value)
                        elif isinstance(value, list) and len(value) > 0:
                            # 处理列表类型的参数（如推进器功率、温度等）
                            for idx, item in enumerate(value):
                                if isinstance(item, (int, float)):
                                    indexed_name = f"{full_param_name}[{idx}]"
                                    self.plot_widget.update_data(indexed_name, item)
                            
                except Exception as e:
                    continue
                    
    def get_parameter_info(self, attr_name):
        """获取参数的中文名称、单位和描述"""
        # 参数信息映射表
        param_info = {
            # 机器人状态
            'sta_position_x': ('X坐标', 'm', '机器人在X轴方向的位置'),
            'sta_position_y': ('Y坐标', 'm', '机器人在Y轴方向的位置'),
            'sta_position_z': ('Z坐标/深度', 'm', '机器人在Z轴方向的位置或深度'),
            'sta_roll': ('横滚角', 'rad', '机器人绕X轴的旋转角度'),
            'sta_pitch': ('俯仰角', 'rad', '机器人绕Y轴的旋转角度'),
            'sta_yaw': ('偏航角', 'rad', '机器人绕Z轴的旋转角度'),
            
            # 浮游模式状态
            'sta_floating_vel_x': ('X方向线速度', 'm/s', '浮游模式下X方向的线速度'),
            'sta_floating_vel_y': ('Y方向线速度', 'm/s', '浮游模式下Y方向的线速度'),
            'sta_floating_vel_z': ('Z方向线速度', 'm/s', '浮游模式下Z方向的线速度'),
            'sta_floating_angular_x': ('X轴角速度', 'rad/s', '浮游模式下绕X轴的角速度'),
            'sta_floating_angular_y': ('Y轴角速度', 'rad/s', '浮游模式下绕Y轴的角速度'),
            'sta_floating_angular_z': ('Z轴角速度', 'rad/s', '浮游模式下绕Z轴的角速度'),
            'sta_thruster_power': ('推进器功率', '%', '4个推进器的功率百分比'),
            'sta_thruster_temp': ('推进器温度', '°C', '4个推进器的温度'),
            
            # 轮式模式状态
            'sta_wheel_linear_vel': ('轮式线速度', 'm/s', '轮式模式下的线速度'),
            'sta_wheel_angular_vel': ('轮式角速度', 'rad/s', '轮式模式下的角速度'),
            'sta_motor_data': ('电机数据', '-', '3个电机的数据（舵机角度、电机速度）'),
            'sta_motor_temp': ('电机温度', '°C', '3个电机的温度'),
            
            # 电磁铁状态
            'sta_electromagnet_enable': ('电磁铁状态', '-', '电磁铁开关状态'),
            'sta_electromagnet_voltage': ('电磁铁电压', '%', '电磁铁电压百分比'),
            
            # 清洗功能状态
            'sta_brush_power': ('滚刷功率', '%', '滚刷功率百分比'),
            'sta_brush_enable': ('滚刷状态', '-', '滚刷开关状态'),
            'sta_vacuum_power': ('吸尘功率', '%', '吸尘器功率百分比'),
            'sta_vacuum_enable': ('吸尘状态', '-', '吸尘器开关状态'),
            
            # 系统状态
            'sta_battery_voltage': ('电池电压', 'V', '系统电池电压'),
            'sta_battery_current': ('电池电流', 'A', '系统电池电流'),
            'sta_battery_percentage': ('电池电量', '%', '电池剩余电量百分比'),
            'sta_system_temp': ('系统温度', '°C', '系统内部温度'),
            'sta_water_temp': ('水温', '°C', '环境水温'),
            'sta_depth': ('深度', 'm', '当前深度'),
            'sta_pressure': ('压力', 'Pa', '环境压力'),
            
            # 浮游模式控制
            'cmd_floating_vel_x': ('X方向线速度控制', 'm/s', '浮游模式X方向线速度控制'),
            'cmd_floating_vel_y': ('Y方向线速度控制', 'm/s', '浮游模式Y方向线速度控制'),
            'cmd_floating_vel_z': ('Z方向线速度控制', 'm/s', '浮游模式Z方向线速度控制'),
            'cmd_floating_angular_x': ('X轴角速度控制', 'rad/s', '浮游模式X轴角速度控制'),
            'cmd_floating_angular_y': ('Y轴角速度控制', 'rad/s', '浮游模式Y轴角速度控制'),
            'cmd_floating_angular_z': ('Z轴角速度控制', 'rad/s', '浮游模式Z轴角速度控制'),
            
            # 轮式模式控制
            'cmd_wheel_linear_vel': ('轮式线速度控制', 'm/s', '轮式模式线速度控制'),
            'cmd_wheel_angular_vel': ('轮式角速度控制', 'rad/s', '轮式模式角速度控制'),
            
            # 清洗功能控制
            'cmd_brush_power': ('滚刷功率控制', '%', '滚刷功率控制'),
            'cmd_brush_enable': ('滚刷开关控制', '-', '滚刷开关控制'),
            'cmd_vacuum_power': ('吸尘功率控制', '%', '吸尘器功率控制'),
            'cmd_vacuum_enable': ('吸尘开关控制', '-', '吸尘器开关控制'),
            
            # 相机控制
            'cmd_camera_enable': ('相机开关控制', '-', '相机开关控制'),
        }
        
        return param_info.get(attr_name, (attr_name, '-', '未知参数'))