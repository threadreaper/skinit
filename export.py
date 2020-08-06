"""
This script handles all of the output, wallpaper, theme files, etc.
"""
import glob
import logging
import os

import utility


def make_theme_files(img, colors):
    utility.save_file_json(img, colors, "templates/colors.json")
    utility.open_write(colors, "templates/colors")


def export_wallpaper(img, splash):
    """change desktop and login screen wallpaper"""
    file_name = str(os.path.split(img))

    if splash:
        link = "./look-and-feel/skinit/contents/splash/images/" + file_name
        utility.link_file(img, link)

        splash_temp = "./look-and-feel/skinit/contents/splash/Splash.template"
        splash_qml = "./look-and-feel/skinit/contents/splash/Splash.qml"

        data = {"replace_string": file_name}
        utility.substitute(splash_temp, splash_qml, **data)

    else:
        logging.info("Bypassed setting splash screen wallpaper.")

    string = """
        var allDesktops = desktops();for (i=0;i<allDesktops.length;i++){
        d = allDesktops[i];d.wallpaperPlugin = "org.kde.image";
        d.currentConfigGroup = Array("Wallpaper", "org.kde.image",
        "General");d.writeConfig("Image", "%s")};"""

    utility.disown(["qdbus", "org.kde.plasmashell", "/PlasmaShell",
                    "org.kde.PlasmaShell.evaluateScript", string % img])


def set_special(index, color, iterm_name="h", alpha=100):
    """Convert a hex color to a special sequence."""
    if utility.OS == "Darwin" and iterm_name:
        return "\033]P%s%s\033\\" % (iterm_name, color.strip("#"))

    if index in [11, 708] and alpha != "100":
        return "\033]%s;[%s]%s\033\\" % (index, alpha, color)
    else:
        return "\033]%s;%s\033\\" % (index, color)


def set_color(index, color):
    """Convert a hex color to a text color sequence."""
    if utility.OS == "Darwin" and index < 20:
        return "\033]P%1x%s\033\\" % (index, color.strip("#"))

    return "\033]4;%s;%s\033\\" % (index, color)


#    def set_iterm_tab_color(color):
#   """Set iTerm2 tab/window color"""
#   return ("\033]6;1;bg;red;brightness;%s\a"
#            "\033]6;1;bg;green;brightness;%s\a"
#            "\033]6;1;bg;blue;brightness;%s\a") % (*utility.hex_to_rgb(color),)


def create_sequences(colors, vte_fix=False):
    """Create the escape sequences."""

    # Colors 0-15.
    sequences = [set_color(index, colors["colors"]["color%s" % index])
                 for index in range(16)]

    # Special colors.
    # Source: https://goo.gl/KcoQgP
    # 10 = foreground, 11 = background, 12 = cursor foregound
    # 13 = mouse foreground, 708 = background border color.
    sequences.extend([
        set_special(10, colors["special"]["foreground"], "g"),
        set_special(11, colors["special"]["background"], "h"),
        set_special(12, colors["special"]["cursor"], "l"),
        set_special(13, colors["special"]["foreground"], "j"),
        set_special(17, colors["special"]["foreground"], "k"),
        set_special(19, colors["special"]["background"], "m"),
        set_color(232, colors["special"]["background"]),
        set_color(256, colors["special"]["foreground"]),
        set_color(257, colors["special"]["background"]),
    ])

    if not vte_fix:
        sequences.extend(
            set_special(708, colors["special"]["background"], "")
        )
#    if utility.OS == "Darwin":
#       sequences += set_iterm_tab_color(colors["special"]["background"])
    return "".join(sequences)


def send(colors, to_send=True, vte_fix=False):
    """Send colors to all open terminals."""
    sequences = create_sequences(colors, vte_fix)

    # Writing to "/dev/pts/[0-9] lets you send data to open terminals.
    if to_send:
        if utility.OS == "Darwin":
            tty_pattern = "/dev/ttys00[0-9]*"
        else:
            tty_pattern = "/dev/pts/[0-9]*"
        for term in glob.glob(tty_pattern):
            utility.open_write(sequences, term)
            logging.info("Set terminal colors.")
