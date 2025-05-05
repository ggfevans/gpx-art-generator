# Phase 1: Foundation Setup Prompts

## Step 1: Project Scaffolding

```text
Create a new Python project called gpx-art-generator following this structure:

gpx-art-generator/
├── cli/
│   ├── gpx_art/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── parsers.py
│   │   ├── visualizer.py
│   │   ├── exporters.py
│   │   └── config.py
│   ├── pyproject.toml
│   ├── setup.py
│   ├── requirements.txt
│   └── tests/
│       ├── __init__.py
│       └── test_main.py
├── docs/
│   ├── SPECIFICATION.md
│   ├── CLI-USAGE.md
│   └── images/
├── README.md
├── LICENSE
└── .gitignore

Create:
1. Empty __init__.py files where needed
2. pyproject.toml with basic metadata (name: gpx-art, version: 0.1.0, requires-python: ">=3.9")
3. setup.py with entry point for gpx-art command
4. requirements.txt with: click>=8.0, gpxpy>=1.6.0
5. README.md with project title and basic description
6. LICENSE file with MIT license
7. .gitignore for Python projects including __pycache__, *.egg-info, .venv, .env
```

## Step 2: Environment Setup

```text
Set up the development environment for the cli/ directory:

1. Create a development requirements file: cli/requirements-dev.txt with:
   - pytest>=7.0
   - pytest-cov>=4.0
   - black>=22.0
   - isort>=5.0
   - mypy>=1.0
   - flake8>=6.0

2. Create cli/.pre-commit-config.yaml with hooks for:
   - black (code formatting)
   - isort (import sorting)
   - flake8 (linting)
   - mypy (type checking)

3. Create cli/pytest.ini with test configuration:
   - addopts = --cov=gpx_art --cov-report=html
   - testpaths = tests
   - python_files = test_*.py

4. Create cli/pyproject.toml configuration sections for:
   - [tool.black]: line-length = 88
   - [tool.isort]: profile = "black"
   - [tool.mypy]: strict = true

5. Create a simple Makefile in cli/ with targets:
   - install: pip install -e . && pip install -r requirements-dev.txt
   - test: pytest
   - lint: flake8 && mypy gpx_art
   - format: black . && isort .
   - clean: remove build artifacts
```

## Step 3: Basic CLI Structure

```text
Create a basic Click CLI structure in cli/gpx_art/main.py:

1. Import necessary modules:
   - click
   - sys

2. Create main command group:
   - @click.group()
   - @click.version_option()
   - def cli():
       """GPX Art Generator - Transform GPS routes into artwork."""
       pass

3. Add three empty command placeholders:
   - @cli.command()
     def convert(...):
         """Convert GPX file to artwork."""
         click.echo("Convert command not implemented")
         
   - @cli.command()
     def validate(...):
         """Validate GPX file."""
         click.echo("Validate command not implemented")
         
   - @cli.command()
     def info(...):
         """Display GPX file information."""
         click.echo("Info command not implemented")

4. Add entry point:
   if __name__ == "__main__":
       cli()

5. Update setup.py to include entry point:
   entry_points={
       'console_scripts': [
           'gpx-art=gpx_art.main:cli',
       ],
   }

6. Create a simple test in tests/test_main.py:
   - Test that cli() function exists
   - Test that --version option works
   - Test that --help option shows all three commands

Success criteria:
- `gpx-art --help` shows all three commands
- `gpx-art --version` shows version
- All commands show "not implemented" when called
```