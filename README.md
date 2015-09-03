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

Run the analysis.

```
python scripts/find_plasmoesmata.py data/raw/interest.lif --series=0
```
