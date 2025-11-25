# Discogs Album Matcher / Discogs 音乐专辑匹配器

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

**A Python desktop application to automatically search Discogs for album information, download cover images and metadata, and organize local music folders.**

**一个Python桌面应用程序，用于自动从Discogs搜索音乐专辑信息，下载封面图片和元数据，并整理本地音乐文件夹。**

[English](#english) | [中文](#中文)

</div>

<img src='screenv3.jpg'>
---

## English

### 📖 Overview

Discogs Album Matcher is a powerful Python desktop application that helps you organize your local music collection by automatically matching folder names with Discogs database entries. It downloads album covers, metadata, and tracklists, then exports everything to Excel for easy management.

### ✨ Features

- 🎵 **Auto Search**: Automatically searches Discogs database based on folder names
- 🖼️ **Image Download**: Downloads all album images (cover and additional photos)
- 📝 **Metadata Export**: Saves detailed album information as JSON files
- 📊 **Excel Export**: Exports all album data to Excel spreadsheets
- ✏️ **Smart Renaming**: Suggests folder names in "Artist - Year - Album" format with one-click renaming
- 🎯 **Multiple Results**: Interactive selection dialog when multiple matches are found
- ⏸️ **Pause & Resume**: Processing pauses when selection dialog appears, waits for user input
- 🖱️ **Double-Click Selection**: Double-click to quickly select from search results
- 📋 **Tracklist Support**: Includes complete tracklist information in JSON and details
- 🛡️ **Windows Safe**: Automatically sanitizes folder names to remove illegal characters

### 🚀 Quick Start

#### Prerequisites

- Python 3.7 or higher
- Discogs Personal Access Token ([Get one here](https://www.discogs.com/settings/developers))

#### Installation

1. **Clone or download this repository**

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment**
   
   Windows:
   ```bash
   .venv\Scripts\activate
   ```
   
   Linux/macOS:
   ```bash
   source .venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Discogs Token**
   
   Open `config.json` and find line 4:
   ```json
   "discogs_token": "YOUR_DISCOGS_TOKEN_HERE"
   ```
   Replace `"YOUR_DISCOGS_TOKEN_HERE"` with your actual token.

6. **Run the application**
   ```bash
   python disc_matcher.py
   ```

### 📖 Usage

1. **Select Folder**: Click "选择文件夹" (Select Folder) button and choose the parent directory containing your album folders

2. **Start Processing**: Click "开始处理" (Start Processing) button. The application will:
   - Search each folder name on Discogs
   - If multiple results found, show selection dialog (processing pauses automatically)
   - Download album covers and images
   - Save metadata as JSON files

3. **Review & Rename**: 
   - View details by double-clicking or right-clicking items
   - Right-click and select "重命名文件夹" (Rename Folder) to apply suggested names
   - Use "批量重命名" (Batch Rename) to rename all completed folders at once

4. **Export Excel**: Click "导出Excel" (Export Excel) to save all album information to an Excel file

### 📦 Dependencies

- **requests** (>=2.31.0) - HTTP library for Discogs API calls
- **Pillow** (>=10.0.0) - Image processing library
- **openpyxl** (>=3.1.0) - Excel file operations

Standard libraries (usually included):
- tkinter - GUI framework
- os, sys, json, time, pathlib, typing, datetime, threading, urllib.parse, io, re

### 📄 Exported Information

**Excel file includes:**
- Folder Name
- Artist
- Album Name
- Release Year
- Record Label
- Catalog Number
- Genre
- Style Tags
- Tracklist
- Notes
- Discogs ID
- Country
- Folder Path

**JSON file (`album_info.json`) includes:**
- All above information plus complete tracklist with positions and durations

**Downloaded files:**
- `cover.jpg` - Album cover image
- `image_1.jpg`, `image_2.png`, etc. - Additional album images

### ⚠️ Notes

- Discogs API has rate limits; the application automatically controls request frequency
- Ensure stable internet connection for image downloads
- Folder renaming automatically removes Windows-illegal characters (`< > : " / \ | ? *`)
- Processing pauses when selection dialog appears, allowing you to choose without rushing

### 🐛 Troubleshooting

**Q: ModuleNotFoundError: No module named 'tkinter'**

A: Install tkinter based on your system:
- Ubuntu/Debian: `sudo apt-get install python3-tk`
- Fedora/RHEL: `sudo dnf install python3-tkinter`
- macOS: Usually included, or install via Homebrew
- Windows: Usually included in Python installation

**Q: How to get Discogs Token?**

A: Visit https://www.discogs.com/settings/developers, log in, and click "Generate new token"

**Q: Can I use this without virtual environment?**

A: Yes, but using virtual environment is recommended to avoid conflicts with other projects.

### 📝 License

MIT License - feel free to use this project for personal or commercial purposes.

---

## 中文

### 📖 项目简介

Discogs 音乐专辑匹配器是一个强大的Python桌面应用程序，通过自动匹配文件夹名称与Discogs数据库条目，帮助您整理本地音乐收藏。它可以下载专辑封面、元数据和曲目表，并将所有信息导出到Excel以便管理。

### ✨ 功能特点

- 🎵 **自动搜索**: 根据文件夹名称自动在Discogs数据库搜索专辑信息
- 🖼️ **图片下载**: 下载所有专辑图片（封面和附加照片）
- 📝 **元数据导出**: 将详细专辑信息保存为JSON文件
- 📊 **Excel导出**: 将所有专辑数据导出到Excel表格
- ✏️ **智能重命名**: 提供"音乐人 -年份- 专辑名"格式的重命名建议，一键重命名
- 🎯 **多结果选择**: 找到多个匹配结果时提供交互式选择对话框
- ⏸️ **暂停等待**: 弹出选择框时处理暂停，等待用户选择
- 🖱️ **双击选择**: 双击快速从搜索结果中选择
- 📋 **曲目表支持**: JSON和详情中包含完整曲目表信息
- 🛡️ **Windows安全**: 自动清理文件夹名称中的非法字符

### 🚀 快速开始

#### 环境要求

- Python 3.7 或更高版本
- Discogs Personal Access Token（[在此获取](https://www.discogs.com/settings/developers)）

#### 安装步骤

1. **克隆或下载此仓库**

2. **创建虚拟环境（推荐）**
   ```bash
   python -m venv .venv
   ```

3. **激活虚拟环境**
   
   Windows:
   ```bash
   .venv\Scripts\activate
   ```
   
   Linux/macOS:
   ```bash
   source .venv/bin/activate
   ```

4. **安装依赖包**
   ```bash
   pip install -r requirements.txt
   ```

5. **配置Discogs Token**
   
   打开 `config.json` 文件，找到第4行：
   ```json
   "discogs_token": "YOUR_DISCOGS_TOKEN_HERE"
   ```
   将 `"YOUR_DISCOGS_TOKEN_HERE"` 替换为你的实际Token。

6. **运行程序**
   ```bash
   python disc_matcher.py
   ```

### 📖 使用方法

1. **选择文件夹**: 点击"选择文件夹"按钮，选择包含专辑文件夹的父目录

2. **开始处理**: 点击"开始处理"按钮。程序将：
   - 在Discogs上搜索每个文件夹名称
   - 如果找到多个结果，显示选择对话框（处理自动暂停）
   - 下载专辑封面和图片
   - 将元数据保存为JSON文件

3. **查看和重命名**: 
   - 双击或右键点击查看详细信息
   - 右键点击选择"重命名文件夹"应用建议的名称
   - 使用"批量重命名"一次性重命名所有已完成的文件夹

4. **导出Excel**: 点击"导出Excel"将所有专辑信息保存到Excel文件

### 📦 依赖包

- **requests** (>=2.31.0) - HTTP请求库，用于调用Discogs API
- **Pillow** (>=10.0.0) - 图片处理库
- **openpyxl** (>=3.1.0) - Excel文件操作库

标准库（通常已包含）：
- tkinter - GUI框架
- os, sys, json, time, pathlib, typing, datetime, threading, urllib.parse, io, re

### 📄 导出信息

**Excel文件包含：**
- 文件夹名
- 音乐人
- 专辑名
- 出版年份
- 唱片厂牌
- 厂牌编号
- 音乐风格
- 风格标签
- 曲目表
- 备注信息
- Discogs ID
- 国家
- 文件夹路径

**JSON文件 (`album_info.json`) 包含：**
- 上述所有信息，以及包含位置和时长的完整曲目表

**下载的文件：**
- `cover.jpg` - 专辑封面图片
- `image_1.jpg`, `image_2.png` 等 - 其他专辑图片

### ⚠️ 注意事项

- Discogs API有速率限制，程序会自动控制请求频率
- 确保网络连接稳定以便下载图片
- 文件夹重命名会自动移除Windows非法字符（`< > : " / \ | ? *`）
- 弹出选择框时处理会暂停，让您有充足时间选择

### 🐛 常见问题

**Q: ModuleNotFoundError: No module named 'tkinter'**

A: 根据系统安装tkinter：
- Ubuntu/Debian: `sudo apt-get install python3-tk`
- Fedora/RHEL: `sudo dnf install python3-tkinter`
- macOS: 通常已包含，或通过Homebrew安装
- Windows: 通常已包含在Python安装中

**Q: 如何获取Discogs Token？**

A: 访问 https://www.discogs.com/settings/developers，登录后点击"Generate new token"

**Q: 可以不使用虚拟环境吗？**

A: 可以，但推荐使用虚拟环境以避免与其他项目冲突。

### 📝 许可证

MIT License - 可自由用于个人或商业用途。

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

欢迎贡献代码！请随时提交Pull Request。

## 📧 Contact

For issues and questions, please open an issue on GitHub.

如有问题，请在GitHub上提交issue。

---

<div align="center">

**Made with ❤️ for music lovers**

**为音乐爱好者制作**

</div>

