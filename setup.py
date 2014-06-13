#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup, Extension
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, Extension

from numpy import get_include as np_include


def setup_package():
    build_requires = []
    try:
        import numpy
    except:
        build_requires = ['numpy>=1.8.1']

    metadata = dict(
        name='colorfinder',
        version='0.1.6',
        description='A tool for finding colors in an image',
        author='Yigit Ozen',
        license='MIT',
        packages=['colorfinder'],
        ext_modules=[Extension('_pymeanshift',
                               ['pymeanshift/ms.cpp', 'pymeanshift/msImageProcessor.cpp', 'pymeanshift/rlist.cpp',
                                'pymeanshift/RAList.cpp', 'pymeanshift/pymeanshift.cpp'],
                               depends=['pymeanshift/ms.h', 'pymeanshift/msImageProcessor.h', 'pymeanshift/RAList.h',
                                        'pymeanshift/rlist.h', 'pymeanshift/tdef.h'],
                               language='c++',
                               include_dirs=[np_include()]
        )],
        package_data={
            'colorfinder': ['*.json'],
        },
        data_files=[("", ["LICENSE", "README"])],
        setup_requires=build_requires,
        install_requires=[
            'Pillow',
            'numpy',
            'scipy',
        ],
    )

    setup(**metadata)


if __name__ == '__main__':
    setup_package()
