from __future__ import division, print_function

import numpy as np

"""
Computes the distribution of labels, returns a array indexed by label ID.
"""
def labelDistribution(labels):
    minLabel = np.min(labels)
    maxLabel = np.max(labels)

    distribution = np.zeros(maxLabel - minLabel + 1, dtype = np.uint64)

    for label in labels:
        distribution[label] += 1

    return distribution.astype(np.float32) / sum(distribution)
