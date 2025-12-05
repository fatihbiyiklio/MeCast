import subprocess
import re

class AdbManager:
    @staticmethod
    def get_devices():
        """
        Bağlı ADB cihazlarını listeler.
        Returns:
            list: Cihaz seri numaraları ve durumlarını içeren sözlük listesi.
                  Örnek: [{'serial': '123456', 'status': 'device', 'model': 'Pixel_6'}]
        """
        try:
            # adb devices -l komutunu çalıştır (timeout eklendi)
            result = subprocess.run(['adb', 'devices', '-l'], capture_output=True, text=True, timeout=5)
            output = result.stdout.strip().split('\n')
            
            devices = []
            # İlk satır genellikle "List of devices attached" olur, onu atla
            for line in output[1:]:
                if not line.strip():
                    continue
                
                # Örnek satır: "SERIAL_NO device product:model model:Pixel_6 device:oriole transport_id:1"
                parts = line.split()
                if len(parts) >= 2:
                    serial = parts[0]
                    status = parts[1]
                    
                    model = "Unknown"
                    for part in parts:
                        if part.startswith("model:"):
                            model = part.split(":")[1]
                    
                    devices.append({
                        'serial': serial,
                        'status': status,
                        'model': model
                    })
            return devices
        except FileNotFoundError:
            return []
        except subprocess.TimeoutExpired:
            print("ADB zaman aşımına uğradı.")
            return []
        except Exception as e:
            print(f"ADB Hatası: {e}")
            return []

    @staticmethod
    def is_adb_installed():
        try:
            subprocess.run(['adb', '--version'], capture_output=True)
            return True
        except FileNotFoundError:
            return False
