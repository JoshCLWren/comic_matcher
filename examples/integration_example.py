"""
Example of integrating Comic Matcher with existing projects
"""

import os
import sys
import json
import pandas as pd

# Add parent directory to path so we can import comic_matcher
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from comic_matcher import ComicMatcher, ComicTitleParser
from comic_matcher.utils import export_matches_to_csv


def comic_pricer_integration(web_pricer_path, comic_pricer_path, output_path):
    """
    Example of matching comics between web_pricer and comic_pricer data
    
    Args:
        web_pricer_path: Path to web_pricer data
        comic_pricer_path: Path to comic_pricer data
        output_path: Path to save results
    """
    print(f"Loading data from {web_pricer_path} and {comic_pricer_path}...")
    
    # Load data from web_pricer
    try:
        web_df = pd.read_csv(web_pricer_path)
        print(f"Loaded {len(web_df)} comics from web_pricer")
    except Exception as e:
        print(f"Error loading web_pricer data: {e}")
        web_df = pd.DataFrame(columns=['title', 'issue', 'price', 'store_name'])
    
    # Load data from comic_pricer
    try:
        with open(comic_pricer_path, 'r') as f:
            comic_data = json.load(f)
            
        # Convert to list of dicts
        if isinstance(comic_data, dict):
            comic_list = []
            for comic_id, comic in comic_data.items():
                comic_dict = comic.copy()
                comic_dict['id'] = comic_id
                comic_list.append(comic_dict)
        else:
            comic_list = comic_data
            
        print(f"Loaded {len(comic_list)} comics from comic_pricer")
    except Exception as e:
        print(f"Error loading comic_pricer data: {e}")
        comic_list = []
    
    # Initialize matcher
    matcher = ComicMatcher()
    
    # Match comics
    print("Matching comics...")
    matches = matcher.match(web_df, comic_list, threshold=0.7)
    
    # Print summary
    if not matches.empty:
        print(f"\nFound {len(matches)} matches")
        
        # Export results
        export_matches_to_csv(matches, output_path)
        print(f"Saved matches to {output_path}")
        
        # Show sample
        print("\nSample matches:")
        for _, match in matches.head(5).iterrows():
            print(f"  {match['source_title']} #{match['source_issue']} = {match['target_title']} #{match['target_issue']} (similarity: {match['similarity']:.2f})")
    else:
        print("\nNo matches found")


def xmen_reading_order_integration(reading_order_path, wishlist_path, output_path):
    """
    Example of matching X-Men reading order with wishlist
    
    Args:
        reading_order_path: Path to reading order CSV
        wishlist_path: Path to wishlist data
        output_path: Path to save results
    """
    print(f"Loading data from {reading_order_path} and {wishlist_path}...")
    
    # Load reading order
    try:
        reading_df = pd.read_csv(reading_order_path)
        
        # Extract titles and issues from reading order
        parser = ComicTitleParser()
        
        # Process reading order data
        processed_records = []
        for _, row in reading_df.iterrows():
            title = row.get('TItle', '')
            if not title:
                continue
                
            # Extract issue from title if needed
            issue = None
            if '#' in title:
                parts = title.split('#')
                title = parts[0].strip()
                issue = parser.extract_issue_number(parts[1].strip())
            
            # Parse title to components
            components = parser.parse(title)
            
            # Create record
            record = {
                'title': title,
                'issue': issue,
                'main_title': components['main_title'],
                'year': components['year'],
                'era': row.get('Era', ''),
                'read': row.get('Read', False),
                'owned': row.get('Owned', False),
                'order': row.get('Order', 0)
            }
            processed_records.append(record)
            
        reading_records = processed_records
        print(f"Processed {len(reading_records)} reading order entries")
    except Exception as e:
        print(f"Error loading reading order: {e}")
        reading_records = []
    
    # Load wishlist
    try:
        wishlist_df = pd.read_csv(wishlist_path)
        print(f"Loaded {len(wishlist_df)} wishlist comics")
    except Exception as e:
        print(f"Error loading wishlist: {e}")
        wishlist_df = pd.DataFrame()
    
    # Initialize matcher with settings optimized for X-Men
    matcher = ComicMatcher()
    
    # Match comics
    print("Matching comics...")
    matches = matcher.match(reading_records, wishlist_df, threshold=0.7)
    
    # Print summary
    if not matches.empty:
        # Add additional info about reading order
        matches['reading_priority'] = matches['order']
        
        # Filter for unread comics
        unread_matches = matches[~matches['read'] & ~matches['owned']]
        print(f"\nFound {len(matches)} total matches, {len(unread_matches)} unread")
        
        # Export results
        export_matches_to_csv(unread_matches, output_path)
        print(f"Saved unread matches to {output_path}")
        
        # Show sample
        print("\nSample unread matches:")
        for _, match in unread_matches.head(5).iterrows():
            print(f"  {match['source_title']} #{match['source_issue']} (Order: {match['order']}) = {match['target_title']} #{match['target_issue']} (${match.get('price', 'N/A')})")
    else:
        print("\nNo matches found")


def main():
    """Main function with example invocations"""
    
    print("Comic Matcher Integration Examples")
    print("=================================\n")
    
    # Example paths - replace with your actual file paths
    SAMPLE_PATHS = {
        'comic_data': '../sample_data/comic_data.json',
        'wishlist_data': '../sample_data/wishlist.csv',
        'reading_order': '../sample_data/reading_order.csv', 
    }
    
    # Check if sample files exist
    if any(not os.path.exists(os.path.join(os.path.dirname(__file__), p)) for p in SAMPLE_PATHS.values()):
        print("Sample data files not found. This script is an example of how to integrate with your existing data.")
        print("You will need to modify the paths to point to your actual data files.")
        
        # Create example data
        print("\nCreating example data for demonstration...")
        
        # Simple example with hardcoded data
        print("\n=== Simple Example ===")
        
        source_comics = [
            {"title": "Uncanny X-Men", "issue": "142", "source": "web_pricer"},
            {"title": "Amazing Spider-Man", "issue": "300", "source": "web_pricer"},
        ]
        
        target_comics = [
            {"title": "X-Men", "issue": "142", "source": "comic_pricer"},
            {"title": "Spider-Man", "issue": "300", "source": "comic_pricer"},
        ]
        
        matcher = ComicMatcher()
        matches = matcher.match(source_comics, target_comics)
        
        print(f"Found {len(matches)} matches in example data")
        
        if not matches.empty:
            for _, match in matches.iterrows():
                print(f"  {match['source_title']} #{match['source_issue']} = {match['target_title']} #{match['target_issue']} (similarity: {match['similarity']:.2f})")
    else:
        # Run integration examples with actual data
        print("\n=== comic_pricer Integration ===")
        comic_pricer_integration(
            SAMPLE_PATHS['wishlist_data'],
            SAMPLE_PATHS['comic_data'],
            'comic_matches.csv'
        )
        
        print("\n=== X-Men Reading Order Integration ===")
        xmen_reading_order_integration(
            SAMPLE_PATHS['reading_order'],
            SAMPLE_PATHS['wishlist_data'],
            'reading_order_matches.csv'
        )

if __name__ == "__main__":
    main()
