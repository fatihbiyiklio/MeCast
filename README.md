# MeCast

MeCast, Android cihaz ekranınızı bilgisayarınıza yansıtmanızı ve kontrol etmenizi sağlayan, `scrcpy` tabanlı modern bir masaüstü uygulamasıdır.

## Özellikler

- **Kablosuz Bağlantı:** QR kod ile kolayca eşleştirme ve otomatik bağlanma.
- **Kablolu Bağlantı:** USB üzerinden hızlı bağlantı.
- **DeX Modu:** Sanal ikinci ekran oluşturarak masaüstü deneyimi (Android 10+).
- **Ekran Kontrolü:** Fare ve klavye ile tam kontrol.
- **Ekranı Kapatma:** Yansıtma sırasında telefon ekranını karartma seçeneği.

## Gereksinimler

- **Sistem:** Linux veya Windows
- **Yazılım:** 
    - `adb` (Android Debug Bridge)
    - `scrcpy` (Ekran yansıtma için)
    - Python 3.10+

## Kurulum

1. Repoyu klonlayın:
   ```bash
   git clone https://github.com/kullaniciadi/MeCast.git
   cd MeCast
   ```

2. Sanal ortam oluşturun ve bağımlılıkları yükleyin:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Uygulamayı çalıştırın:
   ```bash
   python main.py
   ```

## Derleme (Build)

### Linux
```bash
pyinstaller --onefile --windowed --name MeCast --add-data "ui:ui" --add-data "utils:utils" --add-data "receivers:receivers" main.py
```

### Windows
Windows üzerinde `pyinstaller` kullanarak benzer komutla .exe oluşturabilirsiniz.

## Lisans
MIT
