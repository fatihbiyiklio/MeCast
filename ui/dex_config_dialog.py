from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QComboBox, 
                             QCheckBox, QDialogButtonBox, QFormLayout, QSpinBox)

class DexConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DeX Modu Ayarları")
        self.setModal(True)
        self.resize(300, 200)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Çözünürlük Seçimi
        self.res_combo = QComboBox()
        self.res_combo.addItems(["1920x1080", "2560x1440", "1600x900", "1280x720"])
        self.res_combo.setCurrentIndex(0) # Varsayılan 1080p
        form_layout.addRow("Çözünürlük:", self.res_combo)
        
        # DPI Ayarı
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(100, 600)
        self.dpi_spin.setValue(160) # Varsayılan DPI
        self.dpi_spin.setSingleStep(10)
        form_layout.addRow("DPI (Ölçek):", self.dpi_spin)
        
        # Seçenekler
        self.fullscreen_cb = QCheckBox("Tam Ekran Başlat")
        layout.addWidget(self.fullscreen_cb)
        
        layout.addLayout(form_layout)
        
        # Butonlar
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def get_settings(self):
        return {
            "resolution": self.res_combo.currentText(),
            "dpi": self.dpi_spin.value(),
            "fullscreen": self.fullscreen_cb.isChecked()
        }
