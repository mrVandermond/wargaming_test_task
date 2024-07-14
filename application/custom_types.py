from typing import TypedDict, Optional, TypeVar

from PyQt6.QtCore import QPoint, QRect
from PyQt6.QtGui import QColor


class ReferenceLineT(TypedDict):
    id: str
    first_rect_id: Optional[str]
    second_rect_id: Optional[str]
    start_point: Optional[QPoint]
    end_point: Optional[QPoint]


class RectDataT(TypedDict):
    id: str
    rect: QRect
    color: QColor


QuadTreeDataT = TypeVar("QuadTreeDataT")
QuadTreeNodeT = TypeVar("QuadTreeNodeT")
QuadTreeNodeDataT = TypeVar("QuadTreeNodeDataT")
