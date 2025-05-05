import click
import sys
from importlib.metadata import version

# Define the package version - will be used in the CLI's version option
try:
    __version__ = version("gpx-art")
except Exception:
    __version__ = "0.1.0"  # Default fallback version


@click.group()
@click.version_option(version=__version__)
def cli():
    """GPX Art Generator - Transform GPS routes into artwork."""
    pass


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def convert(input_file, output):
    """Convert GPX file to artwork."""
    click.echo("Convert command not implemented")


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
def validate(input_file):
    """Validate GPX file."""
    click.echo("Validate command not implemented")


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
def info(input_file):
    """Display GPX file information."""
    click.echo("Info command not implemented")


if __name__ == "__main__":
    cli()

