# 代码重构与架构说明文档

为了提高代码的可维护性、可读性以及修复当前存在的显示问题（如调整模式下边框消失、图标丢失等），我们对 `main.py` 进行了拆分重构。

## 1. 架构变更

原单文件结构拆分为以下模块化结构：

```text
mmticktock/
├── main.py           # 程序入口与主窗口逻辑 (CountdownWindow)
├── assets.py         # 资源加载逻辑 (AssetLoader)
├── widgets.py        # 自定义UI组件 (DraggableLabel, ContainerWidget)
├── utils.py          # 通用工具函数 (如路径处理, DPI适配)
└── layout_config.json # 配置文件
```

## 2. 模块职责

### 2.1 assets.py
- **AssetLoader 类**: 负责从 `assets/` 目录加载图片资源（数字、冒号、背景、图标）。
- 处理 PyInstaller 打包后的资源路径兼容性。
- 提供资源的集中访问点，避免在主逻辑中散落路径处理代码。

### 2.2 widgets.py
- **DraggableLabel 类**: 
  - 显示数字或冒号。
  - **核心功能**: 实现拖拽、右键菜单触发、缩放逻辑。
  - **调整模式**: 在 `is_editing=True` 时显示红色虚线边框，支持调整大小。
  - **交互**: 处理鼠标事件，支持将组件拖出窗口范围（触发窗口自动扩展）。

- **ContainerWidget 类**:
  - **核心功能**: 作为一个可视化的“蓝框”容器，用于整体移动所有数字。
  - **调整模式**: 在 `is_editing=True` 时显示蓝色虚线边框和半透明背景。
  - **交互**: 拖动蓝框时，自动计算并移动所有关联的数字组件。

### 2.3 main.py
- **CountdownWindow 类**:
  - 继承自 `QMainWindow`。
  - 负责窗口初始化、无边框设置、背景绘制。
  - **核心逻辑**: 
    - 倒计时计算与刷新 (`update_display`)。
    - 调整模式切换 (`toggle_edit_mode`)：统一控制所有子组件的编辑状态。
    - 窗口自动扩展逻辑 (`ensure_bounds`)：当数字被拖出边界时自动调整窗口大小。
    - 托盘与任务栏图标设置。
- **Entry Point**: 程序启动入口，处理异常捕获和应用配置。

## 3. 修复方案 (针对用户反馈)

### 3.1 蓝框/红框消失问题
- **原因**: 重构前的代码中，`ContainerWidget` 和 `DraggableLabel` 的层级关系或 `setStyleSheet` 调用在切换模式时可能未正确刷新，或者被背景遮挡。
- **修复**: 
  - 明确 `toggle_edit_mode` 逻辑：切换时强制调用 `show()` 和 `raise_()` 确保边框层级在背景之上。
  - 优化 `paintEvent`：仅绘制背景图片，不再干扰组件的边框绘制。

### 3.2 任务栏图标缺失
- **原因**: Windows 任务栏需要明确的 AppID 才能将无边框窗口识别为独立应用，且 `ctypes` 调用在某些环境中可能失败。
- **修复**: 
  - 增加 `ctypes` 导入的安全检查，防止因缺少 DLL 导致程序崩溃。
  - 显式调用 `setWindowIcon`，确保即使 AppID 设置失败，窗口自身也有图标。

### 3.3 数字拖拽与背景
- **优化**: 保持“无限画布”逻辑，确保数字拖拽时窗口尺寸能动态响应，不限制在背景图范围内。

## 4. 后续维护
- 修改 UI 样式请前往 `widgets.py`。
- 修改倒计时逻辑请前往 `main.py`。
- 添加新资源请更新 `assets.py`。
