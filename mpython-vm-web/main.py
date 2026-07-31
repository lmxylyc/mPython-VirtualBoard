import webview
import os
import sys

from backend.api import API


class ApiBridge:
    def __init__(self, api: API):
        self._api = api

    def start(self):
        self._api.start()

    def stop(self):
        self._api.stop()

    def reset(self):
        return self._api.reset()

    def execute_code(self, code: str, language: str = 'python') -> dict:
        return self._api.execute_code(code, language)

    def stop_execution(self) -> dict:
        return self._api.stop_execution()

    def transpile_code(self, code: str) -> dict:
        return self._api.transpile_code(code)

    def rewrite_pinpong_code(self, code: str, instruction: str = '') -> dict:
        return self._api.rewrite_pinpong_code(code, instruction)

    def get_ai_status(self) -> dict:
        return self._api.get_ai_status()

    def get_state(self) -> dict:
        return self._api.get_state()

    def set_button(self, btn: str, pressed: str) -> dict:
        return self._api.set_button(btn, pressed)

    def set_touch(self, pad: str, pressed: str) -> dict:
        return self._api.set_touch(pad, pressed)

    def set_sensor(self, sensor_type: str, value) -> dict:
        return self._api.set_sensor(sensor_type, value)

    def set_sensor_source(self, source: str) -> dict:
        return self._api.set_sensor_source(source)

    def list_sensor_ports(self):
        return self._api.list_sensor_ports()

    def connect_sensor_device(self, port: str = '') -> dict:
        return self._api.connect_sensor_device(port)

    def disconnect_sensor_device(self) -> dict:
        return self._api.disconnect_sensor_device()

    def set_rgb(self, index: int, r: int, g: int, b: int) -> dict:
        return self._api.set_rgb(index, r, g, b)

    def set_oled(self, text: str, y: int = 0) -> dict:
        return self._api.set_oled(text, y)

    def clear_oled(self) -> dict:
        return self._api.clear_oled()

    def poll_state(self) -> str:
        return self._api.poll_state()


def configure_runtime():
    if sys.platform == 'darwin':
        os.environ.setdefault('PYWEBVIEW_GUI', 'cocoa')


def validate_runtime():
    if sys.platform != 'darwin':
        return

    missing_modules = []

    for module_name in ('AppKit', 'WebKit', 'Foundation'):
        try:
            __import__(module_name)
        except ImportError:
            missing_modules.append(module_name)

    if missing_modules:
        missing_text = ', '.join(missing_modules)
        raise RuntimeError(
            'macOS WebView runtime is missing required PyObjC modules '
            f'({missing_text}). Install them with '
            '"pip install pywebview[cocoa]" or install the PyObjC frameworks manually.'
        )


def main():
    configure_runtime()
    validate_runtime()

    current_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(current_dir, 'frontend')
    index_html = os.path.join(frontend_dir, 'index.html')

    if not os.path.exists(index_html):
        print(f"Error: {index_html} not found", file=sys.stderr)
        sys.exit(1)

    from backend.simulator import Simulator
    simulator = Simulator()
    api = API(simulator)
    bridge = ApiBridge(api)
    bridge.start()

    window = webview.create_window(
        title='mPython VM Studio',
        url=index_html,
        width=1280,
        height=800,
        min_size=(960, 600),
        resizable=True,
        text_select=True,
        js_api=bridge,
    )

    print("Starting mPython VM Web...")
    print(f"Frontend: {frontend_dir}")
    print("Window will open shortly.")

    try:
        start_kwargs = {
            'debug': False,
            'http_server': True,
        }
        if sys.platform == 'darwin':
            start_kwargs['gui'] = 'cocoa'

        webview.start(**start_kwargs)
    except Exception as e:
        if sys.platform == 'darwin':
            print('Failed to start macOS webview runtime.', file=sys.stderr)
            print(
                'Please make sure PyObjC / Cocoa WebKit dependencies are installed. '
                'Recommended command: pip install "pywebview[cocoa]"',
                file=sys.stderr,
            )
        raise
    finally:
        bridge.stop()


if __name__ == '__main__':
    main()
