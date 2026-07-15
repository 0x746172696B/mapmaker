import pytest

from apps.mcp_server.src.mcp_server import create_server


@pytest.fixture
def state_file(tmp_path):
    return tmp_path / "maps.json"


@pytest.fixture
def server(state_file):
    return create_server(state_file=state_file)
