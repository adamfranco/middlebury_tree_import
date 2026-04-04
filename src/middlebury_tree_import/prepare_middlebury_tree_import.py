from osmium import SimpleWriter
from osmium.osm.mutable import Node
from pyproj import Transformer
import shapefile
import typer
from pathlib import Path
from typing_extensions import Annotated

def prepare_middlebury_tree_import(
    trees: Annotated[Path, typer.Option(exists=True, readable=True, dir_okay=False, file_okay=True, help="Path to the input shapefile. Example: campus-trees.zip OR campus-trees.shp")],
    names: Annotated[Path, typer.Option(exists=True, readable=True, dir_okay=False, file_okay=True, help="Path to the input shapefile. Example: campus-trees.zip OR campus-trees.shp")],
    output: Annotated[Path, typer.Option(writable=True, dir_okay=False, file_okay=True, help="Path of the output .osm file. Example: campus-trees.osm")]
):
    writer = SimpleWriter(output, overwrite=True)

    # Load all Plant Names for easier lookup.
    namesDict = {record['PlantPlant']: record.as_dict() for record in shapefile.Reader(names).iterRecords() }

    # Initialize the transformer
    # EPSG:32145 = NAD83 / Vermont
    # EPSG:4326 = WGS84
    transformer = Transformer.from_crs("EPSG:32145", "EPSG:4326", always_xy=True)

    sf = shapefile.Reader(trees)
    i=0
    for shapeRecord in sf.shapeRecords():
        i=i-1
        treeRec = shapeRecord.record
        treeFields = treeRec.as_dict()
        print(treeFields)
        nameFields = namesDict[treeFields['PlantName']]
        print(nameFields)
        tags = {
            'species:en': nameFields['PlantsComm']
        }
        xNAD, yNAD = shapeRecord.shape.points[0]
        lon, lat = transformer.transform(xNAD, yNAD)
        writer.add_node(Node(
            id = i,
            location = (lon, lat),
            tags = tags
        ))
        exit()
