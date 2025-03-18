"""
Test that the matcher correctly handles structural differences in titles
"""

import pytest

from comic_matcher.matcher import ComicMatcher


def test_structural_title_differences():
    """Test that titles with different structures aren't incorrectly matched"""
    matcher = ComicMatcher()

    # Test cases where we want to ensure low similarity
    should_not_match = [
        # Format: (title1, title2, max_expected_similarity)
        ("Marvel: Shadows and Light", "Marvels", 0.4),
        ("Image: United", "Images", 0.4),
    ]

    for title1, title2, max_sim in should_not_match:
        similarity = matcher._compare_titles(title1, title2)
        assert similarity <= max_sim, (
            f"'{title1}' and '{title2}' had similarity {similarity}, expected <= {max_sim}"
        )
        print(f"'{title1}' vs '{title2}': {similarity:.2f} ✓")

    # Test cases that should still match despite structural differences
    should_match = [
        # These have different structures but are legitimately the same series
        (
            "X-Men: Gold",
            "Uncanny X-Men",
            0.6,
        ),  # Different structure but same core series
        (
            "Avengers: Disassembled",
            "Avengers (1998)",
            0.6,
        ),  # Different structure but same series
        (
            "Fantastic Four: The End",
            "Fantastic Four",
            0.6,
        ),  # Main series and limited series
    ]

    for title1, title2, min_sim in should_match:
        similarity = matcher._compare_titles(title1, title2)
        assert similarity >= min_sim, (
            f"'{title1}' and '{title2}' had similarity {similarity}, expected >= {min_sim}"
        )
        print(f"'{title1}' vs '{title2}': {similarity:.2f} ✓")


def test_find_best_match_with_structural_differences():
    """Test that find_best_match handles structural differences correctly"""
    matcher = ComicMatcher()

    # Test cases
    test_cases = [
        # Format: source title, candidates list, expected match (or None)
        {
            "source": {"title": "Marvel: Shadows and Light", "issue": "1"},
            "candidates": [
                {"title": "Marvel Comics", "issue": "1"},
                {"title": "Marvels", "issue": "1"},
                {"title": "Marvel: Shadows and Light", "issue": "1"},
            ],
            "expected": "Marvel: Shadows and Light",
        },
        {
            "source": {"title": "Marvel: Shadows and Light", "issue": "1"},
            "candidates": [
                {"title": "Marvel Comics", "issue": "1"},
                {"title": "Marvels", "issue": "1"},
            ],
            "expected": None,  # Should not match either candidate
        },
        {
            "source": {"title": "DC: New Frontier", "issue": "1"},
            "candidates": [
                {"title": "DC", "issue": "1"},
                {"title": "DC Comics", "issue": "1"},
                {"title": "DC Universe", "issue": "1"},
                {"title": "DC: New Frontier", "issue": "1"},
            ],
            "expected": "DC: New Frontier",
        },
    ]

    for case in test_cases:
        source = case["source"]
        candidates = case["candidates"]
        expected = case["expected"]

        result = matcher.find_best_match(source, candidates)

        if expected is None:
            assert result is None or result["similarity"] < 0.5, (
                f"Expected no match for {source['title']}"
            )
            print(f"'{source['title']}' correctly didn't match with any candidates ✓")
        else:
            assert result is not None, f"Expected to find a match for {source['title']}"
            assert result["matched_comic"]["title"] == expected, (
                f"Expected '{expected}' but got '{result['matched_comic']['title']}'"
            )
            print(
                f"'{source['title']}' correctly matched with '{result['matched_comic']['title']}' ✓"
            )


def test_colon_strings():
    """
    Ensure: X-Men: Liberators 3
    does not match: Uncanny X-Men 3
    """
    matcher = ComicMatcher()
    source = {"title": "X-Men: Liberators", "issue": "3"}
    candidates = [{"title": "Uncanny X-Men", "issue": "3"}]
    result = matcher.find_best_match(source, candidates)
    assert not result


def test_colon_strings():
    """
    Ensure Astonishing X-Men Xenogenesis 1	Astonishing X-Men 1
    does not match: Astonishing X-Men 1
    """
    matcher = ComicMatcher()
    source = {"title": "Astonishing X-Men", "issue": "1"}
    candidates = [{"title": "Astonishing X-Men Xenogenesis", "issue": "1"}]
    result = matcher.find_best_match(source, candidates)
    assert not result
