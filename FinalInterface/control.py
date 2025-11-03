from main import MainWindow
from start import StartWindow
from map import MapWindow

from PyQt5.QtWidgets import QApplication

import sys

class Controler():
    def __init__(self):
        self.app = QApplication(sys.argv)

        self.startWindow = None
        self.mainWindow = None
        self.mapWindow = None

        self.pName = None
        self.eLength = None

    def show_start_window(self):
        self.startWindow = StartWindow()
        self.startWindow.projectDataEntered.connect(self.open_main_window)
        self.startWindow.showMaximized()

    def open_main_window(self, pName, eLength):
        self.startWindow.close()

        self.mainWindow = MainWindow(pName, eLength)
        self.mainWindow.openMapRequest.connect(self.open_map_window)
        self.mainWindow.showMaximized()

    def open_map_window(self, lat: float, lng: float):

        if self.mapWindow is not None:
            self.mapWindow.close()
        
        self.mapWindow = MapWindow(lat, lng)
        self.mapWindow.showMaximized()


    def run(self):
        self.show_start_window()
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    controller = Controler()
    controller.run()

    

        