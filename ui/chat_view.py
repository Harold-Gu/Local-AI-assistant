from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QLineEdit, QPushButton, QLabel)
from PyQt6.QtCore import pyqtSignal


class ChatView(QWidget):
    """视图组件，没有任何 API 相关的逻辑"""

    # 定义信号：当用户要求发送消息时触发，携带 (用户文本, 系统提示词)
    send_requested = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('MVC 架构本地聊天机器人')
        self.resize(600, 700)
        layout = QVBoxLayout()

        # 系统提示词输入区
        layout.addWidget(QLabel("全局系统提示词 (System Prompt):"))
        self.prompt_input = QTextEdit()
        self.prompt_input.setFixedHeight(80)
        self.prompt_input.setPlaceholderText("例如：你是一个资深的架构师，请用最精简的代码回答。")
        layout.addWidget(self.prompt_input)

        # 对话展示区
        layout.addWidget(QLabel("对话记录:"))
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        # 用户输入区
        input_layout = QHBoxLayout()
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("输入你的问题...")
        self.user_input.returnPressed.connect(self._trigger_send)

        self.send_btn = QPushButton("发送")
        self.send_btn.clicked.connect(self._trigger_send)

        input_layout.addWidget(self.user_input)
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)
        self.setLayout(layout)

    def _trigger_send(self):
        """收集界面数据并发射信号，交给 Controller 去处理"""
        user_text = self.user_input.text().strip()
        system_prompt = self.prompt_input.toPlainText().strip()
        if user_text:
            self.send_requested.emit(user_text, system_prompt)

    # ==========================================
    # 供 Controller 调用的 UI 更新接口
    # ==========================================
    def append_user_message(self, text):
        self.chat_display.append(f"<b>你:</b> {text}")

    def append_ai_message(self, text):
        self.chat_display.append(f"<b>AI:</b> {text}<br>")

    def show_error(self, err_msg):
        self.chat_display.append(f"<font color='red'><b>发生错误:</b> {err_msg}</font><br>")

    def show_loading(self):
        self.chat_display.append("<i id='loading'>AI 正在思考...</i>")
        self.send_btn.setEnabled(False)
        self.user_input.clear()

    def hide_loading(self):
        current_html = self.chat_display.toHtml()
        self.chat_display.setHtml(current_html.replace("<i id='loading'>AI 正在思考...</i>", ""))
        self.send_btn.setEnabled(True)