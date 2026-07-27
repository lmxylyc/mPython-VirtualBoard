import sys
import os
import socket
import threading
import json
import time

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'simulator'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'simulator', 'modules'))

from shared_state import shared_state
from pc_sensors import pc_sensors
from mindplus_transpiler import is_mindplus_code, transpile

class VMServer:
    def __init__(self, host='127.0.0.1', port=7778):
        self.host = host
        self.port = port
        self.server = None
        self.running = False
        self._client_conns = []
        self._lock = threading.Lock()
        
        self._button_a_state = False
        self._button_b_state = False
        self._touch_states = {'P': False, 'Y': False, 'T': False, 'H': False, 'O': False, 'N': False}
        self._rgb_colors = [(0,0,0), (0,0,0), (0,0,0)]
        self._oled_text = [""] * 8
        
        self._use_real_sensors = False
        self._sensor_config = {}
    
    def start(self):
        self.running = True
        
        self._pc_sensors = pc_sensors
        self._pc_sensors.start()
        shared_state.set_pc_sensors(self._pc_sensors)
        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        self.server.settimeout(1.0)
        
        threading.Thread(target=self._accept_loop, daemon=True).start()
        threading.Thread(target=self._sensor_poll, daemon=True).start()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def _accept_loop(self):
        while self.running:
            try:
                conn, addr = self.server.accept()
                conn.settimeout(30)
                with self._lock:
                    self._client_conns.append(conn)
                threading.Thread(target=self._handle_client, args=(conn,), daemon=True).start()
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    pass
    
    def _handle_client(self, conn):
        try:
            buffer = b""
            while self.running:
                try:
                    data = conn.recv(4096)
                    if not data:
                        break
                    buffer += data
                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        response = self._process_command(line.decode('utf-8'))
                        if response:
                            conn.sendall(response.encode('utf-8') + b"\n")
                except socket.timeout:
                    continue
                except:
                    break
        finally:
            with self._lock:
                if conn in self._client_conns:
                    self._client_conns.remove(conn)
            conn.close()
    
    def _process_command(self, cmd):
        try:
            if not cmd.strip():
                return ""
            
            data = json.loads(cmd)
            action = data.get('action', '')
            
            if action == 'oled_fill':
                color = data.get('color', 0)
                if color == 0:
                    self._oled_text = [""] * 8
                    shared_state.clear_oled_text()
                return json.dumps({'status': 'ok'})
            
            elif action == 'oled_show':
                return json.dumps({'status': 'ok', 'text': self._oled_text})
            
            elif action == 'oled_text':
                text = data.get('text', '')
                y = data.get('y', 0)
                row = y // 16
                if 0 <= row < 8:
                    self._oled_text[row] = text[:20]
                    shared_state.set_oled_text(row, text[:20])
                return json.dumps({'status': 'ok'})
            
            elif action == 'rgb_write':
                colors = data.get('colors', [(0,0,0),(0,0,0),(0,0,0)])
                self._rgb_colors = colors
                shared_state.set_rgb_colors(colors)
                return json.dumps({'status': 'ok'})
            
            elif action == 'rgb_set':
                idx = data.get('index', 0)
                color = data.get('color', (0,0,0))
                if 0 <= idx < 3:
                    self._rgb_colors[idx] = color
                    shared_state.set_rgb_colors(self._rgb_colors)
                return json.dumps({'status': 'ok'})
            
            elif action == 'button_read':
                btn = data.get('button', 'A')
                result = self._button_a_state if btn == 'A' else self._button_b_state
                return json.dumps({'status': 'ok', 'pressed': result})
            
            elif action == 'touch_read':
                pad = data.get('pad', 'P')
                result = self._touch_states.get(pad, False)
                return json.dumps({'status': 'ok', 'pressed': result})
            
            elif action == 'sensor_read':
                sensor = data.get('sensor', 'light')
                accel, gyro, mag, light, sound = shared_state.get_sensors()
                if sensor == 'light':
                    result = light
                elif sensor == 'sound':
                    result = sound
                elif sensor == 'accelerometer':
                    result = accel
                elif sensor == 'gyro':
                    result = gyro
                elif sensor == 'magnetic':
                    result = mag
                else:
                    result = 0
                return json.dumps({'status': 'ok', 'value': result})
            
            elif action == 'execute':
                code = data.get('code', '')
                output = self._execute_code(code)
                return json.dumps({'status': 'ok', 'output': output})
            
            elif action == 'ping':
                return json.dumps({'status': 'ok', 'message': 'VM Server is running'})
            
            elif action == 'get_state':
                accel, gyro, mag, light, sound = shared_state.get_sensors()
                return json.dumps({
                    'status': 'ok',
                    'oled_text': self._oled_text,
                    'rgb_colors': self._rgb_colors,
                    'button_a': self._button_a_state,
                    'button_b': self._button_b_state,
                    'sensors': {
                        'light': light,
                        'sound': sound,
                        'accelerometer': accel
                    }
                })
            
            elif action == 'button_press':
                btn = data.get('button', 'A')
                if btn == 'A':
                    self._button_a_state = True
                else:
                    self._button_b_state = True
                shared_state.set_button(btn, True)
                return json.dumps({'status': 'ok'})
            
            elif action == 'button_release':
                btn = data.get('button', 'A')
                if btn == 'A':
                    self._button_a_state = False
                else:
                    self._button_b_state = False
                shared_state.set_button(btn, False)
                return json.dumps({'status': 'ok'})
            
            elif action == 'touch_press':
                pad = data.get('pad', 'P')
                if pad in self._touch_states:
                    self._touch_states[pad] = True
                shared_state.set_touch(pad, True)
                return json.dumps({'status': 'ok'})
            
            elif action == 'touch_release':
                pad = data.get('pad', 'P')
                if pad in self._touch_states:
                    self._touch_states[pad] = False
                shared_state.set_touch(pad, False)
                return json.dumps({'status': 'ok'})
            
            elif action == 'sensor_set':
                sensor_type = data.get('sensor', '')
                value = data.get('value', 0)
                shared_state.set_sensor_value(sensor_type, value)
                return json.dumps({'status': 'ok'})
            
            elif action == 'sensor_manual_mode':
                enabled = data.get('enabled', False)
                shared_state.set_sensor_manual_mode(enabled)
                return json.dumps({'status': 'ok'})
            
            elif action == 'sensor_config':
                sensors = data.get('sensors', {})
                self._sensor_config = sensors
                return json.dumps({'status': 'ok'})
            
            elif action == 'sensor_set_real':
                enabled = data.get('enabled', False)
                self._use_real_sensors = enabled
                shared_state.set_use_real_sensors(enabled)
                return json.dumps({'status': 'ok'})
            
            else:
                return json.dumps({'status': 'error', 'message': f'Unknown action: {action}'})
                
        except Exception as e:
            return json.dumps({'status': 'error', 'message': str(e)})
    
    def _execute_code(self, code):
        try:
            if is_mindplus_code(code):
                code = transpile(code)
            
            exec_globals = {
                'shared_state': shared_state,
                'oled_text': self._oled_text,
                'rgb_colors': self._rgb_colors,
                'sleep_ms': lambda ms: time.sleep(ms/1000),
                'sleep': time.sleep,
            }
            
            try:
                import mpython_sim
                for k, v in mpython_sim.__dict__.items():
                    if not k.startswith('_'):
                        exec_globals[k] = v
            except:
                pass
            
            try:
                from clients.pinpong_client import Pin, PinMode, PinState, RGB, OLED, Button, Sensor
                exec_globals['Pin'] = Pin
                exec_globals['PinMode'] = PinMode
                exec_globals['PinState'] = PinState
                exec_globals['RGB'] = RGB
                exec_globals['OLED'] = OLED
                exec_globals['Button'] = Button
                exec_globals['Sensor'] = Sensor
            except:
                pass
            
            exec(code, exec_globals)
            return ""
        except Exception as e:
            return str(e)
    
    def _sensor_poll(self):
        while self.running:
            shared_state.update_sensors()
            time.sleep(0.1)
    
    def stop(self):
        self.running = False
        with self._lock:
            for conn in self._client_conns:
                try:
                    conn.close()
                except:
                    pass
            self._client_conns.clear()
        if self.server:
            try:
                self.server.close()
            except:
                pass

if __name__ == "__main__":
    server = VMServer()
    server.start()