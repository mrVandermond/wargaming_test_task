from PyQt6.QtCore import QRect


class QuadTreeNodeData:
    def __init__(self, rect, rect_id, data):
        self.__rect = rect
        self.__data = data
        self.__id = rect_id

    @property
    def id(self):
        return self.__id

    @property
    def rect(self):
        return self.__rect

    @property
    def data(self):
        return self.__data


class QuadTreeNode:
    def __init__(self, boundary, capacity):
        self.__boundary = boundary
        self.__node_data_list = []
        self.__top_left_tree = None
        self.__top_right_tree = None
        self.__bot_left_tree = None
        self.__bot_right_tree = None
        self.__divided = False
        self.__capacity = capacity

    @property
    def boundary(self):
        return self.__boundary

    def insert(self, node):
        """Inserts a rectangle into the tree."""
        if not self.__boundary.intersects(node.rect):
            return False

        if not self.__divided:  # while we didn't divide this quad insert into it
            self.__node_data_list.append(node)

            if len(self.__node_data_list) > self.__capacity:  # if this quad have enough rect then divide it
                self.__subdivide()

            return True
        else:  # otherwise dive into all subquads and find better position
            inserted = self.__top_left_tree.insert(node)
            inserted = self.__top_right_tree.insert(node) or inserted
            inserted = self.__bot_left_tree.insert(node) or inserted
            inserted = self.__bot_right_tree.insert(node) or inserted

            return inserted

    def delete(self, node):
        """Deletes a rectangle from the tree."""
        if not self.__boundary.intersects(node.rect):
            return

        if node in self.__node_data_list:
            self.__node_data_list.remove(node)
            return

        # go through every subquads if they exist
        if self.__top_left_tree:
            self.__top_left_tree.delete(node)
        if self.__top_right_tree:
            self.__top_right_tree.delete(node)
        if self.__bot_left_tree:
            self.__bot_left_tree.delete(node)
        if self.__bot_right_tree:
            self.__bot_right_tree.delete(node)

    def __subdivide(self):
        """Splits current quad for four subquads and if possible moves to them all rectangles from this quad"""
        x = self.__boundary.x()
        y = self.__boundary.y()
        width = self.__boundary.width()
        height = self.__boundary.height()

        half_width = width / 2
        half_height = height / 2

        # create new subquads
        self.__top_left_tree = QuadTreeNode(QRect(x, y, half_width, half_height), self.__capacity)
        self.__top_right_tree = QuadTreeNode(QRect(x + half_width, y, half_width, half_height), self.__capacity)
        self.__bot_left_tree = QuadTreeNode(QRect(x, y + half_height, half_width, half_height), self.__capacity)
        self.__bot_right_tree = QuadTreeNode(QRect(x + half_width, y + half_height, half_width, half_height), self.__capacity)

        self.__divided = True

        # moves rects to subquads
        # we should check all subquads for every rect because one rect can intersect several subquads
        for node_data in self.__node_data_list:
            self.__top_left_tree.insert(node_data)
            self.__top_right_tree.insert(node_data)
            self.__bot_left_tree.insert(node_data)
            self.__bot_right_tree.insert(node_data)

    def query(self, range_rect):
        """Finds all rectangles which intersect given rectangle"""
        found_rectangles = {}

        if not self.__boundary.intersects(range_rect):
            return found_rectangles

        # check every rectangle on intersection
        for node_data in self.__node_data_list:
            if range_rect.intersects(node_data.rect):
                found_rectangles[node_data.id] = node_data

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
        """Traverses a tree and returns all node_data"""
        data_list = []

        data_list.extend(self.__node_data_list)

        if self.__top_left_tree:
            data_list.extend(self.__top_left_tree.traverse())
        if self.__top_right_tree:
            data_list.extend(self.__top_right_tree.traverse())
        if self.__bot_left_tree:
            data_list.extend(self.__bot_left_tree.traverse())
        if self.__bot_right_tree:
            data_list.extend(self.__bot_right_tree.traverse())

        return data_list


class QuadTree:
    def __init__(self, boundary, capacity):
        self.root = QuadTreeNode(boundary, capacity)

    def insert(self, rect):
        return self.root.insert(rect)

    def update(self, rect):
        self.root.delete(rect)
        self.root.insert(rect)

    def query(self, range_rect):
        return list(self.root.query(range_rect).values())

    def traverse(self):
        return list(map(lambda n: n.data, self.root.traverse()))
