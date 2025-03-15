# Comic Matcher - Claude Context File

This file is intended as a quick reference for Claude to understand the Comic Matcher project structure and purpose. Reference this file in future conversations to quickly establish context.

## Project Overview

Comic Matcher is a specialized Python package for entity resolution and fuzzy matching of comic book titles across different formats and sources. It handles the complexities of comic book naming conventions, series, volumes, and issue numbers.

## Key Components

- **matcher.py**: Core matching functionality using recordlinkage with comic-specific optimizations
- **parser.py**: Specialized parser for comic book titles that extracts structured components
- **utils.py**: Utility functions for data loading, normalization, and preprocessing
- **cli.py**: Command-line interface for the matcher

## Special Handling

The system includes specialized handling for:
- X-Men and other X-series titles
- Common prefixes ("The", "Uncanny", "Amazing", etc.)
- Volume information and publication years
- Issue number normalization
- Publisher normalization

## Development Status

As of March 2025:
- Core structure is established
- Parser implementation is complete
- Matcher implementation has placeholder/mock code that needs to be fully implemented
- Test harness is in place with comprehensive tests
- CLI is functional but depends on complete matcher implementation

## Design Philosophy

1. Domain-specific matching optimizations for comics
2. Flexible input/output formats
3. Configurable matching rules
4. Performance considerations through caching and pre-computed fuzzy hashes

## Next Steps

1. Complete the actual matcher implementation using recordlinkage
2. Add benchmarking
3. Improve configuration options
4. Add web API capabilities
5. Enhance issue matching for special cases

## Project Dependencies

- pandas: Data handling
- recordlinkage: Core entity resolution
- jellyfish: String similarity functions
- Levenshtein/rapidfuzz: Fast fuzzy matching
- pytest: Testing framework
- ruff: Linting and formatting

## Use Cases

1. Match personal comic collection against price guides
2. Normalize comic titles across different databases
3. Find duplicates within a collection
4. Integrate with other comic management tools
