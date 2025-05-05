# GPX Art Generator

Transform GPS routes into visual artwork. This tool allows you to convert GPX files (GPS Exchange Format) into artistic visualizations.

## Installation

```bash
# Install from the current directory
cd cli
pip install -e .
```

## Usage

The GPX Art Generator provides several commands:

```bash
# Show help
gpx-art --help

# Show version
gpx-art --version

# Convert a GPX file to artwork
gpx-art convert path/to/file.gpx

# Validate a GPX file
gpx-art validate path/to/file.gpx

# Display information about a GPX file
gpx-art info path/to/file.gpx
```

## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/yourusername/gpx-art-generator.git
cd gpx-art-generator/cli

# Install development dependencies
make install

# Run tests
make test

# Run linting
make lint

# Format code
make format
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
