"""
Generate color palette using colorz
"""
import logging
import shutil
import subprocess
import sys

import export


def palette():
    """Generate a palette from the colors."""
    for i in range(16):
        if i % 8 == 0:
            print()

        if i > 7:
            i = "8;5;%s" % i

        print("\033[4%sm%s\033[0m" % (i, " " * (80 // 20)), end="")

    print("\n")


def gen_colors(img, light):
    """Convert the output from colorz to a list of hex codes"""
    colorz_cmd = has_colorz()
    colors = get(colorz_cmd, img)
    hex_colors = []

    for i, block in enumerate(colors):
        a, b = str(block).split(' ')
        for x in (a, b):
            hex_colors.append(x.replace("'", ""))

    if hex_colors:
        logging.info("Generation complete.")
        export.make_theme_files(img, hex_colors)
        json_colors = colors_to_json(img, hex_colors)
        return json_colors
    else:
        logging.error('Something went wrong')
        sys.exit(0)


#    def adjust(colors, light):
#     """Adjust the generated colors and store them in a dict that
#        we will later save in json format."""
#     raw_colors = colors[:1] + colors[8:16] + colors[8:-1]
#
#     # Manually adjust colors.
#     if light:
#         for color in raw_colors:
#             color = utility.saturate_color(color, 0.5)
#
#         raw_colors[0] = utility.lighten_color(colors[-1], 0.85)
#         raw_colors[7] = colors[0]
#         raw_colors[8] = utility.darken_color(colors[-1], 0.4)
#         raw_colors[15] = colors[0]
#
#     else:
#         # Darken the background color slightly.
#         if raw_colors[0][1] != "0":
#             raw_colors[0] = utility.darken_color(raw_colors[0], 0.40)
#
#         raw_colors[7] = utility.blend_color(raw_colors[7], "#EEEEEE")
#         raw_colors[8] = utility.darken_color(raw_colors[7], 0.30)
#         raw_colors[15] = utility.blend_color(raw_colors[15], "#EEEEEE")
#
#     return raw_colors


def has_colorz():
    """Check to see if the user has colorz installed."""
    if shutil.which("colorz"):
        return "colorz"
    else:
        logging.error("colorz wasn't found on your system.")
        sys.exit(1)


def get(colorz_cmd, img):
    """Use colorz to generate a scheme."""
    flags = ["-n 8", "--no-preview"]
    out = "colorz couldn't generate a scheme. \nNot enough colors?"
    while True:
        try:
            out = subprocess.check_output([colorz_cmd, img, *flags]).splitlines()
        except subprocess.CalledProcessError:
            logging.error("colorz returned non-zero exit status."
                          "\n Bad image file or not enough colors?")
        finally:
            for i, block in enumerate(out):
                out[i] = str(block).lstrip("b")
            return out


def colors_to_json(wallpaper, colors):
    return {
        "wallpaper": wallpaper,

        "special": {
            "background": colors[0],
            "foreground": colors[7],
            "cursor": colors[7],
        },
        "colors": {
            "color0": colors[0],
            "color1": colors[1],
            "color2": colors[2],
            "color3": colors[3],
            "color4": colors[4],
            "color5": colors[5],
            "color6": colors[6],
            "color7": colors[7],
            "color8": colors[8],
            "color9": colors[9],
            "color10": colors[10],
            "color11": colors[11],
            "color12": colors[12],
            "color13": colors[13],
            "color14": colors[14],
            "color15": colors[15],
        }
    }
