import subprocess
import threading

class ScrcpyWrapper:
    def __init__(self):
        self.process = None

    def start_mirroring(self, serial, bitrate=None, max_size=None, stay_awake=True, new_display=None, turn_screen_off=False, fullscreen=False):
        """
        Belirtilen cihaz için scrcpy'yi başlatır.
        new_display: Örn "1920x1080/160" gibi bir çözünürlük/dpi stringi. DeX modu için kullanılır.
        """
        command = ['scrcpy', '--serial', serial]

        if new_display:
            # Argümanı tek bir string olarak --new-display=VALUE formatında geçiyoruz
            # Bazı scrcpy sürümleri veya ortamlar boşluklu argümanı yanlış yorumlayabilir
            command.append(f'--new-display={new_display}')
            # DeX modunda genellikle tam ekran veya daha büyük bir pencere istenir
            command.extend(['--window-title', f'MeCast DeX - {serial}'])
        else:
            command.extend(['--window-title', f'MeCast - {serial}'])

        if bitrate:
            command.extend(['--video-bit-rate', str(bitrate)])
        
        if max_size and not new_display: # new_display ile max-size çakışabilir veya gereksiz olabilir
            command.extend(['--max-size', str(max_size)])
            
        if stay_awake:
            command.append('--stay-awake')
            
        if turn_screen_off:
            command.append('--turn-screen-off')
            
        if fullscreen:
            command.append('--fullscreen')

        try:
            # Debug için komutu yazdır
            print(f"Çalıştırılan komut: {' '.join(command)}")
            
            # scrcpy'yi ayrı bir işlem olarak başlat
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Kısa bir süre bekle ve işlemin hemen kapanıp kapanmadığını kontrol et
            try:
                stdout, stderr = self.process.communicate(timeout=1)
                if self.process.returncode != 0:
                    return False, f"Scrcpy başlatılamadı:\n{stderr}"
            except subprocess.TimeoutExpired:
                # İşlem 1 saniye içinde kapanmadıysa muhtemelen başarıyla çalışıyordur
                # Ancak stderr'i okumaya devam etmek için ayrı bir thread gerekebilir
                # Şimdilik başarılı varsayıyoruz
                pass

            return True, "Yansıtma başlatıldı."
        except FileNotFoundError:
            return False, "scrcpy bulunamadı. Lütfen yüklü olduğundan emin olun."
        except Exception as e:
            return False, f"Hata oluştu: {str(e)}"

    def stop_mirroring(self):
        if self.process:
            self.process.terminate()
            self.process = None
