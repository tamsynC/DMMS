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
        self.tool_bar()
        self.main_menu()

    def tool_bar(self):

        # Create Toolbar
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(50, 50))
        self.addToolBar(toolbar)

        spacer1 = QWidget()
        spacer1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer1)

        title = QLabel("Project Title")

        title.setStyleSheet("font-size: 30px;"
                            "font-weight: bold")

        toolbar.addWidget(title)

        spacer2 = QWidget()
        spacer2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer2)

        # Home Buton - Toolbar
        action_home = QAction(QIcon("home.png"), "Home", self)
        action_home.triggered.connect(self.on_home)
        toolbar.addAction(action_home)
        

        # Map Button - Toolbar
        action_map = QAction(QIcon("map.png"), "Map", self)
        action_map.triggered.connect(self.on_map)
        toolbar.addAction(action_map)

        # File Button - Toolbar
        action_camera = QAction(QIcon("camera.png"), "Camera", self)
        action_camera.triggered.connect(self.on_camera)
        toolbar.addAction(action_camera)

    def main_menu(self):

        central_widget = QWidget()
        grid = QGridLayout()

        # Column 1-3 Row 1 - 5
        videofeed = QLabel(" ")

        videofeed.setStyleSheet("background-color: grey;")

        grid.addWidget(videofeed, 0, 0, 5, 3)

        # vbox = QVBoxLayout()
        # vbox.addWidget(QPushButton("Top"))
        # vbox.addWidget(QPushButton("Bottom"))
        # grid.addLayout(vbox, 0, 4)

        #Column 4
        # Row 1 - Auto Manual Slider

        slider_hbox = QHBoxLayout()
        manual = QLabel("Manual")
        manual.setStyleSheet("font-size:16px;")
        slider_hbox.addWidget(manual)

        # 0 = manual 1 = auto
        self.control_mode = QSlider(Qt.Horizontal)
        self.control_mode.setMinimum(0)
        self.control_mode.setMaximum(1)
        self.control_mode.setValue(0)

        # self.control_mode.valueChanged.connect(self.control_mode)


        slider_hbox.addWidget(self.control_mode)


        auto = QLabel("Auto")
        auto.setStyleSheet("font-size:16px;")
        slider_hbox.addWidget(auto)

        grid.addLayout(slider_hbox, 0, 4)

        # Row 2 - Speed Control and Forwards/ backwards

        # Row 3 - Damage Log

        # Row 4 - Take Photo and Start/Stop video

        # Row 5 - Distance, GPS Pos and Orientation

        central_widget.setLayout(grid)

        self.setCentralWidget(central_widget)


    def on_home(self):
        print("Home clicked")

    def on_camera(self):
        print("Camera clicked")
    
    def on_map(self):
        print("Map clicked")

    def control_mode(self, value):
        if value == 1:
            print("Automatic Control")
        else:
            print("Manual Control")


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.showMaximized()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()


        