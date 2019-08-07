from PIL import Image
import numpy as np

def imresize(image, output_shape, interp="box"):
    mode = Image.BOX

    if interp is "bilinear":
        mode = Image.BILINEAR
    
    if interp is "bicubic":
        mode = Image.BICUBIC

    if interp is "lanczos":
        mode = Image.LANCZOS

    resampled = Image.fromarray(image).resize(output_shape, resample=mode)

    return np.array(resampled)
