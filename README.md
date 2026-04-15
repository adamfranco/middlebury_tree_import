# Middlebury Tree Import
Scripts to import trees from Middlebury College's tree database into OpenStreetMap (OSM).

In support of the [Middlebury College Tree Import](https://wiki.openstreetmap.org/wiki/Middlebury_College_tree_import)
project.

# Installation

## Prerequisites
* Python 3.14 or later
* Install [GDAL](https://gdal.org/en/stable/) on your system.
   * OS X - MacPorts: `sudo port install gdal`
   * OS X - Homebrew: `sudo brew install gdal`

## Normal installation
This program can be installed for normal usage with pip and pipx:

```
pip install pipx
pipx install --python python3.14 git+https://github.com/adamfranco/middlebury-tree-import.git
```

The you can run the program with:
```
prepare_middlebury_tree_import --help
```

## Development Installation

This program can be installed for normal usage with pip and pipx:

```
pip install pipx
git clone git@github.com:adamfranco/middlebury-tree-import.git
cd middlebury-tree-import
pipx install --editable --python python3.14 .
```

The you can run the program with:
```
prepare_middlebury_tree_import --help
```

# Usage

1. Download a GEOJSON version of the Middlebury College Tree database
[from ArcGIS](https://middlebury.maps.arcgis.com/home/item.html?id=8549539c40834bb8a08326c7a87b1696).

2. Unzip the Shapefile package

3. Prepare the OSM file:
   ```
   prepare_middlebury_tree_import \
    --trees campus_trees/campus_trees.shp \
    --names campus_trees/PlantNames.dbf \
    --visits campus_trees/TreeVisits.dbf \
    --memorial campus_trees/MemorialTrees.dbf \
    --output campus_trees.osm
   ```
