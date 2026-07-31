import re


def transpile(code: str) -> str:
    lines = code.strip().split('\n')
    normalized_lines = []
    skip_dedent = 0

    for raw in lines:
        expanded = raw.expandtabs(4)
        if expanded.strip() == '当启动时':
            # 当启动时是顶层入口块：跳过该行，并让其子块整体退 4 格
            skip_dedent = 4
            continue
        if expanded.strip():
            normalized_lines.append(expanded)

    effective_indents = [max(_get_indent(raw) - skip_dedent, 0) for raw in normalized_lines]
    base_indent = min(effective_indents) if effective_indents else 0

    out_lines = [
        '# 由 Mind+ 图形化代码自动转译',
        '',
    ]

    for raw, eff_indent in zip(normalized_lines, effective_indents):
        line = raw.strip()
        indent = max((eff_indent - base_indent) // 4, 0)

        if line == '重复执行':
            out_lines.append('    ' * indent + 'while True:')
            continue

        m = re.match(r'如果\s*\((.*)\)\s*$', line)
        if m:
            cond = _convert_condition(m.group(1))
            out_lines.append('    ' * indent + f'if {cond}:')
            continue

        m = re.match(r'否则如果\s*\((.*)\)\s*$', line)
        if m:
            cond = _convert_condition(m.group(1))
            out_lines.append('    ' * indent + f'elif {cond}:')
            continue

        if line == '否则':
            out_lines.append('    ' * indent + 'else:')
            continue

        converted = _convert_statement(line)
        if converted:
            out_lines.append('    ' * indent + converted)

    return '\n'.join(out_lines) + '\n'


def _get_indent(line: str) -> int:
    return len(line) - len(line.lstrip(' '))


def _convert_condition(cond: str) -> str:
    cond = _convert_expr(cond)
    cond = re.sub(r'按钮\.A\s*==\s*按下', 'button_a.value() == 0', cond)
    cond = re.sub(r'按钮\.B\s*==\s*按下', 'button_b.value() == 0', cond)
    cond = re.sub(r'Light\.Read\(\)', 'light.read()', cond)
    cond = re.sub(r'Sound\.Read\(\)', 'sound.read()', cond)
    return cond


def _convert_expr(expr: str) -> str:
    expr = expr.strip()
    expr = expr.replace('&&', ' and ').replace('||', ' or ')
    expr = re.sub(r'!([^=])', r'not \1', expr)
    expr = re.sub(r'!$', 'not ', expr)
    expr = re.sub(r'\btrue\b', 'True', expr)
    expr = re.sub(r'\bfalse\b', 'False', expr)
    return expr


def _convert_statement(line: str) -> str:
    line = line.strip()
    if not line:
        return ''

    if line.startswith('//'):
        return '# ' + line[2:].strip()

    line = _transpile_oled(line)
    line = _transpile_rgb(line)
    line = _transpile_sensors(line)
    line = _transpile_delay(line)
    line = _transpile_buttons(line)
    line = _convert_expr(line)

    if not line:
        return ''
    return line


def _transpile_oled(code: str) -> str:
    code = re.sub(r'OLED\.Show\(([^)]*)\)', r'oled.print(\1)', code)
    code = re.sub(r'OLED\.clear\(\)', 'oled.clearDisplay()', code)
    return code


def _transpile_rgb(code: str) -> str:
    def replace_rgb_set(m):
        led_idx = m.group(1)
        hex_color = m.group(2)
        r, g, b = _hex_to_rgb(hex_color)
        return f'rgb[{led_idx}] = ({r}, {g}, {b}); rgb.write()'

    def replace_rgb_fill(m):
        r, g, b = _hex_to_rgb(m.group(1))
        return f'rgb.fill(({r}, {g}, {b})); rgb.write()'

    code = re.sub(r'RGB\.SetPixelColor\((\d+)\s*,\s*0x([0-9a-fA-F]+)\)', replace_rgb_set, code)
    code = re.sub(r'RGB\.Write\(\)', 'rgb.write()', code)
    code = re.sub(r'RGB\.Fill\(0x([0-9a-fA-F]+)\)', replace_rgb_fill, code)
    return code


def _transpile_sensors(code: str) -> str:
    code = re.sub(r'Light\.Read\(\)', 'light.read()', code)
    code = re.sub(r'Sound\.Read\(\)', 'sound.read()', code)
    return code


def _transpile_delay(code: str) -> str:
    code = re.sub(r'延时\s*(\d+)\s*ms', r'sleep_ms(\1)', code)
    code = re.sub(r'延时\s*(\d+)\s*秒', r'time.sleep(\1)', code)
    return code


def _transpile_buttons(code: str) -> str:
    code = re.sub(r'按钮\.A\s*==\s*按下', 'button_a.value() == 0', code)
    code = re.sub(r'按钮\.B\s*==\s*按下', 'button_b.value() == 0', code)
    return code


def _hex_to_rgb(hex_color: str):
    if len(hex_color) == 3:
        hex_color = ''.join(c * 2 for c in hex_color)
    return (
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16),
    )


def is_mindplus_code(code: str) -> bool:
    indicators = ['当启动时', '重复执行', 'OLED.', 'RGB.', 'Light.Read', 'Sound.Read']
    return any(ind in code for ind in indicators)
