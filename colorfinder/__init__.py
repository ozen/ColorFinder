import json
import os
import codecs
from math import sqrt

import scipy
from PIL import Image

import _pymeanshift
from .distance import deltaE_ciede2000
from .conversion import *


class ColorFinder:
    def __init__(self, palette=None):
        if palette is None:
            colors_file = open(os.path.join(os.path.dirname(__file__), 'colorchecker_sg.json'))
            self.palette = json.load(colors_file)
        elif palette.lower() == "colorchecker":
            colors_file = open(os.path.join(os.path.dirname(__file__), 'colorchecker.json'))
            self.palette = json.load(colors_file)
        elif palette.lower() == "colorchecker_sg":
            colors_file = open(os.path.join(os.path.dirname(__file__), 'colorchecker_sg.json'))
            self.palette = json.load(colors_file)
        else:
            self.palette = palette

    def closest_color(self, color, mode):
        if len(color) != 3:
            raise ValueError("'color' parameter needs to be 1D array of length 3")

        mode = mode.lower()
        if mode not in ('rgb', 'xyz', 'lab'):
            raise ValueError("'mode' parameter needs to be one of 'RGB', 'XYZ' or 'LAB'")

        if mode == 'xyz':
            color = xyz_to_lab(color)

        if mode == 'rgb':
            color = rgb_to_lab(color)

        min_dist = float("inf")
        best_color = None
        for clr in self.palette:
            color_dist = deltaE_ciede2000(color, clr['lab'])
            if color_dist < min_dist:
                min_dist = color_dist
                best_color = clr

        return best_color, min_dist

    def find(self, image, color_space='sRGB', html_output=None):
        color_space = color_space.lower()
        if color_space not in ('srgb', 'adobe'):
            raise ValueError("'color_space' parameter needs to be one of 'sRGB' or 'Adobe'")

        im = Image.open(image)
        im = downsize_image(im, 300)
        width = im.size[0]
        heigth = im.size[1]

        # if color space is Adobe RGB, convert it to sRGB
        if color_space == 'adobe':
            print 'converting Adobe RGB to sRGB'
            im = im.convert('RGB', (
                0.57667, 0.18556, 0.18823, 0,
                0.29734, 0.62736, 0.07529, 0,
                0.02703, 0.07069, 0.99134, 0,
            ))
            im = im.convert('RGB', (
                3.2406, -1.5372, -0.4986, 0,
                -0.9689, 1.8758, 0.0415, 0,
                0.0557, -0.2040, 1.0570, 0,
            ))

        print "applying mean-shift filter"
        spatial_radius = tune_radius(width, heigth)
        print("calculated spatial radius: %d" % spatial_radius)
        sgm, labels_image, number_regions = segment(im, spatial_radius=spatial_radius,
                                                    range_radius=8, min_density=300)

        # save_image_from_array('after_filter.bmp', sgm)

        # sample pixels
        print("sampling pixels")
        sgm = sgm.reshape(sgm.shape[0] * sgm.shape[1], sgm.shape[2])
        sgm = get_sample(sgm, width, heigth, (width / 40) + 1, (heigth / 40) + 1)
        print("%d pixels sampled" % sgm.shape[0])

        # count pixels w.r.t colors
        print("counting pixels")
        counts = {}
        for pixel in sgm:
            rgbhash = rgb_hash(pixel)
            if rgbhash in counts:
                counts[rgbhash] += 1
            else:
                counts[rgbhash] = 1

        # match colors with the predefined colors
        print("matching found colors with predefined colors")
        colors = {}
        for rgbhash in counts:
            if counts[rgbhash] > sgm.shape[0] * 0.02:
                (color, dist) = self.closest_color(rgb_dehash(rgbhash), 'rgb')
                print color, dist
                if color['label'] in colors:
                    colors[color['label']]['count'] += counts[rgbhash]
                else:
                    colors[color['label']] = {'count': counts[rgbhash], 'lab': color['lab'],
                                              'rgb': lab_to_rgb(color['lab'])}

        # delete colors that have a close neighbour with bigger pixel count
        print("deleting colors that have a close neighbour with bigger pixel count")
        for c1 in colors.keys():
            for c2 in colors.keys():
                if c1 != c2 and c1 in colors.keys() and c2 in colors.keys():
                    dist = deltaE_ciede2000(colors[c1]['lab'], colors[c2]['lab'])
                    if dist < 10.0:
                        if colors[c1]['count'] < colors[c2]['count']:
                            del colors[c1]
                        else:
                            del colors[c2]

        print("processing finished")

        if html_output:
            print("generation html file")
            with codecs.open(html_output, 'w', 'utf-8') as html_file:
                write_to_html(html_file, colors)

        return colors


def tune_radius(width, heigth):
    smaller = width if width < heigth else heigth
    return int(round(150 / sqrt(smaller)))


def save_image_from_array(path, ar):
    fp = open(path, 'w')
    filtered_image = Image.fromarray(ar)
    filtered_image.save(fp)
    fp.close()


def get_sample(ar, width, heigth, step_x, step_y):
    sample = []
    for x in range(0, width, step_x):
        for y in range(0, heigth, step_y):
            sample.append(ar[x * y])
    return scipy.array(sample)


def rgb_hash(rgb):
    return rgb[0] + rgb[1] * 256 + rgb[2] * 65536


def rgb_dehash(rgbhash):
    (b, rgbhash) = divmod(rgbhash, 65536)
    (g, rgbhash) = divmod(rgbhash, 256)
    r = rgbhash
    return [r, g, b]


def downsize_image(im, maxd):
    if im.size[0] > im.size[1]:
        if im.size[0] > maxd:
            w = maxd
            h = w * im.size[1] // im.size[0]
            return im.resize((w, h), Image.BILINEAR)
    else:
        if im.size[1] > maxd:
            h = maxd
            w = h * im.size[0] // im.size[1]
            return im.resize((w, h), Image.BILINEAR)
    return im


def write_to_html(fp, colors):
    html = '<!DOCTYPE html>'
    html += '<html>'
    html += '<head>'
    html += '    <title>Colorfinder Output</title>'
    html += '</head>'
    html += '<body>'
    html += '<div style="float:left;"><table>'
    html += '    <tr><th>Name</th><th>Color</th><th>Count</th></tr>'
    for c in colors.keys():
        rgb = lab_to_rgb(colors[c]['lab'])
        html += '   <tr><td width="200px">%s</td><td width="400px" style="background-color:rgb(%d,%d,%d)"></td><td>%d</td>' \
                % (c, rgb[0], rgb[1], rgb[2], colors[c]['count'])
    html += '</table></div>'
    html += '</body>'
    html += '</html>'
    fp.write(html)


def segment(image, spatial_radius, range_radius, min_density):
    return _pymeanshift.segment(image, spatial_radius, range_radius, min_density, _pymeanshift.SPEEDUP_HIGH)
