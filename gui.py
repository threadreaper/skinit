"""WIP gui interface for SkinIt"""
import sys
from pathlib import Path

from PyQt5.QtWidgets import (QMainWindow, QLabel, QPushButton, QFrame,
                             QAction, QFileDialog, QApplication)
from PyQt5.QtGui import QPixmap

import color_functions


class Example(QMainWindow):
    """Window class"""
    def __init__(self):
        """initialize window - assign attribs, attach objects, etc"""
        super().__init__()

        self.img_path = QLabel(self)
        self.color = []
        self.frame = []
        self.img = None
        self.label = QLabel(self)

        self.init_ui()

    def init_ui(self):
        """initialize window ui"""
        self.label.setGeometry(0, 100, 800, 500)

        _quit = QAction('Quit', self)
        _quit.setStatusTip('Close the application')
        _quit.triggered.connect(QApplication.instance().quit)

        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(_quit)

        browse = QPushButton("Browse", self)
        browse.setStatusTip("Select a wallpaper")
        browse.move(2, 30)
        browse.minimumSizeHint()
        browse.clicked.connect(self.show_dialog)

        self.img_path.setStyleSheet("QWidget { background-color: #FFFFFF }")

        if self.img:
            self.img_path.setText(self.img)
        else:
            self.img_path.setText("path to image file on your system")
        self.img_path.move(110, 30)
        self.img_path.resize(490, 30)

        for i in range(16):
            self.color.append("#000000")
            self.frame.append(QFrame(self))
            self.frame[i].setGeometry(i*40-30, 70, 30, 30)
            self.frame[i].setStyleSheet(("QWidget { background-color: "
                                         "%s }" % self.color[i]))

        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('File dialog')
        self.show()

    def show_dialog(self):
        """open a file browser dialog window"""
        home_dir = str(Path.home())
        fname = QFileDialog.getOpenFileName(self, 'Open file', home_dir)

        if fname[0]:
            self.img_path.setText(fname[0])
            self.color = color_functions.get(fname[0])
            pixmap = QPixmap(fname[0])
            pixmap2 = pixmap.scaledToWidth(800)
            self.label.setPixmap(pixmap2)
            for i in range(len(self.color)):
                self.frame[i].setStyleSheet(("QWidget { background-color: %s }"
                                             % self.color[i].hex_string))


def main():
    """main application loop"""
    app = QApplication(sys.argv)
    ex = Example()
    ex.statusBar()
    sys.exit(app.exec_())


main()
