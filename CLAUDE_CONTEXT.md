# Comic Matcher - Claude Context File

This file is intended as a quick reference for Claude to understand the Comic Matcher project structure and purpose. Reference this file in future conversations to quickly establish context.

## Project Overview

Comic Matcher is a specialized Python package for entity resolution and fuzzy matching of comic book titles across different formats and sources. It handles the complexities of comic book naming conventions, series, volumes, and issue numbers.

## Key Components

- **matcher.py**: Core matching functionality using recordlinkage with comic-specific optimizations
- **parser.py**: Specialized parser for comic book titles that extracts structured components
- **utils.py**: Utility functions for data loading, normalization, and preprocessing
- **cli.py**: Command-line interface for the matcher
- **team_up_matcher.py**: Specialized handling for team-up titles (e.g., "Wolverine/Doop")

## Special Handling

The system includes specialized handling for:
- X-Men and other X-series titles
- Common prefixes ("The", "Uncanny", "Amazing", etc.)
- Volume information and publication years
- Issue number normalization
- Publisher normalization
- Series sequels (e.g., "Civil War II", "X-Men Forever 2")
- Team-up titles (e.g., "Wolverine/Doop")
- Special editions (Annual, One-Shot, etc.)

## Development Status

As of March 2025:
- Core structure is established and fully implemented
- Parser implementation is complete
- Matcher implementation has been optimized with robust handling of special cases
- Test harness is in place with comprehensive tests including bad match scenarios
- CLI is functional and ready for production use

## Design Philosophy

1. Domain-specific matching optimizations for comics
2. Flexible input/output formats
3. Configurable matching rules
4. Performance considerations through caching and pre-computed fuzzy hashes
5. Robust handling of edge cases like sequels, special editions, and team-ups

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
5. Match reading orders to store inventories

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
6. Filtering candidate pairs based on domain-specific rules
7. Calculating weighted similarity and applying threshold

## Key Implementation Features

### Sequel Detection
The matcher now includes a `_extract_sequel_number` method that identifies sequels in titles, such as:
- Arabic numerals (e.g., "Civil War 2")
- Roman numerals (e.g., "Civil War II")

This allows the matcher to avoid matching different entries in a series (e.g., "Civil War" vs "Civil War II").

### Team-Up Title Handling
The new `team_up_matcher.py` module provides specialized handling for team-up titles with patterns like:
- Slash format (e.g., "Wolverine/Doop")
- Ampersand format (e.g., "Batman & Robin")
- "And" format (e.g., "Wolverine and Jubilee")
- Versus format (e.g., "Batman vs Superman")

### Enhanced Parser
The parser now:
- Preserves special identifiers in clean titles
- Handles subtitle formats consistently
- Provides better normalization for complex titles

### Matching Algorithm Improvements
The matching algorithm now:
- Uses a more conservative candidate filtering approach
- Adjusts weights to prioritize issue number matches (45%)
- Adds special edition type comparison
- Includes post-processing to filter out problematic matches

## What's Working Well

- The parser component robustly extracts structured data from comic titles
- Test coverage is comprehensive and includes specific test cases for known bad matches
- The domain-specific approach handles industry-specific naming conventions well
- Flexible data ingestion from different sources (CSV, JSON) with format detection
- Good separation of concerns between components
- Enhanced handling of special cases like sequels, team-ups, and special editions

## Recently Improved Areas

1. **Title Comparison Logic**: The title comparison now properly handles:
   - Sequel detection (e.g., "Civil War II" vs "Civil War III")
   - Team-up formats (e.g., "Wolverine/Doop" vs "Wolverine")
   - Subtitles after colons (e.g., "X-Men: Phoenix" vs "X-Men: Legacy")
   - Special editions (e.g., "X-Men Annual" vs "X-Men")

2. **Match Filtering**: The matcher now filters out problematic matches based on:
   - Issue number mismatches
   - Sequel mismatches
   - Different subtitles
   - Special edition differences

3. **Parser Improvements**: The parser now:
   - Preserves special identifiers in clean titles
   - Consistently handles series versions and subtitles
   - Better extracts and normalizes issue numbers

4. **Comprehensive Test Suite**: The test suite now includes:
   - Specific tests for bad matches identified in real data
   - Edge case tests for special formats
   - Integration tests simulating real-world scenarios