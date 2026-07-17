from apps.contracts.action import Fill
from apps.contracts.block_status import BlockStatus
from apps.contracts.coord import Coord
from apps.contracts.hex_color import HexColor


def test_fill_sets_block_colors(map_engine):
    map_id = map_engine.create_map(size=10)
    color = HexColor("#818181")
    map_engine.do(map_id, Fill(color=color, start=Coord(0, 0, 0), end=Coord(2, 2, 2)))
    game_map = map_engine.get_map(map_id)
    for coord in (Coord(0, 0, 0), Coord(1, 1, 0), Coord(2, 2, 2)):
        block = game_map.get_block(coord)
        assert block.status is BlockStatus.Active
        assert block.color == color
