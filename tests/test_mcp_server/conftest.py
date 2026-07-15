import pytest

from apps.mcp_server.src.mcp_server import create_server


@pytest.fixture
def server():
    return create_server()
