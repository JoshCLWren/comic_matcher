"""
Integration tests for handling mismatches with special case mappings
"""

import json
import os
from pathlib import Path

import pandas as pd
import pytest

from comic_matcher.matcher import ComicMatcher


class TestMismatchIntegration:
    """
    Integration tests for the comic matcher with special case handling
    for known mismatches in the data.
    """

    @pytest.fixture
    def special_case_mappings(self):
        """Fixture with special case mappings for known problem matches"""
        return {
            # Annual patterns
            "X-Men (Annual)": "X-Men Annual",
            
            # Unlimited series
            "X-Men (Unlimited)": "X-Men Unlimited",
            
            # Academy X titles
            "New X-Men: Academy X": "New X-Men",
            
            # Completely different titles that should be treated as the same
            "X-Men: Kitty Pryde - Shadow & Flame": "X-Men: Die By The Sword",
            
            # DC vs Marvel variations
            "DC Versus Marvel/Marvel Versus DC Consumer Preview": "DC Versus Marvel",
            "DC Versus Marvel/Marvel Versus DC": "DC Versus Marvel",
            "Marvel Versus DC/DC Versus Marvel": "Marvel Versus DC",
            
            # Team-up titles
            "Badrock/Wolverine": "Badrock/Wolverine",
            "Wolverine/Doop": "Wolverine/Doop",
            
            # Yearbooks
            "New X-Men: Academy X Yearbook": "New X-Men: Academy X Yearbook",
        }

    @pytest.fixture
    def special_case_file(self, special_case_mappings, tmp_path):
        """Create a special case mapping file for testing"""
        file_path = tmp_path / "special_cases.json"
        with open(file_path, "w") as f:
            json.dump(special_case_mappings, f)
        return str(file_path)

    @pytest.fixture
    def mismatch_source_data(self):
        """Sample of source data with known mismatches"""
        return [
            {"title": "X-Men", "issue": "2000", "reading_order": "383.002"},
            {"title": "X-Men", "issue": "42", "reading_order": "415.05"},
            {"title": "X-Men", "issue": "46", "reading_order": "424.174"},
            {"title": "X-Men", "issue": "47", "reading_order": "424.175"},
            {"title": "X-Men", "issue": "48", "reading_order": "424.176"},
            {"title": "New X-Men: Academy X", "issue": "7", "reading_order": "451.011"},
            {"title": "New X-Men: Academy X", "issue": "9", "reading_order": "451.013"},
            {"title": "New X-Men: Academy X", "issue": "1", "reading_order": "461.028"},
            {"title": "X-Men: Kitty Pryde - Shadow & Flame", "issue": "1", "reading_order": "486.166"},
            {"title": "X-Men: Kitty Pryde - Shadow & Flame", "issue": "2", "reading_order": "486.167"},
            {"title": "X-Men: Kitty Pryde - Shadow & Flame", "issue": "3", "reading_order": "486.168"},
            {"title": "X-Men: Kitty Pryde - Shadow & Flame", "issue": "4", "reading_order": "486.169"},
            {"title": "X-Men: Kitty Pryde - Shadow & Flame", "issue": "5", "reading_order": "486.17"},
            {"title": "Badrock/Wolverine", "issue": "1", "reading_order": "330.015"},
            {"title": "DC Versus Marvel/Marvel Versus DC Consumer Preview", "issue": "1", "reading_order": "330.016"},
            {"title": "Marvel Versus DC/DC Versus Marvel", "issue": "2", "reading_order": "330.017"},
            {"title": "Marvel Universe Vs Wolverine", "issue": "2", "reading_order": "330.017"},
            {"title": "Marvel Versus DC/DC Versus Marvel", "issue": "3", "reading_order": "330.018"},
            {"title": "Marvel Universe Vs Wolverine", "issue": "3", "reading_order": "330.018"},
            {"title": "DC Versus Marvel/Marvel Versus DC", "issue": "4", "reading_order": "330.019"},
        ]

    @pytest.fixture
    def mismatch_target_data(self):
        """Sample of target data with known mismatches"""
        return [
            {"title": "X-Men Annual 2000", "issue": "1", "reading_order": "383.002"},
            {"title": "X-Men Unlimited", "issue": "42", "reading_order": "415.05"},
            {"title": "X-Men Unlimited", "issue": "46", "reading_order": "424.174"},
            {"title": "X-Men Unlimited", "issue": "47", "reading_order": "424.175"},
            {"title": "X-Men Unlimited", "issue": "48", "reading_order": "424.176"},
            {"title": "New X-Men", "issue": "7", "reading_order": "451.011"},
            {"title": "New X-Men", "issue": "9", "reading_order": "451.013"},
            {"title": "New X-Men: Academy X Yearbook", "issue": "1", "reading_order": "461.028"},
            {"title": "X-Men: Die By The Sword", "issue": "1", "reading_order": "486.166"},
            {"title": "X-Men: Die By The Sword", "issue": "2", "reading_order": "486.167"},
            {"title": "X-Men: Die By The Sword", "issue": "3", "reading_order": "486.168"},
            {"title": "X-Men: Die By The Sword", "issue": "4", "reading_order": "486.169"},
            {"title": "X-Men: Die By The Sword", "issue": "5", "reading_order": "486.17"},
            {"title": "Badrock/Wolverine", "issue": "1", "reading_order": "330.015"},
            {"title": "DC Versus Marvel", "issue": "1", "reading_order": "330.016"},
            {"title": "Marvel Versus DC", "issue": "2", "reading_order": "330.017"},
            {"title": "Marvel Versus DC", "issue": "2", "reading_order": "330.017"},
            {"title": "Marvel Versus DC", "issue": "3", "reading_order": "330.018"},
            {"title": "Marvel Versus DC", "issue": "3", "reading_order": "330.018"},
            {"title": "DC Versus Marvel", "issue": "4", "reading_order": "330.019"},
        ]

    def test_enhanced_matcher_with_special_cases(self, special_case_file, mismatch_source_data, mismatch_target_data):
        """
        Test an enhanced version of the matcher that uses special case mappings
        to handle known problematic matches. This represents how the matcher could
        be extended to handle these cases.
        """
        # Create a subclass of ComicMatcher that handles special cases
        class EnhancedMatcher(ComicMatcher):
            """Extended matcher with special case handling"""
            
            def __init__(self, special_case_path=None, **kwargs):
                super().__init__(**kwargs)
                self.special_case_map = {}
                if special_case_path and os.path.exists(special_case_path):
                    with open(special_case_path) as f:
                        self.special_case_map = json.load(f)
            
            def _compare_titles(self, title1, title2):
                """Override comparison to check special cases first"""
                # Check if either title is in the special case map
                if title1 in self.special_case_map and self.special_case_map[title1] == title2:
                    return 1.0  # Perfect match for special cases
                
                if title2 in self.special_case_map and self.special_case_map[title2] == title1:
                    return 1.0  # Perfect match for special cases
                
                # Handle pattern-based special cases
                for pattern, replacement in self.special_case_map.items():
                    if pattern in title1 and replacement == title2:
                        return 0.9  # High confidence for pattern matches
                    
                    if pattern in title2 and replacement == title1:
                        return 0.9  # High confidence for pattern matches
                
                # Fall back to normal comparison
                return super()._compare_titles(title1, title2)
        
        # Create an enhanced matcher with special cases
        matcher = EnhancedMatcher(special_case_path=special_case_file)
        
        # Convert test data to DataFrames
        source_df = pd.DataFrame(mismatch_source_data)
        target_df = pd.DataFrame(mismatch_target_data)
        
        # Run matching with enhanced matcher
        results = matcher.match(source_df, target_df, threshold=0.7)
        
        # Check that we successfully match previously problematic pairs
        assert len(results) > 0, "Should match some of the items with special case handling"
        
        # Check key matches
        matched_pairs = {}
        for _, row in results.iterrows():
            source_title = row["source_title"]
            target_title = row["target_title"]
            matched_pairs[(source_title, target_title)] = row["similarity"]
        
        # Key test cases to verify
        key_matches = [
            # Format: (source_title, target_title, expected_match)
            ("X-Men: Kitty Pryde - Shadow & Flame", "X-Men: Die By The Sword", True),
            ("New X-Men: Academy X", "New X-Men", True),
            ("DC Versus Marvel/Marvel Versus DC", "DC Versus Marvel", True),
            ("Marvel Versus DC/DC Versus Marvel", "Marvel Versus DC", True),
            # This one should still be rejected (completely different titles)
            ("Marvel Universe Vs Wolverine", "Marvel Versus DC", False),
        ]
        
        for source, target, expected in key_matches:
            if expected:
                assert (source, target) in matched_pairs or any(
                    s == source and t == target for (s, t) in matched_pairs
                ), f"Should match {source} with {target}"
            else:
                assert (source, target) not in matched_pairs and not any(
                    s == source and t == target for (s, t) in matched_pairs
                ), f"Should NOT match {source} with {target}"

    def test_explicit_mapping_integration(self, mismatch_source_data, mismatch_target_data):
        """
        Test using an explicit mapping process for known mismatches.
        This approach bypasses the normal matching algorithm for special cases.
        """
        # First, create direct mapping dicts from source and target data
        source_map = {
            item["reading_order"]: {
                "title": item["title"],
                "issue": item["issue"],
                "reading_order": item["reading_order"]
            }
            for item in mismatch_source_data
        }
        
        target_map = {
            item["reading_order"]: {
                "title": item["title"],
                "issue": item["issue"],
                "reading_order": item["reading_order"]
            }
            for item in mismatch_target_data
        }
        
        # Create standard matcher
        matcher = ComicMatcher()
        
        # Process each source item
        results = []
        for source_item in mismatch_source_data:
            reading_order = source_item["reading_order"]
            
            # Check if this is a known match by reading order
            if reading_order in target_map:
                # Known match - direct mapping
                results.append({
                    "source_title": source_item["title"],
                    "source_issue": source_item["issue"],
                    "target_title": target_map[reading_order]["title"],
                    "target_issue": target_map[reading_order]["issue"],
                    "similarity": 1.0,  # Force high confidence
                    "match_type": "direct_mapping"
                })
            else:
                # Unknown match - use standard matcher
                target_comics = [t for t in mismatch_target_data 
                                if t["reading_order"] != reading_order]
                
                match_result = matcher.find_best_match(source_item, target_comics)
                if match_result and match_result["similarity"] >= 0.7:
                    results.append({
                        "source_title": source_item["title"],
                        "source_issue": source_item["issue"],
                        "target_title": match_result["matched_comic"]["title"],
                        "target_issue": match_result["matched_comic"]["issue"],
                        "similarity": match_result["similarity"],
                        "match_type": "algorithm_match"
                    })
        
        # Convert results to DataFrame for analysis
        results_df = pd.DataFrame(results)
        
        # All items should be matched by reading order
        assert len(results_df) == len(mismatch_source_data), \
            "All source items should have matches through direct mapping"
        
        # All matches should be high confidence
        assert all(results_df["similarity"] >= 0.7), \
            "All matches should have high confidence"
        
        # Check key problematic pairs - they should all match via direct mapping
        problematic_pairs = [
            ("X-Men", "X-Men Annual 2000"),
            ("X-Men", "X-Men Unlimited"),
            ("New X-Men: Academy X", "New X-Men"),
            ("X-Men: Kitty Pryde - Shadow & Flame", "X-Men: Die By The Sword"),
        ]
        
        for source_title, target_title in problematic_pairs:
            mask = (results_df["source_title"] == source_title) & \
                   (results_df["target_title"] == target_title)
            
            # At least one match for this pair should exist
            assert mask.any(), f"Should have at least one match for {source_title} -> {target_title}"
            
            # All matches should be direct mapping
            assert all(results_df.loc[mask, "match_type"] == "direct_mapping"), \
                f"All matches for {source_title} -> {target_title} should be direct mapping"


class TestMismatchProcessor:
    """
    Tests for a specialized processor class that can handle mismatches
    using the reading order information.
    """
    
    @pytest.fixture
    def mismatches_file(self, tmp_path):
        """Create a CSV with mismatches data for testing"""
        mismatches_data = [
            "Reading Order,Title,Issue,Reading Order Title,Era,Best Price,Best Store,Condition,Source,Store Count,Price Range,Mismatch",
            "383.002,X-Men,2000,X-Men Annual 2000 1,Modern,$2.00,Edgewood Comics,FN,ccl,1,$2.00 - $2.00,x",
            "415.05,X-Men,42,X-Men Unlimited 42,Modern,$40.00,BlueMoon Comics,FN,ccl,1,$40.00 - $40.00,x",
            "424.174,X-Men,46,X-Men Unlimited 46,Modern,30,SCOTT.GLASS,5.0,cpg,1,$30.00 - $30.00,x",
            "424.175,X-Men,47,X-Men Unlimited 47,Modern,20.25,anthonyscomicbookart,VG/4,hip,1,$20.25 - $20.25,x",
            "424.176,X-Men,48,X-Men Unlimited 48,Modern,$2.00,Green Bay Comics,PR,ccl,1,$2.00 - $2.00,x",
            "451.011,New X-Men: Academy X,7,New X-Men 7,Modern,0.99,The Goblin's Cavern,FN,ccl,1,$0.99 - $0.99,x",
            "451.013,New X-Men: Academy X,9,New X-Men 9,Modern,$0.99,The Goblin's Cavern,VF,ccl,1,$0.99 - $0.99,x",
            "461.028,New X-Men: Academy X,1,New X-Men: Academy X Yearbook 1,Modern,$0.98,symbiotik comics,VF,ccl,1,$0.98 - $0.98,x",
            "486.166,X-Men: Kitty Pryde - Shadow & Flame,1,X-Men: Die By The Sword 1,Decimation,1.5,Nightwing55,VF,ccl,1,$1.50 - $1.50,x",
        ]
        
        file_path = tmp_path / "mismatches.csv"
        with open(file_path, "w") as f:
            f.write("\n".join(mismatches_data))
        
        return str(file_path)
    
    def test_mismatch_processor(self, mismatches_file):
        """
        Test a processor class that can load mismatch data and create mappings
        for use in the matcher.
        """
        # Define a MismatchProcessor class for handling mismatches
        class MismatchProcessor:
            """Processor for handling known mismatches in comic data"""
            
            def __init__(self, mismatches_path=None):
                self.title_map = {}  # Maps source title to target title
                self.reading_order_map = {}  # Maps reading order to target title
                
                if mismatches_path and os.path.exists(mismatches_path):
                    self.load_mismatches(mismatches_path)
            
            def load_mismatches(self, path):
                """Load mismatches from CSV file"""
                df = pd.read_csv(path)
                
                # Only process rows marked as mismatches
                if "Mismatch" in df.columns:
                    df = df[df["Mismatch"] == "x"]
                
                # Build mapping from source to target titles
                for _, row in df.iterrows():
                    source_title = row["Title"]
                    target_title = row["Reading Order Title"].rsplit(" ", 1)[0]  # Remove issue number
                    reading_order = str(row["Reading Order"])
                    
                    # Add to mappings
                    self.title_map[source_title] = target_title
                    self.reading_order_map[reading_order] = {
                        "source_title": source_title,
                        "target_title": target_title
                    }
            
            def get_target_title(self, source_title):
                """Get target title for a source title if it exists"""
                return self.title_map.get(source_title)
            
            def get_target_by_reading_order(self, reading_order):
                """Get target info by reading order"""
                return self.reading_order_map.get(str(reading_order))
            
            def save_mappings(self, path):
                """Save title mappings to JSON file"""
                with open(path, "w") as f:
                    json.dump(self.title_map, f, indent=2)
        
        # Create processor and test loading mismatches
        processor = MismatchProcessor(mismatches_file)
        
        # Check that mappings were created correctly
        assert "X-Men" in processor.title_map
        assert processor.title_map["X-Men"] == "X-Men Annual 2000"
        assert "New X-Men: Academy X" in processor.title_map
        assert processor.title_map["New X-Men: Academy X"] == "New X-Men"
        assert "X-Men: Kitty Pryde - Shadow & Flame" in processor.title_map
        assert processor.title_map["X-Men: Kitty Pryde - Shadow & Flame"] == "X-Men: Die By The Sword"
        
        # Check reading order mapping
        assert "383.002" in processor.reading_order_map
        assert processor.reading_order_map["383.002"]["source_title"] == "X-Men"
        assert processor.reading_order_map["383.002"]["target_title"] == "X-Men Annual 2000"
        
        # Test mapping function
        assert processor.get_target_title("X-Men") == "X-Men Annual 2000"
        assert processor.get_target_title("New X-Men: Academy X") == "New X-Men"
        assert processor.get_target_title("Unknown Title") is None
        
        # Test reading order lookup
        assert processor.get_target_by_reading_order("486.166") is not None
        assert processor.get_target_by_reading_order("486.166")["target_title"] == "X-Men: Die By The Sword"
        
        # Test integration with ComicMatcher
        # This shows how the processor would be used with the existing matcher
        class MappingAwareComicMatcher(ComicMatcher):
            """Comic matcher that uses mismatch mappings"""
            
            def __init__(self, processor=None, **kwargs):
                super().__init__(**kwargs)
                self.processor = processor
            
            def find_best_match(self, comic, candidates):
                """
                Override to use mappings for known mismatches
                """
                # Check if we have a mapping for this title
                if self.processor and "title" in comic:
                    target_title = self.processor.get_target_title(comic["title"])
                    if target_title:
                        # Look for candidates with matching target title
                        matching_candidates = [
                            c for c in candidates 
                            if c.get("title", "").startswith(target_title)
                        ]
                        
                        if matching_candidates:
                            # Use the first matching candidate
                            best_candidate = matching_candidates[0]
                            return {
                                "source_comic": comic,
                                "matched_comic": best_candidate,
                                "similarity": 1.0,  # Force high confidence
                                "scores": {
                                    "title_similarity": 1.0,
                                    "issue_match": 1.0 if comic.get("issue") == best_candidate.get("issue") else 0.8,
                                    "year_similarity": 1.0,
                                },
                                "match_type": "mapping"
                            }
                
                # Fall back to regular matching
                return super().find_best_match(comic, candidates)
        
        # Create test comics
        source_comics = [
            {"title": "X-Men", "issue": "2000"},
            {"title": "New X-Men: Academy X", "issue": "7"},
            {"title": "X-Men: Kitty Pryde - Shadow & Flame", "issue": "1"},
            {"title": "Uncanny X-Men", "issue": "100"},  # No mapping for this one
        ]
        
        target_comics = [
            {"title": "X-Men Annual 2000", "issue": "1"},
            {"title": "New X-Men", "issue": "7"},
            {"title": "X-Men: Die By The Sword", "issue": "1"},
            {"title": "Uncanny X-Men", "issue": "100"},
        ]
        
        # Create mapping-aware matcher
        mapping_matcher = MappingAwareComicMatcher(processor=processor)
        
        # Test each comic
        results = []
        for source in source_comics:
            result = mapping_matcher.find_best_match(source, target_comics)
            if result:
                results.append(result)
        
        # All comics should match
        assert len(results) == len(source_comics)
        
        # Check mappings were used
        mapping_matches = [r for r in results if r.get("match_type") == "mapping"]
        assert len(mapping_matches) == 3, "3 comics should match via mapping"
        
        # The Uncanny X-Men match should be via regular matching
        regular_matches = [r for r in results if r.get("match_type") != "mapping"]
        assert len(regular_matches) == 1, "1 comic should match via regular matching"
        assert regular_matches[0]["source_comic"]["title"] == "Uncanny X-Men"


if __name__ == "__main__":
    pytest.main(["-v", "test_mismatches_integration.py"])
