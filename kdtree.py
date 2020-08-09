#!/usr/bin/python
# encoding: utf-8
""" KDTree implementation.
Features:
- nearest neighbours search
Matej Drame [matej.drame@gmail.com]
"""
__version__ = "1r11.1.2010"
__all__ = ["KDTree"]

from dataclasses import dataclass


def square_distance(point_a, point_b):
    """ squared euclidean distance """
    dimensions = len(point_a)  # assumes both points have the same dimensions
    return sum(
        (point_a[dimension] - point_b[dimension]) ** 2
        for dimension in range(dimensions)
    )


@dataclass
class KDTreeNode:
    """this is a class, plylint"""
    point = tuple
    left = tuple
    right = tuple


class KDTreeNeighbours:
    """ Internal structure used in nearest-neighbours search.  """
    def __init__(self, query_point, neighbors):
        self.query_point = query_point
        self.neighbors = neighbors  # neighbours wanted
        self.largest_distance = 0  # squared
        self.current_best = []

    def calculate_largest(self):
        """ looks like a fancy way to do max()"""
        if self.neighbors >= len(self.current_best):
            self.largest_distance = self.current_best[-1][1]
        else:
            self.largest_distance = self.current_best[self.neighbors - 1][1]

    def add(self, point):
        """ run through current_best, try to find appropriate place """
        s_d = square_distance(point, self.query_point)

        for i, best in enumerate(self.current_best):
            if i == self.neighbors:
                return
            if best[1] > s_d:
                self.current_best.insert(i, [point, s_d])
                self.calculate_largest()
                return
        # append it to the end otherwise
        self.current_best.append([point, s_d])
        self.calculate_largest()

    def get_best(self):
        """here we're reinventing the wheel again i think"""
        return [element[0] for element in self.current_best[:self.neighbors]]


class KDTree:
    """ KDTree implementation.
        Example usage:
            from kdtree import KDTree
            data = <load data> # iterable of points (which are also iterable,
            same length) point = <the point of which neighbours we're looking
            for> tree = KDTree.construct_from_data(data)
            nearest = tree.query(point, t=4) # find nearest 4 points
    """
    def __init__(self, data):
        """ yup, it's an init function alright."""
        def build_kdtree(point_list, depth):
            """ let's build a tree!"""
            if not point_list:
                return None
            axis = depth % len(point_list[0])
            # sort point list and choose median as pivot point,
            point_list.sort(key=lambda point: point[axis])
            median = int(round(len(point_list)/2))  # choose median
            # create node and recursively construct subtrees
            node = KDTreeNode()
            node.point = point_list[median]
            node.left = build_kdtree(point_list[0:median], depth+1)
            node.right = build_kdtree(point_list[median+1:], depth+1)
            return node
        self.root_node = build_kdtree(data, depth=0)

    @staticmethod
    def construct_from_data(data):
        """ let's build a differnt kind of tree! """
        return KDTree(data)

    def query(self, query_point, neighbors=1):
        """ raise your hand if you have a question"""
        def nn_search(node, kd_query_point, points, depth, best_neighbours):
            """ i love the way he defines a function as the first line
            of another function"""
            if node is None:
                return

            if node.left is None and node.right is None:
                best_neighbours.add(node.point)
                return
            # this node is no leaf
            # select dimension for comparison (based on current depth)
            axis = depth % len(kd_query_point)

            if kd_query_point[axis] < node.point[axis]:
                near_subtree = node.left
                far_subtree = node.right
            else:
                near_subtree = node.right
                far_subtree = node.left
            # recursively search through the tree until a leaf is found
            nn_search(near_subtree, kd_query_point, points, depth + 1,
                      best_neighbours)
            # while unwinding the recursion, check if the current node
            # is closer to query point than the current best,
            # also, until t points have been found, search radius is infinity
            best_neighbours.add(node.point)
            if (node.point[axis] - kd_query_point[axis])**2 <= \
                    best_neighbours.largest_distance:
                nn_search(far_subtree, kd_query_point, points, depth + 1,
                          best_neighbours)
            return
        # if there's no tree, there's no neighbors
        if self.root_node is not None:
            neighbours = KDTreeNeighbours(query_point, neighbors)
            nn_search(self.root_node, query_point, neighbors, depth=0,
                      best_neighbours=neighbours)
            result = neighbours.get_best()
        else:
            result = []
        return result
