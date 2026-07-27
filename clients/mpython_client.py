import socket
import json
import time
import subprocess
import os
import sys

class VirtualOled:
    def __init__(self, client):
        self._client = client
    
    def fill(self, color):
        self._client.send_command({'action': 'oled_fill', 'color': color})
    
    def DispChar(self, text, x=0, y=0, size=1):
        self._client.send_command({'action': 'oled_text', 'text': text, 'x': x, 'y': y})
    
    def show(self):
        return self._client.send_command({'action': 'oled_show'})

class VirtualRGB:
    def __init__(self, client):
        self._client = client
        self._colors = [(0,0,0), (0,0,0), (0,0,0)]
    
    def __setitem__(self, idx, color):
        self._colors[idx] = color
    
    def __getitem__(self, idx):
        return self._colors[idx]
    
    def write(self):
        self._client.send_command({'action': 'rgb_write', 'colors': self._colors})

class VirtualButton:
    def __init__(self, client, name):
        self._client = client
        self._name = name
    
    def is_pressed(self):
        result = self._client.send_command({'action': 'button_read', 'button': self._name})
        return result.get('pressed', False)

class VirtualTouch:
    def __init__(self, client):
        self._client = client
    
    def __getitem__(self, pad):
        return VirtualTouchPad(self._client, pad)

class VirtualTouchPad:
    def __init__(self, client, pad):
        self._client = client
        self._pad = pad
    
    def read(self):
        result = self._client.send_command({'action': 'touch_read', 'pad': self._pad})
        return 200 if result.get('pressed', False) else 1000

class VirtualSensor:
    def __init__(self, client, name):
        self._client = client
        self._name = name
    
    def read(self):
        result = self._client.send_command({'action': 'sensor_read', 'sensor': self._name})
        return result.get('value', 0)

class VirtualAccelerometer:
    def __init__(self, client):
        self._client = client
    
    def get(self):
        result = self._client.send_command({'action': 'sensor_read', 'sensor': 'accelerometer'})
        value = result.get('value', {'x': 0, 'y': 0, 'z': 0})
        if isinstance(value, list) and len(value) == 3:
            return {'x': value[0], 'y': value[1], 'z': value[2]}
        return value

class mPythonClient:
    def __init__(self, host='127.0.0.1', port=7778):
        self.host = host
        self.port = port
        self.socket = None
        self._connected = False
        
        self.oled = VirtualOled(self)
        self.rgb = VirtualRGB(self)
        self.button_a = VirtualButton(self, 'A')
        self.button_b = VirtualButton(self, 'B')
        self.touch = VirtualTouch(self)
        self.light = VirtualSensor(self, 'light')
        self.sound = VirtualSensor(self, 'sound')
        self.accelerometer = VirtualAccelerometer(self)
    
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self._connected = True
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            print("Make sure vm_server.py is running first!")
            return False
    
    def disconnect(self):
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
            self._connected = False
    
    def send_command(self, command):
        if not self._connected:
            return {'status': 'error', 'message': 'Not connected'}
        
        try:
            self.socket.sendall(json.dumps(command).encode('utf-8') + b"\n")
            
            response = ""
            while True:
                data = self.socket.recv(4096)
                if not data:
                    self._connected = False
                    return {'status': 'error', 'message': 'Connection lost'}
                response += data.decode('utf-8')
                if "\n" in response:
                    return json.loads(response.split("\n")[0])
            
            return {'status': 'error', 'message': 'No response'}
        except Exception:
            self._connected = False
            return {'status': 'error', 'message': 'Connection error'}
    
    def get_state(self):
        return self.send_command({'action': 'get_state'})

def connect(host='127.0.0.1', port=7778):
    client = mPythonClient(host, port)
    if client.connect():
        return client
    return None