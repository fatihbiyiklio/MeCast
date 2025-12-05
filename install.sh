#!/bin/bash

echo "MeCast Kurulum Sihirbazına Hoş Geldiniz!"
echo "----------------------------------------"

# 1. Python Kontrolü
if ! command -v python3 &> /dev/null; then
    echo "Hata: Python 3 bulunamadı. Lütfen önce Python 3 yükleyin."
    exit 1
fi

# 2. ADB ve Scrcpy Kontrolü
MISSING_TOOLS=0
if ! command -v adb &> /dev/null; then
    echo "Uyarı: 'adb' bulunamadı. Lütfen 'android-tools-adb' veya benzeri paketi yükleyin."
    MISSING_TOOLS=1
fi

if ! command -v scrcpy &> /dev/null; then
    echo "Uyarı: 'scrcpy' bulunamadı. Android ekran yansıtma için gereklidir."
    echo "Yüklemek için: sudo apt install scrcpy (Debian/Ubuntu) veya paket yöneticinizi kullanın."
    MISSING_TOOLS=1
fi

if ! command -v uxplay &> /dev/null; then
    echo "Uyarı: 'uxplay' bulunamadı. iOS ekran yansıtma için gereklidir."
    echo "Yüklemek için: sudo apt install uxplay (Debian/Ubuntu) veya paket yöneticinizi kullanın."
    # uxplay opsiyonel olabilir, bu yüzden MISSING_TOOLS'u 1 yapmıyoruz veya kullanıcıya soruyoruz.
    # Ancak tam deneyim için uyaralım.
fi

if [ $MISSING_TOOLS -eq 1 ]; then
    read -p "Bazı araçlar eksik. Yine de devam etmek istiyor musunuz? (e/h): " choice
    case "$choice" in 
      e|E ) echo "Devam ediliyor...";;
      * ) echo "Kurulum iptal edildi."; exit 1;;
    esac
fi

# 3. Sanal Ortam Oluşturma
echo "Sanal ortam (venv) oluşturuluyor..."
python3 -m venv venv

# 4. Bağımlılıkları Yükleme
echo "Bağımlılıklar yükleniyor..."
source venv/bin/activate
pip install -r requirements.txt

# 5. Masaüstü Kısayolu Oluşturma
echo "Masaüstü kısayolu oluşturuluyor..."
CURRENT_DIR=$(pwd)
ICON_PATH="$CURRENT_DIR/ui/icon.png" # İkon varsa, yoksa varsayılan kalır

# İkon dosyası kontrolü (yoksa basit bir kontrol)
if [ ! -f "$ICON_PATH" ]; then
    ICON_PATH="utilities-terminal" # Varsayılan sistem ikonu
fi

cat > MeCast.desktop <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=MeCast
Comment=Android Ekran Yansıtma Aracı
Exec=$CURRENT_DIR/venv/bin/python $CURRENT_DIR/main.py
Icon=$ICON_PATH
Path=$CURRENT_DIR
Terminal=false
Categories=Utility;
EOF

chmod +x MeCast.desktop

# Kısayolu uygulamalar menüsüne kopyalama (Opsiyonel)
read -p "Uygulama menüsüne kısayol eklensin mi? (e/h): " add_menu
if [[ "$add_menu" =~ ^[eE]$ ]]; then
    mkdir -p ~/.local/share/applications
    cp MeCast.desktop ~/.local/share/applications/
    echo "Kısayol menüye eklendi."
fi

echo "----------------------------------------"
echo "Kurulum Tamamlandı!"
echo "Masaüstündeki 'MeCast.desktop' dosyasına çift tıklayarak veya terminalden 'python main.py' yazarak başlatabilirsiniz."
