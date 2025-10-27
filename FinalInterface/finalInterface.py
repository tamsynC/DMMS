import sys, os, re, cv2
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

import serial, serial.tools.list_ports
import datetime

string_main_title = "Small Conduit Inspector"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(string_main_title)
        self.setWindowIcon(QIcon("Window_Icon.png"))

        # --- Create toolbar ---
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        # --- Add actions to toolbar ---
        action_home = QAction(QIcon("home.png"), "Home", self)
        action_home.triggered.connect(self.on_home)
        toolbar.addAction(action_home)

        action_camera = QAction(QIcon("camera.png"), "Camera", self)
        action_camera.triggered.connect(self.on_camera)
        toolbar.addAction(action_camera)

        # --- Add a central widget ---
        central_widget = QWidget()
        layout = QVBoxLayout()
        button = QPushButton("Click Me!")
        layout.addWidget(button)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def on_home(self):
        print("Home clicked")

    def on_camera(self):
        print("Camera clicked")


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.showMaximized()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()


        