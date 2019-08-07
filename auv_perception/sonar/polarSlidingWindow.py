#!/bin/env python3

from __future__ import division, print_function
from .fractionalPolarAxes import fractional_polar_axes

import matplotlib.pyplot as plt
import matplotlib.cm as cm

import numpy as np
import tempfile

from imageio import imread

from auv_perception.annotation import Rectangle

def neighbors(p, imageSize):
    ret = []

    if p[0] != 0:
        ret.append((p[0] - 1, p[1]))

    if p[1] != 0:
        ret.append((p[0], p[1] - 1))

    if p[0] + 1 < imageSize[0]:
        ret.append((p[0] + 1, p[1]))

    if p[1] + 1 < imageSize[1]:
        ret.append((p[0], p[1] + 1))

    return ret

from collections import deque

"""
Extracts a polar mask from a grayscale image by taking the assumption
that black pixels correspond to mask positions, but only if they are connected,
starting at (0, 0).
"""
def extractPolarMask(image):
    visited = np.zeros(image.shape, dtype = np.uint8)

    queue = deque()
    queue.append((0, 0))

    while len(queue) > 0:
        y, x = queue.popleft()

        #Skip non-black pixels
        if image[y][x] > 0:
            continue

        if visited[y][x] > 0:
            continue

        visited[y][x] = 255

        for neighbor in neighbors((y, x), image.shape):
            if visited[neighbor[0]][neighbor[1]]:
                continue

            queue.append(neighbor)

    return (255 - visited).astype(np.uint8)

"""
Renders a polar mask from a given sonar ranges (in meters) and FOV (in degrees).
The default fov is from an ARIS Explorer 3000.
"""
def renderPolarMask(frameSize, ranges = (0.7, 1.7), fov = (-15, 15)):
    fig = plt.figure()

    frame = np.ones(frameSize)

    theta, r = np.mgrid[fov[0]:fov[1]:(frameSize[0] * 1j), ranges[0]:ranges[1]:(frameSize[1] * 1j)]
    ax = fractional_polar_axes(fig, thlim = fov, rlim = ranges, ticklabels = False)
    im = ax.pcolormesh(theta, r, frame, cmap = cm.Greys_r, shading='flat')

    #This is a hack, savefig can convert the figure to bytes without borders and it is the same
    #method that we use to generate the sonar images in polar coordinates.
    tmpFile = tempfile.SpooledTemporaryFile()

    fig.savefig(tmpFile, format = "png", bbox_inches = 'tight', facecolor = 'white')
    plt.close(fig)

    output = imread(tmpFile, as_gray = True)

    for x in range(output.shape[0]):
        for y in range(output.shape[1]):
            pix = output[x][y]

            if pix > 100:
                output[x][y] = 0
            else:
                output[x][y] = 255

    tmpFile.close()

    return output.astype(np.uint8)


from ..compat import imresize

"""
Runs a sliding window over a polar image, skipping all windows
that fall outside of the polar field of view.
Assumes that the image points up.
Computes all the sliding window rectangles and returns them in a list (list of Rectangle).
The polarMask parameter is a image that defines the polar FOV. This image
contains a 0 in pixels outside the FOV, and a value > 0 (usually 1) inside the FOV.
"""
def polarSlidingWindow(imageSize, windowSize, polarMask, stepSize = 2):
    actualPolarMask = None

    #If polarMask shapes do not match, resize the polar mask
    if polarMask.shape != imageSize:
        actualPolarMask = imresize(polarMask, imageSize, interp = "bilinear")
    else:
        actualPolarMask = polarMask

    windows = []

    xRange = imageSize[0] - windowSize[0]
    yRange = imageSize[1] - windowSize[1]

    for x in range(0, xRange, stepSize):
        for y in range(0, yRange, stepSize):

            #Check if it makes sense to start a window
            #at the current position
            if actualPolarMask[x][y] == 0:
                continue

            windowRect = Rectangle((x, y), windowSize[0], windowSize[1])

            #Check each corner fo the rectangle
            cornerX, cornerY = windowRect.topLeft
            if actualPolarMask[cornerX][cornerY] == 0:
                continue

            cornerX, cornerY = windowRect.topRight
            if actualPolarMask[cornerX][cornerY] == 0:
                continue

            cornerX, cornerY = windowRect.bottomLeft
            if actualPolarMask[cornerX][cornerY] == 0:
                continue

            cornerX, cornerY = windowRect.bottomRight
            if actualPolarMask[cornerX][cornerY] == 0:
                continue

            #And the center, just in case
            cornerX, cornerY = windowRect.center
            if actualPolarMask[cornerX][cornerY] == 0:
                continue

            #Ok, window is inside Sonar's FOV
            windows.append(windowRect)

    return windows
