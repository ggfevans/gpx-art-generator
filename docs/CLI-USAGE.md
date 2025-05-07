# GPX Art Generator - CLI Usage Guide

This guide provides detailed instructions for using the GPX Art Generator command-line interface.

## Table of Contents

- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Basic Usage](#basic-usage)
  - [First Run](#first-run)
- [Command Reference](#command-reference)
  - [convert](#convert)
  - [validate](#validate)
  - [info](#info)
  - [init-config](#init-config)
  - [Global Options](#global-options)
- [Configuration File Guide](#configuration-file-guide)
  - [Configuration Locations](#configuration-locations)
  - [Configuration Structure](#configuration-structure)
  - [Common Configurations](#common-configurations)
- [Troubleshooting](#troubleshooting)
  - [Common Issues and Solutions](#common-issues-and-solutions)
  - [Debug Mode](#debug-mode)
  - [Log Files](#log-files)
- [Best Practices and Tips](#best-practices-and-tips)
  - [Working with Large GPX Files](#working-with-large-gpx-files)
  - [Creating Beautiful Visualizations](#creating-beautiful-visualizations)
  - [Batch Processing](#batch-processing)

## Getting Started

### Installation

You can install GPX Art Generator using pip:

```bash
pip install gpx-art
```

After installation, verify that the tool works correctly:

```bash
gpx-art --version
```

### Basic Usage

The basic workflow consists of:

1. **Validating** your GPX file to ensure it's properly formatted
2. **Getting information** about your GPX file
3. **Converting** your GPX file to visual artwork
4. Optionally, creating a **configuration file** for customized settings

### First Run

Here's how to create your first GPX art:

```bash
# Create a configuration file (optional)
gpx-art init-config

# Get information about your GPX file
gpx-art info your-activity.gpx

# Create a simple visualization
gpx-art convert your-activity.gpx my-artwork

# This creates my-artwork.png in the current directory
```

## Command Reference

### convert

The `convert` command transforms GPX files into visual artwork.

#### Basic Usage

```bash
gpx-art convert input.gpx output
```

This creates `output.png` with default styling settings.

#### Examples

**Basic conversion with custom color:**
```bash
gpx-art convert run.gpx my-run --color "#FF5500"
```

**Multiple export formats:**
```bash
gpx-art convert ride.gpx bike-ride --format png,svg,pdf
```
This creates `bike-ride.png`, `bike-ride.svg`, and `bike-ride.pdf`.

**Customized visualization with distance markers:**
```bash
gpx-art convert hike.gpx mountain-trek --thickness thick --style dashed --markers --markers-unit km
```

**Full customization example:**
```bash
gpx-art convert marathon.gpx boston-2024 \
  --color "#0066CC" \
  --background "#F5F5F5" \
  --thickness thick \
  --style solid \
  --markers \
  --markers-unit mi \
  --overlay "name,distance,elevation" \
  --overlay-position "bottom-right" \
  --format png,svg
```

### validate

The `validate` command checks if a GPX file is valid and reports any issues.

#### Basic Usage

```bash
gpx-art validate input.gpx
```

#### Examples

**Standard validation:**
```bash
gpx-art validate activity.gpx
```

**Strict validation:**
```bash
gpx-art validate activity.gpx --strict
```
This performs additional checks and reports warnings about potential issues.

### info

The `info` command displays detailed information about a GPX file.

#### Basic Usage

```bash
gpx-art info input.gpx
```

#### Examples

**Basic information:**
```bash
gpx-art info run.gpx
```
This displays general information about the GPX file, including:
- File details (size, creation date)
- Track information (name, type)
- Route statistics (distance, elevation gain/loss, duration)
- Geographic bounds

**JSON output:**
```bash
gpx-art info run.gpx --json > run-info.json
```
This exports the information in JSON format to a file.

### init-config

The `init-config` command creates a configuration file with default settings.

#### Basic Usage

```bash
gpx-art init-config
```
This creates a `gpx-art.yml` file in the current directory.

#### Examples

**Custom configuration location:**
```bash
gpx-art init-config ~/.config/gpx-art/config.yml
```

**Force overwrite existing configuration:**
```bash
gpx-art init-config --force
```

### Global Options

These options can be used with any command:

#### `--config PATH`

Specify a custom configuration file:

```bash
gpx-art --config ~/my-config.yml convert run.gpx artwork
```

#### `--verbose, -v`

Increase output verbosity (can be used multiple times):

```bash
# Normal verbosity
gpx-art convert run.gpx artwork

# Increased verbosity
gpx-art -v convert run.gpx artwork

# Maximum verbosity
gpx-art -vv convert run.gpx artwork
```

#### `--debug`

Enable debug mode for detailed information:

```bash
gpx-art --debug convert run.gpx artwork
```

#### `--help`

Display help information:

```bash
# General help
gpx-art --help

# Command-specific help
gpx-art convert --help
```

## Configuration File Guide

### Configuration Locations

The application looks for configuration files in the following order:

1. Path specified with `--config` option
2. `./gpx-art.yml` in the current directory
3. `~/.config/gpx-art/config.yml` in the user's home directory

### Configuration Structure

A basic configuration file looks like this:

```yaml
defaults:
  # Visualization styling
  thickness: medium    # thin, medium, thick
  style: solid         # solid, dashed
  color: "#0066CC"     # Any valid hex color code
  background: "#FFFFFF"  # Any valid hex color code
  
  # Marker settings
  markers: true        # true or false
  markers_unit: km     # km or mi
  
  # Information overlay settings
  overlay:
    enabled: true
    elements:
      - name
      - distance
      - elevation
    position: top-right  # top-left, top-right, bottom-left, bottom-right
    
export:
  # Export format settings
  formats:
    - png              # Default export formats
  dpi: 300             # DPI for raster exports
```

### Common Configurations

#### Minimal Configuration

A minimal configuration with just essential settings:

```yaml
defaults:
  thickness: medium
  color: "#FF0000"
  markers: false
```

#### Running Activity Configuration

Optimized for running activities:

```yaml
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

#### Artistic Style Configuration

Focused on aesthetic appearance:

```yaml
defaults:
  thickness: thick
  style: dashed
  color: "#8A2BE2"  # BlueViolet
  background: "#F8F8FF"  # GhostWhite
  markers: false
  overlay:
    enabled: false
    
export:
  formats:
    - png
    - svg
  dpi: 600
  
visualization:
  padding: 0.2
```

## Troubleshooting

### Common Issues and Solutions

#### File Not Found Errors

**Issue:** `Error: Cannot find file 'path/to/file.gpx'`

**Solution:**
- Verify the file path is correct
- Check file permissions
- Use absolute paths instead of relative paths

```bash
# Using absolute path
gpx-art convert /full/path/to/activity.gpx output
```

#### Invalid GPX File

**Issue:** `Error: Invalid GPX file: XML syntax error at line X`

**Solution:**
- Validate your GPX file first: `gpx-art validate file.gpx`
- Try redownloading the GPX file from its source
- Use a GPX repair tool to fix common issues

#### Export Format Errors

**Issue:** `Error: Failed to export PDF: Missing dependency`

**Solution:**
- Install required dependencies:
  ```bash
  pip install matplotlib-pdf
  ```
- Try a different export format:
  ```bash
  gpx-art convert input.gpx output --format png,svg
  ```

#### Memory Issues with Large Files

**Issue:** `Error: Memory error when rendering route`

**Solution:**
- Try simplifying the route:
  ```yaml
  # In config file
  visualization:
    simplify: true
    simplify_tolerance: 0.0002  # Increase this value for more simplification
  ```
- Process a subset of the GPX file using external tools

### Debug Mode

For detailed debugging information, use the `--debug` flag:

```bash
gpx-art --debug convert input.gpx output
```

This will:
- Show detailed error traces
- Increase logging verbosity
- Display internal processing steps

### Log Files

The application maintains log files in your user directory:

- Location: `~/.gpx-art/logs/`
- Main log file: `gpx-art.log`

For verbose logging output:

```bash
gpx-art -vv convert input.gpx output
```

To view the most recent log file:

```bash
# On Unix/Linux/Mac
cat ~/.gpx-art/logs/gpx-art.log | tail -n 100

# On Windows
type %USERPROFILE%\.gpx-art\logs\gpx-art.log | more
```

## Best Practices and Tips

### Working with Large GPX Files

For large GPX files (>10MB or with thousands of trackpoints):

1. **Validate first**:
   ```bash
   gpx-art validate large-file.gpx
   ```

2. **Enable simplification** in your config:
   ```yaml
   visualization:
     simplify: true
     simplify_tolerance: 0.0001  # Adjust as needed
   ```

3. **Use the PNG format** for initial tests:
   ```bash
   gpx-art convert large-file.gpx output --format png
   ```

4. **Increase memory limits** if needed (for advanced users):
   ```bash
   PYTHONMEM=2G gpx-art convert large-file.gpx output
   ```

### Creating Beautiful Visualizations

For aesthetically pleasing visualizations:

1. **Choose complementary colors**:
   ```bash
   gpx-art convert route.gpx art --color "#3498DB" --background "#F8F9F9"
   ```

2. **Experiment with line styles**:
   ```bash
   gpx-art convert route.gpx art --style dashed --thickness thick
   ```

3. **Try different overlay positions**:
   ```bash
   gpx-art convert route.gpx art --overlay "name,distance" --overlay-position bottom-left
   ```

4. **For framing, add padding**:
   ```yaml
   # In config file
   visualization:
     padding: 0.15  # Adds 15% padding around the route
   ```

5. **Export in multiple formats** for different uses:
   ```bash
   gpx-art convert route.gpx artwork --format png,svg,pdf
   ```

### Batch Processing

To process multiple GPX files at once:

**Using a Bash script (Unix/Linux/Mac):**

```bash
#!/bin/bash
OUTDIR="./artwork"
mkdir -p $OUTDIR

for file in *.gpx; do
  filename=$(basename "$file" .gpx)
  echo "Processing $file..."
  gpx-art convert "$file" "$OUTDIR/$filename" --format png,svg
done
```

**Using a PowerShell script (Windows):**

```powershell
$OUTDIR=".\artwork"
New-Item -ItemType Directory -Force -Path $OUTDIR

Get-ChildItem -Filter *.gpx | ForEach-Object {
  $filename = $_.BaseName
  Write-Host "Processing $_..."
  gpx-art convert $_.FullName "$OUTDIR\$filename" --format png,svg
}
```

