# Methodology

## Image analysis

The image analysis protocol segmented the confocal images into
three-dimensional objects. Unusually small and large objects were then filtered
out. A comma separated file reporting various descriptors of the objects was
then produced. Three annotated images were also created illustrating the final
selection of plasmodesmata, the small objects that had been filtered out and
the large objects that had been filtered out.

The three-dimensional segmentation was carried out using an absolute threshold
(default 15000). The resulting binary image was then segmented into connected
components.

The post segmentation filtering was based on the number of voxels in each
connected component. The small filter removed objects with less than two voxels
and the large filter removed objects with more than 50 pixels. The small filter
removed noise and the large filter tended to remove noise from callose
accumulated in stomata.

The comma separated file contained one line per object (plasmodesmata). The
columns in the CSV file were: a unique identifier ("id"), the red-green-blue
triplet used to represent the object in the annotated image ("rgb"), the number
of voxels in object ("voxels"), the sum of the intensity values in the object
("sum"), the minimum intensity value in the object ("min"), the maximum
intensity value in the object ("max"), the mean intensity of the object
("mean").

Annotated images were written out as series of PNG files, one file for each
z-slice. Each annotated image contained the intensity of the z-slice in gray
scale. On top of the intensity the outline of each object in the z-slice was
annotated using a pretty colour (also recorded in the comma separated file).

As a sanity check of the image analysis pipeline all annotated images were
inspected prior to inclusion of any data in the statistical analysis.

The image analysis pipeline was written in Python and made use of the [JIC
BioImage framework](https://github.com/JIC-CSB/jicbioimage). The conversion of
the Leica files made use of BioFormat's bfconvert tool [ref1]. The image
anslysis made use of several scientific Python packages including numpy [ref2],
scipy [ref3], and scikit-image [ref4].  The image analysis scripts are
available under the open source MIT licence on GitHub [make available and
include ref].

[ref1] http://www.ncbi.nlm.nih.gov/pubmed/20513764
[ref2] http://ieeexplore.ieee.org/xpl/articleDetails.jsp?arnumber=5725236
[ref3] Jones E, Oliphant E, Peterson P, et al. SciPy: Open Source Scientific Tools for Python, 2001-, http://www.scipy.org/ [Online; accessed 2016-04-11].
[ref4] https://peerj.com/articles/453/
