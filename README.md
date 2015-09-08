# README

Clone the project from githq and go into it.

```
git clone git@githq.nbi.ac.uk:rg-matthew-hartley/find-plasmodesmata.git
cd find-plasmodesmata
```

Create a ``data/raw`` directory and place the microscopy file of interest
there.

```
mkdir -p data/raw
cp /path/to/file/of/interest.lif data/raw/
```

Install the dependencies.

```
pip install numpy
pip install scipy
pip install scikit-image
pip install jicbioimage.transform
```

See also the
[jicbioimage installation notes](http://jicbioimage.readthedocs.org/en/latest/installation_notes.html)
for further dependencies.

Run the analysis.

```
python scripts/find_plasmodesmata.py data/raw/interest.lif --series=0
```
