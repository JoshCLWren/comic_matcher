"""
Tests for the comic_matcher.cli module
"""

import argparse
from unittest.mock import MagicMock, patch

import pandas as pd

from comic_matcher.cli import load_data, main, parse_title, run_matcher, setup_logging


class TestCLI:
    """Test cases for CLI functions"""

    def test_setup_logging(self):
        """Test setting up logging with different levels"""
        with patch("logging.basicConfig") as mock_logging:
            # Test with INFO level
            setup_logging("INFO")
            mock_logging.assert_called_once()

            # Reset mock and test with DEBUG level
            mock_logging.reset_mock()
            setup_logging("DEBUG")
            mock_logging.assert_called_once()

            # Reset mock and test with invalid level (should default to INFO)
            mock_logging.reset_mock()
            setup_logging("INVALID_LEVEL")
            mock_logging.assert_called_once()

    @patch("pathlib.Path.exists")
    @patch("comic_matcher.cli.load_comics_from_csv")
    @patch("comic_matcher.cli.load_comics_from_json")
    def test_load_data(self, mock_load_json, mock_load_csv, mock_exists):
        """Test loading data from different file types"""
        # Setup mocks
        mock_exists.return_value = True
        mock_load_csv.return_value = pd.DataFrame({"title": ["X-Men"]})
        mock_load_json.return_value = [{"title": "X-Men"}]

        # Test loading CSV
        result = load_data("data.csv")
        mock_load_csv.assert_called_once_with("data.csv")
        assert isinstance(result, pd.DataFrame)

        # Test loading JSON
        result = load_data("data.json")
        mock_load_json.assert_called_once_with("data.json")
        assert isinstance(result, list)

        # Test with file not found
        mock_exists.return_value = False
        with patch("logging.error") as mock_log:
            result = load_data("nonexistent.csv")
            assert result == []
            mock_log.assert_called_once()

        # Test with unsupported file format
        mock_exists.return_value = True
        with patch("logging.error") as mock_log:
            result = load_data("data.txt")
            assert result == []
            mock_log.assert_called_once()

    @patch("comic_matcher.cli.load_data")
    @patch("comic_matcher.cli.ComicMatcher")
    def test_run_matcher(self, mock_matcher_class, mock_load_data):
        """Test running the matcher with command-line arguments"""
        # Setup mocks
        mock_matcher_instance = MagicMock()
        mock_matcher_class.return_value = mock_matcher_instance

        source_data = [{"title": "X-Men", "issue": "1"}]
        target_data = [{"title": "Uncanny X-Men", "issue": "1"}]
        mock_load_data.side_effect = [source_data, target_data]

        # Setup matches result
        matches = pd.DataFrame(
            {
                "source_title": ["X-Men"],
                "target_title": ["Uncanny X-Men"],
                "similarity": [0.9],
            }
        )
        mock_matcher_instance.match.return_value = matches

        # Create args
        args = argparse.Namespace(
            source="source.csv",
            target="target.csv",
            threshold=0.7,
            indexer="block",
            fuzzy_hash=None,
            output="output.csv",
            verbose=True,
        )

        # Run function
        with patch("builtins.print") as mock_print:
            run_matcher(args)

            # Check function calls
            mock_load_data.assert_any_call("source.csv")
            mock_load_data.assert_any_call("target.csv")
            mock_matcher_class.assert_called_once()
            mock_matcher_instance.match.assert_called_once_with(
                source_data, target_data, threshold=0.7, indexer_method="block"
            )

            # Should print results
            assert mock_print.call_count >= 3  # At least summary and one sample match

    @patch("comic_matcher.cli.load_data")
    @patch("comic_matcher.cli.ComicMatcher")
    def test_run_matcher_with_empty_results(self, mock_matcher_class, mock_load_data):
        """Test running the matcher with no results"""
        # Setup mocks
        mock_matcher_instance = MagicMock()
        mock_matcher_class.return_value = mock_matcher_instance

        source_data = [{"title": "X-Men", "issue": "1"}]
        target_data = [{"title": "Batman", "issue": "1"}]
        mock_load_data.side_effect = [source_data, target_data]

        # Empty matches result
        mock_matcher_instance.match.return_value = pd.DataFrame()

        # Create args
        args = argparse.Namespace(
            source="source.csv",
            target="target.csv",
            threshold=0.7,
            indexer="block",
            fuzzy_hash=None,
            output="output.csv",
            verbose=True,
        )

        # Run function
        with patch("builtins.print") as mock_print:
            run_matcher(args)

            # Should print no matches message
            mock_print.assert_called_with("No matches found")

    @patch("comic_matcher.cli.load_data", return_value=[])
    def test_run_matcher_with_failed_data_load(self, mock_load_data):
        """Test running the matcher when data loading fails"""
        # Create args
        args = argparse.Namespace(
            source="source.csv",
            target="target.csv",
            threshold=0.7,
            indexer="block",
            fuzzy_hash=None,
            output="output.csv",
            verbose=True,
        )

        # Run function
        with patch("logging.error") as mock_log:
            run_matcher(args)

            # Should log error
            mock_log.assert_called_once()

    @patch("comic_matcher.cli.ComicTitleParser")
    def test_parse_title(self, mock_parser_class):
        """Test parsing a title from command line"""
        # Setup mock
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser

        # Setup parse result
        mock_parser.parse.return_value = {
            "main_title": "X-Men",
            "volume": "2",
            "year": "1991",
            "subtitle": "",
            "special": "",
            "clean_title": "x-men",
        }

        # Create args
        args = argparse.Namespace(title="X-Men Vol. 2 (1991)")

        # Run function
        with patch("builtins.print") as mock_print:
            parse_title(args)

            # Check function calls
            mock_parser.parse.assert_called_once_with("X-Men Vol. 2 (1991)")

            # Should print title and components
            assert mock_print.call_count >= 3  # Title and at least one component

    @patch("argparse.ArgumentParser.parse_args")
    @patch("comic_matcher.cli.run_matcher")
    @patch("comic_matcher.cli.parse_title")
    @patch("comic_matcher.cli.setup_logging")
    def test_main_match_command(
        self, mock_setup_logging, mock_parse_title, mock_run_matcher, mock_parse_args
    ):
        """Test main function with match command"""
        # Setup args
        args = argparse.Namespace(
            command="match",
            log_level="INFO",
            source="source.csv",
            target="target.csv",
            threshold=0.7,
            indexer="block",
            fuzzy_hash=None,
            output="output.csv",
            verbose=True,
        )
        mock_parse_args.return_value = args

        # Run function
        main()

        # Check function calls
        mock_setup_logging.assert_called_once_with("INFO")
        mock_run_matcher.assert_called_once_with(args)
        mock_parse_title.assert_not_called()

    @patch("argparse.ArgumentParser.parse_args")
    @patch("comic_matcher.cli.run_matcher")
    @patch("comic_matcher.cli.parse_title")
    @patch("comic_matcher.cli.setup_logging")
    def test_main_parse_command(
        self, mock_setup_logging, mock_parse_title, mock_run_matcher, mock_parse_args
    ):
        """Test main function with parse command"""
        # Setup args
        args = argparse.Namespace(command="parse", log_level="INFO", title="X-Men Vol. 2 (1991)")
        mock_parse_args.return_value = args

        # Run function
        main()

        # Check function calls
        mock_setup_logging.assert_called_once_with("INFO")
        mock_parse_title.assert_called_once_with(args)
        mock_run_matcher.assert_not_called()

    @patch("argparse.ArgumentParser.parse_args")
    @patch("argparse.ArgumentParser.print_help")
    @patch("comic_matcher.cli.run_matcher")
    @patch("comic_matcher.cli.parse_title")
    @patch("comic_matcher.cli.setup_logging")
    def test_main_no_command(
        self,
        mock_setup_logging,
        mock_parse_title,
        mock_run_matcher,
        mock_print_help,
        mock_parse_args,
    ):
        """Test main function with no command"""
        # Setup args with no command
        args = argparse.Namespace(command=None, log_level="INFO")
        mock_parse_args.return_value = args

        # Run function
        main()

        # Check function calls
        mock_setup_logging.assert_called_once_with("INFO")
        mock_print_help.assert_called_once()
        mock_run_matcher.assert_not_called()
        mock_parse_title.assert_not_called()
