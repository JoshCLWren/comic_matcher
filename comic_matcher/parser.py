"""
Parser module for comic book titles
"""

import re
from typing import Dict, Optional, Tuple


class ComicTitleParser:
    """Parser for extracting structured information from comic book titles"""

    def __init__(self):
        """Initialize the parser with regex patterns"""
        # Patterns for extracting various parts of a comic title
        self.year_pattern = re.compile(r'\((\d{4})\)')
        self.volume_pattern = re.compile(r'(?i)(?:vol\.?|volume)\s*(\d+)')
        self.issue_pattern = re.compile(r'#(\d+\.?\d*)')
        
        # Common prefixes in titles
        self.common_prefixes = [
            'the', 'marvels', "marvel's", 'dc', "dc's", 'uncanny', 
            'amazing', 'spectacular', 'astonishing', 'all-new', 'all new'
        ]
        
        # Special identifiers for issues
        self.special_identifiers = [
            'annual', 'special', 'one-shot', 'limited series', 
            'variant', 'director\'s cut', 'preview', 'giant-size'
        ]

    def parse(self, title: str) -> Dict[str, str]:
        """
        Parse a comic book title into structured components
        
        Args:
            title: The raw comic book title string
            
        Returns:
            Dictionary with parsed components:
                - main_title: The core series title
                - volume: Volume number if present
                - year: Publication year if present
                - subtitle: Any subtitle
                - special: Special identifiers like "Annual"
                - clean_title: Normalized version of the title
        """
        if not title or not isinstance(title, str):
            return {
                'main_title': '',
                'volume': '',
                'year': '',
                'subtitle': '',
                'special': '',
                'clean_title': ''
            }
        
        # Remove any leading/trailing whitespace
        clean_title = title.strip()
        
        # Extract year
        year = ''
        year_match = self.year_pattern.search(clean_title)
        if year_match:
            year = year_match.group(1)
            clean_title = self.year_pattern.sub('', clean_title).strip()
        
        # Extract volume
        volume = ''
        volume_match = self.volume_pattern.search(clean_title)
        if volume_match:
            volume = volume_match.group(1)
            clean_title = self.volume_pattern.sub('', clean_title).strip()
        
        # Extract special identifiers
        special = ''
        for identifier in self.special_identifiers:
            if re.search(r'(?i)\b' + re.escape(identifier) + r'\b', clean_title):
                special = identifier.lower()
                clean_title = re.sub(r'(?i)\b' + re.escape(identifier) + r'\b', '', clean_title).strip()
                break
        
        # Extract subtitle (after colon or in parentheses)
        main_title, subtitle = self._split_title_and_subtitle(clean_title)
        
        # Normalize main title
        main_title = self._normalize_title(main_title)
        
        return {
            'main_title': main_title,
            'volume': volume,
            'year': year,
            'subtitle': subtitle,
            'special': special,
            'clean_title': self._clean_title(title)  # Full normalized version
        }
    
    def _split_title_and_subtitle(self, title: str) -> Tuple[str, str]:
        """Split a title into main title and subtitle"""
        subtitle = ''
        main_title = title
        
        # Check for subtitle after colon
        if ':' in title:
            parts = title.split(':', 1)
            main_title = parts[0].strip()
            subtitle = parts[1].strip()
        # Check for subtitle in parentheses (excluding year)
        elif '(' in title and not self.year_pattern.search(title):
            match = re.search(r'(.*?)\s*\((.*?)\)', title)
            if match:
                main_title = match.group(1).strip()
                subtitle = match.group(2).strip()
                
                # Don't treat volume as subtitle
                if self.volume_pattern.match(subtitle):
                    subtitle = ''
        
        return main_title, subtitle
    
    def _normalize_title(self, title: str) -> str:
        """Normalize a title by removing common prefixes"""
        title_lower = title.lower()
        
        # Remove common prefixes
        for prefix in self.common_prefixes:
            if title_lower.startswith(prefix + ' '):
                return title[len(prefix) + 1:]
        
        return title
    
    def _clean_title(self, title: str) -> str:
        """Clean a title for comparison"""
        # Convert to lowercase
        clean = title.lower()
        
        # Remove year, volume info, special identifiers
        clean = self.year_pattern.sub('', clean)
        clean = self.volume_pattern.sub('', clean)
        
        for identifier in self.special_identifiers:
            clean = re.sub(r'(?i)\b' + re.escape(identifier) + r'\b', '', clean)
        
        # Remove issue numbers
        clean = self.issue_pattern.sub('', clean)
        
        # Remove non-essential punctuation except hyphens
        clean = re.sub(r'[^\w\s-]', ' ', clean)
        
        # Normalize whitespace
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        return clean

    def extract_issue_number(self, text: str) -> Optional[str]:
        """
        Extract issue number from string
        
        Args:
            text: String potentially containing an issue number
            
        Returns:
            Extracted issue number or None
        """
        # First check if text is already just a number
        if text and text.replace('.', '', 1).isdigit():
            return text
            
        # Try to extract from patterns like "#123" or "No. 123"
        issue_match = self.issue_pattern.search(text)
        if issue_match:
            return issue_match.group(1)
            
        # Try to extract from title format "Series Name 123"
        words = text.split()
        if words and words[-1].replace('.', '', 1).isdigit():
            return words[-1]
            
        return None
