#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discogs 音乐专辑匹配器
自动从Discogs搜索专辑信息，下载封面和元数据，并整理文件夹

使用前请配置Discogs Token:
1. 访问 https://www.discogs.com/settings/developers
2. 生成Personal Access Token
3. 在DiscMatcherApp类中找到DISCOGS_TOKEN变量，将Token填入
"""

import os
import sys
import json
import time
import requests
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import threading
from urllib.parse import quote
from PIL import Image
import io
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
import re


class DiscogsAPI:
    """Discogs API 客户端"""
    
    BASE_URL = "https://api.discogs.com"
    
    def __init__(self, token: str):
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DiscMatcher/1.0',
            'Authorization': f'Discogs token={token}'
        })
    
    def search(self, query: str) -> List[Dict]:
        """搜索专辑"""
        # 清理查询字符串
        cleaned_query = query.replace('[', '').replace(']', '').replace('(', '').replace(')', '')
        cleaned_query = cleaned_query.replace('.', ' ').replace('_', ' ').replace('-', ' ')
        cleaned_query = ' '.join(cleaned_query.split())
        
        url = f"{self.BASE_URL}/database/search"
        params = {
            'q': cleaned_query,
            'type': 'release',
            'token': self.token
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('results', [])
        except requests.exceptions.RequestException as e:
            print(f"搜索错误: {e}")
            return []
    
    def get_release_details(self, release_id: int) -> Optional[Dict]:
        """获取专辑详细信息"""
        url = f"{self.BASE_URL}/releases/{release_id}"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"获取详情错误: {e}")
            return None
    
    def download_image(self, url: str, save_path: Path) -> bool:
        """下载图片"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            img = Image.open(io.BytesIO(response.content))
            img.save(save_path)
            return True
        except Exception as e:
            print(f"下载图片错误: {e}")
            return False


class AlbumInfo:
    """专辑信息类"""
    
    def __init__(self, release_data: Dict):
        self.release_id = release_data.get('id')
        self.title = release_data.get('title', '')
        self.year = release_data.get('year', '')
        self.cover_image = release_data.get('cover_image', '')
        self.thumb = release_data.get('thumb', '')
        
        # 解析艺术家和专辑名
        if ' - ' in self.title:
            parts = self.title.split(' - ', 1)
            self.artist = parts[0].strip()
            self.album_name = parts[1].strip()
        else:
            self.artist = ''
            self.album_name = self.title
        
        # 标签信息
        self.labels = release_data.get('label', [])
        if isinstance(self.labels, list):
            self.label_names = [l.get('name', '') if isinstance(l, dict) else str(l) for l in self.labels]
        else:
            self.label_names = [str(self.labels)] if self.labels else []
        
        self.catalog_no = release_data.get('catno', '')
        self.country = release_data.get('country', '')
        self.genre = release_data.get('genre', [])
        self.style = release_data.get('style', [])
        self.format = release_data.get('format', [])
        
        # 详细信息（需要额外请求）
        self.details = None
        self.notes = ''
        self.tracklist = []  # 曲目表
        self.images = []  # 所有图片URL
    
    def sanitize_filename(self, filename: str) -> str:
        """清理Windows文件名中的非法字符"""
        # Windows不允许的字符: < > : " / \ | ? *
        illegal_chars = r'[<>:"/\\|?*]'
        # 替换为下划线
        sanitized = re.sub(illegal_chars, '_', filename)
        # 移除首尾空格和点号
        sanitized = sanitized.strip(' .')
        # 移除连续的下划线
        sanitized = re.sub(r'_+', '_', sanitized)
        return sanitized
    
    def get_suggested_folder_name(self) -> str:
        """生成建议的文件夹名：音乐人 -年份- 专辑名"""
        parts = []
        if self.artist:
            parts.append(self.sanitize_filename(self.artist))
        if self.year:
            parts.append(str(self.year))
        if self.album_name:
            parts.append(self.sanitize_filename(self.album_name))
        
        if parts:
            suggested = ' - '.join(parts)
            # 再次清理整个字符串
            return self.sanitize_filename(suggested)
        return self.sanitize_filename(self.title)
    
    def to_dict(self) -> Dict:
        """转换为字典用于Excel导出和JSON保存"""
        return {
            '音乐人': self.artist,
            '专辑名': self.album_name,
            '出版年份': self.year,
            '唱片厂牌': ', '.join(self.label_names),
            '厂牌编号': self.catalog_no,
            '音乐风格': ', '.join(self.genre) if isinstance(self.genre, list) else str(self.genre),
            '风格标签': ', '.join(self.style) if isinstance(self.style, list) else str(self.style),
            '备注信息': self.notes,
            'Discogs ID': self.release_id,
            '国家': self.country,
            '曲目表': self.tracklist
        }


class DiscMatcherApp:
    """主应用程序"""
    
    # Discogs Token - 请在这里填入你的Token
    DISCOGS_TOKEN = "WjzqFqSmpNdGLjWgESMTyGlWcYuNKSSFpGJkwdQE"
    
    def __init__(self, root):
        self.root = root
        self.root.title("Discogs 音乐专辑匹配器")
        self.root.geometry("1200x800")
        
        self.discogs_api = None
        self.root_folder = None
        self.album_folders = []  # List of (folder_path, folder_name, album_info)
        self.processing_thread = None
        self.waiting_for_selection = threading.Event()  # 用于等待用户选择
        self.selection_result = None  # 存储用户选择的结果
        
        # 初始化Discogs API
        if self.DISCOGS_TOKEN and self.DISCOGS_TOKEN != "YOUR_DISCOGS_TOKEN_HERE":
            self.discogs_api = DiscogsAPI(self.DISCOGS_TOKEN)
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        # 顶部工具栏
        toolbar = ttk.Frame(self.root, padding="10")
        toolbar.pack(fill=tk.X)
        
        # 显示Token状态
        token_status = "已配置" if (self.DISCOGS_TOKEN and self.DISCOGS_TOKEN != "YOUR_DISCOGS_TOKEN_HERE") else "未配置"
        token_color = "green" if token_status == "已配置" else "red"
        token_label = ttk.Label(toolbar, text=f"Token状态: {token_status}", foreground=token_color)
        token_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(toolbar, text="选择文件夹", command=self.select_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="开始处理", command=self.start_processing).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="批量重命名", command=self.batch_rename).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="导出Excel", command=self.export_excel).pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(toolbar, variable=self.progress_var, maximum=100, length=200)
        self.progress_bar.pack(side=tk.LEFT, padx=10)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 主内容区域
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建Treeview显示列表
        columns = ('文件夹名', '音乐人', '专辑名', '年份', '状态', '建议名称')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        self.tree.column('文件夹名', width=200)
        self.tree.column('建议名称', width=250)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 右键菜单
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="查看详情", command=self.view_details)
        self.context_menu.add_command(label="选择专辑", command=self.select_album)
        self.context_menu.add_command(label="重命名文件夹", command=self.rename_folder)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="打开文件夹", command=self.open_folder)
        
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.on_double_click)
    
    def select_folder(self):
        """选择根文件夹"""
        folder = filedialog.askdirectory(title="选择包含音乐专辑文件夹的根目录")
        if folder:
            self.root_folder = Path(folder)
            self.scan_folders()
    
    def scan_folders(self):
        """扫描文件夹下的所有子文件夹"""
        if not self.root_folder:
            return
        
        self.album_folders = []
        self.tree.delete(*self.tree.get_children())
        
        try:
            # 直接扫描选择文件夹下的所有子文件夹
            for item in self.root_folder.iterdir():
                if item.is_dir():
                    folder_name = item.name
                    self.album_folders.append((item, folder_name, None))
                    self.tree.insert('', tk.END, values=(
                        folder_name, '', '', '', '待处理', ''
                    ))
            
            self.status_var.set(f"找到 {len(self.album_folders)} 个文件夹")
        except Exception as e:
            messagebox.showerror("错误", f"扫描文件夹时出错: {e}")
            self.status_var.set("扫描失败")
    
    def start_processing(self):
        """开始处理"""
        # 检查Token是否配置
        if not self.discogs_api:
            if not self.DISCOGS_TOKEN or self.DISCOGS_TOKEN == "YOUR_DISCOGS_TOKEN_HERE":
                messagebox.showwarning("警告", "请在代码中配置Discogs Token\n在disc_matcher.py文件中找到DISCOGS_TOKEN变量并填入你的Token")
                return
            self.discogs_api = DiscogsAPI(self.DISCOGS_TOKEN)
        
        if not self.album_folders:
            messagebox.showwarning("警告", "请先选择文件夹")
            return
        
        # 在新线程中处理
        self.processing_thread = threading.Thread(target=self.process_folders, daemon=True)
        self.processing_thread.start()
    
    def process_folders(self):
        """处理所有文件夹"""
        total = len(self.album_folders)
        for idx, (folder_path, folder_name, _) in enumerate(self.album_folders):
            # 更新进度
            progress = (idx + 1) / total * 100
            self.root.after(0, lambda p=progress: self.progress_var.set(p))
            self.root.after(0, lambda i=idx: self.update_status(f"正在处理 ({i+1}/{total}): {self.album_folders[i][1]}"))
            
            # 更新状态为搜索中
            self.root.after(0, lambda i=idx: self.update_tree_item(i, status='搜索中'))
            
            # 搜索Discogs
            results = self.discogs_api.search(folder_name)
            
            if not results:
                self.root.after(0, lambda i=idx: self.update_tree_item(i, status='未找到'))
                continue
            
            # 如果只有一个结果，自动选择
            if len(results) == 1:
                album_info = self.process_release(results[0], folder_path)
                if album_info:
                    self.album_folders[idx] = (folder_path, folder_name, album_info)
                    suggested_name = album_info.get_suggested_folder_name()
                    self.root.after(0, lambda i=idx, s=suggested_name, a=album_info: 
                        self.update_tree_item(i, status='已完成', album_info=a, suggested=s))
            else:
                # 多个结果，需要用户选择 - 暂停处理，等待用户选择
                self.root.after(0, lambda i=idx, r=results: self.show_selection_dialog(i, r))
                # 等待用户选择
                self.waiting_for_selection.wait()
                self.waiting_for_selection.clear()
                
                # 获取用户选择的结果
                if self.selection_result:
                    album_info = self.process_release(self.selection_result, folder_path)
                    if album_info:
                        self.album_folders[idx] = (folder_path, folder_name, album_info)
                        suggested_name = album_info.get_suggested_folder_name()
                        self.root.after(0, lambda i=idx, s=suggested_name, a=album_info: 
                            self.update_tree_item(i, status='已完成', album_info=a, suggested=s))
                    self.selection_result = None
            
            # 避免API速率限制
            time.sleep(1.2)
        
        self.root.after(0, lambda: self.status_var.set("处理完成"))
        self.root.after(0, lambda: self.progress_var.set(0))
    
    def process_release(self, release_data: Dict, folder_path: Path) -> Optional[AlbumInfo]:
        """处理单个专辑信息"""
        album_info = AlbumInfo(release_data)
        
        # 获取详细信息
        if album_info.release_id:
            details = self.discogs_api.get_release_details(album_info.release_id)
            if details:
                album_info.details = details
                album_info.notes = details.get('notes', '')
                
                # 提取曲目表
                tracklist = details.get('tracklist', [])
                album_info.tracklist = []
                for track in tracklist:
                    track_info = {
                        '位置': track.get('position', ''),
                        '标题': track.get('title', ''),
                        '时长': track.get('duration', '')
                    }
                    album_info.tracklist.append(track_info)
                
                # 获取所有图片
                images = details.get('images', [])
                album_info.images = [img.get('uri', '') for img in images if img.get('uri')]
        
        # 下载所有图片
        image_count = 0
        downloaded_urls = set()  # 跟踪已下载的URL，避免重复
        
        # 下载封面图片（如果存在且不在images列表中）
        if album_info.cover_image and album_info.cover_image not in album_info.images:
            cover_path = folder_path / "cover.jpg"
            if self.discogs_api.download_image(album_info.cover_image, cover_path):
                image_count += 1
                downloaded_urls.add(album_info.cover_image)
        
        # 下载所有图片（包括封面）
        if album_info.images:
            for idx, img_url in enumerate(album_info.images):
                if img_url and img_url not in downloaded_urls:
                    # 确定文件扩展名
                    ext = 'jpg'
                    if '.png' in img_url.lower():
                        ext = 'png'
                    elif '.gif' in img_url.lower():
                        ext = 'gif'
                    elif '.webp' in img_url.lower():
                        ext = 'webp'
                    
                    # 如果是第一张图片且没有单独的cover，保存为cover.jpg
                    if idx == 0 and not album_info.cover_image:
                        img_path = folder_path / "cover.jpg"
                    else:
                        img_path = folder_path / f"image_{idx+1}.{ext}"
                    
                    if self.discogs_api.download_image(img_url, img_path):
                        image_count += 1
                        downloaded_urls.add(img_url)
        
        # 如果只有cover_image，也下载它
        if album_info.cover_image and album_info.cover_image not in downloaded_urls:
            cover_path = folder_path / "cover.jpg"
            if self.discogs_api.download_image(album_info.cover_image, cover_path):
                image_count += 1
        
        # 保存文本信息
        info_path = folder_path / "album_info.json"
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(album_info.to_dict(), f, ensure_ascii=False, indent=2)
        
        return album_info
    
    def show_selection_dialog(self, idx: int, results: List[Dict]):
        """显示选择对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("选择专辑")
        dialog.geometry("700x550")
        dialog.transient(self.root)
        dialog.grab_set()  # 模态对话框
        
        folder_name = self.album_folders[idx][1]
        ttk.Label(dialog, text=f"文件夹: {folder_name}\n找到多个匹配结果，请选择（双击或选择后点击确定）:", 
                 font=('Arial', 10, 'bold')).pack(pady=10)
        
        # 列表框
        listbox_frame = ttk.Frame(dialog)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        listbox = tk.Listbox(listbox_frame, height=18, font=('Arial', 9))
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        
        for result in results:
            title = result.get('title', '')
            year = result.get('year', '')
            label = result.get('label', [])
            label_str = ', '.join([l.get('name', '') if isinstance(l, dict) else str(l) for l in label[:2]]) if label else ''
            display_text = f"{title} ({year}) - {label_str}"
            listbox.insert(tk.END, display_text)
        
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def on_select():
            selection = listbox.curselection()
            if selection:
                self.selection_result = results[selection[0]]
                dialog.destroy()
                self.waiting_for_selection.set()  # 通知处理线程继续
        
        def on_double_click(event):
            """双击选择"""
            selection = listbox.curselection()
            if selection:
                on_select()
        
        def on_cancel():
            self.selection_result = None
            dialog.destroy()
            self.waiting_for_selection.set()  # 通知处理线程继续（取消）
        
        # 绑定双击事件
        listbox.bind('<Double-Button-1>', on_double_click)
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="确定", command=on_select).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=on_cancel).pack(side=tk.LEFT, padx=5)
        
        dialog.wait_window()
    
    def update_tree_item(self, idx: int, status: str = None, album_info: AlbumInfo = None, suggested: str = None):
        """更新树形视图项"""
        folder_path, folder_name, current_info = self.album_folders[idx]
        
        if album_info:
            current_info = album_info
        
        if current_info:
            values = (
                folder_name,
                current_info.artist,
                current_info.album_name,
                current_info.year,
                status or '已完成',
                suggested or current_info.get_suggested_folder_name()
            )
        else:
            values = (
                folder_name,
                '',
                '',
                '',
                status or '待处理',
                ''
            )
        
        # 找到对应的item并更新
        for item in self.tree.get_children():
            if self.tree.item(item, 'values')[0] == folder_name:
                self.tree.item(item, values=values)
                break
    
    def update_status(self, message: str):
        """更新状态栏"""
        self.status_var.set(message)
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            self.context_menu.post(event.x_root, event.y_root)
    
    def on_double_click(self, event):
        """双击事件"""
        self.view_details()
    
    def view_details(self):
        """查看详情"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item, 'values')
        folder_name = values[0]
        
        # 找到对应的专辑信息
        for folder_path, name, album_info in self.album_folders:
            if name == folder_name and album_info:
                self.show_details_dialog(album_info)
                break
    
    def show_details_dialog(self, album_info: AlbumInfo):
        """显示详情对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("专辑详情")
        dialog.geometry("500x600")
        
        text_widget = tk.Text(dialog, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # 格式化曲目表
        tracklist_text = ""
        if album_info.tracklist:
            tracklist_text = "\n\n曲目表:\n"
            for track in album_info.tracklist:
                position = track.get('位置', '')
                title = track.get('标题', '')
                duration = track.get('时长', '')
                tracklist_text += f"  {position}. {title}"
                if duration:
                    tracklist_text += f" ({duration})"
                tracklist_text += "\n"
        
        details_text = f"""
音乐人: {album_info.artist}
专辑名: {album_info.album_name}
出版年份: {album_info.year}
唱片厂牌: {', '.join(album_info.label_names)}
厂牌编号: {album_info.catalog_no}
音乐风格: {', '.join(album_info.genre) if isinstance(album_info.genre, list) else album_info.genre}
风格标签: {', '.join(album_info.style) if isinstance(album_info.style, list) else album_info.style}
国家: {album_info.country}
Discogs ID: {album_info.release_id}
{tracklist_text}
备注信息:
{album_info.notes if album_info.notes else '无'}
        """
        
        text_widget.insert('1.0', details_text.strip())
        text_widget.config(state=tk.DISABLED)
        
        ttk.Button(dialog, text="关闭", command=dialog.destroy).pack(pady=10)
    
    def select_album(self):
        """手动选择专辑"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item, 'values')
        folder_name = values[0]
        
        # 找到对应的文件夹
        for idx, (folder_path, name, _) in enumerate(self.album_folders):
                if name == folder_name:
                    if not self.discogs_api:
                        if not self.DISCOGS_TOKEN or self.DISCOGS_TOKEN == "YOUR_DISCOGS_TOKEN_HERE":
                            messagebox.showwarning("警告", "请在代码中配置Discogs Token")
                            return
                        self.discogs_api = DiscogsAPI(self.DISCOGS_TOKEN)
                    
                    results = self.discogs_api.search(folder_name)
                    if results:
                        self.show_selection_dialog(idx, results)
                    else:
                        messagebox.showinfo("提示", "未找到匹配结果")
                    break
    
    def rename_folder(self):
        """重命名文件夹"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item, 'values')
        folder_name = values[0]
        suggested_name = values[5]
        
        if not suggested_name:
            messagebox.showwarning("警告", "没有建议的名称")
            return
        
        # 找到对应的文件夹
        for folder_path, name, album_info in self.album_folders:
            if name == folder_name:
                # 确保名称已清理（双重保险）
                if album_info:
                    cleaned_name = album_info.get_suggested_folder_name()
                else:
                    # 如果没有album_info，手动清理
                    cleaned_name = re.sub(r'[<>:"/\\|?*]', '_', suggested_name).strip(' .')
                
                new_path = folder_path.parent / cleaned_name
                
                if new_path.exists():
                    messagebox.showwarning("警告", f"目标文件夹已存在: {cleaned_name}")
                    return
                
                try:
                    folder_path.rename(new_path)
                    messagebox.showinfo("成功", f"文件夹已重命名为: {cleaned_name}")
                    self.scan_folders()  # 重新扫描
                except Exception as e:
                    messagebox.showerror("错误", f"重命名失败: {e}")
                break
    
    def batch_rename(self):
        """批量重命名所有已完成的文件夹"""
        rename_count = 0
        skipped_count = 0
        error_count = 0
        
        for folder_path, folder_name, album_info in self.album_folders:
            if not album_info:
                continue
            
            suggested_name = album_info.get_suggested_folder_name()
            if not suggested_name or suggested_name == folder_name:
                skipped_count += 1
                continue
            
            new_path = folder_path.parent / suggested_name
            
            if new_path.exists():
                skipped_count += 1
                continue
            
            try:
                folder_path.rename(new_path)
                rename_count += 1
            except Exception as e:
                error_count += 1
                print(f"重命名失败 {folder_name}: {e}")
        
        messagebox.showinfo("批量重命名完成", 
            f"成功: {rename_count}\n跳过: {skipped_count}\n失败: {error_count}")
        
        if rename_count > 0:
            self.scan_folders()  # 重新扫描
    
    def open_folder(self):
        """打开文件夹"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item, 'values')
        folder_name = values[0]
        
        for folder_path, name, _ in self.album_folders:
            if name == folder_name:
                try:
                    if sys.platform == 'win32':
                        os.startfile(folder_path)
                    elif sys.platform == 'darwin':
                        os.system(f'open "{folder_path}"')
                    else:
                        os.system(f'xdg-open "{folder_path}"')
                except Exception as e:
                    messagebox.showerror("错误", f"无法打开文件夹: {e}")
                break
    
    def export_excel(self):
        """导出到Excel"""
        # 收集所有已完成的专辑信息
        completed_albums = []
        for folder_path, folder_name, album_info in self.album_folders:
            if album_info:
                data = album_info.to_dict()
                data['文件夹名'] = folder_name
                data['文件夹路径'] = str(folder_path)
                completed_albums.append(data)
        
        if not completed_albums:
            messagebox.showwarning("警告", "没有可导出的数据")
            return
        
        # 选择保存位置
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="保存Excel文件"
        )
        
        if not filename:
            return
        
        # 创建Excel文件
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "专辑信息"
        
        # 设置表头
        headers = ['文件夹名', '音乐人', '专辑名', '出版年份', '唱片厂牌', '厂牌编号', 
                  '音乐风格', '风格标签', '备注信息', 'Discogs ID', '国家', '文件夹路径']
        
        # 设置表头样式
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # 写入数据
        for row_idx, album_data in enumerate(completed_albums, 2):
            for col_idx, header in enumerate(headers, 1):
                value = album_data.get(header, '')
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                cell.alignment = Alignment(vertical='top', wrap_text=True)
        
        # 调整列宽
        for col_idx, header in enumerate(headers, 1):
            col_letter = get_column_letter(col_idx)
            if header in ['文件夹路径', '备注信息']:
                ws.column_dimensions[col_letter].width = 40
            elif header in ['音乐人', '专辑名', '唱片厂牌']:
                ws.column_dimensions[col_letter].width = 25
            else:
                ws.column_dimensions[col_letter].width = 15
        
        # 冻结首行
        ws.freeze_panes = 'A2'
        
        # 保存文件
        try:
            wb.save(filename)
            messagebox.showinfo("成功", f"Excel文件已保存: {filename}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")


def main():
    root = tk.Tk()
    app = DiscMatcherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

