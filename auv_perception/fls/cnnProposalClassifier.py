#!/usr/bin/env python3

import numpy as np
import keras

from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten, BatchNormalization
from keras.layers import Convolution2D, MaxPooling2D

from scipy.misc import imresize
from math import sqrt

from .objectProposals import ProposalEvaluator

class CNNProposalBinaryEvaluator(ProposalEvaluator):
    def __init__(self, weightsFile = None):
        self.model = self.buildKerasModel()

        if weightsFile is None:
            self.model.load_weights("cnnProposalFixedBinaryWeights.hdf5")
        else:
            self.model.load_weights(weightsFile)

    def buildKerasModel(self):
        model = Sequential()

        model.add(Convolution2D(12, 5, 5, border_mode='valid', input_shape=(1, 96, 96), activation = "relu"))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(BatchNormalization())

        model.add(Convolution2D(12, 5, 5, border_mode='valid', activation = "relu"))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(BatchNormalization())

        model.add(Flatten())
        model.add(Dense(64, activation = "relu"))
        model.add(BatchNormalization())

        model.add(Dense(2, activation = "softmax"))

        model.compile(loss = "categorical_crossentropy", optimizer = "adam")

        return model

    def evaluate(self, windowImage):
        probs = self.model.predict(windowImage.reshape(1, 1, 96, 96), batch_size = 1)[0]

        #Class 0 is object, and class 1 is background
        #Return true if classifier says object
        decision = probs[1] >= probs[0]

        if decision:
            return True, probs[1]
        else:
            return False, probs[0]

    def resizeAndClassify(self, image):
        resizedImage = None

        if image.shape != (96, 96):
            resizedImage = imresize(image, (96, 96), interp = "bilinear")
        else:
            resizedImage = image

        return self.classify(resizedImage)

class CNNProposalScoreEvaluator(ProposalEvaluator):
    def __init__(self, weightsFile = None):
        self.model = self.buildKerasModel()

        if weightsFile is None:
            self.model.load_weights("cnnProposalFixedScoreWeights.hdf5")
        else:
            self.model.load_weights(weightsFile)

        self.threshold = 0.5

    def buildKerasModel(self):
        model = Sequential()

        model.add(Convolution2D(32, 5, 5, border_mode='valid', input_shape=(1, 96, 96), activation = "relu"))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(BatchNormalization())

        model.add(Convolution2D(32, 5, 5, border_mode='valid', activation = "relu"))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(BatchNormalization())

        model.add(Flatten())
        model.add(Dense(96, activation = "relu"))
        model.add(BatchNormalization())

        model.add(Dense(1, activation = "sigmoid"))

        model.compile(loss = "mse", optimizer = "adam")

        return model

    def evaluate(self, windowImage):
        score = self.score(windowImage)

        return (score > self.threshold), score

    def score(self, windowImage):
        return self.model.predict(windowImage.reshape(1, 1, 96, 96), batch_size = 1)[0]

    def resizeAndScore(self, image):
        resizedImage = None

        if image.shape != (96, 96):
            resizedImage = imresize(image, (96, 96), interp = "bilinear")
        else:
            resizedImage = image

        return self.classify(resizedImage)

class TMProposalEvaluator(ProposalEvaluator):
    def __init__(self, positiveTemplates, mode = "cc"):
        self.positiveTemplates = positiveTemplates
        self.threshold = 0.5

        if mode == "cc":
            self.positiveTemplateMeans = np.zeros(positiveTemplates.shape[0])

            for i in range(positiveTemplates.shape[0]):
                self.positiveTemplateMeans[i] = np.mean(positiveTemplates[i])

            self.matcher = self.evalCC
        elif mode == "sqd":
            self.matcher = self.evalSQD
        else:
            raise ValueError("Invalid mode: {}".format(mode))

    def bestCorrelationMatch(self, image, templates, templateMeans):
        scores = np.zeros(templates.shape[0])
        imageMean = np.mean(image)

        for i, template in enumerate(templates):
            normFactor = np.sum(np.square(image - imageMean)) * np.sum(np.square(template - templateMeans[i]))
            scores[i] = np.sum(np.multiply(image - imageMean, template - templateMeans[i])) / sqrt(normFactor)

        score = max(scores)

        if score < 0.0:
            score = 0.0

        if score > 1.0:
            score = 1.0

        return score

    def bestSquareDiffMatch(self, image, templates):
        scores = np.zeros(templates.shape[0])

        for i, template in enumerate(templates):
            scores[i] = np.mean(np.square(image - template))

        scores = scores / sum(scores)

        return min(scores)

    def evalCC(self, windowImage):
        return self.bestCorrelationMatch(windowImage, self.positiveTemplates, self.positiveTemplateMeans)

    def evalSQD(self, windowImage):
        return 1.0 - self.bestSquareDiffMatch(windowImage, self.positiveTemplates)

    def evaluate(self, windowImage):
        score = self.score(windowImage)

        return (score > self.threshold), score

    def score(self, windowImage):
        return self.matcher(windowImage)

    def resizeAndScore(self, image):
        resizedImage = None

        if image.shape != (96, 96):
            resizedImage = imresize(image, (96, 96), interp = "bilinear")
        else:
            resizedImage = image

        return self.classify(resizedImage)
