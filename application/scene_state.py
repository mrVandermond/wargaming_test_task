from PyQt6.QtCore import Qt, QPoint, QRect

import utils

from constants import WINDOW_HEIGHT, WINDOW_WIDTH, RECT_HEIGHT, RECT_WIDTH
from quad_tree import QuadTree
from enums import ActionType


class SceneState:
    def __init__(self):
        # map of all reference lines between rectangles
        # key -> line id
        # value -> dictionary with line's data
        self.__reference_lines = {}

        # map of links between reference lines and rectangles
        # key -> rectangle id
        # value -> list of related line id
        self.__rectangle_refs = {}

        # line id used in process of creating new line
        self.__current_line_id = None

        # action type of current process
        self.__current_action = None

        # rect used in process of dragging rect
        self.__current_rect = None

        self.__qtree = QuadTree(QRect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))

    @property
    def rectangles(self):
        return self.__qtree.traverse()

    @property
    def reference_lines(self):
        return self.__reference_lines

    @property
    def current_action(self):
        return self.__current_action

    def start_creating_ref_line(self, event_point):
        """Initiates a process of creating the reference line"""
        found_rects = self.__qtree.query(QRect(event_point.x(), event_point.y(), 1, 1))

        # check that only one rectangle under current event_point
        if len(found_rects) == 0 or len(found_rects) > 1:
            return

        rect = found_rects[0]
        line_id = utils.generate_random_id()
        self.__reference_lines[line_id] = {
            "id": line_id,
            "first_rect_id": rect["id"],
            "second_rect_id": None,
            "start_point": event_point,
            "end_point": event_point,
        }
        self.__current_line_id = line_id

    def move_end_point_ref_line(self, event_point):
        """Moves end point of current line while line has not linked with second rectangle"""
        if self.__current_line_id is None:
            return

        line = self.__reference_lines[self.__current_line_id]
        line["end_point"] = event_point

    def finish_creating_ref_line(self, event_point):
        """Finishes the process of creating the reference line"""
        rects = self.__qtree.query(QRect(event_point.x(), event_point.y(), 1, 1))
        rects_count = len(rects)
        line = self.__reference_lines[self.__current_line_id]

        # if under current event_point have no rects
        # or there are more than 1 rect
        # or rect only one and this is first rect of the line
        if rects_count == 0 or rects_count > 1 or rects[0]["id"] == line["first_rect_id"]:
            self.__reference_lines.pop(self.__current_line_id)
        else:
            # otherwise finish filling references between rectangles and lines
            rect_id = rects[0]["id"]
            self.__reference_lines[self.__current_line_id]["second_rect_id"] = rect_id
            self.__rectangle_refs[rect_id].append(self.__current_line_id)
            self.__rectangle_refs[line["first_rect_id"]].append(self.__current_line_id)

    def delete_ref_line(self, point):
        """Deletes the reference line under the point"""
        for line in self.__reference_lines.values():
            if utils.check_point_on_the_line(point, line["start_point"], line["end_point"]):
                self.__rectangle_refs[line["first_rect_id"]].remove(line["id"])
                self.__rectangle_refs[line["second_rect_id"]].remove(line["id"])
                self.__reference_lines.pop(line["id"])
                break

    def create_rect(self, event_point):
        """Creates a rectangle"""
        adjusted_point = utils.get_adjusted_rect_point(event_point)
        rectangles = self.__qtree.query(QRect(adjusted_point.x(), adjusted_point.y(), RECT_WIDTH, RECT_HEIGHT))

        # check that there is no intersections with other rectangles
        if len(rectangles) != 0:
            return

        rect_id = utils.generate_random_id()
        self.__qtree.insert({
            "id": rect_id,
            "rect": QRect(adjusted_point.x(), adjusted_point.y(), RECT_WIDTH, RECT_HEIGHT),
            "color": utils.generate_random_color(),
        })
        self.__rectangle_refs[rect_id] = []

    def start_drag_rect(self, event_point):
        """Initiates a process of dragging the rectangle under the event_point"""
        found_rects = self.__qtree.query(QRect(event_point.x(), event_point.y(), 1, 1))

        if len(found_rects) == 1:
            self.__current_rect = found_rects[0]

    def drag_rect(self, event_point):
        """Drags current rectangle to the adjusted_point if possible"""
        if self.__current_rect is None or self.__current_action != ActionType.DRAG_RECT:
            return

        rect_obj = self.__current_rect
        rect = rect_obj["rect"]

        adjusted_point = utils.get_adjusted_rect_point(event_point)
        dx, dy = utils.calculate_rect_delta(adjusted_point, QPoint(rect.x(), rect.y()))

        query_rect = utils.get_query_rect(rect, dx, dy)

        if query_rect is None:
            return

        rects = self.__qtree.query(query_rect)

        # remove current rect if it includes into intersected rectangles
        if rect_obj in rects:
            rects.remove(rect_obj)

        # check there are no intersected rectangles in the new point
        if len(rects) != 0:
            rectangles = list(map(lambda r: r["rect"], rects))
            vector = utils.calculate_vector_to_intersection_with(rectangles, rect, dx, dy)

            # if we cannot find a better position just do nothing in that case
            if vector is None:
                return

            # move adjusted point right to the last available point before intersection with nearest rectangles
            adjusted_point = QPoint(rect.x() + vector[0], rect.y() + vector[1])
            # recalculate dx and dy used for movement of reference lines
            dx, dy = utils.calculate_rect_delta(adjusted_point, QPoint(rect.x(), rect.y()))

        # move all reference lines related to current rectangle
        for line_id in self.__rectangle_refs[rect_obj["id"]]:
            line = self.__reference_lines[line_id]
            point_key = utils.get_key_of_point(rect_obj["id"], line)
            line[point_key].setX(line[point_key].x() + dx)
            line[point_key].setY(line[point_key].y() + dy)

        rect.moveTo(adjusted_point)

    def finish_drag_rect(self):
        """Finishes the process of dragging the current rectangle"""
        if self.__current_rect is None:
            return

        # update rect position into queue
        self.__qtree.update(self.__current_rect)

    def set_current_action(self, event):
        """Defines current action by event"""
        button = event.button().value
        is_control_pressed = event.modifiers() == Qt.KeyboardModifier.ControlModifier

        if button == Qt.MouseButton.LeftButton.value and is_control_pressed:
            self.__current_action = ActionType.DELETE_REF_LINE
            return

        if button == Qt.MouseButton.LeftButton.value:
            self.__current_action = ActionType.DRAG_RECT
            return

        if button == Qt.MouseButton.RightButton.value:
            self.__current_action = ActionType.CREATE_REF_LINE
            return

    def reset_temporal_data(self):
        """Resets temporal data used in processes of dragging or moving objects"""
        self.__current_action = None
        self.__current_line_id = None
        self.__current_rect = None
