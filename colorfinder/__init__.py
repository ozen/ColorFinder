import json
from PIL import Image
from scipy.misc import fromimage
from sklearn.cluster import KMeans
from skimage.color import *
from .conversion import *


class ColorFinder:
    def __init__(self):
        colors_wide_file = open('colors_wide.json')
        colors_file = open('colors.json')
        self.colors_wide = json.load(colors_wide_file)
        self.colors = json.load(colors_file)

    def find_closest_color(self, color, mode, wide):
        if len(color) != 3:
            raise ValueError("'color' parameter needs to be 1D array of length 3")

        mode = mode.lower()
        if mode not in ('srgb', 'xyz', 'lab'):
            raise ValueError("'mode' parameter needs to be one of 'sRGB', 'XYZ' or 'LAB'")

        if mode == 'xyz':
            color = xyz_to_lab(color)
            mode = 'lab'

        colors = self.colors_wide if wide else self.colors
        min_dist = float("inf")
        best_color = None
        for clr in colors:
            distance = deltaE_ciede2000(color, clr[mode])
            if distance < min_dist:
                min_dist = distance
                best_color = clr

        return best_color

    def find_colors_kmeans(self, image, num_colors, mode):
        mode = mode.lower()
        if mode not in ('srgb', 'adobe', 'xyz', 'lab'):
            raise ValueError("'mode' parameter needs to be one of 'sRGB', 'Adobe', 'XYZ' or 'LAB'")

        im = Image.open(image)
        w = 300 if im.size[0] > 300 else im.size[0]
        h = w * im.size[1] // im.size[0]
        im = im.resize((w, h), Image.BILINEAR)

        if mode == 'adobe':
            im = im.convert('RGB', (
                0.57667, 0.18556, 0.18823, 0,
                0.29734, 0.62736, 0.07529, 0,
                0.02703, 0.07069, 0.99134, 0,
            ))
            mode = 'xyz'

        ar = fromimage(im)
        if mode == 'rgb':
            ar = rgb2lab(ar)
        elif mode == 'xyz':
            ar = xyz2lab(ar)

        ar = ar.reshape(ar.shape[0] * ar.shape[1], ar.shape[2])
        km = KMeans(n_clusters=num_colors, n_jobs=-1).fit(ar)

        colors = set()
        for center in km.cluster_centers_:
            colors.add(self.find_closest_color(center, mode='lab', wide=False))
            colors.add(self.find_closest_color(center, mode='lab', wide=True))

        return list(colors)


def find_color(color, mode="sRGB", wide=True):
    return ColorFinder().find_closest_color(color, mode, wide)


def find_image_colors(image, num_colors, mode="sRGB"):
    return ColorFinder().find_colors_kmeans(image, num_colors, mode)
