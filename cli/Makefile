.PHONY: install test lint format clean

install:
	pip install -e . && pip install -r requirements-dev.txt

test:
	pytest

lint:
	flake8 gpx_art
	mypy gpx_art

format:
	black .
	isort .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov build dist .pytest_cache

