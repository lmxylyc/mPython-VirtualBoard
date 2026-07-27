"""
Mind+ USB Bridge - 跨平台 Mind+ 连接桥接服务

支持平台：
  - Windows: 使用 com0com 创建虚拟串口对
  - macOS:   使用 socat / modem 创建虚拟串口对（推荐 socat）
  - Linux:   使用 socat 创建虚拟串口对
"""

import socket
import threading
import time
import sys
import os
import json
import subprocess
import shutil

# ========== 平台检测 ==========
IS_WINDOWS = sys.platform.startswith('win')
IS_MACOS = sys.platform == 'darwin'
IS_LINUX = sys.platform.startswith('linux')

if IS_WINDOWS:
    try:
        import winreg
        import ctypes
    except ImportError:
        pass

# ========== 串口路径辅助 ==========
def _default_virtual_ports():
    """返回当前平台默认的虚拟串口对 (host_port, device_port)"""
    if IS_WINDOWS:
        return ("COM19", "COM20")
    elif IS_MACOS:
        return ("/dev/cu.mpVirt1", "/dev/cu.mpVirt2")
    elif IS_LINUX:
        return ("/tmp/vcom1", "/tmp/vcom2")
    else:
        return ("/tmp/vcom1", "/tmp/vcom2")


def _list_serial_ports():
    """列出系统可用串口"""
    try:
        import serial.tools.list_ports
        return [p.device for p in serial.tools.list_ports.comports()]
    except Exception:
        return []


def _is_admin():
    """检测是否具有管理员/root 权限"""
    if IS_WINDOWS:
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    elif IS_MACOS or IS_LINUX:
        return os.geteuid() == 0 if hasattr(os, 'geteuid') else False
    return False


# ========== socat 虚拟串口管理 ==========
def _find_socat():
    """查找 socat 可执行文件"""
    path = shutil.which('socat')
    if path:
        return path
    return None


def _create_virtual_pair_socat(port_a, port_b):
    """使用 socat 创建虚拟串口对（后台运行）"""
    socat = _find_socat()
    if not socat:
        print("⚠️ 未找到 socat，请先安装:")
        if IS_MACOS:
            print("   brew install socat")
        elif IS_LINUX:
            print("   sudo apt install socat")
        return False

    # 创建两个 PTY 并符号链接到指定路径
    script = f"""
PTY,link={port_a},mode=666 PTY,link={port_b},mode=666 &
"""
    try:
        # 先清理旧的符号链接
        for p in (port_a, port_b):
            try:
                if os.path.islink(p) or os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass

        # 运行 socat
        cmd = [socat,
               f'PTY,link={port_a},mode=666',
               f'PTY,link={port_b},mode=666']
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # 等待设备就绪
        time.sleep(1)

        if os.path.exists(port_a) and os.path.exists(port_b):
            print(f"✅ socat 虚拟串口对创建成功: {port_a} ↔ {port_b}")
            # 保存 PID 以便清理
            pid_file = os.path.join(os.path.dirname(port_a) or '/tmp', '.mp_socat.pid')
            try:
                with open(pid_file, 'w') as f:
                    f.write(str(proc.pid))
            except Exception:
                pass
            return True
        else:
            proc.terminate()
            print(f"❌ socat 启动失败，设备节点未生成")
            return False
    except Exception as e:
        print(f"❌ socat 创建串口对失败: {e}")
        return False


def _cleanup_virtual_pair_socat(port_a, port_b):
    """清理 socat 创建的虚拟串口对"""
    pid_file = os.path.join(os.path.dirname(port_a) or '/tmp', '.mp_socat.pid')
    try:
        if os.path.exists(pid_file):
            with open(pid_file) as f:
                pid = int(f.read().strip())
            os.kill(pid, 15)
            os.remove(pid_file)
    except Exception:
        pass
    for p in (port_a, port_b):
        try:
            if os.path.islink(p):
                os.remove(p)
        except Exception:
            pass


def _find_modem_service():
    """macOS: 查找/创建虚拟串口对使用 modem 服务"""
    # macOS 的 Virtual Serial Port 可使用 modem 配置
    # 这里生成一个简单的方案：使用 ptys 加符号链接
    return None


# ========== CH9102 设备信息注册 ==========
CH9102_VID = "1A86"
CH9102_PID = "5512"


def _register_ch9102_device_info_windows(serial_port):
    """Windows 专用：注册 CH9102 USB 设备信息到注册表"""
    try:
        base_path = rf"SYSTEM\CurrentControlSet\Enum\USB\VID_{CH9102_VID}&PID_{CH9102_PID}"
        device_instance = "0000"
        device_path = os.path.join(base_path, device_instance)

        try:
            winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, device_path)
        except Exception:
            pass

        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, device_path, 0, winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, "FriendlyName", 0, winreg.REG_SZ, "USB Serial Port")
            winreg.SetValueEx(key, "PortName", 0, winreg.REG_SZ, serial_port)
            winreg.SetValueEx(key, "DeviceDesc", 0, winreg.REG_SZ, "USB Serial Port (CH9102)")

        print(f"✅ 已注册CH9102设备信息 (VID={CH9102_VID}, PID={CH9102_PID})")
        return True
    except Exception as e:
        print(f"⚠️ 设备信息注册失败: {e}")
        return False


# ========== MindPlusUSBBridge ==========
class MindPlusUSBBridge:
    """跨平台 Mind+ USB 桥接"""

    def __init__(self, tcp_host='127.0.0.1', tcp_port=7777, serial_port=None):
        host_port, device_port = _default_virtual_ports()
        if serial_port is None:
            serial_port = device_port

        self.tcp_host = tcp_host
        self.tcp_port = tcp_port
        self.serial_port = serial_port
        self.host_port = host_port if host_port != device_port else None
        self.running = False
        self._thread = None
        self._serial = None
        self._tcp_socket = None
        self._com_port_created = False
        self._socat_cleanup = None

        self._vm_server_host = '127.0.0.1'
        self._vm_server_port = 7778

        # Windows com0com 相关
        self._com0com_path = None
        self._other_port = None

    # ---------- Windows: com0com ----------
    def _find_com0com(self):
        if not IS_WINDOWS:
            return False
        paths = [
            r"C:\Program Files\com0com\setupc.exe",
            r"C:\Program Files (x86)\com0com\setupc.exe",
            r"C:\Program Files\com0com\setupc64.exe",
            r"C:\Program Files (x86)\com0com\setupc64.exe",
        ]
        for path in paths:
            if os.path.exists(path):
                self._com0com_path = path
                print(f"✅ 找到com0com: {path}")
                return True
        print("❌ 未找到com0com，正在尝试自动下载安装...")
        return self._download_and_install_com0com()

    def _download_and_install_com0com(self):
        if not IS_WINDOWS:
            return False
        import urllib.request
        import zipfile

        download_url = (
            "https://sourceforge.net/projects/com0com/files/com0com/3.0.0.0/"
            "com0com-3.0.0.0-x64-signed.zip/download"
        )
        download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        zip_path = os.path.join(download_dir, "com0com.zip")
        extract_dir = os.path.join(download_dir, "com0com")

        try:
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)

            print("📥 正在下载com0com...")
            try:
                urllib.request.urlretrieve(download_url, zip_path)
            except Exception:
                download_url = (
                    "https://github.com/igor-k/com0com/releases/download/v3.0.0.0/"
                    "com0com-3.0.0.0-x64-signed.zip"
                )
                print(f"📥 尝试备用下载源: {download_url}")
                urllib.request.urlretrieve(download_url, zip_path)

            if not os.path.exists(zip_path) or os.path.getsize(zip_path) < 10000:
                print("❌ 下载失败，文件大小异常")
                return False

            print(f"✅ 下载完成: {zip_path}")

            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)

            print("📦 正在解压...")
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(extract_dir)

            print(f"✅ 解压完成: {extract_dir}")

            if not _is_admin():
                print("⚠️ 当前没有管理员权限，无法自动安装")
                print(f"   解压位置: {extract_dir}")
                print("   请手动运行安装程序或使用管理员权限重新运行")
                return False

            install_dir = r"C:\Program Files (x86)\com0com"
            print(f"📁 正在安装到: {install_dir}")
            if os.path.exists(install_dir):
                shutil.rmtree(install_dir)
            shutil.copytree(extract_dir, install_dir)

            self._com0com_path = os.path.join(install_dir, "setupc.exe")
            print(f"✅ com0com安装成功! 路径: {self._com0com_path}")

            subprocess.run(
                [self._com0com_path, 'install', 'CNCA0', 'CNCB0'],
                capture_output=True, text=True, timeout=30
            )
            subprocess.run(
                [self._com0com_path, 'set', 'CNCA0', 'PortName=COM19'],
                capture_output=True, text=True, timeout=30
            )
            subprocess.run(
                [self._com0com_path, 'set', 'CNCB0', 'PortName=COM20'],
                capture_output=True, text=True, timeout=30
            )
            print("✅ 已配置串口: COM19 ↔ COM20")
            time.sleep(2)

            ports = _list_serial_ports()
            if 'COM19' in ports and 'COM20' in ports:
                print("✅ 虚拟串口创建成功!")
                return True
            print("⚠️ 虚拟串口未在系统中显示，可能需要重启")
            return False
        except Exception as e:
            print(f"❌ 下载安装com0com失败: {e}")
            print("   请手动下载安装: https://sourceforge.net/projects/com0com/")
            return False

    def _create_virtual_serial_port_windows(self):
        """Windows: 使用 com0com 创建虚拟串口"""
        ports = _list_serial_ports()
        if self.serial_port in ports:
            print(f"✅ 串口 {self.serial_port} 已存在")
            self._find_com0com()
            return True

        if not self._find_com0com():
            return False

        if not _is_admin():
            print("⚠️ 当前没有管理员权限，无法自动创建虚拟串口")
            print("   请手动创建或使用管理员权限运行")
            return False

        try:
            port_num = int(self.serial_port.replace('COM', ''))
            other_port_num = port_num - 1
            self._other_port = f"COM{other_port_num}"
        except Exception:
            self._other_port = "COM19"

        print(f"📋 尝试创建虚拟串口对: {self._other_port} ↔ {self.serial_port}")
        try:
            port_suffix = self.serial_port.replace('COM', '')
            cnca_name = f'CNCA{port_suffix}'
            cncb_name = f'CNCB{port_suffix}'

            subprocess.run(
                [self._com0com_path, 'install', cnca_name, cncb_name],
                capture_output=True, text=True, timeout=30
            )
            subprocess.run(
                [self._com0com_path, 'set', cnca_name, f'PortName={self._other_port}'],
                capture_output=True, text=True, timeout=30
            )
            subprocess.run(
                [self._com0com_path, 'set', cncb_name, f'PortName={self.serial_port}'],
                capture_output=True, text=True, timeout=30
            )
            print(f"✅ 已配置串口: {self._other_port} ↔ {self.serial_port}")
            time.sleep(2)

            ports_after = _list_serial_ports()
            if self.serial_port in ports_after:
                print(f"✅ 串口 {self.serial_port} 创建成功")
                self._com_port_created = True
                return True
            print(f"❌ 串口 {self.serial_port} 未成功创建")
            return False
        except Exception as e:
            print(f"⚠️ 创建虚拟串口失败: {e}")
            return False

    def _create_virtual_serial_port_unix(self):
        """macOS/Linux: 使用 socat 创建虚拟串口"""
        # 检查端口是否已存在
        if os.path.exists(self.serial_port):
            print(f"✅ 串口 {self.serial_port} 已存在")
            return True

        if _find_socat() is None:
            print("⚠️ 需要安装 socat 来创建虚拟串口")
            if IS_MACOS:
                print("   安装方法: brew install socat")
            elif IS_LINUX:
                print("   安装方法: sudo apt install socat")
            return False

        host_port = self.host_port or "/tmp/vcom_host"
        device_port = self.serial_port
        print(f"📋 尝试创建虚拟串口对: {host_port} ↔ {device_port}")
        success = _create_virtual_pair_socat(host_port, device_port)
        if success:
            self._com_port_created = True
            self._socat_cleanup = (host_port, device_port)
            return True
        return False

    def _create_virtual_serial_port(self):
        """根据平台创建虚拟串口"""
        if IS_WINDOWS:
            return self._create_virtual_serial_port_windows()
        else:
            return self._create_virtual_serial_port_unix()

    # ---------- 启动/停止 ----------
    def start(self):
        print("🔌 启动Mind+ USB桥接服务...")

        if IS_WINDOWS:
            _register_ch9102_device_info_windows(self.serial_port)

        self._create_virtual_serial_port()

        self.running = True
        self._thread = threading.Thread(target=self._bridge_loop, daemon=True)
        self._thread.start()

        print("✅ Mind+ USB桥接服务已启动")
        display_port = self._other_port or self.host_port or self.serial_port
        print(f"   Mind+请连接串口: {display_port}")
        print(f"   TCP目标: {self.tcp_host}:{self.tcp_port}")

    def stop(self):
        self.running = False
        if self._serial:
            try:
                self._serial.close()
            except Exception:
                pass
            self._serial = None
        if self._tcp_socket:
            try:
                self._tcp_socket.close()
            except Exception:
                pass
            self._tcp_socket = None
        if self._socat_cleanup:
            _cleanup_virtual_pair_socat(*self._socat_cleanup)
            self._socat_cleanup = None
        print("⏹ Mind+ USB桥接服务已停止")

    # ---------- 数据桥接 ----------
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
                    bytesize=EIGHTBITS,
                )
                print(f"✅ 已连接串口 {self.serial_port}")

                while self.running:
                    try:
                        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        tcp_socket.connect((self.tcp_host, self.tcp_port))
                        self._tcp_socket = tcp_socket
                        self._data_loop(tcp_socket)
                    except ConnectionRefusedError:
                        print("⚠️ TCP连接被拒绝，正在重试...")
                        time.sleep(1)
                    except Exception as e:
                        print(f"⚠️ TCP连接错误: {e}")
                        time.sleep(2)
                    self._tcp_socket = None

            except serial.SerialException as e:
                print(f"⚠️ 串口连接失败({self.serial_port}): {e}")
                if IS_WINDOWS:
                    print("   请确保已安装虚拟串口驱动(com0com)并创建端口对")
                else:
                    print("   请确保 socat 已安装并已创建虚拟串口对")
                time.sleep(3)
            except Exception as e:
                print(f"⚠️ 未知错误: {e}")
                time.sleep(2)

            if self._serial:
                try:
                    self._serial.close()
                except Exception:
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
        except Exception:
            return {'status': 'error', 'message': 'VM server not available'}


# ========== MindPlusNetworkDiscovery ==========
class MindPlusNetworkDiscovery:
    def __init__(self):
        self.running = False
        self._thread = None
        self._udp_socket = None

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
            except Exception:
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

                    if any(kw in message.lower() for kw in ('mindplus', 'mpython', 'chongzuo')):
                        print(f"📡 收到发现请求: {addr} - {message}")
                        response = json.dumps({
                            'device': 'mPython Virtual Board',
                            'vid': CH9102_VID,
                            'pid': CH9102_PID,
                            'port': 7777,
                            'type': 'virtual',
                        })
                        self._udp_socket.sendto(response.encode('utf-8'), addr)
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"⚠️ 发现服务错误: {e}")
        except Exception as e:
            print(f"⚠️ 启动发现服务失败: {e}")


# ========== MindPlusDirectServer ==========
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
            except Exception:
                pass
        if self.server:
            try:
                self.server.close()
            except Exception:
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
        except Exception:
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
            except Exception:
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
            try:
                from mindplus_transpiler import is_mindplus_code, transpile
                if is_mindplus_code(code):
                    print("🔄 检测到Mind+代码，正在转译...")
                    code = transpile(code)
                    print(f"📝 转译后代码: {code[:100]}...")
            except ImportError:
                pass
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
            except Exception:
                pass
            self._buffer = b""


# ========== 全局实例管理 ==========
_bridge = None
_discovery = None
_direct_server = None


def start_mindplus_services(tcp_port=7777, serial_port=None):
    global _bridge, _discovery, _direct_server

    host_port, device_port = _default_virtual_ports()
    if serial_port is None:
        serial_port = device_port

    print("=" * 60)
    print("   Mind+ 连接服务启动")
    print(f"   平台: {sys.platform}")
    print("=" * 60)

    _direct_server = MindPlusDirectServer(port=tcp_port)
    _direct_server.start()

    _discovery = MindPlusNetworkDiscovery()
    _discovery.start()

    _bridge = MindPlusUSBBridge(tcp_port=tcp_port, serial_port=serial_port)
    _bridge.start()

    try:
        import vm_websocket_server
        _ws = vm_websocket_server.VMWebSocketServer(port=7779)
        _ws.start()
        print("✅ WebSocket服务器已启动 (端口7779)")
    except Exception as e:
        print(f"⚠️ WebSocket服务器启动失败: {e}")

    display_port = _bridge._other_port or _bridge.host_port or serial_port

    print("=" * 60)
    print("   所有Mind+服务已启动")
    print("=" * 60)
    print("📋 使用说明:")

    print("\n   ── 方法1: 实时模式用户库 (推荐) ──")
    print("     Mind+ → 实时模式 → 扩展 → 用户库")
    ext_dir = os.path.join(os.path.dirname(__file__), 'mindplus_extension', 'config.json')
    print(f"     加载: {ext_dir}")
    print("     使用积木连接到 127.0.0.1:7779")

    print("\n   ── 方法2: 串口连接 ──")
    print("     Mind+ → 上传到设备 → 选择串口")
    print(f"     请选择串口: {display_port}")

    print("\n   ── 方法3: TCP直连 ──")
    print(f"     Mind+ → 网络连接 → 127.0.0.1:{tcp_port}")

    print(f"\n   设备信息:")
    print(f"     VID: {CH9102_VID}")
    print(f"     PID: {CH9102_PID}")
    print(f"     设备名称: USB Serial Port (CH9102)")
    print("\n按 Ctrl+C 停止服务")
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
