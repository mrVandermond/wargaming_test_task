from datetime import datetime
from random import randrange

from PyQt6.QtGui import QColor

from constants import WINDOW_WIDTH, WINDOW_HEIGHT, RECT_WIDTH, RECT_HEIGHT, POINT_INTERSECTION_THRESHOLD
from PyQt6.QtCore import QPoint


def generate_random_id():
    """Generates random id based on timestamp"""
    return str(datetime.now().timestamp())


def generate_random_color():
    """Generates random color"""
    return QColor(randrange(0, 255), randrange(0, 255), randrange(0, 255))


def get_adjusted_rect_point(point):
    """
    Creates adjusted rect point so that new point would be at the center of the rect
    and rect cannot be outside the application window
    """
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


def check_point_on_the_line(point, start_point_line, end_point_line):
    """Checks with threshold whether point on the line or not"""
    left_part = (point.x() - start_point_line.x()) / (end_point_line.x() - start_point_line.x())
    right_part = (point.y() - start_point_line.y()) / (end_point_line.y() - start_point_line.y())

    return abs(left_part - right_part) < POINT_INTERSECTION_THRESHOLD


def calculate_rect_delta(current_point, previous_point):
    """Calculates rect delta between points"""
    dx = current_point.x() - previous_point.x()
    dy = current_point.y() - previous_point.y()

    return dx, dy


def get_key_of_point(rect_id, line):
    """Defines which key of point should be chosen based on rectangle id"""
    if line["first_rect_id"] == rect_id:
        return "start_point"
    else:
        return "end_point"
