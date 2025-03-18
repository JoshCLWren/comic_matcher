"""
Test to ensure "Marvel: Shadows and Light 1" doesn't match with "Marvels" #1
"""

import pytest

from comic_matcher.matcher import ComicMatcher


def test_marvel_shadows_not_matching_marvels():
    """
    Test that "Marvel: Shadows and Light 1" doesn't incorrectly match with "Marvels" #1

    This test ensures that the matcher doesn't confuse "Marvel" (publisher name)
    with "Marvels" (series title) when parsing "Marvel: Shadows and Light".
    """
    # Initialize matcher
    matcher = ComicMatcher()

    # Create source comic (what we're trying to match)
    source_comic = {"title": "Marvel: Shadows and Light", "issue": "1"}

    # Create potential target comics including "Marvels" which shouldn't match
    target_comics = [
        {"title": "Marvels", "issue": "1"},
        {"title": "Marvel Comics", "issue": "1"},
        {"title": "Marvel Tales", "issue": "1"},
        # Include an actual match for comparison
        {"title": "Marvel: Shadows and Light", "issue": "1"},
    ]

    # Find the best match
    best_match = matcher.find_best_match(source_comic, target_comics)

    # Verify there's a match (should match with "Marvel: Shadows and Light")
    assert best_match is not None

    # The matched comic should be "Marvel: Shadows and Light", not "Marvels"
    assert best_match["matched_comic"]["title"] == "Marvel: Shadows and Light"
    assert best_match["matched_comic"]["title"] != "Marvels"

    # Now test directly with just "Marvels" to ensure it's not a match
    marvels_comic = [{"title": "Marvels", "issue": "1"}]
    marvels_match = matcher.find_best_match(source_comic, marvels_comic)

    # Should either return None or have a low similarity score below matching threshold
    if marvels_match is not None:
        assert marvels_match["similarity"] < 0.5  # Below the threshold for a good match
