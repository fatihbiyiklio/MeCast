# MeCast

MeCast, Android ve iOS cihaz ekranınızı bilgisayarınıza yansıtmanızı sağlayan, modern bir masaüstü uygulamasıdır.

## 🚀 Özellikler

### Android
- **Kablosuz Bağlantı:** QR kod ile kolayca eşleştirme
- **Kablolu Bağlantı:** USB üzerinden hızlı bağlantı
- **DeX Modu:** Sanal ikinci ekran (Android 10+)
- **Ekran Kontrolü:** Fare ve klavye ile tam kontrol
- **Ekranı Kapatma:** Yansıtma sırasında telefon ekranını karartma

### iOS (Yeni!)
- **AirPlay Desteği:** iPhone/iPad ekranını yansıtma
- **Otomatik Kurulum:** Firewall port yönetimi dahil
- **Cross-Platform:** Linux ve Windows desteği

## 📋 Gereksinimler

### Sistem
- Linux veya Windows
- Python 3.10+

### Android için
- `adb` (Android Debug Bridge)
- `scrcpy`

### iOS için
| Platform | Gereksinimler |
|----------|---------------|
| Linux | `uxplay` |
| Windows | [Bonjour](https://support.apple.com/kb/DL999) + [uxplay-windows](https://github.com/leapbtw/uxplay-windows/releases) |

## 📦 Kurulum

### Hızlı Başlangıç (Linux)
```bash
git clone https://github.com/kullaniciadi/MeCast.git
cd MeCast
./install.sh
```

### Manuel Kurulum
```bash
# Sanal ortam oluştur
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Çalıştır
python main.py
```

### Sistem Bağımlılıkları
```bash
# Debian/Ubuntu
sudo apt install adb scrcpy uxplay

# Fedora
sudo dnf install android-tools scrcpy uxplay

# Arch
sudo pacman -S android-tools scrcpy uxplay
```

## 🏗️ Derleme

### AppImage (Linux)
```bash
./build_appimage.sh
# Çıktı: MeCast-x86_64.AppImage
```

### Windows EXE
```bash
pyinstaller build_windows.spec
```

## 🎯 Kullanım

1. Uygulamayı başlatın
2. **Android** veya **iOS** seçin
3. Cihazınızı bağlayın:
   - **Android:** QR kod ile eşleştirin veya USB bağlayın
   - **iOS:** Ekran Yansıtma > MeCast

## 📁 Proje Yapısı

```
MeCast/
├── main.py              # Ana giriş noktası
├── ui/                  # Kullanıcı arayüzü
│   ├── main_window.py
│   ├── device_selection.py
│   └── ios_setup_dialog.py
├── receivers/           # Yansıtma mantığı
│   └── ios_receiver.py
├── utils/               # Yardımcı araçlar
│   └── system_utils.py  # Firewall yönetimi
└── build_appimage.sh    # AppImage derleyici
```

## 📄 Lisans
MIT
