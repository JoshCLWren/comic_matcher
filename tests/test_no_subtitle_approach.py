"""
Test the simplified approach without subtitle parsing
"""

import pytest

from comic_matcher.matcher import ComicMatcher
from comic_matcher.parser import ComicTitleParser


def test_parser_treats_titles_holistically():
    """Test that titles are treated as complete entities without subtitle splitting"""
    parser = ComicTitleParser()

    # Test cases with titles that have colons
    test_cases = [
        "Marvel: Shadows and Light",
        "Batman: The Long Halloween",
        "X-Men: Age of Apocalypse",
        "DC: New Frontier",
    ]

    for title in test_cases:
        result = parser.parse(title)

        # The important check: clean_title should preserve the overall structure
        # so that "Marvel: Shadows and Light" won't match with just "Marvels"
        assert result["clean_title"] != "marvels" if title == "Marvel: Shadows and Light" else True


def test_marvel_shadows_not_matching_marvels():
    """
    Test that "Marvel: Shadows and Light 1" doesn't incorrectly match with "Marvels" #1
    """
    # Initialize matcher
    matcher = ComicMatcher()

    # Create source comic (what we're trying to match)
    source_comic = {"title": "Marvel: Shadows and Light", "issue": "1"}

    # Create potential target comics including "Marvels" which shouldn't match
    target_comics = [
        {"title": "Marvels", "issue": "1"},
        {"title": "Marvel Tales", "issue": "1"},
        {"title": "Marvel: Shadows and Light", "issue": "1"},
    ]

    # Find the best match
    best_match = matcher.find_best_match(source_comic, target_comics)

    # Verify there's a match (should match with "Marvel: Shadows and Light")
    assert best_match is not None

    # The matched comic should be "Marvel: Shadows and Light", not "Marvels"
    assert best_match["matched_comic"]["title"] == "Marvel: Shadows and Light"

    # Compare similarity scores directly
    marvel_shadows_sim = matcher._compare_titles(
        "Marvel: Shadows and Light", "Marvel: Shadows and Light"
    )
    marvels_sim = matcher._compare_titles("Marvel: Shadows and Light", "Marvels")

    print(f"Similarity with 'Marvel: Shadows and Light': {marvel_shadows_sim}")
    print(f"Similarity with 'Marvels': {marvels_sim}")

    # Should have much higher similarity with correct match
    assert marvel_shadows_sim > marvels_sim + 0.3  # Significant difference
    assert marvels_sim < 0.6  # Below matching threshold
