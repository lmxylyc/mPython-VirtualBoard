#!/bin/bash
# mPython Virtual Board - macOS / Linux 一键启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON="${PYTHON:-python3}"

echo "============================================================"
echo "   mPython Virtual Board - One-Click Launch"
echo "   Platform: $(uname -s)"
echo "============================================================"

# 检查 Python
if ! command -v "$PYTHON" &>/dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$("$PYTHON" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Python version: $PYTHON_VERSION"

# 安装依赖
echo ""
echo "📦 Checking dependencies..."
"$PYTHON" -m pip install -q pyserial

# 检查 socat（macOS/Linux 虚拟串口工具）
echo ""
if command -v socat &>/dev/null; then
    echo "✅ socat is available"
else
    echo "⚠️ socat not found. Virtual serial port bridging will be unavailable."
    echo "   To install:"
    if [[ "$(uname -s)" == "Darwin" ]]; then
        echo "     brew install socat"
    else
        echo "     sudo apt install socat"
    fi
fi

# 创建虚拟串口对（如果 socat 可用）
HOST_PORT="/tmp/vcom_host"
DEVICE_PORT="/tmp/vcom_device"

if command -v socat &>/dev/null; then
    echo ""
    echo "🔌 Creating virtual serial port pair..."
    # 清理旧的
    rm -f "$HOST_PORT" "$DEVICE_PORT" /tmp/.mp_socat.pid 2>/dev/null || true
    socat PTY,link="$HOST_PORT",mode=666 PTY,link="$DEVICE_PORT",mode=666 &
    SOCAT_PID=$!
    echo "$SOCAT_PID" > /tmp/.mp_socat.pid
    sleep 1
    if [ -e "$HOST_PORT" ] && [ -e "$DEVICE_PORT" ]; then
        echo "✅ Virtual serial ports created: $HOST_PORT ↔ $DEVICE_PORT"
    else
        echo "⚠️ Failed to create virtual serial ports"
    fi
fi

# 启动 VM Server
echo ""
echo "🔌 Starting VM Server (port 7778)..."
"$PYTHON" vm_server.py &
VM_PID=$!
sleep 2

# 启动 Virtual USB Service
echo "🔌 Starting Virtual USB Service (port 7777)..."
"$PYTHON" -c "
import sys, os
sys.path.insert(0, '$SCRIPT_DIR')
from simulator.modules.virtual_usb import start_virtual_usb
start_virtual_usb()
import time
time.sleep(3600)
" &
USB_PID=$!
sleep 1

# 启动显示 GUI
echo "🖥️ Starting Virtual Board Display..."
"$PYTHON" display_gui.py &
DISPLAY_PID=$!
sleep 2

# 可选：启动 Thonny
THONNY_PATH=$(command -v thonny 2>/dev/null || true)
if [ -n "$THONNY_PATH" ]; then
    echo "💻 Starting Thonny IDE..."
    "$THONNY_PATH" demo_pinpong.py &
    THONNY_PID=$!
else
    echo "⚠️ Thonny not found, please start manually"
    THONNY_PID=""
fi

echo ""
echo "============================================================"
echo "   All services started successfully!"
echo "============================================================"
echo ""
echo "📋 Usage:"
echo "   1. Virtual Board display is running"
echo "   2. Open demo.py or demo_pinpong.py in Thonny"
echo "   3. Click Run button to see effects"
echo ""
echo "🔗 Mind+ Connection:"
echo "   TCP direct: 127.0.0.1:7777"
echo "   Serial bridge: $HOST_PORT ↔ $DEVICE_PORT"
echo ""
echo "📝 To stop: press Ctrl+C"
echo "============================================================"
echo ""

# 清理函数
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    kill $DISPLAY_PID $USB_PID $VM_PID 2>/dev/null || true
    if [ -n "$THONNY_PID" ]; then
        kill $THONNY_PID 2>/dev/null || true
    fi
    # 清理 socat
    if [ -f /tmp/.mp_socat.pid ]; then
        kill $(cat /tmp/.mp_socat.pid) 2>/dev/null || true
        rm -f /tmp/.mp_socat.pid
    fi
    rm -f "$HOST_PORT" "$DEVICE_PORT" 2>/dev/null || true
    echo "✅ All services stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

wait
