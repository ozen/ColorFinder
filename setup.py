#! /usr/bin/env python
from setuptools import setup

setup(name='ColorFinder',
      version='0.1',
      description='A tool for finding colors in an image',
      author='Yigit Ozen',
      packages=['colorfinder',],
      package_data={
          'colorfinder': ['*.json'],
      },
      data_files = [("", ["LICENSE.txt"])],
      install_requires=[
          'Pillow == 2.4.0',
          'numpy == 1.8.1',
          'scipy == 0.14.0',
          'six == 1.6.1',
          'scikit-image == 0.10.0',
          'scikit-learn == 0.14.1',
          ],
     )