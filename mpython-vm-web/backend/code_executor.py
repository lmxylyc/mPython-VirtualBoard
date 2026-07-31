import io
import sys
import time
import math
import random
import threading
import textwrap

from .hardware import HardwareState


class ExecutionStopped(BaseException):
    pass


class CodeExecutor:
    def __init__(self, hardware: HardwareState):
        self._hw = hardware
        self._exec_lock = threading.Lock()
        self._running = False
        self._output = []
        self._stop_requested = threading.Event()

    def execute(self, code: str, runtime_mode: str = 'mpython') -> dict:
        with self._exec_lock:
            self._output = []
            stdout_capture = io.StringIO()
            original_sleep = time.sleep
            execution_thread_id = {'value': None}
            result = {
                'status': 'ok',
                'output': '',
                'state': self._hw.get_state()
            }
            self._stop_requested.clear()
            self._running = True

            try:
                def _interruptible_sleep(seconds):
                    # Only interrupt sleeps running inside the user-code worker thread.
                    if threading.get_ident() != execution_thread_id['value']:
                        return original_sleep(seconds)

                    remaining = max(float(seconds), 0.0)
                    while remaining > 0:
                        if self._stop_requested.is_set():
                            raise ExecutionStopped()
                        step = min(remaining, 0.02)
                        original_sleep(step)
                        remaining -= step

                def _runner():
                    old_stdout = sys.stdout
                    trace = self._make_trace()
                    execution_thread_id['value'] = threading.get_ident()
                    try:
                        sys.settrace(trace)
                        sys.stdout = stdout_capture
                        time.sleep = _interruptible_sleep

                        exec_globals = self._build_globals(runtime_mode)
                        exec_globals['print'] = self._make_print(stdout_capture)

                        try:
                            exec(code, exec_globals)
                        except SystemExit:
                            pass
                        except ExecutionStopped:
                            result['status'] = 'stopped'
                            self._write_output('执行已停止', stdout_capture)
                        except SyntaxError as e:
                            result['status'] = 'error'
                            self._write_output(self._format_syntax_error(code, e), stdout_capture)
                        except Exception as e:
                            result['status'] = 'error'
                            self._write_output(str(e), stdout_capture)
                    except Exception as e:
                        result['status'] = 'error'
                        self._write_output(str(e), stdout_capture)
                    finally:
                        time.sleep = original_sleep
                        sys.settrace(None)
                        sys.stdout = old_stdout

                worker = threading.Thread(target=_runner, daemon=True)
                worker.start()
                while worker.is_alive():
                    worker.join(0.05)

                result['output'] = stdout_capture.getvalue()
                result['state'] = self._hw.get_state()
                return result
            except Exception as e:
                return {
                    'status': 'error',
                    'output': str(e),
                    'state': self._hw.get_state()
                }
            finally:
                self._running = False
                self._stop_requested.clear()

    def _build_globals(self, runtime_mode: str = 'mpython') -> dict:
        hw = self._hw

        def oled_fill(color):
            if color == 0:
                hw.clear_oled()

        def oled_DispChar(s, x=0, y=0, mode=1, auto_return=False):
            row = y // 16
            if 0 <= row < 8:
                hw.set_oled_text(str(s), row)

        def oled_show():
            pass

        def oled_clearDisplay():
            hw.clear_oled()

        def oled_setCursor(x, y):
            pass

        def oled_fillScreen(color):
            oled_fill(color)

        def oled_print(text):
            hw.set_oled_text(str(text), 0)

        class _OLED:
            def fill(self, c): oled_fill(c)
            def DispChar(self, s, x=0, y=0, m=1, ar=False): oled_DispChar(s, x, y, m, ar)
            def show(self): oled_show()
            def clearDisplay(self): oled_clearDisplay()
            def setCursor(self, x, y): oled_setCursor(x, y)
            def fillScreen(self, c): oled_fillScreen(c)
            def print(self, t): oled_print(t)

        class _RGB:
            def __init__(self):
                self._colors = [(0, 0, 0), (0, 0, 0), (0, 0, 0)]

            def __setitem__(self, idx, color):
                if isinstance(color, (tuple, list)) and len(color) == 3:
                    hw.set_rgb(idx, color)

            def write(self):
                pass

            def fill(self, color):
                for i in range(3):
                    hw.set_rgb(i, color)

        class _Button:
            def __init__(self, name):
                self._name = name

            def value(self):
                if self._name == 'A':
                    return button_a_value()
                return button_b_value()

            def is_pressed(self):
                return self.value() == 0

        def button_a_value():
            return 0 if hw.button_a_pressed else 1

        def button_b_value():
            return 0 if hw.button_b_pressed else 1

        def light_read():
            return hw.light

        def sound_read():
            return hw.sound

        class _Accelerometer:
            def get_x(self): return hw.accel['x']
            def get_y(self): return hw.accel['y']
            def get_z(self): return hw.accel['z']
            def get(self): return (self.get_x(), self.get_y(), self.get_z())

        class _Gyroscope:
            def get_x(self): return hw.gyro['x']
            def get_y(self): return hw.gyro['y']
            def get_z(self): return hw.gyro['z']

        class _Magnetic:
            def get_x(self): return hw.mag['x']
            def get_y(self): return hw.mag['y']
            def get_z(self): return hw.mag['z']

        class _Buzzer:
            def tone(self, freq, duration):
                hw.set_buzzer(freq, duration)

            def noTone(self):
                hw.set_buzzer(0, 0)

        class _Music:
            def pitch(self, freq, duration=0):
                hw.set_buzzer(freq, duration)

            def stop(self):
                hw.set_buzzer(0, 0)

        class _PinMode:
            OUT = 0
            IN = 1
            ANALOG = 2
            PWM = 3
            SERVO = 4

        class _PinState:
            LOW = 0
            HIGH = 1

        class _Pin:
            P0 = 0
            P1 = 1
            P2 = 2
            P3 = 3
            P4 = 4

            def __init__(self, pin=None, mode=None):
                self.pin = pin
                self.mode = mode

            def write_digital(self, value):
                if self.pin == 0:
                    hw.set_button('A', value == _PinState.HIGH)
                elif self.pin == 2:
                    hw.set_button('B', value == _PinState.HIGH)

            def read_digital(self):
                if self.pin == 0:
                    return 1 if hw.button_a_pressed else 0
                if self.pin == 2:
                    return 1 if hw.button_b_pressed else 0
                return 0

            def read_analog(self):
                if self.pin == 3:
                    return hw.light
                if self.pin == 4:
                    return hw.sound
                return 0

            def write_analog(self, value):
                if self.pin == 3:
                    hw.set_sensor('light', value)
                elif self.pin == 4:
                    hw.set_sensor('sound', value)

            def on(self):
                self.write_digital(_PinState.HIGH)

            def off(self):
                self.write_digital(_PinState.LOW)

        class _PinPongOLED:
            def clear(self):
                hw.clear_oled()

            def write(self, text):
                hw.clear_oled()
                lines = str(text).splitlines() or [str(text)]
                for idx, line in enumerate(lines[:8]):
                    hw.set_oled_text(line, idx)

            def show(self):
                pass

            def print(self, text):
                self.write(text)

            def text(self, text, x=0, y=0, color=1):
                row = y // 16
                hw.set_oled_text(str(text), row)

        class _PinPongRGB:
            def write(self, r, g, b):
                for idx in range(3):
                    hw.set_rgb(idx, (r, g, b))

            def write_color(self, color):
                color_map = {
                    'red': (255, 0, 0),
                    'green': (0, 255, 0),
                    'blue': (0, 0, 255),
                    'yellow': (255, 255, 0),
                    'cyan': (0, 255, 255),
                    'magenta': (255, 0, 255),
                    'white': (255, 255, 255),
                    'black': (0, 0, 0),
                }
                if color in color_map:
                    self.write(*color_map[color])

            def red(self):
                self.write(255, 0, 0)

            def green(self):
                self.write(0, 255, 0)

            def blue(self):
                self.write(0, 0, 255)

            def off(self):
                self.write(0, 0, 0)

        class _PinPongButton:
            def __init__(self, pin):
                self.pin = pin

            def read_digital(self):
                if self.pin == 0:
                    return 1 if hw.button_a_pressed else 0
                if self.pin == 2:
                    return 1 if hw.button_b_pressed else 0
                return 0

        class _PinPongSensor:
            def __init__(self, pin):
                self.pin = pin

            def read(self):
                if self.pin == 3:
                    return hw.light
                if self.pin == 4:
                    return hw.sound
                return 0

        def pinpong_init(board='mpython'):
            return board

        def get_oled():
            return _PinPongOLED()

        def get_rgb():
            return _PinPongRGB()

        def get_pin(pin):
            return _Pin(pin)

        def delay(ms):
            sleep_ms(ms)

        def sleep_ms(ms):
            time.sleep(ms / 1000.0)

        def sleep_us(us):
            time.sleep(us / 1000000.0)

        runtime_globals = {
            'oled': _OLED(),
            'display': _OLED(),
            'rgb': _RGB(),
            'button_a': _Button('A'),
            'button_b': _Button('B'),
            'light': type('Light', (), {'read': staticmethod(light_read)})(),
            'sound': type('Sound', (), {'read': staticmethod(sound_read)})(),
            'accelerometer': _Accelerometer(),
            'gyroscope': _Gyroscope(),
            'magnetic': _Magnetic(),
            'buzzer': _Buzzer(),
            'music': _Music(),
            'sleep': time.sleep,
            'sleep_ms': sleep_ms,
            'sleep_us': sleep_us,
            'time': time,
            'math': math,
            'random': random,
            'delay': sleep_ms,
            'delayMicroseconds': sleep_us,
        }

        if runtime_mode == 'pinpong':
            runtime_globals.update({
                'PinMode': _PinMode,
                'PinState': _PinState,
                'Pin': _Pin,
                'RGB': _PinPongRGB,
                'OLED': _PinPongOLED,
                'Button': type('Button', (), {'A': _PinPongButton(0), 'B': _PinPongButton(2)}),
                'Sensor': _PinPongSensor,
                'init': pinpong_init,
                'get_oled': get_oled,
                'get_rgb': get_rgb,
                'get_pin': get_pin,
                'delay': delay,
            })

            prelude = textwrap.dedent(
                '''
                def get_accel():
                    return accelerometer.get()
                '''
            )
            exec(prelude, runtime_globals)

        return runtime_globals

    def stop(self):
        if self._running:
            self._stop_requested.set()

    def _make_print(self, capture):
        def _print(*args, **kwargs):
            sep = kwargs.get('sep', ' ')
            end = kwargs.get('end', '\n')
            text = sep.join(str(a) for a in args) + end
            capture.write(text)
        return _print

    def _make_trace(self):
        def _trace(frame, event, arg):
            if self._stop_requested.is_set():
                raise ExecutionStopped()
            return _trace

        return _trace

    def _write_output(self, text, capture):
        capture.write(text + '\n')

    def _format_syntax_error(self, code, err):
        """把 Python 语法错误格式化为带出错行与光标的可读信息。"""
        lines = code.splitlines()
        msg = str(err).replace('(<string>, ', '').rstrip(')')
        if getattr(err, 'lineno', None):
            line_text = lines[err.lineno - 1] if 0 < err.lineno <= len(lines) else ''
            pointer = ' ' * max(int(err.offset or 1) - 1, 0) + '^'
            msg = f'第 {err.lineno} 行: {line_text}\n{pointer}\n{msg}'
        return msg
