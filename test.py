from colorfinder import find_colors
import os

samples = ['371', '372', '373', '374', '375', '376', '506', '510', '511', '517', '521', '522', '568']
samples_path = os.path.join(os.path.dirname(__file__), 'samples')

for sample in samples:
    fp = open(os.path.join(samples_path, sample))
    find_colors(fp, color_space='Adobe', html_output=os.path.join(samples_path, "colors_%s.html" % sample))
    fp.close()