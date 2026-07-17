import asyncio
import json
import uuid

import pytest


def test_create_map_returns_a_valid_uuid_string(server):
    map_id = server.create_map(size=10)
    assert uuid.UUID(map_id)


def test_create_map_with_invalid_size_returns_error_string(server):
    result = server.create_map(size=0)
    assert result.startswith("error:")
    assert "positive" in result


def test_fill_reports_ok_and_places_blocks(server):
    map_id = server.create_map(size=10)
    result = server.fill(map_id=map_id, start=[0, 0, 0], end=[2, 2, 2])
    assert result == "ok"
    assert "active_blocks=27" in server.map_summary(map_id)


def test_hollow_box_places_only_the_shell(server):
    map_id = server.create_map(size=10)
    result = server.hollow_box(map_id=map_id, start=[0, 0, 0], end=[2, 2, 2])
    assert result == "ok"
    assert "active_blocks=26" in server.map_summary(map_id)


def test_cylinder_places_blocks(server):
    map_id = server.create_map(size=10)
    result = server.cylinder(map_id=map_id, center=[3, 0, 3], radius=1, height=2)
    assert result == "ok"
    assert "active_blocks=10" in server.map_summary(map_id)


def test_out_of_bounds_fill_returns_error_naming_the_bounds(server):
    map_id = server.create_map(size=10)
    result = server.fill(map_id=map_id, start=[5, 5, 5], end=[12, 12, 12])
    assert result.startswith("error:")
    assert "out of bounds" in result
    assert "active_blocks=0" in server.map_summary(map_id)


def test_unknown_map_id_returns_error_string(server):
    result = server.fill(map_id=str(uuid.uuid4()), start=[0, 0, 0], end=[1, 1, 1])
    assert result.startswith("error:")


def test_malformed_map_id_returns_error_string(server):
    result = server.fill(map_id="not-a-uuid", start=[0, 0, 0], end=[1, 1, 1])
    assert result.startswith("error:")


def test_fill_with_invalid_color_returns_error(server):
    map_id = server.create_map(size=10)
    result = server.fill(
        map_id=map_id, start=[0, 0, 0], end=[1, 1, 1], color="#8181811"
    )
    assert result.startswith("error:")
    assert "hex" in result.lower()
    assert "active_blocks=0" in server.map_summary(map_id)


def test_hollow_box_accepts_a_color(server, state_file):
    map_id = server.create_map(size=10)
    result = server.hollow_box(
        map_id=map_id, start=[0, 0, 0], end=[2, 2, 2], color="#00ff00"
    )
    assert result == "ok"
    data = json.loads(state_file.read_text())
    assert all(b["color"] == "#00FF00" for b in data[map_id]["blocks"])


def test_two_servers_do_not_share_state(server, tmp_path):
    from apps.mcp_server.src.mcp_server import create_server

    map_id = server.create_map(size=10)
    other = create_server(state_file=tmp_path / "other.json")
    result = other.map_summary(map_id)
    assert result.startswith("error:")


def test_all_tools_are_registered(server):
    tools = asyncio.run(server.mcp.list_tools())
    names = {t.name for t in tools}
    assert {"create_map", "fill", "hollow_box", "cylinder", "map_summary"} <= names


def test_tool_descriptions_exist_for_llm_guidance(server):
    tools = asyncio.run(server.mcp.list_tools())
    assert all(t.description for t in tools)


def test_successful_fill_persists_blocks_to_state_file(server, state_file):
    map_id = server.create_map(size=10)
    server.fill(map_id=map_id, start=[0, 0, 0], end=[2, 2, 2], color="#ff0000")
    data = json.loads(state_file.read_text())
    blocks = data[map_id]["blocks"]
    assert len(blocks) == 27
    assert data[map_id]["size"] == 10
    # pins the schema, color persistence, and uppercase normalization
    assert {"pos": [0, 0, 0], "color": "#FF0000"} in blocks


def test_fill_without_color_uses_default(server, state_file):
    map_id = server.create_map(size=10)
    server.fill(map_id=map_id, start=[0, 0, 0], end=[0, 0, 0])
    data = json.loads(state_file.read_text())
    assert data[map_id]["blocks"][0]["color"] == "#808080"


def test_failed_fill_does_not_persist_blocks(server, state_file):
    map_id = server.create_map(size=10)
    server.fill(map_id=map_id, start=[5, 5, 5], end=[12, 12, 12])
    data = json.loads(state_file.read_text())
    assert data[map_id]["blocks"] == []


def test_batch_ops_is_registered_with_a_description(server):
    tools = asyncio.run(server.mcp.list_tools())
    names = {t.name: t for t in tools}
    assert "batch_ops" in names
    assert names["batch_ops"].description


def test_batch_ops_applies_a_single_fill_operation(server):
    map_id = server.create_map(size=10)
    result = server.batch_ops(
        map_id=map_id,
        operations=[{"op": "fill", "start": [0, 0, 0], "end": [2, 2, 2]}],
    )
    assert result == "ok, applied 1 operations"
    assert "active_blocks=27" in server.map_summary(map_id)


def test_batch_ops_applies_mixed_operation_types_in_order(server):
    map_id = server.create_map(size=20)
    operations = [
        {"op": "fill", "start": [0, 0, 0], "end": [2, 2, 2]},  # 27 blocks
        {"op": "hollow_box", "start": [10, 10, 10], "end": [12, 12, 12]},  # 26 blocks
        {"op": "cylinder", "center": [5, 0, 5], "radius": 1, "height": 2},  # 10 blocks
    ]
    result = server.batch_ops(map_id=map_id, operations=operations)
    assert result == "ok, applied 3 operations"
    assert "active_blocks=63" in server.map_summary(map_id)


def test_batch_ops_with_empty_list_applies_nothing(server):
    map_id = server.create_map(size=10)
    result = server.batch_ops(map_id=map_id, operations=[])
    assert result == "ok, applied 0 operations"
    assert "active_blocks=0" in server.map_summary(map_id)


def test_batch_ops_uses_default_color_when_omitted(server, state_file):
    map_id = server.create_map(size=10)
    server.batch_ops(
        map_id=map_id,
        operations=[{"op": "fill", "start": [0, 0, 0], "end": [0, 0, 0]}],
    )
    data = json.loads(state_file.read_text())
    assert data[map_id]["blocks"][0]["color"] == "#808080"


def test_batch_ops_honors_per_operation_color(server, state_file):
    map_id = server.create_map(size=10)
    server.batch_ops(
        map_id=map_id,
        operations=[
            {"op": "fill", "start": [0, 0, 0], "end": [0, 0, 0], "color": "#ff0000"},
            {
                "op": "hollow_box",
                "start": [5, 5, 5],
                "end": [6, 6, 6],
                "color": "#00ff00",
            },
        ],
    )
    data = json.loads(state_file.read_text())
    colors = {tuple(b["pos"]): b["color"] for b in data[map_id]["blocks"]}
    assert colors[(0, 0, 0)] == "#FF0000"
    assert colors[(5, 5, 5)] == "#00FF00"


def test_batch_ops_unknown_op_name_applies_nothing(server, state_file):
    map_id = server.create_map(size=10)
    result = server.batch_ops(
        map_id=map_id,
        operations=[{"op": "sphere", "start": [0, 0, 0], "end": [1, 1, 1]}],
    )
    assert result.startswith("error: no operations applied")
    assert "unknown op 'sphere'" in result
    data = json.loads(state_file.read_text())
    assert data[map_id]["blocks"] == []


def test_batch_ops_malformed_operation_missing_key_applies_nothing(server, state_file):
    map_id = server.create_map(size=10)
    result = server.batch_ops(
        map_id=map_id,
        operations=[{"op": "fill", "start": [0, 0, 0]}],  # missing "end"
    )
    assert result.startswith("error: no operations applied, malformed operation:")
    assert "end" in result
    data = json.loads(state_file.read_text())
    assert data[map_id]["blocks"] == []


def test_batch_ops_invalid_color_in_any_operation_applies_nothing(server, state_file):
    map_id = server.create_map(size=10)
    result = server.batch_ops(
        map_id=map_id,
        operations=[
            {"op": "fill", "start": [0, 0, 0], "end": [1, 1, 1]},
            {"op": "fill", "start": [2, 2, 2], "end": [3, 3, 3], "color": "not-a-hex"},
        ],
    )
    assert result.startswith("error: no operations applied, malformed operation:")
    data = json.loads(state_file.read_text())
    # validation happens for all ops up front, before any engine mutation
    assert data[map_id]["blocks"] == []


def test_batch_ops_stops_at_first_failure_and_keeps_earlier_successes(
    server, state_file
):
    map_id = server.create_map(size=10)
    operations = [
        {"op": "fill", "start": [0, 0, 0], "end": [1, 1, 1]},  # ok, 8 blocks
        {"op": "fill", "start": [5, 5, 5], "end": [12, 12, 12]},  # out of bounds
        {"op": "fill", "start": [3, 3, 3], "end": [4, 4, 4]},  # skipped
    ]
    result = server.batch_ops(map_id=map_id, operations=operations)
    assert result.startswith("applied operations 0..0 (1 ok)")
    assert "operation 1 failed" in result
    assert "out of bounds" in result
    assert "operations 1..2 skipped" in result
    data = json.loads(state_file.read_text())
    assert len(data[map_id]["blocks"]) == 8


def test_batch_ops_failing_on_first_operation_reports_zero_applied(server):
    map_id = server.create_map(size=10)
    result = server.batch_ops(
        map_id=map_id,
        operations=[{"op": "fill", "start": [5, 5, 5], "end": [12, 12, 12]}],
    )
    assert result.startswith("applied operations 0..-1 (0 ok)")
    assert "operation 0 failed" in result
    assert "operations 0..0 skipped" in result


def test_batch_ops_with_unknown_map_id_returns_error(server):
    result = server.batch_ops(
        map_id=str(uuid.uuid4()),
        operations=[{"op": "fill", "start": [0, 0, 0], "end": [1, 1, 1]}],
    )
    assert "operation 0 failed" in result
    assert "No map with id" in result


def test_batch_ops_with_malformed_map_id_returns_error_string(server):
    result = server.batch_ops(
        map_id="not-a-uuid",
        operations=[{"op": "fill", "start": [0, 0, 0], "end": [1, 1, 1]}],
    )
    assert result.startswith("error:")


def test_batch_ops_cylinder_with_non_positive_radius_fails_that_operation(server):
    map_id = server.create_map(size=10)
    result = server.batch_ops(
        map_id=map_id,
        operations=[{"op": "cylinder", "center": [3, 0, 3], "radius": 0, "height": 2}],
    )
    assert "operation 0 failed" in result
    assert "radius must be positive" in result


def test_batch_ops_persists_all_applied_blocks_to_state_file(server, state_file):
    map_id = server.create_map(size=10)
    server.batch_ops(
        map_id=map_id,
        operations=[
            {"op": "fill", "start": [0, 0, 0], "end": [0, 0, 0], "color": "#123456"},
        ],
    )
    data = json.loads(state_file.read_text())
    assert data[map_id]["blocks"] == [{"pos": [0, 0, 0], "color": "#123456"}]


def test_batch_ops_non_dict_operation_raises_attribute_error(server):
    # documents current behavior: malformed non-dict entries are not translated
    # into a friendly "error:" string like other failure modes are.
    map_id = server.create_map(size=10)
    with pytest.raises(AttributeError):
        server.batch_ops(map_id=map_id, operations=["not-a-dict"])
