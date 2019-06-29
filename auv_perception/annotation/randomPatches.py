#!/bin/env python3

from __future__ import division, print_function

from PyQt5.QtCore import QCoreApplication, QDir, QRect, QSize, QPoint
from PyQt5.QtGui import QImage

import numpy as np
import argparse

import h5py, sys

#Normalized coordinates of the sonar data in the image
#This area has a fan shape due to the polar nature of the sensor
VALID_AREA_TOP_LEFT = (0.025, 0.31)
VALID_AREA_TOP_RIGHT = (0.88, 0.04)
VALID_AREA_BOTTOM_LEFT = (0.025, 1.0 - VALID_AREA_TOP_LEFT[1])
VALID_AREA_BOTTOM_RIGHT = (0.88, 1.0 - VALID_AREA_TOP_RIGHT[1])

class Line:
    def __init__(self, pointA, pointB):
        self.slope = (pointA[1] - pointB[1]) / (pointA[0] - pointB[0])
        self.intercept = pointA[1] - self.slope * pointA[0]

    """Returns 'A' if the point is above the line, 'B' is the point is below the line
    and 'O' if the point lies in the line, to some specified precision eps."""
    def testPoint(self, point, eps = 1e-4):
        distanceToLine = self.slope * point[0] + self.intercept - point[1]

        if(abs(distanceToLine) < eps):
            return 'O'

        if distanceToLine > 0:
            return 'A'

        return 'B'

topLine = Line(VALID_AREA_TOP_LEFT, VALID_AREA_TOP_RIGHT)
bottomLine = Line(VALID_AREA_BOTTOM_LEFT, VALID_AREA_BOTTOM_RIGHT)

def rectangleInsideValidArea(rect):

    for point in rect:
        if topLine.testPoint(point) != 'B':
            return False

        if bottomLine.testPoint(point) != 'A':
            return False

        if point[0] < VALID_AREA_TOP_LEFT[0]:
            return False

        if point[0] > VALID_AREA_TOP_RIGHT[0]:
            return False

    return True

def generateRandomRectangle(imageRect, patchSize = (32, 32)):
    while(True):
        x = np.random.uniform()
        y = np.random.uniform()

        halfRectX = patchSize[0] / (2.0 * imageRect[0])
        halfRectY = patchSize[1] / (2.0 * imageRect[1])
        normRect = [(x - halfRectX, y - halfRectY), (x + halfRectX, y + halfRectY),
                    (x - halfRectX, y + halfRectY), (x + halfRectX, y - halfRectY)]

        if rectangleInsideValidArea(normRect):
            rect = QRect(QPoint(0, 0), QSize(patchSize[0], patchSize[1]))
            rect.moveCenter(QPoint(x * imageRect[0], y * imageRect[1]))

            return rect
