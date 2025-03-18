"""
Comprehensive test for the 'Marvel: Shadows and Light' vs 'Marvels' issue
"""

import pytest

from comic_matcher.matcher import ComicMatcher
from comic_matcher.parser import ComicTitleParser


def test_parser_behavior_for_marvel_titles():
    """Test how the parser handles various Marvel-related titles"""
    parser = ComicTitleParser()

    # Test different Marvel titles
    titles = [
        "Marvel: Shadows and Light 1",
        "Marvels 1",
        "Marvel Tales 1",
        "Marvel: The End 1",
        "Marvel Comics 1",
        "Marvel Team-Up 1",
    ]

    # Print parsed information for each title
    print("\nParser behavior for Marvel titles:")
    for title in titles:
        parsed = parser.parse(title)
        print(f"\nTitle: {title}")
        print(f"  Main title: '{parsed['main_title']}'")
        print(f"  Clean title: '{parsed['clean_title']}'")

    # Check specific behaviors
    marvel_shadows = parser.parse("Marvel: Shadows and Light 1")
    marvels = parser.parse("Marvels 1")

    # Ideally, we want the clean_title of these to be different enough
    # that they don't get incorrectly matched
    print(f"\nMarvel: Shadows and Light clean title: '{marvel_shadows['clean_title']}'")
    print(f"Marvels clean title: '{marvels['clean_title']}'")

    # The main titles should be different
    assert marvel_shadows["main_title"] != marvels["main_title"]


def test_matcher_behavior_for_marvel_titles():
    """Test how the matcher handles various Marvel-related titles"""
    matcher = ComicMatcher()

    # Test comparisons between different Marvel titles
    title_pairs = [
        ("Marvel: Shadows and Light 1", "Marvels 1"),
        ("Marvel: Shadows and Light 1", "Marvel: Shadows and Light 1"),
        ("Marvels 1", "Marvels 1"),
        ("Marvel: Shadows and Light 1", "Marvel Tales 1"),
        ("Marvel: The End 1", "Marvels 1"),
    ]

    # Print similarity for each pair
    print("\nMatcher similarity scores:")
    for title1, title2 in title_pairs:
        similarity = matcher._compare_titles(title1, title2)
        print(f"'{title1}' vs '{title2}': {similarity:.4f}")

        # For identical titles, similarity should be high
        if title1 == title2:
            assert similarity > 0.9

        # For "Marvel: Shadows and Light" vs "Marvels", similarity should be low
        if "Marvel: Shadows and Light" in title1 and "Marvels" in title2:
            assert similarity < 0.7
        if "Marvel: Shadows and Light" in title2 and "Marvels" in title1:
            assert similarity < 0.7


def test_find_best_match_for_marvel_shadows():
    """Test the find_best_match function with Marvel: Shadows and Light"""
    matcher = ComicMatcher()

    # Source comic: Marvel: Shadows and Light
    source_comic = {"title": "Marvel: Shadows and Light", "issue": "1"}

    # Different test scenarios for target comics
    target_scenarios = [
        # Scenario 1: Exact match available
        [
            {"title": "Marvel: Shadows and Light", "issue": "1"},
            {"title": "Marvels", "issue": "1"},
            {"title": "Marvel Tales", "issue": "1"},
        ],
        # Scenario 2: Only Marvels available
        [{"title": "Marvels", "issue": "1"}, {"title": "Marvel Fanfare", "issue": "1"}],
        # Scenario 3: Similar titles but no exact match
        [
            {"title": "Marvel: The End", "issue": "1"},
            {"title": "Marvels", "issue": "1"},
            {"title": "Marvel Comics", "issue": "1"},
        ],
    ]

    # Test each scenario
    print("\nFind best match results:")
    for i, target_comics in enumerate(target_scenarios):
        print(f"\nScenario {i + 1}:")
        print(f"Source comic: {source_comic}")
        print(f"Target comics: {target_comics}")

        result = matcher.find_best_match(source_comic, target_comics)

        if result:
            print(f"Matched with: {result['matched_comic']['title']} ({result['similarity']:.4f})")
            print(f"Individual scores: {result['scores']}")

            # If "Marvels" is in the list, it should not be the best match
            if any(comic["title"] == "Marvels" for comic in target_comics):
                assert result["matched_comic"]["title"] != "Marvels"
        else:
            print("No match found")

            # If exact match is in the list, we should find it
            if any(comic["title"] == "Marvel: Shadows and Light" for comic in target_comics):
                assert False, "Should have found an exact match"
