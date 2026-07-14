import pytest
from .apps.contracts.block_status import BlockStatus


@pytest.mark.parametrize("map_size", [5, 10, 100])
def test_create_new_map_creates_size_cubed_blocks(map_engine, map_size: int):
    map_engine.create_new_map(size=map_size)

    assert map_engine.blocks_count() == map_size**3


def test_initial_state_of_every_block_is_set_to_inactive(map_engine):
    map_engine.create_new_map(size=10)

    assert all(block.status == BlockStatus.Inactive for block in map_engine.blocks())
