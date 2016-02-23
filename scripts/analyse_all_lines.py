"""Analyse all series in subdirectories of an input directory."""

import os
import os.path
import argparse
import logging

from plasmodesmata_analysis import (
    __version__
)
from analyse_all_images import analyse_dir

# Setup logging with a stream handler.
logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def analyse_line(args):
    """Analyse all series in subdirectories of an input directory."""
    input_dir = args.input_dir
    output_dir = args.output_dir
    for directory in os.listdir(input_dir):
        logger.info("Analysing directory: {}".format(directory))

        specific_out_dir = os.path.join(output_dir, directory)
        if not os.path.isdir(specific_out_dir):
            os.mkdir(specific_out_dir)

        args.input_dir = os.path.join(input_dir, directory)
        args.output_dir = specific_out_dir
        analyse_dir(args)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("input_dir", help="input directory")
    parser.add_argument("output_dir", help="output directory")
    parser.add_argument("-t", "--threshold",
                        default=15000, type=int,
                        help="abs threshold (default=20000)")
    parser.add_argument("--min-voxel", default=2, type=int,
                        help="Minimum voxel volume (default=2)")
    parser.add_argument("--max-voxel", default=50, type=int,
                        help="Maximum voxel volume (default=50)")
    args = parser.parse_args()

    if not os.path.isdir(args.output_dir):
        os.mkdir(args.output_dir)

    # Create file handle logger.
    fh = logging.FileHandler(os.path.join(args.output_dir, "log"), mode="w")
    fh.setLevel(logging.DEBUG)
    format_ = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(format_)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    logger.info("Script version: {}".format(__version__))

    analyse_line(args)


if __name__ == "__main__":
    main()
