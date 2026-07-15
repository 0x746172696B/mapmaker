import pytest

from apps.render_engine.src.render_engine import RenderEngine
from apps.contracts.block_status import BlockStatus
from apps.map_engine.src.map import Map


@pytest.fixture
def render_engine():
    return RenderEngine()


@pytest.fixture
def make_map():
    def _make(*coords, size=10) -> Map:
        m = Map(size)

        for x, y, z in coords:
            m.set_block(x, y, z, BlockStatus.Active)

        return m

    return _make
