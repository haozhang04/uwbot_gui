#ifndef LOWLEVEL_CMD_H
#define LOWLEVEL_CMD_H

#include <stdint.h>

/**
 * @brief 机器人控制命令结构体
 * 包含控制机器人运动和功能的所有命令变量
 */
typedef struct {
    /* 运动控制命令 */

    // 工作模式: 0-浮游模式
    uint8_t mode_floating;              
    float floating_linear_vel_x;   // X方向线速度 (m/s)
    float floating_linear_vel_y;   // Y方向线速度 (m/s)
    float floating_linear_vel_z;   // Z方向线速度 (m/s)
    float floating_angular_vel_x;  // X轴角速度 (rad/s)
    float floating_angular_vel_y;  // Y轴角速度 (rad/s)
    float floating_angular_vel_z;  // Z轴角速度 (rad/s)
    /* 深度控制 */
    uint8_t depth_hold;        // 定深功能: 0-关闭, 1-开启
    float target_depth;        // 目标深度 (m)

    // 工作模式: 0-差速车模式
    uint8_t mode_wheel;              
    float wheel_linear_vel;   // 线速度 (m/s)
    float wheel_angular_vel;  // X轴角速度 (rad/s)
    /* 水平运动控制 */
    uint8_t speed_level;       // 水平速度档位: 0-5
    uint8_t direction_hold;    // 定向功能: 0-关闭, 1-开启
    float target_direction;    // 目标方向 (度)
    
    /* 电磁铁 */
    uint8_t electromagnet_enable;     // 电磁铁状态: 0-关闭, 1-开启
    uint8_t electromagnet_voltage;    // 电磁铁电压: 0-100%

    /* 清洗功能控制 */
    uint8_t brush_power;       // 滚刷功率: 0-100%
    uint8_t brush_enable;      // 滚刷开关: 0-关闭, 1-开启
    uint8_t vacuum_power;      // 吸尘功率: 0-100%
    uint8_t vacuum_enable;     // 吸尘开关: 0-关闭, 1-开启
    uint8_t water_flow;        // 水流强度: 0-100%
    uint8_t water_enable;      // 水流开关: 0-关闭, 1-开启
    
    /* 相机控制 */
    uint8_t camera_select;     // 相机选择: 0-前置, 1-后置
    uint8_t camera_zoom;       // 相机缩放: 0-100%
    uint8_t camera_record;     // 录制功能: 0-停止, 1-开始
    uint8_t camera_snapshot;   // 截图功能: 0-无操作, 1-截图
    
    /* 输入源控制 */
    uint8_t control_source;    // 控制源: 0-界面控制, 1-手柄控制
    
    /* 紧急控制 */
    uint8_t emergency_stop;    // 紧急停止: 0-正常, 1-紧急停止
    uint8_t auto_surface;      // 自动上浮: 0-关闭, 1-开启

} LowlevelCmd;

#endif // LOWLEVEL_CMD_H