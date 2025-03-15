#!/usr/bin/env python
"""
Debug script to diagnose Marvel: Shadows and Light vs Marvels issue
"""

import pandas as pd
from comic_matcher.matcher import ComicMatcher


def debug_marvel_shadows():
    """Debug the matching issue with detailed output"""
    print("\n=== DEBUGGING MARVEL: SHADOWS AND LIGHT ISSUE ===\n")
    
    # Initialize matcher
    matcher = ComicMatcher()
    
    # Source and target comics
    source_comic = {"title": "Marvel: Shadows and Light", "issue": "1"}
    candidates = [
        {"title": "Marvels", "issue": "1"},
        {"title": "Marvel: Shadows and Light", "issue": "1"}
    ]
    
    # 1. Test title comparison
    print("1. TITLE COMPARISON:")
    for candidate in candidates:
        sim = matcher._compare_titles(source_comic["title"], candidate["title"])
        print(f"   {source_comic['title']} vs {candidate['title']}: {sim:.4f}")
    
    # 2. Parse the titles to see what's happening
    print("\n2. TITLE PARSING:")
    for title in ["Marvel: Shadows and Light", "Marvels"]:
        parsed = matcher.parser.parse(title)
        print(f"   {title}:")
        for key, value in parsed.items():
            print(f"      {key}: '{value}'")
    
    # 3. Test issue comparison
    print("\n3. ISSUE COMPARISON:")
    sim = matcher._compare_issues(source_comic["issue"], candidates[0]["issue"])
    print(f"   {source_comic['issue']} vs {candidates[0]['issue']}: {sim:.4f}")
    
    # 4. Test direct find_best_match
    print("\n4. FIND BEST MATCH:")
    result = matcher.find_best_match(source_comic, candidates)
    if result:
        print(f"   Found match: {result['matched_comic']['title']} (similarity: {result['similarity']:.4f})")
        print(f"   Scores: {result['scores']}")
    else:
        print("   No match found")
    
    # 5. Test with only Marvels
    print("\n5. MARVELS-ONLY TEST:")
    marvels_only = [{"title": "Marvels", "issue": "1"}]
    only_result = matcher.find_best_match(source_comic, marvels_only)
    if only_result:
        print(f"   Found match: {only_result['matched_comic']['title']} (similarity: {only_result['similarity']:.4f})")
        print(f"   Scores: {only_result['scores']}")
    else:
        print("   No match found")
    
    # 6. Test the internal match() function
    print("\n6. INTERNAL MATCH() FUNCTION:")
    source_df = pd.DataFrame([source_comic])
    candidates_df = pd.DataFrame(candidates)
    
    # Use the match function with very low threshold to see all potential matches
    matches = matcher.match(source_df, candidates_df, threshold=0.1, indexer_method="full")
    
    if not matches.empty:
        print("   Match results:")
        print(matches)
        
        # Find the best match
        best_idx = matches["similarity"].idxmax()
        best_match = matches.loc[best_idx]
        
        print(f"\n   Best match:")
        print(f"   Source: {best_match['source_title']}")
        print(f"   Target: {best_match['target_title']}")
        print(f"   Similarity: {best_match['similarity']:.4f}")
        
        # Check which index was matched
        if isinstance(best_match.name, tuple):
            target_idx = best_match.name[1]
            print(f"   Target index: {target_idx}")
            matched_title = candidates_df.iloc[target_idx]["title"]
            print(f"   Matched with: {matched_title}")
        else:
            print("   Could not determine exact match")
    else:
        print("   No matches found")
    
    print("\n=== END OF DEBUG ===\n")


if __name__ == "__main__":
    debug_marvel_shadows()
