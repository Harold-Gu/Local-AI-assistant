from core.chat_model import ChatModel
from ui.chat_view import ChatView


class ChatController:
    """控制器，负责连接 Model 和 View"""

    def __init__(self, model: ChatModel, view: ChatView):
        self.model = model
        self.view = view

        # 启动时读取并设置上一次的提示词
        last_prompt = self.model.load_last_prompt()
        if last_prompt:
            self.view.prompt_input.setPlainText(last_prompt)

        # 监听信号
        self.view.send_requested.connect(self.handle_user_input)
        self.model.response_ready.connect(self.handle_ai_response)
        self.model.error_occurred.connect(self.handle_error)

    def handle_user_input(self, user_text, system_prompt):
        # 用户点击发送时，保存当前的提示词到本地
        self.model.save_last_prompt(system_prompt)

        # 更新 UI 并让模型去工作
        self.view.append_user_message(user_text)
        self.view.show_loading()
        self.model.generate_reply(user_text, system_prompt)

    def handle_ai_response(self, text):
        self.view.hide_loading()
        self.view.append_ai_message(text)

    def handle_error(self, err_msg):
        self.view.hide_loading()
        self.view.show_error(err_msg)