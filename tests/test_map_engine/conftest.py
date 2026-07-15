import pytest
from apps.map_engine.src.map_engine import MapEngine


@pytest.fixture
def map_engine():
    return MapEngine()
