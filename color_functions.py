"""
Contains the Color class object which can be instantiated with a
color code in hex string format, such as #FFFFFF.  Extends methods
to return that color's value in hex, or converted to either rgb
or hsv color space.

Also contains functions involved in sorting a list of colors, and
doing other format conversions outside the scope of the Color
class.
"""
import logging
import subprocess
import sys
from math import sqrt


def _palette():
    """Generate a preview palette to be displayed in the terminal."""
    for i in range(16):
        if i % 8 == 0:
            print()
        if i > 7:
            i = "8;5;%s" % i
        print("\033[4%sm%s\033[0m" % (i, " " * (80 // 20)), end="")
    print("\n")


class Color:
    """Class for colors creating color objects, exposes methods for
       retrieving colors in various formats.  Take a color in hex
       string format as its only argument."""

    def __init__(self, hex_color):
        self.hex_value = str(hex_color)
        self.rgb_value = self.rgb()
        self.hsv_value = self.hsv()

    def rgb(self):
        """returns color in rgb format"""
        value = self.hex_value.lstrip('#')
        (r, g, b) = [(value[i:i + 2]) for i in range(0, len(value), 2)]
        (r, g, b) = [i.encode(encoding='utf_8') for i in (r, g, b)]
        return int(r, 16), int(g, 16), int(b, 16)

    def hsv(self):
        """returns color in hsv format"""
        r, g, b = self.rgb()
        r, g, b = int(r) / 255, int(g) / 255, int(b) / 255
        rgb_max, rgb_min = max(r, g, b), min(r, g, b)
        diff = rgb_max - rgb_min
        val = rgb_max * 100
        if diff == 0:
            hue = 0
        else:
            x, y, deg = r, g, 240
            if rgb_max == r:
                x, y, deg = g, b, 360
            if rgb_max == g:
                x, y, deg = b, r, 120
            hue = (60 * ((x - y) / diff) + deg) % 360
        sat = 0 if rgb_max == 0 else diff / rgb_max
        return float("{:.2f}".format(hue)), float("{:.2f}".format(sat)), \
            float("{:.2f}".format(val))

    def shade(self, amt):
        """lighten/darken a color by the amount passed to the method"""
        r, g, b = self.rgb()
        r, g, b = r + amt, g + amt, b + amt
        r, g, b = [0 if color < 0 else 255 if color > 255 else color
                   for color in (r, g, b)]
        return r, g, b


def take_out(item, item_list):
    """the first argument is a list member, second is the list
    function will remove the selected item from the list without
    needing to know its index"""
    for i, x in enumerate(item_list):
        if x == item:
            item_list.pop(i)
            break
    return item_list


def closest_color(rgb, colors):
    """given a single rgb tuple and a list of rgb tuples as arguments,
    returns the color in the list closest to the specified color"""
    r, g, b = rgb
    color_diffs = []
    for color in colors:
        r_prime, g_prime, b_prime = color
        color_diff = sqrt(abs(r - r_prime)**2 + abs(g - g_prime)**2
                          + abs(b - b_prime)**2)
        color_diffs.append((color_diff, color))
    return min(color_diffs)[1]


def sort_colors(rgb, colors):
    """given a single rgb tuple and a list of rgb tuples as arguments:
    attempts to sort colors in 'order' starting with the color given
    in the first argument -- not perfect"""

    sorted_colors = []
    sorted_colors.insert(0, rgb)
    x = len(colors)
    for i in range(len(colors)):
        if i < x:
            sorted_colors.insert(i+1, (closest_color(sorted_colors[i],
                                                     colors)))
            colors = take_out(sorted_colors[i+1], colors)
    return sorted_colors


def rgb_to_hex(rgb):
    """given an rgb tuple color code, returns equivalent hex code"""
    r, g, b = [(''.join("{:02x}".format(x))) for x in rgb]
    return '#%s%s%s' % (r, g, b)


def get(img):
    """Use colorz to generate color objects and sort them before returning"""
    flags = ["-n 8", "--no-preview"]
    colors = []
    error = None
    if subprocess.check_output(("which", "colorz")):
        try:
            out = subprocess.check_output(("colorz", img, *flags)) \
                .decode('ascii')
            colors = []
            for line in out.splitlines():
                colors.append(Color(line[0:7]))
                colors.append(Color(line[9:15]))
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
    fgcolor = closest_color((255, 255, 255), colors)
    colors = take_out(fgcolor, colors)
    colors = sort_colors(bgcolor, colors)
    colors.insert(7, fgcolor)
    colors = [Color(rgb_to_hex(color)) for color in colors]
    return colors
