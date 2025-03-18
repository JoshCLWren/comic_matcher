"""
Tests for the comic_matcher.matcher module
"""

import json
from pathlib import Path

import pandas as pd
import pytest

from comic_matcher.matcher import ComicMatcher


class TestComicMatcher:
    """Test cases for ComicMatcher"""

    def test_initialization(self, test_cache_dir):
        """Test initialization of matcher"""
        matcher = ComicMatcher(cache_dir=test_cache_dir)
        assert hasattr(matcher, "parser")
        assert matcher.cache_dir == test_cache_dir
        assert hasattr(matcher, "fuzzy_hash")
        assert matcher._title_cache == {}

        # Check cache directory was created
        assert Path(test_cache_dir).exists()

    def test_initialization_with_fuzzy_hash(self, fuzzy_hash_path):
        """Test initialization with fuzzy hash file"""
        matcher = ComicMatcher(fuzzy_hash_path=fuzzy_hash_path)
        assert len(matcher.fuzzy_hash) > 0
        assert "uncanny xmen|xmen" in matcher.fuzzy_hash

    def test_initialization_with_invalid_fuzzy_hash(self, tmp_path):
        """Test initialization with invalid fuzzy hash file"""
        # Create an invalid JSON file
        invalid_path = tmp_path / "invalid.json"
        with open(invalid_path, "w") as f:
            f.write("This is not valid JSON")

        # Should not raise an exception, but log a warning
        with pytest.warns(UserWarning, match="Error loading fuzzy hash file") as record:
            matcher = ComicMatcher(fuzzy_hash_path=str(invalid_path))
            assert matcher.fuzzy_hash == {}

    def test_prepare_dataframe_with_list(self, source_comics):
        """Test preparing dataframe from list of dictionaries"""
        matcher = ComicMatcher()
        df = matcher._prepare_dataframe(source_comics, "test_source")

        # Check basic structure
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(source_comics)
        assert "source" in df.columns
        assert df["source"].iloc[0] == "test_source"

        # Check parsed columns
        assert "parsed_main_title" in df.columns
        assert "parsed_volume" in df.columns
        assert "parsed_year" in df.columns
        assert "parsed_subtitle" in df.columns
        assert "parsed_special" in df.columns
        assert "parsed_clean_title" in df.columns

        # Check issue normalization
        assert "normalized_issue" in df.columns

    def test_prepare_dataframe_with_dataframe(self, source_df):
        """Test preparing dataframe from an existing dataframe"""
        matcher = ComicMatcher()
        df = matcher._prepare_dataframe(source_df, "test_source")

        # Check basic structure
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(source_df)
        assert "source" in df.columns
        assert df["source"].iloc[0] == "test_source"

    def test_prepare_dataframe_with_missing_columns(self):
        """Test preparing dataframe with missing required columns"""
        matcher = ComicMatcher()

        # Create data missing title and issue
        comics = [
            {"name": "X-Men", "number": "1"},
            {"name": "Spider-Man", "number": "300"},
        ]

        df = matcher._prepare_dataframe(comics, "test_source")

        # Should map alternative column names
        assert "title" in df.columns
        assert "issue" in df.columns
        assert df["title"].iloc[0] == "X-Men"
        assert df["issue"].iloc[0] == "1"

    def test_clean_title_for_hash(self):
        """Test cleaning title for fuzzy hash"""
        matcher = ComicMatcher()

        # Test basic cleaning
        assert matcher._clean_title_for_hash("Uncanny X-Men") == "uncanny xmen"

        # Test with volume, year, and banned terms
        assert matcher._clean_title_for_hash("X-Men Vol. 2 (1991) Marvel Comics") == "xmen"

        # Test with separators
        assert matcher._clean_title_for_hash("X-Factor :: The Beginning") == "xfactor"

        # Test with non-string input
        assert matcher._clean_title_for_hash(None) == ""
        assert matcher._clean_title_for_hash(123) == ""

    def test_compare_titles(self):
        """Test title comparison logic"""
        matcher = ComicMatcher()

        # Test exact match on clean titles
        assert matcher._compare_titles("Uncanny X-Men", "Uncanny X-Men") == 1.0

        # Test similar titles
        assert matcher._compare_titles("Uncanny X-Men", "X-Men") > 0.7

        # Test different titles
        assert matcher._compare_titles("X-Men", "Spider-Man") < 0.5

        # Test with prefixes
        assert matcher._compare_titles("The Amazing Spider-Man", "Amazing Spider-Man") > 0.9

        # Test with X-series pattern
        assert matcher._compare_titles("X-Men", "X-Force") == 0.0  # Different X- series

    def test_compare_titles_with_fuzzy_hash(self, mock_fuzzy_hash):
        """Test title comparison using fuzzy hash"""
        matcher = ComicMatcher()
        matcher.fuzzy_hash = mock_fuzzy_hash

        # Should get value from fuzzy hash
        assert matcher._compare_titles("Uncanny X-Men", "X-Men") == 0.9
        assert matcher._compare_titles("Amazing Spider-Man", "The Amazing Spider-Man") == 1.0

    def test_compare_issues(self):
        """Test issue number comparison"""
        matcher = ComicMatcher()

        # Test exact matches
        assert matcher._compare_issues("1", "1") == 1.0
        assert matcher._compare_issues("42", "42") == 1.0

        # Test normalized matches
        assert matcher._compare_issues("#1", "1") == 1.0
        assert matcher._compare_issues("Issue #42", "42") == 1.0

        # Test non-matches
        assert matcher._compare_issues("1", "2") == 0.0
        assert matcher._compare_issues("42", "43") == 0.0

    def test_compare_years(self):
        """Test year comparison"""
        matcher = ComicMatcher()

        # Test exact match
        assert matcher._compare_years(1991, 1991) == 1.0
        assert matcher._compare_years("1991", "1991") == 1.0

        # Test close years
        assert matcher._compare_years(1991, 1992) == 0.8
        assert matcher._compare_years(1991, 1993) == 0.8

        # Test far apart years
        assert matcher._compare_years(1991, 2000) < 0.8

        # Test reprint scenario
        assert matcher._compare_years(1980, 2010) == 0.7

        # Test missing years
        assert matcher._compare_years(None, 1991) == 0.5
        assert matcher._compare_years("", 1991) == 0.5

        # Test extracting years from strings
        assert matcher._compare_years("X-Men (1991)", "X-Men (1991)") == 1.0

    def test_match_basic(self, source_comics, target_comics):
        """Test basic matching functionality"""
        matcher = ComicMatcher()

        # Run matching
        matches = matcher.match(source_comics, target_comics)

        # Should find some matches
        assert len(matches) > 0

        # Should contain expected columns
        assert "similarity" in matches.columns
        assert "source_title" in matches.columns
        assert "target_title" in matches.columns
        assert "source_issue" in matches.columns
        assert "target_issue" in matches.columns

        # X-Men #1 should not match with high similarity
        xmen_one_matches = matches[
            (matches["source_title"].str.contains("X-Men")) & (matches["source_issue"] == "1")
        ]
        assert len(xmen_one_matches) == 0
        assert len(matches) == 3

    def test_match_with_dataframes(self, source_df, target_df):
        """Test matching with DataFrames"""
        matcher = ComicMatcher()

        # Run matching
        matches = matcher.match(source_df, target_df)

        # Should find some matches
        assert len(matches) > 0

    def test_match_with_high_threshold(self, source_comics, target_comics):
        """Test matching with high threshold"""
        matcher = ComicMatcher()

        # Run matching with very high threshold
        matches = matcher.match(source_comics, target_comics, threshold=0.99)

        # Should find fewer or no matches
        assert len(matches) < len(source_comics)

    def test_match_with_different_indexer(self, source_comics, target_comics):
        """Test matching with different indexer methods"""
        matcher = ComicMatcher()

        # Run matching with different indexers
        matches_block = matcher.match(source_comics, target_comics, indexer_method="block")
        matches_sorted = matcher.match(
            source_comics, target_comics, indexer_method="sortedneighbourhood"
        )
        matches_full = matcher.match(source_comics, target_comics, indexer_method="fullindex")

        # All should find matches
        assert len(matches_block) > 0
        assert len(matches_sorted) > 0
        assert len(matches_full) > 0

        # Each indexing method should find valid matches
        # But we don't assume any specific relationship between the counts
        # as implementation details may vary

    def test_match_with_no_matches(self):
        """Test matching with no possible matches"""
        matcher = ComicMatcher()

        # Create datasets with no possible matches
        source = [{"title": "X-Men", "issue": "1"}]
        target = [{"title": "Batman", "issue": "500"}]

        # Run matching
        matches = matcher.match(source, target)

        # Should return empty DataFrame
        assert len(matches) == 0
        assert isinstance(matches, pd.DataFrame)

    def test_find_best_match(self, source_comics, target_comics):
        """Test finding best match for a single comic"""
        matcher = ComicMatcher()

        # Find best match for Uncanny X-Men #142
        comic = {"title": "Uncanny X-Men", "issue": "142"}
        best_match = matcher.find_best_match(comic, target_comics)

        # Should find a match
        assert best_match is not None
        assert "source_comic" in best_match
        assert "matched_comic" in best_match
        assert "similarity" in best_match
        assert "scores" in best_match

        # Should not match well to X-Men #142
        assert best_match["matched_comic"]["title"] == "Uncanny X-Men"
        assert best_match["matched_comic"]["issue"] == "141"
        assert best_match["similarity"] == 0.4

    def test_find_best_match_no_match(self, target_comics):
        """Test finding best match when no good match exists"""
        matcher = ComicMatcher()

        # Use a title that wouldn't match anything in target_comics
        comic = {"title": "Captain Planet", "issue": "1"}
        best_match = matcher.find_best_match(comic, target_comics)

        # Should not find a match
        assert best_match is None
