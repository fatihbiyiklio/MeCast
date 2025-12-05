# Windows İçin Derleme (Build) Rehberi

Bu projeyi Windows üzerinde `.exe` olarak derlemek için aşağıdaki adımları takip edin. Bu işlem Linux üzerinde **yapılamaz**, bir Windows bilgisayar gerektirir.

## 1. Hazırlık
1. Proje klasörünü Windows bilgisayarınıza kopyalayın.
2. Bilgisayarınızda Python'un yüklü olduğundan emin olun. (Yüklü değilse [python.org](https://www.python.org/) adresinden indirin).
3. Kurulum sırasında "Add Python to PATH" seçeneğini işaretlemeyi unutmayın.

## 2. Kurulum
Proje klasöründe bir komut satırı (CMD veya PowerShell) açın ve şu komutları sırasıyla girin:

```powershell
# Sanal ortam oluşturma (Opsiyonel ama önerilir)
python -m venv venv

# Sanal ortamı aktif etme
.\venv\Scripts\activate

# Gerekli kütüphaneleri yükleme
pip install -r requirements.txt

# PyInstaller'ı yükleme
pip install pyinstaller
```

## 3. Derleme (.exe Oluşturma)
Hazırladığım `build_windows.spec` dosyasını kullanarak derleme işlemini başlatın:

```powershell
pyinstaller build_windows.spec
```

## 4. Sonuç
İşlem tamamlandığında:
- `dist` klasörü içinde `MeCast.exe` dosyasını bulacaksınız.
- Bu dosyayı `ui`, `utils` ve `receivers` klasörleriyle birlikte taşımanıza gerek yoktur, her şey tek bir dosya içine gömülmüştür.
