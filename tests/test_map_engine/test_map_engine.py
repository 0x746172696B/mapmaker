import pytest

from apps.contracts.block_status import BlockStatus
from apps.contracts.action import Action


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
        # A fill from (0,0,0) to (2,2,2) inclusive covers a 3x3x3 area
        (Action(do=Action.Fill, start=[0, 0, 0], end=[2, 2, 2]), 27),
        (Action(do=Action.Fill, start=[1, 1, 1], end=[1, 1, 1]), 1),
    ],
)
def test_fill_activates_blocks_in_a_given_area(map_engine, action, expected_active):
    map_id = map_engine.create_map(size=10)
    map_engine.do(map_id, action)

    game_map = map_engine.get_map(map_id)
    assert game_map.active_blocks_count() == expected_active
    # Spot-check a block inside the filled area and one outside it
    assert game_map.get_block(*action.start) == BlockStatus.Active
    assert game_map.get_block(9, 9, 9) == BlockStatus.Inactive


@pytest.mark.parametrize(
    "action",
    [Action(do=Action.HBox, start=[0, 0, 0], end=[2, 2, 2])],
)
def test_hbox_activates_blocks_in_a_surrounding_area(map_engine, action):
    map_id = map_engine.create_map(size=10)
    map_engine.do(map_id, action)

    game_map = map_engine.get_map(map_id)
    # A hollow box: the shell is active, the interior is not.
    # 3x3x3 area = 27 blocks, minus the single interior block = 26
    assert game_map.active_blocks_count() == 26
    assert game_map.get_block(0, 0, 0) == BlockStatus.Active  # corner
    assert game_map.get_block(1, 1, 0) == BlockStatus.Active  # face
    assert game_map.get_block(1, 1, 1) == BlockStatus.Inactive  # interior


@pytest.mark.parametrize(
    "action",
    [Action(do=Action.Cylinder, start=[0, 0, 0], end=[2, 2, 2])],
)
def test_cylinder_activates_block_in_a_cylinder_shape_given_a_radius_and_height(
    map_engine, action
):
    map_id = map_engine.create_map(size=10)
    map_engine.do(map_id, action)

    game_map = map_engine.get_map(map_id)
    # Blocks along the central axis of the cylinder must be active
    assert game_map.get_block(1, 1, 0) == BlockStatus.Active
    assert game_map.get_block(1, 1, 2) == BlockStatus.Active
    # A corner of the bounding box lies outside the circular cross-section
    assert game_map.get_block(0, 0, 0) == BlockStatus.Inactive
    assert game_map.active_blocks_count() > 0
