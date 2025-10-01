from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtMultimedia import QCamera, QCameraInfo
from PyQt5.QtMultimediaWidgets import QCameraViewfinder

import os, sys, time

class CameraWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live Camera Feed")
        self.setGeometry(100, 100, 800, 600)

        # Create a camera viewfinder widget
        self.viewfinder = QCameraViewfinder()

        # Layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.viewfinder)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Select the first available camera
        available_cameras = QCameraInfo.availableCameras()
        if not available_cameras:
            raise RuntimeError("No camera devices found")

        self.camera = QCamera(available_cameras[2]) #is the avaliable camera on T laptop
        self.camera.setViewfinder(self.viewfinder)
        self.camera.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraWindow()
    window.show()
    sys.exit(app.exec_())

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
