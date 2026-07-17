import asyncio
import json
import uuid


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
