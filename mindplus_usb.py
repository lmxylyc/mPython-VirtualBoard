import socket
import threading
import time
import sys
import os
import json
import winreg
import ctypes

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from mindplus_transpiler import is_mindplus_code, transpile

CH9102_VID = "1A86"
CH9102_PID = "5512"

class MindPlusUSBBridge:
    def __init__(self, tcp_host='127.0.0.1', tcp_port=7777, serial_port='COM20'):
        self.tcp_host = tcp_host
        self.tcp_port = tcp_port
        self.serial_port = serial_port
        self.running = False
        self._thread = None
        self._serial = None
        self._tcp_socket = None
        self._com_port_created = False
        
        self._vm_server_host = '127.0.0.1'
        self._vm_server_port = 7778
        
        self._com0com_path = None
        self._other_port = None
    
    def _find_com0com(self):
        paths = [
            r"C:\Program Files\com0com\setupc.exe",
            r"C:\Program Files (x86)\com0com\setupc.exe",
            r"C:\Program Files\com0com\setupc64.exe",
            r"C:\Program Files (x86)\com0com\setupc64.exe"
        ]
        for path in paths:
            if os.path.exists(path):
                self._com0com_path = path
                print(f"✅ 找到com0com: {path}")
                return True
        print("❌ 未找到com0com，正在尝试自动下载安装...")
        return self._download_and_install_com0com()
    
    def _download_and_install_com0com(self):
        import urllib.request
        import zipfile
        import shutil
        
        download_url = "https://sourceforge.net/projects/com0com/files/com0com/3.0.0.0/com0com-3.0.0.0-x64-signed.zip/download"
        download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        zip_path = os.path.join(download_dir, "com0com.zip")
        extract_dir = os.path.join(download_dir, "com0com")
        
        try:
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)
            
            print(f"📥 正在下载com0com...")
            print(f"   来源: {download_url}")
            
            try:
                urllib.request.urlretrieve(download_url, zip_path)
            except:
                download_url = "https://github.com/igor-k/com0com/releases/download/v3.0.0.0/com0com-3.0.0.0-x64-signed.zip"
                print(f"📥 尝试备用下载源: {download_url}")
                urllib.request.urlretrieve(download_url, zip_path)
            
            if not os.path.exists(zip_path) or os.path.getsize(zip_path) < 10000:
                print("❌ 下载失败，文件大小异常")
                return False
            
            print(f"✅ 下载完成: {zip_path}")
            
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)
            
            print(f"📦 正在解压...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            print(f"✅ 解压完成: {extract_dir}")
            
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            
            if is_admin:
                install_dir = r"C:\Program Files (x86)\com0com"
                print(f"📁 正在安装到: {install_dir}")
                if os.path.exists(install_dir):
                    shutil.rmtree(install_dir)
                shutil.copytree(extract_dir, install_dir)
                
                self._com0com_path = os.path.join(install_dir, "setupc.exe")
                
                print(f"✅ com0com安装成功!")
                print(f"   路径: {self._com0com_path}")
                
                import subprocess
                result = subprocess.run(
                    [self._com0com_path, 'install', 'CNCA0', 'CNCB0'],
                    capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0:
                    print(f"✅ 已创建默认串口对")
                
                subprocess.run(
                    [self._com0com_path, 'set', 'CNCA0', 'PortName=COM19'],
                    capture_output=True, text=True, timeout=30
                )
                subprocess.run(
                    [self._com0com_path, 'set', 'CNCB0', 'PortName=COM20'],
                    capture_output=True, text=True, timeout=30
                )
                
                print(f"✅ 已配置串口: COM19 ↔ COM20")
                
                time.sleep(2)
                
                import serial.tools.list_ports
                ports = [p.device for p in serial.tools.list_ports.comports()]
                if 'COM19' in ports and 'COM20' in ports:
                    print(f"✅ 虚拟串口创建成功!")
                    return True
                else:
                    print(f"⚠️ 虚拟串口未在系统中显示，可能需要重启")
                    return False
            else:
                print("⚠️ 当前没有管理员权限，无法自动安装")
                print(f"   解压位置: {extract_dir}")
                print("   请手动运行安装程序或使用管理员权限重新运行")
                return False
                
        except Exception as e:
            print(f"❌ 下载安装com0com失败: {e}")
            print("   请手动下载安装:")
            print("   https://sourceforge.net/projects/com0com/")
            return False
    
    def _create_virtual_serial_port(self):
        import serial.tools.list_ports
        
        ports = [p.device for p in serial.tools.list_ports.comports()]
        
        if self.serial_port in ports:
            print(f"✅ 串口 {self.serial_port} 已存在")
            self._find_com0com()
            return True
        
        if not self._find_com0com():
            return False
        
        try:
            port_num = int(self.serial_port.replace('COM', ''))
            other_port_num = port_num - 1
            self._other_port = f"COM{other_port_num}"
        except:
            self._other_port = "COM19"
        
        if self._other_port in ports:
            for i in range(10, 30):
                new_port = f"COM{i}"
                if new_port not in ports and new_port != self.serial_port:
                    self._other_port = new_port
                    break
        
        print(f"📋 尝试创建虚拟串口对: {self._other_port} ↔ {self.serial_port}")
        
        try:
            import subprocess
            
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if not is_admin:
                print("⚠️ 当前没有管理员权限，无法自动创建虚拟串口")
                print("   请手动创建或使用管理员权限运行")
                return False
            
            port_suffix = self.serial_port.replace('COM', '')
            cnca_name = f'CNCA{port_suffix}'
            cncb_name = f'CNCB{port_suffix}'
            
            result = subprocess.run(
                [self._com0com_path, 'install', cnca_name, cncb_name],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                print(f"✅ com0com串口对创建成功")
            else:
                print(f"⚠️ com0com安装输出: {result.stdout}")
                print(f"⚠️ com0com安装错误: {result.stderr}")
                
            time.sleep(1)
            
            result = subprocess.run(
                [self._com0com_path, 'set', cnca_name, f'PortName={self._other_port}'],
                capture_output=True, text=True, timeout=30
            )
            result = subprocess.run(
                [self._com0com_path, 'set', cncb_name, f'PortName={self.serial_port}'],
                capture_output=True, text=True, timeout=30
            )
            
            print(f"✅ 已配置串口: {self._other_port} ↔ {self.serial_port}")
            time.sleep(2)
            
            ports_after = [p.device for p in serial.tools.list_ports.comports()]
            if self.serial_port in ports_after:
                print(f"✅ 串口 {self.serial_port} 创建成功")
                self._com_port_created = True
                return True
            else:
                print(f"❌ 串口 {self.serial_port} 未成功创建")
                return False
                
        except PermissionError:
            print("⚠️ 创建虚拟串口失败: 需要管理员权限")
            print("   请右键点击程序 -> 以管理员身份运行")
            return False
        except Exception as e:
            print(f"⚠️ 创建虚拟串口失败: {e}")
            return False
    
    def _register_ch9102_device_info(self):
        try:
            base_path = rf"SYSTEM\CurrentControlSet\Enum\USB\VID_{CH9102_VID}&PID_{CH9102_PID}"
            
            device_instance = "0000"
            device_path = os.path.join(base_path, device_instance)
            
            try:
                winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, device_path)
            except:
                pass
            
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, device_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "FriendlyName", 0, winreg.REG_SZ, "USB Serial Port")
                winreg.SetValueEx(key, "PortName", 0, winreg.REG_SZ, self.serial_port)
                winreg.SetValueEx(key, "DeviceDesc", 0, winreg.REG_SZ, "USB Serial Port (CH9102)")
            
            print(f"✅ 已注册CH9102设备信息 (VID={CH9102_VID}, PID={CH9102_PID})")
            return True
        except Exception as e:
            print(f"⚠️ 设备信息注册失败: {e}")
            return False
    
    def start(self):
        print("🔌 启动Mind+ USB桥接服务...")
        
        self._register_ch9102_device_info()
        
        self._create_virtual_serial_port()
        
        self.running = True
        self._thread = threading.Thread(target=self._bridge_loop, daemon=True)
        self._thread.start()
        
        print(f"✅ Mind+ USB桥接服务已启动")
        if self._other_port:
            print(f"   Mind+请连接串口: {self._other_port}")
            print(f"   内部桥接串口: {self.serial_port}")
        else:
            print(f"   串口: {self.serial_port}")
        print(f"   TCP目标: {self.tcp_host}:{self.tcp_port}")
    
    def stop(self):
        self.running = False
        if self._serial:
            try:
                self._serial.close()
            except:
                pass
            self._serial = None
        if self._tcp_socket:
            try:
                self._tcp_socket.close()
            except:
                pass
            self._tcp_socket = None
        print("⏹ Mind+ USB桥接服务已停止")
    
    def _bridge_loop(self):
        import serial
        
        PARITY_NONE = getattr(serial, 'PARITY_NONE', 'N')
        STOPBITS_1 = getattr(serial, 'STOPBITS_1', 1)
        EIGHTBITS = getattr(serial, 'EIGHTBITS', 8)
        
        while self.running:
            try:
                self._serial = serial.Serial(
                    self.serial_port,
                    115200,
                    timeout=0.1,
                    parity=PARITY_NONE,
                    stopbits=STOPBITS_1,
                    bytesize=EIGHTBITS
                )
                print(f"✅ 已连接串口 {self.serial_port}")
                
                while self.running:
                    try:
                        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        tcp_socket.connect((self.tcp_host, self.tcp_port))
                        self._tcp_socket = tcp_socket
                        
                        self._data_loop(tcp_socket)
                        
                    except ConnectionRefusedError:
                        print(f"⚠️ TCP连接被拒绝，正在重试...")
                        time.sleep(1)
                    except Exception as e:
                        print(f"⚠️ TCP连接错误: {e}")
                        time.sleep(2)
                        
                    self._tcp_socket = None
                    
            except serial.SerialException as e:
                print(f"⚠️ 串口连接失败({self.serial_port}): {e}")
                print(f"   请确保已安装虚拟串口驱动(com0com)并创建端口对")
                print(f"   将一端设置为 {self.serial_port}")
                time.sleep(3)
            except Exception as e:
                print(f"⚠️ 未知错误: {e}")
                time.sleep(2)
            
            if self._serial:
                try:
                    self._serial.close()
                except:
                    pass
                self._serial = None
    
    def _data_loop(self, tcp_socket):
        tcp_socket.settimeout(0.01)
        self._serial.timeout = 0.01
        
        print(f"🔄 开始数据转发: {self.serial_port} ↔ {self.tcp_host}:{self.tcp_port}")
        
        while self.running and self._serial and tcp_socket:
            try:
                serial_data = self._serial.read(1024)
                if serial_data:
                    tcp_socket.send(serial_data)
            except Exception as e:
                print(f"⚠️ 串口读取错误: {e}")
                break
            
            try:
                tcp_data = tcp_socket.recv(1024)
                if tcp_data:
                    self._serial.write(tcp_data)
            except Exception as e:
                print(f"⚠️ TCP读取错误: {e}")
                break
            
            time.sleep(0.001)
    
    def _send_to_vm(self, command):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self._vm_server_host, self._vm_server_port))
            sock.sendall(json.dumps(command).encode('utf-8') + b"\n")
            response = ""
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                response += data.decode('utf-8')
                if "\n" in response:
                    response = response.split("\n")[0]
                    break
            sock.close()
            return json.loads(response) if response else {'status': 'error', 'message': 'No response'}
        except:
            return {'status': 'error', 'message': 'VM server not available'}


class MindPlusNetworkDiscovery:
    def __init__(self):
        self.running = False
        self._thread = None
        self._udp_socket = None
        self._tcp_socket = None
    
    def start(self):
        print("🔍 启动Mind+网络发现服务...")
        self.running = True
        
        self._thread = threading.Thread(target=self._discovery_loop, daemon=True)
        self._thread.start()
        
        print("✅ Mind+网络发现服务已启动")
    
    def stop(self):
        self.running = False
        if self._udp_socket:
            try:
                self._udp_socket.close()
            except:
                pass
            self._udp_socket = None
        print("⏹ Mind+网络发现服务已停止")
    
    def _discovery_loop(self):
        try:
            self._udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self._udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._udp_socket.bind(('0.0.0.0', 7776))
            self._udp_socket.settimeout(1.0)
            
            while self.running:
                try:
                    data, addr = self._udp_socket.recvfrom(1024)
                    message = data.decode('utf-8', errors='ignore')
                    
                    if 'mindplus' in message.lower() or 'mpython' in message.lower() or 'chongzuo' in message.lower():
                        print(f"📡 收到发现请求: {addr} - {message}")
                        
                        response = json.dumps({
                            'device': 'mPython Virtual Board',
                            'vid': CH9102_VID,
                            'pid': CH9102_PID,
                            'port': 7777,
                            'type': 'virtual'
                        })
                        self._udp_socket.sendto(response.encode('utf-8'), addr)
                        print(f"📤 发送响应: {response}")
                        
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"⚠️ 发现服务错误: {e}")
                        
        except Exception as e:
            print(f"⚠️ 启动发现服务失败: {e}")


class MindPlusDirectServer:
    def __init__(self, host='127.0.0.1', port=7777):
        self.host = host
        self.port = port
        self.server = None
        self.running = False
        self._conn = None
        self._buffer = b""
        self._repl_active = False
        self._raw_repl = False
        self._cmd_buffer = b""
        self._thread = None
        
        self._vm_server_host = '127.0.0.1'
        self._vm_server_port = 7778
    
    def start(self):
        print(f"🚀 启动Mind+直接连接服务 ({self.host}:{self.port})...")
        self.running = True
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(1)
        self.server.settimeout(1.0)
        self._thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._thread.start()
        print("✅ Mind+直接连接服务已启动")
    
    def stop(self):
        self.running = False
        if self._conn:
            try:
                self._conn.close()
            except:
                pass
        if self.server:
            try:
                self.server.close()
            except:
                pass
        print("⏹ Mind+直接连接服务已停止")
    
    def _send_to_vm(self, command):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self._vm_server_host, self._vm_server_port))
            sock.sendall(json.dumps(command).encode('utf-8') + b"\n")
            response = ""
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                response += data.decode('utf-8')
                if "\n" in response:
                    response = response.split("\n")[0]
                    break
            sock.close()
            return json.loads(response) if response else {'status': 'error', 'message': 'No response'}
        except:
            return {'status': 'error', 'message': 'VM server not available'}
    
    def _accept_loop(self):
        while self.running:
            try:
                conn, addr = self.server.accept()
                print(f"🔌 Mind+客户端已连接: {addr}")
                self._conn = conn
                self._conn.settimeout(0.1)
                self._buffer = b""
                self._repl_active = False
                self._raw_repl = False
                self._cmd_buffer = b""
                self._handle_connection(conn)
            except socket.timeout:
                continue
            except:
                if self.running:
                    pass
    
    def _handle_connection(self, conn):
        while self.running:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                
                hex_data = ' '.join(f'{b:02x}' for b in data)
                print(f"📥 收到数据: {hex_data}")
                
                for byte in data:
                    self._process_byte(byte)
                self._send_response()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"⚠️ 连接处理错误: {e}")
                break
        self._conn = None
        print("🔌 Mind+客户端已断开")
    
    def _process_byte(self, byte):
        if not self._repl_active:
            if byte == 0x03:
                self._repl_active = True
                self._buffer += b"\r\n"
                print("📋 进入REPL模式")
            elif byte == 0x01:
                self._repl_active = True
                self._raw_repl = True
                self._buffer += b"raw REPL; CTRL-B to exit\r\n>"
                print("📋 进入RAW REPL模式")
            return
        
        if self._raw_repl:
            if byte == 0x02:
                self._raw_repl = False
                self._buffer += b"\r\n"
                print("📋 退出RAW REPL模式")
            elif byte == 0x03:
                self._buffer += b"\r\n>>> "
            elif byte == 0x04:
                result = self._execute_code()
                self._buffer += b"OK" + result + b"\x04\x04>"
                print("✅ 代码执行完成")
            elif byte == 0x0D:
                self._cmd_buffer += b"\n"
            elif byte == 0x0A:
                pass
            else:
                self._cmd_buffer += bytes([byte])
    
    def _execute_code(self):
        if not self._cmd_buffer:
            return b""
        code = self._cmd_buffer.decode('utf-8', errors='ignore')
        self._cmd_buffer = b""
        
        print(f"📝 待执行代码: {code[:100]}...")
        
        try:
            if is_mindplus_code(code):
                print("🔄 检测到Mind+代码，正在转译...")
                code = transpile(code)
                print(f"📝 转译后代码: {code[:100]}...")
            
            result = self._send_to_vm({'action': 'execute', 'code': code})
            output = result.get('output', '')
            return str(output).encode('utf-8')
        except Exception as e:
            print(f"❌ 执行错误: {e}")
            return str(e).encode('utf-8')
    
    def _send_response(self):
        if self._conn and self._buffer:
            try:
                self._conn.send(self._buffer)
                hex_data = ' '.join(f'{b:02x}' for b in self._buffer)
                print(f"📤 发送响应: {hex_data}")
            except:
                pass
            self._buffer = b""


_bridge = None
_discovery = None
_direct_server = None


def start_mindplus_services(tcp_port=7777, serial_port='COM20'):
    global _bridge, _discovery, _direct_server
    
    print("=" * 60)
    print("   Mind+ 连接服务启动")
    print("=" * 60)
    
    _direct_server = MindPlusDirectServer(port=tcp_port)
    _direct_server.start()
    
    _discovery = MindPlusNetworkDiscovery()
    _discovery.start()
    
    _bridge = MindPlusUSBBridge(tcp_port=tcp_port, serial_port=serial_port)
    _bridge.start()
    
    print("🚀 启动WebSocket服务器 (用于Mind+实时模式)...")
    try:
        import vm_websocket_server
        _websocket_server = vm_websocket_server.VMWebSocketServer(port=7779)
        _websocket_server.start()
        print("✅ WebSocket服务器已启动 (端口7779)")
    except Exception as e:
        print(f"⚠️ WebSocket服务器启动失败: {e}")
        _websocket_server = None
    
    other_port = _bridge._other_port if _bridge else None
    
    print("=" * 60)
    print("   所有Mind+服务已启动")
    print("=" * 60)
    print(f"\n📋 使用说明:")
    
    print(f"\n   ── 方法1: 实时模式用户库 (推荐) ──")
    print(f"     Mind+ → 实时模式 → 扩展 → 用户库")
    print(f"     加载: {os.path.join(os.path.dirname(__file__), 'mindplus_extension', 'config.json')}")
    print(f"     使用积木连接到 127.0.0.1:7779")
    
    print(f"\n   ── 方法2: 串口连接 ──")
    print(f"     Mind+ → 上传到设备 → 选择串口")
    if other_port:
        print(f"     请选择串口: {other_port}")
    else:
        print(f"     请选择串口: {serial_port}")
    
    print(f"\n   ── 方法3: TCP直连 ──")
    print(f"     如果Mind+支持网络连接:")
    print(f"     Mind+ → 网络连接 → 127.0.0.1:{tcp_port}")
    
    print(f"\n   设备信息 (用于驱动配置):")
    print(f"     VID: {CH9102_VID}")
    print(f"     PID: {CH9102_PID}")
    print(f"     设备名称: USB Serial Port (CH9102)")
    print(f"\n按 Ctrl+C 停止服务")
    print("=" * 60 + "\n")
    
    return _bridge, _discovery, _direct_server


def stop_mindplus_services():
    global _bridge, _discovery, _direct_server
    
    if _bridge:
        _bridge.stop()
        _bridge = None
    if _discovery:
        _discovery.stop()
        _discovery = None
    if _direct_server:
        _direct_server.stop()
        _direct_server = None


def is_running():
    global _bridge, _discovery, _direct_server
    return (_direct_server is not None and _direct_server.running) or \
           (_discovery is not None and _discovery.running) or \
           (_bridge is not None and _bridge.running)


if __name__ == "__main__":
    start_mindplus_services()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务...")
        stop_mindplus_services()
        print("✅ 所有服务已停止")