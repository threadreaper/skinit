"""
This script handles all of the output, wallpaper, theme files, etc.
"""
import glob
import os
import subprocess
import logging

from utility import open_write, link_file, substitute,\
    plasma_shell, notifications, OS, disown
from color_functions import palette, Color


def make_theme_files(img, colors):
    """ Generates a config file of some type based on a template
    found in the templates folder.  Gets important info
    from the first two lines of the .skinit file:
       1) Full destination path and filename
       2) Type of color code required
    In this way, support is provided for users to apply
    themes to any application that loads any sort of
    color configuration from text-based config files by
    creating their own compatible template and telling
    SkinIt where to copy it out to.
    """
    os.chdir("templates")
    for file in glob.glob("*.skinit"):
        with open(file, 'r') as _input:
            lines = _input.readlines()
            _output = lines[0].rstrip('\n')
            color_type = lines[1].rstrip('\n')
            theme_data = {'[wallpaper]': img}
        if color_type == 'hex':
            for i, color in enumerate(colors):
                theme_data = {**theme_data, ('[color%s]' % i):
                              color.hex_value}
            offset = len(lines[0]) + len(lines[1])
            with open(file, 'r') as _input:
                _input.seek(offset)
                line = _input.read()
            for key, value in theme_data.items():
                line = line.replace(key, value)
            open_write(line, _output)
        elif color_type == 'rgb':
            for i, color in enumerate(colors):
                theme_data = {**theme_data, ('[color%s]' % i):
                              str(color.rgb_value)}
            offset = len(lines[0]) + len(lines[1])
            with open(file, 'r') as _input:
                _input.seek(offset)
                line = _input.read()
            for key, value in theme_data.items():
                line = line.replace(key, value)
            open_write(line, _output)
    update_theme('SkinIt')


def export_wallpaper(img, splash):
    """change desktop and login screen wallpaper"""
    if splash:
        file_name = str(os.path.split(img))

        link = "./look-and-feel/skinit/contents/splash/images/" + file_name
        link_file(img, link)

        splash_temp = "./look-and-feel/skinit/contents/splash/Splash.template"
        splash_qml = "./look-and-feel/skinit/contents/splash/Splash.qml"

        data = {"replace_string": file_name}
        substitute(splash_temp, splash_qml, **data)

    else:
        string = """var allDesktops = desktops();for (i=0;i<allDesktops.length;i++){
                 d = allDesktops[i];d.wallpaperPlugin = "org.kde.image";
                 d.currentConfigGroup = Array("Wallpaper", "org.kde.image",
                 "General");d.writeConfig("Image", "%s")};"""

        plasma_shell.evaluateScript(string % img)
        notifications.Notify('SkinIt!', 0, '', 'Wallpaper updated!',
                             ('<i>%s</i>' % img), [], {}, 5000)


def set_special(index, color, iterm_name="h", alpha=100):
    """Convert a hex color to a special sequence."""
    if OS == "Darwin" and iterm_name:
        return "\033]P%s%s\033\\" % (iterm_name, color.strip("#"))
    if index in [11, 708] and alpha != "100":
        return "\033]%s;[%s]%s\033\\" % (index, alpha, color)
    return "\033]%s;%s\033\\" % (index, color)


def set_color(index, color):
    """Convert a hex color to a terminal color sequence."""
    if OS == "Darwin" and index < 20:
        return "\033]P%1x%s\033\\" % (index, color.hex_value.strip("#"))
    return "\033]4;%s;%s;\033\\" % (index, color.hex_value)


def set_iterm_tab_color(color):
    """Set iTerm2 tab/window color"""
    rgb_color = Color(color)
    return ("\033]6;1;bg;red;brightness;%s\a"
            "\033]6;1;bg;green;brightness;%s\a"
            "\033]6;1;bg;blue;brightness;%s\a") % rgb_color.rgb()


def create_sequences(colors, vte_fix=False):
    """Create the escape sequences."""
    # Colors 0-15.
    sequences = [set_color(index, colors[index]) for index in range(16)]

    # Special colors.
    # Source: https://goo.gl/KcoQgP
    # 10 = foreground, 11 = background, 12 = cursor foregound
    # 13 = mouse foreground, 708 = background border color.
    sequences.extend([
        set_special(10, colors[7], "g"),
        set_special(11, colors[0], "h"),
        set_special(12, colors[7], "l"),
        set_special(13, colors[7], "j"),
        set_special(17, colors[7], "k"),
        set_special(19, colors[0], "m"),
        set_color(232, colors[0]),
        set_color(256, colors[7]),
        set_color(257, colors[0]),
    ])

    if not vte_fix:
        sequences.extend(
            set_special(708, colors[0], "")
        )
    if OS == "Darwin":
        sequences += set_iterm_tab_color(colors[0])
    return "".join(sequences)


def send(colors, to_send=True, vte_fix=False, quiet=False):
    """Send colors to all open terminals."""
    if not quiet:
        palette()
    # Writing to "/dev/pts/[0-9] lets you send data to open terminals.
    if to_send:
        tty_pattern = "/dev/ttys00[0-9]*" if OS == "Darwin" else "/dev/pts/[0-9]*"
        sequences = create_sequences(colors, vte_fix)
        for term in glob.glob(tty_pattern):
            open_write(sequences, term)


def update_theme(theme):
    """reload the plasma theme - from cli lookandfeeltool &
    lookandfeeltool --platformtheme  also .config/plasmarc
    rm .cache/plasma* -R to clear plasma cache and
    plasmashell --replace
    store in /.local/share/plasma/desktoptheme/
    TODO: loadlookandfeel resets our wallpaper!!  figure that out"""
    home = os.environ['HOME']

    try:
        disown('rm %s/.cache/plasma* -R' % home)
    except subprocess.CalledProcessError as e:
        if 'FileNotFoundError' in e.output:
            logging.info('Nothing to delete in Plasma cache... bypassing')
    finally:
        try:
            disown('plasmashell --replace')
        except subprocess.CalledProcessError as e:
            if 'FileNotFoundError' in e.output:
                logging.info('No plasma shell to restart, do you have Plasma installed?')
        finally:
            return()
