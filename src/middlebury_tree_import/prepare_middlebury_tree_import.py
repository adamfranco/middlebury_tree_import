from osmium import SimpleWriter
from osmium.osm.mutable import Node
from pprint import pp
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
    commonNamesDict = {record['PlantsComm']: record.as_dict() for record in shapefile.Reader(names).iterRecords() }

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
        print ("\n")
        pp(treeFields)
        tags = {
            'natural': 'tree',
            'species:en': treeFields['COMMON_NAM'],
        }
        nameFields = None
        # look up by Id
        if 'PlantName' in treeFields and treeFields['PlantName'] in namesDict:
            nameFields = namesDict[treeFields['PlantName']]
        # Look up by common name if the ids are off.
        elif 'COMMON_NAM' in treeFields and treeFields['COMMON_NAM'] in commonNamesDict:
            nameFields = commonNamesDict[treeFields['COMMON_NAM']]

        if nameFields:
            pp(nameFields)
            tags['species'] = f"{nameFields['GenusLatin']} {nameFields['PlantsSpec']}"
            tags['species:en'] = nameFields['PlantsComm']
            tags['genus'] = nameFields['GenusLatin']
            tags['taxon'] = nameFields['LatinName']
            tags['taxon:en'] = nameFields['PlantsComm']
            tags['taxon:genus'] = nameFields['GenusLatin']
            tags['taxon:cultivar'] = nameFields['PlantsCult']
        if 'DBH' in treeFields:
            tags['diameter'] = f"{treeFields['DBH']}\""
        if 'DBH' in treeFields:
            tags['diameter'] = f"{treeFields['DBH']}\""

        pp(tags)

        xNAD, yNAD = shapeRecord.shape.points[0]
        lon, lat = transformer.transform(xNAD, yNAD)
        writer.add_node(Node(
            id = i,
            location = (lon, lat),
            tags = tags,
        ))
        # if i > 5:
        #     exit()
