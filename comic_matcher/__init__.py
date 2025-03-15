"""
Comic Matcher: Entity resolution for comic book title matching
"""

from .matcher import ComicMatcher
from .parser import ComicTitleParser
from .utils import (
    extract_year,
    normalize_publisher,
    load_comics_from_csv,
    load_comics_from_json,
    export_matches_to_csv,
    find_duplicates,
    preprocess_comic_title,
    generate_series_key
)

__version__ = "0.1.0"
