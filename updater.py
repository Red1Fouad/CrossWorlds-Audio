import sys
import os
import shutil
from pathlib import Path
from urllib import request

try:
    from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QProgressBar, 
                                 QLabel, QPushButton, QTextEdit, QMessageBox)
    from PySide6.QtCore import Qt, QTimer
    HAS_QT = True
except ImportError:
    HAS_QT = False

if HAS_QT:
    import py7zr


class UpdaterUI(QWidget):
    def __init__(self, download_url, new_version):
        super().__init__()
        self.download_url = download_url
        self.new_version = new_version
        
        if getattr(sys, 'frozen', False):
            self.app_dir = Path(sys.executable).parent
        else:
            self.app_dir = Path(__file__).parent.resolve()
        
        self.temp_dir = self.app_dir / "update_temp"
        self.archive_path = self.app_dir / f"CrossWorlds-Music-Editor{new_version}.7z"
        self.skip_files = {"_internal", "updater.exe"}
        
        self.init_ui()
        self.log(f"Starting download of v{self.new_version}...")
        QTimer.singleShot(0, self.start_download)
        
    def init_ui(self):
        self.setWindowTitle(f"CrossWorlds Music Editor - Updating to v{self.new_version}")
        self.setFixedSize(450, 220)
        layout = QVBoxLayout()
        
        self.status_label = QLabel("Downloading update...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(100)
        layout.addWidget(self.log_text)
        
        button_layout = QVBoxLayout()
        self.launch_btn = QPushButton("Launch Application")
        self.launch_btn.hide()
        self.launch_btn.clicked.connect(self.launch_app)
        button_layout.addWidget(self.launch_btn)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.hide()
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def log(self, msg):
        self.log_text.append(msg)
        
    def process_events(self):
        QApplication.processEvents()
        
    def update_progress(self, value, status):
        self.progress_bar.setValue(value)
        self.status_label.setText(status)
        self.log(status)
        self.process_events()
        
    def start_download(self):
        try:
            req = request.Request(self.download_url, headers={"Accept": "application/octet-stream"})
            with request.urlopen(req, timeout=120) as response:
                total = int(response.headers.get('Content-Length', 0))
                downloaded = 0
                self.log(f"Downloading to {self.archive_path}...")
                with open(self.archive_path, 'wb') as f:
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            pct = int(downloaded / total * 100)
                            self.update_progress(pct, f"Downloading... {downloaded // (1024*1024)} MB / {total // (1024*1024)} MB")
            self.log("Download complete.")
            QTimer.singleShot(0, self.start_extract)
        except Exception as e:
            self.log(f"ERROR: {e}")
            self.status_label.setText("Update Failed!")
            self.log_text.selectAll()
            QMessageBox.critical(self, "Update Failed", 
                                f"Download failed!\n\n{e}\n\nThe error has been logged above (select all to copy).")
        
    def start_extract(self):
        self.update_progress(0, "Extracting update...")
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
            self.temp_dir.mkdir(parents=True)
            
            self.log("Extracting archive...")
            with py7zr.SevenZipFile(self.archive_path, 'r') as archive:
                archive.extractall(self.temp_dir)
            
            self.update_progress(100, "Extraction complete")
            self.log("Extraction complete.")
            QTimer.singleShot(0, self.start_install)
        except Exception as e:
            self.log(f"ERROR: {e}")
            self.status_label.setText("Update Failed!")
            self.log_text.selectAll()
            QMessageBox.critical(self, "Update Failed", 
                                f"Extraction failed!\n\n{e}\n\nThe error has been logged above (select all to copy).")
            
    def start_install(self):
        try:
            if not self.temp_dir.exists():
                raise Exception(f"Temporary folder not found: {self.temp_dir}")
                
            items = list(self.temp_dir.iterdir())
            total = len(items)
            
            if total == 0:
                raise Exception("No files found in archive")
            
            for i, item in enumerate(items):
                pct = int((i + 1) / total * 100)
                self.update_progress(pct, f"Installing... {item.name}")
                
                if item.name in self.skip_files:
                    continue
                    
                dest = self.app_dir / item.name
                try:
                    if dest.exists():
                        if dest.is_dir():
                            shutil.rmtree(dest)
                        else:
                            dest.unlink()
                    if item.is_dir():
                        shutil.copytree(item, dest)
                    else:
                        shutil.copy2(item, dest)
                except PermissionError:
                    self.log(f"Skipped (in use): {item.name}")
                except Exception as e:
                    self.log(f"Note: {item.name} - {e}")
                    
            self.update_progress(100, "Update Complete!")
            self.log("Installation complete!")
            self.log_text.selectAll()
            self.launch_btn.show()
            self.close_btn.show()
        except Exception as e:
            self.log(f"ERROR: {e}")
            self.status_label.setText("Update Failed!")
            self.log_text.selectAll()
            QMessageBox.critical(self, "Update Failed", 
                                f"Installation failed!\n\n{e}\n\nThe error has been logged above (select all to copy).")
        
    def launch_app(self):
        exe_path = self.app_dir / "CrossWorlds Music Editor.exe"
        if exe_path.exists():
            os.startfile(str(exe_path))
        self.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: updater.py <download_url> <version>")
        sys.exit(1)
    
    download_url = sys.argv[1]
    new_version = sys.argv[2]
    
    app = QApplication(sys.argv)
    window = UpdaterUI(download_url, new_version)
    window.show()
    sys.exit(app.exec())