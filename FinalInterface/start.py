from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import sys, os

from config import windowTitle, BASE_DIR, PROJECTS_DIR

class StartWindow(QWidget):

    projectDataEntered = pyqtSignal(str, str)
    openFilesRequested = pyqtSignal() 

    def __init__(self):
        super().__init__()
        self.setWindowTitle(windowTitle)
        self.setWindowIcon(QIcon("icons/Window_Icon.png"))

        self.projectName = None
        self.endoscopeLength = None

        self.start_menu()

    def start_menu(self):

        startLayoutVBox = QVBoxLayout()
        startLayoutVBox.setAlignment(Qt.AlignTop)

        title = QLabel(f"{windowTitle}", self)
        title.setStyleSheet("color:white;"
                            "background-color:#0F4BEB;"
                            "font-weight:bold;"
                            "font-size:30px")
        
        title.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        title.setFixedHeight(60)

        startLayoutVBox.addWidget(title)

        # Project Configuration
        # Project Name
        # Endoscope Length

        projectConfig = QLabel("Project Configuration", self)
        projectConfig.setStyleSheet("color:black;"
                                    "font-weight:bold;"
                                    "font-size:24px")
        projectConfig.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        title.setFixedHeight(50)
        startLayoutVBox.addWidget(projectConfig)
        
        settingsGrid = QGridLayout()

        projectNameLabel = QLabel("Project Name:", self)
        projectNameLabel.setStyleSheet("color:black;"
                                  "font-weight:bold;"
                                  "font-size:18px")
        settingsGrid.addWidget(projectNameLabel, 0, 0)

        self.projectNameText = QLineEdit()
        self.projectNameText.setPlaceholderText("Enter a Project Name")
        self.projectNameText.setStyleSheet("""QLineEdit{
                                           font-size=18px;
                                           font-weight=bold;}
                                           QLineEdit::placeholder{
                                           color=grey;
                                           font-size:18px;
                                           font-style=italic;
                                           }""")
        settingsGrid.addWidget(self.projectNameText, 0, 1)

        endoscopeLengthLabel = QLabel("Endoscope Length:", self)
        endoscopeLengthLabel.setStyleSheet("color:black;"
                                      "font-weight:bold;"
                                      "font-size:18px")
        settingsGrid.addWidget(endoscopeLengthLabel, 1, 0)

        self.endoscopeLengthText = QLineEdit()
        self.endoscopeLengthText.setPlaceholderText("Enter a Length")
        self.endoscopeLengthText.setStyleSheet("""QLineEdit{
                                               font-size=18px;
                                               font-weight=bold;}
                                               QLineEdit::placeholder{
                                               color=grey;
                                               font-size:18px;
                                               font-style=italic;
                                               }""")
        settingsGrid.addWidget(self.endoscopeLengthText, 1, 1)
        
        gridContainer = QWidget()
        gridContainer.setLayout(settingsGrid)

        startLayoutVBox.addWidget(gridContainer, alignment=Qt.AlignCenter)

        buttonsHBox = QHBoxLayout()
        buttonsHBox.setSpacing(20)
        buttonsHBox.setAlignment(Qt.AlignCenter)

        self.startButton = QPushButton("Start", self)
        self.startButton.setStyleSheet("color:white;"
                                       "background-color:#0F4BEB;"
                                       "font-weight:bold;"
                                       "font-size:18px")
        self.startButton.clicked.connect(self.open_main_menu)
        buttonsHBox.addWidget(self.startButton)

        self.fileButton = QPushButton()
        self.fileButton.setIcon(QIcon("icons/folder.png"))
        self.fileButton.setIconSize(QSize(25, 25))
        self.fileButton.setFixedSize(self.startButton.sizeHint())
        self.fileButton.clicked.connect(self.open_files)
        buttonsHBox.addWidget(self.fileButton)
        
        startLayoutVBox.addLayout(buttonsHBox)

        self.setLayout(startLayoutVBox)

    def open_main_menu(self):

        self.projectName = self.projectNameText.text().strip()

        if not self.projectName:
            QMessageBox.warning(self, "Error", "Please enter a project name")
            return
        
        self.endoscopeLength = self.endoscopeLengthText.text().strip()

        if not self.endoscopeLength:
            QMessageBox.warning(self, "Error", "Please enter an endoscope length")
            return
        
        projectDir = PROJECTS_DIR
        os.makedirs(projectDir, exist_ok=True)

        import re
        baseName = re.sub(r'[^\w\-. ]', "_", self.projectName)

        candidate = baseName
        counter = 1

        while os.path.exists(os.path.join(projectDir, candidate)):
            candidate = f"{baseName}-{counter}"
            counter += 1

        self.projectName = candidate

        self.projectDataEntered.emit(self.projectName, self.endoscopeLength)

        # print(f"Project Name: {self.projectName}\nEndoscope Length: {self.endoscopeLength}")

    def open_files(self):
        # print("Files Clicked")
        self.openFilesRequested.emit()

