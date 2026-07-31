import json
import threading
import time

try:
    import serial
    import serial.tools.list_ports

    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False
    serial = None

BAUDRATE = 115200
# 超过该时长没有收到数据，视为设备断线
HEARTBEAT_TIMEOUT = 2.0


class SensorDeviceManager:
    """真实传感器设备连接管理。

    通过 USB 串口连接真实掌控板（运行 tools/sensor_report.py 上报脚本），
    持续读取 JSON 行并写入硬件状态。每行格式示例：

        {"accel":[0.0,-0.02,1.01],"gyro":[0,0,0],"mag":[10,20,30],"light":123,"sound":45}
    """

    def __init__(self, hardware):
        self._hw = hardware
        self._serial = None
        self._port = None
        self._thread = None
        self._running = False
        self._last_data_time = 0.0
        self._lock = threading.Lock()

    def list_ports(self):
        if not HAS_SERIAL:
            return []
        try:
            return [p.device for p in serial.tools.list_ports.comports()]
        except Exception:
            return []

    @property
    def connected(self):
        with self._lock:
            return self._serial is not None and self._serial.is_open

    @property
    def port(self):
        return self._port

    def connect(self, port=None):
        """连接真实设备；port 为空时自动挑选第一个可用串口。"""
        if not HAS_SERIAL:
            raise RuntimeError('未安装 pyserial，无法连接真实设备')
        if self.connected:
            return self._port

        if port is None or not port:
            ports = self.list_ports()
            if not ports:
                raise RuntimeError('未发现可用串口设备，请确认掌控板已通过 USB 连接')
            port = ports[0]

        self._serial = serial.Serial(port, baudrate=BAUDRATE, timeout=1)
        self._port = port
        self._last_data_time = time.time()
        self._running = True
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()
        self._hw.set_device_connected(True)
        return port

    def disconnect(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None
        with self._lock:
            if self._serial:
                try:
                    self._serial.close()
                except Exception:
                    pass
                self._serial = None
            self._port = None
        self._hw.set_device_connected(False)

    def _read_loop(self):
        buffer = b''
        while self._running:
            try:
                with self._lock:
                    ser = self._serial
                if ser is None or not ser.is_open:
                    break
                n = ser.inWaiting()
                if n > 0:
                    buffer += ser.read(n)
                    while b'\n' in buffer:
                        line, buffer = buffer.split(b'\n', 1)
                        self._handle_line(line)
                else:
                    time.sleep(0.02)

                # 心跳检测：长时间无数据视为掉线
                if time.time() - self._last_data_time > HEARTBEAT_TIMEOUT:
                    self._hw.set_device_connected(False)
            except Exception:
                time.sleep(0.05)
        self._hw.set_device_connected(False)

    def _handle_line(self, raw):
        line = raw.decode('utf-8', errors='ignore').strip()
        if not line:
            return
        try:
            data = json.loads(line)
        except ValueError:
            # 串口中可能混入 REPL 提示符等噪音行，直接跳过
            return
        if not isinstance(data, dict):
            return
        self._last_data_time = time.time()
        self._hw.set_device_connected(True)
        self._hw.update_device_sensor(data)
