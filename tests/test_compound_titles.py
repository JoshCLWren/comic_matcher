"""
Test handling of compound titles with colons and different formats
"""

import pytest

from comic_matcher.matcher import ComicMatcher
from comic_matcher.parser import ComicTitleParser


def test_compound_title_parsing():
    """Test that compound titles with colons are parsed correctly"""
    parser = ComicTitleParser()

    # Test various compound titles
    test_cases = [
        # Title with publisher-like prefix
        (
            "Marvel: Shadows and Light",
            "marvel shadows and light",
        ),
    ]

    for title, expected_main in test_cases:
        result = parser.parse(title)
        assert result["main_title"] == expected_main


def test_matcher_with_compound_titles():
    """Test that matcher handles compound titles appropriately"""
    matcher = ComicMatcher()

    # Test various title combinations
    test_cases = [
        # These should NOT match
        ("Marvel: Shadows and Light", "Marvels", False),
        ("DC: New Frontier", "DC Comics", False),
        ("Image: First Lights", "Images", False),
        # These SHOULD match
        ("Marvel: Shadows and Light", "Marvel: Shadows & Light", True),
        ("Batman: The Long Halloween", "Batman: Long Halloween", True),
    ]

    for title1, title2, should_match in test_cases:
        similarity = matcher._compare_titles(title1, title2)
        if should_match:
            assert similarity >= 0.63, f"'{title1}' should match '{title2}' but got {similarity}"
        else:
            assert similarity < 0.63, f"'{title1}' should NOT match '{title2}' but got {similarity}"


def test_find_best_match_with_compound_titles():
    """Test find_best_match with various compound title scenarios"""
    matcher = ComicMatcher()

    # Test various source comics with compound titles
    test_cases = [
        # Marvel: Shadows and Light vs. various titles
        {
            "source": {"title": "Marvel: Shadows and Light", "issue": "1"},
            "targets": [
                {"title": "Marvels", "issue": "1"},
                {"title": "Marvel Tales", "issue": "1"},
                {"title": "Marvel: Shadows and Light", "issue": "1"},
            ],
            "expected_match": "Marvel: Shadows and Light",
        },
        # DC: New Frontier vs. various titles
        {
            "source": {"title": "DC: New Frontier", "issue": "1"},
            "targets": [
                {"title": "DC Comics Presents", "issue": "1"},
                {"title": "DC: New Frontier", "issue": "1"},
                {"title": "New Frontier", "issue": "1"},
            ],
            "expected_match": "DC: New Frontier",
        },
        # Batman: Year One vs. various titles
        {
            "source": {"title": "Batman: Year One", "issue": "1"},
            "targets": [
                {"title": "Batman", "issue": "404"},  # Year One starts at #404
                {"title": "Detective Comics", "issue": "1"},
                {"title": "Batman: Year One", "issue": "1"},
            ],
            "expected_match": "Batman: Year One",
        },
    ]

    for case in test_cases:
        result = matcher.find_best_match(case["source"], case["targets"])
        assert result is not None, f"Failed to find any match for {case['source']['title']}"
        assert result["matched_comic"]["title"] == case["expected_match"], (
            f"Expected {case['expected_match']} but got {result['matched_comic']['title']}"
        )
