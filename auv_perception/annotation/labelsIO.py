import xml.etree.ElementTree as ET
from PyQt5.QtCore import QRectF

class LabeledImage:
    def __init__(self, fileName, labels):
        self.fileName = fileName
        self.labels = labels

class Label:
    def __init__(self, label, rectangle):
        self.classLabel = label
        self.rectangle = rectangle

    def __repr__(self):
        return "Label({}, {})".format(self.classLabel, self.rectangle)

def indentXML(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indentXML(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def writeXML(fileName, labeledImages):
    root = ET.Element("dataset")

    for image in labeledImages:
        imageElement = ET.SubElement(root, "image")
        imageElement.set("fileName", image.fileName)

        labelsElement = ET.SubElement(imageElement, "labels")

        for label in image.labels:
            rect = label.rectangle

            labelElement = ET.SubElement(labelsElement, "label")
            labelElement.set("topLeftX", str(rect.topLeft().x()))
            labelElement.set("topLeftY", str(rect.topLeft().y()))
            labelElement.set("width", str(rect.width()))
            labelElement.set("height", str(rect.height()))
            labelElement.set("class", label.classLabel)


    indentXML(root)
    ET.ElementTree(root).write(fileName, encoding = "utf-8")

def readXML(fileName):
    tree = ET.parse(fileName)
    root = tree.getroot()

    labeledImages = []

    for imageElement in root.iter(tag = "image"):
        labelsElement = imageElement.find("labels")

        labeledImage = LabeledImage(imageElement.get("fileName"), [])

        for labelElement in labelsElement.iter(tag = "label"):
            tlX = float(labelElement.get("topLeftX"))
            tlY = float(labelElement.get("topLeftY"))
            w = float(labelElement.get("width"))
            h = float(labelElement.get("height"))

            labelRect = QRectF(tlX, tlY, w, h)
            classLabel = labelElement.get("class")

            labeledImage.labels.append(Label(classLabel, labelRect))

        labeledImages.append(labeledImage)

    return labeledImages

import h5py
import numpy as np

from imageio import imread

labelType = np.dtype([("class", h5py.special_dtype(vlen = str)), ("topLeftX", np.uint32),
                      ("topLeftY", np.uint32), ("width", np.uint32),
                      ("height", np.uint32)])

labeledImageType = np.dtype([("originalFileName", h5py.special_dtype(vlen = str)), ("labeledRectangles", h5py.special_dtype(vlen = labelType))])

class HDF5LabelsFile:
    def __init__(self, fileName, newFile = False, imageShape = None):
        self.hdfFile = h5py.File(fileName, "a")

        if newFile:
            group = self.hdfFile.create_group("labeledImages")
            self.images = self.createGrayscaleImageDataset(group, "images", shape = imageShape, dtype = np.uint8)
            self.labels = group.create_dataset("labels", (None,), dtype = labeledImageType)
        else:
            self.images = self.hdfFile["labeledImages/images"]
            self.labels = self.hdfFile["labeledImages/labels"]


    def createGrayscaleImageDataset(self, group, datasetName, shape, dtype):
        """
        Create a dataset respecting the HDF5 image specification
        http://www.hdfgroup.org/HDF5/doc/ADGuide/ImageSpec.html
        """

        print(shape)

        imgDataset = group.create_dataset(datasetName, shape, maxshape = (None, None, None), dtype = dtype)

        # numpy.string_ is to force fixed-length string (necessary for compatibility)
        imgDataset.attrs["CLASS"] = np.string_("IMAGE")
        imgDataset.attrs["IMAGE_SUBCLASS"] = np.string_("IMAGE_GRAYSCALE")
        imgDataset.attrs["IMAGE_WHITE_IS_ZERO"] = np.array(0, dtype="uint8")
        imgDataset.attrs["IMAGE_MINMAXRANGE"] = [0, 255]

        imgDataset.attrs["DISPLAY_ORIGIN"] = np.string_("UL") # not rotated
        imgDataset.attrs["IMAGE_VERSION"] = np.string_("1.2")

        return imgDataset

    def setImagesFromFileNames(self, imageFileNames):
        i = 0
        for imageFileName in imageFileNames:
            imageData = imread(imageFileName, pilmode = "L")

            self.images[i] = imageData
            self.labels[i] = (imageFileName, [])

            i = i + 1

    def getLabeledImage(self, index):
        image = self.images[index]

    def setLabels(self, index, labels):
        lr = []

        for label in labels:
            lr.append((label.classLabel, label.topLeftx, label.topLeftY, label.width, label.height))

        self.labels[index].labeledRectangles = np.array(labels, dtype = labelType)