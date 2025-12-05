import subprocess
import shutil
import threading
import time

class IosReceiver:
    def __init__(self):
        self.process = None
        self.running = False

    def is_installed(self):
        """Check if uxplay is installed and available in PATH."""
        return shutil.which("uxplay") is not None

    def start(self):
        """Start the uxplay process."""
        if not self.is_installed():
            raise FileNotFoundError("uxplay is not installed. Please install it to use iOS mirroring.")

        if self.running:
            return

        try:
            # Start uxplay. 
            # -n MeCast sets the AirPlay name to MeCast
            # -nh prevents uxplay from hijacking the home directory (optional, but good for safety)
            # We might want to capture output for logging
            cmd = ["uxplay", "-n", "MeCast", "-p"] 
            
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
            # Here we could emit a signal if we were using QObject, 
            # but for now we just track state.
