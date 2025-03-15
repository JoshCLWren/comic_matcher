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

## Installation

```bash
# Install from the local directory
pip install -e .

# Or install required dependencies
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

## Developer Guide

### Setting Up Development Environment

The recommended way to set up your development environment is using the provided Makefile:

```bash
# Clone the repository
git clone https://github.com/yourusername/comic_matcher.git
cd comic_matcher

# Create a Python 3.12 virtual environment with pyenv
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

# Run linting
make lint

# Format code
make format

# Clean up temporary files
make clean

# Build the package
make build

# Check test coverage
make coverage
```

This workflow ensures a clean, isolated development environment and consistent code quality.

### Running Examples

```bash
# Basic matching example
python examples/basic_matching.py

# Integration example
python examples/integration_example.py
```

## Working with Your Existing Projects

### Integration with comic_pricer

```python
from comic_matcher import ComicMatcher
import pandas as pd

# Load data from your comic_pricer project
with open('my_reviews.json') as f:
    reviews = json.load(f)

# Convert to format for matcher
source_comics = []
for review_id, review in reviews.items():
    source_comics.append({
        "title": review.get("title", ""),
        "issue": review.get("issue", ""),
        "year": review.get("year", "")
    })

# Match against some target data
matches = matcher.match(source_comics, target_comics)
```

### Integration with web_pricer

```python
from comic_matcher import ComicMatcher
from constants import get_wishes_df

# Get wishlist data
wishlist_df = get_wishes_df()

# Initialize matcher with fuzzy hash from your project
matcher = ComicMatcher(fuzzy_hash_path="fuzzy_hash.json")

# Match against reading order
matches = matcher.match(wishlist_df, reading_order_df)
```

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

## License

MIT
