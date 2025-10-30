import sys, os, re, cv2
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

import serial, serial.tools.list_ports
import datetime

# Initialisation
gps_lat = 0.0
gps_long = 0.0
distance = 0.0
bearing = 0.0
feedback = ""

# Movement Commands
control_mode = ""
movement = ""
speed = ""

string_main_title = "Small Conduit Inspector"

BAUD = 9600
PORT = "COM5" #WINDOWS

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"Connected to port {PORT}")
except serial.SerialException as e:
    ser = None
    print(f"Could not connect to port {PORT}: {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(string_main_title)
        self.setWindowIcon(QIcon("Window_Icon.png"))
        self.tool_bar()
        self.main_menu()

        self.mode = 0
        self.autoForwardState = False
        self.autoBackwardState = False
        self.movement= "Stopped"

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
        main_grid = QGridLayout()

        # Column 1-3 Row 1 - 4
        videofeed = QLabel(" ")

        videofeed.setStyleSheet("background-color: grey;")

        main_grid.addWidget(videofeed, 0, 0, 1, 1)

        # Column 1-3 Row 5 (Feedback)

        feedback = QLabel("Put some feedback here") #to put in the feedback varible
        feedback.setStyleSheet("font-size: 14 px;")
        feedback.setFixedHeight(60) #THIS MAY BE A PROBLEM FOR THE POSITIONAL INFO
        feedback.setAlignment(Qt.AlignCenter)
        main_grid.addWidget(feedback, 1, 0, 1, 1)

        # Control Panel -> add everthing to this then add to the main_grid
        control_panel_vbox = QVBoxLayout()

        control_panel_vbox.setSpacing(30)
        control_panel_vbox.setContentsMargins(10, 10, 10, 10)
           

        #Column 4
        # Row 1 - Auto Manual Slider
        slider_hbox = QHBoxLayout()
        manual = QLabel("Manual")
        manual.setStyleSheet("font-size:20px;")
        slider_hbox.addWidget(manual)
        # 0 = manual 1 = auto
        self.control_mode = QSlider(Qt.Horizontal)
        self.control_mode.setMinimum(0)
        self.control_mode.setMaximum(1)
        self.control_mode.setValue(0)

        self.control_mode.valueChanged.connect(self.updateMode)

        slider_hbox.addWidget(self.control_mode)
        auto = QLabel("Auto")
        auto.setStyleSheet("font-size:20px;")
        slider_hbox.addWidget(auto)

        control_panel_vbox.addLayout(slider_hbox)

        # Row 2 - Speed Control and Forwards/ backwards -> this needs to change funtionaility for auto vs. manual
        # dial column 1 2 rows button 1 column 2 row 1 button 2 column 2 row 2
        # change to vbox layout? dial is very small and 

        navigation_grid = QGridLayout()

        self.speed_dial = QDial()
        self.speed_dial.setRange(1, 5)
        self.speed_dial.setSingleStep(1)
        self.speed_dial.valueChanged.connect(self.serial_speed)
        self.speed_dial.setMinimumSize(60, 60)  # never smaller than this
        self.speed_dial.setMaximumSize(120, 120)  # never bigger than this
        self.speed_dial.setStyleSheet("background-color:#F0F0F0;")

        navigation_grid.addWidget(self.speed_dial, 0, 0, 1, 1)

        self.forward_button = QPushButton("Forwards")
        self.forward_button.setStyleSheet("font-size:24px; background-color:#F0F0F0;")
        navigation_grid.addWidget(self.forward_button, 0, 1, 1, 1)

        self.forward_button.clicked.connect(self.forward_clicked)
        self.forward_button.pressed.connect(self.forward_pressed)
        self.forward_button.released.connect(self.forward_released)

        self.backward_button = QPushButton("Backwards")
        self.backward_button.setStyleSheet("font-size:24px; background-color:#F0F0F0;")
        navigation_grid.addWidget(self.backward_button, 1, 1, 1, 1)

        self.backward_button.clicked.connect(self.backward_clicked)
        self.backward_button.pressed.connect(self.backward_pressed)
        self.backward_button.released.connect(self.backward_released)

        self.speed_display = QLabel(f"{self.speed_dial.value()}")
        self.speed_display.setAlignment(Qt.AlignCenter)
        self.speed_display.setStyleSheet("font-size:16px;")
        navigation_grid.addWidget(self.speed_display, 1, 0, 1, 1)

        navigation_grid.setRowStretch(0, 1)
        navigation_grid.setRowStretch(1, 0)
        navigation_grid.setColumnStretch(0, 2)

        control_panel_vbox.addLayout(navigation_grid)

        # Row 3 - Damage Log
        # 3x2 grid
        # row 1 columns 1 - 3 title
        # row 2 button 1 button 2 button 3

        damage_grid = QGridLayout()
        
        log_damage = QLabel("Log Damage")
        log_damage.setStyleSheet("font-size:24px;")
        log_damage.setFixedHeight(60)
        log_damage.setAlignment(Qt.AlignCenter)

        damage_grid.addWidget(log_damage, 0, 0, 1, 3)

        log_crack = QPushButton("Crack")
        log_crack.setStyleSheet("font-size:24px; background-color:#F0F0F0;")
        damage_grid.addWidget(log_crack, 1, 0)

        log_partial = QPushButton("Part. Block")
        log_partial.setStyleSheet("font-size:24px; background-color:#F0F0F0;")
        damage_grid.addWidget(log_partial, 1, 1)

        log_full = QPushButton("Full Block")
        log_full.setStyleSheet("font-size:24px; background-color:#F0F0F0;")
        damage_grid.addWidget(log_full, 1, 2)

        control_panel_vbox.addLayout(damage_grid)

        # Row 4 - Take Photo and Start/Stop video

        record_grid = QHBoxLayout()

        record_photo = QPushButton("Photo")
        record_photo.setStyleSheet("font-size:24px; background-color:#F0F0F0;")
        record_grid.addWidget(record_photo)

        record_video = QPushButton("Video")
        record_video.setStyleSheet("font-size:24px; background-color:#F0F0F0;")
        record_grid.addWidget(record_video)

        control_panel_vbox.addLayout(record_grid)

        # Row 5 - Distance, GPS Pos and Orientation



        control_panel_wrapper = QWidget()
        control_panel_wrapper.setLayout(control_panel_vbox)
        control_panel_wrapper.setStyleSheet("background-color:#0F4BEB;")

        main_grid.addWidget(control_panel_wrapper, 0, 1, 2, 1, Qt.AlignCenter)

        main_grid.setColumnStretch(0, 3)  # main content
        main_grid.setColumnStretch(1, 1)  # sidebar

        central_widget.setLayout(main_grid)
        self.setCentralWidget(central_widget)


    def on_home(self):
        print("Home clicked")

    def on_camera(self):
        print("Camera clicked")
    
    def on_map(self):
        print("Map clicked")

    def updateMode(self, value):
        self.mode = value

    def set_movement(self, value: str):
           self.movement = value
           self.serial_movement()

    def serial_speed(self, value):
        speedStr = str(int(value))
        self.speed_display.setText(speedStr)

        payload = f"SPEED:{speedStr}\n".encode("ascii")
        try:
            ser.write(payload)
            print("Sent:", payload.decode("ascii"))
        except Exception as e:
            print("Serial write failed:", e)

    def serial_movement(self):
        if self.mode == 1:
            printMode = "Auto"
        else:
            printMode = "Manual"
        print(f"MODE: {printMode} MOVEMENT: {self.movement}")

        movementStr = str(self.movement)
        payload = f"MOVEMENT:{movementStr}\n".encode("ascii")

        try:
            ser.write(payload)
            print(f"Sent: {payload.decode("ascii")}")
        except Exception as e:
            print("Serial write failed:", e)

    # FORWARD
    def forward_clicked(self):
        if self.mode == 1:
            self.autoForwardState = not self.autoForwardState
            self.set_movement("Forward" if self.autoForwardState else "Stopped")

    def forward_pressed(self):
        if self.mode == 0:
            # print("Pressed")
            self.set_movement("Forward")

    def forward_released(self):
        if self.mode == 0:
            # print("Released")
            self.set_movement("Stopped")

    # BACKWARD
    def backward_clicked(self):
        if self.mode == 1:
            self.autoBackwardState = not self.autoBackwardState
            self.set_movement("Backward" if self.autoBackwardState else "Stopped")

    def backward_pressed(self):
        if self.mode == 0:
            # print("backward Pressed")
            self.set_movement("Backward")

    def backward_released(self):
        if self.mode == 0:
            # print("backward Released")
            self.set_movement("Stopped")




def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.showMaximized()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()  