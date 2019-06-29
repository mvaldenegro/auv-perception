#!/usr/bin/env python3

import numpy as np
import keras

from keras.models import model_from_json
from scipy.ndimage.interpolation import zoom

class FCNProposalScorer:
    def __init__(self, modelJSONFile = "../../data/proposalFCNScore-modules2-model.json",
                     hdf5WeightsFile = "../../data/proposalFCNScore-modules2-weights.hdf5"):

        with open(modelJSONFile, "rt") as jsonFile:
            jsonString = jsonFile.read()

        self.model = model_from_json(jsonString)
        self.model.load_weights(hdf5WeightsFile)

        #Required because I am using an old Keras version
        self.model.compile(loss = "mse", optimizer = "adam")

        self.model.summary()

    def scoreImage(self, image):
        assert(len(image.shape) == 2)

        fcnInput = image.reshape((1, 1, image.shape[0], image.shape[1]))
        fcnResponse = self.model.predict(fcnInput)[0]
        fcnResponse = fcnResponse.reshape((fcnResponse.shape[1], fcnResponse.shape[2]))

        zoomFactor = (image.shape[0] / fcnResponse.shape[0], image.shape[1] / fcnResponse.shape[1])

        objectnessMap = zoom(fcnResponse, zoom = zoomFactor, order = 1)

        return objectnessMap
