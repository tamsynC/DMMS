from PyQt5.QtCore import * 
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtWebEngineWidgets import * 
from PyQt5.QtPrintSupport import *

import os, sys

from config import windowTitle

# GPSLat = -33
# GPSLong = 151

class MapWindow(QWidget):

    def __init__(self, GPSLat, GPSLong, projectName: str):
        super().__init__()

        self.GPSLat = GPSLat
        self.GPSLong = GPSLong

        self.projectName = projectName

        self.setWindowTitle(f"{windowTitle} Map")

        self.map_view(GPSLat, GPSLong, projectName)

    def map_view(self, GPSLat, GPSLong, pName):

        mapLayoutVBox = QVBoxLayout(self)
        mapLayoutVBox.setAlignment(Qt.AlignTop)


        self.backButton = QPushButton("← Back")
        self.backButton.setStyleSheet("font-size:16px;"
                                      "font-weight:bold;")
        mapLayoutVBox.addWidget(self.backButton, alignment=Qt.AlignRight)

        # Title
        mapTitle = QLabel(f"{pName} Map")
        mapTitle.setStyleSheet("font-size:32px;"
                                "font-weight:bold;"
                                "background-color:#0F4BEB;"
                                "color:white;")
        mapTitle.setAlignment(Qt.AlignCenter)

        mapLayoutVBox.addWidget(mapTitle)

        self.mapBrowser = QWebEngineView(self)
        self.mapBrowser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        mapLayoutVBox.addWidget(self.mapBrowser, 1)

        googleMaps = QUrl.fromUserInput(f"https://www.google.com/maps?q={GPSLat},{GPSLong}&z=16")

        self.mapBrowser.load(googleMaps)
        self.mapBrowser.loadFinished.connect(self.on_load_finished)

    def on_load_finished(self, ok: bool):
        if not ok:
            print("Google maps bad")

# def main():
#     app = QApplication(sys.argv)
#     win = MapWindow(-33, 151, "test")
#     win.showMaximized()
#     sys.exit(app.exec_())

# if __name__ == "__main__":
#     main()  