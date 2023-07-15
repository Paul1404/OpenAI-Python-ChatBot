import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit
import openai
import configparser

# Read API key from configuration file
config = configparser.ConfigParser()
config.read('config.ini')
openai.api_key = config['DEFAULT']['OPENAI_API_KEY']


def get_response(prompt):
    """
    This function sends a prompt to the OpenAI API and gets a response.

    Args:
        prompt (str): The input prompt for the OpenAI API.

    Returns:
        str: The text response from the API.
    """

    # Call OpenAI's text completion endpoint
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=0.5,
        max_tokens=100
    )

    # Extract and return the text from the first choice in the response
    return response.choices[0].text.strip()


class ChatBot(QWidget):
    """
    This class defines the main chatbot application GUI. It inherits from QWidget,
    which is a base class for all user interface objects (aka widgets) in PySide6.
    """

    def __init__(self):
        super().__init__()

        # Initialize the user interface
        self.text_edit = None
        self.line_edit = None
        self.init_ui()

    def init_ui(self):
        """
        This function initializes the user interface of the chatbot application.
        """

        # Create a QTextEdit widget for displaying the conversation
        self.text_edit = QTextEdit()

        # Create a QLineEdit widget for user input
        self.line_edit = QLineEdit()

        # Connect the 'returnPressed' signal from the QLineEdit to the 'send_message' function
        self.line_edit.returnPressed.connect(self.send_message)

        # Create a QVBoxLayout for arranging the widgets vertically
        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.line_edit)

        # Set the layout on the widget
        self.setLayout(layout)

    def send_message(self):
        """
        This function sends the user's message to the OpenAI API and updates the QTextEdit
        with the user's message and the API's response.
        """

        # Get the text from the QLineEdit
        message = self.line_edit.text()

        # Append the user's message and the API's response to the QTextEdit
        self.text_edit.append("You: " + message)
        self.text_edit.append("Bot: " + get_response(message))

        # Clear the QLineEdit
        self.line_edit.clear()


# Create an instance of QApplication
app = QApplication(sys.argv)

# Create and show an instance of ChatBot
chat_bot = ChatBot()
chat_bot.show()

# Start the application's event loop
sys.exit(app.exec_())
