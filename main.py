# pip install PySide6 requests
import os
import platform
import requests
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QPushButton, QProgressBar, 
                               QLineEdit, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
import sys


class VersionFetchThread(QThread):
    """获取版本号的线程"""
    finished = Signal(str)
    error = Signal(str)
    
    def run(self):
        try:
            system = platform.system().lower()
            mapping = {
                "windows": "Win_x64",
                "darwin": "Mac",
                "linux": "Linux_x64"
            }
            plat_path = mapping[system]
            base_url = f"https://storage.googleapis.com/chromium-browser-snapshots/{plat_path}"
            
            response = requests.get(f"{base_url}/LAST_CHANGE", timeout=10)
            latest_rev = response.text.strip()
            self.finished.emit(latest_rev)
        except Exception as e:
            self.error.emit(str(e))


class DownloadThread(QThread):
    """下载文件的线程"""
    progress = Signal(int, int, int)  # downloaded, total, percentage
    status = Signal(str)
    finished = Signal(str)
    error = Signal(str)
    
    def __init__(self, url, file_path):
        super().__init__()
        self.url = url
        self.file_path = file_path
        self.is_cancelled = False
    
    def run(self):
        try:
            self.status.emit("正在连接...")
            response = requests.get(self.url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            buffer_size = 1024 * 1024  # 1MB
            
            self.status.emit("正在下载...")
            
            with open(self.file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=buffer_size):
                    if self.is_cancelled:
                        f.close()
                        os.remove(self.file_path)
                        self.status.emit("下载已取消")
                        return
                    
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        percentage = int((downloaded / total_size) * 100) if total_size > 0 else 0
                        self.progress.emit(downloaded, total_size, percentage)
            
            self.finished.emit(self.file_path)
        except Exception as e:
            self.error.emit(str(e))
    
    def cancel(self):
        self.is_cancelled = True


class ChromiumDownloaderWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.latest_version = None
        self.download_thread = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("开发版Chromium(适配DrissionPage) 下载器")
        self.setFixedSize(650, 450)
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title_label = QLabel("开发版Chromium(适配DrissionPage) 浏览器下载器")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 系统信息
        system = platform.system()
        system_label = QLabel(f"检测到系统: {system}")
        system_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(system_label)
        
        main_layout.addSpacing(10)
        
        # 保存路径选择
        path_layout = QHBoxLayout()
        path_label = QLabel("保存路径:")
        path_label.setFixedWidth(80)
        path_layout.addWidget(path_label)
        
        self.path_input = QLineEdit()
        self.path_input.setText(os.path.join(os.getcwd(), "download_chromium"))
        path_layout.addWidget(self.path_input)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.setFixedWidth(80)
        browse_btn.clicked.connect(self.browse_folder)
        path_layout.addWidget(browse_btn)
        
        main_layout.addLayout(path_layout)
        
        # 版本信息
        self.version_label = QLabel("版本: 未获取")
        self.version_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.version_label)
        
        # 获取版本按钮
        self.fetch_btn = QPushButton("获取最新版本")
        self.fetch_btn.setFixedHeight(35)
        self.fetch_btn.clicked.connect(self.fetch_version)
        main_layout.addWidget(self.fetch_btn)
        
        main_layout.addSpacing(10)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(25)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # 下载信息
        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.info_label)
        
        main_layout.addSpacing(10)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.download_btn = QPushButton("开始下载")
        self.download_btn.setFixedSize(120, 35)
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self.start_download)
        button_layout.addWidget(self.download_btn)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setFixedSize(120, 35)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_download)
        button_layout.addWidget(self.cancel_btn)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        main_layout.addStretch()
        central_widget.setLayout(main_layout)
    
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择保存目录")
        if folder:
            self.path_input.setText(folder)
    
    def fetch_version(self):
        self.fetch_btn.setEnabled(False)
        self.status_label.setText("正在获取最新版本...")
        
        self.fetch_thread = VersionFetchThread()
        self.fetch_thread.finished.connect(self.on_version_fetched)
        self.fetch_thread.error.connect(self.on_version_error)
        self.fetch_thread.start()
    
    def on_version_fetched(self, version):
        self.latest_version = version
        self.version_label.setText(f"最新版本: {version}")
        self.status_label.setText("版本获取成功")
        self.download_btn.setEnabled(True)
        self.fetch_btn.setEnabled(True)
    
    def on_version_error(self, error):
        QMessageBox.critical(self, "错误", f"获取版本失败: {error}")
        self.status_label.setText("获取版本失败")
        self.fetch_btn.setEnabled(True)
    
    def start_download(self):
        if not self.latest_version:
            QMessageBox.warning(self, "警告", "请先获取最新版本")
            return
        
        # 准备下载
        system = platform.system().lower()
        mapping = {
            "windows": ("Win_x64", "chrome-win.zip"),
            "darwin": ("Mac", "chrome-mac.zip"),
            "linux": ("Linux_x64", "chrome-linux.zip")
        }
        
        plat_path, zip_name = mapping[system]
        base_url = f"https://storage.googleapis.com/chromium-browser-snapshots/{plat_path}"
        download_url = f"{base_url}/{self.latest_version}/{zip_name}"
        
        save_dir = self.path_input.text()
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        file_path = os.path.join(save_dir, f"chromium_{self.latest_version}.zip")
        
        # 禁用按钮
        self.download_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.fetch_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        
        # 启动下载线程
        self.download_thread = DownloadThread(download_url, file_path)
        self.download_thread.progress.connect(self.on_download_progress)
        self.download_thread.status.connect(self.on_download_status)
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.error.connect(self.on_download_error)
        self.download_thread.start()
    
    def on_download_progress(self, downloaded, total, percentage):
        self.progress_bar.setValue(percentage)
        mb_downloaded = downloaded / (1024 * 1024)
        mb_total = total / (1024 * 1024)
        self.info_label.setText(f"已下载: {mb_downloaded:.2f} MB / {mb_total:.2f} MB")
    
    def on_download_status(self, status):
        self.status_label.setText(status)
    
    def on_download_finished(self, file_path):
        self.status_label.setText(f"下载完成!")
        QMessageBox.information(self, "成功", f"下载完成!\n文件保存至:\n{file_path}")
        self.reset_ui()
    
    def on_download_error(self, error):
        QMessageBox.critical(self, "错误", f"下载失败: {error}")
        self.status_label.setText("下载失败")
        self.reset_ui()
    
    def cancel_download(self):
        if self.download_thread:
            self.download_thread.cancel()
            self.cancel_btn.setEnabled(False)
    
    def reset_ui(self):
        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.fetch_btn.setEnabled(True)


def main():
    app = QApplication(sys.argv)
    window = ChromiumDownloaderWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()