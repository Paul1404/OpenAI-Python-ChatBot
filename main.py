import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit
import openai
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

openai.api_key = config['DEFAULT']['OPENAI_API_KEY']

def get_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=0.5,
        max_tokens=100
    )
    return response.choices[0].text.strip()

class ChatBot(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.text_edit = QTextEdit()
        self.line_edit = QLineEdit()

        self.line_edit.returnPressed.connect(self.send_message)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.line_edit)

        self.setLayout(layout)

    def send_message(self):
        message = self.line_edit.text()
        self.text_edit.append("You: " + message)
        self.text_edit.append("Bot: " + get_response(message))
        self.line_edit.clear()

app = QApplication(sys.argv)

chat_bot = ChatBot()
chat_bot.show()

sys.exit(app.exec_())
