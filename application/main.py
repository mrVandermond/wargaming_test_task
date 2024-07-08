import sys

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QRect
from PyQt6.QtGui import QPalette, QColor
from constants import WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT


class MainWindow(QMainWindow):
    def __init__(self, application):
        super().__init__(parent=None)
        self.__init_window_size(application)
        self.__init_background()
        self.setWindowTitle(WINDOW_TITLE)

    def __init_window_size(self, application):
        screen_size = application.primaryScreen().geometry()

        x = (screen_size.width() - screen_size.x()) // 2 - WINDOW_WIDTH // 2
        y = (screen_size.height() - screen_size.y()) // 2 - WINDOW_HEIGHT // 2
        window_rect = QRect(x, y, WINDOW_WIDTH, WINDOW_HEIGHT)

        self.setGeometry(window_rect)

    def __init_background(self):
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
        self.setPalette(palette)


if __name__ == '__main__':
    application = QApplication([])
    window = MainWindow(application)
    window.show()

    sys.exit(application.exec())
