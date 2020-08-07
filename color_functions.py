"""
Generate color palette using colorz
"""
import logging
import shutil
import subprocess
import sys


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
        self.hex_string = str(hex_color)
        self.rgb_string = self.rgb()

    def rgb(self):
        """given a hex color code, returns an rgb code"""
        value = self.hex_string.lstrip('#')
        (red, green, blue) = [(value[i:i + 2]) for i in
                              range(0, len(value), 2)]
        (red, green, blue) = [i.encode(encoding='utf_8')
                              for i in (red, green, blue)]
        return int(red, 16), int(green, 16), int(blue, 16)

    def hsv(self):
        """TODO: return hsv color code given hex"""
        red, green, blue = self.rgb_string
        red, green, blue = int(red)/255, int(green)/255, int(blue)/255
        return red, green, blue


def get(img):
    """Use colorz to generate color objects"""
    flags = ["-n 16", "--no-preview"]
    colors = []
    color = []
    error = None
    if shutil.which("colorz"):
        try:
            out = subprocess.check_output(("colorz", img, *flags))\
                                          .decode('ascii')
            colors[0:15] = [line[0:7] for line in out.splitlines()]
            color[0:7] = [Color(colors[i]) for i in range(len(colors))]
        except subprocess.CalledProcessError:
            error = True
            logging.error("colorz returned non-zero exit status."
                          "\n Bad image file or not enough colors?")
            sys.exit(1)
        finally:
            if error:
                sys.exit(1)
    return color
