import sys, os, re, cv2
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

from functools import partial

import serial, serial.tools.list_ports
import datetime

from config import windowTitle, BASE_DIR

BAUD = 9600
# PORT = "COM5" #WINDOWS
PORT = "/dev/ttyUSB0"
DEVICE = "/dev/video0" #correct T Linux 


try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"Connected to port {PORT}")
except serial.SerialException as e:
    ser = None
    print(f"Could not connect to port {PORT}: {e}")

class MainWindow(QMainWindow):

    openMapRequest = pyqtSignal(float, float, str)
    openFilesRequested = pyqtSignal()
    goHomeRequested = pyqtSignal()

    def __init__(self, projectName: str, endoscopeLength: str):
        super().__init__()
        self.setWindowTitle(windowTitle)
        self.setWindowIcon(QIcon("icons/Window_Icon.png"))
        

        self.mode = 0
        self.autoForwardState = False
        self.autoBackwardState = False
        self.movement= "Stopped"

        self.GPSLat = 0.0
        self.GPSLong = 0.0

        self.distance = 0.0

        self.pName = projectName
        self.eLength = endoscopeLength
        
        self.serialTimer = QTimer()
        self.serialTimer.timeout.connect(self.read_serial)
        self.serialTimer.start(10)

                # --- OpenCV camera setup ---
        self.cap = cv2.VideoCapture(DEVICE, cv2.CAP_V4L2)
        if not self.cap.isOpened():
            print(f"Could not open camera at {DEVICE}")
            self.cap = None
        else:
            # Try to negotiate a sane mode (V4L2 will pick nearest valid)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)

        self.last_frame_bgr = None

        # Timer for camera frames (~30 fps)
        self.camTimer = QTimer(self)
        self.camTimer.timeout.connect(self.update_frame)
        self.camTimer.start(30)

        self.is_recording = False
        self.video_writer = None
        self.video_path = None



        self.tool_bar()
        self.main_menu()

        self.serial_max_distance()
        self.create_project_file()

        self.mapWindow = None

    def tool_bar(self):

        # Create Toolbar
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(50, 50))
        self.addToolBar(toolbar)

        spacer1 = QWidget()
        spacer1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer1)

        self.title = QLabel(f"{self.pName}")

        self.title.setStyleSheet("font-size: 30px;"
                                 "font-weight: bold;")

        toolbar.addWidget(self.title)

        spacer2 = QWidget()
        spacer2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer2)

        # Home Buton - Toolbar
        actionHome = QAction(QIcon("icons/home.png"), "Home", self)
        actionHome.triggered.connect(self.on_home)
        toolbar.addAction(actionHome)
        

        # Map Button - Toolbar
        action_map = QAction(QIcon("icons/map.png"), "Map", self)
        action_map.triggered.connect(lambda: self.openMapRequest.emit(float(self.GPSLat), float(self.GPSLong), str(self.pName)))
        toolbar.addAction(action_map)

        # File Button - Toolbar
        action_camera = QAction(QIcon("icons/folder.png"), "Folder", self)
        action_camera.triggered.connect(self.on_folder)
        toolbar.addAction(action_camera)

        self.mapWindow = None

    def main_menu(self):

        central_widget = QWidget()
        mainGrid = QGridLayout()

        # Column 1-3 Row 1 - 4
        self.videofeed = QLabel("Starting camera…")
        self.videofeed.setAlignment(Qt.AlignCenter)
        self.videofeed.setStyleSheet("background:#111; color:#bbb;")
        mainGrid.addWidget(self.videofeed, 0, 0, 1, 1)


        mainGrid.addWidget(self.videofeed, 0, 0, 1, 1)

        # Row 1 Column 0 Progress Bar

        progressVboxLayout = QVBoxLayout()
        # progressVboxLayout.setAlignment(Qt.AlignTop)

        progressVboxLayout.setSpacing(30)
        progressVboxLayout.setContentsMargins(10, 10, 10, 10)

        progressLabel = QLabel("Endoscope Progress")
        progressLabel.setStyleSheet("font-size:18px; font-weight:bold;")
        progressVboxLayout.addWidget(progressLabel, alignment=Qt.AlignCenter)

        self.progressBar = QProgressBar()
        self.progressBar.setMinimum(0)

        # eLength is in metres — convert to mm
        try:
            max_length_mm = float(self.eLength) * 1000.0
        except ValueError:
            max_length_mm = 1000.0  # fallback

        self.progressBar.setMaximum(int(max_length_mm))
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(True)
        self.progressBar.setFormat("0.00 / %.2f m" % float(self.eLength))

        self.progressBar.setStyleSheet("""
                                       QProgressBar {
                                       border: 2px solid grey;
                                       border-radius: 5px;
                                       text-align: center;
                                       font-weight: bold;
                                       }
                                       QProgressBar::chunk {
                                       background-color: #0F4BEB;
                                       width: 10px;
                                       }
                                       """) 
        
        progressVboxLayout.addWidget(self.progressBar)
        
        mainGrid.addLayout(progressVboxLayout, 1, 0, alignment=Qt.AlignTop)

        # Control Panel -> add everthing to this then add to the mainGrid
        controlPanelVBox = QVBoxLayout()

        controlPanelVBox.setSpacing(30)
        controlPanelVBox.setContentsMargins(10, 10, 10, 10)
           

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

        controlPanelVBox.addLayout(slider_hbox)

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

        controlPanelVBox.addLayout(navigation_grid)

        # Row 3 - Damage Log
        # 3x2 grid
        # row 1 columns 1 - 3 title
        # row 2 button 1 button 2 button 3

        damageGrid = QGridLayout()
        
        logDamage = QLabel("Log Damage")
        logDamage.setStyleSheet("font-size:24px;")
        logDamage.setFixedHeight(60)
        logDamage.setAlignment(Qt.AlignCenter)

        damageGrid.addWidget(logDamage, 0, 0, 1, 3)

        logCrack = QPushButton("Crack")
        logCrack.setStyleSheet("font-size:24px; background-color:#F0F0F0;")
        logCrack.clicked.connect(lambda: self.capture_damage("Crack"))
        damageGrid.addWidget(logCrack, 1, 0)

        logPartial = QPushButton("Part. Block")
        logPartial.setStyleSheet("font-size:24px; background-color:#F0F0F0;")
        logPartial.clicked.connect(lambda: self.capture_damage("Partial Block"))
        damageGrid.addWidget(logPartial, 1, 1)

        logFull = QPushButton("Full Block")
        logFull.setStyleSheet("font-size:24px; background-color:#F0F0F0;")
        logFull.clicked.connect(lambda: self.capture_damage("Full Block"))
        damageGrid.addWidget(logFull, 1, 2)


        # logCrack = QPushButton("Crack")
        # logCrack.setStyleSheet("font-size:24px; background-color:#F0F0F0;")
        # damageGrid.addWidget(logCrack, 1, 0)

        # logPartial = QPushButton("Part. Block")
        # logPartial.setStyleSheet("font-size:24px; background-color:#F0F0F0;")
        # damageGrid.addWidget(logPartial, 1, 1)

        # logFull = QPushButton("Full Block")
        # logFull.setStyleSheet("font-size:24px; background-color:#F0F0F0;")
        # damageGrid.addWidget(logFull, 1, 2)

        controlPanelVBox.addLayout(damageGrid)

        # Row 4 - Take Photo and Start/Stop video

        # Row 4 - Take Photo and Start/Stop video
        recordHBox = QHBoxLayout()

        self.photoButton = QPushButton("Photo")
        self.photoButton.setStyleSheet("font-size:24px; background-color:#F0F0F0;")
        self.photoButton.clicked.connect(self.capture_photo)   # <-- connect
        recordHBox.addWidget(self.photoButton)

        self.videoButton = QPushButton("Video")
        self.videoButton.setStyleSheet("font-size:24px; background-color:#F0F0F0;")
        self.videoButton.setCheckable(True)                    # toggle-style button
        self.videoButton.clicked.connect(self.toggle_video)    # <-- connect
        recordHBox.addWidget(self.videoButton)

        controlPanelVBox.addLayout(recordHBox)


        # Row 5 - Distance, GPS Pos

        imuGrid = QGridLayout()

        distanceLabel = QLabel("Distance: (mm)")
        # distanceLabel.setSt
        imuGrid.addWidget(distanceLabel, 0, 0)

        self.distanceValue = QLabel(f"{self.distance}", self)
        imuGrid.addWidget(self.distanceValue, 1, 0)

        gpsLatName = QLabel("GPS Lat:")
        imuGrid.addWidget(gpsLatName, 0, 1)

        self.gpsLatValue = QLabel(f"{self.GPSLat}", self)
        imuGrid.addWidget(self.gpsLatValue, 1, 1)

        gpsLongName = QLabel("GPS Long:")
        imuGrid.addWidget(gpsLongName, 0, 2)

        self.gpsLongValue = QLabel(f"{self.GPSLong}", self)
        imuGrid.addWidget(self.gpsLongValue, 1, 2)

        controlPanelVBox.addLayout(imuGrid)


        control_panel_wrapper = QWidget()
        control_panel_wrapper.setLayout(controlPanelVBox)
        control_panel_wrapper.setStyleSheet("background-color:#0F4BEB;")

        mainGrid.addWidget(control_panel_wrapper, 0, 1, 2, 1, Qt.AlignTop)

        mainGrid.setColumnStretch(0, 3)  # main content
        mainGrid.setColumnStretch(1, 1)  # sidebar

        central_widget.setLayout(mainGrid)
        self.setCentralWidget(central_widget)


    def on_home(self):
        print("Home clicked")
        self.goHomeRequested.emit()

    def on_folder(self):
        # print("Folder clicked")
        self.openFilesRequested.emit()

    def updateMode(self, value):
        self.mode = value

    def set_movement(self, value: str):
           self.movement = value
           self.serial_movement()

    def serial_max_distance(self):
        distanceStr = str(self.eLength)
        payload = f"LENGTH:{distanceStr}\n".encode("ascii")

        try:
            ser.write(payload)
            print(f"Sent: ", payload.decode("ascii"))
        except Exception as e:
            print("Serial write failed:", e)

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
            print(f"Sent: {payload.decode('ascii')}")
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

    def update_progress_bar(self, distance_value: float):
        try:
            distance_mm = float(distance_value)
            max_mm = float(self.eLength) * 1000.0
        except ValueError:
            return

        distance_mm = max(0, min(distance_mm, max_mm))
        ratio = distance_mm / max_mm if max_mm > 0 else 0

        # Change color dynamically
        if ratio >= 0.9:
            color = "#FF3B3B"   # red warning
        elif ratio >= 0.75:
            color = "#FFA500"   # orange warning
        else:
            color = "#0F4BEB"   # normal blue

        self.progressBar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                width: 10px;
            }}
        """)

        self.progressBar.setValue(int(distance_mm))
        self.progressBar.setFormat(f"{distance_mm/1000:.2f} / {float(self.eLength):.2f} m")



    def read_serial(self):

        if ser.in_waiting > 0:
            line = ser.readline().decode("ascii").strip()
            if line.startswith("GPSLAT:"):
                self.GPSLat = str(line.split(":")[1])
                self.gpsLatValue.setText(f"{self.GPSLat}")
                # self.fixTimer.start()
                # print(self.GPSLat)
            elif line.startswith("GPSLONG:"):
                self.GPSLong = str(line.split(":")[1])
                self.gpsLongValue.setText(f"{self.GPSLong}")
                # print(self.GPSLong)
                # self.fixTimer.start()
            elif line.startswith("DISTANCE:"):
                self.distance = int(line.split(":")[1])
                self.distanceValue.setText(f"{self.distance}")
                self.update_progress_bar(self.distance)
            
    def create_project_file(self):
        try:
            projectsDir = os.path.join(BASE_DIR, "Projects")
            os.makedirs(projectsDir, exist_ok=True)
    
            self.projectPath = os.path.join(projectsDir, self.pName)
            os.makedirs(self.projectPath, exist_ok=True)
    
            self.filePath = os.path.join(self.projectPath, f"{self.pName}.txt")
    
            now = datetime.datetime.now()
            date = now.strftime("%d-%m-%Y")
            time = now.strftime("%H:%M")
    
            with open(self.filePath, "a", encoding="utf-8") as f:
                f.write(
                    f"Project Name: {self.pName}\n"
                    f"Date: {date}\n"
                    f"Start Time: {time}\n"
                    # f"Location: {self.GPSLat}, {self.GPSLong}\n\n"
                )
        except Exception as e:
            print("Error:", e)

    def update_frame(self):
        """Grab frames from OpenCV and paint into the QLabel."""
        if not self.cap or not self.cap.isOpened():
            # Show a friendly message once; don’t spam.
            if self.videofeed.text() != "Camera not open":
                self.videofeed.setText("Camera not open")
            return

        ok, frame = self.cap.read()
        if not ok or frame is None:
            if self.videofeed.text() != "No frame":
                self.videofeed.setText("No frame")
            return

        # Save last frame for snapshots
        self.last_frame_bgr = frame

        if self.is_recording and self.video_writer is not None:
            self.video_writer.write(self.last_frame_bgr)

        # Convert BGR -> RGB and show
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)

        # Scale to current label size, keep aspect ratio
        pix = QPixmap.fromImage(qimg).scaled(
            self.videofeed.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.videofeed.setPixmap(pix)

    def capture_damage(self, damage_type: str):
        """
        Save a photo + append a log entry with:
        - timestamp
        - damage type
        - distance (mm)
        - GPS (Lat, Long)
        Files saved into the project folder created by create_project_file().
        """
        tstamp = datetime.datetime.now().strftime("%H-%M-%S")
        # Make a safe filename segment for GPS (remove commas/spaces)
        lat = str(self.GPSLat).replace(",", "_").replace(" ", "")
        lon = str(self.GPSLong).replace(",", "_").replace(" ", "")

        # Build image filename
        image_name = os.path.join(
            self.projectPath,
            f"Time-{tstamp}_Distance-{self.distance}_GPS-{lat}_{lon}_Damage-{damage_type}.jpg"
        )

        # Write log line
        log_line = (
            f"Time: {tstamp}   Damage: {damage_type}   "
            f"Distance(mm): {self.distance}   "
            f"GPS: {self.GPSLat},{self.GPSLong}\n"
        )
        try:
            with open(self.filePath, "a", encoding="utf-8") as f:
                f.write(log_line)
        except Exception as e:
            print("Log write error:", e)

        # Save the latest frame
        if self.last_frame_bgr is None:
            print("No frame available to save.")
            return
        try:
            ok = cv2.imwrite(image_name, self.last_frame_bgr)
            if ok:
                print(f"Saved Image to {image_name}")
            else:
                print("cv2.imwrite() failed")
        except Exception as e:
            print("Image save error:", e)

    def capture_photo(self):
        if self.last_frame_bgr is None:
            print("No frame available to save.")
            return
        try:
            tstamp = datetime.datetime.now().strftime("%H-%M-%S")
            image_name = os.path.join(self.projectPath, f"Photo-{tstamp}_Dist-{self.distance}.jpg")
            ok = cv2.imwrite(image_name, self.last_frame_bgr)
            if ok:
                print(f"Saved photo: {image_name}")
                # Optional: append to log
                with open(self.filePath, "a", encoding="utf-8") as f:
                    f.write(f"Photo: {tstamp}  Distance(mm): {self.distance}  GPS: {self.GPSLat},{self.GPSLong}\n")
            else:
                print("cv2.imwrite() failed for photo")
        except Exception as e:
            print("Photo save error:", e)

    def toggle_video(self, checked: bool):
        if checked and not self.is_recording:
            # ---- Start recording ----
            if not self.cap or not self.cap.isOpened():
                print("Camera not open; cannot start recording.")
                self.videoButton.setChecked(False)
                return

            # Determine FPS and frame size
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            if not fps or fps <= 1:
                fps = 30.0  # fallback

            width  = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)  or 640)
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)

            # Choose container + codec; .mp4 with mp4v is widely OK on Linux
            tstamp = datetime.datetime.now().strftime("%H-%M-%S")
            self.video_path = os.path.join(self.projectPath, f"Video-{tstamp}.avi")
            fourcc = cv2.VideoWriter_fourcc(*'X','V','I','D')

            try:
                self.video_writer = cv2.VideoWriter(self.video_path, fourcc, fps, (width, height))
                if not self.video_writer.isOpened():
                    print("Failed to open VideoWriter")
                    self.video_writer = None
                    self.videoButton.setChecked(False)
                    return
                self.is_recording = True
                self.videoButton.setText("Stop Video")
                print(f"Recording started: {self.video_path} @ {fps} fps, {width}x{height}")

                # Optional: write to session log
                with open(self.filePath, "a", encoding="utf-8") as f:
                    f.write(f"Video START: {tstamp}  FPS:{fps:.1f}  Size:{width}x{height}  Dist(mm):{self.distance}\n")

            except Exception as e:
                print("Error starting video:", e)
                self.video_writer = None
                self.videoButton.setChecked(False)

        else:
            # ---- Stop recording ----
            if self.is_recording and self.video_writer is not None:
                try:
                    self.video_writer.release()
                except Exception:
                    pass
            self.video_writer = None
            self.is_recording = False
            self.videoButton.setText("Video")
            self.videoButton.setChecked(False)
            print(f"Recording stopped: {self.video_path or ''}")

            # Optional: log end
            tstamp = datetime.datetime.now().strftime("%H-%M-%S")
            try:
                with open(self.filePath, "a", encoding="utf-8") as f:
                    f.write(f"Video STOP: {tstamp}  Dist(mm):{self.distance}\n")
            except Exception:
                pass



    def closeEvent(self, e):
        try:
            if hasattr(self, "camTimer") and self.camTimer.isActive():
                self.camTimer.stop()
            if hasattr(self, "serialTimer") and self.serialTimer.isActive():
                self.serialTimer.stop()
            if hasattr(self, "cap") and self.cap and self.cap.isOpened():
                self.cap.release()
            if getattr(self, "video_writer", None) is not None:
                try:
                    self.video_writer.release()
                except Exception:
                    pass
        except Exception:
            pass
        super().closeEvent(e)

