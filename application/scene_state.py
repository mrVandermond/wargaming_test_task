from PyQt6.QtCore import Qt, QPoint

import utils

from enums import ActionEnum


class SceneState:
    def __init__(self):
        self.__rectangles = []
        self.__reference_lines = {}

        self.__current_draggable_rect_index = -1
        self.__current_ref_line_id = None

        self.__current_action = None

    @property
    def rectangles(self):
        return self.__rectangles

    @property
    def reference_lines(self):
        return self.__reference_lines

    @property
    def current_action(self):
        return self.__current_action

    def start_creating_ref_line(self, event_point):
        rect_index = utils.find_rect_under_point(event_point, self.__rectangles)

        if rect_index == -1:
            return

        line_id = utils.generate_random_id()
        self.__reference_lines[line_id] = {
            "line_id": line_id,
            "left_rect_index": rect_index,
            "right_rect_index": None,
            "start_point": event_point,
            "end_point": event_point,
        }
        self.__current_ref_line_id = line_id

    def move_end_point_ref_line(self, event_point):
        if self.__current_ref_line_id is None:
            return

        line = self.__reference_lines[self.__current_ref_line_id]
        line["end_point"] = event_point

    def end_creating_ref_line(self, event_point):
        rect_index = utils.find_rect_under_point(event_point, self.__rectangles)
        line = self.__reference_lines[self.__current_ref_line_id]

        if rect_index == -1 or rect_index == line["left_rect_index"]:
            self.__reference_lines.pop(self.__current_ref_line_id)
        else:
            self.__reference_lines[self.__current_ref_line_id]["right_rect_index"] = rect_index
            self.__rectangles[line["left_rect_index"]]["refs"].append(self.__current_ref_line_id)
            self.__rectangles[rect_index]["refs"].append(self.__current_ref_line_id)

    def delete_ref_line(self, point):
        for line in self.__reference_lines.values():
            if utils.check_point_on_the_line(point, line["start_point"], line["end_point"]):
                left_rect = self.__rectangles[line["left_rect_index"]]
                right_rect = self.__rectangles[line["right_rect_index"]]

                left_rect["refs"] = utils.remove_reference_line_link(line["line_id"], left_rect["refs"])
                right_rect["refs"] = utils.remove_reference_line_link(line["line_id"], right_rect["refs"])

                self.__reference_lines.pop(line["line_id"])
                break

    def create_rect(self, event_point):
        point = utils.get_adjusted_rect_point(event_point)

        if utils.has_neighbour_rects_in_point(point, self.__rectangles, self.__current_draggable_rect_index):
            return

        self.__rectangles.append({
            "rect": utils.create_rect(event_point),
            "color": utils.generate_random_color(),
            "refs": [],
        })

    def start_drag_rect(self, event_point):
        self.__current_draggable_rect_index = utils.find_rect_under_point(event_point, self.__rectangles)

    def drag_rect(self, event_point):
        if self.__current_draggable_rect_index == -1:
            return

        rect_obj = self.__rectangles[self.__current_draggable_rect_index]
        rect = rect_obj["rect"]

        adjusted_point = utils.get_adjusted_rect_point(event_point)

        if not utils.has_neighbour_rects_in_point(adjusted_point, self.__rectangles, self.__current_draggable_rect_index):
            dx, dy = utils.calculate_rect_delta(adjusted_point, QPoint(rect.x(), rect.y()))

            for line_id in rect_obj["refs"]:
                line = self.__reference_lines[line_id]
                point_key = utils.get_key_of_point(self.__current_draggable_rect_index, line)
                line[point_key].setX(line[point_key].x() + dx)
                line[point_key].setY(line[point_key].y() + dy)

            rect.moveTo(adjusted_point)

    def set_current_action(self, event):
        button = event.button().value
        is_control_pressed = event.modifiers() == Qt.KeyboardModifier.ControlModifier

        if button == Qt.MouseButton.LeftButton.value and is_control_pressed:
            self.__current_action = ActionEnum.DELETE_REF_LINE
            return

        if button == Qt.MouseButton.LeftButton.value:
            self.__current_action = ActionEnum.DRAG_RECT
            return

        if button == Qt.MouseButton.RightButton.value:
            self.__current_action = ActionEnum.CREATE_REF_LINE
            return

    def reset_temporal_state(self):
        self.__current_action = None
        self.__current_draggable_rect_index = -1
        self.__current_ref_line_id = None
