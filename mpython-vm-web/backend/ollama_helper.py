import json
import os
import urllib.error
import urllib.request


class OllamaHelper:
    def __init__(self):
        self.base_url = os.environ.get('OLLAMA_BASE_URL', 'http://127.0.0.1:11434')
        self.model = os.environ.get('OLLAMA_MODEL', 'deepseek-r1:8b')

    def get_status(self) -> dict:
        try:
            payload = self._request('/api/tags', method='GET')
        except Exception as exc:
            return {
                'status': 'error',
                'available': False,
                'message': str(exc),
                'model': self.model,
                'models': [],
            }

        models = []
        for item in payload.get('models', []):
            name = item.get('name')
            if name:
                models.append(name)

        matched = self.model in models
        if not matched:
            for name in models:
                if 'deepseek' in name.lower():
                    matched = True
                    break

        return {
            'status': 'ok',
            'available': matched,
            'message': 'ok' if matched else f'Ollama is reachable, but model "{self.model}" is unavailable.',
            'model': self.model,
            'models': models,
        }

    def rewrite_pinpong_code(self, code: str, instruction: str = '') -> dict:
        status = self.get_status()
        if status.get('status') != 'ok' or not status.get('available'):
            return status

        prompt = self._build_prompt(code, instruction)
        payload = self._request(
            '/api/generate',
            {
                'model': self.model,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.3,
                },
            },
        )

        response = payload.get('response', '').strip()
        if not response:
            return {
                'status': 'error',
                'available': True,
                'message': 'Model returned an empty response.',
                'model': self.model,
            }

        cleaned = self._strip_code_fence(response)
        return {
            'status': 'ok',
            'available': True,
            'model': self.model,
            'rewritten_code': cleaned,
            'raw_response': response,
        }

    def _build_prompt(self, code: str, instruction: str) -> str:
        instruction = instruction.strip() or '将这段 PinPong 教学代码改写得更适合学生理解，并修正明显错误。'
        return (
            '你是掌控板课堂助教。请根据要求改写 PinPong 教学代码。\n'
            '规则：\n'
            '1. 只输出最终代码，不要解释。\n'
            '2. 保留 PinPong 教学风格。\n'
            '3. 代码需要尽量简单、清晰、适合学生阅读。\n'
            '4. 如果原代码有明显错误，请直接修正。\n'
            '5. 若需要补全初始化，请补成可运行的课堂示例。\n\n'
            f'改写要求：{instruction}\n\n'
            '原始代码：\n'
            f'{code}\n'
        )

    def _request(self, path: str, data=None, method: str = 'POST') -> dict:
        url = f'{self.base_url}{path}'
        body = None
        headers = {}
        if data is not None:
            body = json.dumps(data).encode('utf-8')
            headers['Content-Type'] = 'application/json'

        request = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=8) as response:
                content = response.read().decode('utf-8')
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode('utf-8', errors='ignore')
            raise RuntimeError(f'Ollama HTTP {exc.code}: {detail or exc.reason}') from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f'Unable to connect to Ollama: {exc.reason}') from exc

        return json.loads(content or '{}')

    def _strip_code_fence(self, text: str) -> str:
        stripped = text.strip()
        if stripped.startswith('```'):
            lines = stripped.splitlines()
            if lines:
                lines = lines[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            return '\n'.join(lines).strip()
        return stripped
