#!/usr/bin/env python

from setuptools import setup, find_packages

long_description='''
auv_perception is a library to do limited perception on sonar images, such as Forward-Looking sonar.
It contains code to read ARIScope files, project them into a rectangular coordinates, label bounding boxes,
and run object detection algorithms in this kind of images, by for example limiting the sliding window to a 
polar field of view.

Some relevant algorithms that are implemented:
- Polar Sliding Window
- Detection Proposals with CNN and FCN.
- Sliding Window Object Detectors

This library is only compatible with Python 3.x.
'''

setup(name='auv_perception',
      version='0.0.1',
      description='Sonar Perception with Deep Learning',
      long_description=long_description,
      author='Matias Valdenegro-Toro',
      author_email='matias.valdenegro@gmail.com',
      url='https://github.com/mvaldenegro/auv-perception',
      license='LGPLv3',
      install_requires=['keras>=2.2.0', 'numpy', 'Pillow', 'matplotlib'],
      packages=find_packages()
     )
