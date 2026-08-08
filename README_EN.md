<div align="center">

<img src="docs/assets/banner.svg" alt="mPython VirtualBoard · Virtual Board" width="880" />

**Learn board coding — no hardware required**

[中文](README.md) · [English](README_EN.md)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](#)
[![Stars](https://img.shields.io/github/stars/lmxylyc/mPython-VirtualBoard?style=social)](https://github.com/lmxylyc/mPython-VirtualBoard/stargazers)

[🌐 Interactive Promo Site (Live Demo)](https://lmxylyc.github.io/mPython-VirtualBoard/) · [📖 Full User Guide](USER_GUIDE.md) · [🚀 Getting Started](GettingStarted.md)

</div>

---

## Why it exists

Not enough kits, fear of damage, handing out and collecting devices — none of these should block a coding class.

- **Zero-kit classes**: every student gets a complete board experience on their own computer. No bulk purchase, no maintenance
- **What you code is what you see**: every line of code is reflected live on the virtual board's screen, lights and sensors
- **A smooth path to real hardware**: the same mPython / PinPong APIs — verify on the virtual board in class, flash to a real board at home

## Features

| | |
| --- | --- |
| 🖥️ **Complete hardware simulation** | OLED display, 3 RGB LEDs, dual buttons, 6 touch pads, buzzer, plus accelerometer, gyroscope, magnetometer, light and sound sensors |
| 🔀 **Dual coding modes** | Switch freely between mPython and PinPong teaching paths to fit different curricula |
| 🧩 **Mind+ block transpiling** | Paste auto-generated Mind+ upload-mode code — the built-in transpiler converts it to Python and runs it directly |
| 🤖 **Local AI code rewriting** | PinPong mode integrates local Ollama + DeepSeek models, turning natural-language requirements into well-structured teaching code. Data never leaves your machine |
| 📈 **Real sensor input** | Connect a physical board via USB serial to read real accelerometer, gyroscope, magnetometer, light and sound data in real time |
| 🪟 **Thonny integration & floating window** | The desktop edition works seamlessly with Thonny / IDLE, with an always-on-top floating board window |

## Two editions, pick your fit

| | **mPython VM Studio** (Web) | **mPython Virtual Machine** (Desktop) |
| --- | --- | --- |
| Positioning | All-in-one teaching workbench, ready out of the box | Classroom integration with Thonny / IDLE |
| Tech stack | PyWebView · Vue 3 · Monaco | Tkinter · Socket · Virtual USB |
| Highlights | Built-in editor, Mind+ transpiling, AI rewriting, real sensor input, manual sensor control panel | One-click launcher, floating display, 8 UI languages, virtual USB & client libraries |
| Directory | [`mpython-vm-web/`](mpython-vm-web/README.md) | Repository root |

## Up and running in 3 minutes

**Option 1: VM Studio (recommended)**

```bash
git clone https://github.com/lmxylyc/mPython-VirtualBoard.git
cd mPython-VirtualBoard/mpython-vm-web
pip install -r requirements.txt
python main.py
```

**Option 2: Desktop VM**

```bash
git clone https://github.com/lmxylyc/mPython-VirtualBoard.git
cd mPython-VirtualBoard
python start_vm.py        # or double-click run.bat
```

**Try some code (mPython mode):**

```python
from mpython_client import connect

mp = connect()

mp.oled.fill(0)
mp.oled.DispChar("Hello World!", 0, 0, 1)
mp.oled.show()

mp.rgb[0] = (255, 0, 0)
mp.rgb.write()
```

## Familiar hardware, familiar APIs

The virtual board keeps the same programming interfaces as the real one — everything students learn transfers directly.

| Component | mPython API | PinPong API |
| --- | --- | --- |
| OLED display | `mp.oled` | `get_oled()` |
| RGB LED ×3 | `mp.rgb` | `get_rgb()` |
| Buttons A / B | `mp.button_a` | `Pin(Pin.P0, Pin.IN)` |
| Touch pads ×6 | `mp.touch` | `Pin(Pin.P1, Pin.IN)` |
| Light sensor | `mp.light` | `Sensor(Pin.P2)` |
| Sound sensor | `mp.sound` | `Sensor(Pin.P3)` |
| Accelerometer | `mp.accelerometer` | `get_accel()` |
| Gyroscope | `mp.gyroscope` | `get_gyro()` |
| Magnetometer | `mp.magnetic` | `get_mag()` |

## Designed for real classrooms

- **Blocks-to-code transition**: students start with Mind+ blocks, then read the transpiled Python to grasp abstract concepts naturally
- **Sensor exploration**: connect a real board or use the manual control panel to see acceleration, light and sound values change live
- **AI code-rewriting practice**: students write raw code first, then let local AI rewrite it into a canonical version — learning style by comparison
- **Hardware-free demos**: when no physical boards are available, the virtual board delivers an identical teaching experience

## UI languages

The desktop edition ships with 8 UI languages: 中文 · English · 日本語 · 한국어 · Français · Deutsch · Español · Русский

## Docs & links

- 🌐 [Interactive promo site with a playable virtual board](https://lmxylyc.github.io/mPython-VirtualBoard/)
- 📖 [Full user guide (both editions)](USER_GUIDE.md)
- 🚀 [Getting started](GettingStarted.md)
- 💻 [VM Studio documentation](mpython-vm-web/README.md)

---

<div align="center">

**Author**: Lin Yicheng (林奕呈) · **License**: [MIT](LICENSE)

If this project helps your classroom, a ⭐ **Star** means a lot!

</div>
