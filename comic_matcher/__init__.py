"""
Comic Matcher: Entity resolution for comic book title matching
"""

from .matcher import ComicMatcher
from .parser import ComicTitleParser
from .utils import (
    export_matches_to_csv,
    extract_year,
    find_duplicates,
    generate_series_key,
    load_comics_from_csv,
    load_comics_from_json,
    normalize_publisher,
    preprocess_comic_title,
)

__all__ = [
    "ComicMatcher",
    "ComicTitleParser",
    "export_matches_to_csv",
    "extract_year",
    "find_duplicates",
    "generate_series_key",
    "load_comics_from_csv",
    "load_comics_from_json",
    "normalize_publisher",
    "preprocess_comic_title",
]

__version__ = "0.1.0"
