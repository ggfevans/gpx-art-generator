# GPX Art Generator - Usage Examples

This document provides practical examples of using the GPX Art Generator in various scenarios.

## Table of Contents

- [Common Use Cases](#common-use-cases)
  - [Running Route Visualization](#running-route-visualization)
  - [Cycling Activity Artwork](#cycling-activity-artwork)
  - [Hiking Trail Maps](#hiking-trail-maps)
  - [Multi-Activity Visualizations](#multi-activity-visualizations)
- [Advanced Examples](#advanced-examples)
  - [Custom Styling Combinations](#custom-styling-combinations)
  - [Multi-Format Exports](#multi-format-exports)
  - [Batch Processing](#batch-processing)
- [Configuration Examples](#configuration-examples)
  - [Activity-Specific Configs](#activity-specific-configs)
  - [Style Presets](#style-presets)
  - [Advanced Customization](#advanced-customization)
- [Integration Examples](#integration-examples)
  - [Script Integration](#script-integration)
  - [Automation Examples](#automation-examples)
  - [Error Handling Patterns](#error-handling-patterns)

## Common Use Cases

### Running Route Visualization

Create a simple visualization of your running route with distance markers and basic information.

```bash
gpx-art convert morning-run.gpx run-visualization \
  --color "#FF5500" \
  --thickness medium \
  --style solid \
  --markers \
  --markers-unit km \
  --overlay "name,distance,elevation" \
  --overlay-position "bottom-right"
```

**Expected Output:**

```
Parsing GPX file...
Rendering route...
Adding distance markers every 1 km...
Adding information overlay at bottom-right position...
Exporting to PNG format...
Success! Route visualization saved to run-visualization.png
```

The output will be a PNG file with the running route in orange (#FF5500), medium-thickness solid lines, distance markers every kilometer, and an overlay in the bottom-right showing the route name, total distance, and elevation data.

**Example Config for Running Routes:**

```yaml
# running-config.yml
defaults:
  thickness: medium
  style: solid
  color: "#FF5500"
  background: "#FFFFFF"
  markers: true
  markers_unit: km
  overlay:
    enabled: true
    elements:
      - name
      - distance
      - elevation
    position: bottom-right
```

Usage with config:
```bash
gpx-art --config running-config.yml convert morning-run.gpx run-artwork
```

### Cycling Activity Artwork

Create a stylized visualization of a cycling activity with a colorful route trace and essential information.

```bash
gpx-art convert bike-ride.gpx cycling-art \
  --color "#00AAFF" \
  --background "#F8F8FF" \
  --thickness thick \
  --style solid \
  --markers \
  --markers-unit km \
  --overlay "name,distance" \
  --overlay-position "top-left" \
  --format png,svg
```

**Expected Output:**

```
Parsing GPX file...
Rendering route...
Adding distance markers every 1 km...
Adding information overlay at top-left position...
Exporting to PNG format...
Exporting to SVG format...
Success! Route visualizations saved to:
- cycling-art.png
- cycling-art.svg
```

The output will be PNG and SVG files with the cycling route in blue (#00AAFF) with thick solid lines on a light blue background (#F8F8FF), distance markers every kilometer, and an overlay in the top-left showing the route name and total distance.

### Hiking Trail Maps

Create a detailed visualization of a hiking trail with distance markers in miles and comprehensive information.

```bash
gpx-art convert mountain-trail.gpx trail-map \
  --color "#006600" \
  --background "#F5F5F5" \
  --thickness medium \
  --style dashed \
  --markers \
  --markers-unit mi \
  --overlay "name,distance,elevation,duration" \
  --overlay-position "top-right"
```

**Expected Output:**

```
Parsing GPX file...
Rendering route...
Adding distance markers every 1 mi...
Adding information overlay at top-right position...
Exporting to PNG format...
Success! Route visualization saved to trail-map.png
```

The output will be a PNG file with the hiking trail in green (#006600) with medium-thickness dashed lines on a light gray background (#F5F5F5), distance markers every mile, and an overlay in the top-right showing the route name, total distance, elevation data, and duration.

### Multi-Activity Visualizations

Process multiple GPX files to compare different activities or create a collection of visualizations.

First, create a configuration file for consistent styling:

```yaml
# multi-activity.yml
defaults:
  thickness: medium
  style: solid
  background: "#FFFFFF"
  markers: true
  markers_unit: km
  overlay:
    enabled: true
    elements:
      - name
      - distance
    position: bottom-right
```

Then, process multiple files with activity-specific colors:

```bash
# Process running activity
gpx-art --config multi-activity.yml convert run.gpx collection/run \
  --color "#FF5500"

# Process cycling activity
gpx-art --config multi-activity.yml convert cycle.gpx collection/cycle \
  --color "#00AAFF"

# Process hiking activity
gpx-art --config multi-activity.yml convert hike.gpx collection/hike \
  --color "#006600"
```

**Expected Output:**

Each command will produce a separate visualization with consistent styling but different colors to distinguish the activity types.

## Advanced Examples

### Custom Styling Combinations

Experiment with combinations of styles, thicknesses, colors, and backgrounds to create unique visualizations.

**Minimal Monochrome Style:**

```bash
gpx-art convert route.gpx minimal-art \
  --color "#000000" \
  --background "#FFFFFF" \
  --thickness thin \
  --style solid \
  --no-markers \
  --overlay ""
```

**Bold Contrast Style:**

```bash
gpx-art convert route.gpx bold-art \
  --color "#FF0000" \
  --background "#000000" \
  --thickness thick \
  --style solid \
  --no-markers \
  --overlay ""
```

**Technical Blueprint Style:**

```bash
gpx-art convert route.gpx blueprint \
  --color "#FFFFFF" \
  --background "#0A3A5A" \
  --thickness thin \
  --style dashed \
  --markers \
  --markers-unit km \
  --overlay "distance,elevation" \
  --overlay-position "bottom-left"
```

**Colorful Path Style:**

```bash
gpx-art convert route.gpx colorful-path \
  --color "#8A2BE2" \
  --background "#F0F8FF" \
  --thickness thick \
  --style dashed \
  --markers \
  --markers-unit km \
  --overlay "name" \
  --overlay-position "top-right"
```

### Multi-Format Exports

Export a visualization in multiple formats for different purposes.

```bash
gpx-art convert marathon.gpx boston-marathon \
  --color "#0072CE" \
  --background "#FFFFFF" \
  --thickness medium \
  --style solid \
  --markers \
  --markers-unit mi \
  --overlay "name,distance,elevation" \
  --overlay-position "bottom-right" \
  --format png,svg,pdf
```

**Expected Output:**

```
Parsing GPX file...
Rendering route...
Adding distance markers every 1 mi...
Adding information overlay at bottom-right position...
Exporting to multiple formats...
Success! Route visualizations saved to:
- boston-marathon.png (for web or quick viewing)
- boston-marathon.svg (for editing or scaling)
- boston-marathon.pdf (for printing or publishing)
```

Each format has specific advantages:
- **PNG**: Best for web display and social media sharing
- **SVG**: Vector format ideal for scaling and further editing
- **PDF**: Publication-quality output suitable for printing

### Batch Processing

Process multiple GPX files at once using a script.

**Bash Script (Unix/Linux/Mac):**

```bash
#!/bin/bash
# batch-process.sh

OUTDIR="./artwork"
CONFIG="./batch-config.yml"
mkdir -p $OUTDIR

# Create a configuration file if it doesn't exist
if [ ! -f "$CONFIG" ]; then
  cat > "$CONFIG" <<EOF
defaults:
  thickness: medium
  style: solid
  color: "#3498DB"
  background: "#F8F9F9"
  markers: true
  markers_unit: km
  overlay:
    enabled: true
    elements:
      - name
      - distance
    position: bottom-right
    
export:
  formats:
    - png
    - svg
EOF
  echo "Created configuration file: $CONFIG"
fi

# Process all GPX files
for file in data/*.gpx; do
  if [ -f "$file" ]; then
    filename=$(basename "$file" .gpx)
    echo "Processing $file..."
    gpx-art --config "$CONFIG" convert "$file" "$OUTDIR/$filename"
    echo "Done! Output saved to $OUTDIR/$filename.png"
  fi
done

echo "Batch processing complete!"
```

**Usage:**
```bash
chmod +x batch-process.sh
./batch-process.sh
```

**Expected Output:**
```
Created configuration file: ./batch-config.yml
Processing data/run1.gpx...
Parsing GPX file...
Rendering route...
Adding distance markers every 1 km...
Adding information overlay at bottom-right position...
Exporting to PNG format...
Done! Output saved to artwork/run1.png
Processing data/run2.gpx...
[...processing continues for all files...]
Batch processing complete!
```

## Configuration Examples

### Activity-Specific Configs

Create different configuration files optimized for different activity types.

**Running Configuration (running.yml):**

```yaml
defaults:
  thickness: medium
  style: solid
  color: "#FF5500"
  background: "#FFFFFF"
  markers: true
  markers_unit: km
  markers_frequency: 1
  overlay:
    enabled: true
    elements:
      - name
      - distance
      - pace
    position: bottom-right
    
visualization:
  padding: 0.1
  simplify: true
  simplify_tolerance: 0.0001
```

**Cycling Configuration (cycling.yml):**

```yaml
defaults:
  thickness: thick
  style: solid
  color: "#0066CC"
  background: "#F8F8FF"
  markers: true
  markers_unit: km
  markers_frequency: 5
  overlay:
    enabled: true
    elements:
      - name
      - distance
      - elevation
      - duration
    position: top-left
    
export:
  formats:
    - png
    - svg
  dpi: 300
```

**Hiking Configuration (hiking.yml):**

```yaml
defaults:
  thickness: medium
  style: dashed
  color: "#006600"
  background: "#F5F5F5"
  markers: true
  markers_unit: mi
  markers_frequency: 1
  overlay:
    enabled: true
    elements:
      - name
      - distance
      - elevation
      - duration
    position: top-right
    
visualization:
  padding: 0.15
  simplify: false
```

**Usage:**

```bash
# Process a running activity
gpx-art --config running.yml convert morning-run.gpx run-art

# Process a cycling activity
gpx-art --config cycling.yml convert weekend-ride.gpx ride-art

# Process a hiking activity
gpx-art --config hiking.yml convert forest-trail.gpx trail-art
```

### Style Presets

Create configuration files with different visual styles that can be applied to any activity.

**Minimalist Style (minimalist.yml):**

```yaml
defaults:
  thickness: thin
  style: solid
  color: "#000000"
  background: "#FFFFFF"
  markers: false
  overlay:
    enabled: false
    
export:
  formats:
    - png
    - svg
```

**Blueprint Style (blueprint.yml):**

```yaml
defaults:
  thickness: thin
  style: dashed
  color: "#FFFFFF"
  background: "#0A3A5A"
  markers: true
  markers_unit: km
  overlay:
    enabled: true
    elements:
      - distance
      - elevation
    position: bottom-left
```

**Artistic Style (artistic.yml):**

```yaml
defaults:
  thickness: thick
  style: solid
  color: "#9B30FF"
  background: "#F0F0F0"
  markers: false
  overlay:
    enabled: true
    elements:
      - name
    position: bottom-right
    
visualization:
  padding: 0.2
```

**Usage:**

```bash
# Apply minimalist style to any activity
gpx-art --config minimalist.yml convert activity.gpx minimal-art

# Apply blueprint style to any activity
gpx-art --config blueprint.yml convert activity.gpx blueprint-art

# Apply artistic style to any activity
gpx-art --config artistic.yml convert activity.gpx artistic-art
```

### Advanced Customization

Explore advanced configuration options for specialized use cases.

**High-Resolution Export (high-res.yml):**

```yaml
defaults:
  thickness: medium
  style: solid
  color: "#3498DB"
  background: "#FFFFFF"
  
export:
  formats:
    - png
    - svg
    - pdf
  dpi: 600
  
visualization:
  padding: 0.1
  simplify: false
```

**Memory-Optimized for Large Files (memory-opt.yml):**

```yaml
defaults:
  thickness: thin
  style: solid
  color: "#000000"
  background: "#FFFFFF"
  markers: false
  overlay:
    enabled: false
    
visualization:
  simplify: true
  simplify_tolerance: 0.0005
  
system:
  logging:
    level: warning
```

**Social Media Ready (social-media.yml):**

```yaml
defaults:
  thickness: thick
  style: solid
  color: "#E74C3C"
  background: "#ECF0F1"
  markers: true
  markers_unit: km
  overlay:
    enabled: true
    elements:
      - name
      - distance
    position: bottom-right
    
export:
  formats:
    - png
  dpi: 300
  
visualization:
  padding: 0.15
```

## Integration Examples

### Script Integration

Integrate GPX Art Generator into larger workflows using scripts.

**Python Integration:**

```python
#!/usr/bin/env python3
# process_activities.py

import os
import subprocess
import json
from datetime import datetime

# Configuration
GPX_DIR = "./activities"
OUTPUT_DIR = "./visualizations"
CONFIG_PATH = "./config.yml"

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Get all GPX files
gpx_files = [f for f in os.listdir(GPX_DIR) if f.endswith('.gpx')]

# Process each file
for gpx_file in gpx_files:
    file_path = os.path.join(GPX_DIR, gpx_file)
    base_name = os.path.splitext(gpx_file)[0]
    output_path = os.path.join(OUTPUT_DIR, base_name)
    
    # Get info about the GPX file
    try:
        result = subprocess.run(
            ["gpx-art", "info", file_path, "--json"],
            capture_output=True, text=True, check=True
        )
        info = json.loads(result.stdout)
        
        # Choose color based on activity type
        activity_type = info.get("type", "unknown").lower()
        if "run" in activity_type:
            color = "#FF5500"  # Orange for running
        elif "ride" in activity_type or "cycle" in activity_type:
            color = "#00AAFF"  # Blue for cycling
        elif "hike" in activity_type or "walk" in activity_type:
            color = "#006600"  # Green for hiking/walking
        else:
            color = "#3498DB"  # Default blue
            
        # Convert the GPX file to artwork
        print(f"Processing {gpx_file}...")
        cmd = [
            "gpx-art",
            "--config", CONFIG_PATH,
            "convert",
            file_path,
            output_path,
            "--color", color
        ]
        
        subprocess.run(cmd, check=True)
        print(f"Created visualization at {output_path}.png")
    
    except subprocess.CalledProcessError as e:
        print(f"Error processing {gpx_file}: {e}")

print(f"Processed {len(gpx_files)} GPX files.")
```

### Automation Examples

Automate GPX Art generation as part of larger workflows.

**Automated Processing with Strava API:**

Here's an example script that fetches new activities from Strava and creates visualizations:

```python
#!/usr/bin/env python3
# strava_to_art.py

import os
import requests
import subprocess
import tempfile
from datetime import datetime, timedelta

# Strava API configuration
# (You need to create an app at https://www.strava.com/settings/api)
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
REFRESH_TOKEN = "YOUR_REFRESH_TOKEN"

# Output configuration
OUTPUT_DIR = "./strava-art"
CONFIG_FILE = "./strava-config.yml"

def get_access_token():
    """Get a fresh access token using the refresh token."""
    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
            "grant_type": "refresh_token"
        }
    )
    return response.json()["access_token"]

def get_recent_activities(access_token, days=7):
    """Get activities from the last X days."""
    after_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(
        "https://www.strava.com/api/v3/athlete/activities",
        headers=headers,
        params={"after": after_timestamp, "per_page": 30}
    )
    return response.json()

def download_gpx(activity_id, access_token):
    """Download GPX file for an activity."""
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        f"https://www.strava.com/api/v3/activities/{activity_id}/streams",
        headers=headers,
        params={"keys": "latlng,altitude,time", "key_by_type": True}
    )
    
    if response.status_code != 200:
        return None
    
    # Create a GPX file from the streams
    streams = response.json()
    if "latlng" not in streams:
        return None
        
    # Create a temporary GPX file
    fd, path = tempfile.mkstemp(suffix=".gpx")
    with os.fdopen(fd, 'w') as f:
        # Write GPX XML format
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<gpx version="1.1" creator="Strava GPX Generator">\n')
        f.write('  <trk>\n')
        f.write(f'    <name>Activity {activity_id}</name>\n')
        f.write('    <trkseg>\n')
        
        # Write track points
        for i, latlng in enumerate(streams["latlng"]["data"]):
            lat, lng = latlng
            ele = streams.get("altitude", {}).get("data", [0] * len(streams["latlng"]["data"]))[i]
            f.write(f'      <trkpt lat="{lat}" lon="{lng}">\n')
            f.write(f'        <ele>{ele}</ele>\n')
            f.write('      </trkpt>\n')
            
        f.write('    </trkseg>\n')
        f.write('  </trk>\n')
        f.write('</gpx>\n')
    
    return path

def main():
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Get access token
    access_token = get_access_token()
    
    # Get recent activities
    activities = get_recent_activities(access_token)
    print(f"Found {len(activities)} recent activities")
    
    for activity in activities:
        activity_id = activity["id"]
        activity_name = activity["name"]
        activity_type = activity["type"]
        start_date = activity["start_date"].split("T")[0]
        
        # Skip activities without GPS data
        if activity["has_heartrate"] is False and activity_type in ["VirtualRide", "VirtualRun"]:
            print(f"Skipping {activity_name} - no GPS data")
            continue
            
        print(f"Processing {activity_name} ({activity_type}) from {start_date}")
        
        # Download GPX
        gpx_path = download_gpx(activity_id, access_token)
        if not gpx_path:
            print(f"Failed to download GPX for {activity_name}")
            continue
            
        try:
            # Create a filename safe version of the activity name
            safe_name = "".join(c if c.isalnum() else "_" for c in activity_name)
            output_file = f"{OUTPUT_DIR}/{start_date}_{safe_name}"
            
            # Choose color based on activity type
            if activity_type == "Run":
                color = "#FF5500"  # Orange for running
            elif activity_type in ["Ride", "BikeRide"]:
                color = "#00AAFF"  # Blue for cycling
            elif activity_type in ["Hike", "Walk"]:
                color = "#006600"  # Green for hiking/walking
            else:
                color = "#3498DB"  # Default blue
            
            # Generate the artwork
            cmd = [
                "gpx-art", 
                "convert", 
                gpx_path, 
                output_file,
                "--color", color,
                "--format", "png,svg"
            ]
            
            if CONFIG_FILE and os.path.exists(CONFIG_FILE):
                cmd[1:1] = ["--config", CONFIG_FILE]
                
            subprocess.run(cmd, check=True)
            print(f"Created visualization at {output_file}.png")
            
        except Exception as e:
            print(f"Error processing {activity_name}: {e}")
        finally:
            # Clean up the temporary GPX file
            if gpx_path and os.path.exists(gpx_path):
                os.unlink(gpx_path)

if __name__ == "__main__":
    main()
```

### Error Handling Patterns

Here are examples of robust error handling when using GPX Art Generator in scripts and applications.

**Basic Error Handling:**

```python
#!/usr/bin/env python3
# error_handling_example.py

import subprocess
import sys

def process_gpx(input_file, output_path):
    """Process a GPX file with error handling."""
    try:
        # First validate the file
        validate_cmd = ["gpx-art", "validate", input_file]
        result = subprocess.run(validate_cmd, capture_output=True, text=True, check=False)
        
        if result.returncode != 0:
            print(f"Validation failed: {result.stderr.strip()}")
            return False
        
        # If validation succeeds, convert the file
        convert_cmd = ["gpx-art", "convert", input_file, output_path]
        result = subprocess.run(convert_cmd, capture_output=True, text=True, check=False)
        
        if result.returncode != 0:
            print(f"Conversion failed: {result.stderr.strip()}")
            return False
            
        print(f"Successfully created visualization at {output_path}.png")
        return True
        
    except FileNotFoundError:
        print("Error: gpx-art command not found. Please ensure it's installed and in your PATH.")
        return False
    except subprocess.SubprocessError as e:
        print(f"Error executing gpx-art command: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: error_handling_example.py <input_file.gpx> <output_path>")
        sys.exit(1)
        
    success = process_gpx(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)
```

**Advanced Error Recovery:**

```python
#!/usr/bin/env python3
# advanced_error_handling.py

import os
import subprocess
import tempfile
import json
import shutil

class GPXArtError(Exception):
    """Custom exception for GPX Art processing errors."""
    pass

def process_with_recovery(input_file, output_path, options=None):
    """Process a GPX file with advanced error recovery strategies."""
    options = options or {}
    
    # Ensure the output directory exists
    output_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # First get info about the GPX file
        info_cmd = ["gpx-art", "info", input_file, "--json"]
        result = subprocess.run(info_cmd, capture_output=True, text=True, check=False)
        
        if result.returncode != 0:
            # Try validating to get more specific error
            validate_cmd = ["gpx-art", "validate", input_file]
            val_result = subprocess.run(validate_cmd, capture_output=True, text=True, check=False)
            
            if "No track data found" in val_result.stdout:
                raise GPXArtError(f"The GPX file {input_file} doesn't contain any track data")
            elif "Empty route" in val_result.stdout:
                raise GPXArtError(f"The GPX file {input_file} contains an empty route")
            else:
                raise GPXArtError(f"Invalid GPX file: {val_result.stdout.strip()}")
        
        # Parse the file info
        try:
            file_info = json.loads(result.stdout)
        except json.JSONDecodeError:
            # Fall back to using generic options
            file_info = {}
        
        # Build command with fallbacks for options
        convert_cmd = ["gpx-art", "convert", input_file, output_path]
        
        # Add format option with fallback mechanism
        formats = options.get("formats", ["png", "svg", "pdf"])
        
        # Try the formats one by one until one succeeds
        for format_attempt in range(len(formats)):
            current_formats = formats[:len(formats) - format_attempt]
            format_str = ",".join(current_formats)
            
            retry_cmd = convert_cmd + ["--format", format_str]
            
            # Add other options
            if "color" in options:
                retry_cmd.extend(["--color", options["color"]])
            if "thickness" in options:
                retry_cmd.extend(["--thickness", options["thickness"]])
            if "style" in options:
                retry_cmd.extend(["--style", options["style"]])
                
            # Try current format combination
            print(f"Attempting export with formats: {format_str}")
            result = subprocess.run(retry_cmd, capture_output=True, text=True, check=False)
            
            if result.returncode == 0:
                print(f"Successfully created visualization with formats: {format_str}")
                return [f"{output_path}.{fmt}" for fmt in current_formats]
            
            # If we're on the last attempt with just one format and it failed, raise error
            if format_attempt == len(formats) - 1:
                raise GPXArtError(f"All export formats failed: {result.stderr.strip()}")
        
    except FileNotFoundError:
        raise GP
