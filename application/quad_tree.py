from PyQt6.QtCore import QRect


class QuadTreeNode:
    def __init__(self, boundary):
        self.__boundary = boundary
        self.__rects = []
        self.__top_left_tree = None
        self.__top_right_tree = None
        self.__bot_left_tree = None
        self.__bot_right_tree = None
        self.__divided = False

    @property
    def boundary(self):
        return self.__boundary

    def insert(self, rect):
        """Inserts a rectangle into the tree."""
        if not self.__boundary.intersects(rect["rect"]):
            return False

        if not self.__divided:  # while we didn't divide this quad insert into it
            self.__rects.append(rect)

            if len(self.__rects) == 5:  # if this quad have enough rect then divide it
                self.__subdivide()

            return True
        else:  # otherwise dive into all subquads and find better position
            inserted = self.__top_left_tree.insert(rect)
            inserted = self.__top_right_tree.insert(rect) or inserted
            inserted = self.__bot_left_tree.insert(rect) or inserted
            inserted = self.__bot_right_tree.insert(rect) or inserted

            return inserted

    def delete(self, rect):
        """Deletes a rectangle from the tree."""
        if not self.__boundary.intersects(rect["rect"]):
            return

        if rect in self.__rects:
            self.__rects.remove(rect)
            return

        # go through every subquads if they exist
        if self.__top_left_tree:
            self.__top_left_tree.delete(rect)
        if self.__top_right_tree:
            self.__top_right_tree.delete(rect)
        if self.__bot_left_tree:
            self.__bot_left_tree.delete(rect)
        if self.__bot_right_tree:
            self.__bot_right_tree.delete(rect)

    def __subdivide(self):
        """Splits current quad for four subquads and if possible moves to them all rectangles from this quad"""
        x = self.__boundary.x()
        y = self.__boundary.y()
        width = self.__boundary.width()
        height = self.__boundary.height()

        half_width = width / 2
        half_height = height / 2

        # create new subquads
        self.__top_left_tree = QuadTreeNode(QRect(x, y, half_width, half_height))
        self.__top_right_tree = QuadTreeNode(QRect(x + half_width, y, half_width, half_height))
        self.__bot_left_tree = QuadTreeNode(QRect(x, y + half_height, half_width, half_height))
        self.__bot_right_tree = QuadTreeNode(QRect(x + half_width, y + half_height, half_width, half_height))

        self.__divided = True

        # moves rects to subquads
        # we should check all subquads for every rect because one rect can intersect several subquads
        for rect in self.__rects:
            self.__top_left_tree.insert(rect)
            self.__top_right_tree.insert(rect)
            self.__bot_left_tree.insert(rect)
            self.__bot_right_tree.insert(rect)

    def query(self, range_rect):
        """Finds all rectangles which intersect given rectangle"""
        found_rectangles = {}

        if not self.__boundary.intersects(range_rect):
            return found_rectangles

        # check every rectangle on intersection
        for rect in self.__rects:
            if range_rect.intersects(rect["rect"]):
                found_rectangles[rect["id"]] = rect

        # go through all subquads
        if self.__top_left_tree and self.__top_left_tree.boundary.intersects(range_rect):
            found_rectangles.update(self.__top_left_tree.query(range_rect))
        if self.__top_right_tree and self.__top_right_tree.boundary.intersects(range_rect):
            found_rectangles.update(self.__top_right_tree.query(range_rect))
        if self.__bot_left_tree and self.__bot_left_tree.boundary.intersects(range_rect):
            found_rectangles.update(self.__bot_left_tree.query(range_rect))
        if self.__bot_right_tree and self.__bot_right_tree.boundary.intersects(range_rect):
            found_rectangles.update(self.__bot_right_tree.query(range_rect))

        return found_rectangles

    def traverse(self):
        """Traverses a tree and returns all rectangles"""
        rectangles = []

        rectangles.extend(self.__rects)

        if self.__top_left_tree:
            rectangles.extend(self.__top_left_tree.traverse())
        if self.__top_right_tree:
            rectangles.extend(self.__top_right_tree.traverse())
        if self.__bot_left_tree:
            rectangles.extend(self.__bot_left_tree.traverse())
        if self.__bot_right_tree:
            rectangles.extend(self.__bot_right_tree.traverse())

        return rectangles


class QuadTree:
    def __init__(self, boundary):
        self.root = QuadTreeNode(boundary)

    def insert(self, rect):
        return self.root.insert(rect)

    def update(self, rect):
        self.root.delete(rect)
        self.root.insert(rect)

    def query(self, range_rect):
        return list(self.root.query(range_rect).values())

    def traverse(self):
        return self.root.traverse()
