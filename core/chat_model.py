import json
import os
import google.generativeai as genai
from PyQt6.QtCore import QThread, pyqtSignal, QObject


class APIWorker(QThread):
    """后台工作线程，专职负责网络请求"""
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, api_key, system_prompt, history, user_input):
        super().__init__()
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.history = history
        self.user_input = user_input

    def run(self):
        try:
            genai.configure(api_key=self.api_key)
            # 【修复 1】: 换成了你账号支持的最新且速度极快的模型
            model = genai.GenerativeModel(
                'gemini-2.0-flash',
                system_instruction=self.system_prompt
            )
            chat = model.start_chat(history=self.history)
            response = chat.send_message(self.user_input)
            self.response_ready.emit(response.text)
        except Exception as e:
            self.error_occurred.emit(str(e))


class ChatModel(QObject):
    """数据模型，管理全局状态和记忆"""
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.history = []
        self.config_file = "config.json"  # 提示词保存路径

    # 【修复 2】: 补充了被遗漏的加载方法，防止 Controller 报错卡死
    def load_last_prompt(self):
        """从本地文件读取提示词"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("last_prompt", "")
            except Exception:
                return ""
        return ""

    def save_last_prompt(self, prompt):
        """保存提示词到本地"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({"last_prompt": prompt}, f, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def generate_reply(self, user_text, system_prompt):
        # 1. 记录用户输入到全局记忆
        self.history.append({"role": "user", "parts": [user_text]})

        # 2. 启动独立线程调用 API
        self.worker = APIWorker(self.api_key, system_prompt, self.history.copy(), user_text)
        self.worker.response_ready.connect(self._on_api_success)
        self.worker.error_occurred.connect(self._on_api_error)
        self.worker.start()

    def _on_api_success(self, text):
        self.history.append({"role": "model", "parts": [text]})
        self.response_ready.emit(text)

    def _on_api_error(self, err_msg):
        if self.history and self.history[-1]["role"] == "user":
            self.history.pop()
        self.error_occurred.emit(err_msg)