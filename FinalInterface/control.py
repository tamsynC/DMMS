from main import MainWindow
from start import StartWindow
from map import MapWindow
from files import FileWindow

from PyQt5.QtWidgets import QApplication

import sys

class Controler():
    def __init__(self):
        self.app = QApplication(sys.argv)

        self.startWindow = None
        self.mainWindow = None
        self.mapWindow = None
        self.fileWindow = None 

        self.pName = None
        self.eLength = None

    def show_start_window(self):
        self.startWindow = StartWindow()
        self.startWindow.projectDataEntered.connect(self.open_main_window)
        self.startWindow.openFilesRequested.connect(self.open_file_window)
        self.startWindow.showMaximized()

    def open_main_window(self, pName, eLength):
        self.startWindow.close()

        self.mainWindow = MainWindow(pName, eLength)
        self.mainWindow.openMapRequest.connect(self.open_map_window)
        self.mainWindow.openFilesRequested.connect(self.open_file_window)
        self.mainWindow.goHomeRequested.connect(self.go_home)
        self.mainWindow.showMaximized()

    def go_home(self):
        if MainWindow is not None:
            self.mainWindow.close()
            self.mainWindow = None
        
        self.show_start_window()

    def open_map_window(self, lat: float, lng: float, pName: str):
        if self.mapWindow is None:
            self.mapWindow = MapWindow(lat, lng, pName)
            self.mapWindow.backButton.clicked.connect(self.close_map_window)
            
        
        self.mapWindow.showMaximized()
        self.mapWindow.raise_()
        self.mapWindow.activateWindow()

    def open_file_window(self):
        if self.fileWindow is None:
            self.fileWindow = FileWindow()
            self.fileWindow.backButton.clicked.connect(self.close_file_window)
        
        self.fileWindow.showMaximized()
        self.fileWindow.raise_()
        self.fileWindow.activateWindow()

    def close_file_window(self):
        if self.fileWindow is not None:
            self.fileWindow.close()
            self.fileWindow = None

    def close_map_window(self):
        if self.mapWindow is not None:
            self.mapWindow.close()
            self.mapWindow = None

    def run(self):
        self.show_start_window()
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    controller = Controler()
    controller.run()

    

        