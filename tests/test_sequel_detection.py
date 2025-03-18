"""
Test suite for sequel detection functionality
"""

import re

import pytest

from comic_matcher.matcher import ComicMatcher


def test_extract_sequel_number():
    """Test extraction of sequel numbers from comic titles"""
    matcher = ComicMatcher()

    # Test cases with arabic numerals
    assert matcher._extract_sequel_number("Civil War 2") == "2"
    assert matcher._extract_sequel_number("Secret Wars 3") == "3"

    # Test cases with Roman numerals
    assert matcher._extract_sequel_number("Civil War II") == "II"
    assert matcher._extract_sequel_number("Secret Wars III") == "III"
    assert matcher._extract_sequel_number("X-Men Legacy IV") == "IV"
    assert matcher._extract_sequel_number("Avengers V") == "V"

    # Test cases that should not be detected as sequels
    assert matcher._extract_sequel_number("X-Men #2") is None  # Issue number, not sequel
    assert matcher._extract_sequel_number("Uncanny X-Men") is None
    assert matcher._extract_sequel_number("") is None
    assert matcher._extract_sequel_number(None) is None


def test_compare_titles_with_sequels():
    """Test title comparison with sequels doesn't match different sequels"""
    matcher = ComicMatcher()

    # Different sequels should have zero similarity
    assert (
        matcher._compare_titles("Civil War", "Civil War II") > 0.5
    )  # Different titles, one has sequel
    assert matcher._compare_titles("Civil War II", "Civil War III") == 0.0  # Different sequels
    assert (
        matcher._compare_titles("Secret Wars 2", "Secret Wars 3") == 0.0
    )  # Different sequels (arabic)

    # Same sequels or non-sequels should match normally
    assert matcher._compare_titles("Civil War II", "Civil War II") == 1.0  # Exact match
    assert matcher._compare_titles("Civil War", "Civil War") == 1.0  # Exact match, no sequel


def test_find_best_match_with_sequels():
    """Test finding best match with sequel titles"""
    matcher = ComicMatcher()

    # Test with Civil War series
    source_comic = {"title": "Civil War II", "issue": "1"}
    candidates = [
        {"title": "Civil War", "issue": "1"},
        {"title": "Civil War II", "issue": "1"},
        {"title": "Civil War III", "issue": "1"},
    ]

    match = matcher.find_best_match(source_comic, candidates)
    assert match is not None
    assert match["matched_comic"]["title"] == "Civil War II"

    # Test with only different sequels available
    source_comic = {"title": "Secret Wars 2", "issue": "1"}
    candidates = [
        {"title": "Secret Wars", "issue": "1"},
        {"title": "Secret Wars 3", "issue": "1"},
    ]

    # Should match with "Secret Wars" (non-sequel) rather than "Secret Wars 3" (different sequel)
    match = matcher.find_best_match(source_comic, candidates)
    assert match is not None
    assert match["matched_comic"]["title"] == "Secret Wars"
