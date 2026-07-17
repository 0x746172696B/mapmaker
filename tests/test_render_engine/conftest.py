import pytest

from apps.contracts.block_status import BlockStatus
from apps.contracts.coord import Coord
from apps.contracts.hex_color import HexColor
from apps.map_engine.src.map import Map
from apps.render_engine.src.render_engine import RenderEngine

DEFAULT = HexColor("#808080")


@pytest.fixture
def render_engine() -> RenderEngine:
    return RenderEngine()


@pytest.fixture
def make_map():
    def _make(
        *coords: tuple[int, int, int], size: int = 10, color: HexColor = DEFAULT
    ) -> Map:
        m = Map(size)
        for xyz in coords:
            m.set_block(Coord(*xyz), status=BlockStatus.Active, color=color)
        return m

    return _make
