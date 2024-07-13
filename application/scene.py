from PyQt6.QtCore import Qt, QPoint, QRect

import utils

from constants import RECT_HEIGHT, RECT_WIDTH, QTREE_NODE_CAPACITY
from quad_tree import QuadTree, QuadTreeNodeData
from enums import ActionType


class Scene:
    """Class which implements core logic of movement and storing rectangles and their reference lines"""
    def __init__(self, width, height):
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

        # rect data used in process of dragging rect
        self.__current_rect_data = None

        self.__qtree = QuadTree(QRect(0, 0, width, height), QTREE_NODE_CAPACITY)

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
        data_list = self.__qtree.query(QRect(event_point.x(), event_point.y(), 1, 1))

        # check that only one rectangle under current event_point
        if len(data_list) == 0 or len(data_list) > 1:
            return

        data = data_list[0].data
        line_id = utils.generate_random_id()
        self.__reference_lines[line_id] = {
            "id": line_id,
            "first_rect_id": data["id"],
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
        data_list = self.__qtree.query(QRect(event_point.x(), event_point.y(), 1, 1))
        count = len(data_list)
        line = self.__reference_lines[self.__current_line_id]

        # if under current event_point have no rects
        # or there are more than 1 rect
        # or rect only one and this is first rect of the line
        if count == 0 or count > 1 or data_list[0].data["id"] == line["first_rect_id"]:
            self.__reference_lines.pop(self.__current_line_id)
        else:
            # otherwise finish filling references between rectangles and lines
            rect_id = data_list[0].data["id"]
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
        data_list = self.__qtree.query(QRect(adjusted_point.x(), adjusted_point.y(), RECT_WIDTH, RECT_HEIGHT))

        # check that there is no intersections with other rectangles
        if len(data_list) != 0:
            return

        rect_id = utils.generate_random_id()
        rect = QRect(adjusted_point.x(), adjusted_point.y(), RECT_WIDTH, RECT_HEIGHT)
        node_data = QuadTreeNodeData(rect, rect_id, {
            "id": rect_id,
            "rect": rect,
            "color": utils.generate_random_color(),
        })
        self.__qtree.insert(node_data)
        self.__rectangle_refs[rect_id] = []

    def start_drag_rect(self, event_point):
        """Initiates a process of dragging the rectangle under the event_point"""
        data_list = self.__qtree.query(QRect(event_point.x(), event_point.y(), 1, 1))

        if len(data_list) == 1:
            self.__current_rect_data = data_list[0]

    def drag_rect(self, event_point):
        """Drags current rectangle to the adjusted_point if possible"""
        if self.__current_rect_data is None or self.__current_action != ActionType.DRAG_RECT:
            return

        rect_data = self.__current_rect_data
        rect = rect_data.data["rect"]

        adjusted_point = utils.get_adjusted_rect_point(event_point)
        dx, dy = utils.calculate_rect_delta(adjusted_point, QPoint(rect.x(), rect.y()))

        query_rect = utils.get_query_rect(rect, dx, dy)

        if query_rect is None:
            return

        data_list = self.__qtree.query(query_rect)

        # remove current rect if it includes into intersected rectangles
        if rect_data in data_list:
            data_list.remove(rect_data)

        # check there are no intersected rectangles in the new point
        if len(data_list) != 0:
            rectangles = list(map(lambda r: r.data["rect"], data_list))
            vector = utils.calculate_vector_to_intersection_with(rectangles, rect, dx, dy)

            # if we cannot find a better position just do nothing in that case
            if vector is None:
                return

            # move adjusted point right to the last available point before intersection with nearest rectangles
            adjusted_point = QPoint(rect.x() + vector[0], rect.y() + vector[1])
            # recalculate dx and dy used for movement of reference lines
            dx, dy = utils.calculate_rect_delta(adjusted_point, QPoint(rect.x(), rect.y()))

        # move all reference lines related to current rectangle
        for line_id in self.__rectangle_refs[rect_data.data["id"]]:
            line = self.__reference_lines[line_id]
            point_key = utils.get_key_of_point(rect_data.data["id"], line)
            line[point_key].setX(line[point_key].x() + dx)
            line[point_key].setY(line[point_key].y() + dy)

        rect.moveTo(adjusted_point)

    def finish_drag_rect(self):
        """Finishes the process of dragging the current rectangle"""
        if self.__current_rect_data is None:
            return

        # update rect position into tree
        self.__qtree.update(self.__current_rect_data)

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
        self.__current_rect_data = None
