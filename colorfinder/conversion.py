def srgb_to_xyz(rgb):
    r = rgb[0] / 255
    g = rgb[1] / 255
    b = rgb[2] / 255

    if r > 0.04045:
        r = ((r + 0.055) / 1.055) ** 2.4
    else:
        r /= 12.92
    if g > 0.04045:
        g = ((g + 0.055) / 1.055) ** 2.4
    else:
        g /= 12.92
    if b > 0.04045:
        b = ((b + 0.055) / 1.055) ** 2.4
    else:
        b /= 12.92

    r *= 100
    g *= 100
    b *= 100

    x = r * 0.4124 + g * 0.3576 + b * 0.1805
    y = r * 0.2126 + g * 0.7152 + b * 0.0722
    z = r * 0.0193 + g * 0.1192 + b * 0.9505
    return [x, y, z]


def xyz_to_lab(xyz):
    x = xyz[0] / 95.047
    y = xyz[1] / 100.000
    z = xyz[2] / 108.883

    if x > 0.008856:
        x **= 1 / 3
    else:
        x = (7.787 * x) + (16 / 116)
    if y > 0.008856:
        y **= 1 / 3
    else:
        y = (7.787 * y) + (16 / 116)
    if z > 0.008856:
        z **= 1 / 3
    else:
        z = (7.787 * z) + (16 / 116)

    l = (116 * y) - 16
    a = 500 * (x - y)
    b = 200 * (y - z)
    return [l, a, b]


def lab_to_xyz(lab):
    y = (lab[0] + 16) / 116
    x = lab[1] / 500 + y
    z = y - lab[2] / 200

    if y ** 3 > 0.008856:
        y **= 3
    else:
        y = (y - 16 / 116) / 7.787
    if x ** 3 > 0.008856:
        x **= 3
    else:
        x = (x - 16 / 116) / 7.787
    if z ** 3 > 0.008856:
        z **= 3
    else:
        z = (z - 16 / 116) / 7.787

    return [95.047 * x, 100.000 * y, 108.883 * z]


def xyz_to_srgb(xyz):
    x = xyz[0] / 100
    y = xyz[1] / 100
    z = xyz[2] / 100

    r = x * 3.2406 + y * -1.5372 + z * -0.4986
    g = x * -0.9689 + y * 1.8758 + z * 0.0415
    b = x * 0.0557 + y * -0.2040 + z * 1.0570

    if r > 0.0031308:
        r = 1.055 * (r ** (1 / 2.4)) - 0.055
    else:
        r *= 12.92
    if g > 0.0031308:
        g = 1.055 * (g ** (1 / 2.4)) - 0.055
    else:
        g *= 12.92
    if b > 0.0031308:
        b = 1.055 * (b ** (1 / 2.4)) - 0.055
    else:
        b *= 12.92

    return [r * 255, g * 255, b * 255]


def lab_to_srgb(lab):
    return xyz_to_srgb(lab_to_xyz(lab))


def srgb_to_lab(rgb):
    return xyz_to_lab(srgb_to_xyz(rgb))
