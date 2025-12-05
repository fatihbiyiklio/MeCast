"""
iOS Receiver module for MeCast.
Handles iOS screen mirroring using uxplay (Linux) or uxplay-windows (Windows).
"""

import subprocess
import shutil
import threading
import time
import platform
import os

class IosReceiver:
    def __init__(self):
        self.process = None
        self.running = False
        self.os_type = platform.system().lower()

    def is_installed(self):
        """Check if uxplay is installed and available."""
        if self.os_type == 'linux':
            return shutil.which("uxplay") is not None
        elif self.os_type == 'windows':
            # Check common installation paths on Windows
            paths = [
                os.path.expanduser("~\\uxplay-windows\\uxplay.exe"),
                "C:\\Program Files\\uxplay\\uxplay.exe",
                "C:\\Program Files (x86)\\uxplay\\uxplay.exe",
                shutil.which("uxplay")  # Also check PATH
            ]
            return any(p and os.path.exists(p) for p in paths if p)
        return False

    def get_uxplay_path(self):
        """Get the path to uxplay executable."""
        if self.os_type == 'linux':
            return shutil.which("uxplay")
        elif self.os_type == 'windows':
            paths = [
                os.path.expanduser("~\\uxplay-windows\\uxplay.exe"),
                "C:\\Program Files\\uxplay\\uxplay.exe",
                "C:\\Program Files (x86)\\uxplay\\uxplay.exe",
            ]
            for p in paths:
                if os.path.exists(p):
                    return p
            return shutil.which("uxplay")
        return None

    def setup_firewall(self):
        """Setup firewall rules for AirPlay."""
        from utils.system_utils import open_firewall_ports
        return open_firewall_ports()

    def get_install_instructions(self):
        """Get installation instructions based on OS."""
        if self.os_type == 'linux':
            from utils.system_utils import get_uxplay_install_instructions_linux
            return {
                "type": "command",
                "message": "uxplay yüklü değil. Aşağıdaki komutu çalıştırın:",
                "command": get_uxplay_install_instructions_linux()
            }
        elif self.os_type == 'windows':
            return {
                "type": "steps",
                "message": "uxplay-windows kurulumu gerekli:",
                "steps": [
                    "1. Bonjour'u yükleyin: https://support.apple.com/kb/DL999",
                    "2. uxplay-windows indirin: https://github.com/leapbtw/uxplay-windows/releases",
                    "3. İndirilen dosyayı çıkartın ve uxplay.exe'yi çalıştırın"
                ]
            }
        return {"type": "error", "message": "Desteklenmeyen işletim sistemi"}

    def kill_existing(self):
        """Kill any existing uxplay processes."""
        if self.os_type == 'linux':
            subprocess.run(["pkill", "-f", "uxplay"], capture_output=True)
        elif self.os_type == 'windows':
            subprocess.run(["taskkill", "/F", "/IM", "uxplay.exe"], 
                         capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        time.sleep(0.5)

    def start(self):
        """Start the uxplay process."""
        if not self.is_installed():
            instructions = self.get_install_instructions()
            if instructions["type"] == "command":
                raise FileNotFoundError(
                    f"{instructions['message']}\n{instructions['command']}"
                )
            else:
                raise FileNotFoundError(
                    f"{instructions['message']}\n" + "\n".join(instructions.get('steps', []))
                )

        if self.running:
            return

        try:
            # Kill any existing instances
            self.kill_existing()
            
            # Setup firewall
            success, msg = self.setup_firewall()
            # We don't fail if firewall setup fails, just log it
            
            # Build command based on OS
            uxplay_path = self.get_uxplay_path()
            
            if self.os_type == 'linux':
                cmd = [uxplay_path, "-n", "MeCast", "-p", "7000"]
            elif self.os_type == 'windows':
                cmd = [uxplay_path, "-n", "MeCast", "-p", "7000"]
            else:
                raise OSError("Desteklenmeyen işletim sistemi")

            # Start the process
            if self.os_type == 'windows':
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            self.running = True
            
            # Start a thread to monitor the process
            threading.Thread(target=self._monitor_process, daemon=True).start()
            
        except Exception as e:
            self.running = False
            raise e

    def stop(self):
        """Stop the uxplay process."""
        if self.process and self.running:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.running = False
            self.process = None

    def _monitor_process(self):
        """Monitor the subprocess and update state if it exits."""
        if self.process:
            self.process.wait()
            self.running = False
