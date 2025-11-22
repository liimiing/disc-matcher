# disc-matcher
A web-based tool to scan local folder structures, match albums against the Discogs Database, resolve conflicts, and export metadata to CSV/Excel. Features AI-powered album analysis.

# Discogs 音乐专辑匹配器

一个Python桌面应用程序，用于自动从Discogs搜索音乐专辑信息，下载封面图片和元数据，并整理本地音乐文件夹。

## 功能特点

- 🎵 **自动搜索**: 根据文件夹名称自动在Discogs搜索专辑信息
- 🖼️ **封面下载**: 自动下载专辑封面图片到文件夹
- 📝 **信息保存**: 将专辑信息保存为JSON文件
- 📊 **Excel导出**: 将所有专辑信息导出为Excel表格
- ✏️ **智能重命名**: 提供"音乐人 -年份- 专辑名"格式的重命名建议，一键重命名
- 🎯 **多结果选择**: 当搜索结果有多个时，提供选择界面
- 📋 **详细信息**: 显示完整的专辑信息（音乐人、年份、厂牌、风格等）

## 安装要求

- Python 3.7 或更高版本
- Discogs Personal Access Token（在 https://www.discogs.com/settings/developers 申请）

## 安装步骤

1. 安装依赖包：
```bash
pip install -r requirements.txt
```

2. 运行程序：
```bash
python disc_matcher.py
```

==========================================
Discogs Token 配置说明
==========================================

1. 打开 disc_matcher.py 文件

2. 找到第162行左右的这一行：
   DISCOGS_TOKEN = "YOUR_DISCOGS_TOKEN_HERE"

3. 将 "YOUR_DISCOGS_TOKEN_HERE" 替换为你的Discogs Token

4. 获取Token的方法：
   - 访问：https://www.discogs.com/settings/developers
   - 登录你的Discogs账号
   - 点击 "Generate new token"
   - 复制生成的Token（只显示一次，请妥善保存）

5. 配置完成后，运行程序时界面会显示 "Token状态: 已配置"（绿色）

示例：
DISCOGS_TOKEN = "abc123xyz456your_token_here"

## 使用方法

1. **获取Discogs Token**:
   - 访问 https://www.discogs.com/settings/developers
   - 创建Personal Access Token
   - 将Token复制到程序界面

2. **选择文件夹**:
   - 点击"选择文件夹"按钮
   - 选择包含音乐专辑文件夹的根目录
   - 程序会自动扫描二级子文件夹

3. **开始处理**:
   - 点击"开始处理"按钮
   - 程序会逐一搜索每个文件夹名称
   - 如果找到多个结果，会弹出选择对话框

4. **查看和重命名**:
   - 在列表中查看所有文件夹的处理状态
   - 双击或右键点击查看详细信息
   - 右键点击选择"重命名文件夹"来应用建议的名称

5. **导出Excel**:
   - 点击"导出Excel"按钮
   - 选择保存位置
   - 所有已处理的专辑信息将导出为Excel文件

## 导出的信息

Excel文件包含以下列：
- 文件夹名
- 音乐人
- 专辑名
- 出版年份
- 唱片厂牌
- 厂牌编号
- 音乐风格
- 风格标签
- 备注信息
- Discogs ID
- 国家
- 文件夹路径

## 下载的文件

每个处理过的文件夹会包含：
- `cover.jpg` - 专辑封面图片
- `album_info.json` - 专辑详细信息（JSON格式）

## 注意事项

- Discogs API有速率限制，程序会自动控制请求频率
- 确保网络连接正常，以便下载封面图片
- 重命名文件夹前请确保没有同名文件夹
- 建议在处理大量文件夹前先测试少量文件夹

## 许可证

MIT License

