import typer
from pathlib import Path
from typing_extensions import Annotated

def prepare_middlebury_tree_import(
    input: Annotated[Path, typer.Option(exists=True, readable=True, dir_okay=False, file_okay=True, help="Path to the input .geojson file. Example: campus-trees.geojson")],
    output: Annotated[Path, typer.Option(writable=True, dir_okay=False, file_okay=True, help="Path of the output .osm file. Example: campus-trees.osm")]
):
    print("To do")
