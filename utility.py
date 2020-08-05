"""
Various utility functions needed by other modules
"""

import subprocess
import logging
import sys
import os


def substitute(input_file, output_file, **data):
    """read in a file, replace some data and write it back out"""
    with open(input_file, 'r') as file:
        filedata = file.read()
    for key, value in data.items():
        filedata = filedata.replace(key, value)
    with open(output_file, 'w') as file:
        file.write(filedata)


def link_file(file, link):
    """delete existing symlink and create a new one"""
    if os.path.isfile(link):
        os.unlink(link)
    else:
        os.symlink(file, link)


def disown(cmd):
    """run a shell command as a background process,
       disown it and suppress any output"""
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)


def setup_logging():
    """Logging config."""
    logging.basicConfig(format=("[%(levelname)s\033[0m] "
                                "%(message)s"),
                        level=logging.INFO,
                        stream=sys.stdout)
    logging.addLevelName(logging.ERROR, '\033[1;31mERROR')
    logging.addLevelName(logging.INFO, '\033[1;32mINFO')
    logging.addLevelName(logging.WARNING, '\033[1;33mWARNING')


def update_theme(theme):
    """reload the plasma theme"""
    disown(["qdbus", "org.kde.kuiserver", "/PlasmaShell",
            "loadLookAndFeelDefaultLayout", theme])
