# 水下机器人GUI控制系统

## 项目简介

这是一个基于PyQt5开发的水下机器人控制系统界面，采用模块化设计，支持机器人状态监控、运动控制、相机管理、参数显示和系统设置等功能。

## 功能特性

### 🎮 控制界面
- **机器人状态显示**：实时显示位置、姿态、速度、推进器状态等
- **运动控制**：支持浮游模式和轮式模式的运动控制
- **相机模块**：双相机显示、截图、录制功能

### 📊 参数界面
- **实时数据显示**：树形结构显示所有机器人参数
- **数据绘图**：支持参数的实时绘图和历史数据查看
- **中文界面**：参数名称、单位、描述均为中文显示

### ⚙️ 设置界面
- **UI配置**：主题切换、字体设置、颜色配置
- **系统日志**：实时日志显示、过滤、保存功能
- **配置管理**：导入/导出配置文件

## 项目结构

```
uwbot_GUI/
├── main.py                 # 主应用程序入口
├── robot_data.py          # 机器人数据管理
├── styles.py              # UI样式配置
├── settings_view.py       # 设置界面
├── parameters_view.py     # 参数界面
├── requirements.txt       # 项目依赖
├── README.md             # 项目说明
├── messages/             # 消息定义
│   ├── LowlevelCmd.py    # 底层命令定义
│   ├── LowlevelState.py  # 底层状态定义
│   └── robot_data.py     # 数据管理器
└── ui_modules/           # UI模块
    ├── __init__.py       # 包初始化
    ├── status_display.py # 状态显示模块
    ├── motion_control.py # 运动控制模块
    └── camera_control.py # 相机控制模块
```

## 安装和运行

### 环境要求
- Python 3.7+
- Windows 10/11 (推荐)
- 至少4GB内存
- 支持OpenGL的显卡（用于图形渲染）

### 安装步骤

1. **克隆或下载项目**
   ```bash
   git clone <repository_url>
   cd uwbot_GUI
   ```

2. **创建虚拟环境（推荐）**
   ```bash
   python -m venv uwbot_env
   uwbot_env\Scripts\activate  # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **运行程序**
   ```bash
   python main.py
   ```

### 可能遇到的问题

**OpenCV安装失败**
```bash
# 尝试安装headless版本
pip install opencv-python-headless
```

**PyQt5安装失败**
```bash
# Windows用户可能需要安装Visual C++ Build Tools
# 或者尝试使用conda安装
conda install pyqt
```

**相机无法打开**
- 检查相机设备是否正常连接
- 确认相机驱动已正确安装
- 程序会自动使用模拟画面如果无法检测到相机

## 使用说明

### 界面切换
- 使用顶部选项卡在**控制**、**参数**、**设置**三个界面间切换
- 每个界面都有独立的功能模块

### 控制界面
1. **状态显示**：左上角显示机器人实时状态数据
2. **运动控制**：左下角控制机器人运动，支持模式切换
3. **相机模块**：右侧显示双相机画面，支持截图和录制

### 参数界面
- 左侧树形结构显示所有参数
- 右侧绘图区域显示选中参数的实时曲线
- 支持时间窗口调整和自动更新

### 设置界面
- **UI配置**：调整主题、字体、颜色等界面设置
- **系统日志**：查看系统运行日志，支持过滤和保存

## 开发说明

### 模块化设计
- 每个功能模块独立开发，便于维护和扩展
- 统一的数据管理器`robot_data.py`提供数据访问
- 样式管理器`styles.py`提供统一的UI样式

### 数据流
```
机器人硬件 → LowlevelState/LowlevelCmd → RobotDataManager → UI模块
```

### 扩展开发
1. **添加新的状态参数**：修改`LowlevelState.py`
2. **添加新的控制命令**：修改`LowlevelCmd.py`
3. **添加新的UI模块**：在`ui_modules`目录下创建新文件
4. **修改界面样式**：编辑`styles.py`文件

### 代码规范
- 使用中文注释和文档字符串
- 遵循PEP 8代码风格
- 类名使用驼峰命名法
- 函数和变量使用下划线命名法

## 配置文件

### UI配置 (ui_config.json)
程序运行后会自动生成UI配置文件，包含：
- 主题设置
- 字体配置
- 颜色方案
- 窗口大小
- 更新频率

### 相机配置
- 截图保存路径：`camera_data/camera1_screenshots/`、`camera_data/camera2_screenshots/`
- 录制保存路径：`camera_data/camera1_recordings/`、`camera_data/camera2_recordings/`

## 技术栈

- **GUI框架**：PyQt5
- **数据处理**：NumPy, SciPy
- **图像处理**：OpenCV, Pillow
- **数据可视化**：Matplotlib, PyQtGraph
- **视频处理**：ImageIO
- **系统监控**：psutil

## 版本历史

### v1.0.0 (当前版本)
- 实现基本的三界面框架
- 完成机器人状态显示和运动控制
- 添加双相机支持和录制功能
- 实现参数显示和实时绘图
- 完成设置界面和配置管理

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 贡献

欢迎提交Issue和Pull Request来改进项目。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 项目Issues页面
- 邮箱：[your-email@example.com]

---

**注意**：本项目仅供学习和研究使用，实际部署时请根据具体硬件环境进行调试和优化。