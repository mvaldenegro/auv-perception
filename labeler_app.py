#!/bin/env python3

import PyQt5

from PyQt5.QtCore import Qt, QPointF, QSizeF, QRectF, QVariant, pyqtSignal, QFileInfo, QDir, QFile, QStringListModel
from PyQt5.QtGui import QBrush, QPixmap, QIcon, QTransform, QImage, QKeySequence

from PyQt5.QtWidgets import QGraphicsItem, QGraphicsWidget, QGraphicsRectItem, QGraphicsTextItem, QMenu
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QGraphicsView, QMainWindow, QToolBar
from PyQt5.QtWidgets import QFileDialog, QInputDialog, QLabel, QStatusBar, QListView, QDockWidget, QApplication
from PyQt5.QtWidgets import QProgressDialog, QAbstractItemView

from auv_perception.annotation import writeXML, readXML, LabeledImage, Label

class ResizeHandle(QGraphicsRectItem):
    def __init__(self, rect, parent, cursor, updateCB):
        QGraphicsRectItem.__init__(self, rect, parent)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setPen(Qt.red)
        self.setBrush(QBrush(Qt.red, Qt.SolidPattern))
        self.update = updateCB

        if cursor is not None:
            self.setCursor(cursor)

    def itemChange(self, change, value):
        if change == self.ItemPositionChange:
            if self.update is not None:
                self.update(value - self.pos())

            return value

        return QGraphicsRectItem.itemChange(self, change, value)


class RectangleLabelItem(QGraphicsRectItem):
    def __init__(self, rect, parent, label):
        QGraphicsRectItem.__init__(self, rect, parent = parent)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setPen(Qt.red)
        self.resizeHandleSize = 4.0

        self.updateResizeHandles()

        self.label = label

        self.labelsCombo = QGraphicsTextItem(self.label, self)
        self.labelsCombo.setDefaultTextColor(Qt.red)
        self.labelsCombo.setPos(self.rect().bottomLeft() + QPointF(0, 5.0))

    def updateBottomRight(self, delta):
        newPos = delta + self.rect().bottomRight()
        self.prepareGeometryChange()
        rect = self.rect()
        rect.setBottomRight(newPos)
        self.setRect(rect)
        self.labelsCombo.setPos(self.rect().bottomLeft() + QPointF(0, 5.0))

        self.scene().emitLabelsChanged()

    def updateTopLeft(self, delta):
        newPos = delta + self.rect().topLeft()
        self.prepareGeometryChange()
        rect = self.rect()
        rect.setTopLeft(newPos)
        self.setRect(rect)
        self.labelsCombo.setPos(self.rect().bottomLeft() + QPointF(0, 5.0))

        self.scene().emitLabelsChanged()

    def updateResizeHandles(self):
        self.offset = self.resizeHandleSize * (self.scene().view().mapToScene(1,0) - self.scene().view().mapToScene(0,1)).x()

        tmp = QRectF(QPointF(0.0, 0.0), QSizeF(self.offset, self.offset))
        tmp.moveCenter(self.rect().topLeft())
        self.handleTopLeft = ResizeHandle(tmp, self, cursor = Qt.SizeFDiagCursor, updateCB = self.updateTopLeft)
        tmp.moveCenter(self.rect().bottomRight())
        self.handleBottomRight = ResizeHandle(tmp, self, cursor = Qt.SizeFDiagCursor, updateCB = self.updateBottomRight)

        self.handleTopLeft.setPen(Qt.red)
        self.handleBottomRight.setPen(Qt.red)

    def contextMenu(self):
        menu = QMenu()

        menu.addAction("Edit label", self.editLabel)

        return menu

    def editLabel(self):
        label = self.scene().dialogGetLabel()

        if label is not None:

            self.label = label
            self.labelsCombo.setPlainText(label)

            self.scene().emitLabelsChanged()

    def itemChange(self, change, value):

        if change == self.ItemPositionHasChanged:

            self.scene().emitLabelsChanged()

            return QVariant()

        if change == self.ItemScenePositionHasChanged:
            print("Scene position changed to {}".format(value))

            return QVariant()

        return QGraphicsRectItem.itemChange(self, change, value)

    def sceneRect(self):
        w = self.rect().width()
        h = self.rect().height()

        return QRectF(self.mapToScene(self.rect().topLeft()), QSizeF(w, h))


class LabelingScene(QGraphicsScene):
    mouseMoved = pyqtSignal(QPointF, name = 'mouseMoved')
    labelsChanged = pyqtSignal(list, name = 'labelsChanged')
    nextImage = pyqtSignal(name = 'nextImage')
    previousImage = pyqtSignal(name = 'previousImage')
    copyLabelsFromPrevious = pyqtSignal(name = 'copyLabelsFromPrevious')

    def __init__(self, parent = None):
        QGraphicsScene.__init__(self, parent)
        self.pixmapItem = None
        self.labelsCache = []

    #TODO: Implement this method to remove a label (from the item)
    def removeLabelItem(self, item):
        self.removeItem(item)
        self.emitLabelsChanged()

    def contextMenuEvent(self, event):

        item = self.itemAt(event.scenePos(), QTransform())

        if item != None and item != self.pixmapItem and type(item) is RectangleLabelItem:
            #Later do something to remove rectangles
            menu = item.contextMenu()
            menu.addSeparator()
            menu.addAction("Remove rectangle", lambda: self.removeLabelItem(item))

            menu.exec(event.screenPos())
            return

        menu = QMenu()
        menu.addAction("Insert bounding rectangle", lambda: self.insertBoundingRectangle(event.scenePos()))
        menu.exec(event.screenPos())

    def mouseMoveEvent(self, event):
        self.mouseMoved.emit(event.scenePos())
        QGraphicsScene.mouseMoveEvent(self, event)

    def displayLabeledImage(self, labeledImage, folder):
        #Cleanup
        self.clear()

        imageFileName = folder + QDir.separator() + labeledImage.fileName

        image = QImage(imageFileName)

        if image.isNull():
            print("Cannot load file {}".format(labeledImage.fileName))
            return

        pix = QPixmap.fromImage(image)

        self.pixmapItem = self.addPixmap(pix)
        self.pixmapItem.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)
        self.pixmapItem.setPos(QPointF(0.0, 0.0))

        #Load labels
        for label in labeledImage.labels:
            r = RectangleLabelItem(rect = label.rectangle, parent = self.pixmapItem,
                                   label = label.classLabel)

    def insertBoundingRectangle(self, pos):
        print("Inserting item at {} {}".format(pos.x(), pos.y()))

        defaultWidth = 0.05 * self.pixmapItem.pixmap().width()
        defaultHeight = 0.05 * self.pixmapItem.pixmap().height()

        rect = QRectF(QPointF(), QSizeF(defaultWidth, defaultHeight))
        rect.moveCenter(pos)

        label = self.dialogGetLabel()

        if label is not None:
            rectItem = RectangleLabelItem(rect = rect, parent = self.pixmapItem,
                                      label = label)

            if label not in self.labelsCache:
                self.labelsCache.append(label)
                print("Labels cache is now {}".format(self.labelsCache))

        self.emitLabelsChanged()

    def emitLabelsChanged(self):
        self.labelsChanged.emit(self.labels())

    def view(self):
        return self.views()[0]

    def labels(self):
        labels = []

        allItems = self.items()

        for item in allItems:
            if type(item) is RectangleLabelItem and item.label is not None:
                labels.append(Label(item.label, item.sceneRect()))

        return labels

    def dialogGetLabel(self):

        print("Labels cache contains {}".format(self.labelsCache))

        item = QInputDialog.getItem(None, "Rectangle label item",
                                    "Please enter the label associated with this rectangle:",
                                    self.labelsCache, 0, True)

        if item[1]:
            return item[0]
        else:
            return None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            event.accept()
            self.previousImage.emit()
            return

        if event.key() == Qt.Key_Right:
            event.accept()
            self.nextImage.emit()
            return

        if event.matches(QKeySequence.Copy):
            event.accept()
            self.copyLabelsFromPrevious.emit()
            return

        QGraphicsScene.keyPressEvent(self, event)

    def setLabels(self, labels):
        for item in self.items():
            if type(item) is RectangleLabelItem:
                self.removeItem(item)

        for label in labels:
            r = RectangleLabelItem(rect = label.rectangle, parent = self.pixmapItem,
                                   label = label.classLabel)

class MainWindow(QMainWindow):
    labelsChanged = pyqtSignal(list, name = 'labelsChanged')

    def __init__(self):
        QMainWindow.__init__(self)

        self.view = QGraphicsView()
        self.scene = LabelingScene()

        self.view.setScene(self.scene)
        self.setCentralWidget(self.view)

        self.previousImageIdx = 0
        self.currentImageIdx = 0

        self.setupToolBar()
        self.setupDockWidgets()
        self.setupStatusBar()

        self.showMaximized()

        self.scene.labelsChanged.connect(self.updateLabels)
        self.labelsChanged.connect(self.scene.setLabels)

        self.scene.nextImage.connect(self.nextImage)
        self.scene.previousImage.connect(self.previousImage)
        self.scene.copyLabelsFromPrevious.connect(self.copyLabelsFromPreviousImage)

    def setupToolBar(self):
        self.toolbar = QToolBar()

        self.toolbar.addAction(QIcon.fromTheme("document-new"), "Create a new label file", self.newFile)
        self.toolbar.addAction(QIcon.fromTheme("document-open"), "Open a label file", self.openFile)
        saveAction = self.toolbar.addAction(QIcon.fromTheme("document-save"), "Save", self.saveFile)
        saveAction.setShortcut(QKeySequence(QKeySequence.Save))

        self.toolbar.addSeparator()
        self.toolbar.addAction(QIcon.fromTheme("insert-image"), "Add images to dataset", self.addImages)
        self.toolbar.addSeparator()

        self.toolbar.addAction(QIcon.fromTheme("go-previous"), "Next image", self.nextImage)
        self.toolbar.addAction(QIcon.fromTheme("edit-copy"), "Copy labels from previous image", self.copyLabelsFromPreviousImage)
        self.toolbar.addAction(QIcon.fromTheme("go-next"), "Previous image", self.previousImage)

        self.addToolBar(self.toolbar)

    def setupDockWidgets(self):
        self.fileListWidget = QListView()
        self.leftDockWidget = QDockWidget()
        self.leftDockWidget.setWidget(self.fileListWidget)

        self.fileListModel = QStringListModel(self.fileListWidget)
        self.fileListWidget.setModel(self.fileListModel)
        self.fileListWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.fileListWidget.doubleClicked.connect(lambda index: self.loadImageAtIndex(index.row()))

        self.addDockWidget(Qt.LeftDockWidgetArea, self.leftDockWidget)

    def setupStatusBar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.currentImageLabel = QLabel()
        self.statusBar.addPermanentWidget(self.currentImageLabel)

        self.scene.mouseMoved.connect(lambda p: self.statusBar.showMessage("Mouse at scene pos {}, {}".format(p.x(), p.y())))

    #Here we assume that the image files are stored in the same folder as the labels file.
    #This is usual practice, maybe in the future we could put images and labels in the same file (HDF5)
    def newFile(self):
        imageFileNames = self.normalizeFileNames(QFileDialog.getOpenFileNames(caption = "Select image files to label")[0])
        self.labelsFileName = QFileDialog.getSaveFileName(caption = "Select labels file to save")[0]
        self.labelsFolder = QFileInfo(self.labelsFileName).absolutePath()

        print("Creating new labels file with {} images to be labeled".format(len(imageFileNames)))

        self.labeledImages = []

        for imageFileName in imageFileNames:
            self.labeledImages.append(LabeledImage(imageFileName, []))

        self.loadImageAtIndex(0)
        self.previousImageIdx = 0
        self.fileListModel.setStringList(imageFileNames)

    def normalizeFileNames(self, fileNames):
        return [QFileInfo(f).fileName() for f in fileNames]

    def loadImageAtIndex(self, index):
        if (index < 0) or (index >= len(self.labeledImages)):
            return

        self.previousImageIdx = self.currentImageIdx
        self.currentImageIdx = index
        self.scene.displayLabeledImage(self.labeledImages[self.currentImageIdx], self.labelsFolder)

        self.fileListWidget.setCurrentIndex(self.fileListModel.index(self.currentImageIdx, 0))

        msg = "{} ({}/{})".format(self.labeledImages[self.currentImageIdx].fileName, self.currentImageIdx + 1, len(self.labeledImages))

        self.currentImageLabel.setText(msg)

    def updateLabels(self, newLabels):
        self.labeledImages[self.currentImageIdx].labels = newLabels

    def openFile(self):
        labelsFileName = QFileDialog.getOpenFileName(caption = "Select labels file to load")[0]

        if labelsFileName == "" or len(labelsFileName) == 0:
            return

        self.labelsFileName = labelsFileName
        self.labelsFolder = QFileInfo(self.labelsFileName).absolutePath()
        self.labeledImages = readXML(self.labelsFileName)

        self.fileListModel.setStringList([s.fileName for s in self.labeledImages])

        self.loadImageAtIndex(0)
        self.previousImageIdx = 0

        self.scene.labelsCache = self.allLabelNames()

    def saveFile(self):
        writeXML(self.labelsFileName, self.labeledImages)
        self.statusBar.showMessage("Saved!")

    def nextImage(self):
        self.loadImageAtIndex(self.currentImageIdx + 1)

    def previousImage(self):
        self.loadImageAtIndex(self.currentImageIdx - 1)

    def copyLabelsFromPreviousImage(self):
        self.labeledImages[self.currentImageIdx].labels = self.labeledImages[self.previousImageIdx].labels

        self.labelsChanged.emit(self.labeledImages[self.currentImageIdx].labels)

    def allLabelNames(self):
        labelNames = []

        for labeledImage in self.labeledImages:
            for label in labeledImage.labels:
                if label.classLabel not in labelNames:
                    labelNames.append(label.classLabel)

        return labelNames

    def addImages(self):
        imageFileNames = QFileDialog.getOpenFileNames(caption = "Select image files to label")

        if not imageFileNames[0] or len(imageFileNames[0]) == 0:
            return

        imageFileNames = imageFileNames[0]
        labelsDir = QFileInfo(self.labelsFileName).absoluteDir()
        originDir = QFileInfo(imageFileNames[0]).absoluteDir()

        #Copy image files to the labels folder
        if originDir.absolutePath() != labelsDir.absolutePath():
            progDialog = QProgressDialog("Copying image files to the labels folder", "Cancel", 0, len(imageFileNames), self)

        i = 0
        for imageFileName in imageFileNames:
            progDialog.setValue(i)

            oldName = QFileInfo(imageFileName).fileName()
            newPath = labelsDir.absoluteFilePath(oldName)

            print("Copying {} to {}".format(imageFileName, newPath))

            ok = QFile.copy(imageFileName, newPath)

            QApplication.processEvents()

            if not ok:
                print("Error copying {} to {}".format(imageFileName, newPath))

            i += 1

        progDialog.setValue(len(imageFileNames))
        progDialog.close()

        currentImageFileNames = [s.fileName for s in self.labeledImages]

        newImgIdx = len(self.labeledImages)

        for imageFileName in imageFileNames:
            normalizedFileName = QFileInfo(imageFileName).fileName()

            if normalizedFileName in currentImageFileNames:
                print("File {} already in dataset, skipping".format(normalizedFileName))
                continue

            self.labeledImages.append(LabeledImage(normalizedFileName, []))

        self.fileListModel.setStringList([s.fileName for s in self.labeledImages])
        self.loadImageAtIndex(newImgIdx)

        print("Added {} images to dataset".format(len(imageFileNames)))
        print("New length of labeledImages array {}".format(len(self.labeledImages)))

import sys

app = QApplication(sys.argv)
mainWindow = MainWindow()
mainWindow.show()

app.exec()
