import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer

import serial, serial.tools.list_ports

import datetime

row_height = 100
string_f = "F0\n"
string_rv= "R0\n"
distance = 0

BAUD = 9600
PORT = "/dev/ttyACM0" #windows COM5 for T arduino uno

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"✅ Connected to {PORT}")
except serial.SerialException as e:
    ser = None
    print(f"⚠️ Could not open serial port {PORT}: {e}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Small Conduit Inspector")
        self.setGeometry(100,100,1000,550) #x,y,width,height
        self.setWindowIcon(QIcon("Window_Icon.png"))
        self.initUI()

        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial)
        self.timer.start(10)



    def initUI(self):

        central_widget = QWidget()
        self.setCentralWidget(central_widget)    

        title = QLabel("Small Diameter Conduit UI", self)
        title.setFont(QFont("Calibri", 24))
        # title.setGeometry(0,0,1000,50)
        title.setStyleSheet("color: black;"
                            "background-color: grey;"
                            "font-weight: bold;"
                            "text-decoration: underline;")
        title.setAlignment(Qt.AlignCenter)
        title.setFixedHeight(60)

        image = QLabel(self)
        # image.setGeometry(0, 75, 750, 450) #use // for interger division
        image_pixmap = QPixmap("Video_Feed.png")
        image.setPixmap(image_pixmap)
        image.setScaledContents(True)
        image.setFixedSize(750, 450)

        self.forward = QPushButton("Forward", self)
        self.forward.setFixedHeight(row_height)
        self.forward.setStyleSheet("font-size:30px;")
        self.forward.pressed.connect(self.forward_press)
        self.forward.released.connect(self.forward_release)

        self.backward = QPushButton("Backward", self)
        self.backward.setFixedHeight(row_height)
        self.backward.setStyleSheet("font-size:30px;")
        self.backward.pressed.connect(self.backward_press)
        self.backward.released.connect(self.backward_release)

        self.record = QPushButton("Record Position")
        self.record.setFixedHeight(row_height)
        self.record.setStyleSheet("font-size:30px;")
        self.record.clicked.connect(self.record_position)

        self.distance_label = QLabel("Distance: 0", self)
        self.distance_label.setStyleSheet("font-size:16px; background-color: lightgrey; padding:10px;")


        grid = QGridLayout()
        grid.addWidget(title, 0 , 0, 1, 4)
        grid.addWidget(image, 1, 0, 4, 2)

        grid.addWidget(self.forward, 1, 2, 1, 2)
        grid.addWidget(self.backward, 2, 2, 1, 2)
        grid.addWidget(self.record, 3, 2, 1, 2)
        grid.addWidget(self.distance_label, 4, 2, 1, 2)

        grid.setRowMinimumHeight(1, 100)
        central_widget.setLayout(grid)

    def forward_press(self):
        string_f = "F1\n"
        ser.write(string_f.encode())
        print("Sent: ", string_f.strip())

    def forward_release(self):
        string_f = "F0\n"
        ser.write(string_f.encode())
        print("Sent: ", string_f.strip())

    def backward_press(self):
        string_r = "R1\n"
        ser.write(string_r.encode())
        print("Sent: ", string_r.strip())

    def backward_release(self):
        string_r = "R0\n"
        ser.write(string_r.encode())
        print("Sent: ", string_r.strip())

    def record_position(self):
        print(f"Photo Taken, Position Recorded {self.distance}")
        now = datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S")

        log_line = f"{now}, Distance: {self.distance}\n"

        with open("position.txt", "a") as f:
            f.write(log_line)
        
    def read_serial(self):
        if ser.in_waiting > 0:
            line = ser.readline().decode("utf-8").strip()
            if line.startswith("COUNT:"):
                self.distance = int(line.split(":")[1])
                self.distance = self.distance // 10
                self.distance_label.setText(f"Distance: {self.distance}")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()

    window.show()
    sys.exit(app.exec_()) #exec_ is to execute


if __name__ == "__main__":
    main()