"""
SkinIt! Theme Generator for KDE 5 Plasma
Michael Podrybau
email: threadreaper@gmail.com
https://github.com/threadreaper
"""

import argparse
import sys
import logging
import os

import color_functions
import utility
import export


def get_args():
    """Get command line arguments"""
    description = "SkinIt! - Automagically generate Plasma themes!"
    arg = argparse.ArgumentParser(description=description)

    arg.add_argument("-i", metavar="\"/path/to/image\"",
                     help="Image file to use for theme generation.")

    arg.add_argument("-l", action="store_true",
                     help="Generate a light colorscheme.")

    arg.add_argument("--vte", action="store_true",
                     help="Fix text-artifacts printed in VTE terminals.")

    arg.add_argument("-s", action="store_true",
                     help="Also set the splash (login) screen wallpaper.")

    arg.add_argument("-p", action="store_true",
                     help="Display a preview of the current color scheme.")

    arg.add_argument("-q", action="store_true",
                     help="Quiet mode, don't output anything to the terminal.")

    arg.add_argument("-r", metavar="[name of theme]",
                     help="Switch Plasma theme")

    return arg


def parse_args_exit(parser):
    """Process args that exit."""
    args = parser.parse_args()

    if len(sys.argv) <= 1:
        parser.print_help()
        sys.exit(1)

    if args.p and args.q:
        logging.error("-p and -q are incompatible.")
        parser.print_help()
        sys.exit(1)

    if args.p:
        color_functions.palette()
        sys.exit(0)

    if args.r:
        export.update_theme(args.red)
        logging.info("Switching theme to %s.", args.red)


def parse_args(parser):
    """Process args"""
    args = parser.parse_args()

    if args.i:
        img = utility.get_image(args.i)
        export.export_wallpaper(img, args.s)
        colors = color_functions.get(args.i)
        export.make_theme_files(img, colors)
        export.send(colors, to_send=not args.s, vte_fix=args.vte, quiet=args.q)

    if args.q:
        logging.getLogger().disabled = True
        sys.stdout = sys.stderr = open(os.devnull, 'w')


def main():
    """Main script function."""
    utility.setup_logging()
    parser = get_args()

    parse_args_exit(parser)
    parse_args(parser)


if __name__ == "__main__":
    main()
