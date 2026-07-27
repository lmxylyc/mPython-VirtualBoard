class VirtualMPython {
    constructor(runtime) {
        this.runtime = runtime;
        this.socket = null;
        this.host = '127.0.0.1';
        this.port = 7777;
        this.connected = false;
        this.buffer = '';
    }

    _sendCommand(command) {
        if (this.socket && this.connected) {
            try {
                this.socket.send(JSON.stringify(command) + '\n');
            } catch (e) {
                console.error('发送失败:', e);
                this.connected = false;
            }
        }
    }

    _connect() {
        return new Promise((resolve, reject) => {
            if (this.connected) {
                resolve(true);
                return;
            }

            this.socket = new WebSocket(`ws://${this.host}:${this.port}`);
            
            this.socket.onopen = () => {
                this.connected = true;
                resolve(true);
            };

            this.socket.onclose = () => {
                this.connected = false;
                reject('连接关闭');
            };

            this.socket.onerror = (e) => {
                this.connected = false;
                reject(e);
            };

            this.socket.onmessage = (event) => {
                this.buffer += event.data;
                while (this.buffer.includes('\n')) {
                    const [line, rest] = this.buffer.split('\n', 2);
                    this.buffer = rest;
                    try {
                        const response = JSON.parse(line);
                        if (response.event) {
                            this.runtime.emit(response.event, response.data);
                        }
                    } catch (e) {
                        console.error('解析响应失败:', e);
                    }
                }
            };

            setTimeout(() => {
                if (!this.connected) {
                    reject('连接超时');
                }
            }, 5000);
        });
    }

    _connectTCP() {
        return new Promise((resolve, reject) => {
            const net = require('net');
            this.socket = new net.Socket();
            
            this.socket.connect(this.port, this.host, () => {
                this.connected = true;
                resolve(true);
            });

            this.socket.on('close', () => {
                this.connected = false;
            });

            this.socket.on('error', (e) => {
                this.connected = false;
                reject(e);
            });

            this.socket.on('data', (data) => {
                this.buffer += data.toString();
                while (this.buffer.includes('\n')) {
                    const [line, rest] = this.buffer.split('\n', 2);
                    this.buffer = rest;
                    try {
                        const response = JSON.parse(line);
                        if (response.event) {
                            this.runtime.emit(response.event, response.data);
                        }
                    } catch (e) {
                        console.error('解析响应失败:', e);
                    }
                }
            });

            setTimeout(() => {
                if (!this.connected) {
                    reject('连接超时');
                }
            }, 5000);
        });
    }

    async connectToVM(host, port) {
        this.host = host || '127.0.0.1';
        this.port = parseInt(port) || 7777;
        
        try {
            if (typeof WebSocket !== 'undefined') {
                await this._connect();
            } else {
                await this._connectTCP();
            }
            return true;
        } catch (e) {
            console.error('连接失败:', e);
            return false;
        }
    }

    disconnect() {
        if (this.socket) {
            try {
                this.socket.close();
            } catch (e) {}
            this.socket = null;
        }
        this.connected = false;
    }

    oledClear() {
        this._sendCommand({ action: 'oled_clear' });
    }

    oledShowText(text, x, y, size) {
        this._sendCommand({ 
            action: 'oled_show_text', 
            params: { text, x: parseInt(x), y: parseInt(y), size: parseInt(size) } 
        });
    }

    oledShowNumber(num, x, y) {
        this._sendCommand({ 
            action: 'oled_show_number', 
            params: { num: parseFloat(num), x: parseInt(x), y: parseInt(y) } 
        });
    }

    oledShow() {
        this._sendCommand({ action: 'oled_show' });
    }

    oledFill(color) {
        this._sendCommand({ action: 'oled_fill', params: { color: parseInt(color) } });
    }

    rgbLed(r, g, b) {
        this._sendCommand({ 
            action: 'rgb_led', 
            params: { r: parseInt(r), g: parseInt(g), b: parseInt(b) } 
        });
    }

    buttonAIsPressed() {
        return this.runtime.getVariableValue('buttonA') === true;
    }

    buttonBIsPressed() {
        return this.runtime.getVariableValue('buttonB') === true;
    }

    getTemperature() {
        return this.runtime.getVariableValue('temperature') || 25;
    }

    getLight() {
        return this.runtime.getVariableValue('light') || 500;
    }

    getSound() {
        return this.runtime.getVariableValue('sound') || 30;
    }

    beep(freq, duration) {
        this._sendCommand({ 
            action: 'beep', 
            params: { freq: parseInt(freq), duration: parseInt(duration) } 
        });
    }

    getInfo() {
        return {
            name: '虚拟掌控板',
            color: '#00a8ff',
            blockIconURI: null,
            blocks: [
                {
                    opcode: 'connect',
                    blockType: 'command',
                    text: '连接虚拟掌控板 [HOST]:[PORT]',
                    arguments: {
                        HOST: {
                            type: 'string',
                            defaultValue: '127.0.0.1'
                        },
                        PORT: {
                            type: 'string',
                            defaultValue: '7777'
                        }
                    }
                },
                {
                    opcode: 'disconnect',
                    blockType: 'command',
                    text: '断开连接'
                },
                {
                    opcode: 'oled_clear',
                    blockType: 'command',
                    text: 'OLED清屏'
                },
                {
                    opcode: 'oled_show_text',
                    blockType: 'command',
                    text: 'OLED显示文字 [TEXT] 在位置 ([X],[Y]) 字号 [SIZE]',
                    arguments: {
                        TEXT: {
                            type: 'string',
                            defaultValue: 'Hello'
                        },
                        X: {
                            type: 'string',
                            defaultValue: '0'
                        },
                        Y: {
                            type: 'string',
                            defaultValue: '0'
                        },
                        SIZE: {
                            type: 'string',
                            defaultValue: '1'
                        }
                    }
                },
                {
                    opcode: 'oled_show_number',
                    blockType: 'command',
                    text: 'OLED显示数字 [NUM] 在位置 ([X],[Y])',
                    arguments: {
                        NUM: {
                            type: 'string',
                            defaultValue: '0'
                        },
                        X: {
                            type: 'string',
                            defaultValue: '0'
                        },
                        Y: {
                            type: 'string',
                            defaultValue: '0'
                        }
                    }
                },
                {
                    opcode: 'oled_show',
                    blockType: 'command',
                    text: 'OLED刷新显示'
                },
                {
                    opcode: 'oled_fill',
                    blockType: 'command',
                    text: 'OLED填充颜色 [COLOR]',
                    arguments: {
                        COLOR: {
                            type: 'string',
                            defaultValue: '0'
                        }
                    }
                },
                {
                    opcode: 'rgb_led',
                    blockType: 'command',
                    text: 'RGB灯设置颜色 ([R],[G],[B])',
                    arguments: {
                        R: {
                            type: 'string',
                            defaultValue: '255'
                        },
                        G: {
                            type: 'string',
                            defaultValue: '0'
                        },
                        B: {
                            type: 'string',
                            defaultValue: '0'
                        }
                    }
                },
                {
                    opcode: 'beep',
                    blockType: 'command',
                    text: '蜂鸣器响 [FREQ]Hz 持续 [DURATION]ms',
                    arguments: {
                        FREQ: {
                            type: 'string',
                            defaultValue: '523'
                        },
                        DURATION: {
                            type: 'string',
                            defaultValue: '500'
                        }
                    }
                },
                {
                    opcode: 'button_a_pressed',
                    blockType: 'Boolean',
                    text: '按键A是否按下'
                },
                {
                    opcode: 'button_b_pressed',
                    blockType: 'Boolean',
                    text: '按键B是否按下'
                },
                {
                    opcode: 'get_temperature',
                    blockType: 'reporter',
                    text: '温度'
                },
                {
                    opcode: 'get_light',
                    blockType: 'reporter',
                    text: '光线强度'
                },
                {
                    opcode: 'get_sound',
                    blockType: 'reporter',
                    text: '声音强度'
                }
            ],
            menus: {}
        };
    }

    connect(args) {
        this.connectToVM(args.HOST, args.PORT);
    }

    disconnect(args) {
        this.disconnect();
    }

    oled_clear(args) {
        this.oledClear();
    }

    oled_show_text(args) {
        this.oledShowText(args.TEXT, args.X, args.Y, args.SIZE);
    }

    oled_show_number(args) {
        this.oledShowNumber(args.NUM, args.X, args.Y);
    }

    oled_show(args) {
        this.oledShow();
    }

    oled_fill(args) {
        this.oledFill(args.COLOR);
    }

    rgb_led(args) {
        this.rgbLed(args.R, args.G, args.B);
    }

    beep(args) {
        this.beep(args.FREQ, args.DURATION);
    }

    button_a_pressed(args) {
        return this.buttonAIsPressed();
    }

    button_b_pressed(args) {
        return this.buttonBIsPressed();
    }

    get_temperature(args) {
        return this.getTemperature();
    }

    get_light(args) {
        return this.getLight();
    }

    get_sound(args) {
        return this.getSound();
    }
}

module.exports = VirtualMPython;