from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QMessageBox, QWidget)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont

class DeviceSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MeCast - Cihaz Seçimi")
        self.setFixedSize(500, 350)
        self.selected_mode = None # 'android' or 'ios'
        
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Header
        title = QLabel("Lütfen Cihaz Türünü Seçin")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("header")
        layout.addWidget(title)

        # Buttons Container
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(30)

        # Android Button
        self.btn_android = self.create_device_button("Android", "android_icon")
        self.btn_android.clicked.connect(lambda: self.select_device("android"))
        buttons_layout.addWidget(self.btn_android)

        # iOS Button
        self.btn_ios = self.create_device_button("iOS", "ios_icon")
        self.btn_ios.clicked.connect(lambda: self.select_device("ios"))
        buttons_layout.addWidget(self.btn_ios)

        layout.addLayout(buttons_layout)

        # Info Text
        info = QLabel("Devam etmek için bir platform seçin")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setObjectName("info")
        layout.addWidget(info)

    def create_device_button(self, text, icon_name):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setFixedSize(180, 150)
        btn.setObjectName("device_btn")
        # Icon handling could be added here if we had specific icons
        return btn

    def select_device(self, mode):
        self.selected_mode = mode
        self.accept()

    def apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
            }
            QLabel#header {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
            }
            QLabel#info {
                font-size: 14px;
                color: #7f8c8d;
            }
            QPushButton#device_btn {
                background-color: white;
                border: 2px solid #dcdde1;
                border-radius: 15px;
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
            }
            QPushButton#device_btn:hover {
                border-color: #3498db;
                background-color: #ebf5fb;
            }
            QPushButton#device_btn:pressed {
                background-color: #d6eaf8;
            }
        """)
