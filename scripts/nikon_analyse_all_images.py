"""Analyse all images in an input directory."""

import os
import os.path
import argparse
import logging
import subprocess
import json
import errno

import tifffile

from jicbioimage.core.image import MicroscopyCollection

from plasmodesmata_analysis import __version__
from analyse_all_series import analyse_all

# Setup logging with a stream handler.
logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def convert_to_ome_tiff(input_filename, output_filename):
    """Convert the given file to an OME-TIF file, using bfconvert. If bfconvert
    is not available on the path, an error will be raised."""

    bfconvert = 'bfconvert'

    cmd = [bfconvert, input_filename, output_filename]

    try:
        #p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
        #                     stderr=subprocess.PIPE)
        #stderr = p.stderr.read()
        subprocess.call(cmd)
    except OSError as e:
        msg = 'bfconvert tool not found in PATH\n{}'.format(e)
        raise(RuntimeError(msg))


def generate_manifest_entry(fpath, s, c, z, t):

    entry = {"filename" : fpath,
             "series" : s,
             "channel": c,
             "zslice" : z,
             "timepoint" : t}

    return entry


def split_ome_tif(input_filename, output_path):
    """Split an OME-TIF file into multiple individual images, then create a
    manifest.json file such that these can be read as a jicbioimage
    MicroscopyCollection."""

    all_images_array = tifffile.imread(input_filename)

    components = len(all_images_array.shape)

    if components == 4:
        zdim, cdim, xdim, ydim = all_images_array.shape
    elif components == 3:
        zdim, xdim, ydim = all_images_array.shape
        cdim = 1
    else:
        raise(IndexError("Unexpected OME-TIF image dimensions"))

    entries = []

    s = 0
    t = 0
    for c in range(cdim):
        for z in range(zdim):
            filename_template = "S{}_C{}_Z{}_T{}.tif"
            filename = filename_template.format(s, c, z, t)
            fq_filename = os.path.join(output_path, filename)
            entry = generate_manifest_entry(fq_filename, s, c, z, t)
            entries.append(entry)
            if components == 4:
                image = all_images_array[z,c,:,:]
            else:
                image = all_images_array[z,:,:]
            tifffile.imsave(fq_filename, image)

    manifest_fpath = os.path.join(output_path, 'manifest.json')
    with open(manifest_fpath, 'w') as fh:
        json.dump(entries, fh)

    return manifest_fpath


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise


def convert_and_split(input_filename, backend_path='data/tconv'):
    """Convert the given bioimage file into a directory of TIF files with
    accompanying manifest, suitable for loading into a jicbioimage
    MicroscopyCollection object."""

    fq_backend_path = os.path.join(os.getcwd(), backend_path)

    basename = os.path.basename(input_filename)
    sanified_basename = basename.replace(" ", "_")
    fq_cache_path = os.path.join(fq_backend_path, sanified_basename)

    mkdir_p(fq_cache_path)
    ome_tif_basename = 'converted.ome.tif'
    fq_output_filename = os.path.join(fq_cache_path, ome_tif_basename)

    if not os.path.isfile(fq_output_filename):
        convert_to_ome_tiff(input_filename, fq_output_filename)

    return split_ome_tif(fq_output_filename, fq_cache_path)


def analyse_dir(args):
    """Analyse all images in an input directory."""
    for fname in os.listdir(args.input_dir):
        if not fname.lower().endswith(".nd2"):
            continue
        logger.info("Analysing image: {}".format(fname))

        def get_dir_name(fname):
            no_suffix_list = fname.split(".")[0:-1]
            return ".".join(no_suffix_list)
        dir_name = get_dir_name(fname)
        specific_out_dir = os.path.join(args.output_dir, dir_name)

        # Skip analysis of image if output directory exists.
        if os.path.isdir(specific_out_dir):
            logger.info("Directory exists: {}".format(specific_out_dir))
            logger.info("Skipping: {}".format(fname))
            continue
        os.mkdir(specific_out_dir)

        fpath = os.path.join(args.input_dir, fname)
        manifest_path = convert_and_split(fpath, 'nikon_backend')
        microscopy_collection = MicroscopyCollection(manifest_path)
        analyse_all(microscopy_collection, specific_out_dir, args.threshold,
                    args.min_voxel, args.max_voxel)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("input_dir", help="input directory")
    parser.add_argument("output_dir", help="output directory")
    parser.add_argument("-t", "--threshold",
                        default=500, type=int,
                        help="abs threshold (default=500)")
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
    logger.info("Threshold: {}".format(args.threshold))
    logger.info("Min voxel: {}".format(args.min_voxel))
    logger.info("Max voxel: {}".format(args.max_voxel))

    analyse_dir(args)

if __name__ == "__main__":
    main()
