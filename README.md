# 水下机器人GUI控制系统 (UWBot GUI)

一个基于PyQt5开发的水下机器人控制界面系统，提供实时监控、运动控制、摄像头管理和数据可视化功能。

## 功能特性

- 🎮 **运动控制**: 实时控制水下机器人的运动状态
- 📹 **摄像头管理**: 支持多摄像头实时预览、录制和截图
- 📊 **数据可视化**: 实时显示机器人状态数据和传感器信息
- 📝 **日志系统**: 完整的系统日志记录和查看
- ⚙️ **参数配置**: 灵活的系统参数设置和管理
- 🔄 **实时通信**: 与水下机器人的低延迟数据通信

## 项目结构

```
uwbot_GUI/
├── main.py                 # 主程序入口
├── requirements.txt        # 项目依赖
├── config/                 # 配置文件
│   └── log_config.json
├── ui_modules/            # UI模块
│   ├── control_mode/      # 控制模式界面
│   ├── log_mode/          # 日志查看界面
│   └── param_mode/        # 参数设置界面
├── messages/              # 消息和数据结构
├── camera_data/           # 摄像头数据存储
├── logs/                  # 系统日志
└── resource/              # 资源文件
```

## 环境要求

- Python >= 3.7
- Windows 10/11 (推荐)
- 至少 4GB RAM
- 支持OpenGL的显卡（用于图形渲染）

## 安装说明

### 1. 克隆项目

```bash
git clone https://github.com/haozhang04/uwbot_gui.git
cd uwbot_gui
```

### 2. 创建虚拟环境（推荐）

```bash
# Windows
python -m venv uwbot_env
uwbot_env\Scripts\activate

# Linux/Mac
python -m venv uwbot_env
source uwbot_env/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 运行程序

```bash
python main.py
```

## 使用说明

1. **启动程序**: 运行 `python main.py` 启动GUI界面
2. **连接设备**: 在设置界面配置机器人连接参数
3. **控制操作**: 使用控制面板进行机器人操作
4. **数据监控**: 在状态界面查看实时数据
5. **摄像头**: 在摄像头界面进行视频监控和录制

## 注意事项

- 首次运行前请确保已正确安装所有依赖包
- Windows用户可能需要安装 Visual C++ Build Tools
- 如果 opencv-python 安装失败，可尝试 opencv-python-headless
- 建议在虚拟环境中运行以避免依赖冲突

## 开发说明

### 代码规范
- 使用 Python PEP 8 代码规范
- 所有函数和类都应包含详细的中文注释
- 提交代码前请运行测试确保功能正常

### 贡献指南
1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目维护者: HAO ZHANG
- 项目链接: [https://github.com/haozhang04/uwbot_gui](https://github.com/haozhang04/uwbot_gui)