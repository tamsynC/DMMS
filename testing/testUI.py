# from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout

# app = QApplication([])

# window = QWidget()
# layout = QGridLayout()

# # Create buttons for demonstration
# btn1 = QPushButton("Button 1")  # Top-left
# btn2 = QPushButton("Button 2 (spans 2 rows)")  # Top-middle
# btn3 = QPushButton("Button 3")  # Top-right
# btn4 = QPushButton("Button 4 (spans 2 columns)")  # Middle-left
# btn5 = QPushButton("Button 5")  # Middle-right
# btn6 = QPushButton("Button 6")  # Bottom-left
# btn7 = QPushButton("Button 7")  # Bottom-middle
# btn8 = QPushButton("Button 8")  # Bottom-right

# # Add widgets to the grid
# layout.addWidget(btn1, 0, 0)
# layout.addWidget(btn2, 0, 1, 2, 1)  # spans 2 rows
# layout.addWidget(btn3, 0, 2)
# layout.addWidget(btn4, 1, 0, 1, 2)  # spans 2 columns
# layout.addWidget(btn5, 1, 2)
# layout.addWidget(btn6, 2, 0)
# layout.addWidget(btn7, 2, 1)
# layout.addWidget(btn8, 2, 2)

# # Set row heights using stretch factors
# layout.setRowStretch(0, 1)  # Top row is smallest
# layout.setRowStretch(1, 2)  # Middle row is taller
# layout.setRowStretch(2, 1)  # Bottom row same as top

# # Set column widths using stretch factors
# layout.setColumnStretch(0, 1)  # Left column narrow
# layout.setColumnStretch(1, 3)  # Middle column wide
# layout.setColumnStretch(2, 1)  # Right column narrow

# # Optional: set minimum sizes for individual widgets
# btn2.setMinimumHeight(80)
# btn4.setMinimumHeight(60)
# btn3.setMinimumWidth(100)
# btn5.setMinimumWidth(100)

# window.setLayout(layout)
# window.setWindowTitle("PyQt5 Grid Layout Example")
# window.show()
# app.exec_()

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QSlider, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PyQt5 Slider Example")
        
        layout = QVBoxLayout()

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(50)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(10)
        self.slider.setSingleStep(1)

        self.label = QLabel(f"Slider Value: {self.slider.value()}")

        self.slider.valueChanged.connect(self.update_label)

        layout.addWidget(self.slider)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def update_label(self, value):
        self.label.setText(f"Slider Value: {value}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())