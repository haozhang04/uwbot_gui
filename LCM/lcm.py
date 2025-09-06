import lcm
import threading
import sys
from .lcm_type.LowlevelState_t import LowlevelState_t
from .lcm_type.LowlevelCmd_t import LowlevelCmd_t

class LCMInterface:
    def __init__(self):
        self.lcm = lcm.LCM("udpm://239.255.76.67:7667?ttl=255")
        
        self.state_mutex = threading.Lock()
        self.cmd_mutex = threading.Lock()

        self.state_simple = LowlevelState_t()
        self.command_simple = LowlevelCmd_t()

        self.data_init()
        print("LCM initialized successfully")
        
        self.lcm_stop_flag = True #开启lcm设置为False，关闭lcm设置为True

        self.receiveData()
        self.send_data_once()


    def __del__(self):
        if hasattr(self, 'receive_thread') and self.receive_thread.is_alive():
            self.receive_thread.join()

    #接收：执行一次，订阅uwbot_state
    def receiveData(self):
        self.lcm.subscribe("uwbot_state", self.state_callback)

    def state_callback(self, channel, data):
        msg = LowlevelState_t.decode(data)
        with self.state_mutex:
            self.state_simple = msg

    # def cmd_callback(self, channel, data):
    #     msg = LowlevelCmd_t.decode(data)
    #     with self.cmd_mutex:
    #         self.command_simple = msg

    #创建一个新线程，调用 lcm 对象的 handle_receive 方法，阻塞
    def handle_receive(self):
        while not self.lcm_stop_flag:
            self.lcm.handle()

    #定时发送send_data_once：100hz，放到ui主线程
    def send_data_once(self):
        with self.cmd_mutex:
            self.lcm.publish("uwbot_command", self.command_simple.encode())


    def data_init(self):
        """LowlevelCmd_t数据初始化"""
        # 初始化浮游模式命令
        self.command_simple.cmd_floating_mode.cmd_floating_vel_x = 0.0
        self.command_simple.cmd_floating_mode.cmd_floating_vel_y = 0.0
        self.command_simple.cmd_floating_mode.cmd_floating_vel_z = 0.0
        self.command_simple.cmd_floating_mode.cmd_floating_angular_roll = 0.0
        self.command_simple.cmd_floating_mode.cmd_floating_angular_yaw = 0.0
        self.command_simple.cmd_floating_mode.cmd_floating_angular_pitch = 0.0
        # 初始化浮游模式命令-定深
        self.command_simple.cmd_floating_mode.cmd_depth_hold = 0
        self.command_simple.cmd_floating_mode.cmd_target_depth = 0.0
        # 初始化浮游模式命令-定航
        self.command_simple.cmd_floating_mode.cmd_floating_heading_hold = 0
        self.command_simple.cmd_floating_mode.cmd_target_roll = 0.0
        self.command_simple.cmd_floating_mode.cmd_target_yaw = 0.0
        self.command_simple.cmd_floating_mode.cmd_target_pitch = 0.0
        
        # 初始化轮式模式命令
        self.command_simple.cmd_wheel_mode.cmd_wheel_linear_vel = 0.0
        self.command_simple.cmd_wheel_mode.cmd_wheel_angular_vel = 0.0
        # 初始化轮式模式命令-定航
        self.command_simple.cmd_wheel_mode.cmd_wheel_heading_hold = 0
        self.command_simple.cmd_wheel_mode.cmd_target_heading = 0.0
        
        # 初始化电磁铁功能
        self.command_simple.cmd_electromagnet.cmd_electromagnet_enable = 0
        self.command_simple.cmd_electromagnet.cmd_electromagnet_voltage = 0

        # 初始化清洗功能
        self.command_simple.cmd_brush.cmd_brush_enable = 0
        self.command_simple.cmd_brush.cmd_brush_power = 0
        self.command_simple.cmd_brush.cmd_water_enable = 0
        self.command_simple.cmd_brush.cmd_water_flow = 0
        
        # 初始化相机控制命令
        self.command_simple.cmd_camera.cmd_camera_enable = [ 0 for dim0 in range(2) ]
        self.command_simple.cmd_camera.cmd_camera_zoom = [ 0 for dim0 in range(2) ]
        self.command_simple.cmd_camera.cmd_camera_record = [ 0 for dim0 in range(2) ]
        self.command_simple.cmd_camera.cmd_camera_record_time = [ 0 for dim0 in range(2) ]
        self.command_simple.cmd_camera.cmd_camera_snapshot = [ 0 for dim0 in range(2) ]
        self.command_simple.cmd_camera.cmd_storage_path = [ "" for dim0 in range(2) ]
        self.command_simple.cmd_camera.cmd_camera_path = [ "" for dim0 in range(2) ]
        
        
        """LowlevelState_t数据初始化"""
        #初始化机器人位姿
        self.state_simple.state_robot.sta_position_x = 0.0
        self.state_simple.state_robot.sta_position_y = 0.0
        self.state_simple.state_robot.sta_position_z = 0.0
        self.state_simple.state_robot.sta_roll = 0.0
        self.state_simple.state_robot.sta_pitch = 0.0
        self.state_simple.state_robot.sta_yaw = 0.0

        #初始化浮游模式状态
        self.state_simple.state_floating_mode.sta_floating_vel_x = 0.0
        self.state_simple.state_floating_mode.sta_floating_vel_y = 0.0
        self.state_simple.state_floating_mode.sta_floating_vel_z = 0.0
        self.state_simple.state_floating_mode.sta_floating_angular_x = 0.0
        self.state_simple.state_floating_mode.sta_floating_angular_y = 0.0
        self.state_simple.state_floating_mode.sta_floating_angular_z = 0.0
        self.state_simple.state_floating_mode.sta_thruster_power = [ 0.0 for dim0 in range(4) ]
        self.state_simple.state_floating_mode.sta_thruster_temp = [ 0.0 for dim0 in range(4) ]

        #初始化轮式模式状态
        self.state_simple.state_wheel_mode.sta_wheel_linear_vel = 0.0
        self.state_simple.state_wheel_mode.sta_wheel_angular_vel = 0.0
        self.state_simple.state_wheel_mode.sta_motor_data = [ 0.0 for dim0 in range(3) ]
        self.state_simple.state_wheel_mode.sta_motor_temp = [ 0.0 for dim0 in range(3) ]

        #初始化电磁铁状态
        self.state_simple.state_electromagnet.sta_electromagnet_enable = 0.0
        self.state_simple.state_electromagnet.sta_electromagnet_voltage = 0.0

        #初始化清洗状态
        self.state_simple.state_brush.sta_brush_enable = 0.0
        self.state_simple.state_brush.sta_brush_power = 0.0
        self.state_simple.state_brush.sta_water_enable = 0.0
        self.state_simple.state_brush.sta_water_flow = 0.0

        #初始化系统状态
        self.state_simple.state_system.sta_system_voltage = 0.0
        self.state_simple.state_system.sta_system_current = 0.0
        self.state_simple.state_system.sta_system_power = 0.0
        self.state_simple.state_system.sta_comm_status = 0
        self.state_simple.state_system.sta_communication_status = 0
        self.state_simple.state_system.sta_comm_latency = 0
        self.state_simple.state_system.sta_packet_loss = 0
        self.state_simple.state_system.sta_leak_detected = 0
        self.state_simple.state_system.sta_uptime = 0

    def _convert_cmd_to_lcm_format(self, ui_cmd):
        """将UI的LowlevelCmd数据类转换为LCM的LowlevelCmd_t格式"""
        lcm_cmd = LowlevelCmd_t()
        
        # 转换浮游模式命令
        lcm_cmd.cmd_floating_mode.cmd_floating_vel_x = ui_cmd.cmd_floating_mode.cmd_floating_vel_x
        lcm_cmd.cmd_floating_mode.cmd_floating_vel_y = ui_cmd.cmd_floating_mode.cmd_floating_vel_y
        lcm_cmd.cmd_floating_mode.cmd_floating_vel_z = ui_cmd.cmd_floating_mode.cmd_floating_vel_z
        lcm_cmd.cmd_floating_mode.cmd_floating_angular_roll = ui_cmd.cmd_floating_mode.cmd_floating_angular_roll
        lcm_cmd.cmd_floating_mode.cmd_floating_angular_yaw = ui_cmd.cmd_floating_mode.cmd_floating_angular_yaw
        lcm_cmd.cmd_floating_mode.cmd_floating_angular_pitch = ui_cmd.cmd_floating_mode.cmd_floating_angular_pitch
        lcm_cmd.cmd_floating_mode.cmd_depth_hold = ui_cmd.cmd_floating_mode.cmd_depth_hold
        lcm_cmd.cmd_floating_mode.cmd_target_depth = ui_cmd.cmd_floating_mode.cmd_target_depth
        lcm_cmd.cmd_floating_mode.cmd_floating_heading_hold = ui_cmd.cmd_floating_mode.cmd_floating_heading_hold
        lcm_cmd.cmd_floating_mode.cmd_target_roll = ui_cmd.cmd_floating_mode.cmd_target_roll
        lcm_cmd.cmd_floating_mode.cmd_target_yaw = ui_cmd.cmd_floating_mode.cmd_target_yaw
        lcm_cmd.cmd_floating_mode.cmd_target_pitch = ui_cmd.cmd_floating_mode.cmd_target_pitch
        
        # 转换轮式模式命令
        lcm_cmd.cmd_wheel_mode.cmd_wheel_linear_vel = ui_cmd.cmd_wheel_mode.cmd_wheel_linear_vel
        lcm_cmd.cmd_wheel_mode.cmd_wheel_angular_vel = ui_cmd.cmd_wheel_mode.cmd_wheel_angular_vel
        lcm_cmd.cmd_wheel_mode.cmd_wheel_heading_hold = ui_cmd.cmd_wheel_mode.cmd_wheel_heading_hold
        lcm_cmd.cmd_wheel_mode.cmd_target_heading = ui_cmd.cmd_wheel_mode.cmd_target_heading
        
        # 转换电磁铁命令
        lcm_cmd.cmd_electromagnet.cmd_electromagnet_enable = ui_cmd.cmd_electromagnet.cmd_electromagnet_enable
        lcm_cmd.cmd_electromagnet.cmd_electromagnet_voltage = ui_cmd.cmd_electromagnet.cmd_electromagnet_voltage
        
        # 转换清洗命令
        lcm_cmd.cmd_brush.cmd_brush_enable = ui_cmd.cmd_brush.cmd_brush_enable
        lcm_cmd.cmd_brush.cmd_brush_power = ui_cmd.cmd_brush.cmd_brush_power
        lcm_cmd.cmd_brush.cmd_water_enable = ui_cmd.cmd_brush.cmd_water_enable
        lcm_cmd.cmd_brush.cmd_water_flow = ui_cmd.cmd_brush.cmd_water_flow
        
        # 转换相机命令
        lcm_cmd.cmd_camera.cmd_camera_enable = ui_cmd.cmd_camera.cmd_camera_enable
        lcm_cmd.cmd_camera.cmd_camera_zoom = ui_cmd.cmd_camera.cmd_camera_zoom
        lcm_cmd.cmd_camera.cmd_camera_record = ui_cmd.cmd_camera.cmd_camera_record
        lcm_cmd.cmd_camera.cmd_camera_record_time = ui_cmd.cmd_camera.cmd_camera_record_time
        lcm_cmd.cmd_camera.cmd_camera_snapshot = ui_cmd.cmd_camera.cmd_camera_snapshot
        lcm_cmd.cmd_camera.cmd_storage_path = ui_cmd.cmd_camera.cmd_storage_path
        lcm_cmd.cmd_camera.cmd_camera_path = ui_cmd.cmd_camera.cmd_camera_path
        
        return lcm_cmd

    def _convert_state_to_ui_format(self, lcm_state):
        """将LCM的LowlevelState_t格式转换为UI的LowlevelState dataclass格式"""
        from messages.LowlevelState import LowlevelState, state_robot, state_floating_mode, state_wheel_mode, state_electromagnet, state_brush, state_system
        
        ui_state = LowlevelState()
        
        # 转换机器人位姿状态
        ui_state.state_robot.sta_position_x = lcm_state.state_robot.sta_position_x
        ui_state.state_robot.sta_position_y = lcm_state.state_robot.sta_position_y
        ui_state.state_robot.sta_position_z = lcm_state.state_robot.sta_position_z
        ui_state.state_robot.sta_roll = lcm_state.state_robot.sta_roll
        ui_state.state_robot.sta_pitch = lcm_state.state_robot.sta_pitch
        ui_state.state_robot.sta_yaw = lcm_state.state_robot.sta_yaw
        
        # 转换浮游模式状态
        ui_state.state_floating_mode.sta_floating_vel_x = lcm_state.state_floating_mode.sta_floating_vel_x
        ui_state.state_floating_mode.sta_floating_vel_y = lcm_state.state_floating_mode.sta_floating_vel_y
        ui_state.state_floating_mode.sta_floating_vel_z = lcm_state.state_floating_mode.sta_floating_vel_z
        ui_state.state_floating_mode.sta_floating_angular_x = lcm_state.state_floating_mode.sta_floating_angular_x
        ui_state.state_floating_mode.sta_floating_angular_y = lcm_state.state_floating_mode.sta_floating_angular_y
        ui_state.state_floating_mode.sta_floating_angular_z = lcm_state.state_floating_mode.sta_floating_angular_z
        # 确保推进器数据是列表而不是元组
        ui_state.state_floating_mode.sta_thruster_power = list(lcm_state.state_floating_mode.sta_thruster_power)
        ui_state.state_floating_mode.sta_thruster_temp = list(lcm_state.state_floating_mode.sta_thruster_temp)
        
        # 转换轮式模式状态
        ui_state.state_wheel_mode.sta_wheel_linear_vel = lcm_state.state_wheel_mode.sta_wheel_linear_vel
        ui_state.state_wheel_mode.sta_wheel_angular_vel = lcm_state.state_wheel_mode.sta_wheel_angular_vel
        # 确保电机数据是列表而不是元组
        ui_state.state_wheel_mode.sta_motor_data = list(lcm_state.state_wheel_mode.sta_motor_data)
        ui_state.state_wheel_mode.sta_motor_temp = list(lcm_state.state_wheel_mode.sta_motor_temp)
        
        # 转换电磁铁状态
        ui_state.state_electromagnet.sta_electromagnet_enable = int(lcm_state.state_electromagnet.sta_electromagnet_enable)
        ui_state.state_electromagnet.sta_electromagnet_voltage = int(lcm_state.state_electromagnet.sta_electromagnet_voltage)
        
        # 转换清洗状态
        ui_state.state_brush.sta_brush_enable = int(lcm_state.state_brush.sta_brush_enable)
        ui_state.state_brush.sta_brush_power = int(lcm_state.state_brush.sta_brush_power)
        ui_state.state_brush.sta_water_enable = int(lcm_state.state_brush.sta_water_enable)
        ui_state.state_brush.sta_water_flow = int(lcm_state.state_brush.sta_water_flow)
        
        # 转换系统状态
        ui_state.state_system.sta_system_voltage = lcm_state.state_system.sta_system_voltage
        ui_state.state_system.sta_system_current = lcm_state.state_system.sta_system_current
        ui_state.state_system.sta_system_power = lcm_state.state_system.sta_system_power
        ui_state.state_system.sta_comm_status = lcm_state.state_system.sta_comm_status
        ui_state.state_system.sta_communication_status = lcm_state.state_system.sta_communication_status
        ui_state.state_system.sta_comm_latency = lcm_state.state_system.sta_comm_latency
        ui_state.state_system.sta_packet_loss = lcm_state.state_system.sta_packet_loss
        ui_state.state_system.sta_leak_detected = lcm_state.state_system.sta_leak_detected
        ui_state.state_system.sta_uptime = lcm_state.state_system.sta_uptime
        
        return ui_state