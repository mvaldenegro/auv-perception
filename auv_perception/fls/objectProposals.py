from auv_perception import *
from ..sonar import extractPolarMask, polarSlidingWindow
from ..annotation import Rectangle
import math
import numpy as np

class ProposalEvaluator:
    def __init__(self):
        self.threshold = 0.0

    def evaluate(self, windowImage):
        raise NotImplementedError()

#Generates scores randomly on [0, 1]. Useful for comparison purposes.
class RandomProposalEvaluator:
    def __init__(self):
        pass

    def evaluate(self, windowImage):
        score = np.random.rand()
        decision = score > self.threshold

        return decision, score

def bestMatch(window, proposalBoxes):
    bestIdx = 0
    bestIoU = -1.0

    if len(proposalBoxes) == 0:
        return 0, 1.0

    for i, sp in enumerate(proposalBoxes):
        cw, score = sp

        iou = window.iou(cw)

        if iou > bestIoU:
            bestIoU = iou
            bestIdx = i

    return bestIdx, bestIoU

def nonMaximumSupression(scoredProposals, iouThreshold = 0.4):
    bestBoxes = []
    allBoxes = []

    for window, score in scoredProposals:

        #If we have no boxes to compare, take the first.
        if len(bestBoxes) == 0:
            bestBoxes.append((window, score))

            continue

        idx, iou = bestMatch(window, bestBoxes)

        #Windows intersect, keep the one with highest score (iou)
        if iou > iouThreshold:
            if bestBoxes[idx][1] < score:
                bestBoxes[idx] = (window, score)

        #If window does not intersect, add it to the list
        else:
            bestBoxes.append((window, score))

    return bestBoxes


def generateProposals(image, proposalEvaluator, minWindowSize = 96, maxWindowSize = 96,
                      scaleFactor = 1.5, aspectRatios = [1.0], stepSize = 8, doNMS = False, nmsThresh = 0.5):
    mask = extractPolarMask(image)
    scoredProposals = []

    for ar in aspectRatios:
        window = (int(math.floor(minWindowSize)), int(math.floor(minWindowSize * ar)))
        scale = 1

        while max(window) <= maxWindowSize:

            candidateWindows = polarSlidingWindow(image.shape, window, mask, stepSize = stepSize)

            proposalCount = 0
            for cw in candidateWindows:

                windowImage = image[cw.left:(cw.right), cw.top:(cw.bottom)]

                decision, score = proposalEvaluator.evaluate(windowImage)

                if decision:
                    scoredProposals.append((cw, score))
                    proposalCount += 1

            #print("{} / (max {}) proposals generated at AR {} scale {} window {}".format(proposalCount, len(candidateWindows), ar, scale, window))

            scale *= scaleFactor
            window = (int(math.floor(minWindowSize * scale)), int(math.floor(minWindowSize * scale * ar)))

    if doNMS:
        scoredProposals = nonMaximumSupression(scoredProposals, nmsThresh)

    return scoredProposals

def generateProposalsMultiThreshold(image, proposalEvaluator, thresholds, minWindowSize = 96, maxWindowSize = 96,
                                    scaleFactor = 1.5, aspectRatios = [1.0], doNMS = False, nmsThresh = 0.5):

    mask = extractPolarMask(image)
    scoredProposals = {}

    for thresh in thresholds:
        scoredProposals[thresh] = []

    for ar in aspectRatios:
        window = (int(math.floor(minWindowSize)), int(math.floor(minWindowSize * ar)))
        scale = 1

        while max(window) <= maxWindowSize:

            candidateWindows = polarSlidingWindow(image.shape, window, mask, stepSize = 8)

            proposalCount = 0
            for cw in candidateWindows:

                windowImage = image[cw.left:(cw.right), cw.top:(cw.bottom)]

                decision, score = proposalEvaluator.evaluate(windowImage)

                for thresh in thresholds:
                    if score > thresh:
                        scoredProposals[thresh].append((cw, score))

            #print("{} / (max {}) proposals generated at AR {} scale {} window {}".format(proposalCount, len(candidateWindows), ar, scale, window))

            scale *= scaleFactor
            window = (int(math.floor(minWindowSize * scale)), int(math.floor(minWindowSize * scale * ar)))

    if doNMS:
        for thresh in thresholds:
            scoredProposals[thresh] = nonMaximumSupression(scoredProposals[thresh], nmsThresh)

    return scoredProposals

"""
Returns (rectangle, score) for each proposal to be scored.
This is intended to be draw as a heatmap.
"""
def denseProposalScores(image, proposalScorer, minWindowSize = 96, maxWindowSize = 96,
                      scaleFactor = 1.5, aspectRatios = [1.0], stride = 8):
    mask = extractPolarMask(image)
    proposals = []

    for ar in aspectRatios:
        window = (int(math.floor(minWindowSize)), int(math.floor(minWindowSize * ar)))
        scale = 1

        while max(window) <= maxWindowSize:

            candidateWindows = polarSlidingWindow(image.shape, window, mask, stepSize = stride)

            proposalCount = 0
            for cw in candidateWindows:

                windowImage = image[cw.left:(cw.right), cw.top:(cw.bottom)]

                score = proposalScorer.score(windowImage)
                adjustedWindow = Rectangle((0, 0), stride, stride)
                adjustedWindow.center = cw.center
                proposals.append((adjustedWindow, score))

            scale *= scaleFactor
            window = (int(math.floor(minWindowSize * scale)), int(math.floor(minWindowSize * scale * ar)))

    return proposals


"""
Generates detections through a sliding window.
For each detection, this method returns a tuple (window, score, class)
"""
def generateSlidingWindowDetections(image, classWindowEvaluator, minWindowSize=96, maxWindowSize=96,
                                    scaleFactor=1.5, aspectRatios=[1.0], stepSize=8, doNMS=False):


    mask = extractPolarMask(image)
    scoredProposals = []

    for ar in aspectRatios:
        window = (int(math.floor(minWindowSize)), int(math.floor(minWindowSize * ar)))
        scale = 1

        while max(window) <= maxWindowSize:

            candidateWindows = polarSlidingWindow(image.shape, window, mask, stepSize=stepSize)

            proposalCount = 0
            for cw in candidateWindows:

                windowImage = image[cw.left:(cw.right), cw.top:(cw.bottom)]

                decision, score, classLabel = classWindowEvaluator.evaluate(windowImage)

                if decision:
                    scoredProposals.append((cw, score, classLabel))
                    proposalCount += 1

            # print("{} / (max {}) proposals generated at AR {} scale {} window {}".format(proposalCount, len(candidateWindows), ar, scale, window))

            scale *= scaleFactor
            window = (int(math.floor(minWindowSize * scale)), int(math.floor(minWindowSize * scale * ar)))

    if doNMS:
        scoredProposals = nonMaximumSupression(scoredProposals)

    return scoredProposals

"""
Generates detections through a sliding window, with multiple score thresholds
This function returns a dictionary, indexed by threshold. Each entry in the dictionary contains a list of detections.
each detection contains a tuple (window, score, class).
"""
def generateSlidingWindowDetectionsMultiThreshold(image, proposalEvaluator, thresholds, minWindowSize=96, maxWindowSize=96,
                                                  scaleFactor=1.5, aspectRatios=[1.0], stepSize=8, doNMS=False):

    mask = extractPolarMask(image)
    scoredProposals = {}

    for thresh in thresholds:
        scoredProposals[thresh] = []

    for ar in aspectRatios:
        window = (int(math.floor(minWindowSize)), int(math.floor(minWindowSize * ar)))
        scale = 1

        while max(window) <= maxWindowSize:

            candidateWindows = polarSlidingWindow(image.shape, window, mask, stepSize = stepSize)

            proposalCount = 0
            for cw in candidateWindows:

                windowImage = image[cw.left:(cw.right), cw.top:(cw.bottom)]

                decision, score, classLabel = proposalEvaluator.evaluate(windowImage)

                for thresh in thresholds:
                    if score > thresh:
                        scoredProposals[thresh].append((cw, score, classLabel))

            # print("{} / (max {}) proposals generated at AR {} scale {} window {}".format(proposalCount, len(candidateWindows), ar, scale, window))

            scale *= scaleFactor
            window = (int(math.floor(minWindowSize * scale)), int(math.floor(minWindowSize * scale * ar)))

    return scoredProposals

"""
Generates detection proposals from a objectness map generated by a FCN.
"""
def generateObjectnessMapDetections(image, objectnessMap, threshold = 0.5, stepSize = 8, windowSize = 96):
    mask = extractPolarMask(image)
    candidateWindows = polarSlidingWindow(image.shape, (windowSize, windowSize), mask, stepSize = stepSize)

    proposals = []

    for cw in candidateWindows:
        x, y = cw.center

        if objectnessMap[x, y] >= threshold:
            proposals.append((cw, objectnessMap[x, y]))

    return proposals

def generateObjectnessMapDetectionsMultiThreshold(image, objectnessMap, thresholds, stepSize = 8,
                                                  windowSize = 96, doNMS = False, nmsThresh = 0.5):

    mask = extractPolarMask(image)
    candidateWindows = polarSlidingWindow(image.shape, (windowSize, windowSize), mask, stepSize = stepSize)

    scoredProposals = {}

    for thresh in thresholds:
        scoredProposals[thresh] = []

    for cw in candidateWindows:
        x, y = cw.center
        objectness = objectnessMap[x, y]

        for thresh in thresholds:
            if objectness >= thresh:
                scoredProposals[thresh].append((cw, objectness))

    if doNMS:
        for thresh in thresholds:
            scoredProposals[thresh] = nonMaximumSupression(scoredProposals[thresh], nmsThresh)

    return scoredProposals
