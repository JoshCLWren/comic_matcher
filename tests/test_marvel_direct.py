"""
Direct test for the Marvel: Shadows and Light vs Marvels issue with verbose logging
"""

import pytest

from comic_matcher.matcher import ComicMatcher


def test_marvel_shadows_vs_marvels_direct():
    """
    Test specifically to diagnose and fix the "Marvel: Shadows and Light" vs "Marvels" issue
    """
    # Initialize matcher
    matcher = ComicMatcher()

    # Create test data
    source_comic = {"title": "Marvel: Shadows and Light", "issue": "1"}
    candidates = [
        {"title": "Marvels", "issue": "1"},
        {"title": "Marvel Tales", "issue": "1"},
        {"title": "Marvel: Shadows and Light", "issue": "1"},
    ]

    # Print comparison details
    print("\nTitle comparison scores:")
    for candidate in candidates:
        title_sim = matcher._compare_titles(source_comic["title"], candidate["title"])
        print(f"'{source_comic['title']}' vs '{candidate['title']}': {title_sim:.4f}")

    # Directly test core _compare_titles function
    marvels_sim = matcher._compare_titles("Marvel: Shadows and Light", "Marvels")
    assert marvels_sim < 0.6, f"Expected similarity < 0.6, got {marvels_sim:.4f}"
    print(f"Title similarity check passed: {marvels_sim:.4f} < 0.6")

    # Test complete find_best_match function
    result = matcher.find_best_match(source_comic, candidates)

    # Output detailed results
    print("\nfind_best_match result:")
    if result:
        print(f"Matched with: '{result['matched_comic']['title']}'")
        print(f"Similarity: {result['similarity']:.4f}")
        print(f"Score details: {result['scores']}")

        # Assert it matched with the right title
        assert result["matched_comic"]["title"] == "Marvel: Shadows and Light", (
            f"Expected 'Marvel: Shadows and Light' but got '{result['matched_comic']['title']}'"
        )
        print("Match assertion passed!")
    else:
        print("No match found")
        assert False, "Expected to find a match"

    # Test with just Marvels as a candidate
    print("\nTesting with only Marvels as candidate:")
    marvels_only = [{"title": "Marvels", "issue": "1"}]
    marvels_result = matcher.find_best_match(source_comic, marvels_only)

    if marvels_result:
        print(f"Matched with: '{marvels_result['matched_comic']['title']}'")
        print(f"Similarity: {marvels_result['similarity']:.4f}")

        # This should either be None or have similarity < 0.5
        if marvels_result["similarity"] >= 0.5:
            assert False, (
                f"Expected no match or similarity < 0.5, got {marvels_result['similarity']:.4f}"
            )
        else:
            print("Low similarity - would be rejected in practice")
    else:
        print("No match found - correct behavior")

    print("\nAll tests passed successfully!")
