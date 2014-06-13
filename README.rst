===============
ColorFinder
===============

Python package for finding colors in an image.


Method
=======

This package is originally created to find major colors in a fabric.
We had used several clustering methods until we got good results from mean-shift filtering.
The method used in this package follows these steps:

1. Downsize the image into affordable sizes (300 pixels max width or heigth), if it is too big.
2. Apply mean-shift filter with range radius of 8 and a spatial radius proportional to image size.
3. Sample ~1500 pixels that are homogeneously spreaded
4. Count colors of sampled pixels
5. Discard the colors which have counts less than 2% of the total number of sampled pixels.
6. For each remaining color, find the closest color in the reference colors file.  The default references are ColorChecker and ColorChecker Digital SG colors. Distances between colors are calculated using CIEDE2000 Delta E formula in L*a*b* color space.
7. Look into the found colors and drop the ones that are too close to another found color with a bigger pixel count.
8. Return a list of dictionaries containing labels, RGB and L*a*b* values of found colors



Requirements
=============

Pillow, NumPy and SciPy packages are required to use ColorFinder.

NumPy requires BLAS and LAPACK libraries to compile. They can be installed on Ubuntu using the following command::

    sudo apt-get install libblas3gf libblas-doc libblas-dev liblapack3gf liblapack-doc liblapack-dev

