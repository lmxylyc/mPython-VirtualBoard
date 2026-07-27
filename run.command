#!/bin/bash
# mPython Virtual Board - macOS 双击启动入口
# 将此文件保存为 run.command，双击即可运行

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 使用 Terminal 运行 start_vm.sh
if command -v osascript &>/dev/null; then
    # macOS: 在终端中运行
    osascript -e 'tell application "Terminal" to do script "cd '"$SCRIPT_DIR"' && bash start_vm.sh"'
else
    # 其他 Unix: 直接运行
    bash start_vm.sh
fi
