"""
Mind+ C++ 代码转译器
将 Mind+ 上传模式生成的 Arduino 风格 C++ 代码自动转译为 MicroPython 代码
"""

import re

# Mind+ C++ 代码特征标记
_CPP_MARKERS = (
    '#include',
    'void setup',
    'void loop',
    'Serial.begin',
    'mPython.begin',
    'MPython.h',
)

# C++ 类型声明关键字
_CPP_TYPES = (
    r'(?:unsigned\s+)?(?:int|float|double|long|short|char|bool|byte|void|'
    r'String|uint8_t|uint16_t|uint32_t|int8_t|int16_t|int32_t|size_t)'
)


def is_mindplus_code(code):
    """检测代码是否为 Mind+ 生成的 C++ 代码"""
    if not code or not isinstance(code, str):
        return False
    return any(marker in code for marker in _CPP_MARKERS)


def _convert_expr(expr):
    """转换 C++ 表达式为 Python 表达式"""
    expr = expr.strip()
    # 布尔字面量
    expr = re.sub(r'\btrue\b', 'True', expr)
    expr = re.sub(r'\bfalse\b', 'False', expr)
    # 逻辑运算符（注意保留 !=）
    expr = expr.replace('&&', ' and ').replace('||', ' or ')
    expr = re.sub(r'!(?!=)', 'not ', expr)
    # 类型转换函数
    expr = re.sub(r'\bString\(', 'str(', expr)
    expr = re.sub(r'\btoInt\(\)', '', expr)
    # 数学函数
    expr = re.sub(r'\bsqrt\(', 'math.sqrt(', expr)
    expr = re.sub(r'\babs\(', 'abs(', expr)
    return expr


def _convert_statement(line):
    """转换单行 C++ 语句为 Python（不处理控制结构）"""
    line = line.strip()
    if not line:
        return ''

    # 去掉行尾分号
    line = line.rstrip(';').strip()

    # 跳过初始化调用（虚拟机已初始化）
    if re.match(r'(mPython|mpython)\.begin\(\)', line):
        return None

    # 行注释
    if line.startswith('//'):
        return '# ' + line[2:].strip()

    # 去掉类型声明: int x = 0 -> x = 0
    line = re.sub(rf'^{_CPP_TYPES}\s+', '', line)
    line = re.sub(rf'\bconst\s+{_CPP_TYPES}\s+', '', line)

    # ---- 显示屏 API ----
    m = re.match(r'display\.print(?:ln)?\((.*)\)$', line)
    if m:
        return f'oled.DispChar(str({_convert_expr(m.group(1))}), 0, 0); oled.show()'
    m = re.match(r'display\.setCursor\((.*),(.*)\)$', line)
    if m:
        return f'oled.set_cursor({_convert_expr(m.group(1))}, {_convert_expr(m.group(2))})'
    if re.match(r'display\.update\(\)$', line):
        return 'oled.show()'
    m = re.match(r'display\.fillScreen\((.*)\)$', line)
    if m:
        return f'oled.fill({m.group(1)})'
    if re.match(r'display\.clearDisplay\(\)$', line):
        return 'oled.fill(0); oled.show()'

    # ---- RGB 灯 API ----
    m = re.match(r'rgb\.setPixelColor\((\w+)\s*,\s*0x([0-9a-fA-F]{6})\)$', line)
    if m:
        hex_color = m.group(2)
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return f'rgb[{m.group(1)}] = ({r}, {g}, {b}); rgb.write()'
    m = re.match(r'rgb\.setPixelColor\((\w+)\s*,\s*(.*)\)$', line)
    if m:
        return f'rgb[{m.group(1)}] = {_convert_expr(m.group(2))}; rgb.write()'
    if re.match(r'rgb\.show\(\)$', line):
        return 'rgb.write()'
    if re.match(r'rgb\.clear\(\)$', line):
        return 'rgb.fill((0, 0, 0)); rgb.write()'

    # ---- 延时 ----
    m = re.match(r'delay\((.*)\)$', line)
    if m:
        return f'time.sleep_ms(int({_convert_expr(m.group(1))}))'
    m = re.match(r'delayMicroseconds\((.*)\)$', line)
    if m:
        return f'time.sleep_us(int({_convert_expr(m.group(1))}))'

    # ---- 串口打印 ----
    m = re.match(r'Serial\.print(?:ln)?\((.*)\)$', line)
    if m:
        return f'print({_convert_expr(m.group(1))})'
    if re.match(r'Serial\.begin\(.*\)$', line):
        return None

    # ---- 音乐/蜂鸣器 ----
    m = re.match(r'buzzer\.tone\((.*),(.*)\)$', line)
    if m:
        return f'music.pitch(int({_convert_expr(m.group(1))}), int({_convert_expr(m.group(2))}))'
    if re.match(r'buzzer\.noTone\(\)$', line):
        return 'music.stop()'

    # ---- 通用表达式/赋值 ----
    return _convert_expr(line)


def _convert_condition(cond):
    """转换 C++ 条件表达式为 Python"""
    cond = _convert_expr(cond)
    # 按键
    cond = re.sub(r'buttonA\.isPressed\(\)', 'button_a.value()', cond)
    cond = re.sub(r'buttonB\.isPressed\(\)', 'button_b.value()', cond)
    # 触摸按键
    for pad in ['P', 'Y', 'T', 'H', 'O', 'N']:
        cond = re.sub(rf'touchPad{pad}\.isPressed\(\)', f'touchPad_{pad}.value()', cond)
    # 传感器
    cond = re.sub(r'light\.read\(\)', 'light.read()', cond)
    cond = re.sub(r'sound\.read\(\)', 'sound.read()', cond)
    cond = re.sub(r'accelerometer\.getX\(\)', 'accelerometer.get_x()', cond)
    cond = re.sub(r'accelerometer\.getY\(\)', 'accelerometer.get_y()', cond)
    cond = re.sub(r'accelerometer\.getZ\(\)', 'accelerometer.get_z()', cond)
    return cond


def transpile(code):
    """将 Mind+ C++ 代码转译为 MicroPython 代码"""
    lines = code.split('\n')
    py_lines = [
        '# 由 Mind+ C++ 代码自动转译为 MicroPython',
        'from mpython import *',
        'import time',
        'import math',
        '',
    ]

    indent = 0
    in_function = False  # 是否在 setup/loop 函数体内

    for raw_line in lines:
        line = raw_line.strip()

        # 空行、预处理指令、mPython.begin 直接跳过
        if not line:
            continue
        if line.startswith('#include') or line.startswith('#define'):
            continue

        # 块注释跳过
        if line.startswith('/*'):
            continue

        # setup() 函数入口
        if re.match(r'void\s+setup\s*\(\s*\)\s*\{?$', line):
            py_lines.append('# ===== setup() 初始化代码 =====')
            in_function = True
            indent = 0
            continue

        # loop() 函数入口
        if re.match(r'void\s+loop\s*\(\s*\)\s*\{?$', line):
            py_lines.append('')
            py_lines.append('# ===== loop() 循环代码 =====')
            py_lines.append('while True:')
            in_function = True
            indent = 1
            continue

        # 处理大括号结构
        if line == '{':
            continue

        # else / else if
        m = re.match(r'}\s*else\s+if\s*\((.*)\)\s*\{?$', line)
        if m:
            indent = max(indent - 1, 0)
            py_lines.append('    ' * indent + f'elif {_convert_condition(m.group(1))}:')
            indent += 1
            continue

        m = re.match(r'}\s*else\s*\{?$', line)
        if m:
            indent = max(indent - 1, 0)
            py_lines.append('    ' * indent + 'else:')
            indent += 1
            continue

        # 块结束
        if re.match(r'^\}+\s*;?$', line):
            indent = max(indent - 1, 0)
            if indent == 0:
                in_function = False
            continue

        # if 语句
        m = re.match(r'if\s*\((.*)\)\s*\{?$', line)
        if m:
            py_lines.append('    ' * indent + f'if {_convert_condition(m.group(1))}:')
            indent += 1
            continue

        # while 语句
        m = re.match(r'while\s*\((.*)\)\s*\{?$', line)
        if m:
            py_lines.append('    ' * indent + f'while {_convert_condition(m.group(1))}:')
            indent += 1
            continue

        # for (int i = 0; i < N; i++) 风格循环
        m = re.match(r'for\s*\(\s*(?:int\s+)?(\w+)\s*=\s*(.+?);\s*\1\s*<\s*(.+?);\s*\1(?:\+\+|\s*\+=\s*(\d+))\s*\)\s*\{?$', line)
        if m:
            var, start, end, step = m.group(1), m.group(2), m.group(3), m.group(4) or '1'
            py_lines.append('    ' * indent + f'for {var} in range(int({_convert_expr(start)}), int({_convert_expr(end)}), {step}):')
            indent += 1
            continue

        # 普通语句
        converted = _convert_statement(line)
        if converted:
            py_lines.append('    ' * indent + converted)

    return '\n'.join(py_lines) + '\n'
