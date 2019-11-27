#!/usr/bin/env python

__version__ = "1.0.1"
from array import array
from argparse import ArgumentParser
from PIL import Image


def get_bitmap_value(rgb):
    if rgb[0] > 0 or rgb[1] > 0 or rgb[2] > 0:
        return "1"
    else:
        return "0"


def get_attribute_value(rgb):
    return "{0:b}{1:b}{2:b}".format(rgb[0], rgb[1], rgb[2])


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
    for y in range(h):
        for x in range(0, w, 8):
            column_bits = ""
            for colpart in range(x, x + 8):
                column_bits += get_bitmap_value(image.getpixel((x, y)))
            bloques.append(int(column_bits,2))

    # todo faltaría los atributos

    with open('output.btitle', 'wb') as f:
        f.write(bloques)


if __name__ == "__main__":
    main()

