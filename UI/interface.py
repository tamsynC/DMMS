import sys, os, cv2, datetime, re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QLineEdit,
    QGridLayout, QListWidget, QMessageBox, QStackedWidget, QVBoxLayout
)
from PyQt5.QtGui import QIcon, QPixmap, QImage, QFont
from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal, QObject, QThread, pyqtSlot
import serial, serial.tools.list_ports

# ============================
# Config / Globals
# ============================
row_height = 100
string_window_title = "Small Conduit Inspector"
title_row_height = 60

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BAUD = 9600
PORT = "/dev/ttyACM0"   # On Windows e.g. "COM5"
DEVICE = "/dev/video0"   # V4L2 device

# ============================
# Camera worker (runs in its own thread)
# ============================
class CameraWorker(QObject):
    frameReady = pyqtSignal(QImage, object)   # (qimage, bgr_frame)
    error = pyqtSignal(str)

    def __init__(self, device):
        super().__init__()
        self.device = device
        self._running = False
        self.cap = None

    def start(self):
        self._running = True
        try:
            self.cap = cv2.VideoCapture(self.device, cv2.CAP_V4L2)
            if not self.cap.isOpened():
                self.error.emit(f"Could not open {self.device}")
                return
            # Try a reasonable mode
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 450)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
        except Exception as e:
            self.error.emit(str(e))
            return

        # Tight loop: grab latest frame, drop if UI is busy. Sleep a tad to yield.
        while self._running:
            ok, frame = self.cap.read()
            if not ok or frame is None:
                # Avoid spamming; emit once then short sleep
                self.error.emit("No frame from camera")
                QThread.msleep(50)
                continue
            # Convert to QImage in worker thread to lighten UI thread
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888).copy()
            self.frameReady.emit(qimg, frame)
            QThread.msleep(15)  # ~66 fps cap; UI will render at its own speed

    def stop(self):
        self._running = False
        try:
            if self.cap is not None and self.cap.isOpened():
                self.cap.release()
        except Exception:
            pass

# ============================
# Start Page (stack page)
# ============================
class StartPage(QWidget):
    def __init__(self, appwin):
        super().__init__()
        self.appwin = appwin
        self._build()

    def _build(self):
        layout = QGridLayout()

        title = QLabel("Small Conduit Inspector", self)
        title.setStyleSheet(
            "color: black; background-color: grey; font-weight: bold; text-decoration: underline; font-size: 30px;"
        )
        title.setAlignment(Qt.AlignCenter)
        title.setFixedHeight(60)
        layout.addWidget(title, 0, 0, 1, 3)

        files_btn = QPushButton()
        files_btn.setFixedHeight(title_row_height)
        files_btn.setIcon(QIcon("folder.png"))
        files_btn.setIconSize(QSize(120, 120))
        files_btn.clicked.connect(lambda: self.appwin.show_files(back_to="start"))
        layout.addWidget(files_btn, 0, 3, 1, 1)

        image = QLabel()
        pix = QPixmap("Window_Icon.png")
        image.setPixmap(pix)
        image.setScaledContents(True)
        image.setFixedSize(250, 250)
        layout.addWidget(image, 1, 1, 2, 2, alignment=Qt.AlignCenter)

        self.project_name = QLineEdit()
        self.project_name.setPlaceholderText("Enter a project name")
        self.project_name.setStyleSheet(
            "QLineEdit{font-size: 30px;} QLineEdit::placeholder{color: gray; font-size: 20px; font-style: italic;}"
        )
        layout.addWidget(self.project_name, 3, 1, 1, 2, alignment=Qt.AlignCenter)

        start_button = QPushButton("Start Project", self)
        start_button.clicked.connect(self._start_project)
        start_button.setStyleSheet("font: 30px; font-weight: bold; background-color: grey;")
        layout.addWidget(start_button, 4, 1, 1, 2, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def _start_project(self):
        base = self.project_name.text().strip()
        if not base:
            QMessageBox.warning(self, "Error", "Please enter a project name")
            return
        # unique folder name
        project_name = base
        counter = 1
        while os.path.exists(os.path.join(BASE_DIR, project_name)):
            project_name = f"{base}-{counter}"
            counter += 1
        self.appwin.start_project(project_name)


class FilesPage(QWidget):
    def __init__(self, appwin, base_path="."):
        super().__init__()
        self.appwin = appwin
        self.base_path = base_path
        self.current_folder = None
        self._build()

    def _build(self):
        layout = QGridLayout()

        header = QLabel("Projects List")
        header.setStyleSheet("font: 16px; background-color: grey; font-weight: bold;")
        header.setAlignment(Qt.AlignCenter)
        header.setFixedHeight(40)
        layout.addWidget(header, 0, 0, 1, 3)

        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(self._go_back)
        layout.addWidget(self.back_btn, 0, 3, 1, 1)

        self.folder_list = QListWidget()
        self.folder_list.setStyleSheet("QListWidget{font-size: 14px;}")
        layout.addWidget(self.folder_list, 1, 0, 3, 1)

        self.file_list = QListWidget()
        self.file_list.setStyleSheet("QListWidget{font-size: 14px;}")
        layout.addWidget(self.file_list, 1, 1, 3, 1)

        # --- Preview section ---
        preview_layout = QVBoxLayout()

        self.preview_label = QLabel("Open a file to view")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: lightgray; color: black;")
        self.preview_label.setWordWrap(True)
        preview_layout.addWidget(self.preview_label, stretch=5)

        # NEW: filename label below image/text
        self.filename_label = QLabel("")
        self.filename_label.setAlignment(Qt.AlignCenter)
        self.filename_label.setStyleSheet("font: 14px; color: gray; padding: 4px;")
        preview_layout.addWidget(self.filename_label, stretch=1)

        layout.addLayout(preview_layout, 1, 2, 3, 2)
        # --- End preview section ---

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 2)
        layout.setColumnStretch(3, 0)
        self.setLayout(layout)

        self._refresh_folders()
        self.folder_list.itemClicked.connect(self._load_files)
        self.file_list.itemDoubleClicked.connect(self._show_preview)

    def _refresh_folders(self):
        self.folder_list.clear()
        if os.path.exists(self.base_path):
            for f in sorted(os.listdir(self.base_path)):
                p = os.path.join(self.base_path, f)
                if os.path.isdir(p):
                    self.folder_list.addItem(f)

    def _load_files(self, item):
        self.current_folder = os.path.join(self.base_path, item.text())
        self.file_list.clear()
        self.preview_label.setText("Select a file to preview")
        self.preview_label.setPixmap(QPixmap())
        self.filename_label.setText("")  # Clear file name
        if os.path.exists(self.current_folder):
            for f in sorted(os.listdir(self.current_folder)):
                self.file_list.addItem(f)

    # def _show_preview(self, item):
    #     if not self.current_folder:
    #         return
    #     file_path = os.path.join(self.current_folder, item.text())
    #     if not os.path.isfile(file_path):
    #         return

    #     name = item.text()
    #     lower = name.lower()
    #     self.filename_label.setText(name)  # ✅ Update filename label

    #     if lower.endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
    #         pixmap = QPixmap(file_path)
    #         self.preview_label.setPixmap(pixmap.scaled(
    #             self.preview_label.width(),
    #             self.preview_label.height(),
    #             Qt.KeepAspectRatio,
    #             Qt.SmoothTransformation,
    #         ))
    #         self.preview_label.setText("")
    #     elif lower.endswith(".txt"):
    #         with open(file_path, "r") as f:
    #             text = f.read()
    #         self.preview_label.setPixmap(QPixmap())
    #         self.preview_label.setText(text)
    #     else:
    #         self.preview_label.setText(f"Cannot preview {item.text()}")
    #         self.preview_label.setPixmap(QPixmap())

    def _show_preview(self, item):
        if not self.current_folder:
            return
        file_path = os.path.join(self.current_folder, item.text())
        if not os.path.isfile(file_path):
            return

        filename = item.text()
        lower = filename.lower()

        # Show filename (title line)
        name_no_ext = os.path.splitext(filename)[0]
        self.filename_label.setText(name_no_ext)

        # Preview content
        if lower.endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
            pixmap = QPixmap(file_path)
            self.preview_label.setPixmap(pixmap.scaled(
                self.preview_label.width(),
                self.preview_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            ))
            self.preview_label.setText("")
        elif lower.endswith(".txt"):
            with open(file_path, "r") as f:
                text = f.read()
            self.preview_label.setPixmap(QPixmap())
            self.preview_label.setText(text)
        else:
            self.preview_label.setText(f"Cannot preview {filename}")
            self.preview_label.setPixmap(QPixmap())

        # --- Only Distance & GPS ---
        self.filename_label.setText(self._format_distance_gps(filename))

    # NEW: helper to parse your filename pattern and format just Distance & GPS
    def _format_distance_gps(self, filename: str) -> str:
        """
        Supports names like:
        Time-00-17-55_Distance-10_GPS--33.743137,150.995651.jpg
        """
        # allow integer or decimal distance; robust negative GPS with a literal '-' after 'GPS-'
        m = re.search(r"_Distance-(\d+(?:\.\d+)?)_GPS-(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)",filename)
        if not m:
            return ""  # no metadata found; show nothing
        dist, lat, lon = m.groups()
        return f"Distance: {dist} m    GPS: {lat}, {lon}"

    def _go_back(self):
        self.appwin.pop_to_previous()



# ============================
# Serial worker (pyserial in its own thread)
# ============================
class SerialWorker(QObject):
    lineReceived = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, port: str, baud: int):
        super().__init__()
        self.port_name = port
        self.baud = baud
        self._running = False
        self.ser = None

    @pyqtSlot()
    def start(self):
        self._running = True
        try:
            self.ser = serial.Serial(self.port_name, self.baud, timeout=0.1)
        except Exception as e:
            self.error.emit(f"Serial open error: {e}")
            return
        # Non-blocking read loop
        buf = bytearray()
        while self._running:
            try:
                data = self.ser.read(256)
                if data:
                    buf.extend(data)
                    while b"\n" in buf:
                        line, _, rest = buf.partition(b"\n")
                        buf = bytearray(rest)
                        try:
                            s = line.decode("utf-8", errors="ignore").strip()
                            if s:
                                self.lineReceived.emit(s)
                        except Exception:
                            pass
                else:
                    QThread.msleep(5)
            except Exception as e:
                self.error.emit(f"Serial read error: {e}")
                QThread.msleep(50)

    @pyqtSlot()
    def stop(self):
        self._running = False
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
        except Exception:
            pass

    @pyqtSlot(str)
    def write_text(self, text: str):
        try:
            if self.ser and self.ser.is_open:
                self.ser.write(text.encode("utf-8"))
        except Exception as e:
            self.error.emit(f"Serial write error: {e}")

# ============================
# Main Page (stack page) with threaded camera + threaded serial
# ============================
class MainPage(QWidget):
    def __init__(self, appwin, project_name: str):
        super().__init__()
        self.appwin = appwin
        self.project_name = project_name
        self.distance = 0
        self.last_frame_bgr = None

        self.gps_lat = 0
        self.gps_long = 0

        # paths
        self.project_path = os.path.join(BASE_DIR, self.project_name)
        os.makedirs(self.project_path, exist_ok=True)
        self.file_path = os.path.join(self.project_path, f"{self.project_name}.txt")

        self._build()
        self._init_log_header()

        # Camera thread
        self.cam_thread = QThread(self)
        self.cam_worker = CameraWorker(DEVICE)
        self.cam_worker.moveToThread(self.cam_thread)
        self.cam_thread.started.connect(self.cam_worker.start)
        self.cam_worker.frameReady.connect(self._on_new_frame)
        self.cam_worker.error.connect(self._on_camera_error)
        self.cam_thread.start()

        # Serial thread (pyserial)
        self.ser_thread = QThread(self)
        self.ser_worker = SerialWorker(PORT, BAUD)
        self.ser_worker.moveToThread(self.ser_thread)
        self.ser_thread.started.connect(self.ser_worker.start)
        self.ser_worker.lineReceived.connect(self._on_serial_line)
        self.ser_worker.error.connect(self._on_serial_error)
        self.ser_thread.start()

    # ---------- UI ----------
    def _build(self):
        grid = QGridLayout()

        title = QLabel(self.project_name, self)
        title.setFont(QFont("Calibri", 24))
        title.setStyleSheet("color:black; background-color:grey; font-weight:bold; text-decoration:underline;")
        title.setAlignment(Qt.AlignCenter)
        title.setFixedHeight(title_row_height)
        grid.addWidget(title, 0, 0, 1, 2)

        home = QPushButton()
        home.setFixedHeight(title_row_height)
        home.setIcon(QIcon("home.png"))
        home.setIconSize(QSize(120, 120))
        home.clicked.connect(self._go_home)
        grid.addWidget(home, 0, 2, 1, 1)

        files = QPushButton()
        files.setFixedHeight(title_row_height)
        files.setIcon(QIcon("folder.png"))
        files.setIconSize(QSize(120, 120))
        files.clicked.connect(lambda: self.appwin.show_files(back_to="main"))
        grid.addWidget(files, 0, 3, 1, 1)

        grid.setColumnStretch(0, 4)
        grid.setColumnStretch(1, 3)
        grid.setColumnStretch(2, 2)
        grid.setColumnStretch(3, 2)

        self.video_feed = QLabel("Starting camera…", self)
        self.video_feed.setAlignment(Qt.AlignCenter)
        self.video_feed.setStyleSheet("background:#111; color:#bbb;")
        self.video_feed.setMinimumSize(320, 240)
        grid.addWidget(self.video_feed, 1, 0, 4, 2)

        forward = QPushButton("Forward", self)
        forward.setFixedHeight(row_height)
        forward.setStyleSheet("font-size:16px;")
        forward.pressed.connect(lambda: self._serial_write("F1\n"))
        forward.released.connect(lambda: self._serial_write("F0\n"))
        grid.addWidget(forward, 1, 2, 1, 2)

        backward = QPushButton("Backward", self)
        backward.setFixedHeight(row_height)
        backward.setStyleSheet("font-size:16px;")
        backward.pressed.connect(lambda: self._serial_write("R1\n"))
        backward.released.connect(lambda: self._serial_write("R0\n"))
        grid.addWidget(backward, 2, 2, 1, 2)

        record = QPushButton()
        record.setFixedHeight(row_height)
        record.setIcon(QIcon("camera.png"))
        record.setIconSize(QSize(120, 120))
        record.setStyleSheet("font-size:60px;")
        record.clicked.connect(self._record_position)
        grid.addWidget(record, 3, 2, 1, 2)

        self.distance_label = QLabel(f"Distance: {self.distance}", self)
        self.distance_label.setStyleSheet("font-size:20px; background-color: lightgrey; padding:10px;")
        grid.addWidget(self.distance_label, 4, 2, 1, 1)

        self.gps_label = QLabel(f"GPS\n Lat: {self.gps_lat}\n Long:{self.gps_long}", self)
        self.gps_label.setStyleSheet("font-size:20px; background-color: lightgrey; padding:10px;")
        grid.addWidget(self.gps_label, 4, 3, 1, 1)

        grid.setRowMinimumHeight(1, 100)
        self.setLayout(grid)

    def _init_log_header(self):
        try:
            date = datetime.datetime.now().strftime("%d-%m-%Y")
            with open(self.file_path, "a") as f:
                f.write(f"Project Name: {self.project_name}  Date: {date}\n\n")
        except Exception as e:
            print("Header write error:", e)

    # ---------- Camera slots ----------
    def _on_new_frame(self, qimg: QImage, bgr_frame):
        self.last_frame_bgr = bgr_frame
        pix = QPixmap.fromImage(qimg).scaled(
            self.video_feed.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.video_feed.setPixmap(pix)

    def _on_camera_error(self, msg: str):
        if self.video_feed.text() in ("", "Starting camera…"):
            self.video_feed.setText(msg)

    # # ---------- Serial slots ----------
    # def _on_serial_line(self, s: str):
    #     if s.startswith("COUNT:"):
    #         try:
    #             val = int(s.split(":", 1)[1])
    #             self.distance = val // 10
    #             self.distance_label.setText(f"Distance: {self.distance}")
    #         except Exception:
    #             pass

    def _on_serial_line(self, s: str):
        s = s.strip()
        if s.startswith("COUNT:"):
            try:
                val = int(s.split(":", 1)[1])
                self.distance = val // 10  # your existing scaling
                self.distance_label.setText(f"Distance: {self.distance}")
            except Exception:
                pass

        elif s.startswith("GPS:"):
            payload = s.split(":", 1)[1]
            if payload == "INVALID":
                # Optional: show a hint in the UI
                self.gps_label.setText("GPS\n Lat: --\n Long: --")
            else:
                try:
                    lat_str, lon_str = payload.split(",", 1)
                    self.gps_lat = float(lat_str)
                    self.gps_long = float(lon_str)
                    self.gps_label.setText(
                        f"GPS\n Lat: {self.gps_lat:.6f}\n Long:{self.gps_long:.6f}"
                    )
                except Exception:
                    # Bad parse, ignore
                    pass


    def _on_serial_error(self, msg: str):
        # Optional: show once or log
        print(msg)

    def _serial_write(self, text: str):
        # Cross-thread queued call into worker
        if hasattr(self, 'ser_worker'):
            self.ser_worker.write_text(text)

    def _record_position(self):
        print(f"Photo Taken, Position Recorded {self.distance}")
        tstamp = datetime.datetime.now().strftime("%H-%M-%S")
        # Log GPS if we have it; otherwise write placeholders
        if isinstance(self.gps_lat, (int, float)) and isinstance(self.gps_long, (int, float)) \
           and self.gps_lat != 0 and self.gps_long != 0:
            gps_part = f"   GPS: {self.gps_lat:.6f},{self.gps_long:.6f}"
        else:
            gps_part = "   GPS: --,--"
    
        log_line = f"Time: {tstamp}   Distance: {self.distance}{gps_part}\n"
        try:
            with open(self.file_path, "a") as f:
                f.write(log_line)
        except Exception as e:
            print("Log write error:", e)
    
        if self.last_frame_bgr is not None:
            # Optional: keep filename simple; GPS stays in the log
            image_name = os.path.join(
                self.project_path,
                f"Time-{tstamp}_Distance-{self.distance}_GPS-{self.gps_lat},{self.gps_long}.jpg"
            )
            try:
                cv2.imwrite(image_name, self.last_frame_bgr)
                print(f"Saved Image to {image_name}")
            except Exception as e:
                print("Image save error:", e)
        else:
            print("No frame available to save.")


    # ---------- Navigation & cleanup ----------
    def _go_home(self):
        self._cleanup()
        self.appwin.show_start()

    def _cleanup(self):
        # Stop serial thread
        try:
            if hasattr(self, 'ser_worker'):
                self.ser_worker.stop()
            if hasattr(self, 'ser_thread') and self.ser_thread.isRunning():
                self.ser_thread.quit()
                self.ser_thread.wait(500)
        except Exception:
            pass
        # Stop camera thread
        try:
            if hasattr(self, "cam_worker"):
                self.cam_worker.stop()
            if hasattr(self, "cam_thread") and self.cam_thread.isRunning():
                self.cam_thread.quit()
                self.cam_thread.wait(500)
        except Exception:
            pass

# ============================
# App Window (single top-level with stack)
# ============================
class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(string_window_title)
        self.setWindowIcon(QIcon("Window_Icon.png"))
        self.setGeometry(0, 0, 800, 400)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.start_page = StartPage(self)
        self.files_page = FilesPage(self, base_path=BASE_DIR)
        self.main_page = None

        self.stack.addWidget(self.start_page)   # index 0
        self.stack.addWidget(self.files_page)   # index 1

        self._files_back_target = "start"

    def show_start(self):
        if self.main_page is not None:
            try:
                self.main_page._cleanup()
            except Exception:
                pass
            idx = self.stack.indexOf(self.main_page)
            if idx != -1:
                w = self.stack.widget(idx)
                self.stack.removeWidget(w)
                w.deleteLater()
            self.main_page = None
        self.stack.setCurrentWidget(self.start_page)

    def start_project(self, project_name: str):
        if self.main_page is not None:
            try:
                self.main_page._cleanup()
            except Exception:
                pass
            idx = self.stack.indexOf(self.main_page)
            if idx != -1:
                w = self.stack.widget(idx)
                self.stack.removeWidget(w)
                w.deleteLater()
        self.main_page = MainPage(self, project_name)
        self.stack.addWidget(self.main_page)
        self.stack.setCurrentWidget(self.main_page)

    def show_files(self, back_to: str = "start"):
        self._files_back_target = back_to
        self.files_page._refresh_folders()
        self.stack.setCurrentWidget(self.files_page)

    def pop_to_previous(self):
        if self._files_back_target == "main" and self.main_page is not None:
            self.stack.setCurrentWidget(self.main_page)
        else:
            self.stack.setCurrentWidget(self.start_page)

    def closeEvent(self, e):
        try:
            if self.main_page is not None:
                self.main_page._cleanup()
        except Exception:
            pass
        super().closeEvent(e)

# ============================
class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(string_window_title)
        self.setWindowIcon(QIcon("Window_Icon.png"))
        self.setGeometry(0, 0, 800, 400)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.start_page = StartPage(self)
        self.files_page = FilesPage(self, base_path=BASE_DIR)
        self.main_page = None

        self.stack.addWidget(self.start_page)   # index 0
        self.stack.addWidget(self.files_page)   # index 1

        self._files_back_target = "start"

    def show_start(self):
        if self.main_page is not None:
            try:
                self.main_page._cleanup()
            except Exception:
                pass
            idx = self.stack.indexOf(self.main_page)
            if idx != -1:
                w = self.stack.widget(idx)
                self.stack.removeWidget(w)
                w.deleteLater()
            self.main_page = None
        self.stack.setCurrentWidget(self.start_page)

    def start_project(self, project_name: str):
        if self.main_page is not None:
            try:
                self.main_page._cleanup()
            except Exception:
                pass
            idx = self.stack.indexOf(self.main_page)
            if idx != -1:
                w = self.stack.widget(idx)
                self.stack.removeWidget(w)
                w.deleteLater()
        self.main_page = MainPage(self, project_name)
        self.stack.addWidget(self.main_page)
        self.stack.setCurrentWidget(self.main_page)

    def show_files(self, back_to: str = "start"):
        self._files_back_target = back_to
        self.files_page._refresh_folders()
        self.stack.setCurrentWidget(self.files_page)

    def pop_to_previous(self):
        if self._files_back_target == "main" and self.main_page is not None:
            self.stack.setCurrentWidget(self.main_page)
        else:
            self.stack.setCurrentWidget(self.start_page)

    def closeEvent(self, e):
        try:
            if self.main_page is not None:
                self.main_page._cleanup()
        except Exception:
            pass
        super().closeEvent(e)

# ============================
# Entrypoint
# ============================
def main():
    # If Wayland warns about requestActivate, prefer showMaximized() or mute warnings via env var.
    # os.environ.setdefault("QT_LOGGING_RULES", "qt.qpa.wayland.warning=false")

    app = QApplication(sys.argv)
    win = AppWindow()
    # Safer on Wayland to avoid implicit activation warnings
    win.showMaximized()  # was: win.showFullScreen()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
