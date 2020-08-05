"""
functions related to changing the wallpaper and outputting
various theme files
"""
import os
import logging
import utility


def export_wallpaper(img, splash):
    """change desktop and login screen wallpaper"""
    file_name = os.path.basename(img)

    if splash:
        link = "./look-and-feel/skinit/contents/splash/images/" + file_name
        utility.link_file(img, link)

        splash_temp = "./look-and-feel/skinit/contents/splash/Splash.template"
        splash_qml = "./look-and-feel/skinit/contents/splash/Splash.qml"

        data = {"replace_string": file_name}
        utility.substitute(splash_temp, splash_qml, **data)

    elif not splash:
        logging.info("Bypassed setting splash screen wallpaper.")

    string = """
        var allDesktops = desktops();for (i=0;i<allDesktops.length;i++){
        d = allDesktops[i];d.wallpaperPlugin = "org.kde.image";
        d.currentConfigGroup = Array("Wallpaper", "org.kde.image",
        "General");d.writeConfig("Image", "%s")};"""

    utility.disown(["qdbus", "org.kde.plasmashell", "/PlasmaShell",
                    "org.kde.PlasmaShell.evaluateScript", string % img])
