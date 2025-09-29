from PyQt5.QtWidgets import *
import sys

class MainWindow(QWidget):

    def __init__(self, text):
        super().__init__()
        self.setWindowTitle("Main Menu")
        self.setGeometry(100, 100, 1000, 500)
        self.main_menu(text)

    
    def main_menu(self, text):
        layout = QVBoxLayout()
        lable = QLabel(f"Job Name: {text}")

        layout.addWidget(lable)
        self.setLayout(layout)

class StartWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Start Menu")
        self.setGeometry(100, 100, 1000, 500)

        self.start_menu()

    def start_menu(self):
        layout = QVBoxLayout()
        
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Enter Job Name")
        layout.addWidget(self.text_input)

        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.open_main_menu)

        layout.addWidget(self.start_button)
        self.setLayout(layout)

    def open_main_menu(self):
        text = self.text_input.text()
        self.main_menu = MainWindow(text)
        self.main_menu.show()
        self.close()


def main():
    
    app = QApplication(sys.argv)
    start_menu = StartWindow()

    start_menu.show()
    sys.exit(app.exec_()) #exec_ is to execute


if __name__ == "__main__":
    main()