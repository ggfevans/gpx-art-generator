# GPX Art Generator: Project Specification

## Project Overview

Create a modular CLI tool that transforms GPX files into printable artwork, with an optional web interface wrapper. The tool generates line art and can add distance markers and information overlays to create beautiful representations of athletic routes.

## Project Principles

1. **CLI-First Design**: Core functionality in a command-line tool
2. **Web as Wrapper**: Web interface simply calls the CLI tool
3. **Self-Contained**: No external dependencies required at runtime
4. **Modular**: Each component has a single responsibility

## Technical Architecture

### Core Components

#### 1. CLI Application (`gpx-art`)
```bash
# Basic usage
gpx-art convert route.gpx output.png

# With options
gpx-art convert route.gpx output.png \
  --thickness=thick \
  --color="#FF0000" \
  --markers-unit=miles \
  --overlay="distance,date" \
  --format=pdf,svg,png
```

#### 2. Web Interface
- Simplified UI that wraps the CLI tool
- Uploads file, builds CLI command, executes it
- Returns generated files for download

### Technology Stack

#### CLI Tool
- **Language**: Python 3.9+
- **Framework**: Click (CLI framework)
- **Dependencies**: 
  - `gpxpy` (GPX parsing)
  - `matplotlib` (visualization)
  - `svgutils` (SVG manipulation)
  - `reportlab` (PDF generation)
  - `pillow` (PNG processing)

#### Web Interface
- **Backend**: FastAPI (lightweight wrapper)
- **Frontend**: React with TypeScript
- **Packaging**: Docker for easy deployment

### Project Structure
```
gpx-art-generator/
├── cli/
│   ├── gpx_art/
│   │   ├── __init__.py
│   │   ├── main.py          # CLI entry point
│   │   ├── parsers.py       # GPX parsing
│   │   ├── visualizer.py    # Route rendering
│   │   ├── exporters.py     # File format exports
│   │   └── config.py        # Configuration handling
│   ├── pyproject.toml       # Python package config
│   ├── requirements.txt
│   └── tests/
├── web/
│   ├── backend/
│   │   ├── main.py          # FastAPI app
│   │   └── handlers.py      # CLI wrapper
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── App.tsx
│   │   │   ├── components/
│   │   │   └── types.ts
│   │   └── package.json
│   ├── Dockerfile
│   └── docker-compose.yml
├── README.md
└── docs/
    ├── CLI-USAGE.md
    └── WEB-SETUP.md
```

## CLI Tool Specification

### Command Structure
```
gpx-art [COMMAND] [ARGUMENTS] [OPTIONS]
```

### Commands

#### `convert`
Convert GPX file to artwork.

**Arguments:**
- `input_file`: Path to GPX file
- `output_file`: Path for output file (extension determines format)

**Options:**
```
--thickness TEXT      Line thickness (thin|medium|thick) [default: medium]
--color TEXT          Line color in hex (e.g., #FF0000) [default: #000000]  
--style TEXT          Line style (solid|dashed) [default: solid]
--markers / --no-markers      Enable distance markers [default: True]
--markers-unit TEXT   Distance unit (miles|km) [default: miles]
--overlay TEXT        Comma-separated fields to overlay (distance,duration,elevation,date,name)
--position TEXT       Overlay position (top-left|top-right|bottom-left|bottom-right) [default: top-left]
--format TEXT         Output formats (png,svg,pdf) - comma-separated for multiple [default: png]
--width INTEGER       Output width in inches for print formats [default: 36]
--height INTEGER      Output height in inches for print formats [default: 12]
--dpi INTEGER         DPI for raster formats [default: 300]
--help                Show this message and exit
```

#### `validate`
Check if GPX file is valid and readable.

```
gpx-art validate input.gpx
```

#### `info`
Display information about GPX file.

```
gpx-art info input.gpx
```

### Configuration File Support

The CLI supports a YAML config file:

```yaml
# ~/.gpx-art/config.yml
defaults:
  thickness: medium
  color: "#000000"
  style: solid
  markers:
    enabled: true
    unit: miles
  overlay:
    enabled: true
    fields:
      - distance
      - date
    position: top-left
  export:
    formats:
      - png
    width: 36
    height: 12
    dpi: 300
```

## Web Interface Specification

### Backend API
Single endpoint that proxies to CLI:

```
POST /api/generate
Content-Type: multipart/form-data

Request:
- file: GPX file
- options: JSON configuration

Response:
- files: Array of generated files
- metadata: Generation details
```

### Frontend Flow
1. Upload GPX file
2. Configure options visually
3. Submit for processing
4. Download generated files

## Development Roadmap

### Phase 1: CLI MVP
- Basic GPX parsing
- Simple line rendering
- PNG export only
- Essential options (thickness, color)

### Phase 2: CLI Enhancement
- Multiple export formats
- Distance markers
- Information overlay
- Configuration file support

### Phase 3: Web Wrapper
- FastAPI backend
- React frontend
- Docker packaging
- Documentation

### Phase 4: Polish
- Error handling
- Progress indicators
- Example gallery
- Installation scripts

## Installation & Usage

### CLI Installation
```bash
# From PyPI (future)
pip install gpx-art

# From source
git clone https://github.com/yourusername/gpx-art-generator.git
cd gpx-art-generator/cli
pip install -e .
```

### Web Deployment
```bash
cd gpx-art-generator/web
docker-compose up -d
```

Access at http://localhost:8000

## Example Use Cases

### Command Line
```bash
# Simple usage
gpx-art convert my-ultra.gpx artwork.png

# Advanced usage
gpx-art convert my-ultra.gpx artwork.pdf \
  --thickness=thick \
  --color="#1E40AF" \
  --markers-unit=miles \
  --overlay="distance,duration,elevation,date" \
  --position=bottom-right \
  --format=png,svg,pdf
```

### Python API
```python
from gpx_art import GPXArtGenerator

generator = GPXArtGenerator()
generator.load_gpx("route.gpx")
generator.set_style(thickness="thick", color="#FF0000")
generator.add_markers(unit="miles")
generator.add_overlay(fields=["distance", "date"])
generator.export("output.png", format="png", dpi=300)
```

## Technical Considerations

### Error Handling
- Invalid GPX files
- Memory constraints for large routes
- File permission issues

### Performance
- Optimize for typical GPX file sizes (< 10MB)
- Process routes with up to 10,000 points efficiently
- Target < 5 second generation time

### Security
- Sanitize CLI inputs
- Validate file extensions
- Limit file sizes in web interface

## Non-Goals
- Real-time preview
- Route editing
- Social features
- Cloud storage integration

This modular approach allows starting with a simple CLI tool that can be directly used by technically-savvy users, while the web interface provides accessibility for all users.
