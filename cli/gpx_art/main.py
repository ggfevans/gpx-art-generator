import click
import os
import sys
from datetime import timedelta
from importlib.metadata import version
from pathlib import Path
from typing import List

from gpx_art.exporters import Exporter, ExportError
from gpx_art.models import Route
from gpx_art.parsers import GPXParser
from gpx_art.visualizer import RouteVisualizer

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
@click.argument("output_file", type=click.Path())
@click.option("--color", default="#000000", help="Line color in hex format")
@click.option(
    "--thickness",
    type=click.Choice(["thin", "medium", "thick"]),
    default="medium",
    help="Line thickness"
)
@click.option(
    "--dpi",
    type=int,
    default=300,
    help="Output resolution in dots per inch"
)
def convert(input_file, output_file, color, thickness, dpi):
    """Convert GPX file to artwork."""
    # Validate output file extension
    if not output_file.lower().endswith('.png'):
        click.secho("Error: Output file must have .png extension", fg="red")
        sys.exit(1)
    
    # Parse GPX file
    click.echo("Parsing GPX file...")
    parser = GPXParser(input_file)
    gpx = parser.parse()
    
    if not gpx:
        click.secho(f"Error: {parser.get_error()}", fg="red")
        sys.exit(1)
    
    # Convert to internal model
    route = parser.to_route(gpx)
    
    # Create visualizer
    click.echo("Rendering route...")
    visualizer = RouteVisualizer(route)
    visualizer.create_figure()
    visualizer.render_route(color=color, thickness=thickness)
    
    # Export to PNG
    click.echo("Exporting PNG...")
    exporter = Exporter()
    
    try:
        exporter.export_png(
            figure=visualizer.get_figure(),
            output_path=output_file,
            dpi=dpi
        )
    except ExportError as e:
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)
    
    # Show success message
    click.secho(
        f"\n✓ Conversion complete! Output saved to:",
        fg="green", bold=True
    )
    click.echo(f"{click.format_filename(os.path.abspath(output_file))}")
    
    # Show file information
    size_bytes = os.path.getsize(output_file)
    size_kb = size_bytes / 1024
    size_mb = size_kb / 1024
    
    if size_mb >= 1:
        size_str = f"{size_mb:.2f} MB"
    else:
        size_str = f"{size_kb:.2f} KB"
    
    click.echo(f"Size: {size_str} ({size_bytes:,} bytes)")
    click.echo(f"Resolution: {dpi} DPI")


def validate_coordinates(route: Route) -> List[str]:
    """
    Validate that all coordinates in the route are within valid ranges.
    
    Args:
        route: The Route object to validate
        
    Returns:
        List of error messages, empty if no issues found
    """
    issues = []
    
    for i, segment in enumerate(route.segments):
        for j, point in enumerate(segment.points):
            # Latitude and longitude should already be validated on point creation,
            # but we can do additional checks here if needed
            if abs(point.latitude) > 85.0:
                issues.append(
                    f"Point {j+1} in segment {i+1} has extreme latitude ({point.latitude})"
                    " which may cause issues with map projections"
                )
    
    return issues


def validate_segments(route: Route) -> List[str]:
    """
    Validate segment integrity.
    
    Args:
        route: The Route object to validate
        
    Returns:
        List of error messages, empty if no issues found
    """
    issues = []
    
    # Check if there are any segments at all
    if not route.segments:
        issues.append("Route has no segments")
        return issues
    
    for i, segment in enumerate(route.segments):
        # Check if segment has points
        if not segment.points:
            issues.append(f"Segment {i+1} has no points")
            continue
        
        # Check if segment has enough points for meaningful data
        if len(segment.points) < 2:
            issues.append(f"Segment {i+1} has only one point - no route data")
            
        # Check for excessive points (warning, not error)
        if len(segment.points) > 10000:
            issues.append(f"Segment {i+1} has {len(segment.points)} points, "
                         "which may cause performance issues")
    
    return issues


def validate_timestamps(route: Route) -> List[str]:
    """
    Validate timestamp consistency.
    
    Args:
        route: The Route object to validate
        
    Returns:
        List of error messages, empty if no issues found
    """
    issues = []
    
    for i, segment in enumerate(route.segments):
        # Check if timestamps exist
        has_timestamps = any(p.timestamp for p in segment.points)
        if not has_timestamps:
            continue  # Skip further timestamp checks if no timestamps
            
        # Check if all points have timestamps
        missing_timestamps = any(p.timestamp is None for p in segment.points)
        if missing_timestamps:
            issues.append(f"Segment {i+1} has inconsistent timestamps "
                         "(some points missing timestamp data)")
            
        # Check for timestamp order
        timestamp_issues = False
        for j in range(1, len(segment.points)):
            curr = segment.points[j].timestamp
            prev = segment.points[j-1].timestamp
            if curr and prev and curr < prev:
                timestamp_issues = True
                break
                
        if timestamp_issues:
            issues.append(f"Segment {i+1} has out-of-order timestamps")
            
        # Check for duplicate timestamps
        timestamps = [p.timestamp for p in segment.points if p.timestamp]
        unique_timestamps = set(timestamps)
        if len(unique_timestamps) < len(timestamps):
            issues.append(f"Segment {i+1} has duplicate timestamps")
    
    return issues


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
def validate(input_file):
    """Validate GPX file."""
    # Parse the GPX file
    parser = GPXParser(input_file)
    gpx = parser.parse()
    
    if not gpx:
        click.secho(f"Error: {parser.get_error()}", fg="red")
        sys.exit(1)
    
    # Convert to our model
    route = parser.to_route(gpx)
    
    # Run validation checks
    click.secho("\n=== GPX Validation Results ===", fg="blue", bold=True)
    click.echo(f"File: {click.format_filename(os.path.abspath(input_file))}")
    
    # Run all validations
    segment_issues = validate_segments(route)
    coordinate_issues = validate_coordinates(route)
    timestamp_issues = validate_timestamps(route)
    
    # Combine all issues
    all_issues = segment_issues + coordinate_issues + timestamp_issues
    
    # Display validation status
    if not all_issues:
        click.secho("\n✓ GPX file is valid", fg="green", bold=True)
        click.echo("No issues found")
        sys.exit(0)
    else:
        click.secho(f"\n✗ Found {len(all_issues)} issues:", fg="red", bold=True)
        
        # Display issues by category
        if segment_issues:
            click.secho("\nSegment Issues:", fg="yellow")
            for issue in segment_issues:
                click.echo(f"- {issue}")
                
        if coordinate_issues:
            click.secho("\nCoordinate Issues:", fg="yellow")
            for issue in coordinate_issues:
                click.echo(f"- {issue}")
                
        if timestamp_issues:
            click.secho("\nTimestamp Issues:", fg="yellow")
            for issue in timestamp_issues:
                click.echo(f"- {issue}")
        
        click.echo("\nFix these issues to ensure proper processing of the GPX file.")
        sys.exit(1)


def format_distance(meters):
    """Format distance in both kilometers and miles."""
    km = meters / 1000
    miles = meters / 1609.34
    return f"{km:.2f} km ({miles:.2f} miles)"


def format_duration(duration):
    """Format timedelta for display."""
    if not duration:
        return "Unknown"
    
    days = duration.days
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds and not (days or hours):
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
    
    return ", ".join(parts)


def format_elevation(stats):
    """Format elevation statistics for display."""
    if not stats:
        return "No elevation data available"
    
    return (
        f"Min: {stats['min']:.1f}m, Max: {stats['max']:.1f}m, "
        f"Gain: {stats['gain']:.1f}m, Loss: {stats['loss']:.1f}m"
    )


def format_bounds(bounds):
    """Format geographic bounds for display."""
    min_lat, max_lat, min_lon, max_lon = bounds
    lat_range = f"{min_lat:.6f}° to {max_lat:.6f}°"
    lon_range = f"{min_lon:.6f}° to {max_lon:.6f}°"
    return f"Latitude: {lat_range}, Longitude: {lon_range}"


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
def info(input_file):
    """Display GPX file information."""
    # Parse the GPX file
    parser = GPXParser(input_file)
    gpx = parser.parse()
    
    if not gpx:
        click.secho(f"Error: {parser.get_error()}", fg="red")
        sys.exit(1)
    
    # Convert to our model
    route = parser.to_route(gpx)
    
    # Display file information
    click.secho("\n=== GPX File Information ===", fg="green", bold=True)
    click.echo(f"File: {click.format_filename(os.path.abspath(input_file))}")
    click.echo(f"Name: {route.name or 'Unnamed route'}")
    
    # Display basic stats
    click.secho("\n=== Route Statistics ===", fg="green", bold=True)
    click.echo(f"Distance: {format_distance(route.get_total_distance())}")
    
    duration = route.get_total_duration()
    click.echo(f"Duration: {format_duration(duration)}")
    
    # Display structure information
    click.secho("\n=== Route Structure ===", fg="green", bold=True)
    click.echo(f"Segments: {len(route.segments)}")
    click.echo(f"Points: {route.get_total_points()}")
    
    # Display elevation information if available
    click.secho("\n=== Elevation Profile ===", fg="green", bold=True)
    elevation_stats = route.get_elevation_stats()
    click.echo(format_elevation(elevation_stats))
    
    # Display geographic bounds
    click.secho("\n=== Geographic Bounds ===", fg="green", bold=True)
    click.echo(format_bounds(route.get_bounds()))
    
    click.echo("")  # Add a newline at the end


if __name__ == "__main__":
    cli()

