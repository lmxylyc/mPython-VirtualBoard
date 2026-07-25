# mPython Virtual Machine

> **mPython掌控板虚拟机** —— 青少年学习掌控板的辅助工具，让学习掌控版无需物理硬件，随时随地探索创造！

mPython Virtual Machine 是一个基于 Python 的 mPython 掌控板完整模拟器，学生版支持 mPython 原生模式和 PinPong 模式两种编程方式，可在自制的IDE上运行（建议初学者通过mind+上传模式的代码生成器来写与mind+的直连还在研制中）。Thonny/IDLE 等 IDE端口配合下文给出的调用代码支持通过悬浮显示窗口实时展示虚拟掌控板状态，

## 具身智能教育

本项目致力于降低具身智能（Embodied Intelligence）学习门槛，让青少年无需购买实体机器人设备即可学习具身智能编程。通过完整的感知-决策-执行闭环系统模拟，帮助学生建立具身智能的系统认知。
- **感知层**：光线传感器、声音传感器、加速度计、陀螺仪、地磁传感器
- **决策层**：支持 mPython/PinPong 编程模式
- **执行层**：OLED显示屏、RGB LED、蜂鸣器、触摸按键

##  特点

-  **完整硬件模拟**：OLED显示屏、RGB LED、按键、触摸传感器、光线/声音/加速度传感器、陀螺仪、地磁传感器
-  **双模式支持**：mPython模式和PinPong模式自由切换
-  **悬浮显示窗口**：虚拟掌控板始终置顶，方便观察
-  **网络通信**：服务器-客户端架构，支持Thonny/IDLE远程控制
-  **多语言支持**：支持中文、English、日本語、한국어、Français、Deutsch、Español、Русский
-  **打开即用**：一键启动器，无需物理硬件
-  **具身智能教育**：完整的感知-决策-执行闭环系统

##  快速开始

### 方式一：一键启动（推荐）

```bash
python start_vm.py
```

或双击运行 `run.bat`

### 方式二：集成IDE版本

```bash
python integrated_vm.py
```

### 方式三：手动启动

```bash
# 启动显示窗口（悬浮）
python display_gui.py

# 启动虚拟机服务
python vm_server.py

# 在Thonny中运行演示代码
# 打开 demo.py (mPython模式) 或 demo_pinpong.py (PinPong模式)
```

##  使用指南

### 在 Thonny 中调用虚拟掌控板

#### 第一步：在 Thonny 中运行代码

1. 打开 Thonny IDE
2. 点击「文件」→「打开」，选择项目中的 `demo.py` 或 `demo_pinpong.py`
3. 点击「运行」按钮 
4. 在虚拟掌控板显示窗口中观察效果

#### 第二步：编写自己的代码

**mPython 模式**：使用 `mpython_client` 库

```python
from mpython_client import connect

# 连接到虚拟掌控板
mp = connect()

# 使用 mPython API
mp.oled.fill(0)
mp.oled.DispChar("Hello!", 0, 0, 1)
mp.oled.show()

mp.rgb[0] = (255, 0, 0)
mp.rgb.write()
```

**PinPong 模式**：使用 `pinpong_client` 库

```python
from pinpong_client import *

# 初始化连接
init()

# 使用 PinPong API
oled = get_oled()
oled.clear()
oled.write("Hello PinPong")
oled.show()

rgb = get_rgb()
rgb.write(255, 0, 0)
```

#### 注意事项

-  虚拟掌控板显示窗口必须保持打开
-  虚拟机服务必须正在运行（端口 7778）
-  代码中使用的客户端库必须与项目中的一致
-  不要同时运行多个虚拟机服务实例

### mPython 模式

```python
from mpython_client import connect

mp = connect()

# OLED显示
mp.oled.fill(0)
mp.oled.DispChar("Hello World!", 0, 0, 1)
mp.oled.show()

# RGB灯
mp.rgb[0] = (255, 0, 0)
mp.rgb.write()

# 按键读取
if mp.button_a.value:
    print("按键A按下")

# 传感器读取
print("光线:", mp.light.read())
print("声音:", mp.sound.read())
```

### PinPong 模式

```python
from pinpong_client import *

init()

# OLED显示
oled = get_oled()
oled.clear()
oled.write("Hello PinPong")
oled.show()

# RGB灯
rgb = get_rgb()
rgb.write(255, 0, 0)

# 按键读取
btn_a = Pin(Pin.P0, Pin.IN)
if btn_a.read_digital() == 1:
    print("按键A按下")
```

##  多语言支持

虚拟掌控板支持8种语言界面，可在左上角语言选择器中切换：

| 语言代码 | 显示名称 |
|----------|----------|
| zh_CN | 中文 |
| en_US | English |
| ja_JP | 日本語 |
| ko_KR | 한국어 |
| fr_FR | Français |
| de_DE | Deutsch |
| es_ES | Español |
| ru_RU | Русский |

##  项目结构

```
mpython-virtual-machine/
├── start_vm.py              # 一键启动器
├── run.bat                  # 批处理启动脚本
├── vm_server.py             # 虚拟机服务端
├── display_gui.py           # 虚拟掌控板显示窗口（悬浮）
├── integrated_vm.py         # 集成IDE版本
├── mindplus_usb.py          # Mind+ USB桥接服务
├── mpython_vm.py            # mPython虚拟机核心
├── clients/                 # 客户端库
│   ├── mpython_client.py    # mPython模式客户端
│   └── pinpong_client.py    # PinPong模式客户端
├── mindplus_extension/      # Mind+扩展
│   ├── javascript/
│   │   └── main.js
│   └── config.json
├── simulator/               # 硬件模拟模块
│   ├── __init__.py
│   ├── gui.py               # GUI组件
│   ├── shared_state.py      # 共享状态管理
│   ├── lang/                # 多语言支持
│   │   ├── __init__.py
│   │   ├── zh_CN.py
│   │   ├── en_US.py
│   │   ├── ja_JP.py
│   │   ├── ko_KR.py
│   │   ├── fr_FR.py
│   │   ├── de_DE.py
│   │   ├── es_ES.py
│   │   └── ru_RU.py
│   └── modules/             # MicroPython模块
│       ├── NVS.py
│       ├── camera.py
│       ├── esp.py
│       ├── machine.py
│       ├── neopixel.py
│       ├── network.py
│       ├── pc_sensors.py
│       ├── ssd1106.py
│       ├── virtual_usb.py
│       ├── educore/
│       └── v831/
├── demo.py                  # mPython模式演示代码
├── demo_pinpong.py          # PinPong模式演示代码
├── requirements.txt         # 依赖清单
├── .gitignore               # Git忽略规则
├── GettingStarted.md        # 入门指南
├── LICENSE                  # 许可证
└── README.md                # 项目文档
```

##  支持的硬件组件

| 组件 | mPython API | PinPong API |
|------|-------------|-------------|
| OLED | `mp.oled` | `get_oled()` |
| RGB LED | `mp.rgb` | `get_rgb()` |
| 按键A/B | `mp.button_a` | `Pin(Pin.P0, Pin.IN)` |
| 触摸按键 | `mp.touch` | `Pin(Pin.P1, Pin.IN)` |
| 光线传感器 | `mp.light` | `Sensor(Pin.P2)` |
| 声音传感器 | `mp.sound` | `Sensor(Pin.P3)` |
| 加速度计 | `mp.accelerometer` | `get_accel()` |
| 陀螺仪 | `mp.gyroscope` | `get_gyro()` |
| 地磁传感器 | `mp.magnetic` | `get_mag()` |

##  技术栈

- Python 3.8+
- Tkinter（GUI）
- Socket（网络通信）
- pyserial（串口通信）
- pyusb（USB设备模拟）

##  许可证

MIT License - 详见 [LICENSE](LICENSE)

##  贡献

欢迎提交Issue和Pull Request！

---

**开发作者**：林奕呈

**项目地址**：https://github.com/lmxylyc/mPython-VirtualBoard
