from utilities.random_util import RandomUtil
from typing import NamedTuple, Callable, List
import math
import numpy as np

Point = NamedTuple("Point", x=int, y=int)

class Rectangle:
    def __init__(self, left: int, top: int, width: int, height: int, offset: Point = (0, 0)):
        '''
        Defines a rectangle area on screen.
        Args:
            left: The leftmost x coordinate of the rectangle.
            top: The topmost y coordinate of the rectangle.
            width: The width of the rectangle.
            height: The height of the rectangle.
            offset: The offset to apply to the rectangle.
        Returns:
            A Rectangle object.
        '''
        self.left = left + offset[0]
        self.top = top + offset[1]
        self.width = width
        self.height = height
    
    @classmethod
    def from_points(cls, start_point: Point, end_point: Point, offset: Point = Point(0, 0)):
        '''
        Creates a Rectangle from two points.
        Args:
            start_point: The first point.
            end_point: The second point.
        Returns:
            A Rectangle object.
        '''
        start_point = Point(start_point.x + offset.x, start_point.y + offset.y)
        end_point = Point(end_point.x + offset.x, end_point.y + offset.y)
        return cls(start_point.x, start_point.y, end_point.x - start_point.x, end_point.y - start_point.y)

    def get_center(self) -> Point:
        '''
        Gets the center point of the rectangle.
        Returns:
            A Point representing the center of the rectangle.
        '''
        return Point(self.left + self.width // 2, self.top + self.height // 2)

    def get_top_left(self) -> Point:
        '''
        Gets the top left point of the rectangle.
        Returns:
            A Point representing the top left of the rectangle.
        '''
        return Point(self.left, self.top)

    def get_top_right(self) -> Point:
        '''
        Gets the top right point of the rectangle.
        Returns:
            A Point representing the top right of the rectangle.
        '''
        return Point(self.left + self.width, self.top)

    def get_bottom_left(self) -> Point:
        '''
        Gets the bottom left point of the rectangle.
        Returns:
            A Point representing the bottom left of the rectangle.
        '''
        return Point(self.left, self.top + self.height)

    def get_bottom_right(self) -> Point:
        '''
        Gets the bottom right point of the rectangle.
        Returns:
            A Point representing the bottom right of the rectangle.
        '''
        return Point(self.left + self.width, self.top + self.height)

    def to_dict(self):
        return {
            "left": self.left,
            "top": self.top,
            "width": self.width,
            "height": self.height
        }

    def __str__(self):
        return f"Rectangle(x={self.left}, y={self.top}, w={self.width}, h={self.height})"

    def __repr__(self):
        return self.__str__()


class RuneLiteObject:

    rect_ref = None

    def __init__(self, x_min, x_max, y_min, y_max, width, height, center, axis):
        '''
        Represents an outlined object on screen.
        Args:
            x_min, x_max: The min/max x coordinates of the object.
            y_min, y_max: The min/max y coordinates of the object.
            width: The width of the object.
            height: The height of the object.
            center: The center of the object.
            axis: A 2-column stacked array of points that make up the object.
        '''
        self._x_min = x_min
        self._x_max = x_max
        self._y_min = y_min
        self._y_max = y_max
        self._width = width
        self._height = height
        self._center = center
        self._axis = axis
    
    def set_rectangle_reference(self, rect_function: Callable):
        '''
        Sets the rectangle reference of the object.
        Args:
            rect_function: A reference to the function used to get info for the rectangle
                           that this object belongs in (E.g., Bot.win.rect_game_view).
        '''
        self.rect_ref = rect_function
        
    def center(self) -> Point:  # sourcery skip: raise-specific-error
        '''
        Gets the center of the object relative to the client.
        Returns:
            A Point.
        '''
        if self.rect_ref is None:
            raise Exception("Rectangle reference not set for object.")
        rect: Rectangle = self.rect_ref()
        return Point(self._center[0] + rect.left, self._center[1] + rect.top)

    def distance_from_rect_center(self) -> float:
        '''
        Gets the distance between the object and it's Rectangle parent center.
        Useful for sorting lists of RuneLiteObjects.
        Returns:
            The distance from the point to the center of the object.
        '''
        center: Point = self.center()
        rect: Rectangle = self.rect_ref()
        rect_center: Point = rect.get_center()
        return math.dist([center.x, center.y], [rect_center.x, rect_center.y])

    def random_point(self, custom_seeds: List[List[int]]=None) -> Point:
        '''
        Gets a random point within the object.
        Args:
            custom_seeds: A list of custom seeds to use for the random point. You can generate
                          a seeds list using RandomUtil's random_seeds() function with args.
                          Default: A random seed list based on current date and object position.
        Returns:
            A random Point within the object.
        '''
        if custom_seeds is None:
            custom_seeds = RandomUtil.random_seeds(mod=(self._center[0] + self._center[1]))
        # TODO make it return the point relative to the window - right now it's just relative to the image
        x, y = RandomUtil.random_point_in(self._x_min, self._y_min, self._width, self._height, custom_seeds)
        return self.__relative_point([x, y]) if self.__point_exists([x, y]) else self.center()

    def __relative_point(self, point: List[int]) -> Point:
        '''
        Gets a point relative to the object's container (and thus, the client window).
        Args:
            point: The point to get relative to the object in the format [x, y].
        Returns:
            A Point relative to the client window.
        '''
        rect: Rectangle = self.rect_ref()
        return Point(point[0] + rect.left, point[1] + rect.top)

    def __point_exists(self, p: list) -> bool:
        '''
        Checks if a point exists in the object.
        Args:
            p: The point to check in the format [x, y].
        '''
        return (self._axis == np.array(p)).all(axis=1).any()
