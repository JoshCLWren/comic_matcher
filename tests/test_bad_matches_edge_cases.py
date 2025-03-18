"""
Tests for specific edge cases identified in the bad matches analysis
"""

import pytest

from comic_matcher.matcher import ComicMatcher


class TestBadMatchEdgeCases:
    """
    Test cases for specific edge cases identified in the bad matches analysis.
    Focuses on problematic patterns at a more granular level.
    """

    def test_special_edition_mismatches(self):
        """Test cases with special edition identifiers"""
        matcher = ComicMatcher()

        test_cases = [
            # Format: source title, target title, should_match
            ("Uncanny X-Men Special", "Uncanny X-Men Annual", False),
            ("Uncanny X-Men: Winter'S End", "Uncanny X-Men Annual", False),
            ("X-Men", "X-Men Annual", False),
            ("New X-Men", "New X-Men: Academy X Yearbook", False),
        ]

        for source_title, target_title, should_match in test_cases:
            source = {"title": source_title, "issue": "1"}
            target = {"title": target_title, "issue": "1"}

            result = matcher.find_best_match(source, [target])

            assert result is None or result["similarity"] < 0.5, (
                f"'{source_title}' should not match '{target_title}' but got: "
                f"{result['similarity'] if result else 'None'}"
            )

    def test_issue_number_in_title(self):
        """Test issue numbers appearing in the title"""
        matcher = ComicMatcher()

        test_cases = [
            # Cases where issue number appears in title
            {
                "source": {"title": "X-Men", "issue": "2000"},
                "target": {"title": "X-Men Annual 2000", "issue": "1"},
                "should_match": False,
            },
            {
                "source": {"title": "Civil War II", "issue": "1"},
                "target": {"title": "Civil War II: Choosing Sides", "issue": "1"},
                "should_match": False,
            },
        ]

        for case in test_cases:
            source = case["source"]
            target = case["target"]

            result = matcher.find_best_match(source, [target])

            if case["should_match"]:
                assert result is not None and result["similarity"] >= 0.5, (
                    f"'{source['title']}' should match '{target['title']}' but didn't"
                )
            else:
                assert result is None or result["similarity"] < 0.5, (
                    f"'{source['title']}' should not match '{target['title']}' but got: "
                    f"{result['similarity'] if result else 'None'}"
                )

    def test_kitty_pryde_series(self):
        """Test "X-Men: Kitty Pryde" series which had multiple bad matches"""
        matcher = ComicMatcher()

        # Create test cases based on the Kitty Pryde series
        source = {"title": "X-Men: Kitty Pryde - Shadow & Flame", "issue": "1"}

        # Create various targets that should not match
        bad_targets = [
            {"title": "X-Men: Phoenix", "issue": "1"},
            {"title": "X-Men: The End", "issue": "1"},
            {"title": "X-Men: Unlimited", "issue": "1"},
        ]

        # None of these should match
        for target in bad_targets:
            result = matcher.find_best_match(source, [target])

            assert result is None or result["similarity"] < 0.5, (
                f"'{source['title']}' should not match '{target['title']}' but got: "
                f"{result['similarity'] if result else 'None'}"
            )

        # This one should match
        good_target = {"title": "X-Men: Kitty Pryde - Shadow & Flame", "issue": "1"}
        result = matcher.find_best_match(source, [good_target])

        assert result is not None and result["similarity"] >= 0.9, (
            f"'{source['title']}' should match '{good_target['title']}' but got: "
            f"{result['similarity'] if result else 'None'}"
        )

    def test_roman_numeral_sequels(self):
        """Test Roman numeral sequel handling"""
        matcher = ComicMatcher()

        test_cases = [
            # Cases with Roman numeral sequels
            {
                "source": {"title": "Civil War II", "issue": "1"},
                "target": {"title": "Civil War", "issue": "1"},
                "should_match": False,
            },
            {
                "source": {"title": "Secret Wars II", "issue": "1"},
                "target": {"title": "Secret Wars", "issue": "1"},
                "should_match": False,
            },
        ]

        for case in test_cases:
            source = case["source"]
            target = case["target"]

            result = matcher.find_best_match(source, [target])

            if case["should_match"]:
                assert result is not None and result["similarity"] >= 0.5, (
                    f"'{source['title']}' should match '{target['title']}' but didn't"
                )
            else:
                assert result is None or result["similarity"] < 0.5, (
                    f"'{source['title']}' should not match '{target['title']}' but got: "
                    f"{result['similarity'] if result else 'None'}"
                )

    def test_multi_component_titles(self):
        """Test titles with multiple components/colons that shouldn't match"""
        matcher = ComicMatcher()

        test_cases = [
            # Multi-component titles
            ("X-Men: Children Of The Atom", "X-Men: The End", False),
            ("Civil War: Casualties Of War", "Civil War: House of M", False),
            ("Avengers: Disassembled", "Avengers: Earth's Mightiest Heroes", False),
        ]

        for source_title, target_title, should_match in test_cases:
            source = {"title": source_title, "issue": "1"}
            target = {"title": target_title, "issue": "1"}

            result = matcher.find_best_match(source, [target])

            if should_match:
                assert result is not None and result["similarity"] >= 0.5, (
                    f"'{source_title}' should match '{target_title}' but didn't"
                )
            else:
                assert result is None or result["similarity"] < 0.5, (
                    f"'{source_title}' should not match '{target_title}' but got: "
                    f"{result['similarity'] if result else 'None'}"
                )

    def test_abbreviated_titles(self):
        """Test abbreviated title matching"""
        matcher = ComicMatcher()

        test_cases = [
            # Abbreviated titles
            {
                "source": {"title": "Gen", "issue": "1"},
                "target": {"title": "Generation M", "issue": "1"},
                "should_match": False,
            },
            {
                "source": {"title": "X-Men", "issue": "1"},
                "target": {"title": "Astonishing X-Men", "issue": "1"},
                "should_match": False,
            },  # This should not match due to prefix normalization
        ]

        for case in test_cases:
            source = case["source"]
            target = case["target"]

            result = matcher.find_best_match(source, [target])

            if case["should_match"]:
                assert result is not None and result["similarity"] >= 0.5, (
                    f"'{source['title']}' should match '{target['title']}' but didn't"
                )
            else:
                assert result is None or result["similarity"] < 0.5, (
                    f"'{source['title']}' should not match '{target['title']}' but got: "
                    f"{result['similarity'] if result else 'None'}"
                )

    def test_slash_vs_colon_titles(self):
        """Test handling of slash vs colon in titles"""
        matcher = ComicMatcher()

        test_cases = [
            # Slash vs colon formats
            {
                "source": {"title": "Wolverine/Doop", "issue": "1"},
                "target": {"title": "Wolverine: Evolution", "issue": "1"},
                "should_match": False,
            },
            {
                "source": {"title": "Spider-Man/Deadpool", "issue": "1"},
                "target": {"title": "Spider-Man: Homecoming", "issue": "1"},
                "should_match": False,
            },
        ]

        for case in test_cases:
            source = case["source"]
            target = case["target"]

            result = matcher.find_best_match(source, [target])

            if case["should_match"]:
                assert result is not None and result["similarity"] >= 0.5, (
                    f"'{source['title']}' should match '{target['title']}' but didn't"
                )
            else:
                assert result is None or result["similarity"] < 0.5, (
                    f"'{source['title']}' should not match '{target['title']}' but got: "
                    f"{result['similarity'] if result else 'None'}"
                )

    def test_multiple_similar_candidates(self):
        """Test choosing between multiple similar candidates"""
        matcher = ComicMatcher()

        source = {"title": "X-Men", "issue": "1"}
        candidates = [
            {"title": "X-Men", "issue": "1"},  # Exact match
            {"title": "Uncanny X-Men", "issue": "1"},  # Similar but different
            {"title": "X-Men: Legacy", "issue": "1"},  # Similar but different
            {"title": "X-Men Annual", "issue": "1"},  # Should not match
        ]

        result = matcher.find_best_match(source, candidates)

        assert result is not None, "Should find a match"
        assert result["matched_comic"]["title"] == "X-Men", (
            f"Should match with exact title, got {result['matched_comic']['title']}"
        )
        assert result["matched_comic"]["issue"] == "1", (
            f"Should match with correct issue, got {result['matched_comic']['issue']}"
        )

    def test_explicit_real_world_bad_matches(self):
        """Test specific real-world examples from the dataset with explicit titles"""
        matcher = ComicMatcher()

        # Match exact examples from the dataset
        test_cases = [
            # These are the actual pairs from the spreadsheet
            {
                "source": {"title": "X-Men '92: House Of Xcii", "issue": "3"},
                "target": {"title": "X-Men: Phoenix", "issue": "3"},
                "should_match": False,
            },
            {
                "source": {"title": "X-Men: Children Of The Atom", "issue": "6"},
                "target": {"title": "X-Men: The End", "issue": "6"},
                "should_match": False,
            },
            {
                "source": {"title": "Civil War: Casualties Of War", "issue": "1"},
                "target": {"title": "Civil War: House of M", "issue": "1"},
                "should_match": False,
            },
            {
                "source": {"title": "Civil War: The Confession", "issue": "1"},
                "target": {"title": "Civil War: House of M", "issue": "1"},
                "should_match": False,
            },
            {
                "source": {"title": "Uncanny X-Men Special", "issue": "1"},
                "target": {"title": "Uncanny X-Men Annual", "issue": "1"},
                "should_match": False,
            },
        ]

        for case in test_cases:
            source = case["source"]
            target = case["target"]

            result = matcher.find_best_match(source, [target])

            if case["should_match"]:
                assert result is not None and result["similarity"] >= 0.5, (
                    f"'{source['title']}' should match '{target['title']}' but didn't"
                )
            else:
                assert result is None or result["similarity"] < 0.5, (
                    f"'{source['title']}' should not match '{target['title']}' but got: "
                    f"{result['similarity'] if result else 'None'}"
                )
