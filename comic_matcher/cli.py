"""
Command-line interface for Comic Matcher
"""

import argparse
import logging
from pathlib import Path
from typing import Any

import pandas as pd

from .matcher import ComicMatcher
from .parser import ComicTitleParser
from .utils import export_matches_to_csv, load_comics_from_csv, load_comics_from_json


def setup_logging(level: str = "INFO") -> None:
    """
    Set up logging configuration

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def load_data(file_path: str) -> list[dict[str, Any]] | pd.DataFrame:
    """
    Load comic data from file based on extension

    Args:
        file_path: Path to data file (CSV or JSON)

    Returns:
        List of comics or DataFrame
    """
    if not Path(file_path).exists():
        logging.error(f"File not found: {file_path}")
        return []

    ext = Path(file_path).suffix.lower()

    if ext == ".csv":
        return load_comics_from_csv(file_path)
    if ext == ".json":
        return load_comics_from_json(file_path)
    logging.error(f"Unsupported file format: {ext}")
    return []


def run_matcher(args: argparse.Namespace) -> None:
    """
    Run the matcher with command-line arguments

    Args:
        args: Command-line arguments
    """
    # Load source and target data
    source_data = load_data(args.source)
    target_data = load_data(args.target)

    if not source_data or not target_data:
        logging.error("Failed to load source or target data")
        return

    # Log data summary
    logging.info(f"Loaded {len(source_data)} source comics and {len(target_data)} target comics")

    # Initialize matcher
    matcher = ComicMatcher(fuzzy_hash_path=args.fuzzy_hash if args.fuzzy_hash else None)

    # Run matching
    matches = matcher.match(
        source_data, target_data, threshold=args.threshold, indexer_method=args.indexer
    )

    # Print results summary
    if not matches.empty:
        print(f"Found {len(matches)} matches")

        # Export results
        if args.output:
            export_matches_to_csv(matches, args.output)
            print(f"Saved matches to {args.output}")

        # Print sample
        if args.verbose:
            print("\nSample matches:")
            for _, match in matches.head(5).iterrows():
                get_title_match = match.get("source_title", "Unknown")
                get_source_issue_match = match.get("source_issue", "N/A")
                get_target_title_match = match.get("target_title", "Unknown")
                get_target_issue_match = match.get("target_issue", "N/A")
                print(
                    f"  {get_title_match} #{get_source_issue_match} = "
                    f"{get_target_title_match} #{get_target_issue_match} "
                    f"(similarity: {match['similarity']:.2f})"
                )
    else:
        print("No matches found")


def parse_title(args: argparse.Namespace) -> None:
    """
    Parse a comic title and show components

    Args:
        args: Command-line arguments
    """
    parser = ComicTitleParser()
    components = parser.parse(args.title)

    print(f"Title: {args.title}")
    print("\nParsed components:")
    for key, value in components.items():
        print(f"  {key}: {value}")


def main() -> None:
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(description="Comic Matcher CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Match command
    match_parser = subparsers.add_parser("match", help="Match comics between two sources")
    match_parser.add_argument("source", help="Source comics file (CSV or JSON)")
    match_parser.add_argument("target", help="Target comics file (CSV or JSON)")
    match_parser.add_argument("-o", "--output", help="Output CSV file for matches")
    match_parser.add_argument(
        "-t", "--threshold", type=float, default=0.63, help="Similarity threshold (0-1)"
    )
    match_parser.add_argument(
        "-i",
        "--indexer",
        default="block",
        choices=["block", "sortedneighbourhood", "fullindex"],
        help="Indexing method for matching",
    )
    match_parser.add_argument("-f", "--fuzzy-hash", help="Path to fuzzy hash JSON file")
    match_parser.add_argument("-v", "--verbose", action="store_true", help="Print verbose output")

    # Parse command
    parse_parser = subparsers.add_parser("parse", help="Parse a comic title")
    parse_parser.add_argument("title", help="Comic title to parse")

    # Common options
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
    )

    args = parser.parse_args()

    # Set up logging
    setup_logging(args.log_level)

    # Run the appropriate command
    if args.command == "match":
        run_matcher(args)
    elif args.command == "parse":
        parse_title(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
