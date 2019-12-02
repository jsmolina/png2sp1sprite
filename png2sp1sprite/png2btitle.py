#!/usr/bin/env python

__version__ = "0.0.1"
import math
from array import array
from argparse import ArgumentParser
from PIL import Image
RGB_COLOR_COUNT = 256
GRAYSCALE_COLOR_COUNT = 256

def get_int_from_rgb(rgb):
    if isinstance(rgb, tuple):
        red = rgb[0]
        green = rgb[1]
        blue = rgb[2]
        rgb_int = (red<<16) + (green<<8) + blue
        return rgb_int
    else:
        return rgb


def get_bitmap_value(rgb):
    if get_int_from_rgb(rgb) > 0:
        return "1"
    else:
        return "0"


def get_attribute_value(rgb):
    value = get_int_from_rgb(rgb)
    if value > 15:
        print("WARNING! got color value of {0}, downgrading to 15".format(value))
        value = 15
    attr = "{0:b}".format(value)
    return attr


def changeColorDepth(image, colorCount):
    if image.mode == 'L':
        raito = GRAYSCALE_COLOR_COUNT / colorCount
        change = lambda value: math.trunc(value / raito) * raito
        return image.point(change)

    if image.mode == 'RGB' or image.mode == 'RGBA':
        raito = RGB_COLOR_COUNT / colorCount
        change = lambda value: math.trunc(value / raito) * raito
        return Image.eval(image, change)

    raise ValueError('{mode} error'.format(mode=image.mode))


def main():
    animated = False

    parser = ArgumentParser(description="png2sp1sprite",
                            epilog="Copyright (C) 2019 Jordi Sesmero",
                            )

    parser.add_argument("--version", action="version", version="%(prog)s "  + __version__)
    parser.add_argument("--convert", action="store_true", default=False)

    parser.add_argument("image", help="image to convert", nargs="?")

    args = parser.parse_args()

    if not args.image:
        parser.error("required parameter: image")

    try:
        image = Image.open(args.image)
        (w, h) = image.size
    except IOError:
        parser.error("failed to open the image")
        exit(1)
        return

    convert = args.convert
    mask = None

    # force 8 bit per pixel
    if convert:
        image = image = image.convert('P')
    # Byte 1: bitmap value for 1st pixel line, 1st column (0-8)
    bloques = array('B')

    # todo what about larger images?
    for y in range(16):
        for x in range(0, 16, 8):
            column_bits = ""
            for colpart in range(x, x + 8):
                column_bits += get_bitmap_value(image.getpixel((x, y)))
            bloques.append(int(column_bits, 2))

    for x in range(0, 16, 8):
        for y in range(0, 16, 2):
            # Byte 33: attribute value for 1st and 2nd pixel line, 1st column
            column_bits = ""
            pixelline_one = get_attribute_value(image.getpixel((x, y)))
            pixelline_two = get_attribute_value(image.getpixel((x, y + 1)))
            column_bits = pixelline_one + pixelline_two

            bloques.append(int(column_bits, 2))

    with open('output.btitle', 'wb') as f:
        f.write(bloques)


if __name__ == "__main__":
    main()

