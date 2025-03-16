"""
Module for detecting and comparing team-up comic titles
"""


class TeamUpMatcher:
    """
    Handler for detecting and comparing team-up comic titles

    Team-up comics include titles with patterns like "&", "AND", "/", "VS", etc.
    This class provides methods for detecting and comparing such titles.
    """

    def __init__(self) -> None:
        """Initialize the team-up matcher with common patterns"""
        self.team_up_patterns = ["&", " and ", "/", " vs ", " versus "]

    def is_team_up(self, title: str) -> bool:
        """
        Check if a title is a team-up comic

        Args:
            title: Comic title

        Returns:
            True if title is a team-up, False otherwise
        """
        return any(pattern in title.lower() for pattern in self.team_up_patterns)

    def get_first_character(self, title: str) -> str:
        """
        Extract the first character name from a team-up title

        Args:
            title: Team-up comic title

        Returns:
            First character name or empty string if not found
        """
        title_lower = title.lower()

        # Find which team-up pattern is used
        for pattern in self.team_up_patterns:
            if pattern in title_lower:
                # Extract the part before the pattern
                return title_lower.split(pattern)[0].strip()

        return ""

    def compare(self, title1: str, title2: str) -> float:
        """
        Compare a team-up title with another title

        This specifically handles cases like "Character1 & Character2" vs "Character1"

        Args:
            title1: First title
            title2: Second title

        Returns:
            Similarity score between 0 and 1
        """
        # Check if one is a team-up and the other isn't
        is_team_up1 = self.is_team_up(title1)
        is_team_up2 = self.is_team_up(title2)

        if is_team_up1 == is_team_up2:
            # Both are team-ups or neither is, so this handler doesn't apply
            return -1.0  # Signal that this handler doesn't apply

        # Get the team-up title and the solo title
        team_title = title1 if is_team_up1 else title2
        solo_title = title2 if is_team_up1 else title1

        # Get the first character name from the team-up title
        first_character = self.get_first_character(team_title)

        if not first_character or len(first_character) < 4:
            return -1.0  # Not enough info to make a determination

        # Check if the solo title is similar to just the first character
        solo_lower = solo_title.lower()

        if first_character in solo_lower or solo_lower in first_character:
            # The solo title matches just the first character in the team-up,
            # so they're different comics (e.g., "Gambit & Bishop" vs "Gambit")
            return 0.3  # Return low similarity

        # No match pattern found
        return -1.0  # Signal that this handler doesn't apply
