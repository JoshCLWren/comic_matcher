"""
Test that Wolverine: Evilution is not matched with Wolverine And Jubilee
"""

import pytest

from comic_matcher.matcher import ComicMatcher


def test_wolverine_titles_not_matched():
    """
    Test that "Wolverine: Evilution" doesn't incorrectly match with "Wolverine And Jubilee"
    """
    # Initialize matcher
    matcher = ComicMatcher()

    # Create source comic (what we're trying to match)
    source_comic = {"title": "Wolverine: Evilution", "issue": "1"}

    # Create potential target comics including "Wolverine And Jubilee" which shouldn't match
    target_comics = [
        {"title": "Wolverine And Jubilee", "issue": "1"},
        {"title": "Wolverine", "issue": "1"},
        {"title": "Wolverine: Days of Future Past", "issue": "1"},
    ]

    # Find the best match
    best_match = matcher.find_best_match(source_comic, target_comics)

    # Shouldn't match with "Wolverine And Jubilee"
    if best_match:
        assert best_match["matched_comic"]["title"] != "Wolverine And Jubilee"

    # Compare similarity scores directly
    wolverine_evilution_sim = matcher._compare_titles(
        "Wolverine: Evilution", "Wolverine: Evilution"
    )
    wolverine_jubilee_sim = matcher._compare_titles("Wolverine: Evilution", "Wolverine And Jubilee")

    print(f"Similarity with 'Wolverine: Evilution': {wolverine_evilution_sim}")
    print(f"Similarity with 'Wolverine And Jubilee': {wolverine_jubilee_sim}")

    # Should have much higher similarity with correct match
    assert wolverine_jubilee_sim < 0.5  # Below matching threshold
