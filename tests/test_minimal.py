"""
Minimal test case for Marvel: Shadows and Light issue
"""

import pandas as pd

from comic_matcher.matcher import ComicMatcher


def test_minimal_reproduction():
    """
    Minimal test case to diagnose exactly what's happening with matching
    """
    # Initialize matcher
    matcher = ComicMatcher()

    # Source comic: Marvel: Shadows and Light #1
    source_comic = {"title": "Marvel: Shadows and Light", "issue": "1"}

    # Target candidates including Marvels #1
    candidates = [
        {"title": "Marvels", "issue": "1"},
        {"title": "Marvel: Shadows and Light", "issue": "1"},
    ]

    # Test direct title comparison
    print("\n== Title Similarity Tests ==")
    for candidate in candidates:
        sim = matcher._compare_titles(source_comic["title"], candidate["title"])
        print(f"{source_comic['title']} vs {candidate['title']}: {sim:.4f}")

    # Test find_best_match directly
    print("\n== find_best_match Test ==")
    result = matcher.find_best_match(source_comic, candidates)

    if result:
        print(
            f"Found match: {result['matched_comic']['title']} (similarity: {result['similarity']:.4f})"
        )
        print(f"Scores: {result['scores']}")
    else:
        print("No match found")

    # Try with only Marvels
    print("\n== Marvels-only Test ==")
    marvels_only = [{"title": "Marvels", "issue": "1"}]
    only_result = matcher.find_best_match(source_comic, marvels_only)

    if only_result:
        print(
            f"Found match: {only_result['matched_comic']['title']} (similarity: {only_result['similarity']:.4f})"
        )
        print(f"Scores: {only_result['scores']}")
    else:
        print("No match found")

    # Test using the full match function directly
    print("\n== Full match() Function Test ==")
    source_df = pd.DataFrame([source_comic])
    candidates_df = pd.DataFrame(candidates)

    matches = matcher.match(source_df, candidates_df, threshold=0.3, indexer_method="full")

    if not matches.empty:
        print("Match results:")
        print(matches)

        # Find the best match
        best_idx = matches["similarity"].idxmax()
        best_match = matches.loc[best_idx]

        print(f"\nBest match:")
        print(f"Source: {best_match['source_title']}")
        print(f"Target: {best_match['target_title']}")
        print(f"Similarity: {best_match['similarity']:.4f}")

        # Get index of target
        if isinstance(best_match.name, tuple):
            target_idx = best_match.name[1]
            matched_title = candidates_df.iloc[target_idx]["title"]
            print(f"Matched with: {matched_title}")
        else:
            print("Could not determine exact match")
    else:
        print("No matches found")
