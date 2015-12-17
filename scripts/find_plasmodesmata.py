"""Find plasmodesmata."""

import os.path
import argparse
import logging

import numpy as np
import scipy.misc
import skimage.measure

from jicbioimage.core.io import FileBackend, AutoName
from jicbioimage.core.image import DataManager, SegmentedImage, Image
from jicbioimage.core.transform import transformation
from jicbioimage.core.util.array import dtype_contract, normalise
from jicbioimage.core.util.color import pretty_color

from jicbioimage.transform import (
    max_intensity_projection,
    threshold_otsu,
    remove_small_objects,
)

__version__ = "0.5.1"

HERE = os.path.dirname(os.path.realpath(__file__))

# Setup logging with a stream handler.
logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def get_microscopy_collection(input_file):
    """Return microscopy collection from input file."""
    data_dir = os.path.abspath(os.path.join(HERE, "..", "data"))
    if not os.path.isdir(data_dir):
        os.mkdir(data_dir)
    backend_dir = os.path.join(data_dir, 'unpacked')
    file_backend = FileBackend(backend_dir)
    data_manager = DataManager(file_backend)
    microscopy_collection = data_manager.load(input_file)
    return microscopy_collection


def connected_components(image, neighbors=8, background=0):
    """Return a segmented image."""
    connected_components, n_cc = skimage.measure.label(image,
                                                       neighbors=8,
                                                       background=background,
                                                       return_num=True)

    # Hack to work arounds skimage.measure.label behaviour pre version 0.12.
    # Pre version 0.12 the background in skimage was labeled -1 and the first component was labelled with 0.
    # The jicbioimage.core.image.SegmentedImage assumes that the background is labelled 0.
    if np.min(connected_components) == -1:
        connected_components[np.where(connected_components == 0)] = np.max(connected_components) +1
        connected_components[np.where(connected_components == -1)] = 0

    return connected_components.view(SegmentedImage)


@transformation
@dtype_contract(input_dtype=bool, output_dtype=bool)
def remove_large_objects(image, max_size):
    """Remove objects larger than max_size.

    This function removes more than the large object identified.
    It takes the convex hull of the large object and then performs
    30 rounds of dilation.
    """
    segmented_image = connected_components(image)
    ignored = np.zeros(image.shape, dtype=np.uint8)
    for i in segmented_image.identifiers:
        region = segmented_image.region_by_identifier(i)
        if region.area > max_size:
            to_remove = region
            to_remove = region.convex_hull
            to_remove = to_remove.dilate(30)
            segmented_image[to_remove.index_arrays] = 0
            ignored[to_remove.index_arrays] = 1
    
    logger.info("Number of pixels        : {}".format(segmented_image.size))
    logger.info("Number of ignored pixels: {}".format(np.sum(ignored)))
    scipy.misc.imsave(os.path.join(AutoName.directory, "ignored.png"), normalise(ignored))
    return segmented_image.astype(bool)

def count_spots(image):
    """Return the number of spots identified."""
    segmented_image = connected_components(image)
    logger.info("Number of spots         : {}".format(segmented_image.number_of_segments))
    return segmented_image.number_of_segments

def write_csv(image, max_intensity, fname):
    """Write out a csv file with information about each spot."""
    segmented_image = connected_components(image)
    spot_properties = skimage.measure.regionprops(segmented_image, max_intensity)
    header = [
        "id",
        "centroid_row",
        "centroid_col",
        "area",
        "sum_intensity",
        "max_intensity",
        "mean_intensity",
        "major_axis_length",
        "minor_axis_length",
    ]
    row = "{id:d},{centroid_row:.0f},{centroid_col:.0f},{area:.0f},{sum_intensity},{max_intensity},{mean_intensity},{major_axis_length:.2f},{minor_axis_length:.2f}\n"
    with open(fname, "w") as fh:
        fh.write("{}\n".format(",".join(header)))
        for i, p in enumerate(spot_properties):

            # Make sure that we are picking out the correct region from the
            # segmented image.
            assert segmented_image.region_by_identifier(i+1).area == p.area
            assert np.max(max_intensity[np.where(segmented_image.region_by_identifier(i+1))]) == p.max_intensity

            sum_intensity = np.sum(max_intensity[np.where(segmented_image.region_by_identifier(i+1))])
            data = dict(
                id=i,
                centroid_row=round(p.centroid[0], 0),
                centroid_col=round(p.centroid[1], 0),
                area=p.area,
                sum_intensity=sum_intensity,
                max_intensity=p.max_intensity,
                mean_intensity=p.mean_intensity,
                major_axis_length=p.major_axis_length,
                minor_axis_length=p.minor_axis_length,
            )
            fh.write(row.format(**data))
    
    
def create_annotated_image(image, max_intensity):
    """Write an annotated image to disk."""
    segmented_image = connected_components(image)
    gray_intensity = normalise(max_intensity) * 255
    rgb_intensity = np.dstack([gray_intensity, gray_intensity, gray_intensity])
    annotated = Image.from_array(rgb_intensity)
    for i in segmented_image.identifiers:
        border = segmented_image.region_by_identifier(i).dilate(1).border
        annotated[border.index_arrays] = pretty_color(i)
    with open(os.path.join(AutoName.directory, "annotated.png"), "wb") as fh:
        fh.write(annotated.png())


def find_plasmodesmata(zstack, max_size, min_size):
    """Return segmented image.

    :param zstack: numpy.ndarray
    :param max_size: maximum size allowed
                     for a region to be classified as a plasmodesmata
    :param min_size: minimum size allowed
                     for a region to be classified as a plasmodesmata
    :returns: :class:`jicbioimage.core.image.SegmentedImage`
    """
    max_intensity = max_intensity_projection(zstack)

    im = threshold_otsu(max_intensity)
    im = remove_large_objects(im, max_size=max_size)
    im = remove_small_objects(im, min_size=min_size)

    num_spots = count_spots(im)
    write_csv(im, max_intensity, os.path.join(AutoName.directory, "output.csv"))
    create_annotated_image(im, max_intensity)

    return connected_components(im)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("input_file", help="path to raw microscopy data")
    parser.add_argument("series", type=int,
        help="zero based index of microscopy image series to analyse")
    parser.add_argument("output_dir", help="output directory")
    parser.add_argument("-l", "--max_size",
        default=100, type=int, help="maximum number of pixels (default=100)")
    parser.add_argument("-s", "--min_size",
        default=2, type=int, help="minimum number of pixels (default=2)")
    args = parser.parse_args()

    if not os.path.isdir(args.output_dir):
        os.mkdir(args.output_dir)
    if not os.path.isfile(args.input_file):
        parser.error("No such microscopy file: {}".format(args.input_file))

    AutoName.directory = args.output_dir

    # Create file handle logger.
    fh = logging.FileHandler(os.path.join(AutoName.directory, "log"), mode="w")
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    logger.info("Script version          : {}".format(__version__))

    microscopy_collection = get_microscopy_collection(args.input_file)
    zstack = microscopy_collection.zstack_array(s=args.series)
    find_plasmodesmata(zstack, args.max_size, args.min_size)

if __name__ == "__main__":
    main()
