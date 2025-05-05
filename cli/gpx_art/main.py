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
@click.option("--color", default="#000000", help="Line color in hex format or named color")
@click.option(
    "--thickness",
    type=click.Choice(["thin", "medium", "thick"]),
    default="medium",
    help="Line thickness"
)
@click.option(
    "--style",
    type=click.Choice(["solid", "dashed"]),
    default="solid",
    help="Line style"
)
@click.option(
    "--dpi",
    type=int,
    default=300,
    help="Output resolution in dots per inch (PNG only)"
)
@click.option(
    "--format",
    "formats",
    help="Output formats (comma-separated: png,svg,pdf). Defaults to file extension."
)
@click.option(
    "--page-size",
    type=click.Choice([
        "letter", "a4", 
        "square-small", "square-medium", "square-large",
        "landscape-small", "landscape-medium", "landscape-large"
    ]),
    default="letter",
    help="Page size for PDF output"
)
@click.option(
    "--markers/--no-markers",
    default=False,
    help="Add distance markers along the route"
)
@click.option(
    "--markers-unit",
    type=click.Choice(["miles", "km"]),
    default="miles",
    help="Unit for distance markers"
)
@click.option(
    "--marker-interval",
    type=float,
    help="Distance between markers in the specified unit (defaults to 1.0)"
)
@click.option(
    "--marker-size",
    type=float,
    default=6.0,
    help="Size of the marker points"
)
@click.option(
    "--marker-color",
    help="Color of markers (defaults to route color)"
)
@click.option(
    "--label-font-size",
    type=int,
    default=8,
    help="Font size for distance labels"
)
@click.option(
    "--overlay",
    help="Information to overlay (comma-separated: distance,duration,elevation,name,date)"
)
@click.option(
    "--overlay-position",
    type=click.Choice(["top-left", "top-right", "bottom-left", "bottom-right"]),
    default="top-left",
    help="Position of the information overlay"
)
@click.option(
    "--font-size",
    type=int,
    default=10,
    help="Font size for overlay text"
)
@click.option(
    "--font-color",
    default="black",
    help="Color for overlay text"
)
@click.option(
    "--background/--no-background",
    default=True,
    help="Add background box to overlay"
)
@click.option(
    "--bg-color",
    default="white",
    help="Color for overlay background"
)
@click.option(
    "--bg-alpha",
    type=float,
    default=0.7,
    help="Transparency of overlay background (0-1)"
)
def convert(
    input_file, output_file, color, thickness, style, dpi, formats, page_size,
    markers, markers_unit, marker_interval, marker_size, marker_color, label_font_size,
    overlay, overlay_position, font_size, font_color, background, bg_color, bg_alpha
):
    """Convert GPX file to artwork in PNG, SVG, or PDF format."""
    
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
    
    try:
        # Render the route
        visualizer.render_route(
            color=color,
            thickness=thickness,
            line_style=style
        )
        
        # Add distance markers if requested
        if markers:
            try:
                visualizer.add_distance_markers(
                    unit=markers_unit,
                    interval=marker_interval,
                    marker_size=marker_size,
                    marker_color=marker_color,
                    show_labels=True,
                    label_font_size=label_font_size
                )
            except ValueError as e:
                click.secho(f"Error adding markers: {str(e)}", fg="red")
                click.echo("Continuing without markers...")
                
        # Add information overlay if requested
        if overlay:
            try:
                # Parse overlay fields
                overlay_fields = [field.strip() for field in overlay.split(',')]
                
                visualizer.add_overlay(
                    fields=overlay_fields,
                    position=overlay_position,
                    font_size=font_size,
                    font_color=font_color,
                    background=background,
                    bg_color=bg_color,
                    bg_alpha=bg_alpha
                )
            except ValueError as e:
                click.secho(f"Error adding overlay: {str(e)}", fg="red")
                click.echo("Continuing without overlay...")
    except ValueError as e:
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)
    
    # Determine export formats
    exporter = Exporter()
    output_path = Path(output_file)
    
    # If formats are explicitly provided, use those
    if formats:
        format_list = [f.strip() for f in formats.split(',')]
        try:
            click.echo(f"Exporting to {', '.join(format_list)} formats...")
            exported_files = exporter.export_multiple(
                figure=visualizer.get_figure(),
                base_path=output_path.with_suffix(''),  # Remove extension for base path
                formats=format_list,
                dpi=dpi,
                page_size=page_size
            )
        except ExportError as e:
            click.secho(f"Error: {str(e)}", fg="red")
            sys.exit(1)
    else:
        # Otherwise, determine format from file extension
        try:
            export_format = exporter.get_format(output_path)
            format_name = export_format.name.lower()
            click.echo(f"Exporting {format_name.upper()}...")
            
            # Export based on detected format
            if export_format == ExportFormat.PNG:
                exporter.export_png(
                    figure=visualizer.get_figure(),
                    output_path=output_path,
                    dpi=dpi
                )
            elif export_format == ExportFormat.SVG:
                exporter.export_svg(
                    figure=visualizer.get_figure(),
                    output_path=output_path
                )
            elif export_format == ExportFormat.PDF:
                exporter.export_pdf(
                    figure=visualizer.get_figure(),
                    output_path=output_path,
                    page_size=page_size
                )
            
            exported_files = [output_path]
            
        except ExportError as e:
            click.secho(f"Error: {str(e)}", fg="red")
            sys.exit(1)
    
    
    # Show style information
    style_info = []
    if color.startswith('#'):
        style_info.append(f"Color: {color}")
    else:
        style_info.append(f"Color: {color}")
    style_info.append(f"Thickness: {thickness}")
    style_info.append(f"Style: {style}")
    
    click.echo(f"Style: {', '.join(style_info)}")
    
    # Show marker information if enabled
    if markers:
        marker_info = []
        marker_info.append(f"Unit: {markers_unit}")
        if marker_interval:
            marker_info.append(f"Interval: {marker_interval} {markers_unit}")
        else:
            marker_info.append(f"Interval: 1.0 {markers_unit}")  # Default
        if marker_color:
            marker_info.append(f"Color: {marker_color}")
        marker_info.append(f"Size: {marker_size}")
        marker_info.append(f"Label size: {label_font_size}")
        
        click.echo(f"Markers: {', '.join(marker_info)}")
        
    # Show overlay information if enabled
    if overlay:
        overlay_info = []
        overlay_info.append(f"Fields: {overlay}")
        overlay_info.append(f"Position: {overlay_position}")
        overlay_info.append(f"Font size: {font_size}")
        overlay_info.append(f"Font color: {font_color}")
        overlay_info.append(f"Background: {'On' if background else 'Off'}")
        if background:
            overlay_info.append(f"BG color: {bg_color}")
            overlay_info.append(f"BG alpha: {bg_alpha}")
        
        click.echo(f"Overlay: {', '.join(overlay_info)}")


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

