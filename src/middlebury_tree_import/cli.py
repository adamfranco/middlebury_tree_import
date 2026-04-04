import typer

from .prepare_middlebury_tree_import import prepare_middlebury_tree_import

app = typer.Typer()
app.command(help="Prepare an OSM import file from a GEOJSON export of the Middlebury College Tree database.")(prepare_middlebury_tree_import)

if __name__ == "__main__":
    app()
