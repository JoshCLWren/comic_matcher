"""
Fix for the 'Marvel: Shadows and Light' vs 'Marvels' issue
"""

import pytest

from comic_matcher.matcher import ComicMatcher
from comic_matcher.parser import ComicTitleParser


def test_parser_handles_marvel_shadows_correctly():
    """Test that the parser handles 'Marvel: Shadows and Light' correctly"""
    parser = ComicTitleParser()

    # Parse the title
    result = parser.parse("Marvel: Shadows and Light 1")

    # The main title should be the full "Marvel: Shadows and Light", not just "Marvel"
    # Since "Marvel" is a publisher and not a series, "Shadows and Light" is not just a subtitle
    print(f"Parsed result: {result}")

    # Check that the parser didn't split incorrectly
    assert "marvel shadows and light 1" in result["clean_title"]

    # Test the actual matcher behavior
    matcher = ComicMatcher()
    title_sim = matcher._compare_titles("Marvel: Shadows and Light", "Marvels")

    # The similarity should be low
    print(f"Title similarity: {title_sim}")
    assert title_sim < 0.7  # Should be well below matching threshold
