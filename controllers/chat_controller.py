from core.chat_model import ChatModel
from ui.chat_view import ChatView


class ChatController:
    """控制器，负责连接 Model 和 View"""

    def __init__(self, model: ChatModel, view: ChatView):
        self.model = model
        self.view = view

        # 1. 监听 View 发出的用户输入信号
        self.view.send_requested.connect(self.handle_user_input)

        # 2. 监听 Model 发出的后台处理结果信号
        self.model.response_ready.connect(self.handle_ai_response)
        self.model.error_occurred.connect(self.handle_error)

    def handle_user_input(self, user_text, system_prompt):
        """View 告诉 Controller：用户点击了发送"""
        self.view.append_user_message(user_text)
        self.view.show_loading()
        # Controller 命令 Model 开始工作
        self.model.generate_reply(user_text, system_prompt)

    def handle_ai_response(self, text):
        """Model 告诉 Controller：AI 回复生成完毕"""
        self.view.hide_loading()
        # Controller 命令 View 显示结果
        self.view.append_ai_message(text)

    def handle_error(self, err_msg):
        """Model 告诉 Controller：发生错误了"""
        self.view.hide_loading()
        self.view.show_error(err_msg)