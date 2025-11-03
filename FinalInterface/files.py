from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from config import windowTitle, PROJECTS_DIR

import sys, os

class FileWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{windowTitle} Projects")
        self.setWindowIcon(QIcon("/icons/Window_Icon.png"))

        self.projectDir = PROJECTS_DIR
        self.currentPath = None

        self.file_menu()

    def file_menu(self):

        fileVBox = QVBoxLayout()
        fileVBox.setAlignment(Qt.AlignTop)

        fileTitle = QLabel("Project Files")
        fileTitle.setStyleSheet("font-size:30px;"
                                "font-weight:bold;"
                                "background-color:#0F4BEB;"
                                "color:white;")
        fileTitle.setMaximumHeight(60)
        fileTitle.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        fileVBox.addWidget(fileTitle)

        # H Box for file exploeres and image
        # V Box folder drop down and file selection
        # Image view

        folderViewHBox = QHBoxLayout()
        folderViewHBox.setAlignment(Qt.AlignTop)

        folderSelectionVBox = QVBoxLayout()
        folderSelectionVBox.setAlignment(Qt.AlignTop)

        self.folderList = QComboBox()

        if os.path.exists(self.projectDir):
            folders = [f for f in os.listdir(self.projectDir) if os.path.isdir(os.path.join(self.projectDir, f))]
            for folder in folders:
                self.folderList.addItem(folder)

        self.folderList.setStyleSheet("""
                                      QComboBox{
                                      font-size:16px;}
                                      QComboBox QAbstractItemView{
                                      font-size:16px;}
                                      """)
        
        folderSelectionVBox.addWidget(self.folderList)

        self.fileList = QListWidget()
        

        folderSelectionWidget = QWidget()
        folderSelectionWidget.setLayout(folderSelectionVBox)

        folderViewHBox.addWidget(folderSelectionWidget)

        folderViewWidget = QWidget()
        folderViewWidget.setLayout(folderViewHBox)       

        fileVBox.addWidget(folderViewWidget)

        self.setLayout(fileVBox)

    def load_files(self, item):
        self.currentFolder = os.path.join(self.projectDir, item.text())
        self.fileList.clear()
        
         

def main():
    app = QApplication(sys.argv)
    window = FileWindow()

    window.showMaximized()
    sys.exit(app.exec_()) #exec_ is to execute


if __name__ == "__main__":
    main()


    