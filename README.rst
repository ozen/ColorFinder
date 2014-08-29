===============
ColorFinder
===============

Python package for finding major colors in an image.


Method
=======

This package is originally created to find major colors in a fabric accurately.
We had tested several clustering methods until we got good results from mean-shift filtering.
The method used in this package follows these steps:

1. Downsize the image into affordable sizes (300 pixels max width or heigth), if it is too big.
2. Apply mean-shift filter with range radius of 8 and a spatial radius proportional to image size.
3. Sample ~1500 pixels that are homogeneously spreaded
4. Count colors of sampled pixels
5. Discard the colors which have counts less than 2% of the total number of sampled pixels.
6. For each remaining color, find the closest color in the reference colors file.  The default references are ColorChecker and ColorChecker Digital SG colors. Distances between colors are calculated using CIEDE2000 Delta E formula in L*a*b* color space.
7. Look into the found colors and drop the ones that are too close to another found color with a bigger pixel count.
8. Return a list of dictionaries containing labels, RGB and L*a*b* values of found colors


Installation
=============

Following instructions are for Ubuntu 12.04 but they should be similar in other Linux distros.

1. Install BLAS and LAPACK libraries and Fortran compiler to be able to compile NumPy and SciPy in the next step::

    sudo apt-get install libblas3gf libblas-doc libblas-dev liblapack3gf liblapack-doc liblapack-dev gfortran

2. Install Pillow, NumPy and SciPy packages which are required by ColorFinder. Add sudo if you don't use virtualenv. ColorFinder is tested with the given versions of the packages, but newer versions will probably work too::

    <sudo> pip install numpy==1.8.1 scipy==0.13.3 Pillow==2.3.0
    
3.
    Install ColorFinder using the source::

        <sudo> python setup.py install

    or using pip::

        <sudo> pip install -e git+ssh://git@bitbucket.org/imcom/colorfinder.git#egg=colorfinder

Usage
=============

Instantiate ColorFinder with an optional palette parameter::

    from colorfinder import ColorFinder
    cf = ColorFinder('colorchecker')

The options for palette:

- You can pass a list of colors to be matched against. Look at the colorfinder/colorchecker.json file in the repo for the format.
- If you pass string 'colorchecker', colors are matched against the colors in the ColorChecker chart.
- If you pass string 'colorchecker_sg', colors are matched against the colors in the ColorChecker Digital SG chart.
- If you don't pass a parameter, colorchecker_sg is used as default.

Then, use the colorfinder instance to find colors in an image::

    cf.find(image_file, color_space="Adobe")

color_space parameter is optional and can be either sRGB or Adobe. sRGB is the default. If color_space is Adobe, the image is converted from Adobe to sRGB color space before comparing with the palette.

find method returns a dictionary of found colors. Keys are the labels of colors and values are dictionaries containing

- count: the count of pixels with that color
- rgb: RGB value of the color
- lab: LAB value of the color

An example result::

    {
        'G5': {
            'count': 885,
            'rgb': [157.56191635470245, 157.8574278695142, 158.38404888964826],
            'lab': [65.05, 0, -0.32]
        },
        'K7': {
            'count': 81,
            'rgb': [107.99475754890925, 107.91966049978896, 107.51434797782261],
            'lab': [45.59, -0.05, 0.23]
        },
        'F5': {
            'count': 211,
            'rgb': [197.17771700509283, 196.60123301082598, 197.06211406610106],
            'lab': [79.43, 0.29, -0.17]
        }
    }
