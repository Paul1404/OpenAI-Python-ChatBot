import sys
import json
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QLineEdit
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QTextCursor
import openai
import configparser
from datetime import datetime


class OpenAIAgent:
    """
    A class to interact with OpenAI's GPT-3 model.
    """
    def __init__(self):
        """
        Initialize the OpenAIAgent class.
        """
        # Read API key from configuration file
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        openai.api_key = self.config['DEFAULT']['OPENAI_API_KEY']

    def get_response(self, message):
        """
        Gets a response from OpenAI's GPT-3 model.
        
        Args:
            message (str): The message to which GPT-3 should respond.

        Returns:
            str: The response from GPT-3.
        """
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
    """
    A QThread worker to interact with OpenAI's GPT-3 model in a non-blocking way.
    """
    responseReady = Signal(str)

    def __init__(self, agent, message):
        """
        Initialize the Worker class.

        Args:
            agent (OpenAIAgent): The agent that interacts with GPT-3.
            message (str): The message to which GPT-3 should respond.
        """
        super(Worker, self).__init__()
        self.agent = agent
        self.message = message

    def run(self):
        """
        The main function that is run when the thread starts.
        It gets a response from GPT-3 and emits a signal when the response is ready.
        """
        response = self.agent.get_response(self.message)
        self.responseReady.emit(response)


class ChatBot(QWidget):
    """
    The main GUI class for the chatbot.
    """
    def __init__(self):
        """
        Initialize the ChatBot class.
        """
        super().__init__()

        # Initialize the user interface
        self.text_edit = None
        self.line_edit = None
        self.openai_agent = OpenAIAgent()  # Initialize the OpenAI agent
        self.init_ui()

        self.setWindowTitle("Chat with AI")  # Set window title
        self.resize(800, 600)  # Resize the window to 800 pixels wide and 600 pixels tall

    def init_ui(self):
        """
        Initializes the user interface.
        """
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
        """
        Sends a message to GPT-3 and displays the response.
        """
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
        """
        Displays the response from GPT-3.

        Args:
            response (str): The response from GPT-3.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get the current timestamp
        self.text_edit.append(f"{timestamp} Bot: {response}")
        self.write_to_history(timestamp, "Bot", response)

        # Ensure the text view scrolls to the bottom
        self.text_edit.moveCursor(QTextCursor.End)

    def write_to_history(self, timestamp, role, message):
        """
        Writes a message to the conversation history.

        Args:
            timestamp (str): The timestamp of the message.
            role (str): The role of the sender ("You" or "Bot").
            message (str): The message text.
        """
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
