import sys, os, re, cv2
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *


import serial, serial.tools.list_ports

import datetime

row_height = 100
string_f = "F0\n"
string_rv= "R0\n"
distance = 0
string_window_title = "Small Conduit Inspector"
title_row_height = 60

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BAUD = 9600
PORT = "/dev/ttyACM0" #windows COM5 for T arduino uno
# PORT = "COM5"

DEVICE = "/dev/video4"

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"Connected to {PORT}")
except serial.SerialException as e:
    ser = None
    print(f"Could not open serial port {PORT}: {e}")


class MainWindow(QMainWindow):
    def __init__(self, project_name):
        super().__init__()

        self.project_name = project_name
        self.distance = 0
        self.last_frame_bgr = None

        self.setWindowTitle(string_window_title)
        self.setGeometry(0,0,800,480) #x,y,width,height
        self.setWindowIcon(QIcon("Window_Icon.png"))
        self.main_menu(project_name)

         # --- OpenCV camera setup (V4L2) ---
        self.cap = cv2.VideoCapture(DEVICE, cv2.CAP_V4L2)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open {DEVICE}")

        # Try to negotiate a sane mode (V4L2 will pick nearest valid)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        # Timer for camera frames (~30 fps)
        self.cam_timer = QTimer(self)
        self.cam_timer.timeout.connect(self.update_frame)
        self.cam_timer.start(30)

        # Existing serial read timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial)
        self.timer.start(10)



    def main_menu(self, project_name):

        central_widget = QWidget()
        grid = QGridLayout()

        self.setCentralWidget(central_widget)    

        title = QLabel(f"{project_name}", self)
        title.setFont(QFont("Calibri", 24))
        # title.setGeometry(0,0,1000,50)
        title.setStyleSheet("color: black;"
                            "background-color: grey;"
                            "font-weight: bold;"
                            "text-decoration: underline;")
        title.setAlignment(Qt.AlignCenter)
        title.setFixedHeight(title_row_height)
        grid.addWidget(title, 0 , 0, 1, 2)

        self.home = QPushButton()
        self.home.setFixedHeight(title_row_height)
        self.home.setIcon(QIcon("home.png"))
        self.home.setIconSize(QSize(120, 120))
        self.home.clicked.connect(self.go_home)
        grid.addWidget(self.home, 0, 2, 1, 1)

        self.files = QPushButton()
        self.files.setFixedHeight(title_row_height)
        self.files.setIcon(QIcon("folder.png"))
        self.files.setIconSize(QSize(120, 120))
        self.files.clicked.connect(self.open_files)
        grid.addWidget(self.files, 0, 3, 1, 1)

        grid.setColumnStretch(0, 4)   # Title side
        grid.setColumnStretch(1, 3)
        grid.setColumnStretch(2, 2)   # Home
        grid.setColumnStretch(3, 2)   # Files

        self.video_feed = QLabel("Starting camera…", self)
        self.video_feed.setAlignment(Qt.AlignCenter)
        self.video_feed.setStyleSheet("background:#111; color:#bbb;")
        grid.addWidget(self.video_feed, 1, 0, 4, 2)

        self.forward = QPushButton("Forward", self)
        self.forward.setFixedHeight(row_height)
        self.forward.setStyleSheet("font-size:30px;")
        self.forward.pressed.connect(self.forward_press)
        self.forward.released.connect(self.forward_release)
        grid.addWidget(self.forward, 1, 2, 1, 2)

        self.backward = QPushButton("Backward", self)
        self.backward.setFixedHeight(row_height)
        self.backward.setStyleSheet("font-size:30px;")
        self.backward.pressed.connect(self.backward_press)
        self.backward.released.connect(self.backward_release)
        grid.addWidget(self.backward, 2, 2, 1, 2)

        self.record = QPushButton()
        self.record.setFixedHeight(row_height)
        self.record.setIcon(QIcon("camera.png"))
        self.record.setIconSize(QSize(120, 120))
        self.record.setStyleSheet("font-size:60px;")
        self.record.clicked.connect(self.record_position)
        grid.addWidget(self.record, 3, 2, 1, 2)

        self.distance_label = QLabel("Distance: 0", self)
        self.distance_label.setStyleSheet("font-size:20px; "
                                          "background-color: lightgrey;"
                                          "padding:10px;")
        
        grid.addWidget(self.distance_label, 4, 2, 1, 2)

        try:
            # os.mkdir(project_name)

            self.project_path = os.path.join(BASE_DIR, project_name)
            os.makedirs(self.project_path, exist_ok=True)

            self.file_path = os.path.join(project_name, f"{project_name}.txt")
            date = datetime.datetime.now().strftime("%d-%m-%Y")
            with open(self.file_path, "a") as f:
                f.write(f"Project Name: {project_name}  Date: {date}\n\n")
        except Exception as e:
            print("Error: ", e)

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

    # def record_position(self):
    #     print(f"Photo Taken, Position Recorded {self.distance}")
    #     time = datetime.datetime.now().strftime("%H-%M-%S")

    #     log_line = f"Time: {time}   Distance: {self.distance}\n"

    #     with open(self.file_path, "a") as f:
    #         f.write(log_line)

    #     image_name = os.path.join(self.project_path, f"Time:{time}_Distance:{self.distance}.jpg")
    #     self.image_capture.capture(image_name)
    #     print(f"Saved Image to {image_name}")

    def record_position(self):
        print(f"Photo Taken, Position Recorded {self.distance}")
        tstamp = datetime.datetime.now().strftime("%H-%M-%S")
        log_line = f"Time: {tstamp}   Distance: {self.distance}\n"
        try:
            with open(self.file_path, "a") as f:
                f.write(log_line)
        except Exception as e:
            print("Log write error:", e)

        if self.last_frame_bgr is not None:
            image_name = os.path.join(
                self.project_path, f"Time-{tstamp}_Distance-{self.distance}.jpg"
            )
            try:
                cv2.imwrite(image_name, self.last_frame_bgr)
                print(f"Saved Image to {image_name}")
            except Exception as e:
                print("Image save error:", e)
        else:
            print("No frame available to save.")
        
    def read_serial(self):
        if ser.in_waiting > 0:
            line = ser.readline().decode("utf-8").strip()
            if line.startswith("COUNT:"):
                self.distance = int(line.split(":")[1])
                self.distance = self.distance // 10
                self.distance_label.setText(f"Distance: {self.distance}")

    def open_files(self):
        self.file_window = FileWindow(base_path=".")
        self.file_window.show()

    def go_home(self):
        self.start_window = StartWindow()
        self.start_window.show()
        self.close()

    def update_frame(self):
        if not self.cap or not self.cap.isOpened():
            self.video_feed.setText("Camera not open")
            return
        ok, frame = self.cap.read()
        if not ok or frame is None:
            self.video_feed.setText("No frame")
            return

        # Keep last frame for saving on capture
        self.last_frame_bgr = frame

        # Convert BGR -> RGB and show
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg).scaled(
            self.video_feed.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.video_feed.setPixmap(pix)

    def closeEvent(self, e):
        try:
            if hasattr(self, "cam_timer") and self.cam_timer.isActive():
                self.cam_timer.stop()
            if hasattr(self, "timer") and self.timer.isActive():
                self.timer.stop()
            if hasattr(self, "cap") and self.cap and self.cap.isOpened():
                self.cap.release()
        except Exception:
            pass
        super().closeEvent(e)

class StartWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(string_window_title)
        self.setGeometry(0,0,800,480) #x,y,width,height
        self.setWindowIcon(QIcon("Window_Icon.png"))

        self.start_menu()

    def start_menu(self):

        layout = QGridLayout()

        title = QLabel("Small Conduit Inspector", self)
        title.setStyleSheet("color: black;"
                            "background-color: grey;"
                            "font-weight: bold;"
                            "text-decoration: underline;"
                            "font: calibri;"
                            "font-size: 30px;")
        title.setAlignment(Qt.AlignCenter)
        title.setFixedHeight(60)
        layout.addWidget(title, 0, 0, 1, 3)

        self.files = QPushButton()
        self.files.setFixedHeight(title_row_height)
        self.files.setIcon(QIcon("folder.png"))
        self.files.setIconSize(QSize(120, 120))
        self.files.clicked.connect(self.open_files)
        layout.addWidget(self.files, 0, 3, 1, 1)

        self.close = QPushButton()


        image = QLabel()
        image_pixmap = QPixmap("Window_Icon.png")
        image.setPixmap(image_pixmap)
        image.setScaledContents(True)
        image.setFixedSize(250, 250)
        layout.addWidget(image, 1, 1, 2, 2, alignment=Qt.AlignCenter)
        

        self.project_name = QLineEdit()
        self.project_name.setPlaceholderText("Enter a project name")
        self.project_name.setStyleSheet("""QLineEdit{
                                        font-size: 30px;}
                                        QLineEdit::placeholder {
                                        color: gray;
                                        font-size: 20px;   /* placeholder text size */
                                        font-style: italic;
                                        }""")

        layout.addWidget(self.project_name, 3, 1, 1, 2, alignment=Qt.AlignCenter)

        self.start_button = QPushButton("Start Project", self)
        self.start_button.clicked.connect(self.open_main_menu)
        self.start_button.setStyleSheet("font: 30px;"
                                        "font-weight: bold;"
                                        "background-color: grey;")
                                        
        self.setLayout(layout)


        layout.addWidget(self.start_button, 4, 1, 1, 2, alignment=Qt.AlignCenter)

    def open_main_menu(self):

        base_name = self.project_name.text().strip()

        if not base_name:
            QMessageBox.warning(self, "Error", "Please enter a project name")
            return
        
        project_name = base_name

        counter = 1
        while os.path.exists(project_name):
            project_name = f"{base_name}-{counter}"
            counter += 1

        self.main_menu = MainWindow(project_name)
        self.main_menu.show()
        self.close()

    def open_files(self):
        self.file_window = FileWindow(base_path=".")
        self.file_window.show()

class FileWindow(QWidget):
    def __init__(self, base_path="."):
        super().__init__()
        self.setWindowTitle(f"{string_window_title} Files")
        # self.setGeometry(200, 200, 800, 300)
        # self.setGeometry(0,0,800,480) #x,y,width,height
        self.setGeometry(160, 96, 480, 228)
        self.setWindowIcon(QIcon("Window_Icon.png"))

        self.base_path = base_path
        self.current_path = None

        self.file_menu()

    def file_menu(self):

        layout = QGridLayout()

        folder_lable = QLabel(f"Projects List")
        folder_lable.setStyleSheet("font: 16px;"
                                   "background-color: grey;"
                                   "font-weight: bold;")
        folder_lable.setAlignment(Qt.AlignCenter)
        folder_lable.setFixedHeight(40)
        layout.addWidget(folder_lable, 0, 0, 1, 2)

        self.folder_list = QListWidget()
        if os.path.exists(self.base_path):
            folders = [f for f in os.listdir(self.base_path) if os.path.isdir(os.path.join(self.base_path, f))]
            for folder in folders:
                self.folder_list.addItem(folder)
        self.folder_list.setStyleSheet("""QListWidget{
                                        font-size: 14px;}
                                        """)
        layout.addWidget(self.folder_list, 1, 0, 3, 1)
        
        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""QListWidget{
                                        font-size: 14px;}
                                        """)
        layout.addWidget(self.file_list, 1, 1, 3, 1)

        self.preview_label = QLabel("Open a file to view")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: grey; color: black;")
        self.preview_label.setWordWrap(True)
        layout.addWidget(self.preview_label, 0, 2, 4, 1)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 3)

        self.folder_list.itemClicked.connect(self.load_files)

        self.file_list.itemDoubleClicked.connect(self.show_preview)

        self.setLayout(layout)

    def load_files(self, item):
        self.current_folder = os.path.join(self.base_path, item.text())
        self.file_list.clear()
        if os.path.exists(self.current_folder):
            files = os.listdir(self.current_folder)
            for f in files:
                self.file_list.addItem(f)
        self.preview_label.setText("Select a file to preview")
        self.preview_label.setPixmap(QPixmap())

    def show_preview(self, item):

        if self.current_folder is None:
            return

        file_path = os.path.join(self.current_folder, item.text())

        if os.path.isfile(file_path):
            if item.text().lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                pixmap = QPixmap(file_path)
                self.preview_label.setPixmap(pixmap.scaled(
                    self.preview_label.width(), 
                    self.preview_label.height(), 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                ))
                self.preview_label.setText("")
            # For text files
            elif item.text().lower().endswith(".txt"):
                with open(file_path, "r") as f:
                    text = f.read()
                self.preview_label.setPixmap(QPixmap())  # clear any previous image
                self.preview_label.setText(text)
            else:
                self.preview_label.setText(f"Cannot preview {item.text()}")
                self.preview_label.setPixmap(QPixmap())


def main():
    app = QApplication(sys.argv)
    window = StartWindow()

    window.show()
    sys.exit(app.exec_()) #exec_ is to execute


if __name__ == "__main__":
    main()