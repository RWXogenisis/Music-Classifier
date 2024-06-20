from PySide2.QtWidgets import QWidget, QApplication, QLabel, QPushButton, QHBoxLayout, QVBoxLayout
from qtacrylic import WindowEffect
from PySide2 import QtWidgets
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont, QPalette, QColor, QPixmap, QPainter, QPen
import sys
import subprocess
from classifier import Controller


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(1000)
        self.setFixedHeight(500)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))
        self.setPalette(palette)

        self.ui_layout = QVBoxLayout(self)
        self.ui_layout.setAlignment(Qt.AlignTop)

        # Create a QHBoxLayout for the right side
        right_layout = QHBoxLayout()

        # Read data from a text file
        with open('test.txt', 'r') as file:
            text_data = file.read()

        # Create a label to display the text
        self.text_label = QLabel(text_data, self)
        self.text_label.setFont(QFont("Segoe UI", 14))
        self.text_label.setStyleSheet("color: white")

        # Load and resize the image to fit the available space
        pixmap = QPixmap('pic.png')
        available_width = self.width() - (self.width() // 3)
        available_height = self.height()
        pixmap = pixmap.scaledToWidth(available_width)
        self.image_label = QLabel(self)
        self.image_label.setPixmap(pixmap)

        # Add the text and image to the right side layout
        right_layout.addWidget(self.text_label)
        right_layout.addWidget(self.image_label)

        # Create a button to trigger a command
        self.button = QPushButton("Java Explorer", self)
        self.button.setFixedWidth(120)  # Set the width of the button (in pixels)
        self.button.clicked.connect(self.run_command)

        # Add the button to the main layout on the left
        self.ui_layout.addWidget(self.button)

        # Add the right side layout to the main layout on the right
        self.ui_layout.addLayout(right_layout)

        self.windowFX = WindowEffect()
        self.windowFX.setAcrylicEffect(self.winId())

        self.dragging = False
        self.offset = None
        print("Loading the models...")
        model_path = 'C:\\Users\\S Karun Vikhash\\Downloads\\ADS\\OOAD\\GITZLAB\\model.h5'
        audio_path = 'C:\\Users\\S Karun Vikhash\\Downloads\\ADS\\OOAD\\temp.wav'

        self.controller = Controller(model_path, audio_path)

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(Qt.white)
        pen.setWidth(2)
        painter.setPen(pen)
        # Move the vertical line further to the right
        painter.drawLine(self.width() // 3, 0, self.width() // 3, self.height())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.globalPos() - self.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.offset = None

    def run_command(self):
        # Replace with the command you want to run
        try:
            process = subprocess.run(["cmd.exe", "/c", "java final_page"], shell=True)
            print("storing the song...")
            # process.wait()
            self.controller.load_audio()
            self.controller.process_audio()
            print("Determining the genre of the song...")
            sorted_elements = self.controller.determine_genre()
            genre_dict = {0: "classical",1: "hiphop",2: "jazz",3: "pop",4: "rock"}

            with open('test.txt', 'w') as file:
                    for element, count in sorted_elements:
                        # Write each line to the file
                        file.write(f"{genre_dict[element]}, Frequency: {count}\n")
            self.controller.save_mel_spectrogram()
            self.update_text_label()
            self.controller.save_mel_spectrogram()
             # Update the image label with the new 'pic.png'
            new_pixmap = QPixmap('pic.png')
            available_width = self.width() - (self.width() // 3)
            new_pixmap = new_pixmap.scaledToWidth(available_width)
            self.image_label.setPixmap(new_pixmap)
            print("finished...")


        except subprocess.CalledProcessError:
            # The command failed
            print("Command execution failed")

    def update_text_label(self):
        text_data = self.read_test_file()
        self.text_label.setText(text_data)

    def read_test_file(self):
        try:
            with open('test.txt', 'r') as file:
                text_data = file.read()
            return text_data
        except FileNotFoundError:
            return ""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    app.exec_()
