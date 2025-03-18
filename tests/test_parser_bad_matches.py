"""
Tests for the parser component with bad match examples
"""

import pytest

from comic_matcher.parser import ComicTitleParser


class TestParserBadMatches:
    """
    Test the comic title parser with examples from bad matches
    to ensure proper parsing of problematic titles
    """

    def test_parser_extracts_subtitle_correctly(self):
        """Test that subtitles are correctly extracted and preserved"""
        parser = ComicTitleParser()

        test_cases = [
            # Format: title, expected_main_title
            ("New X-Men: Academy X", "new x-men academy x"),
            ("X-Men: Kitty Pryde - Shadow & Flame", "x-men kitty pryde - shadow flame"),
            ("Civil War: Casualties Of War", "civil war casualties of war"),
            ("X-Men '92: House Of Xcii", "x-men 92 house of xcii"),
        ]

        for title, expected in test_cases:
            result = parser.parse(title)
            assert result["main_title"] == expected, (
                f"Expected main_title '{expected}' for '{title}', but got '{result['main_title']}'"
            )

    def test_parser_handles_annual_correctly(self):
        """Test that annual identifiers are correctly parsed"""
        parser = ComicTitleParser()

        test_cases = [
            # Format: title, expected_special
            ("X-Men Annual", "annual"),
            ("X-Men Annual 2000", "annual"),
            ("Uncanny X-Men Annual", "annual"),
        ]

        for title, expected in test_cases:
            result = parser.parse(title)
            assert result["special"] == expected, (
                f"Expected special '{expected}' for '{title}', but got '{result['special']}'"
            )

    def test_parser_handles_special_editions(self):
        """Test parsing of special editions"""
        parser = ComicTitleParser()

        test_cases = [
            # Format: title, expected_special
            ("Uncanny X-Men Special", "special"),
            ("X-Men Special", "special"),
            ("X-Men One-Shot", "one-shot"),
            ("X-Men Giant-Size", "giant-size"),
        ]

        for title, expected in test_cases:
            result = parser.parse(title)
            assert result["special"] == expected, (
                f"Expected special '{expected}' for '{title}', but got '{result['special']}'"
            )

    def test_parser_handles_crossover_teamup(self):
        """Test parsing of crossover/team-up titles"""
        parser = ComicTitleParser()

        test_cases = [
            # Format: title, expected_clean_title
            ("Wolverine/Doop", "wolverine doop"),
            ("Spider-Man/Deadpool", "spider-man deadpool"),
            ("Wolverine and Jubilee", "wolverine and jubilee"),
            ("Batman vs Superman", "batman vs superman"),
        ]

        for title, expected in test_cases:
            result = parser.parse(title)
            # Check that the clean title preserves the team-up structure
            assert expected in result["clean_title"].lower(), (
                f"Expected clean_title to contain '{expected}' for '{title}', "
                f"but got '{result['clean_title']}'"
            )

    def test_clean_title_normalization(self):
        """Test title normalization in problem cases"""
        parser = ComicTitleParser()

        test_cases = [
            # Format: title, expected_does_not_contain
            # We want to ensure these titles do NOT get normalized to similar ones
            ("X-Men: Phoenix", "x-men"),  # Should not be just "x-men"
            ("X-Men Annual", "x-men"),  # Should preserve "annual"
            ("X-Men Unlimited", "x-men"),  # Should preserve "unlimited"
            ("Civil War: House of M", "civil war"),  # Should not be just "civil war"
        ]

        for title, should_not_be in test_cases:
            result = parser.parse(title)
            # The clean_title should contain more than just the base title,
            # preserving the distinguishing elements
            assert result["clean_title"].lower() != should_not_be, (
                f"Clean title for '{title}' should not be just '{should_not_be}', "
                f"but got '{result['clean_title']}'"
            )

    def test_parse_issue_number_from_title(self):
        """Test extraction of issue numbers from titles"""
        parser = ComicTitleParser()

        test_cases = [
            # Format: title, expected_issue
            ("X-Men #142", "142"),
            ("X-Men #2000", "2000"),
            ("Amazing Spider-Man #300", "300"),
            ("Batman: The Dark Knight Returns #1", "1"),
        ]

        for title, expected in test_cases:
            issue = parser.extract_issue_number(title)
            assert issue == expected, (
                f"Expected issue '{expected}' for '{title}', but got '{issue}'"
            )

    def test_extract_issue_number_special_cases(self):
        """Test extraction of issue numbers from special cases"""
        parser = ComicTitleParser()

        test_cases = [
            # Format: issue_text, expected_issue
            ("2000", "2000"),  # Year as issue number
            ("Annual 2000", "2000"),  # Annual with year
            ("#1", "1"),  # Standard format
            ("No. 42", "42"),  # Different format
        ]

        for issue_text, expected in test_cases:
            issue = parser.extract_issue_number(issue_text)
            assert issue == expected, (
                f"Expected issue '{expected}' for '{issue_text}', but got '{issue}'"
            )

    def test_normalize_specific_problematic_titles(self):
        """Test normalization of specific problematic titles"""
        parser = ComicTitleParser()

        # Test cases from actual bad matches
        test_cases = [
            ("X-Men '92: House Of Xcii", "x-men 92 house of xcii"),
            ("X-Men: Phoenix", "x-men phoenix"),
            ("New X-Men: Academy X", "new x-men academy x"),
            ("New X-Men", "new x-men"),
            ("X-Men Forever 2", "x-men forever 2"),
            ("X-Men Forever", "x-men forever"),
            ("Wolverine/Doop", "wolverine doop"),
            ("Wolverine", "wolverine"),
        ]

        for title, expected_clean in test_cases:
            result = parser.parse(title)
            clean_lower = result["clean_title"].lower()
            # We want to ensure normalized versions remain distinguishable
            assert clean_lower == expected_clean or expected_clean in clean_lower, (
                f"Clean title for '{title}' should contain '{expected_clean}', "
                f"but got '{clean_lower}'"
            )

    def test_annual_vs_issue_parsing(self):
        """Test specific case of issue vs annual confusion"""
        parser = ComicTitleParser()

        # Test the problematic X-Men #2000 vs X-Men Annual 2000 #1 case
        result1 = parser.parse("X-Men")
        result2 = parser.parse("X-Men Annual 2000")

        # Check that they're parsed differently
        assert result1["special"] != result2["special"], (
            f"'X-Men' and 'X-Men Annual 2000' should have different 'special' values"
        )

        # Check that "Annual" is properly identified
        assert result2["special"] == "annual", (
            f"'X-Men Annual 2000' should have 'annual' as 'special', but got '{result2['special']}'"
        )

        # X-Men #2000 vs X-Men Annual 2000 #1
        # Check issue extraction
        issue1 = parser.extract_issue_number("2000")
        issue2 = parser.extract_issue_number("1")

        # These should be different
        assert issue1 != issue2, (
            f"Issue numbers '2000' and '1' should be different, but got '{issue1}' and '{issue2}'"
        )
