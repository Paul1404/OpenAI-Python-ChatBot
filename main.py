import sys
import json
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QLineEdit
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QTextCursor
import openai
import configparser
from datetime import datetime


class OpenAIAgent:
    def __init__(self):
        # Read API key from configuration file
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        openai.api_key = self.config['DEFAULT']['OPENAI_API_KEY']

    def get_response(self, message):
        try:
            # Call OpenAI's chat completion endpoint
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": message},
                ]
            )
            # Extract and return the text from the last message from the assistant
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
    responseReady = Signal(str)

    def __init__(self, agent, message):
        super(Worker, self).__init__()
        self.agent = agent
        self.message = message

    def run(self):
        response = self.agent.get_response(self.message)
        self.responseReady.emit(response)


class ChatBot(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize the user interface
        self.text_edit = None
        self.line_edit = None
        self.openai_agent = OpenAIAgent()  # Initialize the OpenAI agent
        self.init_ui()

        self.setWindowTitle("Chat with AI")  # Set window title
        self.resize(800, 600)  # Resize the window to 800 pixels wide and 600 pixels tall

    def init_ui(self):
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)  # Make the text edit read-only

        # Create a label for the user input
        self.input_label = QLabel("Enter your message:")

        self.line_edit = QLineEdit()

        self.line_edit.returnPressed.connect(self.send_message)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.input_label)  # Add the input label to the layout
        layout.addWidget(self.line_edit)

        self.setLayout(layout)

    def send_message(self):
        message = self.line_edit.text().strip()  # Trim leading/trailing whitespace

        if not message:  # Ignore empty messages
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get the current timestamp

        self.text_edit.append(f"{timestamp} You: {message}")
        self.write_to_history(timestamp, "You", message)
        self.line_edit.clear()

        # Ensure the text view scrolls to the bottom
        self.text_edit.moveCursor(QTextCursor.End)

        self.worker = Worker(self.openai_agent, message)
        self.worker.responseReady.connect(self.display_response)
        self.worker.start()

    def display_response(self, response):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get the current timestamp
        self.text_edit.append(f"{timestamp} Bot: {response}")
        self.write_to_history(timestamp, "Bot", response)

        # Ensure the text view scrolls to the bottom
        self.text_edit.moveCursor(QTextCursor.End)

    def write_to_history(self, timestamp, role, message):
        # Load the existing history, if any
        try:
            with open("conversation_history.json", "r") as file:
                history = json.load(file)
        except FileNotFoundError:
            history = []

        # Add the new message to the history
        history.append({"timestamp": timestamp, "role": role, "message": message})

        # Write the updated history back to the file
        with open("conversation_history.json", "w") as file:
            json.dump(history, file)


app = QApplication(sys.argv)
app.setStyleSheet("""
    QWidget {
        font-size: 18px;
    }

    QTextEdit {
        background-color: #f0f0f0;
    }

    QLineEdit {
        background-color: #ffffff;
    }
""")  # Set a global stylesheet

chat_bot = ChatBot()
chat_bot.show()

sys.exit(app.exec())
