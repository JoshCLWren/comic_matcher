"""
Simple tests for comic book title matching functionality
"""

import pytest

from comic_matcher.matcher import ComicMatcher

# Test cases for specific title matches
KEY_MATCH_CASES = [
    # Format: (source_title, target_title, expected_match)
    ("X-Men: Kitty Pryde - Shadow & Flame", "X-Men: Die By The Sword", False),
    ("New X-Men: Academy X", "New X-Men", False),
    ("DC Versus Marvel/Marvel Versus DC", "DC Versus Marvel", True),
    ("Marvel Versus DC/DC Versus Marvel", "Marvel Versus DC", True),
    # This one should still be rejected (completely different titles)
    ("Marvel Universe Vs Wolverine", "Marvel Versus DC", False),
]


@pytest.mark.parametrize("source_title,target_title,expected", KEY_MATCH_CASES)
def test_title_matching(source_title, target_title, expected):
    """Test specific title matching cases to identify where the matcher needs improvement"""
    matcher = ComicMatcher()

    # Create simple test data with just the titles we want to test
    source_data = [{"title": source_title, "issue": "1"}]
    target_data = [{"title": target_title, "issue": "1"}]
    # Run matching
    results = matcher.match(source_data, target_data, threshold=0.5)

    # Check if match exists as expected
    has_match = not results.empty

    if expected:
        assert has_match, f"Failed to match '{source_title}' with '{target_title}'"
    else:
        assert not has_match, f"Should NOT match '{source_title}' with '{target_title}'"


def test_title_comparison_directly():
    """
    Test the _compare_titles method directly to better understand
    where the title comparison logic is failing
    """
    matcher = ComicMatcher()

    for source_title, target_title, expected in KEY_MATCH_CASES:
        similarity = matcher._compare_titles(source_title, target_title)

        if expected:
            assert similarity >= 0.7, (
                f"Similarity too low: {similarity} for '{source_title}' and '{target_title}'"
            )
        else:
            assert similarity < 0.7, (
                f"Similarity too high: {similarity} for '{source_title}' and '{target_title}'"
            )


def test_batch_matching():
    """
    Test batch matching with all the KEY_MATCH_CASES at once to see
    which pairs get matched and which don't
    """
    matcher = ComicMatcher()

    # Create source and target dataframes from the test cases
    source_data = [{"title": source, "issue": "1"} for source, _, _ in KEY_MATCH_CASES]
    target_data = [{"title": target, "issue": "1"} for _, target, _ in KEY_MATCH_CASES]

    # Run the matcher
    results = matcher.match(source_data, target_data, threshold=0.5)

    # Print results for analysis
    print("\nMatched pairs:")
    matched_pairs = set()
    for _, row in results.iterrows():
        source_title = row["source_title"]
        target_title = row["target_title"]
        similarity = row["similarity"]
        print(f"  {source_title!r} -> {target_title!r} (similarity: {similarity:.2f})")
        matched_pairs.add((source_title, target_title))

    # Check which expected matches are missing
    print("\nMissing expected matches:")
    for source, target, expected in KEY_MATCH_CASES:
        if (
            expected
            and (source, target) not in matched_pairs
            and not any(s == source and t == target for (s, t) in matched_pairs)
        ):
            print(f"  {source!r} -> {target!r}")

    # Check which unexpected matches are present
    print("\nUnexpected matches:")
    for source, target, expected in KEY_MATCH_CASES:
        if not expected and (source, target) in matched_pairs:
            print(f"  {source!r} -> {target!r}")
