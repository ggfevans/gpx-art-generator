import pytest
from click.testing import CliRunner

from route_to_art.main import cli


@pytest.fixture
def runner():
    """Fixture providing a CLI test runner."""
    return CliRunner()


def test_cli_exists():
    """Test that cli function exists."""
    assert callable(cli)


def test_version_option(runner):
    """Test that --version option works."""
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output.lower()


def test_help_option(runner):
    """Test that --help option shows all three commands."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    
    # Check that all three commands are listed in the help output
    assert "convert" in result.output
    assert "validate" in result.output
    assert "info" in result.output


def test_convert_command(runner, tmp_path):
    """Test that convert command shows not implemented message."""
    # Create a test file
    test_file = tmp_path / "test.gpx"
    test_file.write_text("<gpx></gpx>")
    
    result = runner.invoke(cli, ["convert", str(test_file)])
    assert result.exit_code == 0
    assert "not implemented" in result.output.lower()


def test_validate_command(runner, tmp_path):
    """Test that validate command shows not implemented message."""
    # Create a test file
    test_file = tmp_path / "test.gpx"
    test_file.write_text("<gpx></gpx>")
    
    result = runner.invoke(cli, ["validate", str(test_file)])
    assert result.exit_code == 0
    assert "not implemented" in result.output.lower()


def test_info_command(runner, tmp_path):
    """Test that info command shows not implemented message."""
    # Create a test file
    test_file = tmp_path / "test.gpx"
    test_file.write_text("<gpx></gpx>")
    
    result = runner.invoke(cli, ["info", str(test_file)])
    assert result.exit_code == 0
    assert "not implemented" in result.output.lower()

