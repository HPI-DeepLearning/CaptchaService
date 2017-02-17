from __future__ import print_function
import os
import sys
import math
import numpy as np
import random

from decimal import *
from PIL import Image, ImageDraw

import scipy
import scipy.misc
import scipy.cluster


def wave_transformation(input_data, output_data, width, height):
    # slight randomisation for frequency
    frequency_modifier = Decimal(random.uniform(0.6, 0.8) * (width / height))
    frequency = frequency_modifier * \
        (Decimal(1) / Decimal((width / 2))) * Decimal(math.pi)

    # slight randomisation for amplitude
    amplitude_modifier = random.uniform(5, 7)
    amplitude = (height / amplitude_modifier)

    for x in range(width):
        for y in range(height):
            shift = math.sin(frequency * x) * amplitude
            new_y = y + shift
            if new_y < height and new_y > 0:
                output_data[x, y] = input_data[x, new_y]
            # in case pixel would be shifted out of bounds it is replaced with
            # the pixel at the bottom or top
            elif shift < 0:
                output_data[x, y] = input_data[x, 0]
            elif shift >= 0:
                output_data[x, y] = input_data[x, (height - 1)]


def find_dominant_color(input_img):
    NUM_CLUSTERS = 5

    image_array = scipy.misc.fromimage(
        input_img)  # numpy array from input image
    shape = image_array.shape
    image_array = image_array.reshape(scipy.product(shape[:2]), shape[2])

    codes, distortion = scipy.cluster.vq.kmeans(
        image_array.astype(float), NUM_CLUSTERS)

    vecs, distortion = scipy.cluster.vq.vq(image_array, codes)
    counts, bins = scipy.histogram(vecs, len(codes))

    index_max = scipy.argmax(counts)
    peak = codes[index_max].astype(int)

    return tuple(peak)


def processImage(file_path):
    input_img = Image.open(file_path)
    input_data = input_img.load()

    width = input_img.size[0]
    height = input_img.size[1]
    dominant_color = find_dominant_color(input_img)

    output_img = Image.new("RGB", input_img.size, "white")
    output_data = output_img.load()

    draw = ImageDraw.Draw(input_img)
    draw.line((0, height / 2, width - 1, height / 2),
              fill=dominant_color, width=height / 10)

    wave_transformation(input_data, output_data, width, height)

    if len(sys.argv) > 2:
        if sys.argv[2] == "show":
            input_img.show()
            output_img.show()

    return output_img


def main():
    infile = sys.argv[1]
    name, ending = os.path.splitext(infile)
    outfile = name + "_new" + ending

    output_img = processImage(infile)

    output_img.save(outfile)


if __name__ == "__main__":
    main()
