import threading
import time

from .hardware import HardwareState
from .code_executor import CodeExecutor
from .sensor_device import SensorDeviceManager


class Simulator:
    def __init__(self):
        self.hardware = HardwareState()
        self.executor = CodeExecutor(self.hardware)
        self.sensor_device = SensorDeviceManager(self.hardware)
        self._running = False
        self._sensor_thread = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._sensor_thread = threading.Thread(target=self._sensor_loop, daemon=True)
        self._sensor_thread.start()

    def stop(self):
        self.executor.stop()
        self.sensor_device.disconnect()
        self._running = False

    def reset(self):
        self.executor.stop()
        self.hardware.reset()
        # 若真实设备仍保持连接，重置后恢复其连接标记
        if self.sensor_device.connected:
            self.hardware.set_device_connected(True)

    def execute_code(self, code: str, runtime_mode: str = 'mpython') -> dict:
        return self.executor.execute(code, runtime_mode)

    def stop_execution(self) -> dict:
        self.executor.stop()
        return self.hardware.get_state()

    def get_state(self) -> dict:
        return self.hardware.get_state()

    def set_button(self, btn: str, pressed: bool):
        self.hardware.set_button(btn, pressed)

    def set_touch(self, pad: str, pressed: bool):
        self.hardware.set_touch(pad, pressed)

    def set_sensor(self, sensor_type: str, value):
        self.hardware.set_sensor(sensor_type, value)

    def set_sensor_source(self, source: str):
        self.hardware.set_sensor_source(source)

    def set_rgb(self, index: int, color):
        self.hardware.set_rgb(index, color)

    def set_oled_text(self, text: str, y: int = 0):
        self.hardware.set_oled_text(text, y)

    def clear_oled(self):
        self.hardware.clear_oled()

    def _sensor_loop(self):
        while self._running:
            self.hardware.simulate_sensors()
            time.sleep(0.1)
