const { createApp, ref, reactive, computed, onMounted, watch } = Vue;

const TouchPositions = [
    { key: 'P', x: 30, y: 20 },
    { key: 'Y', x: 75, y: 20 },
    { key: 'T', x: 120, y: 20 },
    { key: 'H', x: 165, y: 20 },
    { key: 'O', x: 210, y: 20 },
    { key: 'N', x: 255, y: 20 },
];

const ScrewPositions = [
    { top: '8px', left: '8px' },
    { top: '8px', right: '8px' },
    { bottom: '8px', left: '8px' },
    { bottom: '8px', right: '8px' },
];

const LANGUAGE_LABELS = {
    zh_CN: '中文',
    en_US: 'English',
};

const TRANSLATIONS = {
    zh_CN: {
        web_title: 'mPython VM Studio - 双模式教学工作台',
        studio_subtitle: '双模式教学工作台',
        run: '运行',
        stop: '停止',
        reset: '重置',
        open: '打开',
        save: '保存',
        clear_output: '清空输出',
        current_mode: '当前模式',
        interface_language: '界面语言',
        workspace_overview: '工作区概览',
        workspace_overview_desc: '先选模式，再编辑代码，最后在右侧观察板卡反馈。',
        runtime_label: '运行时',
        learning_modes: '学习模式',
        mindplus_mode_title: 'Mind+ 上传模式',
        mindplus_mode_desc: '粘贴 Mind+ 自动生成代码，转译后直接运行到虚拟掌控板。',
        teaching_mode_title: '教学模式',
        teaching_mode_desc: '直接编写 mPython / PinPong 代码，用于课堂演示与学生练习。',
        mode_briefing: '模式说明',
        code_editor: '代码编辑器',
        clear: '清空',
        example: '示例',
        transpile: '转译',
        transpile_preview: '转译预览',
        transpile_preview_desc: '这里显示 Mind+ 代码转成 Python 后的结果。',
        transpile_preview_empty: '这里会显示 Mind+ 转译后的 Python 代码。',
        ai_rewrite_panel: 'PinPong AI 改写',
        ai_panel_desc: '把自然语言要求交给本地 AI，生成更适合课堂的 PinPong 代码。',
        refresh_status: '刷新状态',
        ai_instruction_placeholder: '例如：把这段代码改写成更适合小学高年级学生理解的版本，并保留注释。',
        rewrite_code: 'AI 改写',
        rewriting: '改写中',
        apply_rewrite: '应用改写',
        rewrite_result: '改写结果',
        rewrite_result_empty: 'AI 返回的改写代码会显示在这里。',
        console: '控制台',
        console_desc: '运行输出、报错和课堂提示都会显示在这里。',
        copy: '复制',
        rgb_led: 'RGB LED',
        sensor_control: '传感器控制',
        light_sensor: '光线传感器',
        sound_sensor: '声音传感器',
        accelerometer: '加速度计',
        gyroscope: '陀螺仪',
        magnetic_sensor: '磁力计',
        buzzer: '蜂鸣器',
        play: '播放',
        board_control: '板卡控制',
        board_preview_title: '虚拟掌控板',
        board_preview_desc: '运行代码后的 OLED、RGB、按钮和触摸状态预览。',
        shake: '模拟晃动',
        shake_x: '左右晃动',
        shake_y: '前后晃动',
        shake_z: '上下晃动',
        clear_screen: '清除屏幕',
        sensor_panel_desc: '手动控制传感器、蜂鸣器和板卡动作。',
        connected: '已连接',
        disconnected: '未连接',
        running_status: '● 运行中',
        ready_status: '○ 就绪',
        board_subtext: '教学虚拟掌控板',
        backend_connected: '>>> 已连接到 Python 后端',
        offline_mode: '>>> 当前未连接 Python 后端，处于离线模拟模式',
        startup_hint: '>>> 可使用 python main.py 启动完整桌面程序',
        code_start: '>>> 开始执行代码...',
        code_finished: '>>> 执行完成',
        stopped: '>>> 执行已停止',
        board_reset: '>>> 板卡已重置',
        transpile_success: '>>> Mind+ 代码转译成功',
        transpile_failed: '转译失败: {message}',
        execution_error: '执行错误: {message}',
        stop_failed: '停止失败: {message}',
        copy_failed: '复制失败: {message}',
        console_copied: '控制台已复制到剪贴板',
        save_empty: '>>> 当前没有可保存的代码',
        save_success: '>>> 已保存到本地',
        save_failed: '保存失败: {message}',
        open_empty: '>>> 没有找到已保存的代码',
        open_confirm_overwrite: '将用已保存的代码覆盖当前编辑器内容，是否继续？',
        open_success: '>>> 已从本地加载代码',
        ai_status_ready: '本地 Ollama / DeepSeek 已就绪',
        ai_status_missing: 'AI 模型不可用，请先启动 Ollama 并拉取 DeepSeek 模型',
        ai_status_error: '无法连接到 Ollama：{message}',
        ai_request_sent: '>>> 已发送 PinPong 改写请求',
        ai_rewrite_applied: '>>> 已将改写结果应用到编辑器',
        ai_rewrite_failed: 'AI 改写失败: {message}',
        ai_rewrite_success: '>>> AI 改写完成',
        buzzer_log: '>>> 蜂鸣器: {freq}Hz',
        shake_log: '>>> 模拟晃动（{mode}）',
        button_label: '按键 {key}',
        touch_pad_label: '触摸按键 {key}',
        mode_mindplus_name: 'Mind+ 上传模式',
        mode_teaching_mpython_name: '教学模式 / mPython',
        mode_teaching_pinpong_name: '教学模式 / PinPong',
        hint_mindplus: '粘贴 Mind+ 上传模式自动生成代码，先转译再运行。',
        hint_mpython: '直接编写 mPython 风格教学代码，适合课堂演示与基础练习。',
        hint_pinpong: '编写 PinPong 课堂代码，可调用本地 AI 做改写与纠错。',
        mindplus_tip_1: '适合从图形化编程过渡到代码执行。',
        mindplus_tip_2: '可先点“转译”查看 Python 结果。',
        mindplus_tip_3: '运行后会同步更新虚拟掌控板状态。',
        mpython_tip_1: '更接近掌控板原生教学写法。',
        mpython_tip_2: '适合 OLED、RGB、按键、传感器入门示例。',
        mpython_tip_3: '可直接运行到当前虚拟板。',
        pinpong_tip_1: '适合课堂代码改写与结构化教学。',
        pinpong_tip_2: '可调用本地 Ollama / DeepSeek 辅助改写。',
        pinpong_tip_3: '建议先写原代码，再使用 AI 优化。',
        sample_mindplus_title: '// Mind+ 上传模式示例',
        sample_mpython_title: '# mPython 教学模式示例',
        sample_pinpong_title: '# PinPong 教学模式示例',
        editor_title_mindplus: 'Mind+ 代码输入区',
        editor_title_teaching: '教学代码编辑区',
        runtime_mindplus: 'Mind+ -> Python',
        runtime_mpython: 'mPython Runtime',
        runtime_pinpong: 'PinPong Runtime',
        run_complete_error: '>>> 运行结束，但存在错误',
        board_reset_error: '>>> 重置失败',
    },
    en_US: {
        web_title: 'mPython VM Studio - Dual Mode Teaching Workspace',
        studio_subtitle: 'Dual Mode Teaching Workspace',
        run: 'Run',
        stop: 'Stop',
        reset: 'Reset',
        open: 'Open',
        save: 'Save',
        clear_output: 'Clear Output',
        current_mode: 'Mode',
        interface_language: 'UI',
        workspace_overview: 'Workspace Overview',
        workspace_overview_desc: 'Choose a mode, edit code, and inspect board feedback on the right.',
        runtime_label: 'Runtime',
        learning_modes: 'Learning Modes',
        mindplus_mode_title: 'Mind+ Upload Mode',
        mindplus_mode_desc: 'Paste generated Mind+ upload code, transpile it, and run it on the virtual board.',
        teaching_mode_title: 'Teaching Mode',
        teaching_mode_desc: 'Write mPython / PinPong code directly for classes, demos, and exercises.',
        mode_briefing: 'Mode Briefing',
        code_editor: 'Code Editor',
        clear: 'Clear',
        example: 'Example',
        transpile: 'Transpile',
        transpile_preview: 'Transpiled Preview',
        transpile_preview_desc: 'This area shows the Python result converted from Mind+ code.',
        transpile_preview_empty: 'The transpiled Python result will appear here.',
        ai_rewrite_panel: 'PinPong AI Rewrite',
        ai_panel_desc: 'Send classroom instructions to local AI and get cleaner PinPong teaching code.',
        refresh_status: 'Refresh',
        ai_instruction_placeholder: 'Example: rewrite this code so it is easier for beginners to understand and keep helpful comments.',
        rewrite_code: 'Rewrite',
        rewriting: 'Rewriting',
        apply_rewrite: 'Apply Rewrite',
        rewrite_result: 'Rewrite Result',
        rewrite_result_empty: 'The rewritten code from AI will appear here.',
        console: 'Console',
        console_desc: 'Runtime output, errors, and classroom hints appear here.',
        copy: 'Copy',
        rgb_led: 'RGB LED',
        sensor_control: 'Sensors',
        light_sensor: 'Light Sensor',
        sound_sensor: 'Sound Sensor',
        accelerometer: 'Accelerometer',
        gyroscope: 'Gyroscope',
        magnetic_sensor: 'Magnetic Sensor',
        buzzer: 'Buzzer',
        play: 'Play',
        board_control: 'Board Control',
        board_preview_title: 'Virtual Board',
        board_preview_desc: 'Preview OLED, RGB, button, and touch states after execution.',
        shake: 'Shake',
        clear_screen: 'Clear Screen',
        shake_x: 'Shake X',
        shake_y: 'Shake Y',
        shake_z: 'Shake Z',
        sensor_panel_desc: 'Manually control sensors, buzzer, and board actions.',
        connected: 'Connected',
        disconnected: 'Disconnected',
        running_status: '● Running',
        ready_status: '○ Ready',
        board_subtext: 'Teaching Virtual Board',
        backend_connected: '>>> Connected to Python backend',
        offline_mode: '>>> Python backend is not connected, running in offline simulation mode',
        startup_hint: '>>> Start the full app with python main.py',
        code_start: '>>> Starting execution...',
        code_finished: '>>> Execution finished',
        stopped: '>>> Execution stopped',
        board_reset: '>>> Board reset',
        transpile_success: '>>> Mind+ code transpiled successfully',
        transpile_failed: 'Transpile failed: {message}',
        execution_error: 'Execution error: {message}',
        stop_failed: 'Stop failed: {message}',
        copy_failed: 'Copy failed: {message}',
        console_copied: 'Console copied to clipboard',
        save_empty: '>>> No code to save',
        save_success: '>>> Saved locally',
        save_failed: 'Save failed: {message}',
        open_empty: '>>> No saved code found',
        open_confirm_overwrite: 'Overwrite the current editor content with saved code?',
        open_success: '>>> Loaded saved code',
        ai_status_ready: 'Local Ollama / DeepSeek is ready',
        ai_status_missing: 'AI model is unavailable. Start Ollama and pull a DeepSeek model first.',
        ai_status_error: 'Cannot connect to Ollama: {message}',
        ai_request_sent: '>>> PinPong rewrite request sent',
        ai_rewrite_applied: '>>> Rewritten code applied to editor',
        ai_rewrite_failed: 'AI rewrite failed: {message}',
        ai_rewrite_success: '>>> AI rewrite finished',
        buzzer_log: '>>> Buzzer: {freq}Hz',
        shake_log: '>>> Shaking ({mode})',
        button_label: 'Button {key}',
        touch_pad_label: 'Touch pad {key}',
        mode_mindplus_name: 'Mind+ Upload Mode',
        mode_teaching_mpython_name: 'Teaching / mPython',
        mode_teaching_pinpong_name: 'Teaching / PinPong',
        hint_mindplus: 'Paste Mind+ generated upload code, transpile first, then run.',
        hint_mpython: 'Write mPython-style teaching code directly for demos and exercises.',
        hint_pinpong: 'Write PinPong classroom code and optionally rewrite it with local AI.',
        mindplus_tip_1: 'Good for transitioning from block programming to code execution.',
        mindplus_tip_2: 'Use "Transpile" first to inspect the Python result.',
        mindplus_tip_3: 'Running will update the virtual board immediately.',
        mpython_tip_1: 'Closer to native mPython teaching examples.',
        mpython_tip_2: 'Good for OLED, RGB, button, and sensor basics.',
        mpython_tip_3: 'Runs directly on the current virtual board.',
        pinpong_tip_1: 'Good for structured classroom code examples.',
        pinpong_tip_2: 'Works with local Ollama / DeepSeek rewrite assistance.',
        pinpong_tip_3: 'Write original code first, then ask AI to improve it.',
        sample_mindplus_title: '// Mind+ upload sample',
        sample_mpython_title: '# mPython teaching sample',
        sample_pinpong_title: '# PinPong teaching sample',
        editor_title_mindplus: 'Mind+ Input',
        editor_title_teaching: 'Teaching Code Editor',
        runtime_mindplus: 'Mind+ -> Python',
        runtime_mpython: 'mPython Runtime',
        runtime_pinpong: 'PinPong Runtime',
        run_complete_error: '>>> Execution finished with errors',
        board_reset_error: '>>> Reset failed',
    },
};

const UI_LANGUAGE_OPTIONS = Object.keys(LANGUAGE_LABELS).map((code) => ({
    value: code,
    label: LANGUAGE_LABELS[code],
}));

function interpolate(template, values = {}) {
    return String(template).replace(/\{(\w+)\}/g, (_, key) => values[key] ?? `{${key}}`);
}

function detectUiLanguage() {
    const stored = window.localStorage?.getItem('mpython-vm-web-ui-language');
    if (stored && TRANSLATIONS[stored]) return stored;
    return 'zh_CN';
}

function getEditorLanguage(productMode) {
    return productMode === 'mindplus' ? 'plaintext' : 'python';
}

const EXAMPLES = {
    mindplus(t) {
        return `${t('sample_mindplus_title')}
当启动时
    OLED.Show("Hello Mind+")
    RGB.SetPixelColor(0, 0xFF0000)
    RGB.Write()
    延时 500ms
    OLED.Show("Ready")
`;
    },
    mpython(t) {
        return `${t('sample_mpython_title')}
import time

oled.print("Hello mPython")
time.sleep(0.5)

for i in range(3):
    rgb[i] = (0, 120, 255)
rgb.write()

print("light =", light.read())
print("sound =", sound.read())
`;
    },
    pinpong(t) {
        return `${t('sample_pinpong_title')}
init()

oled = get_oled()
rgb = get_rgb()

oled.clear()
oled.write("Hello PinPong")
oled.show()

rgb.write(255, 180, 0)
delay(500)
rgb.write(0, 180, 255)
`;
    },
};

const App = {
    setup() {
        const uiLanguage = ref(detectUiLanguage());
        const productMode = ref('mindplus');
        const teachingMode = ref('mpython');
        const running = ref(false);
        const rewriting = ref(false);
        const connected = ref(false);
        const showSensors = ref(false);
        const sensorSource = ref('device');
        const sensorDeviceConnected = ref(false);
        const sensorPorts = ref([]);
        const selectedPort = ref('');
        const sensorConnecting = ref(false);
        const shaking = ref(false);
        const cursorVisible = ref(true);
        const transpiledCode = ref('');
        const rewrittenCode = ref('');
        const rewriteInstruction = ref('');
        const bottomPanel = ref('console');
        const aiStatus = reactive({
            state: 'unknown',
            message: '',
            model: '',
        });

        const lightValue = ref(0);
        const soundValue = ref(0);
        const buzzerFreq = ref(1000);
        const oledCanvas = ref(null);
        const consoleOutput = ref([]);

        const state = reactive({
            oled_text: Array(8).fill(''),
            oled_buffer: Array(128 * 8).fill(0),
            rgb_colors: [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
            button_a: false,
            button_b: false,
            touch: { P: false, Y: false, T: false, H: false, O: false, N: false },
            accel: { x: 0, y: 0, z: 0 },
            gyro: { x: 0, y: 0, z: 0 },
            mag: { x: 0, y: 0, z: 0 },
            light: 0,
            sound: 0,
        });

        const touchPads = TouchPositions;
        const screwPositions = ScrewPositions;
        const uiLanguageOptions = UI_LANGUAGE_OPTIONS;
        let editor = null;
        let editorFallback = null;
        let consoleId = 0;
        let pywebviewApi = null;
        let pollTimer = null;
        let monacoLoading = false;

        const t = (key, values) => {
            const bundle = TRANSLATIONS[uiLanguage.value] || TRANSLATIONS.zh_CN;
            return interpolate(bundle[key] || TRANSLATIONS.zh_CN[key] || key, values);
        };

        const currentModeLabel = computed(() => {
            if (productMode.value === 'mindplus') return t('mode_mindplus_name');
            if (teachingMode.value === 'pinpong') return t('mode_teaching_pinpong_name');
            return t('mode_teaching_mpython_name');
        });

        const currentModeDescription = computed(() => {
            if (productMode.value === 'mindplus') return t('mindplus_mode_desc');
            if (teachingMode.value === 'pinpong') return t('hint_pinpong');
            return t('hint_mpython');
        });

        const currentModeTips = computed(() => {
            if (productMode.value === 'mindplus') return [t('mindplus_tip_1'), t('mindplus_tip_2'), t('mindplus_tip_3')];
            if (teachingMode.value === 'pinpong') return [t('pinpong_tip_1'), t('pinpong_tip_2'), t('pinpong_tip_3')];
            return [t('mpython_tip_1'), t('mpython_tip_2'), t('mpython_tip_3')];
        });

        const editorTitle = computed(() => (
            productMode.value === 'mindplus' ? t('editor_title_mindplus') : t('editor_title_teaching')
        ));

        const currentRuntimeLabel = computed(() => {
            if (productMode.value === 'mindplus') return t('runtime_mindplus');
            if (teachingMode.value === 'pinpong') return t('runtime_pinpong');
            return t('runtime_mpython');
        });

        const currentEditorHint = computed(() => {
            if (productMode.value === 'mindplus') return t('hint_mindplus');
            if (teachingMode.value === 'pinpong') return t('hint_pinpong');
            return t('hint_mpython');
        });

        const activePanelLabel = computed(() => {
            if (bottomPanel.value === 'transpile') return '转译结果';
            if (bottomPanel.value === 'ai') return 'AI 改写';
            return '运行输出';
        });

        const activeLedCount = computed(() => state.rgb_colors.filter((color) => {
            const [r, g, b] = color || [0, 0, 0];
            return Number(r) || Number(g) || Number(b);
        }).length);

        const pressedInputCount = computed(() => {
            let count = 0;
            if (state.button_a) count += 1;
            if (state.button_b) count += 1;
            count += Object.values(state.touch).filter(Boolean).length;
            return count;
        });

        const touchActiveCount = computed(() => Object.values(state.touch).filter(Boolean).length);

        const sensorPanelLabel = computed(() => showSensors.value ? '控制已展开' : '控制已收起');
        const sensorSourceLabel = computed(() => sensorSource.value === 'manual' ? '手动控制' : '真实传感器');
        const sensorConnectionText = computed(() => {
            if (sensorSource.value === 'manual') return '当前使用手动控制值';
            return sensorDeviceConnected.value ? '已连接真实传感器' : '未连接真实传感器';
        });
        const sensorValueVisible = computed(() => sensorSource.value === 'manual' || sensorDeviceConnected.value);

        const bottomPanelTitle = computed(() => {
            if (bottomPanel.value === 'transpile') return t('transpile_preview');
            if (bottomPanel.value === 'ai') return t('ai_rewrite_panel');
            return t('console');
        });

        const bottomPanelHint = computed(() => {
            if (bottomPanel.value === 'transpile') return t('transpile_preview_desc');
            if (bottomPanel.value === 'ai') return t('ai_panel_desc');
            return t('console_desc');
        });

        const bottomPanelMeta = computed(() => {
            if (bottomPanel.value === 'transpile') {
                return transpiledCode.value ? '已生成预览' : '等待转译';
            }
            if (bottomPanel.value === 'ai') {
                return rewriting.value ? t('rewriting') : aiStatusText.value;
            }
            return `日志 ${consoleOutput.value.length} 条`;
        });

        const aiStatusText = computed(() => {
            if (aiStatus.state === 'ready') return t('ai_status_ready');
            if (aiStatus.state === 'missing') return t('ai_status_missing');
            if (aiStatus.state === 'error') return t('ai_status_error', { message: aiStatus.message || 'unknown error' });
            return t('refresh_status');
        });

        const aiStatusClass = computed(() => ({
            ready: aiStatus.state === 'ready',
            missing: aiStatus.state === 'missing',
            error: aiStatus.state === 'error',
        }));

        function formatSensorScalar(value, digits = 0) {
            if (!sensorValueVisible.value) return '--';
            const num = Number(value);
            return Number.isFinite(num) ? num.toFixed(digits) : '--';
        }

        function formatSensorVector(vector, digits = 2) {
            if (!sensorValueVisible.value) return '--';
            return `x ${formatSensorScalar(vector?.x, digits)} / y ${formatSensorScalar(vector?.y, digits)} / z ${formatSensorScalar(vector?.z, digits)}`;
        }

        function updateDocumentMeta() {
            document.title = t('web_title');
            document.documentElement.lang = uiLanguage.value.replace('_', '-');
        }

        function appendConsole(text, type = 'info') {
            const time = new Date().toLocaleTimeString();
            consoleOutput.value.push({ id: ++consoleId, text: `[${time}] ${text}`, type });
            if (consoleOutput.value.length > 200) consoleOutput.value.shift();
        }

        function currentLanguageValue() {
            if (productMode.value === 'mindplus') return 'mindplus';
            return teachingMode.value === 'pinpong' ? 'pinpong' : 'python';
        }

        function loadExample(force = false) {
            if (!editor && !editorFallback) return;
            if (!force && getEditorCode().trim()) return;
            const text = productMode.value === 'mindplus'
                ? EXAMPLES.mindplus(t)
                : teachingMode.value === 'pinpong'
                    ? EXAMPLES.pinpong(t)
                    : EXAMPLES.mpython(t);
            setEditorCode(text);
            transpiledCode.value = '';
            rewrittenCode.value = '';
        }

        function clearCode() {
            setEditorCode('');
            transpiledCode.value = '';
            rewrittenCode.value = '';
        }

        function storageKey() {
            return `mpython-vm-web-code-${currentLanguageValue()}`;
        }

        function saveCode() {
            if (!editor && !editorFallback) return;
            const code = getEditorCode();
            if (!code.trim()) {
                appendConsole(t('save_empty'), 'info');
                return;
            }
            try {
                window.localStorage?.setItem(storageKey(), code);
                appendConsole(t('save_success'), 'success');
            } catch (error) {
                appendConsole(t('save_failed', { message: error.message }), 'error');
            }
        }

        function openCode() {
            if (!editor && !editorFallback) return;
            let saved = '';
            try {
                saved = window.localStorage?.getItem(storageKey()) || '';
            } catch (error) {
                appendConsole(t('save_failed', { message: error.message }), 'error');
                return;
            }
            if (!saved) {
                appendConsole(t('open_empty'), 'info');
                return;
            }
            const current = getEditorCode();
            if (current.trim() && current.trim() !== saved.trim()) {
                const ok = window.confirm(t('open_confirm_overwrite'));
                if (!ok) return;
            }
            setEditorCode(saved);
            bottomPanel.value = 'console';
            appendConsole(t('open_success'), 'success');
        }

        function renderOled() {
            const canvas = oledCanvas.value;
            if (!canvas) return;
            const ctx = canvas.getContext('2d');
            if (!ctx) return;
            ctx.fillStyle = '#0a0a0a';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            const buffer = Array.isArray(state.oled_buffer) ? state.oled_buffer : [];
            const hasBuffer = buffer.length >= 128 * 8 && buffer.some((value) => Number(value) !== 0);

            if (hasBuffer) {
                ctx.fillStyle = '#90d17d';
                for (let page = 0; page < 8; page += 1) {
                    for (let col = 0; col < 128; col += 1) {
                        const byteVal = Number(buffer[page * 128 + col] || 0);
                        if (!byteVal) continue;
                        for (let bit = 0; bit < 8; bit += 1) {
                            if (byteVal & (1 << (7 - bit))) {
                                ctx.fillRect(col, page * 8 + bit, 1, 1);
                            }
                        }
                    }
                }
                return;
            }

            ctx.fillStyle = '#90d17d';
            ctx.font = '8px Consolas';
            ctx.textBaseline = 'top';
            const lines = Array.isArray(state.oled_text) ? state.oled_text : [];
            for (let i = 0; i < Math.min(lines.length, 8); i += 1) {
                ctx.fillText(String(lines[i] || ''), 0, i * 8);
            }
            if (cursorVisible.value) ctx.fillRect(0, Math.min(lines.length, 7) * 8, 4, 8);
        }

        function applyState(data) {
            if (!data) return;
            if (data.oled_text) state.oled_text = data.oled_text;
            if (data.oled_buffer) state.oled_buffer = data.oled_buffer;
            if (data.rgb_colors) state.rgb_colors = data.rgb_colors;
            if (data.button_a !== undefined) state.button_a = !!data.button_a;
            if (data.button_b !== undefined) state.button_b = !!data.button_b;
            if (data.touch) Object.assign(state.touch, data.touch);
            if (data.accel) state.accel = data.accel;
            if (data.gyro) state.gyro = data.gyro;
            if (data.mag) state.mag = data.mag;
            if (data.sensor_source) sensorSource.value = data.sensor_source;
            if (data.sensor_device_connected !== undefined) sensorDeviceConnected.value = !!data.sensor_device_connected;
            if (data.light !== undefined) {
                state.light = data.light;
                lightValue.value = data.light;
            }
            if (data.sound !== undefined) {
                state.sound = data.sound;
                soundValue.value = data.sound;
            }
            if (data.buzzer?.freq !== undefined) buzzerFreq.value = data.buzzer.freq;
            renderOled();
        }

        async function selectSensorSource(source) {
            sensorSource.value = source;
            showSensors.value = source === 'manual';
            if (!pywebviewApi) return;
            try {
                const result = await pywebviewApi.set_sensor_source(source);
                applyState(result);
            } catch {
                // Keep local selection when backend bridge is unavailable.
            }
        }

        async function scanSensorPorts() {
            if (!pywebviewApi) return;
            try {
                const ports = await pywebviewApi.list_sensor_ports();
                sensorPorts.value = Array.isArray(ports) ? ports : [];
                if (!selectedPort.value && sensorPorts.value.length > 0) {
                    selectedPort.value = sensorPorts.value[0];
                }
            } catch {
                sensorPorts.value = [];
            }
        }

        async function toggleSensorDevice() {
            if (!pywebviewApi) return;
            sensorConnecting.value = true;
            try {
                if (sensorDeviceConnected.value) {
                    const result = await pywebviewApi.disconnect_sensor_device();
                    applyState(result.state);
                    appendConsole('>>> 已断开真实传感器设备', 'info');
                } else {
                    const result = await pywebviewApi.connect_sensor_device(selectedPort.value || '');
                    applyState(result.state);
                    if (result.status === 'ok') {
                        appendConsole(`>>> 已连接真实传感器设备（${result.port}）`, 'success');
                    } else {
                        appendConsole(`>>> 连接失败：${result.message || '未知错误'}`, 'error');
                    }
                }
            } catch (e) {
                appendConsole('>>> 传感器设备操作失败：' + (e && e.message ? e.message : String(e)), 'error');
            } finally {
                sensorConnecting.value = false;
            }
        }

        async function pollState() {
            if (!pywebviewApi) return;
            try {
                const raw = await pywebviewApi.poll_state();
                if (raw) {
                    connected.value = true;
                    applyState(JSON.parse(raw));
                }
            } catch {
                connected.value = false;
            }
        }

        async function transpileMindPlus() {
            bottomPanel.value = 'transpile';
            if (!editor && !editorFallback) return;
            const code = getEditorCode();
            if (!code.trim()) return;

            if (!pywebviewApi) {
                transpiledCode.value = code;
                appendConsole(t('offline_mode'), 'info');
                return;
            }

            const result = await pywebviewApi.transpile_code(code);
            if (result.status === 'ok') {
                transpiledCode.value = result.code;
                appendConsole(t('transpile_success'), 'success');
            } else {
                transpiledCode.value = '';
                appendConsole(t('transpile_failed', { message: result.message || 'unknown error' }), 'error');
            }
        }

        async function runCode() {
            if (!editor && !editorFallback) return;
            const code = getEditorCode();
            if (!code.trim()) return;

            running.value = true;
            appendConsole(t('code_start'), 'info');

            try {
                if (!pywebviewApi) {
                    appendConsole(t('offline_mode'), 'info');
                    appendConsole(t('code_finished'), 'info');
                    return;
                }

                const result = await pywebviewApi.execute_code(code, currentLanguageValue());
                if (result?.output) {
                    result.output.split('\n').forEach((line) => {
                        if (!line.trim()) return;
                        const type = result.status === 'error' ? 'error' : 'success';
                        appendConsole(line, type);
                    });
                }
                if (result?.state) applyState(result.state);
                if (result?.status === 'error') {
                    appendConsole(t('run_complete_error'), 'error');
                } else {
                    appendConsole(t('code_finished'), 'info');
                }
            } catch (error) {
                appendConsole(t('execution_error', { message: error.message }), 'error');
            } finally {
                running.value = false;
            }
        }

        async function stopCode() {
            running.value = false;
            if (!pywebviewApi) {
                appendConsole(t('stopped'), 'info');
                return;
            }

            try {
                const result = await pywebviewApi.stop_execution();
                applyState(result);
                appendConsole(t('stopped'), 'info');
            } catch (error) {
                appendConsole(t('stop_failed', { message: error.message }), 'error');
            }
        }

        async function resetBoard() {
            if (!pywebviewApi) {
                state.oled_text = Array(8).fill('');
                state.oled_buffer = Array(128 * 8).fill(0);
                state.rgb_colors = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
                renderOled();
                appendConsole(t('board_reset'), 'info');
                return;
            }

            try {
                const result = await pywebviewApi.reset();
                applyState(result);
                appendConsole(t('board_reset'), 'info');
            } catch {
                appendConsole(t('board_reset_error'), 'error');
            }
        }

        function setButton(btn, pressed) {
            if (btn === 'A') state.button_a = pressed;
            if (btn === 'B') state.button_b = pressed;
            if (pywebviewApi) {
                pywebviewApi.set_button(btn, pressed ? 'true' : 'false')
                    .then((result) => applyState(result))
                    .catch(() => {});
            }
        }

        function setTouch(pad, pressed) {
            state.touch[pad] = pressed;
            if (pywebviewApi) {
                pywebviewApi.set_touch(pad, pressed ? 'true' : 'false')
                    .then((result) => applyState(result))
                    .catch(() => {});
            }
        }

        function capturePointer(event) {
            const element = event?.currentTarget;
            if (element && typeof element.setPointerCapture === 'function') {
                try {
                    element.setPointerCapture(event.pointerId);
                } catch {
                    // Ignore platforms that do not support pointer capture here.
                }
            }
        }

        function releasePointer(event) {
            const element = event?.currentTarget;
            if (element && typeof element.releasePointerCapture === 'function') {
                try {
                    element.releasePointerCapture(event.pointerId);
                } catch {
                    // Ignore platforms that do not support pointer capture here.
                }
            }
        }

        function handleButtonPointerDown(btn, event) {
            capturePointer(event);
            setButton(btn, true);
        }

        function handleButtonPointerUp(btn, event) {
            releasePointer(event);
            setButton(btn, false);
        }

        function handleButtonPointerLeave(btn, event) {
            if (event?.buttons === 1 || event?.pointerType === 'touch') {
                setButton(btn, false);
            }
        }

        function handleTouchPointerDown(pad, event) {
            capturePointer(event);
            setTouch(pad, true);
        }

        function handleTouchPointerUp(pad, event) {
            releasePointer(event);
            setTouch(pad, false);
        }

        function handleTouchPointerLeave(pad, event) {
            if (event?.buttons === 1 || event?.pointerType === 'touch') {
                setTouch(pad, false);
            }
        }

        function updateSensor(sensor, value) {
            if (sensorSource.value !== 'manual') return;
            const intValue = parseInt(value, 10);
            if (sensor === 'light') {
                state.light = intValue;
                lightValue.value = intValue;
            }
            if (sensor === 'sound') {
                state.sound = intValue;
                soundValue.value = intValue;
            }
            if (pywebviewApi) {
                pywebviewApi.set_sensor(sensor, intValue)
                    .then((result) => applyState(result))
                    .catch(() => {});
            }
        }

        const SENSOR_POPUP_CONFIG = {
            light: { min: 0, max: 4095, step: 1 },
            sound: { min: 0, max: 4095, step: 1 },
            accel: { min: -2, max: 2, step: 0.05 },
            gyro: { min: -5, max: 5, step: 0.05 },
            mag: { min: -100, max: 100, step: 1 },
            buzzer: { min: 0, max: 4000, step: 50 },
        };

        const sensorPopup = reactive({
            visible: false,
            title: '',
            key: '',
            axis: '',
            min: 0,
            max: 100,
            step: 1,
            value: 0,
            x: 0,
            y: 0,
        });

        function sensorPopupTitle(key, axis) {
            const names = {
                light: t('light_sensor'),
                sound: t('sound_sensor'),
                accel: t('accelerometer'),
                gyro: t('gyroscope'),
                mag: t('magnetic_sensor'),
                buzzer: t('buzzer'),
            };
            const base = names[key] || key;
            return axis ? `${base} ${axis.toUpperCase()}` : base;
        }

        function readSensorValue(key, axis) {
            if (axis) return state[key][axis];
            if (key === 'light') return lightValue.value;
            if (key === 'sound') return soundValue.value;
            if (key === 'buzzer') return buzzerFreq.value;
            return 0;
        }

        function writeSensorValue(key, axis, value) {
            if (sensorSource.value !== 'manual') return;
            const num = Number(value);
            if (axis) {
                state[key][axis] = num;
                const apiKey = { accel: 'accelerometer', gyro: 'gyro', mag: 'magnetic' }[key];
                if (pywebviewApi) {
                    pywebviewApi.set_sensor(apiKey, state[key])
                        .then((result) => applyState(result))
                        .catch(() => {});
                }
                return;
            }
            if (key === 'light' || key === 'sound') {
                const intVal = parseInt(num, 10);
                state[key] = intVal;
                (key === 'light' ? lightValue : soundValue).value = intVal;
                if (pywebviewApi) {
                    pywebviewApi.set_sensor(key, intVal)
                        .then((result) => applyState(result))
                        .catch(() => {});
                }
                return;
            }
            if (key === 'buzzer') {
                buzzerFreq.value = Math.max(0, Math.min(4000, parseInt(num, 10) || 0));
            }
        }

        function openSensorPopup(event, key, axis = '') {
            const cfg = SENSOR_POPUP_CONFIG[key] || SENSOR_POPUP_CONFIG.light;
            const rect = event.currentTarget.getBoundingClientRect();
            sensorPopup.key = key;
            sensorPopup.axis = axis;
            sensorPopup.title = sensorPopupTitle(key, axis);
            sensorPopup.min = cfg.min;
            sensorPopup.max = cfg.max;
            sensorPopup.step = cfg.step;
            sensorPopup.value = readSensorValue(key, axis);
            sensorPopup.x = rect.left + rect.width / 2;
            sensorPopup.y = rect.bottom + 8;
            sensorPopup.visible = true;
        }

        function updatePopupValue(value) {
            sensorPopup.value = Number(value);
            writeSensorValue(sensorPopup.key, sensorPopup.axis, sensorPopup.value);
        }

        function closeSensorPopup() {
            sensorPopup.visible = false;
        }

        function handlePopupPointerDown(event) {
            if (!sensorPopup.visible) return;
            if (event.target.closest('.sensor-popup') || event.target.closest('.sensor-value-btn')) return;
            closeSensorPopup();
        }

        function setScalarPreset(sensor, value) {
            updateSensor(sensor, value);
        }

        function setEnvPreset(value) {
            updateSensor('light', value);
            updateSensor('sound', value);
        }

        function updateAccel(axis, value) {
            if (sensorSource.value !== 'manual') return;
            state.accel[axis] = parseFloat(value);
            if (pywebviewApi) {
                pywebviewApi.set_sensor('accelerometer', state.accel)
                    .then((result) => applyState(result))
                    .catch(() => {});
            }
        }

        function resetVector(target) {
            if (sensorSource.value !== 'manual') return;
            if (target === 'accel') {
                ['x', 'y', 'z'].forEach((axis) => { state.accel[axis] = 0; });
                if (pywebviewApi) {
                    pywebviewApi.set_sensor('accelerometer', state.accel)
                        .then((result) => applyState(result))
                        .catch(() => {});
                }
                return;
            }
            if (target === 'gyro') {
                ['x', 'y', 'z'].forEach((axis) => { state.gyro[axis] = 0; });
                if (pywebviewApi) {
                    pywebviewApi.set_sensor('gyro', state.gyro)
                        .then((result) => applyState(result))
                        .catch(() => {});
                }
                return;
            }
            if (target === 'mag') {
                ['x', 'y', 'z'].forEach((axis) => { state.mag[axis] = 0; });
                if (pywebviewApi) {
                    pywebviewApi.set_sensor('magnetic', state.mag)
                        .then((result) => applyState(result))
                        .catch(() => {});
                }
            }
        }

        function applyVectorPreset(target, preset) {
            if (sensorSource.value !== 'manual') return;
            if (target === 'accel') {
                if (preset === 'flat') {
                    state.accel = { x: 0, y: 0, z: 1 };
                } else if (preset === 'tilt_x') {
                    state.accel = { x: 1.2, y: 0, z: 0.3 };
                }
                if (pywebviewApi) {
                    pywebviewApi.set_sensor('accelerometer', state.accel)
                        .then((result) => applyState(result))
                        .catch(() => {});
                }
                return;
            }
            if (target === 'gyro') {
                if (preset === 'left') {
                    state.gyro = { x: 0, y: 0, z: -2.5 };
                } else if (preset === 'right') {
                    state.gyro = { x: 0, y: 0, z: 2.5 };
                }
                if (pywebviewApi) {
                    pywebviewApi.set_sensor('gyro', state.gyro)
                        .then((result) => applyState(result))
                        .catch(() => {});
                }
                return;
            }
            if (target === 'mag') {
                if (preset === 'north') {
                    state.mag = { x: 0, y: 80, z: 0 };
                } else if (preset === 'south') {
                    state.mag = { x: 0, y: -80, z: 0 };
                }
                if (pywebviewApi) {
                    pywebviewApi.set_sensor('magnetic', state.mag)
                        .then((result) => applyState(result))
                        .catch(() => {});
                }
            }
        }

        function updateBuzzerValue(value) {
            buzzerFreq.value = Math.max(0, Math.min(4000, parseInt(value, 10) || 0));
        }

        function updateGyro(axis, value) {
            if (sensorSource.value !== 'manual') return;
            state.gyro[axis] = parseFloat(value);
            if (pywebviewApi) {
                pywebviewApi.set_sensor('gyro', state.gyro)
                    .then((result) => applyState(result))
                    .catch(() => {});
            }
        }

        function updateMag(axis, value) {
            if (sensorSource.value !== 'manual') return;
            state.mag[axis] = parseFloat(value);
            if (pywebviewApi) {
                pywebviewApi.set_sensor('magnetic', state.mag)
                    .then((result) => applyState(result))
                    .catch(() => {});
            }
        }

        function playBuzzer() {
            appendConsole(t('buzzer_log', { freq: buzzerFreq.value }), 'info');
            if (pywebviewApi) {
                pywebviewApi.set_sensor('buzzer', parseInt(buzzerFreq.value, 10))
                    .then((result) => applyState(result))
                    .catch(() => {});
            }
        }

        const SHAKE_MODES = {
            x: {
                labelKey: 'shake_x',
                frames: [
                    { x: 2.0, y: 0, z: 1.0 },
                    { x: -2.0, y: 0, z: 1.2 },
                    { x: 1.5, y: 0, z: 1.0 },
                    { x: -1.5, y: 0, z: 1.1 },
                    { x: 0, y: 0, z: 1.0 },
                ],
            },
            y: {
                labelKey: 'shake_y',
                frames: [
                    { x: 0, y: 2.0, z: 1.0 },
                    { x: 0, y: -2.0, z: 1.2 },
                    { x: 0, y: 1.5, z: 1.0 },
                    { x: 0, y: -1.5, z: 1.1 },
                    { x: 0, y: 0, z: 1.0 },
                ],
            },
            z: {
                labelKey: 'shake_z',
                frames: [
                    { x: 0, y: 0, z: 0.3 },
                    { x: 0, y: 0, z: 1.8 },
                    { x: 0, y: 0, z: 0.5 },
                    { x: 0, y: 0, z: 1.6 },
                    { x: 0, y: 0, z: 1.0 },
                ],
            },
        };

        function simulateShake(direction) {
            if (sensorSource.value !== 'manual') return;
            const mode = SHAKE_MODES[direction] || SHAKE_MODES.x;
            appendConsole(t('shake_log', { mode: t(mode.labelKey) }), 'info');
            shaking.value = true;
            mode.frames.forEach((frame, index) => {
                setTimeout(() => {
                    state.accel = { ...frame };
                    if (pywebviewApi) {
                        pywebviewApi.set_sensor('accelerometer', state.accel)
                            .then((result) => applyState(result))
                            .catch(() => {});
                    }
                    if (index === mode.frames.length - 1) shaking.value = false;
                }, index * 120);
            });
        }

        async function clearOled() {
            state.oled_text = Array(8).fill('');
            state.oled_buffer = Array(128 * 8).fill(0);
            renderOled();
            if (pywebviewApi) {
                const result = await pywebviewApi.clear_oled();
                applyState(result);
            }
        }

        function clearConsole() {
            consoleOutput.value = [];
        }

        async function copyConsole() {
            try {
                await navigator.clipboard.writeText(consoleOutput.value.map((line) => line.text).join('\n'));
                appendConsole(t('console_copied'), 'success');
            } catch (error) {
                appendConsole(t('copy_failed', { message: error.message }), 'error');
            }
        }

        async function refreshAiStatus() {
            if (!pywebviewApi) {
                aiStatus.state = 'error';
                aiStatus.message = 'offline';
                return;
            }

            const result = await pywebviewApi.get_ai_status();
            if (result.status === 'ok' && result.available) {
                aiStatus.state = 'ready';
                aiStatus.model = result.model || '';
                aiStatus.message = result.message || '';
            } else if (result.status === 'ok') {
                aiStatus.state = 'missing';
                aiStatus.message = result.message || '';
            } else {
                aiStatus.state = 'error';
                aiStatus.message = result.message || '';
            }
        }

        async function rewriteWithAi() {
            bottomPanel.value = 'ai';
            if ((!editor && !editorFallback) || !pywebviewApi) {
                aiStatus.state = 'error';
                aiStatus.message = 'offline';
                return;
            }

            rewriting.value = true;
            appendConsole(t('ai_request_sent'), 'info');
            try {
                const result = await pywebviewApi.rewrite_pinpong_code(getEditorCode(), rewriteInstruction.value);
                if (result.status === 'ok') {
                    rewrittenCode.value = result.rewritten_code || '';
                    appendConsole(t('ai_rewrite_success'), 'success');
                    await refreshAiStatus();
                } else {
                    appendConsole(t('ai_rewrite_failed', { message: result.message || 'unknown error' }), 'error');
                }
            } catch (error) {
                appendConsole(t('ai_rewrite_failed', { message: error.message }), 'error');
            } finally {
                rewriting.value = false;
            }
        }

        function applyRewrite() {
            if ((!editor && !editorFallback) || !rewrittenCode.value) return;
            setEditorCode(rewrittenCode.value);
            bottomPanel.value = 'console';
            appendConsole(t('ai_rewrite_applied'), 'success');
        }

        function selectProductMode(mode) {
            productMode.value = mode;
            bottomPanel.value = 'console';
            if (mode === 'mindplus') {
                transpiledCode.value = '';
            }
            if (editor) {
                monaco.editor.setModelLanguage(editor.getModel(), getEditorLanguage(mode));
                loadExample(true);
            }
        }

        function selectTeachingMode(mode) {
            productMode.value = 'teaching';
            teachingMode.value = mode;
            bottomPanel.value = 'console';
            if (editor) {
                monaco.editor.setModelLanguage(editor.getModel(), 'python');
                loadExample(true);
            }
            if (mode === 'pinpong') refreshAiStatus();
        }

        function getLedStyle(color) {
            const [r, g, b] = color;
            return (r || g || b)
                ? { background: `radial-gradient(circle, rgb(${r},${g},${b}) 30%, rgba(${r},${g},${b},0.25) 100%)` }
                : { background: 'transparent' };
        }

        function getGlowStyle(color) {
            const [r, g, b] = color;
            return (r || g || b)
                ? {
                    opacity: 0.6,
                    boxShadow: `0 0 18px rgb(${r},${g},${b}), 0 0 36px rgba(${r},${g},${b},0.8)`,
                    background: `radial-gradient(circle, rgba(${r},${g},${b},0.75) 0%, transparent 70%)`,
                }
                : { opacity: 0 };
        }

        function buttonAriaLabel(key) {
            return t('button_label', { key });
        }

        function touchAriaLabel(key) {
            return t('touch_pad_label', { key });
        }

        function createEditor() {
            if (editorFallback) {
                editorFallback.remove();
                editorFallback = null;
            }
            editor = monaco.editor.create(document.getElementById('editor'), {
                value: '',
                language: getEditorLanguage(productMode.value),
                theme: 'vs',
                fontSize: 13,
                lineNumbers: 'on',
                minimap: { enabled: false },
                automaticLayout: true,
                fontFamily: 'Consolas, Monaco, monospace',
                scrollBeyondLastLine: false,
            });

            loadExample(true);

            editor.addCommand(monaco.KeyCode.F5, () => runCode());
            editor.addCommand(monaco.KeyCode.F6, () => stopCode());
            editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => saveCode());
            editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyO, () => openCode());
            editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyL, () => {
                bottomPanel.value = 'console';
                clearConsole();
            });
        }

        function createTextareaEditor() {
            if (editor || editorFallback) return;
            const container = document.getElementById('editor');
            if (!container) return;
            const ta = document.createElement('textarea');
            ta.className = 'editor-fallback';
            ta.spellcheck = false;
            ta.addEventListener('keydown', (e) => {
                if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') { e.preventDefault(); saveCode(); }
                if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'o') { e.preventDefault(); openCode(); }
                if (e.key === 'F5') { e.preventDefault(); runCode(); }
                if (e.key === 'F6') { e.preventDefault(); stopCode(); }
            });
            container.appendChild(ta);
            editorFallback = ta;
            loadExample(true);
        }

        function getEditorCode() {
            if (editor) return editor.getValue();
            if (editorFallback) return editorFallback.value;
            return '';
        }

        function setEditorCode(text) {
            if (editor) { editor.setValue(text); return; }
            if (editorFallback) { editorFallback.value = text; }
        }

        const MONACO_BASE = 'vendor/monaco/vs';

        function loadMonacoLoader() {
            return new Promise((resolve) => {
                if (typeof require !== 'undefined') { resolve(); return; }
                const script = document.createElement('script');
                script.src = MONACO_BASE + '/loader.js';
                script.onload = () => resolve();
                script.onerror = () => resolve();
                document.head.appendChild(script);
            });
        }

        function initEditor() {
            if (typeof monaco !== 'undefined') {
                createEditor();
                return;
            }
            if (monacoLoading) return;
            monacoLoading = true;

            window.MonacoEnvironment = {
                getWorkerUrl: function (moduleId, label) {
                    if (label === 'json') return MONACO_BASE + '/language/json/jsonWorker.js';
                    if (label === 'css' || label === 'scss' || label === 'less') return MONACO_BASE + '/language/css/cssWorker.js';
                    if (label === 'html' || label === 'handlebars' || label === 'razor') return MONACO_BASE + '/language/html/htmlWorker.js';
                    if (label === 'typescript' || label === 'javascript') return MONACO_BASE + '/language/typescript/tsWorker.js';
                    return MONACO_BASE + '/base/worker/workerMain.js';
                },
            };

            loadMonacoLoader().then(() => {
                if (typeof require === 'undefined') {
                    // 本地 loader 加载失败：等待超时降级到 textarea
                    monacoLoading = false;
                    return;
                }
                require.config({
                    paths: {
                        vs: MONACO_BASE,
                    },
                });
                require(['vs/editor/editor.main'], () => {
                    monacoLoading = false;
                    createEditor();
                });
            });

            // Monaco 加载超时降级：8 秒后仍未就绪则切换到 textarea，保证运行/转译可用
            setTimeout(() => {
                if (!editor && !editorFallback) createTextareaEditor();
            }, 8000);
        }

        function startOffline() {
            appendConsole(t('offline_mode'), 'info');
            appendConsole(t('startup_hint'), 'info');
        }

        function resolveBackendApi() {
            if (!window.pywebview || !window.pywebview.api) return null;
            return typeof window.pywebview.api.then === 'function'
                ? window.pywebview.api
                : Promise.resolve(window.pywebview.api);
        }

        function connectBackend() {
            const apiHandle = resolveBackendApi();
            if (!apiHandle) return false;
            apiHandle.then(async (api) => {
                pywebviewApi = api;
                connected.value = true;
                appendConsole(t('backend_connected'), 'success');
                await pollState();
                if (pollTimer) clearInterval(pollTimer);
                pollTimer = setInterval(pollState, 200);
                if (teachingMode.value === 'pinpong') refreshAiStatus();
            }).catch(() => {
                connected.value = false;
                startOffline();
            });
            return true;
        }

        watch(uiLanguage, (value) => {
            window.localStorage?.setItem('mpython-vm-web-ui-language', value);
            updateDocumentMeta();
        }, { immediate: true });

        watch(productMode, () => {
            rewrittenCode.value = '';
            transpiledCode.value = '';
        });

        onMounted(() => {
            initEditor();
            renderOled();
            document.addEventListener('pointerdown', handlePopupPointerDown);

            if (!connectBackend()) {
                window.addEventListener('pywebviewready', connectBackend, { once: true });
                setTimeout(() => {
                    if (!connected.value && !pywebviewApi) startOffline();
                }, 2500);
            }

            setInterval(() => {
                cursorVisible.value = !cursorVisible.value;
                renderOled();
            }, 500);
        });

        return {
            uiLanguage,
            uiLanguageOptions,
            productMode,
            teachingMode,
            running,
            rewriting,
            connected,
            showSensors,
            sensorSource,
            sensorDeviceConnected,
            sensorPorts,
            selectedPort,
            sensorConnecting,
            shaking,
            bottomPanel,
            transpiledCode,
            rewrittenCode,
            rewriteInstruction,
            aiStatusText,
            aiStatusClass,
            formatSensorScalar,
            formatSensorVector,
            currentModeLabel,
            currentModeDescription,
            currentModeTips,
            editorTitle,
            currentRuntimeLabel,
            currentEditorHint,
            activePanelLabel,
            activeLedCount,
            pressedInputCount,
            touchActiveCount,
            sensorPanelLabel,
            sensorSourceLabel,
            sensorConnectionText,
            sensorValueVisible,
            bottomPanelTitle,
            bottomPanelHint,
            bottomPanelMeta,
            lightValue,
            soundValue,
            buzzerFreq,
            oledCanvas,
            consoleOutput,
            state,
            touchPads,
            screwPositions,
            t,
            runCode,
            stopCode,
            resetBoard,
            transpileMindPlus,
            rewriteWithAi,
            applyRewrite,
            refreshAiStatus,
            selectSensorSource,
            scanSensorPorts,
            toggleSensorDevice,
            selectProductMode,
            selectTeachingMode,
            clearCode,
            loadExample,
            clearConsole,
            copyConsole,
            saveCode,
            openCode,
            setButton,
            setTouch,
            handleButtonPointerDown,
            handleButtonPointerUp,
            handleButtonPointerLeave,
            handleTouchPointerDown,
            handleTouchPointerUp,
            handleTouchPointerLeave,
            setScalarPreset,
            setEnvPreset,
            updateSensor,
            sensorPopup,
            openSensorPopup,
            updatePopupValue,
            closeSensorPopup,
            updateAccel,
            updateGyro,
            updateMag,
            resetVector,
            applyVectorPreset,
            updateBuzzerValue,
            playBuzzer,
            simulateShake,
            clearOled,
            getLedStyle,
            getGlowStyle,
            buttonAriaLabel,
            touchAriaLabel,
        };
    },
};

const app = createApp(App);
app.config.errorHandler = (err) => {
    const box = document.getElementById('fatal-error');
    if (box) {
        box.style.display = 'block';
        box.textContent = '页面错误：' + (err && err.message ? err.message : String(err));
    }
};
try {
    app.mount('#app');
} catch (err) {
    const box = document.getElementById('fatal-error');
    if (box) {
        box.style.display = 'block';
        box.textContent = '启动失败：' + (err && err.message ? err.message : String(err));
    }
}
