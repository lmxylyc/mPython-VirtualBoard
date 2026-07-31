import json

from .simulator import Simulator
from .transpiler import transpile, is_mindplus_code
from .ollama_helper import OllamaHelper


class API:
    def __init__(self, simulator: Simulator):
        self._sim = simulator
        self._ollama = OllamaHelper()

    def start(self):
        self._sim.start()

    def stop(self):
        self._sim.stop()

    def reset(self):
        self._sim.reset()
        return self._sim.get_state()

    def execute_code(self, code: str, language: str = 'python') -> dict:
        runtime_mode = 'mpython'

        if language == 'mindplus' or is_mindplus_code(code):
            try:
                code = transpile(code)
            except Exception as e:
                return {
                    'status': 'error',
                    'output': f'转译失败: {e}',
                    'state': self._sim.get_state(),
                }
            runtime_mode = 'mpython'
        elif language == 'pinpong':
            runtime_mode = 'pinpong'
        else:
            runtime_mode = 'mpython'

        return self._sim.execute_code(code, runtime_mode)

    def stop_execution(self) -> dict:
        return self._sim.stop_execution()

    def transpile_code(self, code: str) -> dict:
        try:
            return {'status': 'ok', 'code': transpile(code)}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def rewrite_pinpong_code(self, code: str, instruction: str = '') -> dict:
        return self._ollama.rewrite_pinpong_code(code, instruction)

    def get_ai_status(self) -> dict:
        return self._ollama.get_status()

    def get_state(self) -> dict:
        return self._sim.get_state()

    def set_button(self, btn: str, pressed: str) -> dict:
        self._sim.set_button(btn, pressed in ('true', True, 1, '1'))
        return self._sim.get_state()

    def set_touch(self, pad: str, pressed: str) -> dict:
        self._sim.set_touch(pad, pressed in ('true', True, 1, '1'))
        return self._sim.get_state()

    def set_sensor(self, sensor_type: str, value) -> dict:
        try:
            value = json.loads(value) if isinstance(value, str) else value
        except (json.JSONDecodeError, TypeError):
            pass
        self._sim.set_sensor(sensor_type, value)
        return self._sim.get_state()

    def set_sensor_source(self, source: str) -> dict:
        self._sim.set_sensor_source(source)
        return self._sim.get_state()

    def list_sensor_ports(self):
        return self._sim.sensor_device.list_ports()

    def connect_sensor_device(self, port: str = '') -> dict:
        try:
            connected_port = self._sim.sensor_device.connect(port or None)
            return {
                'status': 'ok',
                'port': connected_port,
                'state': self._sim.get_state(),
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'state': self._sim.get_state(),
            }

    def disconnect_sensor_device(self) -> dict:
        self._sim.sensor_device.disconnect()
        return {'status': 'ok', 'state': self._sim.get_state()}

    def set_rgb(self, index: int, r: int, g: int, b: int) -> dict:
        self._sim.set_rgb(int(index), (int(r), int(g), int(b)))
        return self._sim.get_state()

    def set_oled(self, text: str, y: int = 0) -> dict:
        self._sim.set_oled_text(text, int(y))
        return self._sim.get_state()

    def clear_oled(self) -> dict:
        self._sim.clear_oled()
        return self._sim.get_state()

    def poll_state(self) -> str:
        return json.dumps(self._sim.get_state())
