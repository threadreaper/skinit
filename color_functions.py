"""
Generate color palette using colorz
"""
import logging
import subprocess
import sys
from math import sqrt

from kdtree import KDTree


def palette():
    """Generate a palette from the colors."""
    for i in range(16):
        if i % 8 == 0:
            print()

        if i > 7:
            i = "8;5;%s" % i

        print("\033[4%sm%s\033[0m" % (i, " " * (80 // 20)), end="")
    print("\n")


class Color:
    """Class for colors, exposes methods for retrieving colors
       in various formats"""

    def __init__(self, hex_color):
        self.hex_value = str(hex_color)
        self.rgb_value = self.rgb()
        self.hsv_value = self.hsv()

    def rgb(self):
        """returns color in rgb format"""
        value = self.hex_value.lstrip('#')
        (red, green, blue) = [(value[i:i + 2]) for i in
                              range(0, len(value), 2)]
        (red, green, blue) = [i.encode(encoding='utf_8')
                              for i in (red, green, blue)]
        return int(red, 16), int(green, 16), int(blue, 16)

    def hsv(self):
        """returns color in hsv format"""
        hue, sat, val = (0, 0, 0)
        red, green, blue = self.rgb()
        red, green, blue = int(red) / 255, int(green) / 255, int(blue) / 255
        mx = max(red, green, blue)
        mn = min(red, green, blue)
        diff = mx - mn
        val = mx * 100
        if diff == 0:
            hue = 0
        else:
            if mx == red:
                hue = (60 * ((green - blue) / diff) + 360) % 360
            if mx == green:
                hue = (60 * ((blue - red) / diff) + 120) % 360
            if mx == blue:
                hue = (60 * ((red - green) / diff) + 240) % 360
        if mx == 0:
            sat = 0
        else:
            sat = diff / mx
        return float("{:.2f}".format(hue)), float("{:.2f}".format(sat)), float("{:.2f}".format(val))

    def shade(self, amt):
        """lighten/darken a color by the amount passed to the method"""
        red, green, blue = self.rgb()
        red, green, blue = red + amt, green + amt, blue + amt
        red, green, blue = [0 if color < 0 else 255 if color > 255 else color
                            for color in (red, green, blue)]
        return red, green, blue


def closest_color(rgb, colors):
    red, green, blue = rgb
    color_diffs = []
    for color in colors:
        cr, cg, cb = color
        color_diff = sqrt(abs(red - cr)**2 + abs(green - cg)**2 + abs(blue - cb)**2)
        color_diffs.append((color_diff, color))
    return min(color_diffs)[1]


def sort_colors(rgb, colors):
    """given a single rgb tuple and a list of rgb tuples as arguments:
    returns the list sorted by their proximity to the first given color"""
    tree = KDTree.construct_from_data(colors)
    sorted_colors = tree.query(query_point=rgb, neighbors=len(colors))
    return sorted_colors


def rgb_to_hex(rgb):
    red, green, blue = [(''.join("{:02x}".format(x))) for x in rgb]
    return '#%s%s%s' % (red, green, blue)


def get(img):
    """Use colorz to generate color objects and sort them before returning"""
    flags = ["-n 16", "--no-preview"]
    colors = []
    error = None
    if subprocess.check_output(("which", "colorz")):
        try:
            out = subprocess.check_output(("colorz", img, *flags)) \
                .decode('ascii')
            colors = [line[0:7] for line in out.splitlines()]
            colors = [Color(colors[i]) for i in range(len(colors))]
        except subprocess.CalledProcessError:
            error = True
            logging.error("colorz returned non-zero exit status."
                          "\n Bad image file or not enough colors?")
            sys.exit(1)
        finally:
            if error:
                sys.exit(1)

    if len(colors) < 16:
        logging.error("colorz couldn't get enough colors from the"
                      "selected image file.")
        sys.exit(1)

    colors = [x.rgb_value for x in colors]
    bgcolor = closest_color((0, 0, 0), colors)
    for i, x in enumerate(colors):
        if x == bgcolor:
            colors.pop(i)
            break
    sorted_colors = sort_colors(bgcolor, colors)
    sorted_colors.insert(0, bgcolor)
    colors = [Color(rgb_to_hex(color)) for color in sorted_colors]
    return colors
