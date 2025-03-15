.PHONY: clean dev test lint format build coverage venv

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

lint:
	flake8 comic_matcher
	isort --check-only --profile black comic_matcher
	black --check comic_matcher

format:
	isort --profile black comic_matcher
	black comic_matcher

build:
	python setup.py sdist bdist_wheel

coverage:
	pytest --cov=comic_matcher --cov-report=html
