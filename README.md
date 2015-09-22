# README

## Installation notes

## Dependencies

- [OpenMicroscopy bftools](http://www.openmicroscopy.org/site/support/bio-formats5.1/users/comlinetools/)
- [FreeImage](http://freeimage.sourceforge.net/download.html)

Notes on how to install ``bftools`` and ``FreeImage`` can be found in the
[jicbioimage installation notes](http://jicbioimage.readthedocs.org/en/latest/installation_notes.html)

## Windows

Install the [Anaconda Python distribution](http://continuum.io/downloads).

Setup a virtual environment named ``find_plasmodesmata_env`` and install the
scientific Python package dependencies.

```
conda create –n find_plasmodesmata_env python=2.7 numpy scipy scikit-image
```

Activate the virtual environment.

```
activate find_plasmodesmata_env
```

Install the ``jicbioimage`` dependencies.

```
pip install jicbioimage.transform
```

Download the
[find_plasmodesmata](https://githq.nbi.ac.uk/rg-matthew-hartley/find-plasmodesmata)
project from githq and go into it.


## Linux

Clone the project from githq and go into it.

```
git clone git@githq.nbi.ac.uk:rg-matthew-hartley/find-plasmodesmata.git
cd find-plasmodesmata
```

Install the dependencies.

```
pip install numpy
pip install scipy
pip install scikit-image
pip install jicbioimage.transform
```

## Data analysis

On Windows remember to activate the virtual environment when you open a new
command prompt.

```
activate find_plasmodesmata_env
```

Run the analysis.

```
python scripts/find_plasmodesmata.py /path/to/raw/file/of/interest.lif --series=0 output_directory
```
