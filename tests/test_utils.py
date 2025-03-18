"""
Tests for the comic_matcher.utils module
"""

from unittest.mock import mock_open, patch

import pandas as pd
import pytest

from comic_matcher.utils import (
    export_matches_to_csv,
    extract_year,
    find_duplicates,
    generate_series_key,
    load_comics_from_csv,
    load_comics_from_json,
    normalize_publisher,
    preprocess_comic_title,
)


class TestUtils:
    """Test cases for utils functions"""

    def test_extract_year(self):
        """Test extracting year from different formats"""
        # Test direct year
        assert extract_year(2023) == 2023
        assert extract_year("2023") == 2023

        # Test with date strings
        assert extract_year("Jan 01 2023") == 2023
        assert extract_year("2023-01-01") == 2023
        assert extract_year("01/01/2023") == 2023

        # Test with year in text
        assert extract_year("X-Men (1991)") == 1991
        assert extract_year("Published in 2005") == 2005

        # Test with no year
        assert extract_year(None) is None
        assert extract_year("") is None
        assert extract_year("No year here") is None

    def test_normalize_publisher(self):
        """Test normalizing publisher names"""
        # Test direct matches
        assert normalize_publisher("marvel comics") == "marvel"
        assert normalize_publisher("dc comics") == "dc"
        assert normalize_publisher("image comics") == "image"

        # Test variations
        assert normalize_publisher("Marvel Entertainment") == "marvel"
        assert normalize_publisher("DC Entertainment") == "dc"

        # Test partial matches
        assert normalize_publisher("Marvel's Comics Division") == "marvel"
        assert normalize_publisher("Published by DC") == "dc"

        # Test unknown publisher
        assert normalize_publisher("Unknown Comics") == "unknown comics"

        # Test empty input
        assert normalize_publisher("") == ""
        assert normalize_publisher(None) == ""
        assert normalize_publisher(123) == ""

    @patch("pandas.read_csv")
    def test_load_comics_from_csv(self, mock_read_csv):
        """Test loading comics from CSV file"""
        # Mock DataFrame result
        mock_df = pd.DataFrame({"title": ["X-Men", "Spider-Man"], "issue": [1, 300]})
        mock_read_csv.return_value = mock_df

        # Call function
        result = load_comics_from_csv("dummy_path.csv")

        # Check results
        assert isinstance(result, pd.DataFrame)
        assert "title" in result.columns
        assert "issue" in result.columns
        assert result["issue"].dtype == "object"  # Should convert issue to string

        # Check with custom column names
        mock_df_with_name = pd.DataFrame({"name": ["X-Men", "Spider-Man"], "number": [1, 300]})
        mock_read_csv.return_value = mock_df_with_name

        result = load_comics_from_csv("dummy_path.csv", title_col="name", issue_col="number")
        assert isinstance(result, pd.DataFrame)
        assert "name" in result.columns
        assert "number" in result.columns

        # Test fallback to 'name' column
        mock_df_name_only = pd.DataFrame({"name": ["X-Men", "Spider-Man"], "issue": [1, 300]})
        mock_read_csv.return_value = mock_df_name_only

        result = load_comics_from_csv("dummy_path.csv")  # default title_col="title"
        assert "title" in result.columns
        assert result["title"].equals(mock_df_name_only["name"])

    @patch("pandas.read_csv")
    def test_load_comics_from_csv_missing_columns(self, mock_read_csv):
        """Test loading CSV with missing required columns"""
        # Mock DataFrame missing title column
        mock_df = pd.DataFrame({"issue": [1, 300], "publisher": ["Marvel", "Marvel"]})
        mock_read_csv.return_value = mock_df

        # Should raise ValueError for missing title column
        with pytest.raises(ValueError, match="Title column 'title' not found"):
            load_comics_from_csv("dummy_path.csv")

    @patch("pandas.read_csv", side_effect=Exception("CSV error"))
    def test_load_comics_from_csv_error(self, mock_read_csv):
        """Test handling errors when loading CSV"""
        # Should return empty DataFrame and log error
        with patch("logging.error") as mock_log:
            result = load_comics_from_csv("bad_path.csv")
            assert len(result) == 0
            assert isinstance(result, pd.DataFrame)
            mock_log.assert_called_once()

    @patch("pandas.DataFrame.to_csv")
    def test_export_matches_to_csv(self, mock_to_csv):
        """Test exporting matches to CSV file"""
        # Create sample matches
        matches = pd.DataFrame(
            {
                "source_title": ["X-Men", "Spider-Man"],
                "target_title": ["Uncanny X-Men", "Amazing Spider-Man"],
                "similarity": [0.9, 0.95],
            }
        )

        # Call function
        with patch("logging.info") as mock_log:
            export_matches_to_csv(matches, "output.csv")

            # Check output
            mock_to_csv.assert_called_once_with("output.csv", index=False)
            mock_log.assert_called_once()

    @patch("pandas.DataFrame.to_csv", side_effect=Exception("CSV error"))
    def test_export_matches_to_csv_error(self, mock_to_csv):
        """Test handling errors when exporting CSV"""
        # Create sample matches
        matches = pd.DataFrame(
            {
                "source_title": ["X-Men", "Spider-Man"],
                "target_title": ["Uncanny X-Men", "Amazing Spider-Man"],
                "similarity": [0.9, 0.95],
            }
        )

        # Call function
        with patch("logging.error") as mock_log:
            export_matches_to_csv(matches, "bad_path.csv")
            mock_log.assert_called_once()

    def test_find_duplicates(self):
        """Test finding duplicate comics in a dataset"""
        # Create sample comics with duplicates
        comics = pd.DataFrame(
            {
                "title": [
                    "X-Men",
                    "Uncanny X-Men",
                    "Spider-Man",
                    "Amazing Spider-Man",
                    "Batman",
                ],
                "issue": ["1", "1", "300", "300", "500"],
            }
        )

        # Find duplicates
        duplicates = find_duplicates(comics)

        # Should find 2 pairs of duplicates
        assert len(duplicates) == 2

        # Check content of results
        assert "comic1_title" in duplicates.columns
        assert "comic2_title" in duplicates.columns
        assert "comic1_issue" in duplicates.columns
        assert "comic2_issue" in duplicates.columns

        # Empty dataset should return empty result
        empty_df = pd.DataFrame(columns=["title", "issue"])
        empty_result = find_duplicates(empty_df)
        assert len(empty_result) == 0
        assert isinstance(empty_result, pd.DataFrame)

    def test_preprocess_comic_title(self):
        """Test preprocessing comic titles for matching"""
        # Test basic cleaning
        assert preprocess_comic_title("Uncanny X-Men (1991) #142") == "uncanny x men"

        # Test with volume and special characters
        assert preprocess_comic_title("Amazing Spider-Man Vol. 2 #1!") == "amazing spider man"

        # Test with issue indicators
        assert preprocess_comic_title("X-Men Issue 10") == "x men"

        # Test with empty input
        assert preprocess_comic_title("") == ""
        assert preprocess_comic_title(None) == ""
        assert preprocess_comic_title(123) == ""

    @patch(
        "pathlib.Path.open",
        new_callable=mock_open,
        read_data='{"comics": [{"title": "X-Men", "issue": "1"}]}',
    )
    def test_load_comics_from_json(self, mock_file):
        """Test loading comics from JSON file"""
        # Call function
        result = load_comics_from_json("dummy_path.json")

        # Check results
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["title"] == "X-Men"
        assert result[0]["issue"] == "1"

        # Test with direct list
        with patch(
            "pathlib.Path.open",
            new_callable=mock_open,
            read_data='[{"title": "X-Men", "issue": "1"}]',
        ):
            result = load_comics_from_json("list_path.json")
            assert isinstance(result, list)
            assert len(result) == 1

        # Test with results key
        with patch(
            "pathlib.Path.open",
            new_callable=mock_open,
            read_data='{"results": [{"title": "X-Men", "issue": "1"}]}',
        ):
            result = load_comics_from_json("results_path.json")
            assert isinstance(result, list)
            assert len(result) == 1

        # Test with flat dictionary
        with patch(
            "pathlib.Path.open",
            new_callable=mock_open,
            read_data='{"1": {"title": "X-Men", "issue": "1"}}',
        ):
            result = load_comics_from_json("dict_path.json")
            assert isinstance(result, list)
            assert len(result) == 1

    @patch("pathlib.Path.open", side_effect=Exception("JSON error"))
    def test_load_comics_from_json_error(self, mock_file):
        """Test handling errors when loading JSON"""
        # Should return empty list and log error
        with patch("logging.error") as mock_log:
            result = load_comics_from_json("bad_path.json")
            assert result == []
            mock_log.assert_called_once()

    def test_generate_series_key(self):
        """Test generating canonical series keys"""
        # Test basic series
        assert generate_series_key("X-Men").lower() == "xmen"

        # Test with Spider-Man series - full name, not just 'amazing'
        assert generate_series_key("Amazing Spider-Man").lower() == "amazing spiderman"

        # Test with X- pattern
        assert generate_series_key("Uncanny X-Men").lower() == "xmen"
        assert generate_series_key("X-Force").lower() == "xmen"

        # Test with common articles
        assert generate_series_key("The Avengers") == "avengers"

        # Test with multi-word titles - should retain the full name
        assert generate_series_key("New Mutants") == "new mutants"

        # Test with empty input
        assert generate_series_key("") == ""
        assert generate_series_key(None) == ""
