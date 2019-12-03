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
    if (rgb[0] == rgb[1] == rgb[2]) and rgb[0] != 0:
        return "0"
    else:
        return "1"


def _rgb_no_bright(value):
    return 160 <= value <= 220


def _rgb_bright(value):
    return value > 220


def get_attribute_value(rgb):

    # quick and dirty rgb map
    if rgb[0] == 0 and rgb[1] == 0 and rgb[2] == 0:
        ink = "0100"
    elif rgb[0] < 2 and rgb[1] < 2 and _rgb_no_bright(rgb[2]):
        ink = "1000"
    elif _rgb_no_bright(rgb[0]) and rgb[1] < 2 and rgb[2] < 2:
        ink = "0001"
    elif _rgb_no_bright(rgb[0]) and rgb[1] < 1 and rgb[2] > 70:
        ink = "1010"
    elif rgb[0] < 2 and _rgb_no_bright(rgb[1]) and rgb[2] < 2:
        ink = "0010"
    elif rgb[0] < 2 and _rgb_no_bright(rgb[1]) and rgb[2] > 70:
        ink = "1100"
    elif rgb[0] > 70 and _rgb_no_bright(rgb[1]) and rgb[2] < 2:
        ink = "0011"
    elif _rgb_no_bright(rgb[0]) and _rgb_no_bright(rgb[1]) and _rgb_no_bright(rgb[2]):
        ink = "1110"
    # todo bright cases
    elif rgb[0] < 2 and rgb[1] < 2 and _rgb_bright(rgb[2]):
        ink = "1000"
    elif _rgb_bright(rgb[0]) and rgb[1] < 2 and rgb[2] < 2:
        ink = "0101"
    elif _rgb_bright(rgb[0]) and rgb[1] < 1 and rgb[2] > 70:
        ink = "1010"
    elif rgb[0] < 2 and _rgb_bright(rgb[1]) and rgb[2] < 2:
        ink = "0110"
    elif rgb[0] < 2 and _rgb_bright(rgb[1]) and rgb[2] > 70:
        ink = "1100"
    elif rgb[0] > 70 and _rgb_bright(rgb[1]) and rgb[2] < 2:
        ink = "0111"
    elif _rgb_bright(rgb[0]) and _rgb_bright(rgb[1]) and _rgb_bright(rgb[2]):
        ink = "1110"
    else:
        ink = "0011"

    return ink


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

    mask = None

    # Byte 1: bitmap value for 1st pixel line, 1st column (0-8)
    bloques = array('B')
    b_count = 1

    # todo what about larger images?
    for y in range(16):
        for x in range(0, 16, 8):
            column_bits = ""
            for colpart in range(x, x + 8):
                column_bits += get_bitmap_value(image.getpixel((colpart, y)))

            bloques.append(int(column_bits, 2))
            print("{}: bitmap value for {} pixel line, and columnn {} to {}: {}".format(b_count, y, x, x+8, hex(int(column_bits, 2))))

            b_count += 1

    for x in range(0, 16, 8):
        for y in range(0, 16, 2):
            # Byte 33: attribute value for 1st and 2nd pixel line, 1st column
            column_bits = ""
            pixelline_one = get_attribute_value(image.getpixel((x, y)))
            pixelline_two = get_attribute_value(image.getpixel((x, y + 1)))
            column_bits = pixelline_one + pixelline_two
            if pixelline_one == '1110' and pixelline_two == '1110':
                column_bits = "00111000"
            print("{}: Attr value for {} and {} pixel line, column {}: {}".format(b_count, y, y + 1, x,
                                                                                  hex(int(column_bits, 2))))
            bloques.append(int(column_bits, 2))
            b_count += 1

    with open('output.btile', 'wb') as f:
        f.write(bloques)


if __name__ == "__main__":
    main()

