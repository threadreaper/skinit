"""
Theme Generator for KDE 5 Plasma
Michael Podrybau
email: threadreaper@gmail.com
https://github.com/threadreaper
"""

import argparse
import sys
import logging
import os

from pywal import image
from pywal import colors

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

    arg.add_argument("--saturate", metavar="0.0-1.0",
                     help="Set the color saturation.")

    arg.add_argument("--backend", metavar="backend",
                     choices=["colorz", "colorthief", "schemer2",
                              "wal", "haishoku", "list_backends"],
                     help="Which color backend to use. \
                           Use 'skinit --backend' to list backends.",
                     const="list_backends", type=str, nargs="?")

    arg.add_argument("-s", action="store_true",
                     help="Also set the splash (login) screen wallpaper.")

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

    if not args.i and \
       not args.backend:
        parser.error("No input specified.\n"
                     "--backend or -i is required.")
        sys.exit(0)

    if args.backend == "list_backends":
        print("\n - ".join(["\033[1;32mBackends\033[0m:",
                            *colors.list_backends()]))
        sys.exit(0)


def parse_args(parser):
    """Process args"""
    args = parser.parse_args()

    if args.i:
        img = image.get(args.i, "false", "false")
        colors_plain = colors.get(img, args.l, args.backend,
                                  sat=args.saturate)
        export.export_wallpaper(img, args.s)

    if sys.stdout.isatty():
        colors.palette()

    if args.q:
        logging.getLogger().disabled = True
        sys.stdout = sys.stderr = open(os.devnull, 'w')

    if args.r:
        utility.update_theme(args.r)
        logging.info("Switching theme to %s.", args.r)


def main():
    """Main script function."""
    utility.setup_logging()
    parser = get_args()

    parse_args_exit(parser)
    parse_args(parser)


if __name__ == "__main__":
    main()
