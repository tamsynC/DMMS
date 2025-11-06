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
        self.projectName = None

        self.file_menu()

    def file_menu(self):

        fileVBox = QVBoxLayout()
        fileVBox.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        self.backButton = QPushButton("← Back")
        self.backButton.setStyleSheet("font-size:16px;"
                                      "font-weight:bold;")
        fileVBox.addWidget(self.backButton, alignment=Qt.AlignRight)

        fileTitle = QLabel("Project Files")
        fileTitle.setStyleSheet("font-size:32px;"
                                "font-weight:bold;"
                                "background-color:#0F4BEB;"
                                "color:white;")
        fileTitle.setAlignment(Qt.AlignHCenter)
        fileVBox.addWidget(fileTitle)

        # H Box for file exploeres and image
        # V Box folder drop down and file selection
        # Image view

        folderViewHBox = QHBoxLayout()
        folderViewHBox.setAlignment(Qt.AlignTop)

        folderSelectionVBox = QVBoxLayout()
        folderSelectionVBox.setAlignment(Qt.AlignTop)

        folderListLabel = QLabel("Folder Lists", self)
        folderListLabel.setStyleSheet("font-size:16px;"
                                      "font-weight:bold;")
        
        folderSelectionVBox.addWidget(folderListLabel)

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
        
        self.folderList.currentTextChanged.connect(self.load_files)
        
        folderSelectionVBox.addWidget(self.folderList)

        self.fileListLabel = QLabel(f"Files in {self.currentPath}")
        self.fileListLabel.setStyleSheet("font-size:16px;"
                                      "font-weight:bold;")
        folderSelectionVBox.addWidget(self.fileListLabel)

        self.fileList = QListWidget()
        self.fileList.setStyleSheet("""
                                    QListWidget{
                                    font-size:16px;
                                    }""")
        
        self.fileList.itemClicked.connect(self.show_preview)
        
        folderSelectionVBox.addWidget(self.fileList)        

        folderSelectionWidget = QWidget()
        folderSelectionWidget.setLayout(folderSelectionVBox)
        folderSelectionWidget.setMaximumWidth(150)

        folderViewHBox.addWidget(folderSelectionWidget)

        self.previewLabel = QLabel()
        self.previewLabel.setAlignment(Qt.AlignCenter)
        self.previewLabel.setStyleSheet("background-color:grey;")
        folderViewHBox.addWidget(self.previewLabel)


        folderViewWidget = QWidget()
        folderViewWidget.setLayout(folderViewHBox)       

        fileVBox.addWidget(folderViewWidget)

        self.setLayout(fileVBox)

        if self.folderList.count() > 0:
            self.load_files(self.folderList.currentText())

    def load_files(self, folderName):

        if not folderName:
            self.fileList.clear()
            self.currentPath = None
            self.projectName = None
            return

        self.currentPath = os.path.join(self.projectDir, folderName)
        self.projectName = os.path.basename(self.currentPath)

        self.fileList.clear()

        self.fileListLabel.setText(f"Files in {self.projectName}")

        if os.path.exists(self.currentPath):
            for f in sorted(os.listdir(self.currentPath)):
                full = os.path.join(self.currentPath, f)
                if os.path.isfile(full):  # only files; remove if you also want subfolders
                    self.fileList.addItem(f)

    def show_preview(self, fileName):

        if self.currentPath is None:
            return
        
        filePath = os.path.join(self.currentPath, fileName.text())

        if os.path.isfile(filePath):

            if fileName.text().lower().endswith(".txt"):
                with open(filePath, "r") as f:
                    text = f.read()
                
                self.previewLabel.setPixmap(QPixmap())
                self.previewLabel.setText(text)

            elif fileName.text().lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                pixmap = QPixmap(filePath)
                self.previewLabel.setPixmap(pixmap.scaled(
                    self.previewLabel.height(),
                    self.previewLabel.width(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                ))
                self.previewLabel.setText("")
            
            else:
                self.previewLabel.setPixmap(QPixmap())
                self.previewLabel.setText(f"Cannot preview {fileName.text()}")

        
         

def main():
    app = QApplication(sys.argv)
    window = FileWindow()

    window.showMaximized()
    sys.exit(app.exec_()) #exec_ is to execute


if __name__ == "__main__":
    main()


    