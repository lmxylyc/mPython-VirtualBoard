import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'clients'))

from mpython_client import connect

print("=" * 50)
print("   mPython 虚拟掌控板 - 演示程序")
print("=" * 50)

client = connect()

if client:
    print("\n🔹 控制OLED显示")
    client.oled.fill(0)
    client.oled.DispChar("Hello Thonny!", 0, 0, 1)
    client.oled.DispChar("mPython VM", 0, 16, 1)
    client.oled.show()
    print("   ✅ OLED已更新")

    print("\n🔹 控制RGB灯")
    client.rgb[0] = (255, 0, 0)   
    client.rgb[1] = (0, 255, 0)   
    client.rgb[2] = (0, 0, 255)   
    client.rgb.write()
    print("   ✅ RGB已更新（红、绿、蓝）")

    print("\n🔹 读取传感器")
    light_val = client.light.read()
    sound_val = client.sound.read()
    accel = client.accelerometer.get()
    print(f"   光线: {light_val}")
    print(f"   声音: {sound_val}")
    if isinstance(accel, list) and len(accel) == 3:
        print(f"   加速度: x={accel[0]:.2f}, y={accel[1]:.2f}, z={accel[2]:.2f}")
    elif isinstance(accel, dict):
        print(f"   加速度: x={accel.get('x', 0):.2f}, y={accel.get('y', 0):.2f}, z={accel.get('z', 0):.2f}")
    else:
        print(f"   加速度: {accel}")

    print("\n🔹 交互测试")
    print("   点击显示窗口中的按键A/B或触摸按键")
    print("   按 Ctrl+C 退出")
    
    try:
        import time
        while True:
            if client.button_a.is_pressed():
                print("   ⚡ 按键A被按下！")
            if client.button_b.is_pressed():
                print("   ⚡ 按键B被按下！")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n🛑 程序已退出")
else:
    print("\n❌ 连接失败")
    print("   请确保 vm_server.py 已启动")

print("=" * 50)