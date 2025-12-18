# ChromeDownLoader - 开发版Chromium下载器

一个基于PySide6的图形界面工具，用于下载开发版Chromium浏览器，特别适配DrissionPage使用。

## 功能特性

- 🖥️ **跨平台支持** - 支持Windows、macOS和Linux系统
- 🔄 **自动版本检测** - 自动获取Chromium最新开发版本号
- 📥 **断点续传下载** - 支持大文件分块下载，显示实时进度
- 🎯 **DrissionPage适配** - 专门为DrissionPage自动化框架优化
- 🚀 **图形界面** - 简洁易用的PySide6界面
- 💾 **自定义路径** - 可自由选择下载保存位置

## 系统要求

- Python 3.10+
- 支持的操作系统：Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- 至少2GB可用磁盘空间

## 安装方法

### 方法一：使用uv（推荐）

项目已配置uv依赖管理：

```bash
# 安装uv（如果尚未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 激活虚拟环境并安装依赖
uv sync

# 运行程序
python main.py
```

### 方法二：使用pip

```bash
# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

### 依赖说明

- **PySide6** - 图形界面框架
- **requests** - HTTP请求库
- **pyinstaller** - 打包工具（可选）

## 使用方法

1. **启动程序**
   ```bash
   python main.py
   ```

2. **获取版本**
   - 点击"获取最新版本"按钮
   - 程序将自动检测当前系统并获取对应的最新Chromium版本

3. **选择保存路径**
   - 默认路径为当前目录下的`download_chromium`文件夹
   - 可点击"浏览..."按钮自定义保存位置

4. **开始下载**
   - 获取版本成功后，"开始下载"按钮将变为可用状态
   - 点击开始下载，程序将显示实时下载进度
   - 下载过程中可随时取消

5. **完成使用**
   - 下载完成后，压缩包将保存到指定目录
   - 解压后即可使用Chromium浏览器

## 项目结构

```
ChromeDownLoader/
├── main.py              # 主程序文件
├── pyproject.toml       # 项目配置和依赖
├── requirements.txt     # pip依赖文件
├── uv.lock             # uv锁定文件
├── build/              # 构建输出目录
├── dist/               # 分发目录
└── README.md           # 项目说明文档
```

## 代码架构

### 主要类说明

- **ChromiumDownloaderWindow** - 主窗口类，管理界面和用户交互
- **VersionFetchThread** - 版本获取线程，异步获取最新版本号
- **DownloadThread** - 下载线程，支持进度显示和取消操作

### 核心功能

- **跨平台适配**：自动识别操作系统并选择对应的Chromium版本
- **多线程下载**：使用QThread实现异步下载，避免界面卡顿
- **进度监控**：实时显示下载速度和剩余时间
- **错误处理**：完善的异常处理和用户提示

## 打包发布

使用pyinstaller打包为可执行文件：

```bash
pyinstaller --onefile --windowed  --name ChromeDownLoader --icon=app.ico main.py
```

打包后的文件将在`dist`目录中生成。

## 技术细节

### 下载源
程序从Google官方的Chromium浏览器快照存储库下载：
- Windows: `https://storage.googleapis.com/chromium-browser-snapshots/Win_x64`
- macOS: `https://storage.googleapis.com/chromium-browser-snapshots/Mac`
- Linux: `https://storage.googleapis.com/chromium-browser-snapshots/Linux_x64`

### DrissionPage适配
下载的Chromium版本经过测试，确保与DrissionPage框架兼容，适合自动化测试和网页爬虫使用。


## 许可证

本项目采用MIT许可证。详见LICENSE文件。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 更新日志

### v0.1.0 (2024-12-18)
- 初始版本发布
- 支持Windows、macOS、Linux三平台
- 图形界面下载功能
- 自动版本检测

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至项目维护者

---

