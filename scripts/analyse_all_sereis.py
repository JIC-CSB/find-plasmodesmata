"""Analyse all series."""

import os
import os.path
import argparse
import logging

from jicbioimage.core.io import AutoName

from find_plasmodesmata import get_microscopy_collection, find_plasmodesmata, __version__


# Setup logging with a stream handler.
logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

def analyse_all(microscopy_collection, output_dir, max_size, min_size):
    """Analyse all series in input microscopy file."""
    for s in microscopy_collection.series:
        sub_dir = os.path.join(output_dir, str(s))
        if not os.path.isdir(sub_dir):
            os.mkdir(sub_dir)

        AutoName.directory = sub_dir


        logger.info("Analysing series {}".format(s))
        zstack = microscopy_collection.zstack_array(s=s)
        find_plasmodesmata(zstack, max_size, min_size)
    

def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("input_file", help="path to raw microscopy data")
    parser.add_argument("output_dir", help="output directory")
    parser.add_argument("-l", "--max_size",
        default=100, type=int, help="maximum number of pixels (default=100)")
    parser.add_argument("-s", "--min_size",
        default=2, type=int, help="minimum number of pixels (default=2)")
    args = parser.parse_args()

    specific_out_dir = os.path.join(args.output_dir,
        os.path.basename(args.input_file).split(".")[0])

    if not os.path.isdir(args.output_dir):
        os.mkdir(args.output_dir)
    if not os.path.isdir(specific_out_dir):
        os.mkdir(specific_out_dir)
    if not os.path.isfile(args.input_file):
        parser.error("No such microscopy file: {}".format(args.input_file))

    # Create file handle logger.
    fh = logging.FileHandler(os.path.join(specific_out_dir, "log"), mode="w")
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    logger.info("Script version          : {}".format(__version__))


    microscopy_collection = get_microscopy_collection(args.input_file)
    analyse_all(microscopy_collection, specific_out_dir, args.max_size, args.min_size)

if __name__ == "__main__":
    main()
