import subprocess
import sys
import os
import time

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_EXE = sys.executable
IS_WINDOWS = sys.platform.startswith('win')

print("=" * 60)
print("   mPython Virtual Board - One-Click Launch")
print("=" * 60)

# Windows: use CREATE_NO_WINDOW flag; Unix: no flags
creation_flags = 0
if IS_WINDOWS:
    creation_flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)

print("\n🔌 Starting VM Server (port 7778)...")
vm_server_path = os.path.join(PROJECT_DIR, 'vm_server.py')
server_proc = subprocess.Popen([PYTHON_EXE, vm_server_path], creationflags=creation_flags)
time.sleep(2)

print("\n🔌 Starting Virtual USB Service (port 7777)...")
virtual_usb_path = os.path.join(PROJECT_DIR, 'simulator', 'modules', 'virtual_usb.py')
usb_proc = subprocess.Popen(
    [PYTHON_EXE, '-c',
     f"import sys; sys.path.insert(0, r'{PROJECT_DIR}'); "
     f"from simulator.modules.virtual_usb import start_virtual_usb; "
     f"start_virtual_usb(); import time; time.sleep(3600)"],
    creationflags=creation_flags,
)
time.sleep(1)

print("\n🖥️ Starting Virtual Board Display...")
display_gui_path = os.path.join(PROJECT_DIR, 'display_gui.py')
display_proc = subprocess.Popen([PYTHON_EXE, display_gui_path])
time.sleep(2)

# Thonny detection
thonny_path = None
if IS_WINDOWS:
    candidates = [
        os.path.join(os.environ.get('APPDATA', ''), 'Roaming', 'Python', 'Python311', 'Scripts', 'thonny.exe'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Thonny', 'thonny.exe'),
    ]
    for c in candidates:
        if os.path.exists(c):
            thonny_path = c
            break
else:
    import shutil
    thonny_path = shutil.which('thonny')

if thonny_path and os.path.exists(thonny_path):
    demo_path = os.path.join(PROJECT_DIR, 'demo_pinpong.py')
    thonny_proc = subprocess.Popen([thonny_path, demo_path])
else:
    print("   ⚠️ Thonny not found, please start manually")
    thonny_proc = None

# Default serial port info
if IS_WINDOWS:
    default_serial = "COM20"
    default_host = "COM19"
elif sys.platform == 'darwin':
    default_serial = "/dev/cu.mpVirt2"
    default_host = "/dev/cu.mpVirt1"
else:
    default_serial = "/tmp/vcom2"
    default_host = "/tmp/vcom1"

print("\n" + "=" * 60)
print("   All services started successfully!")
print("=" * 60)
print(f"\n📋 Usage:")
print(f"   1. Virtual Board display is running")
print(f"   2. Open demo.py or demo_pinpong.py in Thonny")
print(f"   3. Click Run button to see effects")
print(f"\n🔗 Mind+ Connection:")
print(f"   Connect via TCP: 127.0.0.1:7777")
print(f"   Or use serial bridge: {default_host} ↔ {default_serial}")
print(f"\nPress Ctrl+C to stop all services")
print("=" * 60 + "\n")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 Stopping all services...")
    for proc in [display_proc, usb_proc, server_proc, thonny_proc]:
        if proc:
            try:
                proc.terminate()
                proc.wait(timeout=3)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
    print("✅ All services stopped")
