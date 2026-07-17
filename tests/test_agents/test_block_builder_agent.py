import asyncio
import re
from pathlib import Path

import pytest

from apps.mcp_server.src.mcp_server import create_server

AGENT_PATH = (
    Path(__file__).resolve().parents[2] / ".claude" / "agents" / "block-builder.md"
)

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def _parse_agent_file() -> tuple[dict[str, str], str]:
    text = AGENT_PATH.read_text()
    match = _FRONTMATTER_RE.match(text)
    assert match, "block-builder.md must start with a '---' delimited frontmatter block"
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        assert sep, f"malformed frontmatter line: {line!r}"
        fields[key.strip()] = value.strip()
    return fields, match.group(2)


@pytest.fixture
def frontmatter():
    return _parse_agent_file()[0]


@pytest.fixture
def body():
    return _parse_agent_file()[1]


@pytest.fixture
def registered_tool_names(tmp_path):
    server = create_server(state_file=tmp_path / "maps.json")
    tools = asyncio.run(server.mcp.list_tools())
    return {t.name for t in tools}


def test_agent_file_exists():
    assert AGENT_PATH.is_file()


def test_frontmatter_has_required_fields(frontmatter):
    assert frontmatter["name"] == "block-builder"
    assert frontmatter["description"]
    assert frontmatter["tools"]


def test_frontmatter_description_mentions_map_id_and_region(frontmatter):
    description = frontmatter["description"].lower()
    assert "map_id" in description
    assert "region" in description


def test_frontmatter_tools_are_all_prefixed_for_the_mapmaker_server(frontmatter):
    tools = [t.strip() for t in frontmatter["tools"].split(",")]
    assert tools
    for tool in tools:
        assert tool.startswith("mcp__mapmaker__"), tool


def test_frontmatter_tools_have_no_duplicates(frontmatter):
    tools = [t.strip() for t in frontmatter["tools"].split(",")]
    assert len(tools) == len(set(tools))


def test_frontmatter_tools_reference_real_registered_mcp_tools(
    frontmatter, registered_tool_names
):
    tools = [t.strip() for t in frontmatter["tools"].split(",")]
    referenced = {t.removeprefix("mcp__mapmaker__") for t in tools}
    assert referenced <= registered_tool_names


def test_frontmatter_tools_includes_batch_ops(frontmatter):
    tools = [t.strip() for t in frontmatter["tools"].split(",")]
    assert "mcp__mapmaker__batch_ops" in tools


def test_frontmatter_tools_excludes_map_creation(frontmatter):
    # a builder is dispatched onto an already-created shared map/region and
    # must not be able to create new maps of its own.
    tools = [t.strip() for t in frontmatter["tools"].split(",")]
    assert "mcp__mapmaker__create_map" not in tools


def test_body_instructs_never_building_outside_the_region(body):
    assert "outside" in body.lower()
    assert "region" in body.lower()


def test_body_instructs_that_blocks_cannot_be_removed(body):
    assert "cannot remove blocks" in body.lower()


def test_body_mentions_batch_ops_batch_size_guidance(body):
    assert "batch_ops" in body
    assert "50" in body


def test_body_ends_with_map_summary_reporting_instruction(body):
    assert "map_summary" in body
    assert "block count" in body.lower()