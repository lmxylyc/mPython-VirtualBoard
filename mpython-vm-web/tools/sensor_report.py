"""掌控板端传感器上报脚本（MicroPython / mPython 固件）。

用途：
    让 mPython VM Studio 的"真实传感器"页实时读取掌控板传感器数据。

使用方法：
    1. 用 mPython IDE / Thonny 将本文件上传到掌控板；
    2. 在掌控板上运行本脚本（代码会一直循环上报，不会退出）；
    3. 在 mPython VM Studio 的"真实传感器"页点击"扫描"，选择端口后点击"连接"。

上报格式：
    每行一个 JSON 对象，例如：
    {"accel":[0.01,-0.02,1.02],"gyro":[0.0,0.0,0.0],"mag":[10,20,30],"light":123,"sound":45}

说明：
    - 兼容 mPython 固件（mpython 包）的加速度计、陀螺仪、磁力计、光线、声音传感器；
    - 固件缺少某个传感器时，对应字段会省略，不影响其他数据上报；
    - 数据每 100ms 上报一次。
"""

import time
import json

try:
    from mpython import accelerometer, gyroscope, magnetic, light, sound
except ImportError:
    accelerometer = None
    gyroscope = None
    magnetic = None
    light = None
    sound = None


def read_vec(sensor, digits=2):
    """读取三维向量传感器，返回 [x, y, z] 或 None。"""
    try:
        v = sensor.get()
        return [
            round(float(v[0]), digits),
            round(float(v[1]), digits),
            round(float(v[2]), digits),
        ]
    except Exception:
        return None


while True:
    data = {}
    if accelerometer is not None:
        v = read_vec(accelerometer)
        if v:
            data['accel'] = v
    if gyroscope is not None:
        v = read_vec(gyroscope)
        if v:
            data['gyro'] = v
    if magnetic is not None:
        v = read_vec(magnetic)
        if v:
            data['mag'] = v
    if light is not None:
        try:
            data['light'] = int(light.read())
        except Exception:
            pass
    if sound is not None:
        try:
            data['sound'] = int(sound.read())
        except Exception:
            pass
    print(json.dumps(data))
    time.sleep_ms(100)
