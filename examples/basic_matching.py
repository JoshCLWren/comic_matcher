"""
Basic example of using Comic Matcher
"""

import os
import sys

import pandas as pd

# Add parent directory to path so we can import comic_matcher
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from comic_matcher import ComicMatcher

# Example data
source_comics = [
    {"title": "Uncanny X-Men", "issue": "142"},
    {"title": "Amazing Spider-Man", "issue": "300"},
    {"title": "Wolverine", "issue": "1"},
    {"title": "New Mutants", "issue": "87"},
    {"title": "X-Factor", "issue": "1"},
]

target_comics = [
    {"title": "X-Men", "issue": "142"},
    {"title": "The Amazing Spider-Man", "issue": "300"},
    {"title": "Wolverine (Limited Series)", "issue": "1"},
    {"title": "The New Mutants (1983)", "issue": "87"},
    {"title": "X-Factor (1986)", "issue": "1"},
    {"title": "Uncanny X-Men", "issue": "141"},  # Close but not a match
]


def main():
    # Initialize the matcher
    matcher = ComicMatcher()

    print("Source comics:")
    for comic in source_comics:
        print(f"  - {comic['title']} #{comic['issue']}")

    print("\nTarget comics:")
    for comic in target_comics:
        print(f"  - {comic['title']} #{comic['issue']}")

    # Find matches
    matches = matcher.match(source_comics, target_comics)

    print(f"\nFound {len(matches)} matches:")

    # Display matches in a readable format
    if not matches.empty:
        for _, match in matches.iterrows():
            print(f"\nMatch with similarity {match['similarity']:.2f}:")
            print(f"  Source: {match['source_title']} #{match['source_issue']}")
            print(f"  Target: {match['target_title']} #{match['target_issue']}")
            print(f"  Title similarity: {match['title_sim']:.2f}")
            print(f"  Issue match: {match['issue_match']:.2f}")

    # Example of finding a best match for a single comic
    print("\n--- Finding best match for a single comic ---")

    comic = {"title": "Uncanny X-Men", "issue": "142"}
    best_match = matcher.find_best_match(comic, target_comics)

    if best_match:
        print(f"\nBest match for {comic['title']} #{comic['issue']}:")
        print(
            f"  {best_match['matched_comic']['title']} #{best_match['matched_comic']['issue']}"
        )
        print(f"  Similarity: {best_match['similarity']:.2f}")
        print(f"  Scores: {best_match['scores']}")
    else:
        print(f"\nNo match found for {comic['title']} #{comic['issue']}")


if __name__ == "__main__":
    main()
