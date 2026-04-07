from osgeo import ogr
from osmium import SimpleWriter
from osmium.osm.mutable import Node
import pandas
from pprint import pp
from pyproj import Transformer
import shapefile
import typer
from pathlib import Path
from typing_extensions import Annotated

def prepare_middlebury_tree_import(
    trees: Annotated[Path, typer.Option(exists=True, readable=True, dir_okay=False, file_okay=True, help="Path to the input shapefile. Example: campus-trees.shp")],
    names: Annotated[Path, typer.Option(exists=True, readable=True, dir_okay=False, file_okay=True, help="Path to the plant names shapefile. Example: PlantNames.dbf")],
    visits: Annotated[Path, typer.Option(exists=True, readable=True, dir_okay=False, file_okay=True, help="Path to the visits shapefile. Example: TreeVisits.dbf")],
    output: Annotated[Path, typer.Option(writable=True, dir_okay=False, file_okay=True, help="Path of the output .osm file. Example: campus-trees.osm")]
):
    writer = SimpleWriter(output, overwrite=True)

    # Load all Plant Names for easier lookup.
    namesDict = {record['PlantPlant']: record.as_dict() for record in shapefile.Reader(names).iterRecords() }
    commonNamesDict = {record['PlantsComm']: record.as_dict() for record in shapefile.Reader(names).iterRecords() }

    # Load visits
    ogr.UseExceptions()
    ds = ogr.Open(visits)
    visitsLayer = ds.GetLayer()

    # Load tree details from the OSM wiki.
    wikiSpecies = pandas.read_html('https://wiki.openstreetmap.org/wiki/Tag:natural%3Dtree/List_of_Species')[0]

    # Initialize the transformer
    # EPSG:32145 = NAD83 / Vermont
    # EPSG:4326 = WGS84
    transformer = Transformer.from_crs("EPSG:32145", "EPSG:4326", always_xy=True)

    sf = shapefile.Reader(trees)
    i=0
    missingWikidata = {}
    for shapeRecord in sf.shapeRecords():
        i=i-1
        treeRec = shapeRecord.record
        treeFields = treeRec.as_dict()
        # print ("\n")
        # pp(treeFields)
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
            # pp(nameFields)
            tags['species'] = f"{nameFields['GenusLatin']} {nameFields['PlantsSpec']}"
            tags['species:en'] = nameFields['PlantsComm']
            tags['genus'] = nameFields['GenusLatin']
            tags['taxon'] = nameFields['LatinName']
            tags['taxon:en'] = nameFields['PlantsComm']
            tags['taxon:genus'] = nameFields['GenusLatin']
            if nameFields['PlantsCult']:
                tags['taxon:cultivar'] = nameFields['PlantsCult']

        # Add additional data from the
        if 'species' in tags:
            wikiDetails = wikiSpecies[wikiSpecies["species"] == tags['species']]
            # If we can find details of the species, use those.
            if wikiDetails.size > 0:
                wikidata = wikiDetails['species:wikidata'].item()
                if wikidata and isinstance(wikidata, str):
                    tags['species:wikidata'] = wikidata
                leaf_cycle = wikiDetails['leaf_cycle=*'].item()
                if leaf_cycle and isinstance(leaf_cycle, str):
                    tags['leaf_cycle'] = leaf_cycle
                leaf_type = wikiDetails['leaf_type=*'].item()
                if leaf_type and isinstance(leaf_type, str):
                    tags['leaf_type'] = leaf_type
            # Otherwise, try to get at least the leaf_type & leaf_cycle from the genus.
            else:
                wikiDetails = wikiSpecies[wikiSpecies["genus"] == tags['genus']]
                if wikiDetails.size > 0:
                    leaf_cycle = wikiDetails.iloc[:1]['leaf_cycle=*'].item()
                    if leaf_cycle and isinstance(leaf_cycle, str):
                        tags['leaf_cycle'] = leaf_cycle
                    leaf_type = wikiDetails.iloc[:1]['leaf_type=*'].item()
                    if leaf_type and isinstance(leaf_type, str):
                        tags['leaf_type'] = leaf_type
                    missingWikidata[tags['species']] = f"Only genus matched for {tags['species']} ({tags['species:en']})"
                else:
                    missingWikidata[tags['species']] = f"No species or genus matches for {tags['species']} ({tags['species:en']})"

        # Find the latest visit.
        visitsLayer.SetAttributeFilter(f"FK_GUID = '{treeFields['GlobalID']}'")
        latestVisit = None
        for visit in visitsLayer:
            if latestVisit is None or visit['Last_Inspe'] > latestVisit['Last_Inspe']:
                latestVisit = visit

        if latestVisit:
            diameter = latestVisit.GetField('DBH')
            if diameter and diameter > 0:
                tags['diameter'] = f"{diameter}\""
            height = latestVisit.GetField('Height')
            if height and height > 0:
                tags['height'] = f"{height}\'"
            diameter_crown = latestVisit.GetField('Spread')
            if diameter_crown and diameter_crown > 0:
                tags['diameter_crown'] = f"{diameter_crown}\'"
            tags['check_date'] = latestVisit.GetField('Last_Inspe')

        # pp(tags)

        xNAD, yNAD = shapeRecord.shape.points[0]
        lon, lat = transformer.transform(xNAD, yNAD)
        writer.add_node(Node(
            id = i,
            location = (lon, lat),
            tags = tags,
        ))
        # if i > 5:
        #     exit()

    pp(sorted(missingWikidata.items()))
