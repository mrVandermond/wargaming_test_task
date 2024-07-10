import sys

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QRect, Qt, QPoint
from PyQt6.QtGui import QPalette, QColor, QPainter, QPen

import constants as const

from enums import ActionEnum
from scene_state import SceneState


class MainWindow(QWidget):
    def __init__(self, screen_size):
        super().__init__(parent=None)
        self.setWindowTitle(const.WINDOW_TITLE)
        self.screen_size = screen_size
        self.__init_background()
        self.__init_window_size()

        self.scene_state = SceneState()

    def __init_window_size(self):
        x = (self.screen_size.width() - self.screen_size.x()) // 2 - const.WINDOW_WIDTH // 2
        y = (self.screen_size.height() - self.screen_size.y()) // 2 - const.WINDOW_HEIGHT // 2
        window_rect = QRect(x, y, const.WINDOW_WIDTH, const.WINDOW_HEIGHT)

        self.setGeometry(window_rect)

    def __init_background(self):
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))

        self.setPalette(palette)

    def paintEvent(self, event):
        painter = QPainter(self)

        for rect in self.scene_state.rectangles:
            painter.fillRect(rect["rect"], rect["color"])

        pen = QPen(QColor(0, 0, 0))
        pen.setWidthF(3)
        painter.setPen(pen)

        for line in self.scene_state.reference_lines.values():
            painter.drawLine(line["start_point"].x(), line["start_point"].y(), line["end_point"].x(), line["end_point"].y())

    def mouseDoubleClickEvent(self, event):
        self.scene_state.create_rect(event.pos())
        self.update()

    def mousePressEvent(self, event):
        event_point = event.pos()

        self.scene_state.set_current_action(event)

        if self.scene_state.current_action == ActionEnum.DRAG_RECT:
            self.scene_state.start_drag_rect(event_point)
            return

        if self.scene_state.current_action == ActionEnum.CREATE_REF_LINE:
            self.scene_state.start_creating_ref_line(event_point)
            return

        if self.scene_state.current_action == ActionEnum.DELETE_REF_LINE:
            self.scene_state.delete_ref_line(event_point)
            self.update()
            return

    def mouseMoveEvent(self, event):
        event_point = event.pos()

        if self.scene_state.current_action == ActionEnum.DRAG_RECT:
            self.scene_state.drag_rect(event_point)

        if self.scene_state.current_action == ActionEnum.CREATE_REF_LINE:
            self.scene_state.move_end_point_ref_line(event_point)

        self.update()

    def mouseReleaseEvent(self, event):
        if self.scene_state.current_action == ActionEnum.CREATE_REF_LINE:
            self.scene_state.end_creating_ref_line(event.pos())
            self.update()

        self.scene_state.reset_temporal_state()


if __name__ == '__main__':
    application = QApplication([])
    window = MainWindow(application.primaryScreen().geometry())
    window.show()

    sys.exit(application.exec())
