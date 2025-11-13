# from PyQt5.QtWidgets import *
# from PyQt5.QtGui import *
# from PyQt5.QtCore import *

# from config import windowTitle, PROJECTS_DIR

# import sys, os

# class FileWindow(QWidget):

#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle(f"{windowTitle} Projects")
#         self.setWindowIcon(QIcon("/icons/Window_Icon.png"))

#         self.projectDir = PROJECTS_DIR
#         self.currentPath = None
#         self.projectName = None

#         self.file_menu()

#     def file_menu(self):

#         fileVBox = QVBoxLayout()
#         fileVBox.setAlignment(Qt.AlignTop | Qt.AlignCenter)

#         self.backButton = QPushButton("← Back")
#         self.backButton.setStyleSheet("font-size:16px;"
#                                       "font-weight:bold;")
#         fileVBox.addWidget(self.backButton, alignment=Qt.AlignRight)

#         fileTitle = QLabel("Project Files")
#         fileTitle.setStyleSheet("font-size:32px;"
#                                 "font-weight:bold;"
#                                 "background-color:#0F4BEB;"
#                                 "color:white;")
#         fileTitle.setAlignment(Qt.AlignHCenter)
#         fileVBox.addWidget(fileTitle)

#         # H Box for file exploeres and image
#         # V Box folder drop down and file selection
#         # Image view

#         folderViewHBox = QHBoxLayout()
#         folderViewHBox.setAlignment(Qt.AlignTop)

#         folderSelectionVBox = QVBoxLayout()
#         folderSelectionVBox.setAlignment(Qt.AlignTop)

#         folderListLabel = QLabel("Folder Lists", self)
#         folderListLabel.setStyleSheet("font-size:16px;"
#                                       "font-weight:bold;")
        
#         folderSelectionVBox.addWidget(folderListLabel)

#         self.folderList = QComboBox()

#         if os.path.exists(self.projectDir):
#             folders = [f for f in os.listdir(self.projectDir) if os.path.isdir(os.path.join(self.projectDir, f))]
#             for folder in folders:
#                 self.folderList.addItem(folder)

#         self.folderList.setStyleSheet("""
#                                       QComboBox{
#                                       font-size:16px;}
#                                       QComboBox QAbstractItemView{
#                                       font-size:16px;}
#                                       """)
        
#         self.folderList.currentTextChanged.connect(self.load_files)
        
#         folderSelectionVBox.addWidget(self.folderList)

#         self.fileListLabel = QLabel(f"Files in {self.currentPath}")
#         self.fileListLabel.setStyleSheet("font-size:16px;"
#                                       "font-weight:bold;")
#         folderSelectionVBox.addWidget(self.fileListLabel)

#         self.fileList = QListWidget()
#         self.fileList.setStyleSheet("""
#                                     QListWidget{
#                                     font-size:16px;
#                                     }""")
        
#         self.fileList.itemClicked.connect(self.show_preview)
        
#         folderSelectionVBox.addWidget(self.fileList)        

#         folderSelectionWidget = QWidget()
#         folderSelectionWidget.setLayout(folderSelectionVBox)
#         folderSelectionWidget.setMaximumWidth(150)

#         folderViewHBox.addWidget(folderSelectionWidget)

#         self.previewLabel = QLabel()
#         self.previewLabel.setAlignment(Qt.AlignCenter)
#         self.previewLabel.setStyleSheet("background-color:grey;")
#         folderViewHBox.addWidget(self.previewLabel)


#         folderViewWidget = QWidget()
#         folderViewWidget.setLayout(folderViewHBox)       

#         fileVBox.addWidget(folderViewWidget)

#         self.setLayout(fileVBox)

#         if self.folderList.count() > 0:
#             self.load_files(self.folderList.currentText())

#     def load_files(self, folderName):

#         if not folderName:
#             self.fileList.clear()
#             self.currentPath = None
#             self.projectName = None
#             return

#         self.currentPath = os.path.join(self.projectDir, folderName)
#         self.projectName = os.path.basename(self.currentPath)

#         self.fileList.clear()

#         self.fileListLabel.setText(f"Files in {self.projectName}")

#         if os.path.exists(self.currentPath):
#             for f in sorted(os.listdir(self.currentPath)):
#                 full = os.path.join(self.currentPath, f)
#                 if os.path.isfile(full):  # only files; remove if you also want subfolders
#                     self.fileList.addItem(f)

#     def show_preview(self, fileName):

#         if self.currentPath is None:
#             return
        
#         filePath = os.path.join(self.currentPath, fileName.text())

#         if os.path.isfile(filePath):

#             if fileName.text().lower().endswith(".txt"):
#                 with open(filePath, "r") as f:
#                     text = f.read()
                
#                 self.previewLabel.setPixmap(QPixmap())
#                 self.previewLabel.setText(text)

#             elif fileName.text().lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
#                 pixmap = QPixmap(filePath)
#                 self.previewLabel.setPixmap(pixmap.scaled(
#                     self.previewLabel.height(),
#                     self.previewLabel.width(),
#                     Qt.KeepAspectRatio,
#                     Qt.SmoothTransformation
#                 ))
#                 self.previewLabel.setText("")
            
#             else:
#                 self.previewLabel.setPixmap(QPixmap())
#                 self.previewLabel.setText(f"Cannot preview {fileName.text()}")

        
         

# def main():
#     app = QApplication(sys.argv)
#     window = FileWindow()

#     window.showMaximized()
#     sys.exit(app.exec_()) #exec_ is to execute


# if __name__ == "__main__":
#     main()

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

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

        # Media player for video preview
        self.player = QMediaPlayer(self, QMediaPlayer.VideoSurface)
        self.player.setVolume(100)

        self.file_menu()

    def file_menu(self):

        fileVBox = QVBoxLayout()
        fileVBox.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        self.backButton = QPushButton("← Back")
        self.backButton.setStyleSheet("font-size:16px; font-weight:bold;")
        fileVBox.addWidget(self.backButton, alignment=Qt.AlignRight)

        fileTitle = QLabel("Project Files")
        fileTitle.setStyleSheet(
            "font-size:32px; font-weight:bold; background-color:#0F4BEB; color:white;"
        )
        fileTitle.setAlignment(Qt.AlignHCenter)
        fileVBox.addWidget(fileTitle)

        folderViewHBox = QHBoxLayout()
        folderViewHBox.setAlignment(Qt.AlignTop)

        # ---- Left: folders & files ----
        folderSelectionVBox = QVBoxLayout()
        folderSelectionVBox.setAlignment(Qt.AlignTop)

        folderListLabel = QLabel("Folder Lists", self)
        folderListLabel.setStyleSheet("font-size:16px; font-weight:bold;")
        folderSelectionVBox.addWidget(folderListLabel)

        self.folderList = QComboBox()
        if os.path.exists(self.projectDir):
            folders = [f for f in os.listdir(self.projectDir)
                       if os.path.isdir(os.path.join(self.projectDir, f))]
            for folder in sorted(folders):
                self.folderList.addItem(folder)

        self.folderList.setStyleSheet("""
            QComboBox{ font-size:16px; }
            QComboBox QAbstractItemView{ font-size:16px; }
        """)
        self.folderList.currentTextChanged.connect(self.load_files)
        folderSelectionVBox.addWidget(self.folderList)

        self.fileListLabel = QLabel(f"Files in {self.currentPath}")
        self.fileListLabel.setStyleSheet("font-size:16px; font-weight:bold;")
        folderSelectionVBox.addWidget(self.fileListLabel)

        self.fileList = QListWidget()
        self.fileList.setStyleSheet("QListWidget{ font-size:16px; }")
        self.fileList.itemClicked.connect(self.show_preview)
        folderSelectionVBox.addWidget(self.fileList)

        folderSelectionWidget = QWidget()
        folderSelectionWidget.setLayout(folderSelectionVBox)
        folderSelectionWidget.setMaximumWidth(250)
        folderViewHBox.addWidget(folderSelectionWidget)

        # ---- Right: preview area (stacked) ----
        self.previewStack = QStackedWidget()
        self.previewStack.setMinimumSize(640, 480)

        # Text preview
        self.textPreview = QTextEdit()
        self.textPreview.setReadOnly(True)
        self.textPreview.setStyleSheet("background-color:#f7f7f7; font-size:14px;")
        self.textPreview.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)

        # Image preview
        self.imagePreview = QLabel()
        self.imagePreview.setAlignment(Qt.AlignCenter)
        self.imagePreview.setStyleSheet("background-color:#222; color:#ddd;")
        self.imagePreview.setMinimumSize(400, 300)

        # Video preview (with controls)
        videoContainer = QWidget()
        videoLayout = QVBoxLayout(videoContainer)
        videoLayout.setContentsMargins(0, 0, 0, 0)
        self.videoWidget = QVideoWidget()
        self.videoWidget.setMinimumSize(400, 300)
        videoLayout.addWidget(self.videoWidget)

        # Controls for video
        controls = QHBoxLayout()
        self.playBtn = QPushButton("Play")
        self.pauseBtn = QPushButton("Pause")
        self.stopBtn = QPushButton("Stop")
        for b in (self.playBtn, self.pauseBtn, self.stopBtn):
            b.setStyleSheet("font-size:14px;")
        controls.addStretch(1)
        controls.addWidget(self.playBtn)
        controls.addWidget(self.pauseBtn)
        controls.addWidget(self.stopBtn)
        controls.addStretch(1)
        videoLayout.addLayout(controls)

        self.player.setVideoOutput(self.videoWidget)
        self.playBtn.clicked.connect(self.player.play)
        self.pauseBtn.clicked.connect(self.player.pause)
        self.stopBtn.clicked.connect(self.player.stop)

        # Add pages to stack
        self.previewStack.addWidget(self.textPreview)   # index 0
        self.previewStack.addWidget(self.imagePreview)  # index 1
        self.previewStack.addWidget(videoContainer)     # index 2

        folderViewHBox.addWidget(self.previewStack, 1)

        folderViewWidget = QWidget()
        folderViewWidget.setLayout(folderViewHBox)
        fileVBox.addWidget(folderViewWidget)

        self.setLayout(fileVBox)

        if self.folderList.count() > 0:
            self.load_files(self.folderList.currentText())

    def load_files(self, folderName):
        # stop any playing video when switching folders
        self.player.stop()

        if not folderName:
            self.fileList.clear()
            self.currentPath = None
            self.projectName = None
            self.fileListLabel.setText("Files")
            return

        self.currentPath = os.path.join(self.projectDir, folderName)
        self.projectName = os.path.basename(self.currentPath)

        self.fileList.clear()
        self.fileListLabel.setText(f"Files in {self.projectName}")

        if os.path.exists(self.currentPath):
            for f in sorted(os.listdir(self.currentPath)):
                full = os.path.join(self.currentPath, f)
                if os.path.isfile(full):
                    self.fileList.addItem(f)

        # default to a neutral preview
        self.previewStack.setCurrentIndex(1)
        self.imagePreview.setPixmap(QPixmap())
        self.imagePreview.setText("Select a file to preview")

    def show_preview(self, item: QListWidgetItem):
        if self.currentPath is None:
            return

        file_name = item.text()
        file_path = os.path.join(self.currentPath, file_name)

        # stop any existing video
        self.player.stop()

        if not os.path.isfile(file_path):
            self.previewStack.setCurrentIndex(1)
            self.imagePreview.setPixmap(QPixmap())
            self.imagePreview.setText("Selected item is not a file.")
            return

        fname_lower = file_name.lower()

        # --- Text preview ---
        if fname_lower.endswith(".txt"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            except Exception as e:
                text = f"Error reading file:\n{e}"
            self.textPreview.setPlainText(text)
            self.previewStack.setCurrentIndex(0)
            return

        # --- Image preview ---
        if fname_lower.endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                self.imagePreview.setPixmap(QPixmap())
                self.imagePreview.setText("Unable to load image.")
            else:
                # scale to label size keeping aspect ratio
                target_w = self.imagePreview.width()
                target_h = self.imagePreview.height()
                self.imagePreview.setPixmap(
                    pixmap.scaled(target_w, target_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
                self.imagePreview.setText("")
            self.previewStack.setCurrentIndex(1)
            return

        # --- Video preview (AVI/MP4 etc.) ---
        if fname_lower.endswith((".avi", ".mp4", ".mov", ".mkv")):
            url = QUrl.fromLocalFile(file_path)
            self.player.setMedia(QMediaContent(url))
            self.previewStack.setCurrentIndex(2)
            # Autoplay when selected (optional—comment this out if you prefer manual)
            self.player.play()
            return

        # --- Fallback ---
        self.previewStack.setCurrentIndex(1)
        self.imagePreview.setPixmap(QPixmap())
        self.imagePreview.setText(f"Cannot preview {file_name}")

    def closeEvent(self, e):
        try:
            self.player.stop()
        except Exception:
            pass
        super().closeEvent(e)


def main():
    app = QApplication(sys.argv)
    window = FileWindow()
    window.showMaximized()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

    