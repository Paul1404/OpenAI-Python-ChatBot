import sys
import json
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QLineEdit
from PySide6.QtCore import QThread, Signal, QTimer, QEventLoop
from PySide6.QtGui import QTextCursor
import openai
import configparser
from datetime import datetime


class OpenAIAgent:
    """
    Class representing an agent that interacts with the OpenAI Chat API.
    """

    def __init__(self):
        """
        Initializes the OpenAIAgent class.
        """
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        openai.api_key = self.config['DEFAULT']['OPENAI_API_KEY']

    def get_response(self, message):
        """
        Sends a message to the OpenAI Chat API and returns the response.

        Args:
            message (str): The user's message to send to the API.

        Returns:
            str: The response from the API.
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": message},
                ]
            )
            return response['choices'][0]['message']['content']
        except openai.AuthenticationError:
            print("Invalid API key")
            return "Error: Invalid API key"
        except openai.RateLimitError:
            print("Rate limit exceeded")
            return "Error: Rate limit exceeded"
        except openai.Error as e:
            print(f"OpenAI error: {e}")
            return f"Error: {e}"


class Worker(QThread):
    """
    A worker thread that communicates with the OpenAI agent.
    """

    responseReady = Signal(str)

    def __init__(self, agent, message):
        """
        Initializes the Worker class.

        Args:
            agent (OpenAIAgent): The OpenAIAgent instance to use.
            message (str): The user's message to send to the agent.
        """
        super(Worker, self).__init__()
        self.agent = agent
        self.message = message

    def run(self):
        """
        Runs the worker thread, sends the user's message to the agent, and emits the response signal.
        """
        response = self.agent.get_response(self.message)
        self.responseReady.emit(response)


class ChatBot(QWidget):
    """
    A simple chatbot application that interacts with the user using the OpenAI Chat API.
    """

    def __init__(self):
        """
        Initializes the ChatBot class.
        """
        super().__init__()

        self.text_edit = None
        self.line_edit = None
        self.openai_agent = OpenAIAgent()
        self.init_ui()

        self.setWindowTitle("Chat with AI")
        self.resize(800, 600)

    def init_ui(self):
        """
        Initializes the user interface of the chatbot.
        """
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)

        self.input_label = QLabel("Enter your message:")

        self.line_edit = QLineEdit()

        self.line_edit.returnPressed.connect(self.send_message)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.input_label)
        layout.addWidget(self.line_edit)

        self.setLayout(layout)

    def send_message(self):
        """
        Sends the user's message to the OpenAI agent and handles the response.
        """
        message = self.line_edit.text().strip()

        if not message:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.text_edit.append(f"{timestamp} You: {message}\n")  # Added newline
        self.write_to_history(timestamp, "You", message)
        self.line_edit.clear()

        self.text_edit.moveCursor(QTextCursor.End)

        self.worker = Worker(self.openai_agent, message)
        self.worker.responseReady.connect(self.display_response)
        self.worker.start()

    def display_response(self, response):
        """
        Displays the response from the OpenAI agent in the chat window.

        Args:
            response (str): The response from the OpenAI agent.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.write_to_history(timestamp, "Bot", response)

        for char in f"{timestamp} Bot: {response}\n":  # Added newline
            self.text_edit.moveCursor(QTextCursor.End)
            self.text_edit.insertPlainText(char)
            QApplication.processEvents(QEventLoop.AllEvents, 100)  # Adjusted delay
            QTimer.singleShot(100, lambda: None)  # Adjusted delay

        self.text_edit.append('')

        self.text_edit.moveCursor(QTextCursor.End)

    def write_to_history(self, timestamp, role, message):
        """
        Writes the conversation history to a JSON file.

        Args:
            timestamp (str): The timestamp of the message.
            role (str): The role of the message sender (e.g., "You", "Bot").
            message (str): The content of the message.
        """
        try:
            with open("conversation_history.json", "r") as file:
                history = json.load(file)
        except FileNotFoundError:
            history = []

        history.append({"timestamp": timestamp, "role": role, "message": message})

        with open("conversation_history.json", "w") as file:
            json.dump(history, file)


app = QApplication(sys.argv)
app.setStyleSheet(
    "QWidget {"
    "    font-size: 18px;"
    "}"
    ""
    "QTextEdit {"
    "    background-color: #f0f0f0;"
    "}"
    ""
    "QLineEdit {"
    "    background-color: #ffffff;"
    "}"
)

chat_bot = ChatBot()
chat_bot.show()

sys.exit(app.exec())
