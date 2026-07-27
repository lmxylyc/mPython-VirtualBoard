import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from shared_state import shared_state

_pin_initialized = False
_oled_initialized = False
_rgb_initialized = False

class PinMode:
    OUT = 0
    IN = 1
    ANALOG = 2
    PWM = 3
    SERVO = 4

class PinState:
    LOW = 0
    HIGH = 1

class Pin:
    def __init__(self, pin):
        self.pin = pin
        self.mode = PinMode.OUT
        self.value = PinState.LOW
    
    def write_digital(self, value):
        self.value = value
        if value == PinState.HIGH:
            shared_state.set_led_state('user_led', True)
        else:
            shared_state.set_led_state('user_led', False)
    
    def read_digital(self):
        if self.pin in [0, 1, 2]:
            if self.pin == 0:
                return 1 if shared_state.get_button_state('A') else 0
            elif self.pin == 1:
                return 1 if shared_state.get_button_state('B') else 0
        return self.value
    
    def write_analog(self, value):
        self.value = value
    
    def read_analog(self):
        if self.pin in [3, 4, 5]:
            if self.pin == 3:
                return int(shared_state.get_sensor_data('light') * 4095)
            elif self.pin == 4:
                return int(shared_state.get_sensor_data('sound') * 4095)
            elif self.pin == 5:
                return int(shared_state.get_sensor_data('temperature') * 4095)
        return int(self.value * 4095)
    
    def set_mode(self, mode):
        self.mode = mode
    
    def on(self):
        self.write_digital(PinState.HIGH)
    
    def off(self):
        self.write_digital(PinState.LOW)

class RGB:
    def __init__(self):
        global _rgb_initialized
        _rgb_initialized = True
    
    def write(self, r, g, b):
        shared_state.set_rgb_colors([(r, g, b), (r, g, b), (r, g, b)])
    
    def write_color(self, color):
        if isinstance(color, str):
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

class OLED:
    def __init__(self, width=128, height=64):
        global _oled_initialized
        _oled_initialized = True
        self.width = width
        self.height = height
        self._text_buffer = [""] * 8
    
    def init(self):
        shared_state.clear_oled_text()
    
    def clear(self):
        shared_state.clear_oled_text()
        self._text_buffer = [""] * 8
    
    def write(self, text):
        for i, line in enumerate(text.split('\n')[:8]):
            if i < 8:
                self._text_buffer[i] = line[:20]
                shared_state.set_oled_text(i, line[:20])
    
    def show(self):
        pass
    
    def text(self, text, x=0, y=0, color=1):
        row = y // 16
        if 0 <= row < 8:
            current_text = self._text_buffer[row]
            self._text_buffer[row] = current_text[:x] + text + current_text[x+len(text):]
            shared_state.set_oled_text(row, self._text_buffer[row][:20])
    
    def fill(self, color):
        if color == 0:
            self.clear()
    
    def draw_point(self, x, y, color=1):
        pass
    
    def draw_line(self, x1, y1, x2, y2, color=1):
        pass
    
    def draw_rectangle(self, x1, y1, x2, y2, color=1):
        pass
    
    def draw_circle(self, x, y, radius, color=1):
        pass
    
    def print(self, text):
        self.write(text)
        self.show()

class Button:
    A = Pin(0)
    B = Pin(1)

class Sensor:
    def __init__(self, pin):
        self.pin = pin
    
    def read(self):
        if self.pin in [3, 4, 5]:
            if self.pin == 3:
                return shared_state.get_sensor_data('light')
            elif self.pin == 4:
                return shared_state.get_sensor_data('sound')
            elif self.pin == 5:
                return shared_state.get_sensor_data('temperature')
        return 0

def init(board='mpython'):
    global _pin_initialized
    _pin_initialized = True
    shared_state.set_oled_text(0, 'PinPong')
    shared_state.set_oled_text(1, 'Initialized!')
    print(f"PinPong board: {board}")

def get_pin(pin):
    return Pin(pin)

def get_oled():
    return OLED()

def get_rgb():
    return RGB()

def delay(ms):
    import time
    time.sleep(ms / 1000)

def sleep(seconds):
    import time
    time.sleep(seconds)