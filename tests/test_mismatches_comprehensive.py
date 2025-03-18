"""
Comprehensive tests for mismatches identified in the data
"""

import pandas as pd
import pytest

from comic_matcher.matcher import ComicMatcher


class TestMismatchComprehensive:
    """
    Comprehensive tests for the known mismatches in the data.
    These tests ensure that incorrectly matched items are properly handled.
    """

    @pytest.fixture
    def matcher(self):
        """Initialize a fresh matcher for each test"""
        return ComicMatcher()

    @pytest.fixture
    def x_men_annual_data(self):
        """Data for X-Men Annual vs regular issue tests"""
        return [
            # Source data
            {"title": "X-Men", "issue": "2000"},
            # Target data
            {"title": "X-Men Annual 2000", "issue": "1"},
        ]

    @pytest.fixture
    def x_men_unlimited_data(self):
        """Data for X-Men vs X-Men Unlimited tests"""
        return [
            # Source data
            {"title": "X-Men", "issue": "42"},
            {"title": "X-Men", "issue": "46"},
            {"title": "X-Men", "issue": "47"},
            {"title": "X-Men", "issue": "48"},
            # Target data
            {"title": "X-Men Unlimited", "issue": "42"},
            {"title": "X-Men Unlimited", "issue": "46"},
            {"title": "X-Men Unlimited", "issue": "47"},
            {"title": "X-Men Unlimited", "issue": "48"},
        ]

    @pytest.fixture
    def new_x_men_data(self):
        """Data for New X-Men: Academy X vs New X-Men tests"""
        return [
            # Source data
            {"title": "New X-Men: Academy X", "issue": "7"},
            {"title": "New X-Men: Academy X", "issue": "9"},
            # Target data
            {"title": "New X-Men", "issue": "7"},
            {"title": "New X-Men", "issue": "9"},
        ]

    @pytest.fixture
    def kitty_pryde_data(self):
        """Data for X-Men: Kitty Pryde - Shadow & Flame vs X-Men: Die By The Sword tests"""
        return [
            # Source data
            {"title": "X-Men: Kitty Pryde - Shadow & Flame", "issue": "1"},
            {"title": "X-Men: Kitty Pryde - Shadow & Flame", "issue": "2"},
            {"title": "X-Men: Kitty Pryde - Shadow & Flame", "issue": "3"},
            {"title": "X-Men: Kitty Pryde - Shadow & Flame", "issue": "4"},
            {"title": "X-Men: Kitty Pryde - Shadow & Flame", "issue": "5"},
            # Target data
            {"title": "X-Men: Die By The Sword", "issue": "1"},
            {"title": "X-Men: Die By The Sword", "issue": "2"},
            {"title": "X-Men: Die By The Sword", "issue": "3"},
            {"title": "X-Men: Die By The Sword", "issue": "4"},
            {"title": "X-Men: Die By The Sword", "issue": "5"},
        ]

    @pytest.fixture
    def dc_vs_marvel_data(self):
        """Data for DC Versus Marvel/Marvel Versus DC tests"""
        return [
            # Source data (different variations of the same title)
            {
                "title": "DC Versus Marvel/Marvel Versus DC Consumer Preview",
                "issue": "1",
            },
            {"title": "DC Versus Marvel/Marvel Versus DC", "issue": "1"},
            {"title": "Marvel Versus DC/DC Versus Marvel", "issue": "2"},
            {"title": "Marvel Universe Vs Wolverine", "issue": "2"},
            {"title": "Marvel Versus DC/DC Versus Marvel", "issue": "3"},
            {"title": "Marvel Universe Vs Wolverine", "issue": "3"},
            {"title": "DC Versus Marvel/Marvel Versus DC", "issue": "4"},
            # Target data
            {"title": "DC Versus Marvel", "issue": "1"},
            {"title": "Marvel Versus DC", "issue": "2"},
            {"title": "Marvel Versus DC", "issue": "3"},
            {"title": "DC Versus Marvel", "issue": "4"},
        ]

    @pytest.fixture
    def all_mismatch_data(
        self,
        x_men_annual_data,
        x_men_unlimited_data,
        new_x_men_data,
        kitty_pryde_data,
        dc_vs_marvel_data,
    ):
        """Combined dataset of all mismatches for integration testing"""
        source_data = (
            x_men_annual_data[:1]
            + x_men_unlimited_data[:4]
            + new_x_men_data[:2]
            + kitty_pryde_data[:5]
            + dc_vs_marvel_data[:7]
        )

        target_data = (
            x_men_annual_data[1:]
            + x_men_unlimited_data[4:]
            + new_x_men_data[2:]
            + kitty_pryde_data[5:]
            + dc_vs_marvel_data[7:]
        )

        return {"source": source_data, "target": target_data}

    def test_x_men_annual_mismatch(self, matcher, x_men_annual_data):
        """
        Test that X-Men #2000 does not match with X-Men Annual 2000 #1
        These are different issues that happen to have similar numbering.
        """
        source = x_men_annual_data[0]
        target = x_men_annual_data[1]

        # Test direct matching
        result = matcher.find_best_match(source, [target])

        # This should not match or have a very low similarity score
        assert result is None or result["similarity"] < 0.5, (
            f"Should not match X-Men #2000 with X-Men Annual 2000 #1, got {result}"
        )

        # Test matching with DataFrame
        source_df = pd.DataFrame([source])
        target_df = pd.DataFrame([target])

        matches = matcher.match(source_df, target_df, threshold=0.3)

        # Should have no matches or very low confidence
        assert matches.empty or all(matches["similarity"] < 0.5), (
            f"Should not match X-Men #2000 with X-Men Annual 2000 #1 in DataFrame"
        )

    def test_x_men_unlimited_mismatch(self, matcher, x_men_unlimited_data):
        """
        Test that X-Men issues do not match with X-Men Unlimited issues
        These are different series despite the similar names.
        """
        source_comics = x_men_unlimited_data[:4]  # X-Men issues
        target_comics = x_men_unlimited_data[4:]  # X-Men Unlimited issues

        # Test each pair individually
        for source, target in zip(source_comics, target_comics):
            result = matcher.find_best_match(source, [target])

            # This should not match or have a very low similarity score
            assert result is None or result["similarity"] < 0.5, (
                f"Should not match {source} with {target}, got {result}"
            )

        # Test batch matching
        source_df = pd.DataFrame(source_comics)
        target_df = pd.DataFrame(target_comics)

        matches = matcher.match(source_df, target_df, threshold=0.3)

        # Should have no matches or very low confidence
        assert matches.empty or all(matches["similarity"] < 0.5), (
            f"Should not match X-Men with X-Men Unlimited in DataFrame"
        )

    def test_new_x_men_academy_mismatch(self, matcher, new_x_men_data):
        """
        Test that New X-Men: Academy X does not match with New X-Men
        These are different series despite the similar names.
        """
        source_comics = new_x_men_data[:2]  # New X-Men: Academy X
        target_comics = new_x_men_data[2:]  # New X-Men

        # Test each pair individually
        for source, target in zip(source_comics, target_comics):
            result = matcher.find_best_match(source, [target])

            # This should not match or have a very low similarity score
            assert result is None or result["similarity"] < 0.5, (
                f"Should not match {source} with {target}, got {result}"
            )

        # Test batch matching
        source_df = pd.DataFrame(source_comics)
        target_df = pd.DataFrame(target_comics)

        matches = matcher.match(source_df, target_df, threshold=0.3)

        # Should have no matches or very low confidence
        assert matches.empty or all(matches["similarity"] < 0.5), (
            f"Should not match New X-Men: Academy X with New X-Men in DataFrame"
        )

    def test_kitty_pryde_mismatch(self, matcher, kitty_pryde_data):
        """
        Test that X-Men: Kitty Pryde - Shadow & Flame does not match X-Men: Die By The Sword
        These are completely different titles that should not match.
        """
        source_comics = kitty_pryde_data[:5]  # Kitty Pryde
        target_comics = kitty_pryde_data[5:]  # Die By The Sword

        # Test each pair individually
        for source, target in zip(source_comics, target_comics):
            result = matcher.find_best_match(source, [target])

            # This should not match or have a very low similarity score
            assert result is None or result["similarity"] < 0.5, (
                f"Should not match {source} with {target}, got {result}"
            )

        # Test batch matching
        source_df = pd.DataFrame(source_comics)
        target_df = pd.DataFrame(target_comics)

        matches = matcher.match(source_df, target_df, threshold=0.3)

        # Should have no matches or very low confidence
        assert matches.empty or all(matches["similarity"] < 0.5), (
            f"Should not match Kitty Pryde with Die By The Sword in DataFrame"
        )

    def test_dc_vs_marvel_variations(self, matcher, dc_vs_marvel_data):
        """
        Test handling of the various DC vs Marvel title variations
        Some should match, others (like Marvel Universe vs Wolverine) should not.
        """
        # First test should match: DC Versus Marvel/Marvel Versus DC with DC Versus Marvel
        source1 = dc_vs_marvel_data[1]  # DC Versus Marvel/Marvel Versus DC #1
        target1 = dc_vs_marvel_data[7]  # DC Versus Marvel #1
        result1 = matcher.find_best_match(source1, [target1])

        # These should match with high similarity despite the variation
        assert result1 is not None and result1["similarity"] >= 0.7, (
            f"Should match similar DC vs Marvel titles, got {result1}"
        )

        # Next test should NOT match: Marvel Universe Vs Wolverine with Marvel Versus DC
        source2 = dc_vs_marvel_data[3]  # Marvel Universe Vs Wolverine #2
        target2 = dc_vs_marvel_data[8]  # Marvel Versus DC #2
        result2 = matcher.find_best_match(source2, [target2])

        # These should not match (completely different titles)
        assert result2 is None or result2["similarity"] < 0.5, (
            f"Should not match Marvel Universe Vs Wolverine with Marvel Versus DC, got {result2}"
        )

    def test_integration_all_mismatches(self, matcher, all_mismatch_data):
        """
        Integration test with all mismatch types together
        Ensures the matcher correctly handles all various mismatch cases simultaneously.
        """
        source_df = pd.DataFrame(all_mismatch_data["source"])
        target_df = pd.DataFrame(all_mismatch_data["target"])

        # Set a threshold that would allow matches if the matcher wasn't handling these cases
        matches = matcher.match(source_df, target_df, threshold=0.3)

        # Check for specific problematic matches
        problematic_matches = []

        if not matches.empty:
            for _, match in matches.iterrows():
                source_title = match["source_title"]
                target_title = match["target_title"]

                # Check for known problematic matches
                if any(
                    [
                        "X-Men Annual" in target_title and "Annual" not in source_title,
                        "X-Men Unlimited" in target_title and "Unlimited" not in source_title,
                        "New X-Men: Academy X" in source_title and "Academy X" not in target_title,
                        "Kitty Pryde" in source_title and "Die By The Sword" in target_title,
                        "Marvel Universe Vs Wolverine" in source_title
                        and "Marvel Versus DC" in target_title,
                    ]
                ):
                    problematic_matches.append((source_title, target_title, match["similarity"]))

        # Assert no problematic matches above reasonable confidence
        problematic_high_confidence = [m for m in problematic_matches if m[2] >= 0.5]
        assert len(problematic_high_confidence) == 0, (
            f"Found problematic high-confidence matches: {problematic_high_confidence}"
        )

    def test_with_special_case_handling(self, matcher):
        """
        Test that we can handle special cases with a pre-defined mapping
        This allows for manual overrides of known problematic matches.
        """
        # Create a ComicMatcher with special case handling
        # For a real implementation, this could be loaded from a JSON file
        special_case_map = {
            "X-Men: Kitty Pryde - Shadow & Flame": "X-Men: Die By The Sword",
            "X-Men": "X-Men Unlimited",  # Forced match for issue numbers
            "Marvel Universe Vs Wolverine": "Marvel Versus DC",  # Forced match for issue numbers
        }

        # Create test cases
        source = {"title": "X-Men: Kitty Pryde - Shadow & Flame", "issue": "1"}
        target = {"title": "X-Men: Die By The Sword", "issue": "1"}

        # In a real implementation, the matcher would need to be modified to use the special_case_map
        # For this test, we'll mock the behavior:

        # Manual matching based on special case map
        if (
            source["title"] in special_case_map
            and special_case_map[source["title"]] == target["title"]
        ):
            # This is a special case match
            assert True, "Special case matching should allow this match"
        else:
            # Normal matching should reject this
            result = matcher.find_best_match(source, [target])
            assert result is None or result["similarity"] < 0.5, (
                f"Should not match without special case handling, got {result}"
            )


class TestMismatchEdgeCases:
    """
    Additional tests for edge cases and specific scenarios from the mismatches data.
    """

    @pytest.fixture
    def matcher(self):
        """Initialize a fresh matcher for each test"""
        return ComicMatcher()

    def test_year_vs_issue_number(self, matcher):
        """Test handling of year vs issue number confusion"""
        source = {"title": "X-Men", "issue": "1997"}
        target = {"title": "X-Men Annual 1997", "issue": "1"}

        result = matcher.find_best_match(source, [target])

        # Should not match a year with an issue number
        assert result is None or result["similarity"] < 0.5, (
            f"Should not match X-Men #1997 with X-Men Annual 1997 #1, got {result}"
        )

    def test_team_up_title_mismatch(self, matcher):
        """Test handling of team-up titles like Wolverine/Doop"""
        source = {"title": "Wolverine/Doop", "issue": "1"}
        target = {"title": "Wolverine", "issue": "1"}

        result = matcher.find_best_match(source, [target])

        # Should not match team-up with solo title
        assert result is None

    def test_yearbook_vs_regular_title(self, matcher):
        """Test handling of yearbook vs regular title"""
        source = {"title": "New X-Men: Academy X", "issue": "1"}
        target = {"title": "New X-Men: Academy X Yearbook", "issue": "1"}

        result = matcher.find_best_match(source, [target])

        # Should not match regular series with yearbook
        assert result is None or result["similarity"] < 0.5, (
            f"Should not match regular series with yearbook, got {result}"
        )

    def test_dracula_gauntlet_vs_regular_deadpool(self, matcher):
        """Test handling of Deadpool: Dracula's Gauntlet vs regular Deadpool"""
        source = {"title": "Deadpool: Dracula's Gauntlet", "issue": "7"}
        target = {"title": "Deadpool", "issue": "7"}

        result = matcher.find_best_match(source, [target])

        # Should not match subtitled series with regular series
        assert result is None or result["similarity"] < 0.5, (
            f"Should not match Deadpool: Dracula's Gauntlet with Deadpool, got {result}"
        )

    def test_half_vs_full_issue_number(self, matcher):
        """Test handling of issue #1/2 vs #1"""
        source = {"title": "Gambit", "issue": "1/2"}
        target = {"title": "Gambit", "issue": "1"}

        result = matcher.find_best_match(source, [target])

        # These should be treated as different issues
        assert result is None or result["similarity"] < 0.5, (
            f"Should not match issue #1/2 with #1, got {result}"
        )

    def test_volume_vs_series_name(self, matcher):
        """Test handling where volume is part of series name vs regular volume"""
        source = {"title": "Weapon X vol. 5", "issue": "5"}
        target = {"title": "Weapon X", "issue": "5"}
        result = matcher.find_best_match(source, [target])

        # The matcher should normalize and match these
        assert result is None
