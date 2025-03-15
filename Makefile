.PHONY: clean dev test lint lint-verbose fix format build coverage venv

venv:
	pyenv install 3.12 --skip-existing
	-pyenv uninstall -f comic_matcher_py312
	-pyenv virtualenv 3.12 comic_matcher_py312
	pyenv local comic_matcher_py312
	pip install --upgrade pip
	pip install --upgrade pip-tools

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

dev: venv
	pip install -e ".[dev]"
	pip install -r requirements.txt

test:
	pytest

test-cov:
	pytest --cov=comic_matcher tests/

test-verbose:
	pytest -vv

lint:
	ruff check comic_matcher
	ruff format --check comic_matcher

fix:
	ruff check --fix comic_matcher
	ruff format comic_matcher

fix-unsafe:
	ruff check --unsafe-fixes comic_matcher
	ruff format comic_matcher

lint-verbose:
	ruff check comic_matcher --verbose

format:
	ruff format comic_matcher tests

build:
	python setup.py sdist bdist_wheel

coverage:
	pytest --cov=comic_matcher --cov-report=html
