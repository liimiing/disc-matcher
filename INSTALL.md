# 安装说明

## 环境要求

- Python 3.7 或更高版本
- pip（Python包管理器）

## 安装步骤

### 方法一：使用虚拟环境（推荐）

1. **创建虚拟环境**
   ```bash
   python -m venv .venv
   ```

2. **激活虚拟环境**
   
   Windows:
   ```bash
   .venv\Scripts\activate
   ```
   
   Linux/macOS:
   ```bash
   source .venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **运行程序**
   ```bash
   python disc_matcher.py
   ```

### 方法二：全局安装（不推荐）

直接安装到系统Python环境：
```bash
pip install -r requirements.txt
```

## 依赖包说明

### 必需依赖

- **requests** (>=2.31.0) - HTTP请求库，用于调用Discogs API
- **Pillow** (>=10.0.0) - 图片处理库，用于下载和保存专辑封面
- **openpyxl** (>=3.1.0) - Excel文件操作库，用于导出专辑信息

### 标准库（通常已包含）

以下库是Python标准库，通常不需要单独安装：
- tkinter - GUI界面库
- os, sys, json, time, pathlib, typing, datetime, threading, urllib.parse, io, re

### tkinter 特殊说明

如果遇到 `ModuleNotFoundError: No module named 'tkinter'` 错误，请根据系统安装：

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3-tk
```

**Fedora/RHEL:**
```bash
sudo dnf install python3-tkinter
```

**macOS:**
通常已包含，如无则通过Homebrew安装：
```bash
brew install python-tk
```

**Windows:**
通常已包含在Python安装中，如无请重新安装Python并勾选"tcl/tk and IDLE"选项。

## 验证安装

运行以下命令验证所有依赖是否已正确安装：

```bash
python -c "import requests; import PIL; import openpyxl; import tkinter; print('所有依赖已安装成功！')"
```

## 常见问题

### Q: pip install 失败怎么办？
A: 尝试使用国内镜像源：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: 虚拟环境激活后命令提示符没有变化？
A: 这是正常的，激活后你应该能看到 `(.venv)` 前缀。如果使用PowerShell，可能需要先运行 `Set-ExecutionPolicy RemoteSigned`。

### Q: 如何退出虚拟环境？
A: 运行命令：`deactivate`

### Q: 如何更新依赖包？
A: 运行命令：`pip install --upgrade -r requirements.txt`

