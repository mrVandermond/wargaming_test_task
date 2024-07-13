from datetime import datetime
from random import randrange
from typing import Optional, List, Literal, Union

from PyQt6.QtGui import QColor

from custom_types import ReferenceLineT
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, RECT_WIDTH, RECT_HEIGHT, POINT_INTERSECTION_THRESHOLD
from PyQt6.QtCore import QPoint, QRect


def generate_random_id() -> str:
    """Generates random id based on timestamp"""
    return str(datetime.now().timestamp())


def generate_random_color() -> QColor:
    """Generates random color"""
    return QColor(randrange(0, 255), randrange(0, 255), randrange(0, 255))


def get_adjusted_rect_point(point: QPoint) -> QPoint:
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


def check_point_on_the_line(point: QPoint, start_point_line: QPoint, end_point_line: QPoint):
    """Checks with threshold whether point on the line or not"""

    if (end_point_line.x() - start_point_line.x()) == 0:
        return False
    elif (end_point_line.y() - start_point_line.y()) == 0:
        return False

    left_part = (point.x() - start_point_line.x()) / (end_point_line.x() - start_point_line.x())
    right_part = (point.y() - start_point_line.y()) / (end_point_line.y() - start_point_line.y())

    return abs(left_part - right_part) < POINT_INTERSECTION_THRESHOLD


def calculate_rect_delta(current_point: QPoint, previous_point: QPoint) -> tuple[int, int]:
    """Calculates rect delta between points"""
    dx = current_point.x() - previous_point.x()
    dy = current_point.y() - previous_point.y()

    return dx, dy


def get_key_of_point(rect_id: str, line: ReferenceLineT) -> Union[Literal["start_point"], Literal["end_point"]]:
    """Defines which key of point should be chosen based on rectangle id"""
    if line["first_rect_id"] == rect_id:
        return "start_point"
    else:
        return "end_point"


def get_query_rect(moving_rect: QRect, dx: int, dy: int) -> Optional[QRect]:
    """
    Defines a rectangle which should be queried to search elements in Quad Tree based on the moving direction

    :param moving_rect: rectangle which moving right now
    :param dx: x coordinate of moving vector of moving_rect
    :param dy: y coordinate of moving vector of moving_rect
    """
    query_rect = None

    if dx >= 0 and dy >= 0:
        query_rect = QRect(moving_rect.x(), moving_rect.y(), moving_rect.width() + dx, moving_rect.height() + dy)
    elif dx >= 0 and dy <= 0:
        query_rect = QRect(moving_rect.x(), moving_rect.y() + dy, moving_rect.width() + dx, moving_rect.height() - dy)
    elif dx <= 0 and dy >= 0:
        query_rect = QRect(moving_rect.x() + dx, moving_rect.y(), moving_rect.width() - dx, moving_rect.height() + dy)
    elif dx <= 0 and dy <= 0:
        query_rect = QRect(moving_rect.x() + dx, moving_rect.y() + dy, moving_rect.width() - dx, moving_rect.height() - dy)

    return query_rect


def calculate_vector_to_intersection_with(
        rects: List[QRect],
        moving_rect: QRect, dx: int, dy: int
) -> Optional[tuple[int, int]]:
    """
    Calculates a vector to where moving_rect can be moved in order to not intersect other rectangles but be placed in
    border-to-border point with other rectangles

    :param rects: list of rectangles which moving_rect can intersect
    :param moving_rect: rectangle which moving right now
    :param dx: x position of moving vector of moving_rect
    :param dy: y position of moving vector of moving_rect
    """
    min_t_entry = float('inf')
    vector = None

    for rect in rects:
        # time to rich intersection with rect by X axis
        tx_entry = float('inf')
        # time to rich intersection with rect by Y axis
        ty_entry = float('inf')

        # time to leave intersection area with rect by X axis
        tx_exit = float('inf')
        # time to leave intersection area with rect by Y axis
        ty_exit = float('inf')

        # calculate times by X axis in accordance with movement direction
        if dx > 0:
            tx_entry = (rect.x() - (moving_rect.x() + moving_rect.width())) / dx
            tx_exit = ((rect.x() + rect.width()) - moving_rect.x()) / dx
        elif dx < 0:
            tx_entry = ((rect.x() + rect.width()) - moving_rect.x()) / dx
            tx_exit = (rect.x() - (moving_rect.x() + moving_rect.width())) / dx

        # calculate times by Y axis in accordance with movement direction
        if dy > 0:
            ty_entry = (rect.y() - (moving_rect.y() + moving_rect.height())) / dy
            ty_exit = ((rect.y() + rect.height()) - moving_rect.y()) / dy
        elif dy < 0:
            ty_entry = ((rect.y() + rect.height()) - moving_rect.y()) / dy
            ty_exit = (rect.y() - (moving_rect.y() + moving_rect.height())) / dy

        # to get actual time when rectangles be intersected we should get maximum of times by axes
        # to be sure that intersection happened on X axis and Y axis
        t_entry = max(tx_entry, ty_entry)

        # to get actual time when moving_rect leaves intersection area with rect
        # we should get minimum of times by axes
        # because once moving_rect leaves intersection area with rect by any axes
        # they wouldn't be intersected at all
        t_exit = min(tx_exit, ty_exit)

        # check that time to intersection between 0 and time leave intersection area
        if 0 <= t_entry <= t_exit:
            if t_entry < min_t_entry:
                # update new time to intersection if it less than previous among founded rectangles
                min_t_entry = t_entry

                # update available distance vector to intersection
                vector = (int(dx * t_entry), int(dy * t_entry))

    return vector
