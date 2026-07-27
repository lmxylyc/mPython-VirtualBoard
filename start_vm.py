import subprocess
import sys
import os
import time

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_EXE = sys.executable

print("=" * 60)
print("   mPython Virtual Board - One-Click Launch")
print("=" * 60)

print("\n🔌 Starting VM Server (port 7778)...")
vm_server_path = os.path.join(PROJECT_DIR, 'vm_server.py')
server_proc = subprocess.Popen([PYTHON_EXE, vm_server_path], creationflags=subprocess.CREATE_NO_WINDOW)
time.sleep(2)

print("\n🔌 Starting Virtual USB Service (port 7777)...")
virtual_usb_path = os.path.join(PROJECT_DIR, 'simulator', 'modules', 'virtual_usb.py')
usb_proc = subprocess.Popen([PYTHON_EXE, '-c', f"import sys; sys.path.insert(0, r'{PROJECT_DIR}'); from simulator.modules.virtual_usb import start_virtual_usb; start_virtual_usb(); import time; time.sleep(3600)"], 
                             creationflags=subprocess.CREATE_NO_WINDOW)
time.sleep(1)

print("\n🖥️ Starting Virtual Board Display (always on top)...")
display_gui_path = os.path.join(PROJECT_DIR, 'display_gui.py')
display_proc = subprocess.Popen([PYTHON_EXE, display_gui_path])
time.sleep(2)

print("\n💻 Starting Thonny IDE...")
thonny_path = os.path.join(os.environ['APPDATA'], 'Roaming', 'Python', 'Python311', 'Scripts', 'thonny.exe')
if os.path.exists(thonny_path):
    demo_path = os.path.join(PROJECT_DIR, 'demo_pinpong.py')
    thonny_proc = subprocess.Popen([thonny_path, demo_path])
else:
    print("   ⚠️ Thonny not found, please start manually")
    thonny_proc = None

print("\n" + "=" * 60)
print("   All services started successfully!")
print("=" * 60)
print("\n📋 Usage:")
print("   1. Virtual Board display is always on top")
print("   2. Open demo.py or demo_pinpong.py in Thonny")
print("   3. Click Run button to see effects")
print("\n🔗 Mind+ Connection:")
print("   Connect via TCP: 127.0.0.1:7777")
print("   Or use serial bridge: COM20 → 127.0.0.1:7777")
print("\nPress Ctrl+C to stop all services")
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
            except:
                try:
                    proc.kill()
                except:
                    pass
    print("✅ All services stopped")