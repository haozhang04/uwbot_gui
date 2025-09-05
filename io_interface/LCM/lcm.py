import lcm
import threading
import sys
from lcm_type.LowlevelState_t import LowlevelState_t
from lcm_type.LowlevelCmd_t import LowlevelCmd_t

class Custom:
    def __init__(self):
        self.lcm = lcm.LCM("udpm://239.255.76.67:7667?ttl=255")
        if not self.lcm.good():
            sys.stderr.write("Failed to initialize LCM\n")
            return
        
        self.state_mutex = threading.Lock()
        self.cmd_mutex = threading.Lock()

        self.state_simple = LowlevelState_t()
        self.command_simple = LowlevelCmd_t()

        self.data_init()
        print("LCM initialized successfully")
        
        self.receive_thread = threading.Thread(target=self.handle_receive)
        self.receive_thread.daemon = True
        self.receive_thread.start()
        
        self.lcm.subscribe("uwbot_state", self.state_callback)

    def __del__(self):
        if hasattr(self, 'receive_thread') and self.receive_thread.is_alive():
            self.receive_thread.join()

    def state_callback(self, channel, data):
        msg = LowlevelState_t.decode(data)
        with self.state_mutex:
            self.state_simple = msg

    def cmd_callback(self, channel, data):
        msg = LowlevelCmd_t.decode(data)
        with self.cmd_mutex:
            self.command_simple = msg

    def handle_receive(self):
        while True:
            self.lcm.handle()

    def send_data_once(self):
        if not self.lcm.good():
            sys.stderr.write("LCM is not ready\n")
            return
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
        self.command_simple.cmd_brush.cmd_brush_power = 0.0
        self.command_simple.cmd_brush.cmd_water_enable = 0
        self.command_simple.cmd_brush.cmd_water_flow = 0.0
        
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
        self.state_simple.state_robot.position_x = 0.0
        self.state_simple.state_robot.position_y = 0.0
        self.state_simple.state_robot.position_z = 0.0
        self.state_simple.state_robot.roll = 0.0
        self.state_simple.state_robot.pitch = 0.0
        self.state_simple.state_robot.yaw = 0.0

        #初始化浮游模式状态
        self.state_simple.state_floating_mode.vel_x = 0.0
        self.state_simple.state_floating_mode.vel_y = 0.0
        self.state_simple.state_floating_mode.vel_z = 0.0
        self.state_simple.state_floating_mode.angular_x = 0.0
        self.state_simple.state_floating_mode.angular_y = 0.0
        self.state_simple.state_floating_mode.angular_z = 0.0
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
