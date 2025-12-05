import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QListWidget, QMessageBox, 
                             QComboBox, QGroupBox, QCheckBox)
from PyQt6.QtCore import QTimer, Qt
from utils.adb_manager import AdbManager
from receivers.scrcpy_wrapper import ScrcpyWrapper
from ui.dex_config_dialog import DexConfigDialog
from ui.qr_dialog import QrDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MeCast - Telefon Yansıtıcı")
        self.setMinimumSize(500, 400)
        
        self.adb_manager = AdbManager()
        self.scrcpy = ScrcpyWrapper()
        
        self.init_ui()
        
        # Cihazları periyodik olarak kontrol et
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_devices)
        self.timer.start(2000) # 2 saniyede bir
        
        self.refresh_devices()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Başlık
        title_label = QLabel("MeCast")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Cihaz Listesi Grubu
        device_group = QGroupBox("Bağlı Cihazlar")
        device_layout = QVBoxLayout()
        
        self.device_list = QListWidget()
        device_layout.addWidget(self.device_list)
        
        refresh_btn = QPushButton("Listeyi Yenile")
        refresh_btn.clicked.connect(self.refresh_devices)
        device_layout.addWidget(refresh_btn)
        
        qr_btn = QPushButton("QR ile Bağla (Wi-Fi)")
        qr_btn.clicked.connect(self.open_qr_dialog)
        device_layout.addWidget(qr_btn)
        
        device_group.setLayout(device_layout)
        layout.addWidget(device_group)
        
        # Ayarlar Grubu
        settings_group = QGroupBox("Yansıtma Ayarları")
        settings_layout = QHBoxLayout()
        
        settings_layout.addWidget(QLabel("Bitrate:"))
        self.bitrate_combo = QComboBox()
        self.bitrate_combo.addItems(["Varsayılan", "2M", "4M", "8M", "16M"])
        settings_layout.addWidget(self.bitrate_combo)
        
        settings_layout.addWidget(QLabel("Çözünürlük:"))
        self.res_combo = QComboBox()
        self.res_combo.addItems(["Varsayılan", "720", "1080"])
        settings_layout.addWidget(self.res_combo)
        
        self.screen_off_check = QCheckBox("Ekranı Kapat")
        settings_layout.addWidget(self.screen_off_check)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Kontrol Butonları
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Yansıtmayı Başlat")
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        self.start_btn.clicked.connect(lambda: self.start_mirroring(dex_mode=False))
        btn_layout.addWidget(self.start_btn)

        self.dex_btn = QPushButton("DeX Modu Başlat")
        self.dex_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 10px;")
        self.dex_btn.clicked.connect(lambda: self.start_mirroring(dex_mode=True))
        btn_layout.addWidget(self.dex_btn)
        
        self.stop_btn = QPushButton("Durdur")
        self.stop_btn.setStyleSheet("background-color: #f44336; color: white; padding: 10px;")
        self.stop_btn.clicked.connect(self.stop_mirroring)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_btn)
        
        layout.addLayout(btn_layout)
        
        # Durum Çubuğu
        self.statusBar().showMessage("Hazır")

    def refresh_devices(self):
        if not self.adb_manager.is_adb_installed():
            self.statusBar().showMessage("Hata: ADB yüklü değil!")
            return

        devices = self.adb_manager.get_devices()
        current_row = self.device_list.currentRow()
        
        self.device_list.clear()
        for device in devices:
            item_text = f"{device['model']} ({device['serial']}) - {device['status']}"
            self.device_list.addItem(item_text)
            
        if self.device_list.count() > 0:
            if current_row >= 0 and current_row < self.device_list.count():
                self.device_list.setCurrentRow(current_row)
            else:
                self.device_list.setCurrentRow(0)
        
        self.statusBar().showMessage(f"{len(devices)} cihaz bulundu.")

    def open_qr_dialog(self):
        dialog = QrDialog(self)
        dialog.exec()
        self.refresh_devices()

    def start_mirroring(self, dex_mode=False):
        current_item = self.device_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir cihaz seçin.")
            return
            
        # Seçili metinden seri numarasını ayıkla (basitçe parantez içini al)
        text = current_item.text()
        try:
            serial = text.split('(')[1].split(')')[0]
        except IndexError:
            QMessageBox.critical(self, "Hata", "Seri numarası alınamadı.")
            return

        bitrate = self.bitrate_combo.currentText()
        if bitrate == "Varsayılan":
            bitrate = None
            
        max_size = self.res_combo.currentText()
        if max_size == "Varsayılan":
            max_size = None

        new_display = None
        fullscreen = False
        
        # Her iki mod için de ekran kapatma ayarını ana pencereden al
        turn_screen_off = self.screen_off_check.isChecked()

        if dex_mode:
            dialog = DexConfigDialog(self)
            if dialog.exec():
                settings = dialog.get_settings()
                # Çözünürlük ve DPI birleştiriliyor: 1920x1080/160
                new_display = f"{settings['resolution']}/{settings['dpi']}"
                fullscreen = settings['fullscreen']
            else:
                return # Kullanıcı iptal etti

        success, message = self.scrcpy.start_mirroring(
            serial, 
            bitrate, 
            max_size, 
            new_display=new_display,
            turn_screen_off=turn_screen_off,
            fullscreen=fullscreen
        )
        
        if success:
            mode_text = "DeX Modu" if dex_mode else "Yansıtma"
            self.statusBar().showMessage(f"{mode_text} başlatıldı: {serial}")
            self.start_btn.setEnabled(False)
            self.dex_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
        else:
            QMessageBox.critical(self, "Hata", message)

    def stop_mirroring(self):
        self.scrcpy.stop_mirroring()
        self.statusBar().showMessage("Yansıtma durduruldu.")
        self.start_btn.setEnabled(True)
        self.dex_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
