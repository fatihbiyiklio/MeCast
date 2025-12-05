"""
Cross-platform system utilities for MeCast.
Handles firewall configuration and dependency checks.
"""

import subprocess
import shutil
import platform
import os

def get_os():
    """Return 'linux', 'windows', or 'darwin' (macOS)."""
    system = platform.system().lower()
    if system == 'linux':
        return 'linux'
    elif system == 'windows':
        return 'windows'
    elif system == 'darwin':
        return 'darwin'
    return 'unknown'

# ============== Firewall Management ==============

def open_firewall_ports_linux():
    """Open required ports for AirPlay on Linux using ufw or iptables."""
    ports_tcp = [7000, 7001, 7002]
    ports_udp = [7000, 7001, 7002, 5353]  # 5353 for mDNS
    
    # Check if ufw is available
    if shutil.which("ufw"):
        try:
            # Check if ufw is active
            result = subprocess.run(["ufw", "status"], capture_output=True, text=True)
            if "inactive" in result.stdout.lower():
                return True, "Firewall (ufw) inactive - no changes needed"
            
            # Open TCP ports
            for port in ports_tcp:
                subprocess.run(["sudo", "ufw", "allow", f"{port}/tcp"], 
                             capture_output=True, check=False)
            
            # Open UDP ports
            for port in ports_udp:
                subprocess.run(["sudo", "ufw", "allow", f"{port}/udp"], 
                             capture_output=True, check=False)
            
            return True, "Firewall ports opened successfully (ufw)"
        except Exception as e:
            return False, f"Failed to configure ufw: {str(e)}"
    
    # Fall back to iptables
    elif shutil.which("iptables"):
        try:
            for port in ports_tcp:
                subprocess.run(["sudo", "iptables", "-A", "INPUT", "-p", "tcp", 
                              "--dport", str(port), "-j", "ACCEPT"], 
                             capture_output=True, check=False)
            
            for port in ports_udp:
                subprocess.run(["sudo", "iptables", "-A", "INPUT", "-p", "udp", 
                              "--dport", str(port), "-j", "ACCEPT"], 
                             capture_output=True, check=False)
            
            return True, "Firewall ports opened successfully (iptables)"
        except Exception as e:
            return False, f"Failed to configure iptables: {str(e)}"
    
    return False, "No supported firewall found (ufw or iptables)"


def open_firewall_ports_windows():
    """Open required ports for AirPlay on Windows using netsh."""
    ports = [7000, 7001, 7002, 5353]
    
    try:
        # Create firewall rules
        for port in ports:
            # TCP rule
            subprocess.run([
                "netsh", "advfirewall", "firewall", "add", "rule",
                f"name=MeCast_TCP_{port}",
                "dir=in", "action=allow", "protocol=tcp",
                f"localport={port}"
            ], capture_output=True, check=False)
            
            # UDP rule
            subprocess.run([
                "netsh", "advfirewall", "firewall", "add", "rule",
                f"name=MeCast_UDP_{port}",
                "dir=in", "action=allow", "protocol=udp",
                f"localport={port}"
            ], capture_output=True, check=False)
        
        return True, "Firewall rules added successfully"
    except Exception as e:
        return False, f"Failed to configure Windows Firewall: {str(e)}"


def open_firewall_ports():
    """Open required firewall ports for the current OS."""
    os_type = get_os()
    
    if os_type == 'linux':
        return open_firewall_ports_linux()
    elif os_type == 'windows':
        return open_firewall_ports_windows()
    else:
        return False, f"Unsupported OS: {os_type}"


# ============== Dependency Checks ==============

def check_uxplay_linux():
    """Check if uxplay is installed on Linux."""
    return shutil.which("uxplay") is not None


def get_uxplay_install_instructions_linux():
    """Get installation instructions for uxplay on Linux."""
    # Detect distribution
    if os.path.exists("/etc/debian_version"):
        return "sudo apt update && sudo apt install uxplay"
    elif os.path.exists("/etc/fedora-release"):
        return "sudo dnf install uxplay"
    elif os.path.exists("/etc/arch-release"):
        return "sudo pacman -S uxplay"
    else:
        return "Please install uxplay using your package manager"


def check_bonjour_windows():
    """Check if Bonjour is installed on Windows (required for uxplay)."""
    # Check if Bonjour service exists
    try:
        result = subprocess.run(
            ["sc", "query", "Bonjour Service"],
            capture_output=True, text=True
        )
        return "RUNNING" in result.stdout or "STOPPED" in result.stdout
    except:
        return False


def get_uxplay_windows_info():
    """Get info about uxplay-windows setup."""
    return {
        "download_url": "https://github.com/leapbtw/uxplay-windows/releases",
        "bonjour_url": "https://support.apple.com/kb/DL999",
        "instructions": [
            "1. Download and install Bonjour from Apple (required)",
            "2. Download uxplay-windows from GitHub releases",
            "3. Extract and run uxplay.exe"
        ]
    }


def check_ios_dependencies():
    """Check all iOS mirroring dependencies for the current OS."""
    os_type = get_os()
    
    if os_type == 'linux':
        uxplay_installed = check_uxplay_linux()
        return {
            "os": "linux",
            "uxplay_installed": uxplay_installed,
            "install_cmd": get_uxplay_install_instructions_linux() if not uxplay_installed else None,
            "ready": uxplay_installed
        }
    elif os_type == 'windows':
        bonjour_installed = check_bonjour_windows()
        # Check if uxplay.exe exists in common locations
        uxplay_paths = [
            os.path.expanduser("~\\uxplay-windows\\uxplay.exe"),
            "C:\\Program Files\\uxplay\\uxplay.exe",
            "C:\\Program Files (x86)\\uxplay\\uxplay.exe"
        ]
        uxplay_installed = any(os.path.exists(p) for p in uxplay_paths)
        
        return {
            "os": "windows",
            "bonjour_installed": bonjour_installed,
            "uxplay_installed": uxplay_installed,
            "setup_info": get_uxplay_windows_info(),
            "ready": bonjour_installed and uxplay_installed
        }
    
    return {"os": os_type, "ready": False, "error": "Unsupported OS"}
