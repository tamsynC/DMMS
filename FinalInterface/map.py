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

    

    def __init__(self, GPSLat, GPSLong):
        super().__init__()

        self.GPSLat = GPSLat
        self.GPSLong = GPSLong

        self.setWindowTitle(f"{windowTitle} Map")

        self.map_view(GPSLat, GPSLong)

    def map_view(self, GPSLat, GPSLong):

        mapLayout = QVBoxLayout(self)

        self.mapBrowser = QWebEngineView(self)

        mapLayout.addWidget(self.mapBrowser)

        # self.mapBrowser.setUrl(QUrl(f"https://www.google.com/maps/place/{GPSLat},{GPSLong}"))

        googleMaps = QUrl.fromUserInput(f"https://www.google.com/maps?q={GPSLat},{GPSLong}&z=16")

        self.mapBrowser.load(googleMaps)

        self.mapBrowser.loadFinished.connect(self.on_load_finished)

    def on_load_finished(self, ok: bool):
        if not ok:
            print("Google maps bad")


def main():
    app = QApplication(sys.argv)
    win = MapWindow(-33, 151)
    win.showMaximized()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()  


