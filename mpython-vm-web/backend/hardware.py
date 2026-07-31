import threading


class HardwareState:
    def __init__(self):
        self._lock = threading.Lock()

        self.oled_text = [""] * 8
        self.oled_buffer = bytearray(128 * 8)

        self.rgb_colors = [(0, 0, 0), (0, 0, 0), (0, 0, 0)]

        self.button_a_pressed = False
        self.button_b_pressed = False

        self.touch_states = {
            'P': False, 'Y': False, 'T': False,
            'H': False, 'O': False, 'N': False
        }

        self.accel = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.gyro = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.mag = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.light = 0
        self.sound = 0

        self.buzzer_freq = 0
        self.buzzer_duration = 0

        self.sensor_source = 'device'
        self.sensor_device_connected = False

        self._running = False

    def reset(self):
        with self._lock:
            self.oled_text = [""] * 8
            self.oled_buffer = bytearray(128 * 8)
            self.rgb_colors = [(0, 0, 0), (0, 0, 0), (0, 0, 0)]
            self.button_a_pressed = False
            self.button_b_pressed = False
            for k in self.touch_states:
                self.touch_states[k] = False
            self.accel = {'x': 0.0, 'y': 0.0, 'z': 0.0}
            self.gyro = {'x': 0.0, 'y': 0.0, 'z': 0.0}
            self.mag = {'x': 0.0, 'y': 0.0, 'z': 0.0}
            self.light = 0
            self.sound = 0
            self.buzzer_freq = 0
            self.buzzer_duration = 0
            self.sensor_source = 'device'
            self.sensor_device_connected = False

    def get_state(self):
        with self._lock:
            return {
                'oled_text': list(self.oled_text),
                'oled_buffer': list(self.oled_buffer),
                'rgb_colors': list(self.rgb_colors),
                'button_a': self.button_a_pressed,
                'button_b': self.button_b_pressed,
                'touch': dict(self.touch_states),
                'accel': dict(self.accel),
                'gyro': dict(self.gyro),
                'mag': dict(self.mag),
                'light': self.light,
                'sound': self.sound,
                'sensor_source': self.sensor_source,
                'sensor_device_connected': self.sensor_device_connected,
                'buzzer': {
                    'freq': self.buzzer_freq,
                    'duration': self.buzzer_duration
                }
            }

    def set_oled_text(self, text, y=0):
        with self._lock:
            if 0 <= y < 8:
                self.oled_text[y] = str(text)[:20]
                self.oled_buffer = bytearray(128 * 8)

    def clear_oled(self):
        with self._lock:
            self.oled_text = [""] * 8
            self.oled_buffer = bytearray(128 * 8)

    def set_rgb(self, index, color):
        with self._lock:
            if 0 <= index < 3:
                self.rgb_colors[index] = tuple(color)

    def set_button(self, btn, pressed):
        with self._lock:
            if btn == 'A':
                self.button_a_pressed = pressed
            elif btn == 'B':
                self.button_b_pressed = pressed

    def set_touch(self, pad, pressed):
        with self._lock:
            if pad in self.touch_states:
                self.touch_states[pad] = pressed

    def set_sensor_source(self, source):
        with self._lock:
            if source in ('device', 'manual'):
                self.sensor_source = source

    def set_sensor(self, sensor_type, value):
        with self._lock:
            if self.sensor_source != 'manual' and sensor_type != 'buzzer':
                return
            if sensor_type == 'accelerometer' and isinstance(value, dict):
                self.accel.update(value)
            elif sensor_type == 'gyro' and isinstance(value, dict):
                self.gyro.update(value)
            elif sensor_type == 'magnetic' and isinstance(value, dict):
                self.mag.update(value)
            elif sensor_type == 'light':
                self.light = max(0, min(4095, int(value)))
            elif sensor_type == 'sound':
                self.sound = max(0, min(4095, int(value)))
            elif sensor_type == 'buzzer':
                self.buzzer_freq = max(0, int(value))
                self.buzzer_duration = 0.0

    def set_buzzer(self, freq, duration=0):
        with self._lock:
            self.buzzer_freq = int(freq)
            self.buzzer_duration = float(duration)

    def set_device_connected(self, connected):
        with self._lock:
            self.sensor_device_connected = bool(connected)

    def update_device_sensor(self, data):
        """写入真实设备上报的传感器数据（来自串口 JSON 行）。"""
        with self._lock:
            accel = data.get('accel')
            if isinstance(accel, (list, tuple)) and len(accel) == 3:
                self.accel = {'x': float(accel[0]), 'y': float(accel[1]), 'z': float(accel[2])}
            gyro = data.get('gyro')
            if isinstance(gyro, (list, tuple)) and len(gyro) == 3:
                self.gyro = {'x': float(gyro[0]), 'y': float(gyro[1]), 'z': float(gyro[2])}
            mag = data.get('mag')
            if isinstance(mag, (list, tuple)) and len(mag) == 3:
                self.mag = {'x': float(mag[0]), 'y': float(mag[1]), 'z': float(mag[2])}
            if 'light' in data:
                self.light = max(0, min(4095, int(data['light'])))
            if 'sound' in data:
                self.sound = max(0, min(4095, int(data['sound'])))

    def simulate_sensors(self):
        return
