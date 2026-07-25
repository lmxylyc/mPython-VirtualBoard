import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'clients'))

import subprocess

print("=" * 50)
print("   PinPong 库 - 演示程序")
print("=" * 50)

print("\n🖥️ 启动虚拟掌控板显示窗口...")
try:
    display_gui_path = os.path.join(os.path.dirname(__file__), 'display_gui.py')
    subprocess.Popen([sys.executable, display_gui_path])
    import time
    time.sleep(1)
except:
    pass

from pinpong_client import *

print("\n🔹 初始化 PinPong")
init()
print("   ✅ PinPong 已初始化")

print("\n🔹 OLED显示")
oled = get_oled()
oled.clear()
oled.write("PinPong Mode\nOLED Test")
oled.show()
print("   ✅ OLED已更新")

print("\n🔹 RGB灯控制")
rgb = get_rgb()
rgb.write_color('red')
delay(500)
rgb.write_color('green')
delay(500)
rgb.write_color('blue')
delay(500)
rgb.write(255, 255, 0)
print("   ✅ RGB已更新")

print("\n🔹 读取按键")
btn_a = get_pin(0)
btn_b = get_pin(1)
print("   按键A状态:", btn_a.read_digital())
print("   按键B状态:", btn_b.read_digital())

print("\n🔹 读取传感器")
light = Sensor(3)
sound = Sensor(4)
print("   光线:", light.read())
print("   声音:", sound.read())

print("\n🔹 交互测试")
print("   点击显示窗口中的按键A/B或触摸按键")
print("   按 Ctrl+C 退出")

try:
    while True:
        if btn_a.read_digital() == 1:
            print("   ⚡ 按键A被按下！")
            rgb.write_color('red')
        elif btn_b.read_digital() == 1:
            print("   ⚡ 按键B被按下！")
            rgb.write_color('green')
        else:
            rgb.write_color('blue')
        delay(100)
except KeyboardInterrupt:
    rgb.off()
    oled.clear()
    oled.write("Goodbye!")
    oled.show()
    print("\n🛑 程序已退出")

print("=" * 50)