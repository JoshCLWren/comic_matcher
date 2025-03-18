"""
Test cases specifically for the bad matches identified in the reading order sheet
"""

import pytest

from comic_matcher.matcher import ComicMatcher


class TestBadMatches:
    """
    Test cases for bad matches identified in the reading order sheet.
    These tests are expected to fail with the current implementation and will pass once fixed.
    """

    def test_completely_different_titles(self):
        """Test cases where the titles are completely different but got matched"""
        matcher = ComicMatcher()

        # Based on examples from analysis of bad matches
        test_cases = [
            # Format: source title, target title, should_match
            ("X-Men '92: House Of Xcii", "X-Men: Phoenix", False),
            ("X-Men: Children Of The Atom", "X-Men: The End", False),
            ("Civil War: Casualties Of War", "Civil War: House of M", False),
            ("Civil War: The Confession", "Civil War: House of M", False),
            ("Civil War: Marvels Snapshots", "Civil War: X-Men", False),
        ]

        for source_title, target_title, should_match in test_cases:
            source = {"title": source_title, "issue": "1"}
            target = {"title": target_title, "issue": "1"}

            # Test using find_best_match
            result = matcher.find_best_match(source, [target])

            assert result is None or result["similarity"] < 0.5, (
                f"'{source_title}' should not match '{target_title}' but got: "
                f"{result['similarity'] if result else 'None'}"
            )

    def test_subtitle_missing_matches(self):
        """Test cases where subtitles are missing in one title"""
        matcher = ComicMatcher()

        # Based on examples from analysis of bad matches
        test_cases = [
            # Format: source title, target title, should_match
            ("New X-Men: Academy X", "New X-Men", False),
            ("X-Men Unlimited: X-Men Green", "X-Men Unlimited", False),
        ]

        for source_title, target_title, should_match in test_cases:
            source = {"title": source_title, "issue": "2"}
            target = {"title": target_title, "issue": "2"}

            # Test using find_best_match
            result = matcher.find_best_match(source, [target])

            assert result is None or result["similarity"] < 0.5, (
                f"'{source_title}' should not match '{target_title}' but got: "
                f"{result['similarity'] if result else 'None'}"
            )

    def test_annual_special_mismatches(self):
        """Test cases with annual/special edition mismatches"""
        matcher = ComicMatcher()

        # Based on examples from analysis of bad matches
        test_cases = [
            # Format: source title, target title, should_match
            ("X-Men", "X-Men Annual", False),
            ("Uncanny X-Men", "Uncanny X-Men Annual", False),
            ("Uncanny X-Men Special", "Uncanny X-Men Annual", False),
            ("Uncanny X-Men: Winter'S End", "Uncanny X-Men Annual", False),
        ]

        for source_title, target_title, should_match in test_cases:
            source = {"title": source_title, "issue": "1"}
            target = {"title": target_title, "issue": "1"}

            # Test using find_best_match
            result = matcher.find_best_match(source, [target])

            assert result is None or result["similarity"] < 0.5, (
                f"'{source_title}' should not match '{target_title}' but got: "
                f"{result['similarity'] if result else 'None'}"
            )

    def test_series_version_mismatches(self):
        """Test cases with series version number mismatches"""
        matcher = ComicMatcher()

        # Based on examples from analysis of bad matches
        test_cases = [
            # Format: source title, target title, should_match
            ("X-Men Forever 2", "X-Men Forever", False),
        ]

        for source_title, target_title, should_match in test_cases:
            source = {"title": source_title, "issue": "1"}
            target = {"title": target_title, "issue": "1"}

            # Test using find_best_match
            result = matcher.find_best_match(source, [target])

            assert result is None or result["similarity"] < 0.5, (
                f"'{source_title}' should not match '{target_title}' but got: "
                f"{result['similarity'] if result else 'None'}"
            )

    def test_crossover_teamup_mismatches(self):
        """Test cases with crossover/team-up format differences"""
        matcher = ComicMatcher()

        # Based on examples from analysis of bad matches
        test_cases = [
            # Format: source title, target title, should_match
            ("Wolverine", "Wolverine/Doop", False),
        ]

        for source_title, target_title, should_match in test_cases:
            source = {"title": source_title, "issue": "1"}
            target = {"title": target_title, "issue": "1"}

            # Test using find_best_match
            result = matcher.find_best_match(source, [target])

            assert result is None or result["similarity"] < 0.5, (
                f"'{source_title}' should not match '{target_title}' but got: "
                f"{result['similarity'] if result else 'None'}"
            )

    def test_series_variant_mismatches(self):
        """Test cases with series variant mismatches"""
        matcher = ComicMatcher()

        # Based on examples from analysis of bad matches
        test_cases = [
            # Format: source title, target title, should_match
            ("X-Men", "X-Men Unlimited", False),
        ]

        for source_title, target_title, should_match in test_cases:
            source = {"title": source_title, "issue": "42"}
            target = {"title": target_title, "issue": "42"}

            # Test using find_best_match
            result = matcher.find_best_match(source, [target])

            assert result is None or result["similarity"] < 0.5, (
                f"'{source_title}' should not match '{target_title}' but got: "
                f"{result['similarity'] if result else 'None'}"
            )

    def test_specific_bad_matches_from_data(self):
        """Test specific bad matches identified in the reading order data"""
        matcher = ComicMatcher()

        # Based on real examples from the reading order data
        test_cases = [
            # These are specific examples from the dataset
            {
                "source": {"title": "X-Men '92: House Of Xcii", "issue": "3"},
                "target": {"title": "X-Men: Phoenix", "issue": "3"},
            },
            {
                "source": {"title": "X-Men", "issue": "2000"},
                "target": {"title": "X-Men Annual 2000", "issue": "1"},
            },
            {
                "source": {"title": "X-Men Forever 2", "issue": "1"},
                "target": {"title": "X-Men Forever", "issue": "1"},
            },
            {
                "source": {"title": "X-Men", "issue": "42"},
                "target": {"title": "X-Men Unlimited", "issue": "42"},
            },
            {
                "source": {"title": "Wolverine", "issue": "1"},
                "target": {"title": "Wolverine/Doop", "issue": "1"},
            },
            {
                "source": {"title": "New X-Men: Academy X", "issue": "2"},
                "target": {"title": "New X-Men", "issue": "2"},
            },
        ]

        for case in test_cases:
            source = case["source"]
            target = case["target"]

            # Test using find_best_match
            result = matcher.find_best_match(source, [target])

            assert result is None or result["similarity"] < 0.5, (
                f"'{source['title']}' #{source['issue']} should not match "
                f"'{target['title']}' #{target['issue']} but got: "
                f"{result['similarity'] if result else 'None'}"
            )

    def test_match_with_multiple_candidates(self):
        """Test matching with multiple candidates including bad matches"""
        matcher = ComicMatcher()

        # Test with a bad match alongside a good match
        source = {"title": "X-Men Forever 2", "issue": "1"}
        candidates = [
            {"title": "X-Men Forever", "issue": "1"},  # Bad match
            {"title": "X-Men Forever 2", "issue": "1"},  # Good match
            {"title": "X-Force", "issue": "1"},  # No match
        ]

        result = matcher.find_best_match(source, candidates)

        assert result is not None, f"Should find a match for {source['title']}"
        assert result["matched_comic"]["title"] == "X-Men Forever 2", (
            f"Should match with exact title, got {result['matched_comic']['title']}"
        )

        # Test with only bad matches
        source = {"title": "X-Men", "issue": "42"}
        candidates = [
            {"title": "X-Men Unlimited", "issue": "42"},  # Bad match
            {"title": "Uncanny X-Men", "issue": "42"},  # Different series
        ]

        result = matcher.find_best_match(source, candidates)

        assert result is None or result["similarity"] < 0.5, (
            f"Should not match with any candidate, but got {result}"
        )

    def test_annual_with_year_mismatches(self):
        """Test specific case of X-Men #2000 vs X-Men Annual 2000 #1"""
        matcher = ComicMatcher()

        source = {"title": "X-Men", "issue": "2000"}
        candidates = [{"title": "X-Men Annual 2000", "issue": "1"}]

        result = matcher.find_best_match(source, candidates)

        assert result is None or result["similarity"] < 0.5, (
            f"'X-Men #2000' should not match 'X-Men Annual 2000 #1' but got: "
            f"{result['similarity'] if result else 'None'}"
        )

    def test_same_base_different_targets(self):
        """Test cases with same base title but different subtitles/targets"""
        matcher = ComicMatcher()

        # Civil War related titles that shouldn't match
        test_cases = [
            {
                "source": {"title": "Civil War: Casualties Of War", "issue": "1"},
                "candidates": [
                    {"title": "Civil War: House of M", "issue": "1"},
                    {"title": "Civil War", "issue": "1"},
                ],
            },
            {
                "source": {"title": "Civil War: The Confession", "issue": "1"},
                "candidates": [
                    {"title": "Civil War: House of M", "issue": "1"},
                    {"title": "Civil War", "issue": "1"},
                ],
            },
            {
                "source": {"title": "Civil War: Marvels Snapshots", "issue": "1"},
                "candidates": [
                    {"title": "Civil War: X-Men", "issue": "1"},
                    {"title": "Civil War", "issue": "1"},
                ],
            },
        ]

        for case in test_cases:
            source = case["source"]
            candidates = case["candidates"]

            # Each should find no match or the base title, but not the other subtitle
            result = matcher.find_best_match(source, candidates)

            if result is not None:
                assert result["matched_comic"]["title"] == "Civil War", (
                    f"Should only match with base title, not with different subtitle. "
                    f"Got {result['matched_comic']['title']}"
                )
