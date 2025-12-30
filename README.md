# TikTak 跨年倒计时 (TikTakCountdown)

全手绘风格的桌面倒计时工具，专为主播设计。

## 功能特性
- **跨年倒计时**：自动计算距离 2026 年的时间。
- **智能切换**：跨年后自动变为正计时，直到 99:99。
- **手绘风格**：支持自定义手绘数字和背景图片。
- **透明背景**：无边框设计，完美融入直播画面。
- **时区选择**：右键菜单支持多国时区切换。

## 快速开始

1. **运行程序**：
   - 如果你下载的是 EXE 版本，直接双击运行即可。
   - 默认会加载 `assets` 文件夹下的图片。

2. **自定义资源**：
   - 在程序同级目录下创建 `assets` 文件夹（如果不存在）。
   - 放入你的手绘图片（参考 `docs/ASSETS_LIST.md`）。
   - 重启程序即可生效。

3. **操作说明**：
   - **移动窗口**：按住窗口任意位置（数字或背景）即可拖拽。
   - **右键菜单**：
     - **选择时区**：切换到你所在的地区时间。
     - **退出**：关闭程序。

## 开发与构建

如果你想自己修改代码或重新打包：

1. **安装依赖**：
   ```bash
   pip install PyQt5 pytz pyinstaller Pillow
   ```

2. **运行代码**：
   ```bash
   python main.py
   ```

3. **生成占位资源** (可选)：
   ```bash
   python generate_assets.py
   ```

4. **打包为 EXE**：
   - 双击运行 `build.bat`。
   - 或者在命令行执行：
     ```bash
     pyinstaller --noconsole --onefile --name "TikTakCountdown" --add-data "assets;assets" main.py
     ```
   - 生成的 EXE 文件位于 `dist` 文件夹中。

## 目录结构
```
TikTak/
├── main.py              # 主程序代码
├── generate_assets.py   # 资源生成脚本
├── build.bat            # 打包脚本
├── assets/              # 图片资源目录
│   ├── 0.png - 9.png
│   ├── colon.png
│   └── bg.png
├── docs/                # 文档
│   ├── DESIGN.md
│   └── ASSETS_LIST.md
└── README.md            # 说明文档
```
