"""Shared test fixtures and configuration."""

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir():
    """Return the path to the fixtures directory."""
    return FIXTURES_DIR
