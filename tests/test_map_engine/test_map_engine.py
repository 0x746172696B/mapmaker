import pytest

from apps.contracts.action import Cylinder, Fill, HollowBox
from apps.contracts.block_status import BlockStatus
from apps.contracts.coord import Coord


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


@pytest.mark.parametrize(
    "action, expected_active",
    [
        (Fill(start=Coord(0, 0, 0), end=Coord(2, 2, 2)), 27),
        (Fill(start=Coord(1, 1, 1), end=Coord(1, 1, 1)), 1),
        (Fill(start=Coord(2, 2, 2), end=Coord(0, 0, 0)), 27),  # reversed corners
    ],
)
def test_fill_activates_blocks_in_a_given_area(map_engine, action, expected_active):
    map_id = map_engine.create_map(size=10)
    map_engine.do(map_id, action)
    game_map = map_engine.get_map(map_id)
    assert game_map.active_blocks_count() == expected_active
    assert game_map.get_block(9, 9, 9) == BlockStatus.Inactive


def test_hollow_box_activates_only_the_shell(map_engine):
    map_id = map_engine.create_map(size=10)
    map_engine.do(map_id, HollowBox(start=Coord(0, 0, 0), end=Coord(2, 2, 2)))
    game_map = map_engine.get_map(map_id)
    assert game_map.active_blocks_count() == 26
    assert game_map.get_block(0, 0, 0) == BlockStatus.Active  # corner
    assert game_map.get_block(1, 1, 0) == BlockStatus.Active  # face
    assert game_map.get_block(1, 1, 1) == BlockStatus.Inactive  # interior


def test_cylinder_activates_blocks_in_a_cylinder_shape(map_engine):
    map_id = map_engine.create_map(size=10)
    map_engine.do(map_id, Cylinder(center=Coord(3, 0, 3), radius=1, height=2))
    game_map = map_engine.get_map(map_id)
    # radius 1 -> 5 blocks per layer (center + 4 axis neighbors), 2 layers = 10
    assert game_map.active_blocks_count() == 10
    assert game_map.get_block(3, 0, 3) == BlockStatus.Active  # center
    assert game_map.get_block(4, 0, 3) == BlockStatus.Active  # edge
    assert game_map.get_block(3, 1, 3) == BlockStatus.Active  # second layer
    assert (
        game_map.get_block(4, 0, 4) == BlockStatus.Inactive
    )  # diagonal corner (dist² = 2 > 1)


def test_out_of_bounds_fill_raises_and_changes_nothing(map_engine):
    map_id = map_engine.create_map(size=10)
    with pytest.raises(ValueError):
        map_engine.do(map_id, Fill(start=Coord(5, 5, 5), end=Coord(12, 12, 12)))
    assert map_engine.get_map(map_id).active_blocks_count() == 0
