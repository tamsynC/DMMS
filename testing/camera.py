# from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
# from PyQt5.QtMultimedia import QCamera, QCameraInfo
# from PyQt5.QtMultimediaWidgets import QCameraViewfinder

# import os, sys, time

# class CameraWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Live Camera Feed")
#         self.setGeometry(100, 100, 800, 600)

#         # Create a camera viewfinder widget
#         self.viewfinder = QCameraViewfinder()

#         # Layout
#         central_widget = QWidget()
#         layout = QVBoxLayout()
#         layout.addWidget(self.viewfinder)
#         central_widget.setLayout(layout)
#         self.setCentralWidget(central_widget)

#         # Select the first available camera
#         available_cameras = QCameraInfo.availableCameras()
#         if not available_cameras:
#             raise RuntimeError("No camera devices found")

#         self.camera = QCamera(available_cameras[4]) #is the avaliable camera on T laptop
#         self.camera.setViewfinder(self.viewfinder)
#         self.camera.start()


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = CameraWindow()
#     window.show()
#     sys.exit(app.exec_())

# import cv2

# def list_cameras(max_index=10):
#     available = []
#     for i in range(max_index):
#         cap = cv2.VideoCapture(i, cv2.CAP_ANY) # CAP_DSHOW helps avoid warnings on Windows
#         if cap is not None and cap.isOpened():
#             available.append(i)
#             cap.release()
#     return available

# cameras = list_cameras()
# print("Available cameras:", cameras if cameras else "None found")

# import sys, cv2
# from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
# from PyQt5.QtCore import QTimer, Qt
# from PyQt5.QtGui import QImage, QPixmap

# DEVICE = "/dev/video6"

# class CVWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Live Camera Feed (/dev/video6 via OpenCV)")
#         self.setGeometry(100, 100, 800, 600)

#         self.label = QLabel("Starting...", self)
#         self.label.setAlignment(Qt.AlignCenter)
#         self.setCentralWidget(self.label)

#         # Use V4L2 backend explicitly
#         self.cap = cv2.VideoCapture(DEVICE, cv2.CAP_V4L2)
#         if not self.cap.isOpened():
#             raise RuntimeError(f"Could not open {DEVICE}")

#         # Try a sane mode (won't fail if unsupported; V4L2 will pick closest)
#         self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#         self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
#         self.cap.set(cv2.CAP_PROP_FPS, 30)

#         self.timer = QTimer(self)
#         self.timer.timeout.connect(self.update_frame)
#         self.timer.start(30)  # ~33ms ~= 30fps

#     def update_frame(self):
#         ok, frame = self.cap.read()
#         if not ok:
#             self.label.setText("⚠️ No frame")
#             return
#         # Convert BGR (OpenCV) -> RGB (Qt)
#         rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         h, w, ch = rgb.shape
#         qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
#         self.label.setPixmap(QPixmap.fromImage(qimg).scaled(
#             self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

#     def closeEvent(self, e):
#         self.timer.stop()
#         if self.cap.isOpened():
#             self.cap.release()
#         super().closeEvent(e)

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     win = CVWindow()
#     win.show()
#     sys.exit(app.exec_())

# from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
# from PyQt5.QtMultimedia import QCamera, QCameraInfo
# from PyQt5.QtMultimediaWidgets import QCameraViewfinder

# import sys

# PREFERRED_DESC = "Teslong"       # match by description
# PREFERRED_DEV  = "/dev/video4"   # optional: match by device path

# class CameraWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Live Camera Feed")
#         self.setGeometry(100, 100, 800, 600)

#         self.viewfinder = QCameraViewfinder()
#         central = QWidget()
#         layout = QVBoxLayout(central)
#         layout.addWidget(self.viewfinder)
#         self.setCentralWidget(central)

#         cam_info = self.pick_camera()
#         if cam_info is None:
#             raise RuntimeError("Teslong camera not found (and no fallback available).")

#         print(f"Using camera: {cam_info.description()} [{cam_info.deviceName()}]")
#         self.camera = QCamera(cam_info)
#         self.camera.setViewfinder(self.viewfinder)
#         self.camera.start()

#     def pick_camera(self) -> QCameraInfo:
#         cams = QCameraInfo.availableCameras()

#         if not cams:
#             print("No camera devices found.")
#             return None

#         # Show what Qt sees (helps debug)
#         print("Detected cameras:")
#         for i, c in enumerate(cams):
#             print(f"  [{i}] {c.description()}  -> {c.deviceName()}")

#         # 1) Prefer description match (e.g., "Teslong")
#         for c in cams:
#             if PREFERRED_DESC.lower() in c.description().lower():
#                 return c

#         # 2) Prefer exact device path match (e.g., "/dev/video4")
#         for c in cams:
#             # deviceName() is like "v4l2:/dev/video4" on Linux
#             dev = c.deviceName()
#             if dev.endswith(PREFERRED_DEV) or dev == PREFERRED_DEV:
#                 return c

#         # 3) Fallback: first camera (or choose some other policy)
#         print("Preferred camera not found; falling back to the first available device.")
#         return cams[0]

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     w = CameraWindow()
#     w.show()
#     sys.exit(app.exec_())

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtMultimedia import QCamera, QCameraInfo, QCameraViewfinderSettings
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtMultimedia import QVideoFrame
import sys

PREFERRED_DEV = "/dev/video4"   # your Teslong node

def pick_camera():
    for c in QCameraInfo.availableCameras():
        if c.deviceName().endswith(PREFERRED_DEV):
            return c
    cams = QCameraInfo.availableCameras()
    return cams[0] if cams else None

class CameraWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Teslong (MJPEG forced)")
        self.setGeometry(100, 100, 800, 600)

        self.viewfinder = QCameraViewfinder()
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(self.viewfinder)
        self.setCentralWidget(central)

        cam_info = pick_camera()
        if not cam_info:
            raise RuntimeError("No cameras found")

        print(f"Using: {cam_info.description()} -> {cam_info.deviceName()}")
        self.camera = QCamera(cam_info)
        self.camera.setViewfinder(self.viewfinder)

        # Helpful debug
        self.camera.error.connect(lambda _: print("Camera error:", self.camera.errorString()))
        self.camera.statusChanged.connect(lambda s: print("Status:", s))

        # Force MJPEG + safe resolution; avoid setting FPS (some drivers reject it)
        s = QCameraViewfinderSettings()
        s.setResolution(1280, 720)                      # or 640x480 if you prefer
        s.setPixelFormat(QVideoFrame.Format_Jpeg)       # MUST match MJPG
        self.camera.setViewfinderSettings(s)

        self.camera.start()

if __name__ == "__main__":
    # (Optional) Workaround Wayland oddities:
    # import os; os.environ["QT_QPA_PLATFORM"] = "xcb"
    app = QApplication(sys.argv)
    w = CameraWindow()
    w.show()
    sys.exit(app.exec_())
