"""
iOS Setup Dialog for MeCast.
Handles dependency checks and setup instructions for iOS mirroring.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QMessageBox, QTextEdit, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import platform


class FirewallSetupThread(QThread):
    """Thread for setting up firewall rules."""
    finished = pyqtSignal(bool, str)
    
    def run(self):
        try:
            from utils.system_utils import open_firewall_ports
            success, message = open_firewall_ports()
            self.finished.emit(success, message)
        except Exception as e:
            self.finished.emit(False, str(e))


class IosSetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MeCast - iOS Kurulumu")
        self.setFixedSize(550, 400)
        self.setup_complete = False
        
        self.init_ui()
        self.check_dependencies()
        self.apply_styles()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        # Header
        title = QLabel("iOS Yansıtma Kurulumu")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("header")
        layout.addWidget(title)

        # Status area
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setObjectName("status_area")
        layout.addWidget(self.status_text)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.btn_firewall = QPushButton("Firewall Ayarla")
        self.btn_firewall.clicked.connect(self.setup_firewall)
        self.btn_firewall.setEnabled(False)
        buttons_layout.addWidget(self.btn_firewall)
        
        self.btn_start = QPushButton("Başlat")
        self.btn_start.clicked.connect(self.start_mirroring)
        self.btn_start.setEnabled(False)
        self.btn_start.setObjectName("primary_btn")
        buttons_layout.addWidget(self.btn_start)
        
        self.btn_cancel = QPushButton("İptal")
        self.btn_cancel.clicked.connect(self.reject)
        buttons_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(buttons_layout)

    def check_dependencies(self):
        """Check all dependencies for iOS mirroring."""
        self.status_text.clear()
        os_type = platform.system().lower()
        
        self.log(f"🖥️ İşletim Sistemi: {platform.system()}")
        self.log("")
        
        from receivers.ios_receiver import IosReceiver
        receiver = IosReceiver()
        
        if receiver.is_installed():
            self.log("✅ uxplay kurulu")
            self.btn_firewall.setEnabled(True)
            self.btn_start.setEnabled(True)
            self.setup_complete = True
        else:
            self.log("❌ uxplay kurulu değil")
            self.log("")
            
            instructions = receiver.get_install_instructions()
            if instructions["type"] == "command":
                self.log(instructions["message"])
                self.log("")
                self.log(f"📋 Komut: {instructions['command']}")
            else:
                self.log(instructions["message"])
                self.log("")
                for step in instructions.get("steps", []):
                    self.log(step)
        
        self.log("")
        self.log("ℹ️ Firewall portlarının açık olması gerekiyor (7000-7002, 5353)")

    def log(self, message):
        """Add a log message to the status area."""
        self.status_text.append(message)

    def setup_firewall(self):
        """Setup firewall rules."""
        self.btn_firewall.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)  # Indeterminate
        
        self.log("")
        self.log("🔧 Firewall ayarlanıyor...")
        
        self.firewall_thread = FirewallSetupThread()
        self.firewall_thread.finished.connect(self.on_firewall_setup_complete)
        self.firewall_thread.start()

    def on_firewall_setup_complete(self, success, message):
        """Handle firewall setup completion."""
        self.progress.setVisible(False)
        self.btn_firewall.setEnabled(True)
        
        if success:
            self.log(f"✅ {message}")
        else:
            self.log(f"⚠️ {message}")
            self.log("ℹ️ Manuel olarak portları açmanız gerekebilir.")

    def start_mirroring(self):
        """Start iOS mirroring."""
        self.accept()

    def apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
            }
            QLabel#header {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
            }
            QTextEdit#status_area {
                background-color: white;
                border: 1px solid #dcdde1;
                border-radius: 8px;
                padding: 10px;
                font-family: monospace;
                font-size: 12px;
            }
            QPushButton {
                background-color: white;
                border: 2px solid #dcdde1;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
            }
            QPushButton:hover {
                border-color: #3498db;
                background-color: #ebf5fb;
            }
            QPushButton:disabled {
                background-color: #ecf0f1;
                color: #95a5a6;
            }
            QPushButton#primary_btn {
                background-color: #3498db;
                border-color: #3498db;
                color: white;
            }
            QPushButton#primary_btn:hover {
                background-color: #2980b9;
            }
            QProgressBar {
                border: 1px solid #dcdde1;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)
