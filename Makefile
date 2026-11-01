.PHONY: install dev test lint serve clean run

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

serve:
	8gen serve

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
