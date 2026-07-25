import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import sys
import os
import threading
import socket
import time
import random
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'simulator'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'simulator', 'modules'))
sys.path.insert(0, os.path.dirname(__file__))

from shared_state import shared_state
from mindplus_transpiler import is_mindplus_code, transpile

pc_sensors = None
VM_PORT = 7777

# 后导入VM模块（避免循环依赖）
_vm_thread = None
_vm_initialized = False


class IntegratedVMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("mPython掌控板虚拟机 - 教育版")
        self.root.geometry("1300x800")
        self.root.minsize(1100, 700)

        self.vm_process = None
        self.vm_socket = None
        self.connect_status = False
        self._running = True
        self._current_tutorial = 0
        self._completed_tutorials = []
        self._current_mode = tk.StringVar(value="mpython")
        self._current_mode.trace_add("write", lambda *a: self._on_mode_changed())

        self._create_menu()
        self._create_toolbar()
        self._create_main_layout()
        self._setup_sensor_timer()
        self._check_vm_status()
        self._load_tutorial_progress()

    def _create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="打开文件", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="保存文件", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="另存为...", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self._on_exit)
        menubar.add_cascade(label="文件", menu=file_menu)

        vm_menu = tk.Menu(menubar, tearoff=0)
        vm_menu.add_command(label="启动虚拟机", command=self.start_vm)
        vm_menu.add_command(label="连接虚拟机", command=self._toggle_connect)
        vm_menu.add_command(label="重启虚拟机", command=self.restart_vm)
        menubar.add_cascade(label="虚拟机", menu=vm_menu)

        code_menu = tk.Menu(menubar, tearoff=0)
        code_menu.add_command(label="运行代码", command=self.run_code, accelerator="F5")
        code_menu.add_command(label="停止运行", command=self.stop_code, accelerator="F6")
        code_menu.add_command(label="清空输出", command=self.clear_output)
        menubar.add_cascade(label="代码", menu=code_menu)

        learn_menu = tk.Menu(menubar, tearoff=0)
        learn_menu.add_command(label="教程入门", command=self._show_tutorial_select)
        learn_menu.add_command(label="示例代码", command=self._show_example_select)
        learn_menu.add_command(label="API文档", command=self._show_api_docs)
        learn_menu.add_command(label="组件说明", command=self._show_component_info)
        menubar.add_cascade(label="学习", menu=learn_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="使用说明", command=self._show_help)
        help_menu.add_command(label="关于", command=self._show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)

        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<F5>', lambda e: self.run_code())
        self.root.bind('<F6>', lambda e: self.stop_code())

    def _create_toolbar(self):
        toolbar = ttk.Frame(self.root, padding=3)
        toolbar.pack(fill=tk.X)

        self.vm_btn = ttk.Button(toolbar, text="▶ 启动虚拟机", command=self.start_vm)
        self.vm_btn.pack(side=tk.LEFT, padx=2)

        self.conn_btn = ttk.Button(toolbar, text="🔗 连接", command=self._toggle_connect, state=tk.DISABLED)
        self.conn_btn.pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        ttk.Button(toolbar, text="▶ 运行 (F5)", command=self.run_code).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="⏹ 停止 (F6)", command=self.stop_code).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🗑 清空输出", command=self.clear_output).pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        ttk.Button(toolbar, text="📂 打开", command=self.open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="💾 保存", command=self.save_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📋 示例", command=self.load_example).pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        mode_label = ttk.Label(toolbar, text="模式:", font=("Arial", 9))
        mode_label.pack(side=tk.LEFT, padx=(5, 2))

        self.mp_btn = ttk.Button(toolbar, text="mPython", width=9,
                                 command=lambda: self._set_mode("mpython"))
        self.mp_btn.pack(side=tk.LEFT, padx=1)

        self.pp_btn = ttk.Button(toolbar, text="PinPong", width=9,
                                 command=lambda: self._set_mode("pinpong"))
        self.pp_btn.pack(side=tk.LEFT, padx=1)

        self.mode_indicator = ttk.Label(toolbar, text="● mPython", foreground="#2196F3", font=("Arial", 8))
        self.mode_indicator.pack(side=tk.LEFT, padx=5)

        self.status_label = ttk.Label(toolbar, text="🔌 未连接", foreground="red")
        self.status_label.pack(side=tk.RIGHT, padx=5)

        self.mindplus_status = ttk.Label(toolbar, text="🖥️ Mind+: 未启动", foreground="gray", font=("Arial", 8))
        self.mindplus_status.pack(side=tk.RIGHT, padx=5)

        ttk.Button(toolbar, text="⚙️ Mind+配置", command=self._show_mindplus_settings).pack(side=tk.RIGHT, padx=2)

    def _create_main_layout(self):
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        left_frame = ttk.Frame(paned, width=400)
        paned.add(left_frame, weight=0)
        self._create_hardware_panel(left_frame)

        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)
        self._create_editor_panel(right_frame)

    def _create_hardware_panel(self, parent):
        self._board_label = ttk.LabelFrame(parent, text="mPython掌控板", padding=8)
        board_frame = self._board_label
        board_frame.pack(fill=tk.BOTH, expand=True)

        # ── OLED显示屏（文本模式） ──
        oled_frame = ttk.LabelFrame(board_frame, text="OLED显示屏 (128x64)", padding=0)
        oled_frame.pack(pady=5)

        outer_frame = tk.Frame(oled_frame, bg="#2a2a2a", bd=0, highlightthickness=0)
        outer_frame.pack(padx=12, pady=12)

        inner_frame = tk.Frame(outer_frame, bg="#0a0a1a", bd=0, highlightthickness=0)
        inner_frame.pack(padx=8, pady=8)

        # 使用Label直接显示文本，模拟OLED
        self.oled_text = tk.Label(inner_frame, text="", font=("Courier New", 10),
                                  bg="#0a0a1a", fg="#b4d4ff",
                                  justify=tk.LEFT, anchor="nw",
                                  width=21, height=8,
                                  padx=4, pady=4)
        self.oled_text.pack()

        label_frame = tk.Frame(outer_frame, bg="#2a2a2a")
        label_frame.pack(fill=tk.X, padx=8, pady=(0, 6))
        tk.Label(label_frame, text="128×64 OLED", fg="#666", bg="#2a2a2a",
                font=("Arial", 7)).pack(side=tk.LEFT)
        tk.Label(label_frame, text="●", fg="#0f0", bg="#2a2a2a",
                font=("Arial", 6)).pack(side=tk.RIGHT)

        # ── RGB LED ──
        rgb_frame = ttk.LabelFrame(board_frame, text="RGB LED", padding=3)
        rgb_frame.pack(fill=tk.X, pady=5)

        rgb_canvas = tk.Canvas(rgb_frame, width=256, height=40, bg="#222", highlightthickness=0)
        rgb_canvas.pack()
        self._rgb_canvas = rgb_canvas
        self.rgb_indicators = []
        for i in range(3):
            x = 20 + i * 80
            indicator = rgb_canvas.create_oval(x, 8, x + 40, 32, fill="black", outline="#444")
            self.rgb_indicators.append(indicator)

        # ── 按键 ──
        btn_frame = ttk.LabelFrame(board_frame, text="按键", padding=3)
        btn_frame.pack(fill=tk.X, pady=5)

        btn_row = ttk.Frame(btn_frame)
        btn_row.pack()
        self.btn_a = ttk.Button(btn_row, text="按键A", width=10,
                                command=lambda: self._toggle_button('A'))
        self.btn_a.pack(side=tk.LEFT, padx=10, pady=2)
        self.btn_b = ttk.Button(btn_row, text="按键B", width=10,
                                command=lambda: self._toggle_button('B'))
        self.btn_b.pack(side=tk.LEFT, padx=10, pady=2)

        # ── 触摸按键 ──
        touch_frame = ttk.LabelFrame(board_frame, text="触摸按键 (P Y T H O N)", padding=3)
        touch_frame.pack(fill=tk.X, pady=5)

        touch_canvas = tk.Canvas(touch_frame, width=256, height=45, bg="#333", highlightthickness=0)
        touch_canvas.pack()
        self._touch_canvas = touch_canvas

        touch_labels = ['P', 'Y', 'T', 'H', 'O', 'N']
        self.touch_indicators = {}
        for i, label in enumerate(touch_labels):
            x = 15 + i * 40
            indicator = touch_canvas.create_oval(x, 8, x + 22, 28, fill="#555", outline="#777")
            text = touch_canvas.create_text(x + 11, 38, text=label, fill="#AAA", font=("Arial", 8))
            self.touch_indicators[label] = indicator
            touch_canvas.tag_bind(indicator, '<ButtonPress-1>', lambda e, l=label: self._set_touch(l, True))
            touch_canvas.tag_bind(indicator, '<ButtonRelease-1>', lambda e, l=label: self._set_touch(l, False))
            touch_canvas.tag_bind(text, '<ButtonPress-1>', lambda e, l=label: self._set_touch(l, True))
            touch_canvas.tag_bind(text, '<ButtonRelease-1>', lambda e, l=label: self._set_touch(l, False))

        # ── 传感器数据 ──
        sensor_frame = ttk.LabelFrame(board_frame, text="传感器数据", padding=3)
        sensor_frame.pack(fill=tk.X, pady=5)

        sensor_items = [
            ("加速度:", "x: 0.00  y: 0.00  z: 1.00"),
            ("陀螺仪:", "x: 0.00  y: 0.00  z: 0.00"),
            ("地磁:", "x: 0.0  y: 0.0  z: 0.0"),
            ("光线:", "---"),
            ("声音:", "---"),
            ("WiFi:", "未连接"),
            ("摄像头:", "❌ 未连接"),
            ("麦克风:", "❌ 未连接"),
        ]
        self.sensor_vars = []
        for label, default in sensor_items:
            row = ttk.Frame(sensor_frame)
            row.pack(fill=tk.X, pady=1)
            ttk.Label(row, text=label, width=8, font=("Arial", 8)).pack(side=tk.LEFT)
            var = tk.StringVar(value=default)
            self.sensor_vars.append(var)
            ttk.Label(row, textvariable=var, font=("Arial", 8)).pack(side=tk.LEFT)

    def _redraw_oled(self, buffer):
        """文本模式OLED显示"""
        text_lines = shared_state.get_oled_text()
        display_text = "\n".join(text_lines)
        self.oled_text.config(text=display_text)

    def _update_rgb_display(self, colors):
        for i, color in enumerate(colors):
            hex_color = '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])
            self._rgb_canvas.itemconfig(self.rgb_indicators[i], fill=hex_color)

    def _toggle_button(self, btn):
        current = shared_state.get_button(btn)
        new_state = not current
        shared_state.set_button(btn, new_state)
        style = 'Pressed.TButton' if new_state else 'TButton'
        getattr(self, f'btn_{btn.lower()}').configure(style=style)

    def _set_touch(self, label, state):
        shared_state.set_touch(label, state)
        color = "#2196F3" if state else "#555"
        self._touch_canvas.itemconfig(self.touch_indicators[label], fill=color)

    def _update_sensor_display(self):
        accel, gyro, mag, light, sound = shared_state.get_sensors()
        wifi_connected, wifi_ssid = shared_state.get_wifi()
        self.sensor_vars[0].set(f"x: {accel['x']:.2f}  y: {accel['y']:.2f}  z: {accel['z']:.2f}")
        self.sensor_vars[1].set(f"x: {gyro['x']:.2f}  y: {gyro['y']:.2f}  z: {gyro['z']:.2f}")
        self.sensor_vars[2].set(f"x: {mag['x']:.1f}  y: {mag['y']:.1f}  z: {mag['z']:.1f}")
        self.sensor_vars[3].set(str(light))
        self.sensor_vars[4].set(str(sound))
        self.sensor_vars[5].set(f"已连接: {wifi_ssid}" if wifi_connected else "未连接")
        if pc_sensors is not None:
            cam_status = "✅ 已连接" if pc_sensors.is_camera_available() else "❌ 未连接"
            mic_status = "✅ 已连接" if pc_sensors.is_audio_available() else "❌ 未连接"
            self.sensor_vars[6].set(cam_status)
            self.sensor_vars[7].set(mic_status)

    def _setup_sensor_timer(self):
        def poll():
            if self._running:
                shared_state.update_sensors()
                self._update_sensor_display()
                # 更新 OLED（文本模式显示，PinPong/mPython 都兼容）
                self._redraw_oled(None)
                # 像素缓冲区更新（保留给未来像素模式使用）
                oled_buf = shared_state.get_oled_buffer()
                if oled_buf and any(b != 0 for b in oled_buf):
                    self._redraw_oled(oled_buf)
                rgb = shared_state.get_rgb_colors()
                if any(any(c != 0 for c in color) for color in rgb):
                    self._update_rgb_display(rgb)
                self.root.after(500, poll)
        self.root.after(500, poll)

    def _create_editor_panel(self, parent):
        self._code_label = ttk.LabelFrame(parent, text="代码编辑区（从Mind+复制代码粘贴到这里运行）", padding=3)
        code_frame = self._code_label
        code_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 3))

        self.code_text = scrolledtext.ScrolledText(code_frame, width=80, height=22,
                                                    font=('Consolas', 10), wrap=tk.NONE)
        self.code_text.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        self._insert_default_code()

        output_frame = ttk.LabelFrame(parent, text="运行输出", padding=3)
        output_frame.pack(fill=tk.BOTH, expand=True)

        self.output_text = scrolledtext.ScrolledText(output_frame, width=80, height=8,
                                                      font=('Consolas', 10), state=tk.DISABLED, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

    def _insert_default_code(self):
        self.code_text.insert(tk.END, """/*! 
  * MindPlus 
  * mpython 
  * 
  */ 
#include <MPython.h> 

// 主程序开始 
void setup() { 
    mPython.begin(); 
} 
void loop() { 
    display.setCursorLine(1); 
    display.printLine("Mind+");
}""")

    # ────────── 文件操作 ──────────

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[('Python文件', '*.py'), ('所有文件', '*.*')])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.code_text.delete("1.0", tk.END)
                self.code_text.insert(tk.END, content)
                self.root.title(f"mPython掌控板虚拟机 - {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("打开失败", f"无法打开文件: {e}")

    def save_file(self):
        if hasattr(self, '_current_file') and self._current_file:
            try:
                content = self.code_text.get("1.0", tk.END)
                with open(self._current_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("保存成功", "文件已保存")
            except Exception as e:
                messagebox.showerror("保存失败", f"无法保存文件: {e}")
        else:
            self.save_as_file()

    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension='.py',
                                                  filetypes=[('Python文件', '*.py'), ('所有文件', '*.*')])
        if file_path:
            try:
                content = self.code_text.get("1.0", tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self._current_file = file_path
                self.root.title(f"mPython掌控板虚拟机 - {os.path.basename(file_path)}")
                messagebox.showinfo("保存成功", "文件已保存")
            except Exception as e:
                messagebox.showerror("保存失败", f"无法保存文件: {e}")

    # ────────── 虚拟机控制 ──────────

    def start_vm(self):
        global _vm_initialized, _vm_thread
        if _vm_initialized:
            messagebox.showinfo("提示", "虚拟机已在运行")
            return

        self.add_output("⏳ 启动虚拟掌控板（同一进程）...")
        self.status_label.config(text="⏳ 启动中...", foreground="orange")
        self.vm_btn.config(text="⏳ 启动中...", state=tk.DISABLED)

        def _start():
            global _vm_initialized, pc_sensors
            try:
                from pc_sensors import pc_sensors as sensors_module
                pc_sensors = sensors_module
                
                pc_sensors.start()
                shared_state.set_pc_sensors(pc_sensors)
                shared_state.set_use_real_sensors(True)

                import virtual_usb
                virtual_usb.start_virtual_usb()
                
                bridge = virtual_usb.SerialToTCPBridge(tcp_port=7777, serial_port='COM20')
                bridge.start()

                _vm_initialized = True

                self.root.after(1000, self._on_vm_started)
            except Exception as e:
                import traceback
                self.root.after(0, lambda: self.add_output(f"❌ 启动失败: {e}"))
                self.root.after(0, lambda: self.add_output(traceback.format_exc()))
                self.root.after(0, lambda: self.status_label.config(text="❌ 启动失败", foreground="red"))
                self.root.after(0, lambda: self.vm_btn.config(text="▶ 启动虚拟机", state=tk.NORMAL))

        _vm_thread = threading.Thread(target=_start, daemon=True)
        _vm_thread.start()

    def _on_vm_started(self):
        self.add_output("✅ 虚拟掌控板启动成功！")
        self.status_label.config(text="✅ 虚拟机运行中", foreground="green")
        self.vm_btn.config(text="⏹ 关闭虚拟机")
        self.conn_btn.config(state=tk.NORMAL)
        self.root.after(2000, self._auto_connect)

    def restart_vm(self):
        self.stop_vm()
        self.add_output("⏳ 等待重启...")
        self.root.after(2000, self.start_vm)

    def stop_vm(self):
        global _vm_initialized, _vm_thread
        if self.vm_socket:
            try:
                self.vm_socket.send(b"\x02")
                time.sleep(0.2)
                self.vm_socket.close()
            except:
                pass
            self.vm_socket = None
        self.connect_status = False
        _vm_initialized = False
        # 停止电脑传感器
        if pc_sensors is not None:
            pc_sensors.stop()
        shared_state.set_use_real_sensors(False)
        # 停止USB服务器
        try:
            import virtual_usb
            virtual_usb.stop_virtual_usb()
        except:
            pass
        # 停止VM循环
        try:
            import mpython_vm
            mpython_vm._running = False
        except:
            pass
        self.status_label.config(text="🔌 未连接", foreground="red")
        self.vm_btn.config(text="▶ 启动虚拟机")
        self.conn_btn.config(text="🔗 连接", state=tk.DISABLED)
        self.add_output("⏹ 虚拟机已关闭")

    # ────────── 连接管理 ──────────

    def _auto_connect(self):
        self.root.after(500, self._toggle_connect)

    def _toggle_connect(self):
        if self.connect_status:
            self.disconnect_vm()
        else:
            self.connect_vm()

    def connect_vm(self):
        self.add_output("⏳ 连接虚拟机...")
        try:
            self.vm_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.vm_socket.settimeout(5.0)
            self.vm_socket.connect(('127.0.0.1', VM_PORT))
            self.connect_status = True
            self.status_label.config(text="✅ 已连接", foreground="green")
            self.conn_btn.config(text="🔗 断开")
            self.add_output("✅ 已连接到虚拟掌控板")

            self.vm_socket.send(b"\r\n\x03\x03")
            time.sleep(0.2)
            self.vm_socket.send(b"\r\n\x01")
            time.sleep(0.5)

            response = b""
            while True:
                try:
                    self.vm_socket.settimeout(2.0)
                    data = self.vm_socket.recv(1024)
                    if data:
                        response += data
                        if b">" in response:
                            break
                except:
                    break

            if b"raw REPL" in response:
                self.add_output("✅ REPL模式已就绪")
            else:
                self.add_output("⚠️ 连接状态: " + response[:50].decode('utf-8', errors='ignore'))
        except Exception as e:
            messagebox.showerror("连接失败", f"无法连接到虚拟机: {e}\n请确保虚拟机已启动!")
            self.connect_status = False
            self.status_label.config(text="🔌 未连接", foreground="red")

    def disconnect_vm(self):
        if self.vm_socket:
            try:
                self.vm_socket.send(b"\x02")
                time.sleep(0.2)
                self.vm_socket.close()
            except:
                pass
            self.vm_socket = None
        self.connect_status = False
        self.status_label.config(text="🔌 未连接", foreground="red")
        self.conn_btn.config(text="🔗 连接")
        self.add_output("✓ 已断开连接")

    # ────────── 代码执行 ──────────

    def run_code(self):
        if not self.connect_status:
            messagebox.showwarning("未连接", "请先启动并连接到虚拟机！")
            return

        code = self.code_text.get("1.0", tk.END).strip()
        if not code:
            messagebox.showwarning("空代码", "请输入代码！")
            return

        self.add_output("=" * 60)

        # ── 检测是否Mind+ C++代码，自动转译 ──
        if is_mindplus_code(code):
            self.add_output("🔄 检测到 Mind+ C++ 代码，自动转译为 MicroPython...")
            try:
                py_code = transpile(code)
                self.add_output("✅ 转译成功！")
                self.add_output("-" * 60)
                # 显示转译后的代码
                for line in py_code.split('\n'):
                    if line.strip():
                        self.add_output(f"  {line}")
                self.add_output("-" * 60)
                code = py_code
            except Exception as e:
                self.add_output(f"❌ 转译失败: {e}")
                return
        else:
            self.add_output("▶ 运行代码...")
        self.add_output("-" * 60)

        def execute():
            try:
                self.vm_socket.send(code.encode('utf-8'))
                time.sleep(0.3)
                self.vm_socket.send(b"\x04")
                time.sleep(3.0)

                response = b""
                while True:
                    try:
                        self.vm_socket.settimeout(3.0)
                        data = self.vm_socket.recv(4096)
                        if data:
                            response += data
                            if b"\x04\x04" in response:
                                break
                    except:
                        break

                output = response.decode('utf-8', errors='ignore').replace('\x04', '')
                self.add_output(output)

                if b"OK" in response:
                    self.add_output("✅ 代码执行成功！")
                else:
                    self.add_output("⚠️ 代码执行完成")

            except Exception as e:
                self.add_output(f"❌ 执行错误: {e}")

        threading.Thread(target=execute, daemon=True).start()

    def stop_code(self):
        if self.vm_socket and self.connect_status:
            try:
                self.vm_socket.send(b"\x03\x03")
                self.add_output("⏹ 已停止代码执行")
            except Exception as e:
                self.add_output(f"❌ 停止失败: {e}")
        else:
            self.add_output("⚠️ 未连接到虚拟机")

    # ────────── 输出 ──────────

    def add_output(self, text):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def clear_output(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)

    # ────────── 示例代码 ──────────

    def load_example(self):
        examples = [
            """# 示例1: RGB闪烁
from mpython_sim import *

while True:
    rgb[0] = (255, 0, 0)
    rgb[1] = (0, 255, 0)
    rgb[2] = (0, 0, 255)
    rgb.write()
    sleep_ms(500)
    rgb[0] = (0, 0, 0)
    rgb[1] = (0, 0, 0)
    rgb[2] = (0, 0, 0)
    rgb.write()
    sleep_ms(500)""",
            """# 示例2: OLED显示传感器数据
from mpython_sim import *

while True:
    oled.fill(0)
    oled.DispChar("Accel: " + str(accelerometer.get()), 0, 0, 1)
    oled.DispChar("Light: " + str(light.read()), 0, 20, 1)
    oled.DispChar("Sound: " + str(sound.read()), 0, 40, 1)
    oled.show()
    sleep_ms(500)""",
            """# 示例3: 按键控制RGB
from mpython_sim import *

rgb[0] = (0, 0, 0)
rgb[1] = (0, 0, 0)
rgb[2] = (0, 0, 0)
rgb.write()

while True:
    if button_a.is_pressed():
        rgb[0] = (255, 0, 0)
    else:
        rgb[0] = (0, 0, 0)

    if button_b.is_pressed():
        rgb[1] = (0, 255, 0)
    else:
        rgb[1] = (0, 0, 0)

    rgb.write()
    sleep_ms(100)""",
            """# 示例4: 触摸按键
from mpython_sim import *

rgb[0] = (0, 0, 0)
rgb[1] = (0, 0, 0)
rgb[2] = (0, 0, 0)
rgb.write()

while True:
    if touchpad_p.is_pressed():
        rgb[0] = (255, 0, 0)
    else:
        rgb[0] = (0, 0, 0)

    if touchpad_y.is_pressed():
        rgb[1] = (0, 255, 0)
    else:
        rgb[1] = (0, 0, 0)

    if touchpad_t.is_pressed():
        rgb[2] = (0, 0, 255)
    else:
        rgb[2] = (0, 0, 0)

    rgb.write()
    sleep_ms(100)""",
        ]

        current = self.code_text.get("1.0", tk.END)
        for i, ex in enumerate(examples):
            if ex[:40] in current:
                next_idx = (i + 1) % len(examples)
                self.code_text.delete("1.0", tk.END)
                self.code_text.insert(tk.END, examples[next_idx])
                return

        self.code_text.delete("1.0", tk.END)
        self.code_text.insert(tk.END, examples[0])
        self.add_output("📋 已加载示例代码")

    # ────────── 状态检查 ──────────

    def _check_vm_status(self):
        if self._running:
            is_running = self._check_port(VM_PORT)
            if not self.connect_status:
                if is_running:
                    self.status_label.config(text="🔍 虚拟机运行中", foreground="blue")
                    self.conn_btn.config(state=tk.NORMAL)
                    if self.vm_btn.cget('text') == '▶ 启动虚拟机':
                        self.vm_btn.config(text="⏹ 关闭虚拟机")
                else:
                    if self.vm_btn.cget('text') != '▶ 启动虚拟机':
                        self.status_label.config(text="🔌 未连接", foreground="red")
                        self.conn_btn.config(state=tk.DISABLED)
            self.root.after(3000, self._check_vm_status)

    def _check_port(self, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            result = s.connect_ex(('127.0.0.1', port))
            s.close()
            return result == 0
        except:
            return False

    # ────────── Mind+ 配置 ──────────

    def _show_mindplus_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Mind+ 连接配置")
        settings_window.geometry("500x450")
        settings_window.transient(self.root)
        settings_window.grab_set()

        ttk.Label(settings_window, text="Mind+ 连接配置", font=("Arial", 14, "bold")).pack(pady=10)

        ttk.Label(settings_window, text="连接方式:", font=("Arial", 10)).pack(anchor=tk.W, padx=20)
        
        frame1 = ttk.Frame(settings_window)
        frame1.pack(fill=tk.X, padx=20, pady=5)
        
        self._mindplus_mode = tk.StringVar(value="serial")
        
        ttk.Radiobutton(frame1, text="串口连接 (推荐)", variable=self._mindplus_mode, 
                       value="serial", command=self._on_mindplus_mode_change).pack(anchor=tk.W)
        ttk.Radiobutton(frame1, text="TCP直连", variable=self._mindplus_mode, 
                       value="tcp", command=self._on_mindplus_mode_change).pack(anchor=tk.W)

        serial_frame = ttk.LabelFrame(settings_window, text="串口配置", padding=10)
        serial_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(serial_frame, text="串口号:").pack(side=tk.LEFT)
        self._serial_port_var = tk.StringVar(value="COM20")
        ttk.Entry(serial_frame, textvariable=self._serial_port_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(serial_frame, text="波特率:").pack(side=tk.LEFT, padx=10)
        ttk.Combobox(serial_frame, values=["9600", "19200", "38400", "57600", "115200"], 
                    width=8, state="readonly").pack(side=tk.LEFT)
        
        ttk.Button(serial_frame, text="检测com0com", command=self._detect_com0com).pack(side=tk.RIGHT, padx=5)

        tcp_frame = ttk.LabelFrame(settings_window, text="TCP配置", padding=10)
        tcp_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(tcp_frame, text="端口号:").pack(side=tk.LEFT)
        self._tcp_port_var = tk.StringVar(value="7777")
        ttk.Entry(tcp_frame, textvariable=self._tcp_port_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(tcp_frame, text=f"连接地址: 127.0.0.1:7777", font=("Arial", 8), foreground="gray").pack(side=tk.RIGHT)

        info_frame = ttk.LabelFrame(settings_window, text="设备信息", padding=10)
        info_frame.pack(fill=tk.X, padx=20, pady=5)
        
        info_text = tk.Text(info_frame, height=4, font=("Arial", 9), state=tk.DISABLED)
        info_text.pack(fill=tk.X)
        info_text.config(state=tk.NORMAL)
        info_text.insert(tk.END, "设备信息 (用于驱动配置):\n")
        info_text.insert(tk.END, "  VID: 1A86\n")
        info_text.insert(tk.END, "  PID: 5512\n")
        info_text.insert(tk.END, "  设备名称: USB Serial Port (CH9102)")
        info_text.config(state=tk.DISABLED)

        guide_frame = ttk.LabelFrame(settings_window, text="连接步骤", padding=10)
        guide_frame.pack(fill=tk.X, padx=20, pady=5)
        
        guide_text = tk.Text(guide_frame, height=6, font=("Arial", 8), state=tk.DISABLED)
        guide_text.pack(fill=tk.X)
        guide_text.config(state=tk.NORMAL)
        guide_text.insert(tk.END, "方法1 (串口连接 - 推荐):\n")
        guide_text.insert(tk.END, "  1. 确保虚拟机已启动\n")
        guide_text.insert(tk.END, "  2. 点击「启动Mind+服务」\n")
        guide_text.insert(tk.END, "  3. 在Mind+中选择「上传到设备」\n")
        guide_text.insert(tk.END, "  4. 选择显示的串口（如 COM19）\n\n")
        guide_text.insert(tk.END, "方法2 (TCP直连):\n")
        guide_text.insert(tk.END, "  仅当Mind+支持网络连接时使用\n")
        guide_text.insert(tk.END, "  1. 在Mind+中选择网络连接\n")
        guide_text.insert(tk.END, "  2. 输入地址: 127.0.0.1:7777")
        guide_text.config(state=tk.DISABLED)

        btn_frame = ttk.Frame(settings_window)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="启动Mind+服务", command=self._start_mindplus_services).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="关闭Mind+服务", command=self._stop_mindplus_services).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="确定", command=settings_window.destroy).pack(side=tk.RIGHT, padx=5)

        self._mindplus_services_running = False
        self._on_mindplus_mode_change()

    def _on_mindplus_mode_change(self):
        mode = self._mindplus_mode.get()
        self.add_output(f"📋 Mind+连接模式: {'TCP直连' if mode == 'tcp' else '串口连接'}")

    def _detect_com0com(self):
        import os
        paths = [
            r"C:\Program Files\com0com\setupc.exe",
            r"C:\Program Files (x86)\com0com\setupc.exe",
            r"C:\Program Files\com0com\setupc64.exe",
            r"C:\Program Files (x86)\com0com\setupc64.exe"
        ]
        found = False
        for path in paths:
            if os.path.exists(path):
                found = True
                messagebox.showinfo("检测结果", f"✅ com0com已安装\n路径: {path}\n\n可以使用串口连接方式。")
                break
        if not found:
            result = messagebox.askyesno("com0com未安装", "❌ 未找到com0com虚拟串口驱动\n\n是否自动下载安装？")
            if result:
                self._install_com0com()
    
    def _install_com0com(self):
        try:
            self.add_output("⏳ 正在下载安装com0com...")
            
            import mindplus_usb
            bridge = mindplus_usb.MindPlusUSBBridge()
            
            success = bridge._find_com0com()
            
            if success:
                self.add_output("✅ com0com安装成功!")
                messagebox.showinfo("安装成功", "✅ com0com虚拟串口驱动安装成功!\n\n已创建虚拟串口对: COM19 ↔ COM20\n\nMind+可连接 COM19 端口")
            else:
                self.add_output("❌ com0com安装失败，请手动安装")
                messagebox.showwarning("安装失败", "❌ 自动安装失败\n\n请手动下载安装:\nhttps://sourceforge.net/projects/com0com/\n\n或使用管理员权限重新运行程序")
                
        except Exception as e:
            self.add_output(f"❌ 安装com0com出错: {e}")
            messagebox.showerror("安装错误", f"安装com0com时发生错误: {e}")

    def _start_mindplus_services(self):
        try:
            import mindplus_usb
            
            mode = self._mindplus_mode.get()
            if mode == 'tcp':
                port = int(self._tcp_port_var.get())
                mindplus_usb.start_mindplus_services(tcp_port=port)
                self.add_output(f"✅ Mind+ TCP服务已启动 (端口: {port})")
            else:
                serial_port = self._serial_port_var.get()
                mindplus_usb.start_mindplus_services(serial_port=serial_port)
                self.add_output(f"✅ Mind+串口桥接服务已启动 ({serial_port})")
            
            self._mindplus_services_running = True
            self.mindplus_status.config(text="🖥️ Mind+: 运行中", foreground="green")
            
        except Exception as e:
            self.add_output(f"❌ 启动Mind+服务失败: {e}")
            messagebox.showerror("启动失败", f"无法启动Mind+服务: {e}")

    def _stop_mindplus_services(self):
        try:
            import mindplus_usb
            mindplus_usb.stop_mindplus_services()
            self.add_output("⏹ Mind+服务已停止")
            self._mindplus_services_running = False
            self.mindplus_status.config(text="🖥️ Mind+: 已停止", foreground="orange")
        except Exception as e:
            self.add_output(f"❌ 停止Mind+服务失败: {e}")

    # ────────── 帮助 ──────────

    def _show_help(self):
        help_text = """mPython掌控板虚拟机 - 集成版 使用说明

1. 启动虚拟机: 点击"启动虚拟机"按钮
2. 连接虚拟机: 启动后自动连接，或点击"连接"
3. 编辑代码: 在右侧代码编辑区输入Python代码
4. 运行代码: 按F5或点击"运行"
5. 查看结果: OLED/RGB在左侧虚拟掌控板显示
6. 传感器数据: 左侧面板实时显示模拟传感器值

快捷键:
  Ctrl+O  打开文件
  Ctrl+S  保存文件
  F5      运行代码
  F6      停止运行

注意: 代码中使用 from mpython_sim import * 导入掌控板API"""
        messagebox.showinfo("使用说明", help_text)

    def _show_about(self):
        messagebox.showinfo("关于",
            "mPython掌控板虚拟机 教育版 v2.1\n\n"
            "完整的掌控板硬件模拟环境\n"
            "支持OLED显示、RGB LED、按键、触摸按键、传感器\n"
            "兼容Mind+生成的Python代码\n\n"
            "教育功能:\n"
            "  - 分阶段教程系统\n"
            "  - 丰富示例代码库\n"
            "  - 实时API文档\n"
            "  - 组件说明面板\n"
            "  - 学习进度记录")

    # ────────── 教程系统 ──────────

    def _show_tutorial_select(self):
        tutorial_window = tk.Toplevel(self.root)
        tutorial_window.title("选择教程")
        tutorial_window.geometry("600x500")
        tutorial_window.transient(self.root)
        tutorial_window.grab_set()

        tutorials = [
            {"id": 1, "title": "第1课: 点亮LED", "desc": "学习如何控制RGB LED灯", "difficulty": "入门"},
            {"id": 2, "title": "第2课: OLED显示", "desc": "学习在OLED屏幕上显示文字", "difficulty": "入门"},
            {"id": 3, "title": "第3课: 按键控制", "desc": "学习使用按钮控制LED", "difficulty": "基础"},
            {"id": 4, "title": "第4课: 触摸感应", "desc": "学习使用触摸按键", "difficulty": "基础"},
            {"id": 5, "title": "第5课: 传感器数据", "desc": "学习读取传感器数据", "difficulty": "进阶"},
            {"id": 6, "title": "第6课: 综合项目", "desc": "制作一个环境监测器", "difficulty": "进阶"},
        ]

        listbox = tk.Listbox(tutorial_window, font=("Arial", 12))
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for i, t in enumerate(tutorials):
            status = " ✅" if t["id"] in self._completed_tutorials else ""
            listbox.insert(tk.END, f"{t['title']} [{t['difficulty']}]{status}")

        def select_tutorial(event=None):
            idx = listbox.curselection()
            if idx:
                tutorial_window.destroy()
                self._start_tutorial(tutorials[idx[0]])
            else:
                messagebox.showinfo("提示", "请先选择一个教程！")

        listbox.bind('<Double-1>', select_tutorial)

        ttk.Button(tutorial_window, text="开始学习", command=select_tutorial).pack(pady=10)

    def _start_tutorial(self, tutorial):
        self._current_tutorial = tutorial["id"]
        
        tutorial_data = {
            1: {
                "title": "第1课: 点亮LED",
                "steps": [
                    "欢迎来到第1课！在这节课中，你将学习如何控制RGB LED灯。",
                    "RGB LED有三个颜色通道：红色、绿色和蓝色。",
                    "每个通道的亮度范围是0-255。",
                    "尝试修改代码中的数值来改变LED颜色！",
                ],
                "code": """# 第1课: 点亮LED
# 学习如何控制RGB LED灯
# 修改下面的数值来改变颜色

from mpython_sim import *

# 设置LED颜色 (RGB 0-255)
rgb[0] = (255, 0, 0)    # LED1: 红色
rgb[1] = (0, 255, 0)    # LED2: 绿色
rgb[2] = (0, 0, 255)    # LED3: 蓝色

rgb.write()  # 应用颜色设置

# 显示说明
oled.fill(0)
oled.DispChar("LED Lesson 1", 0, 0, 1)
oled.DispChar("RGB Colors", 0, 20, 1)
oled.DispChar("Red Green Blue", 0, 40, 1)
oled.show()""",
            },
            2: {
                "title": "第2课: OLED显示",
                "steps": [
                    "欢迎来到第2课！学习在OLED屏幕上显示信息。",
                    "OLED屏幕是128x64像素的单色显示屏。",
                    "使用 oled.DispChar() 来显示文字。",
                    "使用 oled.show() 来刷新显示。",
                ],
                "code": """# 第2课: OLED显示
# 学习在OLED屏幕上显示文字

from mpython_sim import *

# 清除屏幕
oled.fill(0)

# 在不同位置显示文字
oled.DispChar("Hello World!", 0, 0, 1)
oled.DispChar("mPython VM", 0, 16, 1)
oled.DispChar("OLED Display", 0, 32, 1)
oled.DispChar("Lesson 2", 0, 48, 1)

# 刷新显示
oled.show()""",
            },
            3: {
                "title": "第3课: 按键控制",
                "steps": [
                    "欢迎来到第3课！学习使用按钮控制LED。",
                    "掌控板有两个物理按钮：A和B。",
                    "使用 button_a.is_pressed() 来检测按钮状态。",
                    "运行代码后，尝试点击按钮A和B！",
                ],
                "code": """# 第3课: 按键控制
# 学习使用按钮控制LED

from mpython_sim import *

# 初始化LED为关闭状态
rgb[0] = (0, 0, 0)
rgb[1] = (0, 0, 0)
rgb[2] = (0, 0, 0)
rgb.write()

oled.fill(0)
oled.DispChar("Press Button A/B", 0, 0, 1)
oled.show()

while True:
    # 检测按钮A
    if button_a.is_pressed():
        rgb[0] = (255, 0, 0)  # 红色
    else:
        rgb[0] = (0, 0, 0)
    
    # 检测按钮B
    if button_b.is_pressed():
        rgb[1] = (0, 255, 0)  # 绿色
    else:
        rgb[1] = (0, 0, 0)
    
    rgb.write()
    sleep_ms(100)""",
            },
            4: {
                "title": "第4课: 触摸感应",
                "steps": [
                    "欢迎来到第4课！学习使用触摸按键。",
                    "掌控板有6个触摸按键：P Y T H O N。",
                    "触摸按键可以检测手指的触摸。",
                    "运行代码后，尝试触摸不同的按键！",
                ],
                "code": """# 第4课: 触摸感应
# 学习使用触摸按键

from mpython_sim import *

rgb[0] = (0, 0, 0)
rgb[1] = (0, 0, 0)
rgb[2] = (0, 0, 0)
rgb.write()

oled.fill(0)
oled.DispChar("Touch P Y T H O N", 0, 0, 1)
oled.show()

while True:
    # 触摸P键 - 红色
    if touchpad_p.is_pressed():
        rgb[0] = (255, 0, 0)
    else:
        rgb[0] = (0, 0, 0)
    
    # 触摸Y键 - 绿色
    if touchpad_y.is_pressed():
        rgb[1] = (0, 255, 0)
    else:
        rgb[1] = (0, 0, 0)
    
    # 触摸T键 - 蓝色
    if touchpad_t.is_pressed():
        rgb[2] = (0, 0, 255)
    else:
        rgb[2] = (0, 0, 0)
    
    rgb.write()
    sleep_ms(100)""",
            },
            5: {
                "title": "第5课: 传感器数据",
                "steps": [
                    "欢迎来到第5课！学习读取传感器数据。",
                    "掌控板内置多种传感器：加速度计、陀螺仪、光线、声音等。",
                    "传感器数据会实时更新。",
                    "尝试移动或遮挡光线传感器来观察变化！",
                ],
                "code": """# 第5课: 传感器数据
# 学习读取传感器数据

from mpython_sim import *

while True:
    oled.fill(0)
    
    # 读取加速度计数据
    accel = accelerometer.get()
    oled.DispChar("Accel:", 0, 0, 1)
    oled.DispChar(f"X:{accel['x']:.1f}", 0, 16, 1)
    oled.DispChar(f"Y:{accel['y']:.1f}", 64, 16, 1)
    oled.DispChar(f"Z:{accel['z']:.1f}", 0, 32, 1)
    
    # 读取光线传感器
    light_val = light.read()
    oled.DispChar(f"Light:{light_val}", 0, 48, 1)
    
    oled.show()
    sleep_ms(200)""",
            },
            6: {
                "title": "第6课: 综合项目",
                "steps": [
                    "欢迎来到第6课！这是一个综合项目。",
                    "制作一个环境监测器，显示温度、湿度和光线。",
                    "使用学到的所有知识来完成这个项目！",
                    "尝试修改代码来添加更多功能！",
                ],
                "code": """# 第6课: 综合项目 - 环境监测器
# 制作一个环境监测器

from mpython_sim import *

while True:
    oled.fill(0)
    
    # 标题
    oled.DispChar("Environment", 0, 0, 1)
    oled.DispChar("Monitor", 0, 16, 1)
    
    # 显示传感器数据
    light_val = light.read()
    sound_val = sound.read()
    
    oled.DispChar(f"Light: {light_val}", 0, 32, 1)
    oled.DispChar(f"Sound: {sound_val}", 0, 48, 1)
    
    # 根据光线强度改变LED颜色
    if light_val < 200:
        rgb[0] = (255, 255, 0)  # 黄色 - 光线暗
    else:
        rgb[0] = (0, 255, 0)    # 绿色 - 光线亮
    
    rgb.write()
    oled.show()
    sleep_ms(200)""",
            },
        }

        data = tutorial_data.get(tutorial["id"], {})
        if data:
            self.code_text.delete("1.0", tk.END)
            self.code_text.insert(tk.END, data["code"])
            
            tutorial_dialog = tk.Toplevel(self.root)
            tutorial_dialog.title(data["title"])
            tutorial_dialog.geometry("500x400")
            tutorial_dialog.transient(self.root)
            
            text = scrolledtext.ScrolledText(tutorial_dialog, font=("Arial", 12))
            text.pack(fill=tk.BOTH, expand=True)
            for i, step in enumerate(data["steps"], 1):
                text.insert(tk.END, f"📌 步骤{i}: {step}\n\n")
            text.config(state=tk.DISABLED)
            
            def mark_complete():
                if tutorial["id"] not in self._completed_tutorials:
                    self._completed_tutorials.append(tutorial["id"])
                    self._save_tutorial_progress()
                    self.add_output(f"🎉 恭喜完成教程: {data['title']}")
                tutorial_dialog.destroy()
            
            ttk.Button(tutorial_dialog, text="完成", command=mark_complete).pack(pady=10)

    def _load_tutorial_progress(self):
        try:
            import json
            progress_file = os.path.join(os.path.expanduser("~"), ".mpython-vm", "tutorial_progress.json")
            if os.path.exists(progress_file):
                with open(progress_file, 'r') as f:
                    self._completed_tutorials = json.load(f)
        except:
            pass

    def _save_tutorial_progress(self):
        try:
            import json
            progress_dir = os.path.join(os.path.expanduser("~"), ".mpython-vm")
            os.makedirs(progress_dir, exist_ok=True)
            progress_file = os.path.join(progress_dir, "tutorial_progress.json")
            with open(progress_file, 'w') as f:
                json.dump(self._completed_tutorials, f)
        except:
            pass

    # ────────── 示例代码选择 ──────────

    def _show_example_select(self):
        example_window = tk.Toplevel(self.root)
        mode_name = "mPython" if self._current_mode.get() == "mpython" else "PinPong"
        example_window.title(f"选择示例代码 - {mode_name}模式")
        example_window.geometry("600x500")
        example_window.transient(self.root)
        example_window.grab_set()

        categories = [
            {"name": "基础入门", "mode": "mpython", "examples": [
                ("LED闪烁", "rgb_blink"),
                ("OLED显示", "oled_text"),
                ("按键检测", "button_check"),
            ]},
            {"name": "传感器", "mode": "mpython", "examples": [
                ("加速度计", "sensor_accel"),
                ("光线传感器", "sensor_light"),
                ("声音传感器", "sensor_sound"),
            ]},
            {"name": "交互控制", "mode": "mpython", "examples": [
                ("按键控制LED", "button_control"),
                ("触摸按键", "touch_control"),
                ("传感器控制LED", "sensor_led"),
            ]},
            {"name": "PinPong库", "mode": "pinpong", "examples": [
                ("PinPong OLED", "pinpong_oled"),
                ("PinPong RGB", "pinpong_rgb"),
                ("PinPong 按键", "pinpong_button"),
                ("PinPong 传感器", "pinpong_sensor"),
            ]},
            {"name": "综合项目", "mode": "mpython", "examples": [
                ("环境监测器", "env_monitor"),
                ("RGB彩虹", "rgb_rainbow"),
                ("心跳检测", "heartbeat_sim"),
            ]},
        ]

        # 根据当前模式过滤示例
        current_mode = self._current_mode.get()
        if current_mode == "mpython":
            categories = [c for c in categories if c["mode"] in ("mpython", "both")]
        else:
            categories = [c for c in categories if c["mode"] in ("pinpong", "both")]

        example_code = {
            "rgb_blink": """# LED闪烁
# 让三个LED轮流闪烁

from mpython_sim import *

while True:
    # 红色
    rgb[0] = (255, 0, 0)
    rgb[1] = (0, 0, 0)
    rgb[2] = (0, 0, 0)
    rgb.write()
    sleep_ms(300)
    
    # 绿色
    rgb[0] = (0, 0, 0)
    rgb[1] = (255, 0, 0)
    rgb[2] = (0, 0, 0)
    rgb.write()
    sleep_ms(300)
    
    # 蓝色
    rgb[0] = (0, 0, 0)
    rgb[1] = (0, 0, 0)
    rgb[2] = (255, 0, 0)
    rgb.write()
    sleep_ms(300)""",
            "oled_text": """# OLED显示
# 在屏幕上显示各种信息

from mpython_sim import *

oled.fill(0)
oled.DispChar("mPython VM", 0, 0, 1)
oled.DispChar("OLED Test", 0, 16, 1)
oled.DispChar("128x64", 0, 32, 1)
oled.DispChar("Ready!", 0, 48, 1)
oled.show()""",
            "button_check": """# 按键检测
# 检测按钮状态并显示

from mpython_sim import *

while True:
    oled.fill(0)
    
    if button_a.is_pressed():
        oled.DispChar("Button A: PRESSED", 0, 0, 1)
    else:
        oled.DispChar("Button A: RELEASED", 0, 0, 1)
    
    if button_b.is_pressed():
        oled.DispChar("Button B: PRESSED", 0, 16, 1)
    else:
        oled.DispChar("Button B: RELEASED", 0, 16, 1)
    
    oled.show()
    sleep_ms(100)""",
            "sensor_accel": """# 加速度计
# 读取并显示加速度数据

from mpython_sim import *

while True:
    oled.fill(0)
    accel = accelerometer.get()
    
    oled.DispChar("Accelerometer", 0, 0, 1)
    oled.DispChar(f"X: {accel['x']:.2f}", 0, 16, 1)
    oled.DispChar(f"Y: {accel['y']:.2f}", 0, 32, 1)
    oled.DispChar(f"Z: {accel['z']:.2f}", 0, 48, 1)
    
    oled.show()
    sleep_ms(100)""",
            "sensor_light": """# 光线传感器
# 读取环境光线强度

from mpython_sim import *

while True:
    oled.fill(0)
    light_val = light.read()
    
    oled.DispChar("Light Sensor", 0, 0, 1)
    oled.DispChar(f"Value: {light_val}", 0, 16, 1)
    
    if light_val < 200:
        oled.DispChar("Dark", 0, 32, 1)
        rgb[0] = (255, 255, 0)
    else:
        oled.DispChar("Bright", 0, 32, 1)
        rgb[0] = (0, 255, 0)
    
    rgb.write()
    oled.show()
    sleep_ms(200)""",
            "sensor_sound": """# 声音传感器
# 读取环境声音强度

from mpython_sim import *

while True:
    oled.fill(0)
    sound_val = sound.read()
    
    oled.DispChar("Sound Sensor", 0, 0, 1)
    oled.DispChar(f"Value: {sound_val}", 0, 16, 1)
    
    if sound_val > 500:
        oled.DispChar("LOUD!", 0, 32, 1)
        rgb[0] = (255, 0, 0)
    else:
        oled.DispChar("Quiet", 0, 32, 1)
        rgb[0] = (0, 0, 0)
    
    rgb.write()
    oled.show()
    sleep_ms(100)""",
            "button_control": """# 按键控制LED
# 使用按钮控制LED开关

from mpython_sim import *

rgb[0] = (0, 0, 0)
rgb[1] = (0, 0, 0)
rgb.write()

while True:
    if button_a.is_pressed():
        rgb[0] = (255, 0, 0)
    else:
        rgb[0] = (0, 0, 0)
    
    if button_b.is_pressed():
        rgb[1] = (0, 255, 0)
    else:
        rgb[1] = (0, 0, 0)
    
    rgb.write()
    sleep_ms(50)""",
            "touch_control": """# 触摸控制
# 使用触摸按键控制LED

from mpython_sim import *

rgb[0] = (0, 0, 0)
rgb[1] = (0, 0, 0)
rgb[2] = (0, 0, 0)
rgb.write()

while True:
    rgb[0] = (255, 0, 0) if touchpad_p.is_pressed() else (0, 0, 0)
    rgb[1] = (0, 255, 0) if touchpad_y.is_pressed() else (0, 0, 0)
    rgb[2] = (0, 0, 255) if touchpad_t.is_pressed() else (0, 0, 0)
    rgb.write()
    sleep_ms(50)""",
            "sensor_led": """# 传感器控制LED
# 根据传感器值控制LED颜色

from mpython_sim import *

while True:
    light_val = light.read()
    
    if light_val < 100:
        rgb[0] = (255, 255, 0)  # 黄色
    elif light_val < 300:
        rgb[0] = (0, 255, 0)    # 绿色
    else:
        rgb[0] = (0, 0, 255)    # 蓝色
    
    rgb.write()
    sleep_ms(100)""",
            "env_monitor": """# 环境监测器
# 综合监测各种环境参数

from mpython_sim import *

while True:
    oled.fill(0)
    
    oled.DispChar("Environment", 0, 0, 1)
    oled.DispChar(f"Light: {light.read()}", 0, 16, 1)
    oled.DispChar(f"Sound: {sound.read()}", 0, 32, 1)
    
    accel = accelerometer.get()
    oled.DispChar(f"Accel: {accel['x']:.1f}", 0, 48, 1)
    
    oled.show()
    sleep_ms(200)""",
            "rgb_rainbow": """# RGB彩虹效果
# 创建彩虹渐变效果

from mpython_sim import *
import math

step = 0
while True:
    r = int(128 + 127 * math.sin(step * 0.05))
    g = int(128 + 127 * math.sin(step * 0.05 + 2))
    b = int(128 + 127 * math.sin(step * 0.05 + 4))
    
    rgb[0] = (r, 0, 0)
    rgb[1] = (0, g, 0)
    rgb[2] = (0, 0, b)
    rgb.write()
    
    step += 1
    sleep_ms(20)""",
            "heartbeat_sim": """# 心跳模拟器
# 模拟心跳脉冲效果

from mpython_sim import *

while True:
    # 心跳脉冲
    for i in range(0, 255, 10):
        rgb[0] = (i, 0, 0)
        rgb.write()
        sleep_ms(20)
    
    for i in range(255, 0, -10):
        rgb[0] = (i, 0, 0)
        rgb.write()
        sleep_ms(20)
    
    sleep_ms(500)""",
            "pinpong_oled": """# PinPong OLED显示
# 使用PinPong库控制OLED

from pinpong import *

init()
oled = get_oled()

oled.clear()
oled.write("PinPong")
oled.write("OLED Test")
oled.write("128x64")
oled.show()""",
            "pinpong_rgb": """# PinPong RGB控制
# 使用PinPong库控制RGB LED

from pinpong import *

init()
rgb = get_rgb()

while True:
    rgb.red()
    delay(500)
    rgb.green()
    delay(500)
    rgb.blue()
    delay(500)
    rgb.write_color("yellow")
    delay(500)""",
            "pinpong_button": """# PinPong 按键检测
# 使用PinPong库检测按键

from pinpong import *

init()
oled = get_oled()

while True:
    oled.clear()
    
    if Button.A.read_digital():
        oled.write("Button A: ON")
    else:
        oled.write("Button A: OFF")
    
    if Button.B.read_digital():
        oled.write("Button B: ON")
    else:
        oled.write("Button B: OFF")
    
    oled.show()
    delay(100)""",
            "pinpong_sensor": """# PinPong 传感器读取
# 使用PinPong库读取传感器

from pinpong import *

init()
oled = get_oled()
rgb = get_rgb()

while True:
    oled.clear()
    
    light_val = Pin(3).read_analog()
    oled.write(f"Light: {light_val}")
    
    if light_val > 2000:
        rgb.write_color("green")
    else:
        rgb.write_color("yellow")
    
    oled.show()
    delay(200)""",
        }

        listbox = tk.Listbox(example_window, font=("Arial", 12))
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for cat in categories:
            listbox.insert(tk.END, f"=== {cat['name']} ===")
            for name, key in cat["examples"]:
                listbox.insert(tk.END, f"  ▶ {name}")

        def select_example(event):
            idx = listbox.curselection()
            if idx:
                line = listbox.get(idx[0])
                if "▶" in line:
                    example_name = line.strip(" ▶")
                    for cat in categories:
                        for name, key in cat["examples"]:
                            if name == example_name:
                                example_window.destroy()
                                self.code_text.delete("1.0", tk.END)
                                self.code_text.insert(tk.END, example_code.get(key, ""))
                                self.add_output(f"📋 已加载示例: {example_name}")
                                return

        listbox.bind('<Double-1>', select_example)

    # ────────── API文档 ──────────

    def _show_api_docs(self):
        api_window = tk.Toplevel(self.root)
        api_window.title("API文档")
        api_window.geometry("800x600")
        api_window.transient(self.root)

        notebook = ttk.Notebook(api_window)
        notebook.pack(fill=tk.BOTH, expand=True)

        docs = {
            "LED控制": """RGB LED 控制

rgb[index] = (r, g, b)
  设置LED颜色，index为0-2，r/g/b为0-255

rgb.write()
  应用颜色设置到LED

示例:
  rgb[0] = (255, 0, 0)  # 设置LED1为红色
  rgb[1] = (0, 255, 0)  # 设置LED2为绿色
  rgb.write()           # 应用设置""",
            "OLED显示": """OLED 显示屏控制

oled.fill(color)
  填充屏幕，color为0(黑)或1(白)

oled.DispChar(text, x, y, size)
  在指定位置显示文字
  x: 水平位置(0-127)
  y: 垂直位置(0-63)
  size: 字体大小(1或2)

oled.show()
  刷新显示

示例:
  oled.fill(0)
  oled.DispChar("Hello", 0, 0, 1)
  oled.show()""",
            "按键": """物理按键

button_a.is_pressed()
  返回按钮A是否被按下(True/False)

button_b.is_pressed()
  返回按钮B是否被按下(True/False)

示例:
  if button_a.is_pressed():
      rgb[0] = (255, 0, 0)""",
            "触摸按键": """触摸按键

touchpad_p.is_pressed()
touchpad_y.is_pressed()
touchpad_t.is_pressed()
touchpad_h.is_pressed()
touchpad_o.is_pressed()
touchpad_n.is_pressed()
  返回对应触摸键是否被触摸

示例:
  if touchpad_p.is_pressed():
      rgb[0] = (255, 0, 0)""",
            "传感器": """传感器

accelerometer.get()
  返回加速度计数据 {'x': val, 'y': val, 'z': val}

gyroscope.get()
  返回陀螺仪数据 {'x': val, 'y': val, 'z': val}

magnetometer.get()
  返回地磁数据 {'x': val, 'y': val, 'z': val}

light.read()
  返回光线传感器值(0-1023)

sound.read()
  返回声音传感器值(0-1023)

示例:
  accel = accelerometer.get()
  print(accel['x'])""",
            "延时": """延时函数

sleep_ms(ms)
  延时指定毫秒数

sleep_us(us)
  延时指定微秒数

示例:
  sleep_ms(500)  # 延时500毫秒""",
        }

        for title, content in docs.items():
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=title)
            
            text = scrolledtext.ScrolledText(frame, font=("Consolas", 11))
            text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text.insert(tk.END, content)
            text.config(state=tk.DISABLED)

    # ────────── 模式切换 ──────────

    def _set_mode(self, mode):
        """设置当前模式"""
        if mode != self._current_mode.get():
            self._current_mode.set(mode)

    def _on_mode_changed(self):
        """模式切换时的界面更新"""
        mode = self._current_mode.get()

        # 1. 更新模式指示器
        if mode == "mpython":
            self.mode_indicator.config(text="● mPython", foreground="#2196F3")
            self.mp_btn.config(text="▸ mPython")
            self.pp_btn.config(text="  PinPong")
        else:
            self.mode_indicator.config(text="● PinPong", foreground="#FF5722")
            self.mp_btn.config(text="  mPython")
            self.pp_btn.config(text="▸ PinPong")

        # 2. 更新硬件面板标题
        if mode == "mpython":
            self._board_label.config(text="mPython掌控板")
        else:
            self._board_label.config(text="PinPong掌控板")

        # 3. 更新代码编辑区提示
        if mode == "mpython":
            self._code_label.config(text="代码编辑区（从Mind+复制代码粘贴到这里运行）")
        else:
            self._code_label.config(text="代码编辑区（使用PinPong库编写代码）")

        # 4. 更新默认代码
        self.code_text.delete("1.0", tk.END)
        if mode == "mpython":
            self.code_text.insert(tk.END, """/*! 
  * MindPlus 
  * mpython 
  * 
  */ 
#include <MPython.h> 

// 主程序开始 
void setup() { 
    mPython.begin(); 
} 
void loop() { 
    display.setCursorLine(1); 
    display.printLine("Mind+");
}""")
        else:
            self.code_text.insert(tk.END, """# PinPong 示例
# 使用pinpong库控制掌控板

from pinpong import *

init()

oled = get_oled()
oled.clear()
oled.write("PinPong Mode")
oled.write("Ready!")
oled.show()

rgb = get_rgb()
rgb.write_color("green")""")

        self.add_output(f"🔄 已切换到 {mode.upper()} 模式")

    # ────────── 组件说明 ──────────

    def _show_component_info(self):
        info_window = tk.Toplevel(self.root)
        info_window.title("组件说明")
        info_window.geometry("700x500")
        info_window.transient(self.root)

        notebook = ttk.Notebook(info_window)
        notebook.pack(fill=tk.BOTH, expand=True)

        components = {
            "OLED显示屏": """OLED显示屏 (128x64)

OLED（有机发光二极管）显示屏是一种自发光显示技术。
掌控板使用的是128x64像素的单色OLED屏幕。

特点:
- 自发光，不需要背光
- 对比度高，显示清晰
- 低功耗
- 响应速度快

使用方法:
- oled.fill(0) - 清除屏幕
- oled.DispChar(text, x, y, size) - 显示文字
- oled.show() - 刷新显示""",
            "RGB LED": """RGB LED

RGB LED是可以发出红、绿、蓝三种颜色的LED灯。
通过混合不同比例的RGB颜色，可以产生各种颜色。

掌控板有3个RGB LED:
- LED1 (P13)
- LED2 (P14)
- LED3 (P15)

颜色范围: 0-255
- (255, 0, 0) = 红色
- (0, 255, 0) = 绿色
- (0, 0, 255) = 蓝色
- (255, 255, 255) = 白色""",
            "物理按键": """物理按键

掌控板有两个物理按键:
- 按键A (P16)
- 按键B (P20)

按键是一种输入设备，用于检测用户的按下操作。
可以通过代码检测按键状态，实现交互式控制。

使用方法:
- button_a.is_pressed() - 检测按键A
- button_b.is_pressed() - 检测按键B""",
            "触摸按键": """触摸按键

掌控板有6个触摸按键: P Y T H O N

触摸按键基于电容感应原理工作。
当手指触摸按键时，电容变化会被检测到。

触摸按键位置:
- P: 最左侧
- Y: P右侧
- T: 中间
- H: T右侧
- O: H右侧
- N: 最右侧

使用方法:
- touchpad_p.is_pressed()
- touchpad_y.is_pressed()
- touchpad_t.is_pressed()
- touchpad_h.is_pressed()
- touchpad_o.is_pressed()
- touchpad_n.is_pressed()""",
            "传感器": """传感器

掌控板集成了多种传感器:

1. 加速度计 (LIS2DH12)
   - 检测设备的加速度
   - 可以检测设备的倾斜角度

2. 陀螺仪 (LIS2DH12)
   - 检测设备的旋转速度
   - 测量角速度

3. 地磁传感器 (MMC5983MA)
   - 检测地球磁场
   - 用于方向识别

4. 光线传感器 (BH1750)
   - 检测环境光线强度
   - 范围: 0-1023

5. 声音传感器 (SPH0645)
   - 检测环境声音强度
   - 范围: 0-1023""",
            "摄像头": """摄像头

掌控板可以外接摄像头模块。
摄像头用于图像采集和AI识别。

支持的功能:
- 拍照
- 视频录制
- AI物体识别
- QR码扫描

使用方法:
- camera.init() - 初始化摄像头
- camera.snapshot() - 拍摄照片
- camera.read() - 读取图像数据""",
        }

        for title, content in components.items():
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=title)
            
            text = scrolledtext.ScrolledText(frame, font=("Arial", 11))
            text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text.insert(tk.END, content)
            text.config(state=tk.DISABLED)

    def _on_exit(self):
        self._running = False
        self.stop_vm()
        self.root.quit()
        self.root.destroy()


def show_splash():
    """Show splash screen, return True when done"""
    root = tk.Tk()
    root.overrideredirect(True)
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 800
    window_height = 500
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    canvas = tk.Canvas(root, width=window_width, height=window_height, bg="white", highlightthickness=0)
    canvas.pack()
    
    # Draw D.O.O.R Logo
    hex_center_x = 200
    hex_center_y = 250
    hex_radius = 80
    
    points = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        px = hex_center_x + hex_radius * math.cos(angle)
        py = hex_center_y + hex_radius * math.sin(angle)
        points.extend([px, py])
    canvas.create_polygon(points, fill="#1a1a1a", outline="#333", width=3)
    
    inner_radius = hex_radius * 0.7
    inner_points = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        px = hex_center_x + inner_radius * math.cos(angle)
        py = hex_center_y + inner_radius * math.sin(angle)
        inner_points.extend([px, py])
    canvas.create_polygon(inner_points, fill="#1a1a1a", outline="#444", width=2)
    
    canvas.create_text(hex_center_x, hex_center_y, text="R", font=("Arial Black", 80), fill="#ffffff")
    
    # Wings
    wing1 = [hex_center_x - hex_radius - 10, hex_center_y - 30,
             hex_center_x - hex_radius * 0.3, hex_center_y - 20,
             hex_center_x - hex_radius * 0.3, hex_center_y + 20,
             hex_center_x - hex_radius - 10, hex_center_y + 30]
    canvas.create_polygon(wing1, fill="#1a1a1a", outline="#333")
    
    wing2 = [hex_center_x + hex_radius + 10, hex_center_y - 30,
             hex_center_x + hex_radius * 0.3, hex_center_y - 20,
             hex_center_x + hex_radius * 0.3, hex_center_y + 20,
             hex_center_x + hex_radius + 10, hex_center_y + 30]
    canvas.create_polygon(wing2, fill="#1a1a1a", outline="#333")
    
    canvas.create_text(hex_center_x, hex_center_y + 120, text="D.O.O.R.", font=("Arial Black", 24), fill="#1a1a1a")
    canvas.create_text(hex_center_x, hex_center_y + 145, text="Door the Oneness Organization of Rovers", font=("Arial", 10), fill="#666")
    canvas.create_text(600, 250, text="作者：末日独白", font=("SimHei", 36), fill="#1a1a1a")
    canvas.create_text(400, 450, text="mPython Virtual Machine v2.0", font=("Arial", 14), fill="#999")
    
    # Animation
    alpha = [0.0]
    
    def fade_in():
        if alpha[0] < 1.0:
            alpha[0] = min(alpha[0] + 0.08, 1.0)
            root.attributes('-alpha', alpha[0])
            root.after(20, fade_in)
        else:
            root.after(1500, fade_out)
    
    def fade_out():
        if alpha[0] > 0:
            alpha[0] = max(alpha[0] - 0.08, 0.0)
            root.attributes('-alpha', alpha[0])
            root.after(20, fade_out)
        else:
            root.destroy()
    
    fade_in()
    root.mainloop()


def main():
    show_splash()
    
    root = tk.Tk()
    root.title("mPython掌控板虚拟机 - 教育版")
    root.geometry("1300x800")
    root.minsize(1100, 700)
    
    app = IntegratedVMApp(root)
    root.protocol("WM_DELETE_WINDOW", app._on_exit)
    root.mainloop()


if __name__ == "__main__":
    main()