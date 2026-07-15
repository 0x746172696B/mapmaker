import asyncio
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


def test_two_servers_do_not_share_state(server):
    from apps.mcp_server.src.mcp_server import create_server

    map_id = server.create_map(size=10)
    other = create_server()
    result = other.map_summary(map_id)
    assert result.startswith("error:")


def test_all_tools_are_registered(server):
    tools = asyncio.run(server.mcp.list_tools())
    names = {t.name for t in tools}
    assert {"create_map", "fill", "hollow_box", "cylinder", "map_summary"} <= names


def test_tool_descriptions_exist_for_llm_guidance(server):
    tools = asyncio.run(server.mcp.list_tools())
    assert all(t.description for t in tools)
