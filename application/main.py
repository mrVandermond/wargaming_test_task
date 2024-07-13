import sys
from typing import Optional

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QRect
from PyQt6.QtGui import QPalette, QColor, QPainter, QPen, QMouseEvent, QPaintEvent

import constants as const

from scene import Scene


class MainWindow(QWidget):
    def __init__(self, screen_size: QRect):
        super().__init__(parent=None)
        self.setWindowTitle(const.WINDOW_TITLE)
        self.screen_size = screen_size
        self.__init_background()
        self.__init_window_size()

        self.scene = Scene(const.WINDOW_WIDTH, const.WINDOW_HEIGHT)

    def __init_window_size(self) -> None:
        """Initialises the window size and position"""
        x = (self.screen_size.width() - self.screen_size.x()) // 2 - const.WINDOW_WIDTH // 2
        y = (self.screen_size.height() - self.screen_size.y()) // 2 - const.WINDOW_HEIGHT // 2
        window_rect = QRect(x, y, const.WINDOW_WIDTH, const.WINDOW_HEIGHT)

        self.setGeometry(window_rect)
        self.setFixedWidth(const.WINDOW_WIDTH)
        self.setFixedHeight(const.WINDOW_HEIGHT)

    def __init_background(self) -> None:
        """Initialises the background of window"""
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))

        self.setPalette(palette)

    def __draw_rectangles(self, painter: QPainter) -> None:
        """Draws all rectangles"""
        for rect in self.scene.rectangles:
            painter.fillRect(rect["rect"], rect["color"])

    def __draw_reference_lines(self, painter: QPainter) -> None:
        """Draw all reference lines"""
        pen = QPen(QColor(0, 0, 0))
        pen.setWidthF(3)
        painter.setPen(pen)

        for line in self.scene.reference_lines.values():
            x1 = line["start_point"].x()
            x2 = line["end_point"].x()
            y1 = line["start_point"].y()
            y2 = line["end_point"].y()
            painter.drawLine(x1, y1, x2, y2)

    def paintEvent(self, event: Optional[QPaintEvent]) -> None:
        painter = QPainter(self)

        self.__draw_rectangles(painter)
        self.__draw_reference_lines(painter)

    def mouseDoubleClickEvent(self, event: Optional[QMouseEvent]) -> None:
        if event is None:
            return

        self.scene.create_rect(event.pos())
        self.update()

    def mousePressEvent(self, event: Optional[QMouseEvent]) -> None:
        if event is None:
            return

        event_point = event.pos()

        self.scene.set_current_action(event)

        if self.scene.current_action == const.ActionType.DRAG_RECT:
            self.scene.start_drag_rect(event_point)
            return

        if self.scene.current_action == const.ActionType.CREATE_REF_LINE:
            self.scene.start_creating_ref_line(event_point)
            return

        if self.scene.current_action == const.ActionType.DELETE_REF_LINE:
            self.scene.delete_ref_line(event_point)
            self.update()
            return

    def mouseMoveEvent(self, event: Optional[QMouseEvent]) -> None:
        if event is None:
            return

        event_point = event.pos()

        if self.scene.current_action == const.ActionType.DRAG_RECT:
            self.scene.drag_rect(event_point)

        if self.scene.current_action == const.ActionType.CREATE_REF_LINE:
            self.scene.move_end_point_ref_line(event_point)

        self.update()

    def mouseReleaseEvent(self, event: Optional[QMouseEvent]) -> None:
        if event is None:
            return

        if self.scene.current_action == const.ActionType.DRAG_RECT:
            self.scene.finish_drag_rect()

        if self.scene.current_action == const.ActionType.CREATE_REF_LINE:
            self.scene.finish_creating_ref_line(event.pos())
            self.update()

        self.scene.reset_temporal_data()


if __name__ == '__main__':
    application = QApplication([])
    primary_screen = application.primaryScreen()
    screen_size = QRect(0, 0, const.WINDOW_WIDTH, const.WINDOW_HEIGHT)

    if primary_screen:
        screen_size = primary_screen.geometry()

    window = MainWindow(screen_size)
    window.show()

    sys.exit(application.exec())
