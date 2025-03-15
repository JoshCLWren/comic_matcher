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
- recordlinkage (v0.15+): Core entity resolution
  - Note: Recordlinkage API has specific import paths:
    - Main comparing functionality is in `recordlinkage.Compare`
    - Comparison methods are in `recordlinkage.compare` (e.g., `String`, `Exact`, `Numeric`)
    - Do NOT use `recordlinkage.comparing` which is deprecated/removed
- jellyfish: String similarity functions
- Levenshtein/rapidfuzz: Fast fuzzy matching
- pytest: Testing framework
- ruff: Linting and formatting

## Use Cases

1. Match personal comic collection against price guides
2. Normalize comic titles across different databases
3. Find duplicates within a collection
4. Integrate with other comic management tools

## Recordlinkage API Usage

The matcher.py file uses recordlinkage as follows:

1. Creating an indexer: `indexer = recordlinkage.Index()`
2. Generating candidate pairs: `candidate_pairs = indexer.index(df_source, df_target)`
3. Creating a compare object: `compare = recordlinkage.Compare()`
4. Adding comparison methods:
   ```python
   compare.string("title", "title", method="jarowinkler", label="title_sim")
   compare.exact("parsed_year", "parsed_year", label="year_sim")
   ```
5. Computing similarity scores: `feature_vectors = compare.compute(candidate_pairs, df_source, df_target)`

Refer to the recordlinkage documentation for more details on these methods.

## What's Working Well

- The parser component is robust and effectively extracts structured data from comic titles
- Test coverage is comprehensive and catches edge cases
- The domain-specific approach to comic matching handles industry-specific naming conventions well
- Flexible data ingestion from different sources (CSV, JSON) with format detection
- Good separation of concerns between components

## Areas Needing Improvement

1. **Normalization Consistency**: Decide on a consistent approach to title normalization across the codebase
   - Currently the parser normalizes titles differently than the matcher and utilities
   - Example: "Uncanny X-Men" sometimes becomes "X-Men" and sometimes remains unchanged

2. **Dependency Management**: Better handling of external package dependencies
   - The recordlinkage import issue showed vulnerability to API changes
   - Consider adding fallbacks or more robust error handling for critical dependencies

3. **Series Key Generation**: Current approach to generating series keys needs refinement
   - Should preserve multi-word titles rather than truncating to first word
   - Needs more robust handling of variant titles and special editions

4. **Test Resilience**: Some tests make rigid assumptions about implementation details
   - Tests should focus on behavior and functionality rather than specific implementation choices
   - Make more resilient to refactoring and algorithm changes

5. **Complete Core Implementation**: The matcher implementation still relies on placeholder code
   - The recordlinkage integration needs to be fully implemented
   - The actual matching algorithm needs optimization for comic-specific matching
