"""
Core comic book entity matching functionality
"""

import re
import json
import logging
import os
from typing import Any, Callable, Dict, List, Set, Tuple, Union, Optional

import jellyfish
import pandas as pd
import recordlinkage

from .parser import ComicTitleParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComicMatcher:
    """
    Entity resolution system for comic book titles
    
    Uses recordlinkage toolkit to match comic books from different sources
    with specialized comparison methods for comic titles.
    """
    
    def __init__(self, 
                 cache_dir: str = ".cache", 
                 fuzzy_hash_path: Optional[str] = None):
        """
        Initialize the comic matcher
        
        Args:
            cache_dir: Directory to store cache files
            fuzzy_hash_path: Path to pre-computed fuzzy hash JSON file
        """
        self.parser = ComicTitleParser()
        self.cache_dir = cache_dir
        self._ensure_cache_dir()
        
        # Initialize fuzzy hash from file if provided
        self.fuzzy_hash = {}
        if fuzzy_hash_path and os.path.exists(fuzzy_hash_path):
            try:
                with open(fuzzy_hash_path, 'r') as f:
                    self.fuzzy_hash = json.load(f)
                logger.info(f"Loaded {len(self.fuzzy_hash)} pre-computed fuzzy matches")
            except Exception as e:
                logger.warning(f"Error loading fuzzy hash file: {e}")
        
        # Cache for parsed titles
        self._title_cache = {}
    
    def _ensure_cache_dir(self) -> None:
        """Create cache directory if it doesn't exist"""
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _prepare_dataframe(self, 
                           comics: Union[List[Dict[str, Any]], pd.DataFrame],
                           source_name: str) -> pd.DataFrame:
        """
        Convert comics data to a standardized DataFrame
        
        Args:
            comics: List of comic dictionaries or DataFrame
            source_name: Name of the data source (for tracking)
            
        Returns:
            DataFrame with standardized columns
        """
        if isinstance(comics, list):
            df = pd.DataFrame(comics)
        else:
            df = comics.copy()
            
        # Ensure required columns exist
        required_columns = ['title', 'issue']
        for col in required_columns:
            if col not in df.columns:
                # Try to map from alternative column names
                alt_columns = {
                    'title': ['name', 'comic_name', 'series'],
                    'issue': ['issue_number', 'number', 'issue_num']
                }
                
                for alt in alt_columns.get(col, []):
                    if alt in df.columns:
                        df[col] = df[alt]
                        break
                else:
                    # If still missing, create empty column
                    df[col] = ""
        
        # Add source column
        df['source'] = source_name
        
        # Ensure index is unique
        if not df.index.is_unique:
            # Add sequential index if not unique
            df = df.reset_index(drop=True)
        
        # Parse titles and extract structured components
        parsed_components = df['title'].apply(self.parser.parse)
        
        for component in ['main_title', 'volume', 'year', 'subtitle', 'special', 'clean_title']:
            df[f'parsed_{component}'] = parsed_components.apply(lambda x: x.get(component, ''))
        
        # Extract and normalize issue numbers
        if 'issue' in df.columns:
            df['normalized_issue'] = df['issue'].astype(str).apply(self.parser.extract_issue_number)
        
        return df
    
    def _clean_title_for_hash(self, title: str) -> str:
        """Clean a title for fuzzy hash lookup"""
        if not isinstance(title, str):
            return ""
            
        # Similar cleaning approach to fuzzy_hash.py
        banned_terms = [
            "marvel", "comics", "vol", "comic", "book", "direct", "edition", 
            "newstand", "variant", "polybagged", "sealed", "foil", 
            "epilogue", "  ", "newsstand", "vf", "nm", "condition", "unread"
        ]
        separators = ["::", "("]
        
        title = title.lower()
        
        # Split on separators
        for separator in separators:
            if separator in title:
                title = title.split(separator)[0]
        
        # Remove banned terms
        for term in banned_terms:
            if term in title:
                title = title.replace(term, "")
        
        # Remove special characters and numbers
        title = re.sub(r"[^\w\s]|[\d]", "", title).strip().lower()
        return title
    
    def _compare_titles(self, title1: str, title2: str) -> float:
        """
        Compare two comic titles with specialized comic matching logic
        
        Args:
            title1: First title
            title2: Second title
            
        Returns:
            Similarity score between 0 and 1
        """
        # Check fuzzy hash for pre-computed similarity
        if self.fuzzy_hash:
            # Clean both titles for hash lookup
            hash_key1 = self._clean_title_for_hash(title1)
            hash_key2 = self._clean_title_for_hash(title2)
            
            # Check hash in both directions
            key1 = f"{hash_key1}|{hash_key2}"
            key2 = f"{hash_key2}|{hash_key1}"
            
            if key1 in self.fuzzy_hash:
                return self.fuzzy_hash[key1]
            if key2 in self.fuzzy_hash:
                return self.fuzzy_hash[key2]
        
        # Clean titles by removing years, volume info, etc.
        clean1 = self.parser.parse(title1)['clean_title']
        clean2 = self.parser.parse(title2)['clean_title']
        
        # Short-circuit: exact match on cleaned titles
        if clean1 == clean2:
            return 1.0
        
        # Extract X-series identifiers (X-Men, X-Force, etc.)
        x_pattern = re.compile(r'x-[a-z]+')
        x_matches1 = x_pattern.findall(clean1)
        x_matches2 = x_pattern.findall(clean2)
        
        # If both have different X- titles, they're different series
        if x_matches1 and x_matches2 and x_matches1[0] != x_matches2[0]:
            return 0.0
            
        # Handle common prefixes
        prefixes = ['the', 'uncanny', 'all-new', 'all new', 'amazing', 'spectacular']
        for prefix in prefixes:
            prefix_pattern = re.compile(r'^' + re.escape(prefix) + r'\s+', re.IGNORECASE)
            if prefix_pattern.match(clean1) and not prefix_pattern.match(clean2):
                clean1 = prefix_pattern.sub('', clean1)
            if prefix_pattern.match(clean2) and not prefix_pattern.match(clean1):
                clean2 = prefix_pattern.sub('', clean2)
        
        # Calculate Jaro-Winkler similarity
        return jellyfish.jaro_winkler_similarity(clean1, clean2)
    
    def _compare_issues(self, issue1: str, issue2: str) -> float:
        """
        Compare issue numbers
        
        Args:
            issue1: First issue number
            issue2: Second issue number
            
        Returns:
            1.0 if identical, 0.0 otherwise
        """
        # Normalize issue numbers
        norm1 = self.parser.extract_issue_number(str(issue1))
        norm2 = self.parser.extract_issue_number(str(issue2))
        
        # Compare normalized numbers
        if norm1 and norm2 and norm1 == norm2:
            return 1.0
        
        return 0.0
    
    def _compare_years(self, year1: Union[str, int], year2: Union[str, int]) -> float:
        """
        Compare publication years
        
        Args:
            year1: First year
            year2: Second year
            
        Returns:
            Similarity score between 0 and 1
        """
        # Extract years if strings
        try:
            y1 = int(year1) if year1 else None
            y2 = int(year2) if year2 else None
        except (ValueError, TypeError):
            # Try to extract year from string
            y1_match = re.search(r'\b(19|20)\d{2}\b', str(year1))
            y2_match = re.search(r'\b(19|20)\d{2}\b', str(year2))
            
            y1 = int(y1_match.group(0)) if y1_match else None
            y2 = int(y2_match.group(0)) if y2_match else None
        
        # If either year is missing, return neutral score
        if y1 is None or y2 is None:
            return 0.5
        
        # Exact match
        if y1 == y2:
            return 1.0
        
        # Within 2 years
        if abs(y1 - y2) <= 2:
            return 0.8
        
        # Check for reprint scenario (original + modern reprint)
        classic_decades = [1960, 1970, 1980, 1990]
        if ((y1 >= 2000 and any(decade <= y2 < decade + 10 for decade in classic_decades)) or
            (y2 >= 2000 and any(decade <= y1 < decade + 10 for decade in classic_decades))):
            return 0.7
        
        # Different eras
        return 0.0
    
    def match(self, 
              source_comics: Union[List[Dict[str, Any]], pd.DataFrame],
              target_comics: Union[List[Dict[str, Any]], pd.DataFrame],
              threshold: float = 0.7,
              indexer_method: str = 'block') -> pd.DataFrame:
        """
        Match comics from source to target
        
        Args:
            source_comics: Comics to match (list of dicts or DataFrame)
            target_comics: Comics to match against (list of dicts or DataFrame)
            threshold: Matching threshold (0-1)
            indexer_method: Blocking method ('block', 'sortedneighbourhood', 'fullindex')
            
        Returns:
            DataFrame with matched comics
        """
        # Prepare dataframes
        df_source = self._prepare_dataframe(source_comics, 'source')
        df_target = self._prepare_dataframe(target_comics, 'target')
        
        logger.info(f"Matching {len(df_source)} source comics against {len(df_target)} target comics")
        
        # Create indexer for blocking
        indexer = recordlinkage.Index()
        
        if indexer_method == 'fullindex':
            # Full index (compare all pairs - very slow for large datasets)
            indexer.full()
        elif indexer_method == 'sortedneighbourhood':
            # Sorted neighbourhood indexing
            indexer.sortedneighbourhood('parsed_main_title', window=3)
            if 'normalized_issue' in df_source.columns and 'normalized_issue' in df_target.columns:
                indexer.sortedneighbourhood('normalized_issue', window=1)
        else:
            # Default: blocking
            # Block on first character of title (efficient first pass)
            indexer.block(lambda x: x['parsed_main_title'].str[0:1])
            
            # Block on issue number if available
            if 'normalized_issue' in df_source.columns and 'normalized_issue' in df_target.columns:
                indexer.block('normalized_issue')
        
        # Generate candidate pairs
        candidate_pairs = indexer.index(df_source, df_target)
        logger.info(f"Generated {len(candidate_pairs)} candidate pairs")
        
        # Create comparison object
        compare = recordlinkage.Compare()
        
        # Add comparison methods
        compare.add(lambda s1, s2: self._compare_titles(s1, s2), 'title', 'title', label='title_sim')
        compare.add(lambda s1, s2: self._compare_issues(s1, s2), 'issue', 'issue', label='issue_match')
        
        # Add year comparison if available
        if 'parsed_year' in df_source.columns and 'parsed_year' in df_target.columns:
            compare.add(lambda y1, y2: self._compare_years(y1, y2), 'parsed_year', 'parsed_year', label='year_sim')
        
        # Compute feature vectors
        features = compare.compute(candidate_pairs, df_source, df_target)
        
        # Calculate overall similarity score
        weights = {
            'title_sim': 0.5,
            'issue_match': 0.5,
            'year_sim': 0.2  # Lower weight since year might be missing
        }
        
        # Only include available columns
        used_weights = {col: weights[col] for col in features.columns if col in weights}
        total_weight = sum(used_weights.values())
        
        # Calculate weighted similarity score
        if total_weight > 0:
            scores = sum(features[col] * weight for col, weight in used_weights.items()) / total_weight
        else:
            scores = features.mean(axis=1)
        
        # Filter matches based on threshold
        matches_idx = scores[scores >= threshold].index
        logger.info(f"Found {len(matches_idx)} matches above threshold {threshold}")
        
        # Create DataFrame with match results
        if not matches_idx.empty:
            # Get matched pairs
            matched_pairs = pd.DataFrame(index=matches_idx)
            matched_pairs['similarity'] = scores[matches_idx]
            
            # Expand multi-index to columns
            matched_pairs['source_idx'] = matched_pairs.index.get_level_values(0)
            matched_pairs['target_idx'] = matched_pairs.index.get_level_values(1)
            
            # Include detailed match scores
            for col in features.columns:
                matched_pairs[col] = features.loc[matches_idx, col]
            
            # Join with source and target data
            matched_pairs = matched_pairs.merge(
                df_source, left_on='source_idx', right_index=True, suffixes=('', '_source')
            )
            matched_pairs = matched_pairs.merge(
                df_target, left_on='target_idx', right_index=True, suffixes=('', '_target')
            )
            
            # Rename columns for clarity
            matched_pairs = matched_pairs.rename(columns={
                'title': 'source_title',
                'issue': 'source_issue',
                'title_target': 'target_title',
                'issue_target': 'target_issue'
            })
            
            return matched_pairs
        else:
            return pd.DataFrame()  # Return empty DataFrame if no matches
    
    def find_best_match(self, comic: Dict[str, Any], candidates: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Find the best match for a single comic from candidates
        
        Args:
            comic: Comic to match
            candidates: List of potential match candidates
            
        Returns:
            Best match with similarity score or None if no match found
        """
        # Convert to dataframes for the matcher
        comic_df = pd.DataFrame([comic])
        candidates_df = pd.DataFrame(candidates)
        
        # Run match
        matches = self.match(comic_df, candidates_df, threshold=0.5)
        
        # Return best match
        if not matches.empty:
            best_match_idx = matches['similarity'].idxmax()
            best_match = matches.loc[best_match_idx].to_dict()
            
            # Format result
            result = {
                'source_comic': comic,
                'matched_comic': candidates[int(best_match['target_idx'])],
                'similarity': best_match['similarity'],
                'scores': {
                    'title_similarity': best_match.get('title_sim', 0),
                    'issue_match': best_match.get('issue_match', 0),
                    'year_similarity': best_match.get('year_sim', 0)
                }
            }
            return result
        
        return None
    
    def save_fuzzy_hash(self, path: str = "fuzzy_hash.json") -> None:
        """
        Save the current fuzzy hash to file
        
        Args:
            path: Path to save the JSON file
        """
        with open(path, 'w') as f:
            json.dump(self.fuzzy_hash, f)
        logger.info(f"Saved {len(self.fuzzy_hash)} fuzzy hash entries to {path}")
    
    def update_fuzzy_hash(self, title1: str, title2: str, similarity: float) -> None:
        """
        Update the fuzzy hash with a new title pair
        
        Args:
            title1: First title
            title2: Second title
            similarity: Similarity score (0-1)
        """
        hash_key1 = self._clean_title_for_hash(title1)
        hash_key2 = self._clean_title_for_hash(title2)
        
        if hash_key1 and hash_key2:
            key = f"{hash_key1}|{hash_key2}"
            self.fuzzy_hash[key] = similarity
