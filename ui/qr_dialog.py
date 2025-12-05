from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                             QProgressBar, QMessageBox)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from utils.qr_manager import QrManager

class QrWorker(QThread):
    qr_ready = pyqtSignal(object)
    pairing_success = pyqtSignal(str)
    pairing_error = pyqtSignal(str)

    def __init__(self, qr_manager):
        super().__init__()
        self.qr_manager = qr_manager

    def run(self):
        try:
            print("QrWorker: Başlıyor...")
            # QR içeriğini oluştur
            data = self.qr_manager.generate_qr_content()
            print("QrWorker: QR içerik üretildi.")
            
            img = self.qr_manager.get_qr_image(data)
            print("QrWorker: QR resim üretildi.")
            
            self.qr_ready.emit(img)
            print("QrWorker: QR sinyali gönderildi.")
            
            # Eşleştirmeyi bekle
            print("QrWorker: Eşleştirme bekleniyor...")
            success, msg = self.qr_manager.wait_for_pairing()
            print(f"QrWorker: Eşleştirme bitti. Durum: {success}, Mesaj: {msg}")
            
            if success:
                self.pairing_success.emit(msg)
            else:
                self.pairing_error.emit(msg)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"QrWorker Hata: {e}")
            self.pairing_error.emit(str(e))

class QrDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("QR ile Wi-Fi Eşleştirme")
        self.setModal(True)
        self.resize(400, 500)
        
        self.qr_manager = QrManager()
        self.worker = None
        
        self.init_ui()
        self.start_pairing_process()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        info_label = QLabel("Telefonunuzdan:\nAyarlar > Geliştirici Seçenekleri > Kablosuz Hata Ayıklama\nmenüsüne gidin ve 'QR kodu ile cihaz eşle' seçeneğini seçin.")
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        
        self.qr_label = QLabel("QR Kod Oluşturuluyor...")
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_label.setMinimumSize(300, 300)
        self.qr_label.setStyleSheet("border: 1px solid #ccc; background-color: white;")
        layout.addWidget(self.qr_label)
        
        self.status_label = QLabel("Bekleniyor...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 0) # Indeterminate
        layout.addWidget(self.progress)
        
        close_btn = QPushButton("İptal")
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)

    def start_pairing_process(self):
        self.worker = QrWorker(self.qr_manager)
        self.worker.qr_ready.connect(self.show_qr)
        self.worker.pairing_success.connect(self.on_success)
        self.worker.pairing_error.connect(self.on_error)
        self.worker.start()

    def show_qr(self, img):
        pixmap = QPixmap.fromImage(img)
        self.qr_label.setPixmap(pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio))
        self.qr_label.setText("")
        self.status_label.setText("QR Kodu Taratın...")

    def on_success(self, msg):
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.status_label.setText("Eşleştirme Başarılı!")
        QMessageBox.information(self, "Başarılı", f"Cihaz eşleşti: {msg}")
        self.accept()

    def on_error(self, msg):
        self.progress.setRange(0, 100)
        self.status_label.setText("Hata Oluştu")
        QMessageBox.critical(self, "Hata", f"Eşleştirme başarısız: {msg}")
        self.reject()
    
    def reject(self):
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
        self.qr_manager.close()
        super().reject()

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.terminate() # Güvenli değil ama örnek için yeterli
        self.qr_manager.close()
        event.accept()
