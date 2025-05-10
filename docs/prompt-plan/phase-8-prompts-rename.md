# Phase 8: Project Renaming Plan - GPX Art Generator to Route-to-Art

## Overview of the Renaming Process

This document outlines a comprehensive plan for renaming the "gpx-art-generator" project to "route-to-art". The renaming involves changing the project name, module names, documentation references, and updating all related configurations while maintaining project integrity and functionality.

This renaming is motivated by:
- Creating a more user-friendly and descriptive name
- Better alignment with the project's purpose of transforming routes into artwork
- Improving marketability and brand perception

The process will be methodical, involving identification of all instances of the old name, systematic updates, and thorough testing to ensure no functionality is broken during the transition.

## Step-by-Step Instructions

### 1. Preparation Phase

1. **Create a new branch**
   ```bash
   git checkout -b feature/project-rename
   ```

2. **Identify all occurrences of the old name**
   ```bash
   find . -type f -not -path "*/\.*" -not -path "*/venv/*" -not -path "*/\__pycache__/*" -exec grep -l "gpx-art-generator\|gpx_art\|GPX Art Generator" {} \;
   ```

3. **Create a backup of the repository**
   ```bash
   cp -r /Users/gevans/code/projects/gpx-art-generator /Users/gevans/code/projects/gpx-art-generator-backup
   ```

### 2. Code and Package Renaming

1. **Rename Python package**
   - Change directory structure from `gpx_art` to `route_to_art`
   - Update all import statements

2. **Update module references**
   - Replace all imports and references to `gpx_art` with `route_to_art`
   - Update class and function names where appropriate

3. **Update configuration files**
   - Modify `setup.py`, `requirements.txt`, etc.
   - Update Docker configurations

4. **Update CLI command references**
   - Modify command names and references in CLI modules

### 3. Documentation Updates

1. **Update README.md and other markdown files**
   - Replace all occurrences of "GPX Art Generator" with "Route-to-Art"
   - Update project descriptions
   - Update command examples

2. **Update docstrings and comments**
   - Modify all relevant docstrings in Python files
   - Update inline comments

3. **Update code examples**
   - Update all examples in documentation
   - Ensure consistency in naming

### 4. Web Interface Updates

1. **Update frontend components**
   - Modify HTML titles
   - Update React component names
   - Change branding elements

2. **Update API endpoints**
   - Rename API routes if needed
   - Update API documentation

3. **Update UI text and labels**
   - Change all UI elements referring to the old name

## File and Directory Updates

### 1. Directory Renaming

```bash
# Rename the Python package directory
mv cli/gpx_art cli/route_to_art

# Update any other directories containing the old name
find . -type d -name "*gpx*art*" | while read dir; do
  new_dir=$(echo $dir | sed 's/gpx[_-]art/route-to-art/g')
  mv "$dir" "$new_dir"
done
```

### 2. Core Python Files

| Old Path | New Path |
|----------|----------|
| `cli/gpx_art/__init__.py` | `cli/route_to_art/__init__.py` |
| `cli/gpx_art/main.py` | `cli/route_to_art/main.py` |
| `cli/gpx_art/parser.py` | `cli/route_to_art/parser.py` |
| `cli/gpx_art/models.py` | `cli/route_to_art/models.py` |
| `cli/gpx_art/visualizer.py` | `cli/route_to_art/visualizer.py` |
| `cli/gpx_art/exporter.py` | `cli/route_to_art/exporter.py` |
| `cli/gpx_art/config.py` | `cli/route_to_art/config.py` |
| `cli/gpx_art/errors.py` | `cli/route_to_art/errors.py` |

### 3. Test Files

| Old Path | New Path |
|----------|----------|
| `cli/tests/test_parser.py` | `cli/tests/test_parser.py` (update imports) |
| `cli/tests/test_models.py` | `cli/tests/test_models.py` (update imports) |
| `cli/tests/test_visualizer.py` | `cli/tests/test_visualizer.py` (update imports) |
| `cli/tests/test_exporter.py` | `cli/tests/test_exporter.py` (update imports) |
| `cli/tests/test_config.py` | `cli/tests/test_config.py` (update imports) |
| `cli/tests/test_errors.py` | `cli/tests/test_errors.py` (update imports) |

### 4. Configuration Files

| Old Path | New Path |
|----------|----------|
| `cli/setup.py` | `cli/setup.py` (update package name) |
| `cli/requirements.txt` | `cli/requirements.txt` (update references) |
| `web/docker-compose.yml` | `web/docker-compose.yml` (update service names) |
| `web/backend/Dockerfile` | `web/backend/Dockerfile` (update references) |

### 5. Documentation Files

| Old Path | New Path |
|----------|----------|
| `README.md` | `README.md` (update content) |
| `docs/SPECIFICATION.md` | `docs/SPECIFICATION.md` (update content) |
| `docs/CLI-USAGE.md` | `docs/CLI-USAGE.md` (update content) |
| `docs/EXAMPLES.md` | `docs/EXAMPLES.md` (update content) |
| `docs/CONTRIBUTING.md` | `docs/CONTRIBUTING.md` (update content) |
| `docs/ARCHITECTURE.md` | `docs/ARCHITECTURE.md` (update content) |

## Testing and Verification Steps

### 1. Unit Tests

1. **Update and run all unit tests**
   ```bash
   cd cli
   python -m pytest
   ```

2. **Verify test coverage**
   ```bash
   python -m pytest --cov=route_to_art
   ```

### 2. Integration Tests

1. **Test CLI functionality**
   ```bash
   python -m route_to_art.main --help
   python -m route_to_art.main convert sample.gpx output.png
   ```

2. **Test configuration loading**
   ```bash
   python -m route_to_art.main validate sample.gpx --config config.yml
   ```

### 3. Web Interface Testing

1. **Test API endpoints**
   ```bash
   curl -X GET http://localhost:8000/api/
   ```

2. **Test frontend rendering**
   - Verify all UI elements display correctly
   - Ensure no references to old name remain

### 4. Documentation Testing

1. **Verify README instructions**
   - Follow installation steps
   - Test code examples

2. **Check hyperlinks**
   - Ensure all internal links work
   - Verify external links

### 5. Installation Testing

1. **Test package installation**
   ```bash
   pip install -e .
   route-to-art --help
   ```

2. **Docker container tests**
   ```bash
   docker-compose build
   docker-compose up -d
   ```

## Deployment Considerations

### 1. Repository and Package Hosting

1. **GitHub repository**
   - Consider creating a new repository or renaming the existing one
   - Update GitHub Pages if used
   - Update repository description and topics

2. **PyPI package**
   - Register new package name if distributing via PyPI
   - Ensure the old package points to the new one

### 2. Documentation and Website

1. **Update documentation site**
   - Rename site if using GitHub Pages or ReadTheDocs
   - Update domain name if necessary

2. **Update external references**
   - Identify and update any external links to the project

### 3. Backward Compatibility

1. **Deprecation notices**
   - Add deprecation warnings for old import paths
   - Create compatibility layer if needed

2. **Communication**
   - Notify users about the name change
   - Update any blog posts or articles about the project

### 4. Release Management

1. **Version number consideration**
   - Consider if the rename warrants a major version bump

2. **Release notes**
   - Document the rename in release notes
   - Provide clear migration instructions

## Conclusion

This renaming plan provides a comprehensive approach to transitioning from "gpx-art-generator" to "route-to-art" while maintaining project integrity. By following these steps methodically and conducting thorough testing, we can ensure a smooth transition with minimal disruption to users.

After completing all steps, review the entire project once more to catch any remaining references to the old name before finalizing the rename.

