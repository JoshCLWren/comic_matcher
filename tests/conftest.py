"""
Common test fixtures for comic_matcher tests
"""

import json

import pandas as pd
import pytest


@pytest.fixture
def sample_titles():
    """Sample comic titles for testing"""
    return [
        "Uncanny X-Men (1981) #142",
        "The Amazing Spider-Man #300",
        "X-Men Vol. 2 #1",
        "New Mutants (1983) Annual #3",
        "X-Factor (1986) #1: The Beginning",
        "Wolverine: Limited Series (1982) #1",
        "Cable & Deadpool #15",
        "Excalibur: The Sword is Drawn",
        "Giant-Size X-Men #1",
        "Generation X #1 Collector's Preview",
    ]


@pytest.fixture
def source_comics():
    """Sample source comics for matcher testing"""
    return [
        {"title": "Uncanny X-Men", "issue": "142"},
        {"title": "Amazing Spider-Man", "issue": "300"},
        {"title": "Wolverine", "issue": "1"},
        {"title": "New Mutants", "issue": "87"},
        {"title": "X-Factor", "issue": "1"},
        {"title": "X-Men", "issue": "1"},
        {"title": "Deadpool", "issue": "1"},
        {"title": "Excalibur", "issue": "1"},
    ]


@pytest.fixture
def target_comics():
    """Sample target comics for matcher testing"""
    return [
        {"title": "X-Men", "issue": "142", "publisher": "Marvel"},
        {"title": "The Amazing Spider-Man", "issue": "300", "publisher": "Marvel"},
        {"title": "Wolverine (Limited Series)", "issue": "1", "publisher": "Marvel"},
        {"title": "The New Mutants (1983)", "issue": "87", "publisher": "Marvel"},
        {"title": "X-Factor (1986)", "issue": "1", "publisher": "Marvel"},
        {
            "title": "Uncanny X-Men",
            "issue": "141",
            "publisher": "Marvel",
        },  # Close but not a match
        {
            "title": "New Mutants",
            "issue": "98",
            "publisher": "Marvel",
        },  # First Deadpool
        {"title": "Cable & Deadpool", "issue": "1", "publisher": "Marvel"},
    ]


@pytest.fixture
def source_df(source_comics):
    """Source comics as DataFrame"""
    return pd.DataFrame(source_comics)


@pytest.fixture
def target_df(target_comics):
    """Target comics as DataFrame"""
    return pd.DataFrame(target_comics)


@pytest.fixture
def mock_fuzzy_hash():
    """Mock fuzzy hash for testing"""
    return {
        "uncanny xmen|xmen": 0.9,
        "amazing spiderman|the amazing spiderman": 1.0,
        "wolverine|wolverine limited series": 0.95,
        "new mutants|the new mutants": 0.98,
        "xfactor|xfactor": 1.0,
    }


@pytest.fixture
def test_cache_dir(tmp_path):
    """Temporary cache directory for testing"""
    cache_dir = tmp_path / "test_cache"
    cache_dir.mkdir()
    return str(cache_dir)


@pytest.fixture
def fuzzy_hash_path(tmp_path, mock_fuzzy_hash):
    """Create a temporary fuzzy hash file"""
    hash_path = tmp_path / "test_fuzzy_hash.json"
    with open(hash_path, "w") as f:
        json.dump(mock_fuzzy_hash, f)
    return str(hash_path)
