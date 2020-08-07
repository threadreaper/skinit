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


def get(img):
    """Use colorz to generate color objects"""
    class Color:
        def __init__(self, hex_color):
            self.hex_string = str(hex_color)

        def rgb(self):
            value = self.hex_string.lstrip('#')
            (r, g, b) = [(value[i:i + 2]) for i in range(0, len(value), 2)]
            (r, g, b) = [i.encode(encoding='utf_8') for i in (r, g, b)]
            return int(r, 16), int(g, 16), int(b, 16)

    flags = ["-n 16", "--no-preview"]
    colors = list()
    color = list()
    if shutil.which("colorz"):
        try:
            out = subprocess.check_output(("colorz", img, *flags)).decode('ascii')
            colors[0:15] = [line[0:7] for line in (out.splitlines())]
            color[0:7] = [Color(colors[i]) for i in range(len(colors))]
        except subprocess.CalledProcessError:
            logging.error("colorz returned non-zero exit status."
                          "\n Bad image file or not enough colors?")
        finally:
            return color
    else:
        logging.error("colorz wasn't found on your system.")
        sys.exit(1)


def to_json(wallpaper, colors):
    return {
        "wallpaper": wallpaper,

        "special": {
            "background": colors[0].hex_string,
            "foreground": colors[7].hex_string,
            "cursor": colors[7].hex_string,
        },
        "colors": {
            "color0": colors[0].hex_string,
            "color1": colors[1].hex_string,
            "color2": colors[2].hex_string,
            "color3": colors[3].hex_string,
            "color4": colors[4].hex_string,
            "color5": colors[5].hex_string,
            "color6": colors[6].hex_string,
            "color7": colors[7].hex_string,
            "color8": colors[8].hex_string,
            "color9": colors[9].hex_string,
            "color10": colors[10].hex_string,
            "color11": colors[11].hex_string,
            "color12": colors[12].hex_string,
            "color13": colors[13].hex_string,
            "color14": colors[14].hex_string,
            "color15": colors[15].hex_string,
        }
    }
