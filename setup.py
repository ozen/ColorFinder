#! /usr/bin/env python
from distutils.core import setup

setup(name='ColorFinder',
      version='0.1',
      description='A tool for finding colors in an image',
      author='Yigit Ozen',
      packages=['colorfinder',],
      package_data={
          'colorfinder': ['*.json'],
      },
      data_files = [("", ["LICENSE.txt"])],
     )
