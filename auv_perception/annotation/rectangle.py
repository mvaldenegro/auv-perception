#!/bin/env python3

from __future__ import division, print_function

"""
An object representing a rectangle in cartesian coordinates.
A rectangle is defined by a top left point and a given width and height.
"""
class Rectangle:
    def __init__(self, topLeft, width, height):

        if width < 0:
            raise ValueError("Width cannot be negative")

        if height < 0:
            raise ValueError("Height cannot be negative")

        self.topLeft = topLeft
        self.size = (int(width), int(height))

    def __str__(self):
        return "Rectangle({}, {}, {})".format(self.topLeft, self.width, self.height)

    @property
    def isValid(self):
        return self.width != 0 and self.height != 0

    @property
    def width(self):
        return self.size[0]

    @width.setter
    def width(self, w):
        self.size = (w, self.height)

    @property
    def height(self):
        return self.size[1]

    @height.setter
    def height(self, h):
        self.size = (self.width, h)

    @property
    def center(self):
        return (self.topLeft[0] + self.width // 2, self.topLeft[1] + self.height // 2)

    @center.setter
    def center(self, c):
        self.topLeft = (c[0] - self.width // 2, c[1] - self.height // 2)

    @property
    def topRight(self):
        return (self.topLeft[0] + self.width, self.topLeft[1])

    @property
    def bottomRight(self):
        return (self.topLeft[0] + self.width, self.topLeft[1] + self.height)

    @property
    def bottomLeft(self):
        return (self.topLeft[0], self.topLeft[1] + self.height)
    
    @property
    def left(self):
        return self.topLeft[0]
    
    @property
    def right(self):
        return self.left + self.width
    
    @property
    def top(self):
        return self.topLeft[1]
    
    @property
    def bottom(self):
        return self.top + self.height

    @property
    def area(self):
        return self.width * self.height
    
    def union(self, otherRectangle):
        l = min(self.left, otherRectangle.left)
        t = min(self.top, otherRectangle.top)
        
        r = max(self.right, otherRectangle.right)
        b = max(self.bottom, otherRectangle.bottom)
        
        return Rectangle.fromPoint(topLeft = (l, t), bottomRight = (r, b))
    
    def intersection(self, otherRectangle):
        l = max(self.left, otherRectangle.left)
        t = max(self.top, otherRectangle.top)
        
        r = min(self.right, otherRectangle.right)
        b = min(self.bottom, otherRectangle.bottom)
        
        if l > r or t > b:
            return Rectangle(topLeft = (t, l), width = 0, height = 0)
        
        return Rectangle.fromPoint(topLeft = (l, t), bottomRight = (r, b))
    
    def iou(self, otherRectangle):
        return float(self.intersection(otherRectangle).area) / float(self.union(otherRectangle).area)
    
    def containsPoint(self, point):
        if point[0] < self.left or point[0] > self.right:
            return False
        
        if point[1] < self.top or point[1] > self.bottom:
            return False
        
        return True
    
    @staticmethod
    def fromPoint(topLeft, bottomRight):
        return Rectangle(topLeft, bottomRight[0] - topLeft[0], bottomRight[1] - topLeft[1])

    @staticmethod
    def fromCenter(center, width, height):
        r = Rectangle((0, 0), width, height)
        r.center = center

        return r

    @staticmethod
    def fromQRectF(qrectf):
        topLeft = (int(qrectf.topLeft().y()), int(qrectf.topLeft().x()))
        return Rectangle(topLeft, int(qrectf.width()), int(qrectf.height()))