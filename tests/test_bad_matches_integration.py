"""
Integration tests for bad matches identified in the reading order sheet
"""

import pandas as pd
import pytest

from comic_matcher.matcher import ComicMatcher


class TestBadMatchesIntegration:
    """
    Integration tests for bad matches identified in the reading order sheet.
    Tests full matching pipeline with multiple comics simultaneously.
    """

    def test_different_title_categories_integration(self):
        """
        Test integration with multiple comics representing different bad match categories
        """
        matcher = ComicMatcher()

        # Source comics representing different categories of bad matches
        source_comics = [
            # Completely different titles
            {"title": "X-Men '92: House Of Xcii", "issue": "3"},
            # Subtitle missing
            {"title": "New X-Men: Academy X", "issue": "2"},
            # Annual/special issue
            {"title": "X-Men", "issue": "2000"},
            # Series version
            {"title": "X-Men Forever 2", "issue": "1"},
            # Crossover/team-up
            {"title": "Wolverine", "issue": "1"},
            # Series variant
            {"title": "X-Men", "issue": "42"},
            # Control cases that should match
            {"title": "Uncanny X-Men", "issue": "142"},
            {"title": "Amazing Spider-Man", "issue": "300"},
        ]

        # Target comics that would cause bad matches
        target_comics = [
            # Completely different titles
            {"title": "X-Men: Phoenix", "issue": "3"},
            # Subtitle missing
            {"title": "New X-Men", "issue": "2"},
            # Annual/special issue
            {"title": "X-Men Annual 2000", "issue": "1"},
            # Series version
            {"title": "X-Men Forever", "issue": "1"},
            # Crossover/team-up
            {"title": "Wolverine/Doop", "issue": "1"},
            # Series variant
            {"title": "X-Men Unlimited", "issue": "42"},
            # Matches for control cases
            {"title": "Uncanny X-Men", "issue": "142"},
            {"title": "Amazing Spider-Man", "issue": "300"},
        ]

        # Run the matcher
        matches = matcher.match(source_comics, target_comics, threshold=0.5)

        # We should only find matches for the control cases
        expected_matches = 2  # Just the control cases

        # Verify match count
        assert len(matches) == expected_matches, (
            f"Expected {expected_matches} matches but got {len(matches)}"
        )

        # Verify that only the control cases matched
        matched_sources = matches["source_title"].tolist()
        assert "Uncanny X-Men" in matched_sources, "Control case 'Uncanny X-Men' did not match"
        assert "Amazing Spider-Man" in matched_sources, (
            "Control case 'Amazing Spider-Man' did not match"
        )

        # Ensure none of the bad match cases matched
        bad_match_titles = [
            "X-Men '92: House Of Xcii",
            "New X-Men: Academy X",
            "X-Men Forever 2",
            "Wolverine",
            "X-Men",
        ]

        for title in bad_match_titles:
            assert title not in matched_sources, f"Bad match case '{title}' matched incorrectly"

    def test_civil_war_title_mismatches(self):
        """Test specific case of Civil War related titles that should not match"""
        matcher = ComicMatcher()

        # Source comics - different Civil War subtitles
        source_comics = [
            {"title": "Civil War: Casualties Of War", "issue": "1"},
            {"title": "Civil War: The Confession", "issue": "1"},
            {"title": "Civil War: Marvels Snapshots", "issue": "1"},
            {"title": "Civil War", "issue": "1"},  # Base title should match
        ]

        # Target comics
        target_comics = [
            {"title": "Civil War: House of M", "issue": "1"},
            {"title": "Civil War: X-Men", "issue": "1"},
            {"title": "Civil War", "issue": "1"},  # Base title
        ]

        # Run the matcher
        matches = matcher.match(source_comics, target_comics, threshold=0.5)

        # We should only match the base "Civil War" title
        expected_matches = 1

        # Verify match count
        assert len(matches) == expected_matches, (
            f"Expected {expected_matches} matches but got {len(matches)}"
        )

        # Verify that only the base title matched
        matched_source = matches["source_title"].tolist()[0]
        matched_target = matches["target_title"].tolist()[0]

        assert matched_source == "Civil War", f"Expected 'Civil War' but got '{matched_source}'"
        assert matched_target == "Civil War", f"Expected 'Civil War' but got '{matched_target}'"

    def test_reading_order_vs_wishlist_integration(self):
        """
        Simulate reading order vs wishlist matching with actual problem cases
        """
        matcher = ComicMatcher()

        # Simulate reading order entries (target)
        reading_order = [
            {"title": "X-Men: Phoenix", "issue": "3", "reading_order": "375.023"},
            {"title": "X-Men Annual 2000", "issue": "1", "reading_order": "383.002"},
            {"title": "X-Men Forever", "issue": "1", "reading_order": "385.002"},
            {"title": "X-Men Forever", "issue": "5", "reading_order": "385.006"},
            {"title": "X-Men Unlimited", "issue": "42", "reading_order": "415.05"},
            {"title": "Wolverine/Doop", "issue": "1", "reading_order": "424.211"},
            {"title": "Wolverine/Doop", "issue": "2", "reading_order": "424.212"},
            {"title": "New X-Men", "issue": "2", "reading_order": "449.009"},
            {"title": "New X-Men", "issue": "3", "reading_order": "449.01"},
            # Control - should match
            {"title": "Uncanny X-Men", "issue": "142", "reading_order": "100.1"},
        ]

        # Simulate wishlist entries (source)
        wishlist = [
            {"title": "X-Men '92: House Of Xcii", "issue": "3", "store": "Store A"},
            {"title": "X-Men", "issue": "2000", "store": "Store B"},
            {"title": "X-Men Forever 2", "issue": "1", "store": "Store C"},
            {"title": "X-Men Forever 2", "issue": "5", "store": "Store D"},
            {"title": "X-Men", "issue": "42", "store": "Store E"},
            {"title": "Wolverine", "issue": "1", "store": "Store F"},
            {"title": "Wolverine", "issue": "2", "store": "Store G"},
            {"title": "New X-Men: Academy X", "issue": "2", "store": "Store H"},
            {"title": "New X-Men: Academy X", "issue": "3", "store": "Store I"},
            # Control - should match
            {"title": "Uncanny X-Men", "issue": "142", "store": "Store J"},
        ]

        # Run the matcher
        matches = matcher.match(wishlist, reading_order, threshold=0.5)

        # We should only match the control case
        expected_matches = 1

        # Verify match count
        assert len(matches) == expected_matches, (
            f"Expected {expected_matches} matches but got {len(matches)}"
        )

        # Verify the control case matched
        assert matches["source_title"].iloc[0] == "Uncanny X-Men", "Control case did not match"
        assert matches["source_issue"].iloc[0] == "142", "Control case issue did not match"

    def test_issue_annual_disambiguation(self):
        """
        Test specific case of issue number vs annual confusion
        X-Men #2000 vs X-Men Annual 2000 #1
        """
        matcher = ComicMatcher()

        # Test both directions of the matching
        source = [{"title": "X-Men", "issue": "2000"}]
        target = [{"title": "X-Men Annual 2000", "issue": "1"}]

        # Direction 1: source → target
        matches1 = matcher.match(source, target, threshold=0.5)

        # Direction 2: target → source
        matches2 = matcher.match(target, source, threshold=0.5)

        # Neither direction should match
        assert len(matches1) == 0, "X-Men #2000 should not match X-Men Annual 2000 #1"
        assert len(matches2) == 0, "X-Men Annual 2000 #1 should not match X-Men #2000"

    def test_full_reading_order_sample(self):
        """
        Test with a larger sample that simulates the reading order sheet
        """
        matcher = ComicMatcher()

        # Simulate a larger reading order dataset (target)
        reading_order_data = [
            # Regular matches that should work
            {"title": "Uncanny X-Men", "issue": "142", "reading_order": "100.1"},
            {"title": "X-Men", "issue": "1", "reading_order": "200.1"},
            {"title": "Wolverine", "issue": "100", "reading_order": "300.1"},
            {"title": "X-Force", "issue": "50", "reading_order": "400.1"},
            # Bad matches we want to avoid
            {"title": "X-Men: Phoenix", "issue": "3", "reading_order": "375.023"},
            {"title": "X-Men Annual 2000", "issue": "1", "reading_order": "383.002"},
            {"title": "X-Men Forever", "issue": "1", "reading_order": "385.002"},
            {"title": "X-Men Forever", "issue": "5", "reading_order": "385.006"},
            {"title": "X-Men Unlimited", "issue": "42", "reading_order": "415.05"},
            {"title": "Wolverine/Doop", "issue": "1", "reading_order": "424.211"},
            {"title": "New X-Men", "issue": "2", "reading_order": "449.009"},
            {"title": "New X-Men", "issue": "3", "reading_order": "449.01"},
            {
                "title": "Civil War: House of M",
                "issue": "1",
                "reading_order": "461.072",
            },
            {"title": "Civil War: X-Men", "issue": "1", "reading_order": "486.038"},
        ]

        # Simulate wishlist/store inventory (source)
        wishlist_data = [
            # Good matches
            {"title": "Uncanny X-Men", "issue": "142", "store": "Store A"},
            {"title": "X-Men", "issue": "1", "store": "Store B"},
            {"title": "Wolverine", "issue": "100", "store": "Store C"},
            {"title": "X-Force", "issue": "50", "store": "Store D"},
            # Should not match
            {"title": "X-Men '92: House Of Xcii", "issue": "3", "store": "Store E"},
            {"title": "X-Men", "issue": "2000", "store": "Store F"},
            {"title": "X-Men Forever 2", "issue": "1", "store": "Store G"},
            {"title": "X-Men Forever 2", "issue": "5", "store": "Store H"},
            {"title": "X-Men", "issue": "42", "store": "Store I"},
            {"title": "Wolverine", "issue": "1", "store": "Store J"},
            {"title": "New X-Men: Academy X", "issue": "2", "store": "Store K"},
            {"title": "New X-Men: Academy X", "issue": "3", "store": "Store L"},
            {"title": "Civil War: Casualties Of War", "issue": "1", "store": "Store M"},
            {"title": "Civil War: The Confession", "issue": "1", "store": "Store N"},
            {"title": "Civil War: Marvels Snapshots", "issue": "1", "store": "Store O"},
        ]

        # Convert to DataFrames
        reading_order_df = pd.DataFrame(reading_order_data)
        wishlist_df = pd.DataFrame(wishlist_data)

        # Run the matcher
        matches = matcher.match(wishlist_df, reading_order_df, threshold=0.5)

        # We should only match the regular cases
        expected_matches = 4

        assert len(matches) == expected_matches, (
            f"Expected {expected_matches} matches but got {len(matches)}"
        )
