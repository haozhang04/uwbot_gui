#ifndef LOWLEVEL_STATE_H
#define LOWLEVEL_STATE_H

#include <stdint.h>

/**
 * @brief 机器人状态结构体
 * 包含机器人的所有状态和传感器数据
 */
typedef struct {
    /* 位置和姿态 */
    float position_x;          // X坐标 (m)
    float position_y;          // Y坐标 (m)
    float position_z;          // Z坐标/深度 (m)
    float roll;                // 横滚角 (rad)
    float pitch;               // 俯仰角 (rad)
    float yaw;                 // 航向角 (rad)
    
    /* 速度 如果是车模式的话，只有velocity_x和angular_vel_x*/
    float velocity_x;          // X方向速度 (m/s)
    float velocity_y;          // Y方向速度 (m/s)
    float velocity_z;          // Z方向速度 (m/s)
    float angular_vel_x;       // X轴角速度 (rad/s)
    float angular_vel_y;       // Y轴角速度 (rad/s)
    float angular_vel_z;       // Z轴角速度 (rad/s)
    
    /* 环境传感器数据 */
    float depth;   // 深度 (m)
    float temperature_inside;  // 内部温度 (°C)
    float humidity_inside;     // 内部湿度 (%)
    float pressure_water;      // 水压 (kPa)
    float pressure_inside;     // 内部气压 (kPa)
    
    /* 电气系统状态 */
    float voltage_main;        // 主电池电压 (V)
    float current_main;        // 主电池电流 (A)
    float power_consumption;   // 功耗 (W)
    
    /* 4推进器状态 */
    float thruster_power[4];    // 4个推进器功率百分比 (0-100%)
    float thruster_temp[4];     // 4个推进器温度 (°C)

    /* 3电机状态 */
    float motor_data[3];   // 3个电机数据: 0-舵机角度 (°), 1-1号电机速度 (m/s), 2-1号电机速度(m/s)
    float motor_temp[3];       // 3个电机温度 (°C)
    
    /* 电磁铁状态 */
    uint8_t electromagnet_status;     // 电磁铁状态: 0-关闭, 1-开启
    float electromagnet_voltage;      // 电磁铁电压 (V)
    
    /* 清洗系统状态 */
    uint8_t water_pump_status; // 水泵状态: 0-关闭, 1-正常, 2-警告, 3-错误
    float water_flow_rate;     // 水流速率 (L/min)
    
    /* 相机系统状态 */
    uint8_t camera_status[2];  // 2个相机状态: 0-关闭, 1-正常, 2-警告, 3-错误
    uint8_t recording_status[2];  // 录制状态: 0-未录制, 1-录制中
    char storage_path[2][128];    // 储存路径
    char camera_path[2][128];     // 储存名称
    uint32_t storage_used;     // 已用存储空间 (MB)
    uint32_t storage_total;    // 总存储空间 (MB)
    
    /* 通信状态 */
    uint8_t comm_status;       // 通信状态: 0-断开, 1-正常, 2-延迟高, 3-不稳定
    uint16_t comm_latency;     // 通信延迟 (ms)
    uint32_t packet_loss;      // 丢包计数
    int8_t signal_strength;    // 信号强度 (dBm)
    
    /* 控制系统状态 */
    uint8_t control_mode;      // 当前控制模式: 0-浮游, 1-爬行, 2-清洗
    uint8_t auto_mode_status;  // 自动模式状态: 0-手动, 1-定深, 2-定向, 3-定深+定向

    /* 系统诊断 */
    uint8_t leak_detected;     // 漏水检测: 0-正常, 1-检测到漏水
    uint8_t system_warnings;   // 系统警告计数
    uint8_t system_errors;     // 系统错误计数
    uint32_t uptime;           // 系统运行时间 (s)
    
} LowlevelState;

#endif // LOWLEVEL_STATE_H