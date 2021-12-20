#!/usr/bin/python3

from __future__ import print_function

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import matplotlib
matplotlib.use('Agg')

from auv_perception.fls import ARISFrameFile
from auv_perception.sonar import fractional_polar_axes

import sys, os, argparse

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.cm as cm

from skimage.io import imsave

#ARIS Explorer 3000 horizontal field of view
MIN_FOV = -15
MAX_FOV = 15

def savePolarProjection(outputFileName, frame):
    fig = plt.figure()

    theta, r = np.mgrid[MIN_FOV:MAX_FOV:(frame.width() * 1j), frame.windowStart():frame.windowEnd():(frame.height() * 1j)]
    ax = fractional_polar_axes(fig, thlim = (MIN_FOV, MAX_FOV), rlim = (frame.windowStart(), frame.windowEnd()), ticklabels = False)
    im = ax.pcolormesh(theta, r, frame.numpyImage().T, cmap = cm.Greys_r, shading='flat', edgecolors="none", vmin=0, vmax=255)

    fig.tight_layout()
    fig.savefig(outputFileName, bbox_inches = 'tight', facecolor = 'white', dpi=150, antialiased=False, pad_inches=0)
    plt.close(fig)

def saveRectangularProjection(outputFileName, frame):
    imsave(outputFileName, frame.data)

def progress(count, total, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()

parser = argparse.ArgumentParser()
parser.add_argument("inputArisFile", help = "Input ARIS DDFv5 sonar file (.aris extension)")
parser.add_argument("outputFolder", help = "Output folder where to store the image frames as PNG files")
parser.add_argument("--startIndex", help = "Starting frame index", type = int)
parser.add_argument("--endIndex", help = "End frame index (inclusive)", type = int)

polarParser = parser.add_mutually_exclusive_group(required=False)
polarParser.add_argument('--polar', dest='polar', action='store_true', help = "Output polar projection images")
polarParser.add_argument('--rectangular', dest='polar', action='store_false', help = "Output rectangular images")
parser.set_defaults(polar = True)

args = parser.parse_args()
baseFileName = os.path.splitext(os.path.basename(args.inputArisFile))[0]
arisFile = ARISFrameFile(args.inputArisFile)

projectAndSave = None

if args.polar:
    projectAndSave = savePolarProjection
else:
    projectAndSave = saveRectangularProjection

try:
    os.mkdir(args.outputFolder)
except FileExistsError:
    pass

startIdx = 0
endIdx = arisFile.frameCount() - 1

if args.startIndex is not None:
    startIdx = args.startIndex

if args.endIndex is not None:
    endIdx = args.endIndex

for i in range(startIdx, endIdx + 1):
    frame = arisFile.frame(i)

    #print("Window start {} window end {}".format(frame.windowStart(), frame.windowEnd()))

    outFileName = "{}/{}-frame{:05d}.png".format(args.outputFolder, baseFileName, i)

    progress(i, arisFile.frameCount(), " Processing frame {}".format(i))

    projectAndSave(outFileName, frame)

#sys.exit(0)
