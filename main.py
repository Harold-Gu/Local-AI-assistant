import sys
import os
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication

# 导入自己写的 MVC 模块
from core.chat_model import ChatModel
from ui.chat_view import ChatView
from controllers.chat_controller import ChatController


def main():
    # 1. 加载 .env 文件中的环境变量
    load_dotenv()
    api_key = os.getenv("API_KEY")

    if not api_key:
        print("错误: 请在根目录下创建 .env 文件并填入 API_KEY")
        sys.exit(1)

    app = QApplication(sys.argv)

    # 2. 实例化 MVC 组件
    model = ChatModel(api_key=api_key)
    view = ChatView()
    controller = ChatController(model=model, view=view)

    # 3. 显示界面并运行主循环
    view.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()