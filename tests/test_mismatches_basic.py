"""
Basic tests for specific mismatches identified in the data
"""

import pytest

from comic_matcher.matcher import ComicMatcher


def test_annual_vs_regular_issues():
    """Test handling of annual issues vs regular issues"""
    matcher = ComicMatcher()

    # X-Men #2000 vs X-Men Annual 2000 #1
    source = {"title": "X-Men", "issue": "2000"}
    target = {"title": "X-Men Annual 2000", "issue": "1"}

    # Test using find_best_match
    result = matcher.find_best_match(source, [target])

    # Should not match annual 2000 #1 with regular issue #2000
    assert result is None or result["similarity"] < 0.5


def test_unlimited_vs_regular_series():
    """Test handling of X-Men vs X-Men Unlimited"""
    matcher = ComicMatcher()

    # X-Men #42 vs X-Men Unlimited #42
    source = {"title": "X-Men", "issue": "42"}
    target = {"title": "X-Men Unlimited", "issue": "42"}

    # Test using find_best_match
    result = matcher.find_best_match(source, [target])

    # Should not match regular series with Unlimited series
    assert result is None or result["similarity"] < 0.5


def test_academy_x_vs_regular_series():
    """Test handling of New X-Men: Academy X vs New X-Men"""
    matcher = ComicMatcher()

    # New X-Men: Academy X #7 vs New X-Men #7
    source = {"title": "New X-Men: Academy X", "issue": "7"}
    target = {"title": "New X-Men", "issue": "7"}

    # Test using find_best_match
    result = matcher.find_best_match(source, [target])

    # Should not match Academy X with the regular series
    assert result is None or result["similarity"] < 0.5


def test_completely_different_titles():
    """Test handling of completely different titles that have been mismatched"""
    matcher = ComicMatcher()

    # X-Men: Kitty Pryde - Shadow & Flame vs X-Men: Die By The Sword
    source = {"title": "X-Men: Kitty Pryde - Shadow & Flame", "issue": "1"}
    target = {"title": "X-Men: Die By The Sword", "issue": "1"}

    # Test using find_best_match
    result = matcher.find_best_match(source, [target])

    # Should not match these completely different titles
    assert result is None or result["similarity"] < 0.5
