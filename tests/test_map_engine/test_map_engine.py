import pytest
from apps.contracts.block_status import BlockStatus


@pytest.mark.parametrize("map_size", [5, 10, 100])
def test_create_new_map_creates_size_cubed_blocks(map_engine, map_size: int):
    map_id = map_engine.create_map(size=map_size)

    assert map_engine.get_map(map_id).blocks_count() == map_size**3


def test_new_map_has_no_active_blocks(map_engine):
    map_id = map_engine.create_map(size=10)
    assert map_engine.get_map(map_id).active_blocks_count() == 0


def test_set_block_round_trips(map_engine):
    map_id = map_engine.create_map(size=10)
    game_map = map_engine.get_map(map_id)
    game_map.set_block(3, 4, 5, BlockStatus.Active)
    assert game_map.get_block(3, 4, 5) == BlockStatus.Active


def test_out_of_bounds_access_raises(map_engine):
    map_id = map_engine.create_map(size=10)
    with pytest.raises(ValueError):
        map_engine.get_map(map_id).get_block(10, 0, 0)
