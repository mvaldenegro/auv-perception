from __future__ import division, print_function

import numpy as np

"""
Computes the best matching rectangle for a ground truth rectangle
"""
def bestMatch(proposal, groundTruth):
    bestIoU = -1.0
    bestMatch = None

    for gtRect in groundTruth:
        candidateIoU = proposal.iou(gtRect)

        if candidateIoU > bestIoU:
            bestIoU = candidateIoU
            bestMatch = proposal

    return bestMatch, bestIoU

"""
Computes recall given a set of proposals and ground truth rectangles.
"""
def computeRecall(proposals, groundTruth, iouThreshold = 0.5):
    matches = 0

    if len(groundTruth) == 0:
        return 1.0

    bestMatches = []
    matchIoU = []

    for gt in groundTruth:
        p, iou = bestMatch(gt, proposals)

        if iou > iouThreshold:
            bestMatches.append(1.0)
        else:
            bestMatches.append(0.0)

        matchIoU.append(iou)

    return np.mean(bestMatches), matchIoU
