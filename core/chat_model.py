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
            # 实时应用最新的系统提示词
            model = genai.GenerativeModel(
                'gemini-1.5-pro-latest',
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
        self.history = []  # 全局记忆力
        self.worker = None

    def generate_reply(self, user_text, system_prompt):
        # 1. 记录用户输入到全局记忆
        self.history.append({"role": "user", "parts": [user_text]})

        # 2. 启动独立线程调用 API，防止阻塞主线程
        self.worker = APIWorker(self.api_key, system_prompt, self.history.copy(), user_text)
        self.worker.response_ready.connect(self._on_api_success)
        self.worker.error_occurred.connect(self._on_api_error)
        self.worker.start()

    def _on_api_success(self, text):
        # 记录 AI 回复到全局记忆
        self.history.append({"role": "model", "parts": [text]})
        self.response_ready.emit(text)

    def _on_api_error(self, err_msg):
        # 请求失败时，撤销刚才加入记忆的用户输入
        if self.history and self.history[-1]["role"] == "user":
            self.history.pop()
        self.error_occurred.emit(err_msg)