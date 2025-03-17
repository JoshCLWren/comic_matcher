"""
Test fixtures for bad match test cases
"""

import json
import os
import tempfile
from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def test_cache_dir():
    """Create a temporary directory for cache testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def fuzzy_hash_path(tmp_path):
    """Create a temporary fuzzy hash file for testing"""
    fuzzy_hash = {
        "uncanny xmen|xmen": 0.9,
        "amazing spiderman|the amazing spiderman": 1.0,
        "fantastic four|the fantastic four": 0.95,
    }

    hash_path = tmp_path / "test_fuzzy_hash.json"
    with open(hash_path, "w") as f:
        json.dump(fuzzy_hash, f)

    yield str(hash_path)


@pytest.fixture
def mock_fuzzy_hash():
    """Create a mock fuzzy hash dictionary"""
    return {
        "uncanny xmen|xmen": 0.9,
        "amazing spiderman|the amazing spiderman": 1.0,
        "fantastic four|the fantastic four": 0.95,
    }


@pytest.fixture
def source_comics():
    """Sample source comics for testing"""
    return [
        {"title": "Uncanny X-Men", "issue": "142"},
        {"title": "Amazing Spider-Man", "issue": "300"},
        {"title": "Wolverine", "issue": "1"},
        {"title": "X-Men", "issue": "1"},
        {"title": "Fantastic Four", "issue": "48"},
    ]


@pytest.fixture
def target_comics():
    """Sample target comics for testing"""
    return [
        {"title": "Uncanny X-Men", "issue": "141"},  # One issue off
        {"title": "Uncanny X-Men", "issue": "142"},  # Direct match
        {"title": "X-Men", "issue": "142"},  # Similar series, same issue
        {"title": "Amazing Spider-Man", "issue": "300"},  # Direct match
        {"title": "X-Force", "issue": "1"},  # Different series
    ]


@pytest.fixture
def source_df(source_comics):
    """Convert source comics to DataFrame"""
    return pd.DataFrame(source_comics)


@pytest.fixture
def target_df(target_comics):
    """Convert target comics to DataFrame"""
    return pd.DataFrame(target_comics)


@pytest.fixture
def bad_match_source_comics():
    """Sample source comics for bad match testing"""
    return [
        # Completely different titles
        {"title": "X-Men '92: House Of Xcii", "issue": "3"},
        {"title": "X-Men: Children Of The Atom", "issue": "6"},
        # Subtitle missing
        {"title": "New X-Men: Academy X", "issue": "2"},
        {"title": "New X-Men: Academy X", "issue": "3"},
        # Annual/special issue
        {"title": "X-Men", "issue": "2000"},
        {"title": "Uncanny X-Men Special", "issue": "1"},
        # Series version
        {"title": "X-Men Forever 2", "issue": "1"},
        {"title": "X-Men Forever 2", "issue": "5"},
        # Crossover/team-up
        {"title": "Wolverine", "issue": "1"},
        {"title": "Wolverine", "issue": "2"},
        # Series variant
        {"title": "X-Men", "issue": "42"},
        # Civil War titles
        {"title": "Civil War: Casualties Of War", "issue": "1"},
        {"title": "Civil War: The Confession", "issue": "1"},
        {"title": "Civil War: Marvels Snapshots", "issue": "1"},
        # Control cases (should match)
        {"title": "Uncanny X-Men", "issue": "142"},
        {"title": "Amazing Spider-Man", "issue": "300"},
    ]


@pytest.fixture
def bad_match_target_comics():
    """Sample target comics for bad match testing"""
    return [
        # Completely different titles
        {"title": "X-Men: Phoenix", "issue": "3"},
        {"title": "X-Men: The End", "issue": "6"},
        # Subtitle missing
        {"title": "New X-Men", "issue": "2"},
        {"title": "New X-Men", "issue": "3"},
        # Annual/special issue
        {"title": "X-Men Annual 2000", "issue": "1"},
        {"title": "Uncanny X-Men Annual", "issue": "1"},
        # Series version
        {"title": "X-Men Forever", "issue": "1"},
        {"title": "X-Men Forever", "issue": "5"},
        # Crossover/team-up
        {"title": "Wolverine/Doop", "issue": "1"},
        {"title": "Wolverine/Doop", "issue": "2"},
        # Series variant
        {"title": "X-Men Unlimited", "issue": "42"},
        # Civil War titles
        {"title": "Civil War: House of M", "issue": "1"},
        {"title": "Civil War: X-Men", "issue": "1"},
        # Control cases (should match)
        {"title": "Uncanny X-Men", "issue": "142"},
        {"title": "Amazing Spider-Man", "issue": "300"},
    ]


@pytest.fixture
def bad_match_source_df(bad_match_source_comics):
    """Convert bad match source comics to DataFrame"""
    return pd.DataFrame(bad_match_source_comics)


@pytest.fixture
def bad_match_target_df(bad_match_target_comics):
    """Convert bad match target comics to DataFrame"""
    return pd.DataFrame(bad_match_target_comics)
