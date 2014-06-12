# Copyright (C) 2011, the scikit-image team
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#  1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#  3. Neither the name of skimage nor the names of its contributors may be
#     used to endorse or promote products derived from this software without
#     specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from __future__ import division
import numpy as np


def deltaE_cie76(lab1, lab2):
    """Euclidean distance between two points in Lab color space

Parameters
----------
lab1 : array_like
reference color (Lab colorspace)
lab2 : array_like
comparison color (Lab colorspace)

Returns
-------
dE : array_like
distance between colors `lab1` and `lab2`

References
----------
.. [1] http://en.wikipedia.org/wiki/Color_difference
.. [2] A. R. Robertson, "The CIE 1976 color-difference formulae,"
Color Res. Appl. 2, 7-11 (1977).
"""
    lab1 = np.asarray(lab1)
    lab2 = np.asarray(lab2)
    L1, a1, b1 = np.rollaxis(lab1, -1)[:3]
    L2, a2, b2 = np.rollaxis(lab2, -1)[:3]
    return np.sqrt((L2 - L1) ** 2 + (a2 - a1) ** 2 + (b2 - b1) ** 2)


def deltaE_ciede2000(lab1, lab2, kL=1, kC=1, kH=1):
    """Color difference as given by the CIEDE 2000 standard.

CIEDE 2000 is a major revision of CIDE94. The perceptual calibration is
largely based on experience with automotive paint on smooth surfaces.

Parameters
----------
lab1 : array_like
reference color (Lab colorspace)
lab2 : array_like
comparison color (Lab colorspace)
kL : float (range), optional
lightness scale factor, 1 for "acceptably close"; 2 for "imperceptible"
see deltaE_cmc
kC : float (range), optional
chroma scale factor, usually 1
kH : float (range), optional
hue scale factor, usually 1

Returns
-------
deltaE : array_like
The distance between `lab1` and `lab2`

Notes
-----
CIEDE 2000 assumes parametric weighting factors for the lightness, chroma,
and hue (`kL`, `kC`, `kH` respectively). These default to 1.

References
----------
.. [1] http://en.wikipedia.org/wiki/Color_difference
.. [2] http://www.ece.rochester.edu/~gsharma/ciede2000/ciede2000noteCRNA.pdf
(doi:10.1364/AO.33.008069)
.. [3] M. Melgosa, J. Quesada, and E. Hita, "Uniformity of some recent
color metrics tested with an accurate color-difference tolerance
dataset," Appl. Opt. 33, 8069-8077 (1994).
"""
    lab1 = np.asarray(lab1)
    lab2 = np.asarray(lab2)
    unroll = False
    if lab1.ndim == 1 and lab2.ndim == 1:
        unroll = True
        if lab1.ndim == 1:
            lab1 = lab1[None, :]
        if lab2.ndim == 1:
            lab2 = lab2[None, :]
    L1, a1, b1 = np.rollaxis(lab1, -1)[:3]
    L2, a2, b2 = np.rollaxis(lab2, -1)[:3]

    # distort `a` based on average chroma
    # then convert to lch coordines from distorted `a`
    # all subsequence calculations are in the new coordiantes
    # (often denoted "prime" in the literature)
    Cbar = 0.5 * (np.hypot(a1, b1) + np.hypot(a2, b2))
    c7 = Cbar ** 7
    G = 0.5 * (1 - np.sqrt(c7 / (c7 + 25 ** 7)))
    scale = 1 + G
    C1, h1 = _cart2polar_2pi(a1 * scale, b1)
    C2, h2 = _cart2polar_2pi(a2 * scale, b2)
    # recall that c, h are polar coordiantes. c==r, h==theta

    # cide2000 has four terms to delta_e:
    # 1) Luminance term
    # 2) Hue term
    # 3) Chroma term
    # 4) hue Rotation term

    # lightness term
    Lbar = 0.5 * (L1 + L2)
    tmp = (Lbar - 50) ** 2
    SL = 1 + 0.015 * tmp / np.sqrt(20 + tmp)
    L_term = (L2 - L1) / (kL * SL)

    # chroma term
    Cbar = 0.5 * (C1 + C2) # new coordiantes
    SC = 1 + 0.045 * Cbar
    C_term = (C2 - C1) / (kC * SC)

    # hue term
    h_diff = h2 - h1
    h_sum = h1 + h2
    CC = C1 * C2

    dH = h_diff.copy()
    dH[h_diff > np.pi] -= 2 * np.pi
    dH[h_diff < -np.pi] += 2 * np.pi
    dH[CC == 0.] = 0. # if r == 0, dtheta == 0
    dH_term = 2 * np.sqrt(CC) * np.sin(dH / 2)

    Hbar = h_sum.copy()
    mask = np.logical_and(CC != 0., np.abs(h_diff) > np.pi)
    Hbar[mask * (h_sum < 2 * np.pi)] += 2 * np.pi
    Hbar[mask * (h_sum >= 2 * np.pi)] -= 2 * np.pi
    Hbar[CC == 0.] *= 2
    Hbar *= 0.5

    T = (1 -
         0.17 * np.cos(Hbar - np.deg2rad(30)) +
         0.24 * np.cos(2 * Hbar) +
         0.32 * np.cos(3 * Hbar + np.deg2rad(6)) -
         0.20 * np.cos(4 * Hbar - np.deg2rad(63))
         )
    SH = 1 + 0.015 * Cbar * T

    H_term = dH_term / (kH * SH)

    # hue rotation
    c7 = Cbar ** 7
    Rc = 2 * np.sqrt(c7 / (c7 + 25 ** 7))
    dtheta = np.deg2rad(30) * np.exp(-((np.rad2deg(Hbar) - 275) / 25) ** 2)
    R_term = -np.sin(2 * dtheta) * Rc * C_term * H_term

    # put it all together
    dE2 = L_term ** 2
    dE2 += C_term ** 2
    dE2 += H_term ** 2
    dE2 += R_term
    ans = np.sqrt(dE2)
    if unroll:
        ans = ans[0]
    return ans


def _cart2polar_2pi(x, y):
    """convert cartesian coordiantes to polar (uses non-standard theta range!)

NON-STANDARD RANGE! Maps to ``(0, 2*pi)`` rather than usual ``(-pi, +pi)``
"""
    r, t = np.hypot(x, y), np.arctan2(y, x)
    t += np.where(t < 0., 2 * np.pi, 0)
    return r, t