import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Device Selection
    from ui.device_selection import DeviceSelectionDialog
    selection_dialog = DeviceSelectionDialog()
    
    if selection_dialog.exec():
        mode = selection_dialog.selected_mode
        
        if mode == 'android':
            window = MainWindow()
            window.show()
            sys.exit(app.exec())
            
        elif mode == 'ios':
            from ui.ios_setup_dialog import IosSetupDialog
            from receivers.ios_receiver import IosReceiver
            from PyQt6.QtWidgets import QMessageBox
            
            # Show setup dialog first
            setup_dialog = IosSetupDialog()
            
            if setup_dialog.exec():
                receiver = IosReceiver()
                try:
                    receiver.start()
                    
                    # Show a simple dialog while mirroring is active
                    msg = QMessageBox()
                    msg.setWindowTitle("MeCast - iOS Mirroring")
                    msg.setText("iOS Mirroring Başlatıldı.\n\nLütfen iOS cihazınızdan Ekran Yansıtma menüsünü açın ve 'MeCast'i seçin.\n\nDurdurmak için bu pencereyi kapatın veya Tamam'a basın.")
                    msg.setIcon(QMessageBox.Icon.Information)
                    msg.exec()
                    
                    receiver.stop()
                    
                except FileNotFoundError as e:
                    QMessageBox.critical(None, "Hata", str(e))
                except Exception as e:
                    QMessageBox.critical(None, "Hata", f"Bir hata oluştu: {str(e)}")
                
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
