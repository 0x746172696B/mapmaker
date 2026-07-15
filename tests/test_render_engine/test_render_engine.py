def test_empty_map_builds_empty_scene(render_engine, make_map):
    scene = render_engine.build_scene(make_map())

    assert scene.n_points == 0


def test_scene_has_one_cube_per_active_block(render_engine, make_map):
    scene = render_engine.build_scene(make_map((0, 0, 0), (3, 4, 5), (9, 9, 9)))

    # each glyphed cube contributes 8 corner points and 6 faces
    assert scene.n_points == 3 * 8
    assert scene.n_cells == 3 * 6


def test_single_cube_is_centered_on_its_block_coord(render_engine, make_map):
    scene = render_engine.build_scene(make_map((3, 4, 5)))

    assert tuple(scene.center) == (3.0, 4.0, 5.0)


def test_cubes_have_unit_size(render_engine, make_map):
    scene = render_engine.build_scene(make_map((3, 4, 5)))

    xmin, xmax, ymin, ymax, zmin, zmax = scene.bounds
    assert (xmax - xmin, ymax - ymin, zmax - zmin) == (1.0, 1.0, 1.0)


def test_scene_bounds_span_all_blocks(render_engine, make_map):
    scene = render_engine.build_scene(make_map((0, 0, 0), (9, 9, 9)))

    xmin, xmax, ymin, ymax, zmin, zmax = scene.bounds
    # blocks are unit cubes centered on coords: 0 -> -0.5, 9 -> 9.5
    assert (xmin, ymin, zmin) == (-0.5, -0.5, -0.5)
    assert (xmax, ymax, zmax) == (9.5, 9.5, 9.5)


def test_scene_reflects_map_changes_between_builds(render_engine, make_map):
    from apps.contracts.block_status import BlockStatus

    game_map = make_map((0, 0, 0))
    first = render_engine.build_scene(game_map)

    game_map.set_block(5, 5, 5, BlockStatus.Active)
    second = render_engine.build_scene(game_map)

    assert first.n_points == 8
    assert second.n_points == 16
