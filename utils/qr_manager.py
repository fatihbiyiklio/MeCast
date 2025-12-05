import socket
import secrets
import string
import qrcode
import io
import subprocess
import threading
from PyQt6.QtGui import QImage
from zeroconf import Zeroconf, ServiceInfo, ServiceBrowser, ServiceListener, IPVersion

class PairingListener(ServiceListener):
    def __init__(self, service_name, password, callback):
        self.service_name = service_name
        self.password = password
        self.callback = callback
        self.paired = False

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        if self.paired:
            return
        
        # Sadece bizim servis ismimizle başlayanları kabul et
        # Servis ismi genellikle "MeCast-XXXX._adb-tls-pairing._tcp.local." formatındadır
        if not name.startswith(self.service_name):
            print(f"Servis yoksayıldı (İsim uyuşmuyor): {name} != {self.service_name}")
            return
            
        info = zc.get_service_info(type_, name)
        if info:
            print(f"Servis bulundu: {name}, Info: {info}")
            self.pair(info)

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        pass

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        pass

    def pair(self, info):
        try:
            # IP adresini al
            addresses = info.ip_addresses_by_version(IPVersion.All)
            if not addresses:
                print("IP adresi bulunamadı.")
                return
            
            ip_address = addresses[0].exploded
            port = info.port
            
            print(f"Eşleştirme deneniyor: {ip_address}:{port} şifre: {self.password}")
            
            cmd = ["adb", "pair", f"{ip_address}:{port}", self.password]
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            stdout = process.stdout
            stderr = process.stderr
            print(f"ADB Çıktısı: {stdout}")
            print(f"ADB Hata: {stderr}")
            
            if "Successfully paired" in stdout:
                self.paired = True
                self.callback(True, f"Başarıyla eşleşti: {ip_address}")
            else:
                print("Eşleştirme başarısız, bekleniyor...")
                
        except Exception as e:
            print(f"Eşleştirme hatası: {e}")

class ConnectionListener(ServiceListener):
    def __init__(self, callback):
        self.callback = callback
        self.connected_ips = set()

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        if info:
            print(f"Bağlantı servisi bulundu: {name}, Info: {info}")
            self.connect(info)

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        pass

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        pass

    def connect(self, info):
        try:
            addresses = info.ip_addresses_by_version(IPVersion.All)
            if not addresses:
                return
            
            ip_address = addresses[0].exploded
            port = info.port
            
            if ip_address in self.connected_ips:
                return

            print(f"Bağlantı deneniyor: {ip_address}:{port}")
            
            cmd = ["adb", "connect", f"{ip_address}:{port}"]
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            stdout = process.stdout.strip()
            print(f"ADB Connect Çıktısı: {stdout}")
            
            if "connected to" in stdout:
                self.connected_ips.add(ip_address)
                self.callback(True, f"Cihaz bağlandı: {ip_address}")
                
        except Exception as e:
            print(f"Bağlantı hatası: {e}")

class QrManager:
    def __init__(self):
        self.zeroconf = Zeroconf()
        self.password = self._generate_password()
        self.service_name = f"MeCast-{secrets.token_hex(2)}"
        self.pairing_browser = None
        self.connection_browser = None

    def _generate_password(self):
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for i in range(10))

    def generate_qr_content(self):
        """
        ADB Wi-Fi eşleştirme için QR içeriğini üretir.
        Format: WIFI:T:ADB;S:name;P:password;;
        """
        print("QR içerik üretiliyor...")
        # QR Data Formatı: WIFI:T:ADB;S:name;P:password;;
        qr_data = f"WIFI:T:ADB;S:{self.service_name};P:{self.password};;"
        return qr_data

    def get_qr_image(self, data):
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # PIL Image -> QImage conversion via buffer
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qimg = QImage.fromData(buffer.getvalue())
        return qimg

    def wait_for_pairing(self):
        """
        Eşleştirme isteğini bekler.
        """
        self.pairing_event = threading.Event()
        self.pairing_result = (False, "Zaman aşımı")
        
        def pairing_callback(success, msg):
            if success:
                print(f"Eşleştirme başarılı ({msg}), bağlantı bekleniyor...")
                # Eşleşme başarılı olsa bile hemen dönme, bağlantıyı bekle
                # Ama UI'a bilgi vermek için belki bir sinyal? 
                # Şimdilik basit tutalım: Eşleşme olunca bağlantıyı da bekleyelim.
            else:
                self.pairing_result = (False, msg)
                self.pairing_event.set()

        def connection_callback(success, msg):
            if success:
                self.pairing_result = (True, msg)
                self.pairing_event.set()
            
        pairing_listener = PairingListener(self.service_name, self.password, pairing_callback)
        self.pairing_browser = ServiceBrowser(self.zeroconf, "_adb-tls-pairing._tcp.local.", pairing_listener)
        
        connection_listener = ConnectionListener(connection_callback)
        self.connection_browser = ServiceBrowser(self.zeroconf, "_adb-tls-connect._tcp.local.", connection_listener)
        
        print("Servisler aranıyor (Pairing & Connect)...")
        self.pairing_event.wait(timeout=60)
        
        self.close()
        return self.pairing_result
        
    def close(self):
        if self.pairing_browser:
            self.pairing_browser.cancel()
        if self.connection_browser:
            self.connection_browser.cancel()
        self.zeroconf.close()
