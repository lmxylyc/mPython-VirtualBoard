# 🚀 快速上手指南

## 安装步骤

### 方式一：绿色便携版（推荐）

1. **下载**：从 [GitHub Releases](https://github.com/lmxylyc/mPython-VirtualBoard/releases) 下载最新版本
2. **解压**：将压缩包解压到任意文件夹
3. **运行**：双击 `mPython-VM.exe` 即可启动

### 方式二：源码运行

1. **克隆项目**：
   ```bash
   git clone https://github.com/lmxylyc/mPython-VirtualBoard.git
   cd mPython-VirtualBoard
   ```

2. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

3. **启动**：
   - 双击 `run.bat`（Windows）
   - 或运行 `python integrated_vm.py`

---

## 首次使用

### 第1步：启动虚拟机

打开软件后，点击工具栏上的 **"▶ 启动虚拟机"** 按钮：

- 等待约2秒自动连接
- 状态栏变为 **"🔍 虚拟机运行中"** 表示启动成功

### 第2步：运行示例代码

点击菜单栏 **"学习" → "示例代码"**，选择一个示例：

- **LED闪烁**：让三个LED轮流闪烁
- **OLED显示**：在屏幕上显示文字
- **按键控制**：使用按钮控制LED

### 第3步：编写自己的代码

在右侧代码编辑器中输入代码，按 **F5** 运行：

```python
from mpython_sim import *

# 点亮LED1为红色
rgb[0] = (255, 0, 0)
rgb.write()

# 在OLED上显示文字
oled.fill(0)
oled.DispChar("Hello World!", 0, 0, 1)
oled.show()
```

---

## 界面说明

### 左侧：虚拟掌控板

| 组件 | 说明 |
|------|------|
| **OLED显示屏** | 显示代码输出的文字 |
| **RGB LED** | 三个LED指示灯 |
| **按键A/B** | 物理按键，点击模拟按下 |
| **触摸按键** | P/Y/T/H/O/N 六个触摸键 |
| **传感器面板** | 显示实时传感器数据 |

### 右侧：代码编辑器

| 功能 | 快捷键 |
|------|--------|
| 运行代码 | F5 |
| 停止运行 | F6 |
| 打开文件 | Ctrl+O |
| 保存文件 | Ctrl+S |

---

## 常用API

### LED控制
```python
rgb[0] = (255, 0, 0)  # 设置LED1为红色
rgb[1] = (0, 255, 0)  # 设置LED2为绿色
rgb[2] = (0, 0, 255)  # 设置LED3为蓝色
rgb.write()            # 应用颜色设置
```

### OLED显示
```python
oled.fill(0)                       # 清除屏幕
oled.DispChar("文字", 0, 0, 1)     # 在位置(0,0)显示文字
oled.show()                        # 刷新显示
```

### 按键检测
```python
if button_a.is_pressed():
    rgb[0] = (255, 0, 0)
```

### 触摸按键
```python
if touchpad_p.is_pressed():
    rgb[0] = (255, 0, 0)
```

### 传感器读取
```python
accel = accelerometer.get()  # 加速度计
light_val = light.read()     # 光线传感器
sound_val = sound.read()     # 声音传感器
```

---

## 学习路径

推荐学习顺序：

1. **第1课：点亮LED** → 学习控制RGB LED
2. **第2课：OLED显示** → 学习在屏幕上显示信息
3. **第3课：按键控制** → 学习使用按钮交互
4. **第4课：触摸感应** → 学习使用触摸按键
5. **第5课：传感器数据** → 学习读取传感器数据
6. **第6课：综合项目** → 制作环境监测器

点击菜单栏 **"学习" → "教程入门"** 开始学习！

---

## 常见问题

### Q: 启动时提示缺少模块？
A: 请运行 `pip install -r requirements.txt` 安装依赖。

### Q: 连接失败？
A: 确保没有其他程序占用端口7777，关闭后重试。

### Q: OLED不显示？
A: 代码中需要调用 `oled.show()` 才能刷新显示。

### Q: Mind+代码如何使用？
A: 直接复制Mind+生成的代码粘贴到编辑器，会自动转译为MicroPython。

---

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| F5 | 运行代码 |
| F6 | 停止运行 |
| Ctrl+O | 打开文件 |
| Ctrl+S | 保存文件 |
| Ctrl+Q | 退出程序 |

---

## 获取帮助

- **使用说明**：点击菜单栏 **"帮助" → "使用说明"**
- **API文档**：点击菜单栏 **"学习" → "API文档"**
- **组件说明**：点击菜单栏 **"学习" → "组件说明"**

---

祝你学习愉快！🎉