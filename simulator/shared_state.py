import threading
import random


class SharedState:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init()
        return cls._instance

    def _init(self):
        self._oled_buffer = bytearray(128 * 8)
        self._oled_text_lines = [""] * 8  # 存储8行文本
        self._rgb_colors = [(0, 0, 0), (0, 0, 0), (0, 0, 0)]
        
        self._button_a_pressed = False
        self._button_b_pressed = False
        self._touch_states = {'P': False, 'Y': False, 'T': False, 'H': False, 'O': False, 'N': False}
        
        self._accel_values = {'x': 0.0, 'y': 0.0, 'z': 1.0}
        self._gyro_values = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self._mag_values = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self._light_value = 500
        self._sound_value = 200
        
        self._wifi_connected = False
        self._wifi_ssid = ""
        
        self._lock = threading.Lock()
        
        self._oled_callback = None
        self._rgb_callback = None
        self._sensor_callback = None
        
        self._use_real_sensors = False
        self._pc_sensors = None
        self._sensor_manual_mode = False

    def set_oled_buffer(self, buffer):
        with self._lock:
            self._oled_buffer = bytearray(buffer)
        if self._oled_callback:
            try:
                self._oled_callback(buffer)
            except:
                pass

    def get_oled_buffer(self):
        with self._lock:
            return bytes(self._oled_buffer)

    def set_oled_text(self, line_idx, text):
        with self._lock:
            if 0 <= line_idx < 8:
                self._oled_text_lines[line_idx] = text[:20]  # 每行最多20个字符

    def get_oled_text(self):
        with self._lock:
            return list(self._oled_text_lines)

    def clear_oled_text(self):
        with self._lock:
            self._oled_text_lines = [""] * 8

    def set_rgb_colors(self, colors):
        with self._lock:
            self._rgb_colors = list(colors)
        if self._rgb_callback:
            try:
                self._rgb_callback(colors)
            except:
                pass

    def get_rgb_colors(self):
        with self._lock:
            return list(self._rgb_colors)

    def set_button(self, btn, state):
        with self._lock:
            if btn == 'A':
                self._button_a_pressed = state
            elif btn == 'B':
                self._button_b_pressed = state

    def get_button(self, btn):
        with self._lock:
            if btn == 'A':
                return self._button_a_pressed
            elif btn == 'B':
                return self._button_b_pressed

    def set_touch(self, label, state):
        with self._lock:
            self._touch_states[label] = state

    def get_touch(self, label):
        with self._lock:
            return self._touch_states.get(label, False)

    def set_use_real_sensors(self, enabled):
        with self._lock:
            self._use_real_sensors = enabled

    def set_pc_sensors(self, pc_sensors):
        self._pc_sensors = pc_sensors

    def update_sensors(self):
        with self._lock:
            if self._pc_sensors:
                data = self._pc_sensors.get_sensor_data()
                
                real_sound = data.get('sound', 0)
                if real_sound > 0:
                    scaled_sound = int(real_sound * 30)
                    self._sound_value = max(100, min(4095, scaled_sound))
                elif not self._sensor_manual_mode:
                    self._sound_value = random.randint(100, 3000)
                
                real_light = data.get('light', 0)
                if real_light > 0:
                    scaled_light = int(real_light / 10)
                    self._light_value = max(100, min(4095, scaled_light))
                elif not self._sensor_manual_mode:
                    self._light_value = random.randint(100, 4000)
            elif not self._sensor_manual_mode:
                self._accel_values['x'] = random.uniform(-0.2, 0.2)
                self._accel_values['y'] = random.uniform(-0.2, 0.2)
                self._accel_values['z'] = 1.0 + random.uniform(-0.1, 0.1)
                
                self._gyro_values['x'] = random.uniform(-0.5, 0.5)
                self._gyro_values['y'] = random.uniform(-0.5, 0.5)
                self._gyro_values['z'] = random.uniform(-0.5, 0.5)
                
                self._mag_values['x'] = random.uniform(-50, 50)
                self._mag_values['y'] = random.uniform(-50, 50)
                self._mag_values['z'] = random.uniform(-50, 50)
                
                self._light_value = random.randint(100, 4000)
                self._sound_value = random.randint(100, 3000)
        
        if self._sensor_callback:
            try:
                self._sensor_callback(self._accel_values, self._gyro_values, 
                                     self._mag_values, self._light_value, self._sound_value)
            except:
                pass
    
    def set_sensor_value(self, sensor_type, value):
        with self._lock:
            if sensor_type == 'light':
                self._light_value = max(0, min(4095, int(value)))
            elif sensor_type == 'sound':
                self._sound_value = max(0, min(4095, int(value)))
            elif sensor_type == 'accelerometer':
                if isinstance(value, dict):
                    self._accel_values.update(value)
            elif sensor_type == 'gyro':
                if isinstance(value, dict):
                    self._gyro_values.update(value)
            elif sensor_type == 'magnetic':
                if isinstance(value, dict):
                    self._mag_values.update(value)
    
    def set_sensor_manual_mode(self, enabled):
        with self._lock:
            self._sensor_manual_mode = enabled

    def get_sensors(self):
        with self._lock:
            return (self._accel_values.copy(),
                    self._gyro_values.copy(),
                    self._mag_values.copy(),
                    self._light_value,
                    self._sound_value)

    def set_wifi(self, connected, ssid=""):
        with self._lock:
            self._wifi_connected = connected
            self._wifi_ssid = ssid

    def get_wifi(self):
        with self._lock:
            return self._wifi_connected, self._wifi_ssid

    def set_callbacks(self, oled_callback=None, rgb_callback=None, sensor_callback=None):
        self._oled_callback = oled_callback
        self._rgb_callback = rgb_callback
        self._sensor_callback = sensor_callback


shared_state = SharedState()