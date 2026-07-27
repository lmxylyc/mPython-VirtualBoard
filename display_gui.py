import tkinter as tk
from tkinter import ttk
import socket
import json
import threading
import time
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'simulator'))
from theme import apply_theme, DarkTheme

class DisplayGUI:
    def __init__(self, root, vm_host='127.0.0.1', vm_port=7778):
        self.root = root
        self.theme = apply_theme(root, DarkTheme)
        self.root.title("mPython Virtual Board")
        self.root.geometry("420x860")
        self.root.attributes('-topmost', True)
        self.root.lift()
        self.root.focus_force()
        
        self.vm_host = vm_host
        self.vm_port = vm_port
        self.socket = None
        self._running = True
        self._last_state = None
        
        self._connected_sensors = {
            'camera': False,
            'microphone': True,
            'speaker': False,
            'battery': False,
            'display': False,
            'accelerometer': True,
            'gyro': False,
            'magnetic': False,
            'light': False,
            'sound': True
        }
        
        self._cached_sensors = None
        
        self._create_widgets()
        self._start_polling()
        self._detect_sensors_async()
    
    def _create_widgets(self):
        t = self.theme

        top_bar = tk.Frame(self.root, bg=t.BG_PANEL, height=40)
        top_bar.pack(fill=tk.X, side=tk.TOP)
        top_bar.pack_propagate(False)
        tk.Label(top_bar, text="◆", fg=t.ACCENT, bg=t.BG_PANEL,
                 font=("Segoe UI", 14)).pack(side=tk.LEFT, padx=(12, 4))
        tk.Label(top_bar, text="Virtual Board", fg=t.FG, bg=t.BG_PANEL,
                 font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)
        tk.Button(top_bar, text="⚙", width=3, command=self._show_settings,
                  bg=t.BUTTON_BG, fg=t.FG, activebackground=t.BUTTON_HOVER,
                  activeforeground=t.FG, font=("Segoe UI", 10),
                  relief=tk.FLAT, bd=0, padx=6, pady=2, cursor="hand2").pack(side=tk.RIGHT, padx=10)

        canvas = tk.Canvas(self.root, bg=t.BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=t.BG)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self._create_oled(scroll_frame, t)
        self._create_rgb(scroll_frame, t)
        self._create_buttons(scroll_frame, t)
        self._create_touch(scroll_frame, t)
        self._create_sensors(scroll_frame, t)
        self._create_control(scroll_frame, t)
        self._create_status(scroll_frame, t)
    
    def _create_oled(self, parent, t):
        oled_frame = tk.Frame(parent, bg=t.BG_CARD, bd=0, highlightthickness=0)
        oled_frame.pack(fill=tk.X, padx=4, pady=4)

        header = tk.Frame(oled_frame, bg=t.BG_CARD)
        header.pack(fill=tk.X, padx=12, pady=(10, 0))
        tk.Label(header, text="OLED 显示屏", fg=t.FG, bg=t.BG_CARD,
                 font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
        tk.Label(header, text="128×64", fg=t.FG_DIM, bg=t.BG_CARD,
                 font=("Segoe UI", 8)).pack(side=tk.RIGHT)

        outer_frame = tk.Frame(oled_frame, bg=t.OLED_FRAME, bd=0, highlightthickness=0)
        outer_frame.pack(padx=16, pady=10)

        inner_frame = tk.Frame(outer_frame, bg=t.OLED_BG, bd=0, highlightthickness=0)
        inner_frame.pack(padx=6, pady=6)

        self.oled_text = tk.Label(inner_frame, text="等待连接...", font=("Consolas", 10),
                                  bg=t.OLED_BG, fg=t.OLED_FG, justify=tk.LEFT, anchor="nw",
                                  width=21, height=8, padx=4, pady=4)
        self.oled_text.pack()

        self.oled_status = tk.Label(header, text="●", fg=t.ERROR, bg=t.BG_CARD,
                                    font=("Segoe UI", 10))
        self.oled_status.pack(side=tk.RIGHT, padx=(0, 40))

    def _create_rgb(self, parent, t):
        rgb_frame = tk.Frame(parent, bg=t.BG_CARD, bd=0, highlightthickness=0)
        rgb_frame.pack(fill=tk.X, padx=4, pady=4)

        header = tk.Frame(rgb_frame, bg=t.BG_CARD)
        header.pack(fill=tk.X, padx=12, pady=(10, 0))
        tk.Label(header, text="RGB LED", fg=t.FG, bg=t.BG_CARD,
                 font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)

        self._rgb_canvas = tk.Canvas(rgb_frame, height=50, bg=t.BG_CARD, highlightthickness=0)
        self._rgb_canvas.pack(fill=tk.X, padx=12, pady=8)
        self.rgb_indicators = []
        for i in range(3):
            x = 40 + i * 90
            indicator = self._rgb_canvas.create_oval(x, 12, x + 34, 40,
                                                     fill=t.RGB_OFF, outline=t.RGB_OUTLINE, width=2)
            self.rgb_indicators.append(indicator)
            self._rgb_canvas.create_text(x + 17, 50, text=f"RGB {i+1}",
                                         fill=t.FG_DIM, font=("Segoe UI", 8))

    def _create_buttons(self, parent, t):
        btn_frame = tk.Frame(parent, bg=t.BG_CARD, bd=0, highlightthickness=0)
        btn_frame.pack(fill=tk.X, padx=4, pady=4)

        header = tk.Frame(btn_frame, bg=t.BG_CARD)
        header.pack(fill=tk.X, padx=12, pady=(10, 0))
        tk.Label(header, text="按键", fg=t.FG, bg=t.BG_CARD,
                 font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)

        btn_row = tk.Frame(btn_frame, bg=t.BG_CARD)
        btn_row.pack(pady=12)

        self.btn_a = tk.Button(btn_row, text="按键 A", width=12,
                               bg=t.BUTTON_BG, fg=t.FG,
                               activebackground=t.ACCENT, activeforeground=t.BG,
                               font=("Segoe UI", 9, "bold"),
                               relief=tk.FLAT, bd=0, padx=8, pady=6, cursor="hand2")
        self.btn_a.pack(side=tk.LEFT, padx=12)
        self.btn_a.bind('<ButtonPress-1>', lambda e: self._send_button('A', True))
        self.btn_a.bind('<ButtonRelease-1>', lambda e: self._send_button('A', False))

        self.btn_b = tk.Button(btn_row, text="按键 B", width=12,
                               bg=t.BUTTON_BG, fg=t.FG,
                               activebackground=t.ACCENT, activeforeground=t.BG,
                               font=("Segoe UI", 9, "bold"),
                               relief=tk.FLAT, bd=0, padx=8, pady=6, cursor="hand2")
        self.btn_b.pack(side=tk.LEFT, padx=12)
        self.btn_b.bind('<ButtonPress-1>', lambda e: self._send_button('B', True))
        self.btn_b.bind('<ButtonRelease-1>', lambda e: self._send_button('B', False))

    def _create_touch(self, parent, t):
        touch_frame = tk.Frame(parent, bg=t.BG_CARD, bd=0, highlightthickness=0)
        touch_frame.pack(fill=tk.X, padx=4, pady=4)

        header = tk.Frame(touch_frame, bg=t.BG_CARD)
        header.pack(fill=tk.X, padx=12, pady=(10, 0))
        tk.Label(header, text="触摸按键", fg=t.FG, bg=t.BG_CARD,
                 font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
        tk.Label(header, text="P Y T H O N", fg=t.FG_DIM, bg=t.BG_CARD,
                 font=("Segoe UI", 8)).pack(side=tk.RIGHT)

        self._touch_canvas = tk.Canvas(touch_frame, height=55, bg=t.BG_CARD, highlightthickness=0)
        self._touch_canvas.pack(fill=tk.X, padx=12, pady=(4, 10))

        self.touch_indicators = {}
        for i, label in enumerate(['P', 'Y', 'T', 'H', 'O', 'N']):
            x = 20 + i * 42
            indicator = self._touch_canvas.create_oval(x, 10, x + 26, 36,
                                                        fill=t.RGB_OFF, outline=t.RGB_OUTLINE, width=1)
            text = self._touch_canvas.create_text(x + 13, 46, text=label, fill=t.FG_DIM,
                                                  font=("Segoe UI", 9, "bold"))
            self.touch_indicators[label] = indicator
            self._touch_canvas.tag_bind(indicator, '<ButtonPress-1>', lambda e, l=label: self._send_touch(l, True))
            self._touch_canvas.tag_bind(indicator, '<ButtonRelease-1>', lambda e, l=label: self._send_touch(l, False))
            self._touch_canvas.tag_bind(text, '<ButtonPress-1>', lambda e, l=label: self._send_touch(l, True))
            self._touch_canvas.tag_bind(text, '<ButtonRelease-1>', lambda e, l=label: self._send_touch(l, False))

    def _create_sensors(self, parent, t):
        sensor_frame = tk.Frame(parent, bg=t.BG_CARD, bd=0, highlightthickness=0)
        sensor_frame.pack(fill=tk.X, padx=4, pady=4)

        header = tk.Frame(sensor_frame, bg=t.BG_CARD)
        header.pack(fill=tk.X, padx=12, pady=(10, 0))
        tk.Label(header, text="传感器数据", fg=t.FG, bg=t.BG_CARD,
                 font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)

        sensor_grid = tk.Frame(sensor_frame, bg=t.BG_CARD)
        sensor_grid.pack(fill=tk.X, padx=12, pady=(6, 10))

        sensor_items = [
            ("加速度:", "x: 0.00  y: 0.00  z: 1.00"),
            ("光线:", "---"),
            ("声音:", "---"),
        ]
        self.sensor_vars = []
        for i, (label, default) in enumerate(sensor_items):
            cell = tk.Frame(sensor_grid, bg=t.BG_CARD)
            cell.grid(row=i, column=0, sticky="w", padx=6, pady=2)
            tk.Label(cell, text=label, fg=t.FG_DIM, bg=t.BG_CARD,
                     font=("Segoe UI", 9)).pack(side=tk.LEFT)
            var = tk.StringVar(value=default)
            self.sensor_vars.append(var)
            tk.Label(cell, textvariable=var, fg=t.FG, bg=t.BG_CARD,
                     font=("Consolas", 9)).pack(side=tk.LEFT, padx=(4, 0))

    def _create_control(self, parent, t):
        control_frame = tk.Frame(parent, bg=t.BG_CARD, bd=0, highlightthickness=0)
        control_frame.pack(fill=tk.X, padx=4, pady=4)

        header = tk.Frame(control_frame, bg=t.BG_CARD)
        header.pack(fill=tk.X, padx=12, pady=(10, 0))
        tk.Label(header, text="传感器控制", fg=t.FG, bg=t.BG_CARD,
                 font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)

        manual_frame = tk.Frame(control_frame, bg=t.BG_CARD)
        manual_frame.pack(fill=tk.X, padx=12, pady=8)

        self._manual_mode_var = tk.BooleanVar(value=False)
        tk.Checkbutton(manual_frame, text="手动模式", variable=self._manual_mode_var,
                        command=self._toggle_manual_mode,
                        bg=t.BG_CARD, fg=t.FG, activebackground=t.BG_CARD,
                        activeforeground=t.FG, selectcolor=t.BG_INPUT,
                        font=("Segoe UI", 9)).pack(anchor=tk.W)

        light_row = tk.Frame(manual_frame, bg=t.BG_CARD)
        light_row.pack(fill=tk.X, pady=4)
        tk.Label(light_row, text="光线:", width=6, fg=t.FG_DIM, bg=t.BG_CARD,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self._light_slider = ttk.Scale(light_row, from_=0, to=4095, orient=tk.HORIZONTAL,
                                       command=lambda v: self._set_sensor('light', int(float(v))))
        self._light_slider.set(500)
        self._light_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        self._light_label = tk.Label(light_row, text="500", width=6, fg=t.FG, bg=t.BG_CARD,
                                     font=("Consolas", 9))
        self._light_label.pack(side=tk.LEFT)

        sound_row = tk.Frame(manual_frame, bg=t.BG_CARD)
        sound_row.pack(fill=tk.X, pady=4)
        tk.Label(sound_row, text="声音:", width=6, fg=t.FG_DIM, bg=t.BG_CARD,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self._sound_slider = ttk.Scale(sound_row, from_=0, to=4095, orient=tk.HORIZONTAL,
                                        command=lambda v: self._set_sensor('sound', int(float(v))))
        self._sound_slider.set(200)
        self._sound_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        self._sound_label = tk.Label(sound_row, text="200", width=6, fg=t.FG, bg=t.BG_CARD,
                                      font=("Consolas", 9))
        self._sound_label.pack(side=tk.LEFT)

        action_frame = tk.Frame(control_frame, bg=t.BG_CARD)
        action_frame.pack(fill=tk.X, padx=12, pady=(4, 10))

        tk.Label(action_frame, text="加速度控制", fg=t.FG_DIM, bg=t.BG_CARD,
                 font=("Segoe UI", 8)).pack(anchor=tk.W)

        actions = [
            ("静止", lambda: self._set_accel(0.0, 0.0, 1.0)),
            ("摇动", self._shake_action),
            ("前倾", lambda: self._set_accel(0.0, 1.0, 0.1)),
            ("后倾", lambda: self._set_accel(0.0, -1.0, 0.1)),
            ("左倾", lambda: self._set_accel(-1.0, 0.0, 0.1)),
            ("右倾", lambda: self._set_accel(1.0, 0.0, 0.1)),
        ]

        for i in range(2):
            btn_row = tk.Frame(action_frame, bg=t.BG_CARD)
            btn_row.pack(fill=tk.X, pady=2)
            for name, cmd in actions[i*3:(i+1)*3]:
                tk.Button(btn_row, text=name, width=8, command=cmd,
                          bg=t.BUTTON_BG, fg=t.FG, activebackground=t.ACCENT,
                          activeforeground=t.BG, font=("Segoe UI", 8),
                          relief=tk.FLAT, bd=0, padx=6, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=2)

    def _create_status(self, parent, t):
        status_frame = tk.Frame(parent, bg=t.BG_CARD)
        status_frame.pack(fill=tk.X, padx=4, pady=4)

        self.status_label = tk.Label(status_frame, text="● 未连接", fg=t.ERROR, bg=t.BG_CARD,
                                     font=("Segoe UI", 9))
        self.status_label.pack(side=tk.LEFT, padx=12, pady=8)
        self.update_time = tk.Label(status_frame, text="", fg=t.FG_DIM, bg=t.BG_CARD,
                                     font=("Segoe UI", 8))
        self.update_time.pack(side=tk.RIGHT, padx=12)
    
    def _detect_sensors_async(self):
        def detect():
            self._cached_sensors = self._detect_real_sensors()
        threading.Thread(target=detect, daemon=True).start()
    
    def _detect_real_sensors(self):
        devices = []
        
        try:
            import wmi
            c = wmi.WMI()
            
            for dev_name, keywords, label in [
                ('camera', ['camera', '摄像头', 'video'], 'Camera'),
                ('microphone', ['microphone', '麦克风'], 'Microphone'),
                ('speaker', ['speaker', '扬声器'], 'Speaker'),
            ]:
                found = []
                for dev in c.Win32_PnPEntity():
                    name = str(dev.Name).lower()
                    if any(k in name for k in keywords):
                        found.append(dev.Name)
                devices.append((dev_name, label, ', '.join(found[:2]) if found else 'Not detected', bool(found)))
            
            batteries = []
            for dev in c.Win32_Battery():
                batteries.append(f"{dev.Caption} ({dev.EstimatedChargeRemaining}%)")
            devices.append(('battery', 'Battery', ', '.join(batteries) if batteries else 'Not detected', bool(batteries)))
            
            displays = []
            for dev in c.Win32_DesktopMonitor():
                displays.append(dev.Name)
            devices.append(('display', 'Display', ', '.join(displays[:2]) if displays else 'Not detected', bool(displays)))
            
        except:
            try:
                import cv2
                cap = cv2.VideoCapture(0)
                devices.append(('camera', 'Camera', 'Webcam' if cap.isOpened() else 'Not detected', cap.isOpened()))
                cap.release()
            except:
                devices.append(('camera', 'Camera', 'Not detected', False))
            
            try:
                import pyaudio
                pa = pyaudio.PyAudio()
                info = pa.get_host_api_info_by_index(0)
                has_mic = any(pa.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels', 0) > 0 
                            for i in range(info.get('deviceCount', 0)))
                pa.terminate()
                devices.append(('microphone', 'Microphone', 'Detected' if has_mic else 'Not detected', has_mic))
            except:
                devices.append(('microphone', 'Microphone', 'Not detected', False))
            
            try:
                import psutil
                battery = psutil.sensors_battery()
                devices.append(('battery', 'Battery', f"{battery.percent}%{' (Charging)' if battery.power_plugged else ''}" if battery else 'Not detected', bool(battery)))
            except:
                devices.append(('battery', 'Battery', 'Not detected', False))
        
        for dev_name, label in [
            ('accelerometer', 'Accelerometer'),
            ('gyro', 'Gyroscope'),
            ('magnetic', 'Magnetic Sensor'),
            ('light', 'Light Sensor'),
            ('sound', 'Sound Sensor'),
        ]:
            devices.append((dev_name, label, 'Virtual Sensor', True))
        
        return devices
    
    def _show_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Sensor Settings")
        settings_window.geometry("350x500")
        settings_window.attributes('-topmost', True)
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        ttk.Label(settings_window, text="Select Connected Sensors", font=("Arial", 12, "bold")).pack(pady=10)
        
        sensors = self._cached_sensors if self._cached_sensors else [
            (s, s.title(), 'Detecting...', False) for s in ['camera', 'microphone', 'speaker', 'battery', 'display',
                                                            'accelerometer', 'gyro', 'magnetic', 'light', 'sound']
        ]
        
        self._sensor_check_vars = {}
        for sensor_id, name, desc, available in sensors:
            frame = ttk.LabelFrame(settings_window, text=name, padding=5)
            frame.pack(fill=tk.X, padx=10, pady=3)
            
            var = tk.BooleanVar(value=self._connected_sensors.get(sensor_id, False))
            self._sensor_check_vars[sensor_id] = var
            
            check = ttk.Checkbutton(frame, text="Enable", variable=var)
            status_label = ttk.Label(frame, text="✓ Available" if available else "✗ Unavailable", 
                                     font=("Arial", 8), foreground="green" if available else "red")
            
            if not available:
                check.configure(state=tk.DISABLED)
            
            check.pack(side=tk.LEFT)
            status_label.pack(side=tk.RIGHT)
            ttk.Label(frame, text=desc, font=("Arial", 8), foreground="#666").pack(anchor=tk.W, pady=(2, 0))
        
        btn_frame = ttk.Frame(settings_window)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="OK", command=lambda: self._apply_settings(settings_window)).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=settings_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _apply_settings(self, window):
        for sensor_id, var in self._sensor_check_vars.items():
            self._connected_sensors[sensor_id] = var.get()
        
        if self.socket:
            try:
                msg = json.dumps({'action': 'sensor_config', 'sensors': self._connected_sensors}) + "\n"
                self.socket.sendall(msg.encode('utf-8'))
                
                use_real = self._connected_sensors.get('microphone', False) or \
                          self._connected_sensors.get('camera', False) or \
                          self._connected_sensors.get('light', False)
                msg = json.dumps({'action': 'sensor_set_real', 'enabled': use_real}) + "\n"
                self.socket.sendall(msg.encode('utf-8'))
            except:
                self.socket = None
        
        window.destroy()
    
    def _connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.vm_host, self.vm_port))
            self.socket.settimeout(1.0)
            return True
        except:
            self.socket = None
            return False
    
    def _send_button(self, btn, pressed):
        if self.socket:
            try:
                action = 'button_press' if pressed else 'button_release'
                msg = json.dumps({'action': action, 'button': btn}) + "\n"
                self.socket.sendall(msg.encode('utf-8'))
            except:
                self.socket = None
    
    def _send_touch(self, pad, pressed):
        if self.socket:
            try:
                action = 'touch_press' if pressed else 'touch_release'
                msg = json.dumps({'action': action, 'pad': pad}) + "\n"
                self.socket.sendall(msg.encode('utf-8'))
                color = "#2196F3" if pressed else "#555"
                self._touch_canvas.itemconfig(self.touch_indicators[pad], fill=color)
            except:
                self.socket = None
    
    def _set_sensor(self, sensor_type, value):
        if self.socket:
            try:
                msg = json.dumps({'action': 'sensor_set', 'sensor': sensor_type, 'value': value}) + "\n"
                self.socket.sendall(msg.encode('utf-8'))
                if sensor_type == 'light':
                    self._light_label.config(text=str(value))
                elif sensor_type == 'sound':
                    self._sound_label.config(text=str(value))
            except:
                self.socket = None
    
    def _toggle_manual_mode(self):
        if self.socket:
            try:
                msg = json.dumps({'action': 'sensor_manual_mode', 'enabled': self._manual_mode_var.get()}) + "\n"
                self.socket.sendall(msg.encode('utf-8'))
            except:
                self.socket = None
    
    def _set_accel(self, x, y, z):
        if self.socket:
            try:
                msg = json.dumps({'action': 'sensor_set', 'sensor': 'accelerometer', 'value': {'x': x, 'y': y, 'z': z}}) + "\n"
                self.socket.sendall(msg.encode('utf-8'))
            except:
                self.socket = None
    
    def _shake_action(self):
        def shake():
            for _ in range(5):
                for dx, dy in [(2.0, 0.5), (-2.0, -0.5), (0.5, 2.0), (-0.5, -2.0)]:
                    self._set_accel(dx, dy, 0.5)
                    time.sleep(0.1)
            self._set_accel(0.0, 0.0, 1.0)
        threading.Thread(target=shake, daemon=True).start()
    
    def _start_polling(self):
        def poll():
            while self._running:
                if not self.socket and not self._connect():
                    time.sleep(1)
                    continue
                
                try:
                    self.socket.sendall(json.dumps({'action': 'get_state'}).encode('utf-8') + b"\n")
                    response = ""
                    while True:
                        data = self.socket.recv(4096)
                        if not data:
                            self.socket = None
                            break
                        response += data.decode('utf-8')
                        if "\n" in response:
                            response = response.split("\n")[0]
                            break
                    
                    if response:
                        self._last_state = json.loads(response)
                except:
                    self.socket = None
                
                time.sleep(0.1)
        
        threading.Thread(target=poll, daemon=True).start()
        self._schedule_update()
    
    def _schedule_update(self):
        if self._running:
            if self._last_state:
                self._update_display(self._last_state)
                self.status_label.config(text="✅ Connected", foreground="green")
                self.oled_status.config(fg="#0f0")
            else:
                self.status_label.config(text="🔌 Disconnected", foreground="red")
                self.oled_status.config(fg="#f00")
            self.update_time.config(text=time.strftime("%H:%M:%S"))
            self.root.after(100, self._schedule_update)
    
    def _update_display(self, state):
        oled_text = state.get('oled_text', [""] * 8)
        self.oled_text.config(text="\n".join(oled_text))
        
        rgb_colors = state.get('rgb_colors', [(0,0,0),(0,0,0),(0,0,0)])
        for i, color in enumerate(rgb_colors):
            hex_color = '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])
            self._rgb_canvas.itemconfig(self.rgb_indicators[i], fill=hex_color)
        
        sensors = state.get('sensors', {})
        accel = sensors.get('accelerometer', {'x': 0, 'y': 0, 'z': 0})
        if isinstance(accel, tuple):
            self.sensor_vars[0].set(f"x: {accel[0]:.2f}  y: {accel[1]:.2f}  z: {accel[2]:.2f}")
        else:
            self.sensor_vars[0].set(f"x: {accel.get('x', 0):.2f}  y: {accel.get('y', 0):.2f}  z: {accel.get('z', 0):.2f}")
        self.sensor_vars[1].set(str(sensors.get('light', 0)))
        self.sensor_vars[2].set(str(sensors.get('sound', 0)))

if __name__ == "__main__":
    root = tk.Tk()
    app = DisplayGUI(root)
    root.mainloop()