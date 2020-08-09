"""
Various utility functions needed by other modules
"""
import subprocess
import logging
import sys
import os
import platform


OS = platform.uname()[0]


def open_read(_input):
    with open(_input, 'r') as file:
        return file.read()


def open_write(_data, _output):
    with open(_output, 'w') as file:
        file.writelines(_data)


def substitute(input_file, output_file, **data):
    filedata = open_read(input_file)
    for key, value in data.items():
        filedata = filedata.replace(key, value)
    open_write(output_file, filedata)


def create_dir(directory):
    """Called whenever we need to make a directory"""
    os.makedirs(directory, exist_ok=True)


"""deprecated
def save_file_json(img, _colors, export_file):

    json_colors = color_functions.to_json(img, _colors)
    with open(export_file, "w") as file:
        json.dump(json_colors, file, indent=4)
"""


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


def get_image(img):
    """Validate image input."""
    if os.path.isfile(img):
        return img
    else:
        logging.error("No valid image file found.")
        sys.exit(1)
