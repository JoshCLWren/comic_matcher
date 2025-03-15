"""
Utility functions for comic matching
"""

import json
import logging
import re
from pathlib import Path
from typing import Any

import pandas as pd


def extract_year(date_str: str | int | None) -> int | None:
    """
    Extract year from various date formats

    Args:
        date_str: String or object containing a date

    Returns:
        Extracted year as int or None if not found
    """
    if not date_str:
        return None

    # Convert to string
    date_str = str(date_str)

    # Try to extract a 4-digit year with regex
    year_match = re.search(r"(19|20)\d{2}", date_str)
    if year_match:
        return int(year_match.group(0))

    # Try common date formats
    date_formats = [
        "%b %d %Y",  # Jan 01 2023
        "%Y-%m-%d",  # 2023-01-01
        "%m/%d/%Y",  # 01/01/2023
        "%Y",  # 2023
    ]

    from datetime import datetime

    for fmt in date_formats:
        try:
            date_obj = datetime.strptime(date_str.strip(), fmt)
            return date_obj.year
        except (ValueError, TypeError):
            continue

    return None


def normalize_publisher(publisher: str) -> str:
    """
    Normalize publisher names

    Args:
        publisher: Publisher name string

    Returns:
        Normalized publisher name
    """
    if not publisher or not isinstance(publisher, str):
        return ""

    publisher = publisher.lower().strip()

    # Map variations to canonical names
    publisher_map = {
        "marvel": ["marvel comics", "marvel comic", "marvel entertainment"],
        "dc": ["dc comics", "detective comics", "dc entertainment"],
        "image": ["image comics"],
        "dark horse": ["dark horse comics"],
        "idw": ["idw publishing"],
        "valiant": ["valiant entertainment", "valiant comics"],
        "boom": ["boom! studios", "boom studios"],
        "dynamite": ["dynamite entertainment"],
    }

    # Check if publisher matches any known variations
    for canonical, variations in publisher_map.items():
        if publisher in variations:
            return canonical

    # Check partial matches
    for canonical, variations in publisher_map.items():
        if canonical in publisher:
            return canonical

        for var in variations:
            if var in publisher:
                return canonical

    return publisher


def load_comics_from_csv(
    filepath: str, title_col: str = "title", issue_col: str = "issue"
) -> pd.DataFrame:
    """
    Load comics data from CSV file

    Args:
        filepath: Path to CSV file
        title_col: Column name for title
        issue_col: Column name for issue number

    Returns:
        DataFrame with comics data
    """
    try:
        df = pd.read_csv(filepath)

        # Verify required columns exist
        if title_col not in df.columns:
            raise ValueError(f"Title column '{title_col}' not found in CSV")

        # Convert issue column to string if it exists
        if issue_col in df.columns:
            df[issue_col] = df[issue_col].astype(str)

        return df
    except Exception as e:
        logging.error(f"Error loading comics from CSV: {e}")
        return pd.DataFrame()


def export_matches_to_csv(matches: pd.DataFrame, filepath: str) -> None:
    """
    Export matches to CSV file

    Args:
        matches: DataFrame with match results
        filepath: Path to save CSV file
    """
    try:
        matches.to_csv(filepath, index=False)
        logging.info(f"Exported {len(matches)} matches to {filepath}")
    except Exception as e:
        logging.error(f"Error exporting matches to CSV: {e}")


def find_duplicates(comics: pd.DataFrame) -> pd.DataFrame:
    """
    Find potential duplicates within a comic dataset

    Args:
        comics: DataFrame with comics

    Returns:
        DataFrame with duplicate groups
    """
    from recordlinkage import Compare
    from recordlinkage.index import Full

    # Self-comparison requires unique index
    if not comics.index.is_unique:
        comics = comics.reset_index(drop=True)

    # Create pairs for self-comparison (excluding identical records)
    indexer = Full()
    pairs = indexer.index(comics)

    # Remove pairs of identical indices
    pairs = pairs[pairs.get_level_values(0) < pairs.get_level_values(1)]

    # Create comparison object
    compare = Compare()

    # Add comparisons
    compare.string("title", "title", method="jarowinkler", threshold=0.85)
    if "issue" in comics.columns:
        compare.exact("issue", "issue")

    # Compute similarities
    features = compare.compute(pairs, comics)

    # Find duplicates (all features match)
    duplicates = features[features.sum(axis=1) == len(features.columns)]

    if duplicates.empty:
        return pd.DataFrame()

    # Create result dataframe
    dup_list = []
    for pair_idx, _ in duplicates.iterrows():
        idx1, idx2 = pair_idx
        dup_list.append(
            {
                "comic1_idx": idx1,
                "comic1_title": comics.loc[idx1, "title"],
                "comic1_issue": comics.loc[idx1, "issue"] if "issue" in comics.columns else "",
                "comic2_idx": idx2,
                "comic2_title": comics.loc[idx2, "title"],
                "comic2_issue": comics.loc[idx2, "issue"] if "issue" in comics.columns else "",
            }
        )

    return pd.DataFrame(dup_list)


def preprocess_comic_title(title: str) -> str:
    """
    Normalize and clean comic book title for better matching

    Args:
        title: Comic book title

    Returns:
        Preprocessed title
    """
    if not title or not isinstance(title, str):
        return ""

    # Convert to lowercase
    title = title.lower()

    # Remove year in parentheses
    title = re.sub(r"\(\d{4}\)", "", title)

    # Remove common issue indicators
    title = re.sub(r"#\d+", "", title)
    title = re.sub(r"issue\s+\d+", "", title)

    # Remove volume indicators
    title = re.sub(r"vol\.?\s*\d+", "", title)
    title = re.sub(r"volume\s*\d+", "", title)

    # Remove special character sequences
    title = re.sub(r"[^\w\s\-]", " ", title)

    # Normalize whitespace
    return re.sub(r"\s+", " ", title).strip()


def load_comics_from_json(filepath: str) -> list[dict[str, Any]]:
    """
    Load comics data from JSON file

    Args:
        filepath: Path to JSON file

    Returns:
        List of comic dictionaries
    """
    try:
        with Path(filepath).open() as f:
            data = json.load(f)

        # Handle different JSON structures
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            # First check for known keys
            if "results" in data:
                return data["results"]
            if "comics" in data:
                return data["comics"]
            # Then check if it's a flat dict of comics
            if all(isinstance(v, dict) for v in data.values()):
                return list(data.values())

        logging.warning(f"Unrecognized JSON structure in {filepath}")
        return []
    except Exception as e:
        logging.error(f"Error loading comics from JSON: {e}")
        return []


def generate_series_key(title: str) -> str:
    """
    Generate a canonical series key for blocking/grouping

    Args:
        title: Comic book title

    Returns:
        Series key for grouping similar titles
    """
    if not title or not isinstance(title, str):
        return ""

    # Clean and normalize
    title = title.lower().strip()
    title = re.sub(r"\([^)]*\)", "", title)  # Remove parenthetical content
    title = re.sub(r'[:.,"\'!?;]', "", title)  # Remove punctuation except hyphen

    # Handle special case for X-Men titles
    if re.search(r"x-[a-zA-Z]+", title):
        x_match = re.search(r"(x-[a-zA-Z]+)", title)
        if x_match:
            return x_match.group(1)

    # Extract first word as key if it's distinctive enough
    words = title.split()
    if not words:
        return ""

    # Skip common articles
    if words[0] in ["the", "a", "an"]:
        if len(words) > 1:
            return words[1]
        return ""

    # Use first word if it's meaningful
    if len(words[0]) >= 4:
        return words[0]

    # Otherwise use first two words
    if len(words) > 1:
        return f"{words[0]} {words[1]}"

    return words[0]
