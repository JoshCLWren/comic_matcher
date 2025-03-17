"""
Tests for the comic_matcher.parser module
"""

from comic_matcher.parser import ComicTitleParser


class TestComicTitleParser:
    """Test cases for ComicTitleParser"""

    def test_initialization(self):
        """Test initialization of parser"""
        parser = ComicTitleParser()
        assert hasattr(parser, "year_pattern")
        assert hasattr(parser, "volume_pattern")
        assert hasattr(parser, "issue_pattern")
        assert hasattr(parser, "common_prefixes")
        assert hasattr(parser, "special_identifiers")

    def test_parse_with_empty_input(self):
        """Test parsing empty input"""
        parser = ComicTitleParser()
        result = parser.parse("")
        assert result["main_title"] == ""
        assert result["volume"] == ""
        assert result["year"] == ""
        assert result["special"] == ""
        assert result["clean_title"] == ""

        # Also test None input
        result = parser.parse(None)
        assert result["main_title"] == ""

    def test_parse_with_year(self, sample_titles):
        """Test parsing titles with year"""
        parser = ComicTitleParser()

        # Test title with year in parentheses
        result = parser.parse("Uncanny X-Men (1981) #142")
        # The parse method should normalize the title by removing common prefixes
        assert result["main_title"] == "uncanny x-men"
        assert result["year"] == "1981"

        # Test another format
        result = parser.parse("New Mutants (1983) Annual #3")
        assert result["main_title"] == "new mutants annual"
        assert result["year"] == "1983"
        assert result["special"] == "annual"

    def test_parse_with_volume(self):
        """Test parsing titles with volume information"""
        parser = ComicTitleParser()

        # Test with "Vol."
        result = parser.parse("X-Men Vol. 2 #1")
        assert result["main_title"] == "x-men"
        assert result["volume"] == "2"

        # Test with "Volume"
        result = parser.parse("Avengers Volume 3 #1")
        assert result["main_title"] == "avengers"
        assert result["volume"] == "3"

    def test_parse_with_subtitle(self):
        """Test parsing titles with subtitles"""
        parser = ComicTitleParser()

        # Test with colon
        result = parser.parse("X-Factor (1986) #1: The Beginning")
        assert result["main_title"] == "x-factor the beginning"
        assert result["year"] == "1986"

        # Test with parentheses
        result = parser.parse("Excalibur (The Sword is Drawn)")
        assert result["main_title"] == "excalibur the sword is drawn"

    def test_parse_with_special_identifier(self):
        """Test parsing titles with special identifiers"""
        parser = ComicTitleParser()

        # Test Annual
        result = parser.parse("X-Men Annual #2")
        assert result["main_title"] == "x-men annual"
        assert result["special"] == "annual"

        # Test Giant-Size
        result = parser.parse("Giant-Size X-Men #1")
        assert result["special"] == "giant-size"
        assert result["main_title"] == "x-men giant-size"

        # Test One-Shot
        result = parser.parse("Wolverine: One-Shot")
        assert result["main_title"] == "wolverine one-shot"
        assert result["special"] == "one-shot"

    def test_extract_issue_number(self):
        """Test extracting issue numbers"""
        parser = ComicTitleParser()

        # Test basic issue number
        assert parser.extract_issue_number("1") == "1"
        assert parser.extract_issue_number("42") == "42"

        # Test with # prefix
        assert parser.extract_issue_number("#123") == "123"

        # Test with decimal
        assert parser.extract_issue_number("5.1") == "5.1"
        assert parser.extract_issue_number("#5.1") == "5.1"

        # Test from title
        assert parser.extract_issue_number("X-Men #42") == "42"

        # Test trailing issue
        assert parser.extract_issue_number("Uncanny X-Men 275") == "275"

        # Test with non-issue
        assert parser.extract_issue_number("No issue") is None

    def test_normalize_title(self):
        """Test normalizing titles with common prefixes"""
        parser = ComicTitleParser()

        # Test common prefix removal
        assert parser._normalize_title("The Avengers") == "Avengers"
        assert parser._normalize_title("Amazing Spider-Man") == "Spider-Man"

        # Test case where no prefix should be removed
        assert parser._normalize_title("Daredevil") == "Daredevil"

        # Test case where prefix is part of the name
        assert (
            parser._normalize_title("Thor") == "Thor"
        )  # Should not remove 'the' from beginning of Thor

    def test_clean_title(self):
        """Test cleaning titles for comparison"""
        parser = ComicTitleParser()

        # Test full cleaning
        clean = parser._clean_title("Uncanny X-Men (1981) #142 Vol. 2")
        assert "(1981)" not in clean
        assert "#142" not in clean
        assert "Vol. 2" not in clean
        assert "uncanny x-men" in clean.lower()

        # Test special identifiers
        clean = parser._clean_title("X-Men Annual #1")
        assert "annual" not in clean.lower()
        assert "#1" not in clean
        assert "x-men" in clean.lower()

    def test_split_title_and_subtitle(self):
        """Test splitting title and subtitle"""
        parser = ComicTitleParser()

        # Test colon separator
        main, sub = parser._split_title_and_subtitle("X-Men: Dark Phoenix Saga")
        assert main == "X-Men"
        assert sub == "Dark Phoenix Saga"

        # Test parenthetical subtitle
        main, sub = parser._split_title_and_subtitle("Excalibur (The Sword is Drawn)")
        assert main == "Excalibur"
        assert sub == "The Sword is Drawn"

        # Test no subtitle
        main, sub = parser._split_title_and_subtitle("Daredevil")
        assert main == "Daredevil"
        assert sub == ""

        # Test multiple colons (should split on first)
        main, sub = parser._split_title_and_subtitle("X-Men: First Class: Finals")
        assert main == "X-Men"
        assert sub == "First Class: Finals"
