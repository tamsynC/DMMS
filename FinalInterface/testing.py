import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QSlider
from PyQt5.QtCore import *


class ButtonDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

        self.mode = 0

        self.autoState = False

    def init_ui(self):
        self.setWindowTitle("State Control for Auto Manual Modes")
        self.resize(300, 150)

        self.control_mode = QSlider(Qt.Horizontal)
        self.control_mode.setMinimum(0)
        self.control_mode.setMaximum(1)
        self.control_mode.setValue(0)

        self.control_mode.valueChanged.connect(self.updateMode)

        # Create button
        self.button = QPushButton("Hold or Click Me", self)

        # Connect signals
        self.button.clicked.connect(self.on_clicked)
        self.button.pressed.connect(self.on_pressed)
        self.button.released.connect(self.on_released)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.control_mode)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def updateMode(self, value):
        self.mode = value

    def on_clicked(self):
        if self.mode == 1: 
            print("Clicked")
            self.autoState = not self.autoState
            print(f"{self.autoState}")
        else:
            pass

    def on_pressed(self):
        if self.mode == 0: 
            print("Pressed")
        else:
            pass

    def on_released(self):
        if self.mode == 0: 
            print("Released")
        else:
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ButtonDemo()
    window.show()
    sys.exit(app.exec_())
