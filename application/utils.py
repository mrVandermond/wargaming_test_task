from datetime import datetime
from random import randrange

from PyQt6.QtGui import QColor

from constants import WINDOW_WIDTH, WINDOW_HEIGHT, RECT_WIDTH, RECT_HEIGHT
from PyQt6.QtCore import QRect, QPoint


def generate_random_id():
    return datetime.now().timestamp()


def generate_random_color():
    return QColor(randrange(0, 255), randrange(0, 255), randrange(0, 255))


def get_adjusted_rect_point(point):
    x = point.x() - RECT_WIDTH // 2
    y = point.y() - RECT_HEIGHT // 2

    if x < 0:
        x = 0
    elif x + RECT_WIDTH > WINDOW_WIDTH:
        x = WINDOW_WIDTH - RECT_WIDTH

    if y < 0:
        y = 0
    elif y + RECT_HEIGHT > WINDOW_HEIGHT:
        y = WINDOW_HEIGHT - RECT_HEIGHT

    return QPoint(x, y)


def create_rect(point):
    adjusted_point = get_adjusted_rect_point(point)

    return QRect(adjusted_point.x(), adjusted_point.y(), RECT_WIDTH, RECT_HEIGHT)


def check_point_on_the_line(point, start_point_line, end_point_line):
    left_part = (point.x() - start_point_line.x()) / (end_point_line.x() - start_point_line.x())
    right_part = (point.y() - start_point_line.y()) / (end_point_line.y() - start_point_line.y())

    return abs(left_part - right_part) < 0.2


def find_rect_under_point(point, rectangles):
    for i, rect in enumerate(rectangles):
        if rect["rect"].contains(point):
            return i

    return -1


def has_neighbour_rects_in_point(point, rectangles, current_rect_index):
    x1 = point.x()
    x2 = point.x() + RECT_WIDTH
    y1 = point.y()
    y2 = point.y() + RECT_HEIGHT

    for i, rect in enumerate(rectangles):
        if current_rect_index == i:
            continue

        actual_rect = rect["rect"]
        rect_x1 = actual_rect.x()
        rect_x2 = actual_rect.x() + actual_rect.width()
        rect_y1 = actual_rect.y()
        rect_y2 = actual_rect.y() + actual_rect.height()

        if rect_x1 < x2 and rect_x2 > x1 and rect_y1 < y2 and rect_y2 > y1:
            return True

    return False


def calculate_rect_delta(current_point, previous_point):
    dx = current_point.x() - previous_point.x()
    dy = current_point.y() - previous_point.y()

    return dx, dy


def get_key_of_point(rect_index, line):
    if line["left_rect_index"] == rect_index:
        return "start_point"
    else:
        return "end_point"


def remove_reference_line_link(line_id, links):
    return list(filter(lambda temp: temp != line_id, links))
