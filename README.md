# Comic Matcher

Entity resolution and fuzzy matching for comic book titles.

## Overview

Comic Matcher is a specialized package for matching comic book titles across different formats and sources. 
It uses a combination of techniques from the record linkage toolkit with domain-specific optimizations for comic book naming conventions.

## Features

- Specialized comic book title parser
- Fuzzy matching with comic-specific optimizations
- Handling for series, volume, issue numbers
- Support for X-Men and other special series cases
- Configurable blocking and comparison rules
- Pre-computed fuzzy hash support
- Robust handling of sequels, team-ups, and special editions
- Smart filtering to avoid common bad matches

## Installation

```bash
# Install directly from PyPI
pip install comic-matcher

# Install from GitHub
pip install git+https://github.com/JoshCLWren/comic_matcher.git

# Install from the local directory (for development)
pip install -e .

# Or install required dependencies only
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from comic_matcher import ComicMatcher

# Initialize the matcher
matcher = ComicMatcher()

# Example data
source_comics = [
    {"title": "Uncanny X-Men", "issue": "142"},
    {"title": "Amazing Spider-Man", "issue": "300"}
]

target_comics = [
    {"title": "X-Men", "issue": "142"},
    {"title": "Spider-Man", "issue": "300"}
]

# Find matches
matches = matcher.match(source_comics, target_comics)

# Print results
print(f"Found {len(matches)} matches")
print(matches)
```

### Command-line Interface

```bash
# Match comics between two sources
comic-matcher match source_data.csv target_data.csv -o matches.csv

# Parse a comic title into components
comic-matcher parse "Uncanny X-Men (1963) #142"

# Get help
comic-matcher --help
```

### Finding a Single Best Match

```python
# Find best match for a single comic
comic = {"title": "Uncanny X-Men", "issue": "142"}
candidates = [
    {"title": "X-Men", "issue": "142"},
    {"title": "X-Men", "issue": "143"},
    {"title": "X-Force", "issue": "1"}
]

best_match = matcher.find_best_match(comic, candidates)
print(best_match)
```

### Parsing Comic Titles

```python
from comic_matcher import ComicTitleParser

parser = ComicTitleParser()
parsed = parser.parse("Uncanny X-Men (1963) #142")
print(parsed)
```

### Handling Special Cases

Comic Matcher includes specialized handling for various complex comic title patterns:

#### Sequels
```python
# Will match same sequel number but not different sequels
matcher.find_best_match({"title": "Civil War II", "issue": "1"}, 
                       [{"title": "Civil War", "issue": "1"}, 
                        {"title": "Civil War II", "issue": "1"}, 
                        {"title": "Civil War III", "issue": "1"}])
```

#### Team-ups
```python
# Properly handles team-up formats
matcher.find_best_match({"title": "Wolverine", "issue": "1"}, 
                       [{"title": "Wolverine/Doop", "issue": "1"}])  # Won't match

matcher.find_best_match({"title": "Wolverine/Doop", "issue": "1"}, 
                       [{"title": "Wolverine/Doop", "issue": "1"}])  # Will match
```

#### Subtitles and Special Editions
```python
# Handles subtitle differences
matcher.find_best_match({"title": "X-Men: Phoenix", "issue": "1"}, 
                       [{"title": "X-Men: Legacy", "issue": "1"}])  # Won't match

# Distinguishes special editions
matcher.find_best_match({"title": "X-Men", "issue": "1"}, 
                       [{"title": "X-Men Annual", "issue": "1"}])  # Won't match
```

## Developer Guide

### Setting Up Development Environment

The recommended way to set up your development environment is using the provided Makefile:

```bash
# Clone the repository
git clone https://github.com/JoshCLWren/comic_matcher.git
cd comic_matcher

# Create a Python 3.12 virtual environment with pyenv
brew install pyenv virtualenv
make venv

# Install dev dependencies
make dev
```

This will create a pyenv virtual environment called `comic_matcher_py312` using Python 3.12.

### Using the Makefile

The project includes a Makefile with common development tasks:

```bash
# Create a Python 3.12 virtual environment with pyenv
make venv

# Install development dependencies
make dev

# Run tests
make test

# Run tests with coverage report
make test-cov

# Run tests with detailed output
make test-verbose

# Run linting with Ruff
make lint

# Format code with Ruff
make format

# Clean up temporary files
make clean

# Build the package
make build

# Check test coverage
make coverage
```

This workflow ensures a clean, isolated development environment and consistent code quality.

### Linting with Ruff

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting. Ruff is a fast, modern Python linter and formatter written in Rust. It replaces multiple tools (flake8, black, isort, etc.) with a single, unified tool.

To lint your code:
```bash
make lint
```

To automatically format your code:
```bash
make format
```

### Running Examples

```bash
# Basic matching example
python examples/basic_matching.py

# Integration example
python examples/integration_example.py
```

## Testing

The project includes a comprehensive test suite using pytest. The tests cover all major components:

- `test_parser.py`: Tests for the comic title parsing functionality
- `test_matcher.py`: Tests for the core matcher functionality
- `test_utils.py`: Tests for utility functions
- `test_cli.py`: Tests for command-line interface
- `test_bad_matches*.py`: Specialized tests for known problematic match cases
- `test_sequel_detection.py`: Tests for sequel detection and handling

To run the tests:

```bash
# Run all tests
make test

# Run with coverage report
make test-cov

# Run tests with verbose output
make test-verbose

# Run specific test categories
pytest tests/test_bad_matches*.py -v
```

### Test Structure

The tests use pytest fixtures defined in `tests/conftest.py` to provide sample data and common setup. This makes the tests more readable and maintainable.

## Key Implementation Details

### Matcher Algorithm

The matching algorithm follows these steps:

1. Parse and normalize titles using the specialized comic title parser
2. Generate candidate pairs using recordlinkage blocking
3. Compute similarity scores for titles and issue numbers
4. Filter candidates based on domain-specific rules:
   - Different sequel numbers (e.g., "Civil War II" vs "Civil War III")
   - Team-up vs. solo titles (e.g., "Wolverine/Doop" vs "Wolverine")
   - Titles with different subtitles (e.g., "X-Men: Phoenix" vs "X-Men: Legacy")
   - Special edition differences (e.g., "X-Men Annual" vs "X-Men")
5. Calculate weighted similarity with adjusted weights:
   - Title: 35%
   - Issue number: 45%
   - Year: 10%
   - Special edition type: 10%
6. Apply threshold and return matches

### Parser Features

The parser extracts and normalizes:
- Main title
- Volume information
- Publication year
- Special identifiers (Annual, One-Shot, etc.)
- Subtitles
- Issue numbers

## CI/CD Workflows

This project uses GitHub Actions for continuous integration and delivery:

- **Python CI**: Runs tests and linting on multiple Python versions
- **Security Scan**: Checks for security vulnerabilities in code and dependencies
- **CodeQL Analysis**: Performs advanced code quality and security analysis
- **Dependency Review**: Reviews dependencies in pull requests for vulnerabilities
- **Dependency Update**: Automatically updates dependencies weekly
- **Build and Publish**: Builds and publishes releases to PyPI

### Status Badges

![Python CI](https://github.com/JoshCLWren/comic_matcher/actions/workflows/python-ci.yml/badge.svg)
![Security Scan](https://github.com/JoshCLWren/comic_matcher/actions/workflows/security-scan.yml/badge.svg)
![CodeQL](https://github.com/JoshCLWren/comic_matcher/actions/workflows/codeql-analysis.yml/badge.svg)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a virtual environment (`make venv`)
3. Install development dependencies (`make dev`)
4. Create your feature branch (`git checkout -b feature/amazing-feature`)
5. Make your changes and run tests (`make test`)
6. Format your code (`make format`)
7. Commit your changes (`git commit -m 'Add some amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

All pull requests are automatically tested using our CI workflows.

## License

MIT