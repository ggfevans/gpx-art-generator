# Phase 5: Configuration Prompts

## Step 15: Config File Support

```text
Implement YAML configuration support in cli/gpx_art/config.py:

1. Create Config class:
   - __init__(self, config_path: str | None = None)
   - load_config(self) -> dict
   - get_default_path(self) -> str
   - merge_with_defaults(self, config: dict) -> dict

2. Define default configuration structure:
   DEFAULT_CONFIG = {
       "defaults": {
           "thickness": "medium",
           "color": "#000000",
           "style": "solid",
           "markers": {
               "enabled": True,
               "unit": "miles"
           },
           "overlay": {
               "enabled": True,
               "fields": ["distance", "date"],
               "position": "top-left"
           },
           "export": {
               "formats": ["png"],
               "width": 36,
               "height": 12,
               "dpi": 300
           }
       }
   }

3. Implement YAML loading:
   - Use PyYAML for parsing
   - Handle missing file gracefully
   - Validate configuration structure
   - Merge with defaults for missing values

4. Add config file discovery:
   - Check ~/.gpx-art/config.yml
   - Check current directory ./gpx-art.yml
   - Allow override with environment variable

5. Create configuration validator:
   - Check valid values for enums
   - Validate numeric ranges
   - Ensure required fields exist

6. Create tests for config system:
   - Test default loading
   - Test file loading
   - Test merging behavior
   - Test validation errors

7. Update requirements.txt:
   - Add pyyaml>=6.0

Success criteria:
- Config files load and validate correctly
- Defaults merge properly with user config
- Configuration errors are clear
```

## Step 16: CLI Options Integration

```text
Integrate config file with CLI options in cli/gpx_art/main.py:

1. Update convert command to use config:
   - Load config at command start
   - Use config values as option defaults
   - Allow CLI options to override config

2. Implement option resolution order:
   1. CLI arguments (highest priority)
   2. Config file values
   3. Built-in defaults (lowest priority)

3. Add global config option:
   @click.option('--config', type=click.Path(exists=True), help='Path to config file')

4. Refactor command options:
   - Remove hardcoded defaults
   - Use config values for defaults
   - Update help text to indicate config override

5. Implement config inheritance:
   - Pass config through to visualizer
   - Pass config through to exporter
   - Allow per-command overrides

6. Create helper function:
   def get_effective_options(
       config: dict,
       cli_options: dict
   ) -> dict:
       """Merge CLI options with config, prioritizing CLI."""

7. Update documentation:
   - Document config file format
   - Explain option precedence
   - Provide example config files

8. Create tests:
   - Test config loading in commands
   - Test CLI override behavior
   - Test default behavior
   - Test multi-format generation via config

9. Add config generation command:
   @cli.command()
   @click.argument('output_file', type=click.Path())
   def init_config(output_file):
       """Generate a sample configuration file."""

Success criteria:
- Config file values are used as defaults
- CLI options override config values
- Multiple formats work via config
- Configuration is well-documented
```