#!/usr/bin/env python3

from PyQt5.QtCore import QTimer, Qt, QSize
from PyQt5.QtGui import QImage, QPainter, QPixmap, qRgba, QBrush, QColor, QPen

def paintColorProposalScoreHeatmap(imageFileName, scoredProposals):
    outputImage = QImage(imageFileName)
    outputImage = outputImage.convertToFormat(QImage.Format_ARGB32)

    p = QPainter()
    p.begin(outputImage)
    p.setBrush(Qt.SolidPattern)
    #p.setPen(Qt.red)

    for window, score in scoredProposals:
        brush = QBrush(QColor(int(255 * score), 0, int(255 * (1.0 - score)), 75 ), Qt.SolidPattern)
        p.setBrush(brush)
        p.setPen(QPen(Qt.NoPen))
        p.drawRect(window.topLeft[1], window.topLeft[0], window.width, window.height)
    p.end()

    return outputImage

def paintGrayscaleProposalScoreHeatmap(imageFileName, scoredProposals):
    outputImage = QImage(imageFileName)
    outputImage.fill(Qt.white)

    p = QPainter()
    p.begin(outputImage)
    p.setBrush(Qt.SolidPattern)

    for window, score in scoredProposals:
        c = int(255 * (1.0 - score))
        brush = QBrush(QColor(c, c, c, 255), Qt.SolidPattern)
        p.setBrush(brush)
        p.setPen(QPen(Qt.NoPen))
        p.drawRect(window.topLeft[1], window.topLeft[0], window.width, window.height)
    p.end()

    return outputImage

def paintProposalBoxes(imageFileName, proposals, groundTruth = []):
    outputImage = QImage(imageFileName)
    outputImage = outputImage.convertToFormat(QImage.Format_RGB888)

    p = QPainter()
    p.begin(outputImage)
    p.setBrush(Qt.NoBrush)
    p.setPen(Qt.red)

    for proposal in proposals:
        p.drawRect(proposal.topLeft[1], proposal.topLeft[0], proposal.width, proposal.height)

    p.setPen(Qt.green)

    for proposal in groundTruth:
        p.drawRect(proposal.topLeft[1], proposal.topLeft[0], proposal.width, proposal.height)

    p.end()

    return outputImage
