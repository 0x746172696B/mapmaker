import json
import os
import uuid
from pathlib import Path
from types import SimpleNamespace

from mcp.server.fastmcp import FastMCP

from apps.contracts.action import Cylinder, Fill, HollowBox
from apps.contracts.coord import Coord
from apps.contracts.hex_color import HexColor
from apps.map_engine.src.map_engine import MapEngine

STATE_FILE = Path("state/maps.json")
DEFAULT_COLOR = "#808080"


def create_server(state_file: Path = STATE_FILE) -> SimpleNamespace:
    mcp = FastMCP("mapmaker")
    engine = MapEngine()

    def _persist() -> None:
        state_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            str(mid): {
                "size": m.size,
                "blocks": [
                    {"pos": [c.x, c.y, c.z], "color": b.color.value}
                    for c, b in m.blocks()
                ],
            }
            for mid, m in engine.maps().items()
        }
        tmp = state_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(data))
        os.replace(tmp, state_file)

    def _run(fn) -> str:
        try:
            result = fn()
            _persist()
            return result
        except (ValueError, KeyError) as e:
            return f"error: {e}"

    @mcp.tool()
    def create_map(size: int) -> str:
        """Create a new empty 3D map of size x size x size. y is up. Returns the map id."""
        return _run(lambda: str(engine.create_map(size=size)))

    @mcp.tool()
    def fill(
        map_id: str, start: list[int], end: list[int], color: str = DEFAULT_COLOR
    ) -> str:
        """Fill a solid box of blocks between two opposite corners, inclusive.
        Coordinates are [x, y, z], 0-indexed, any corner order accepted.
        color is a hex string like '#FF0000'."""

        def op():
            engine.do(
                uuid.UUID(map_id),
                Fill(start=Coord(*start), end=Coord(*end), color=HexColor(color)),
            )
            return "ok"

        return _run(op)

    @mcp.tool()
    def hollow_box(
        map_id: str, start: list[int], end: list[int], color: str = DEFAULT_COLOR
    ) -> str:
        """Build only the shell of a box between two opposite corners, inclusive.
        The interior is left untouched. color is a hex string like '#FF0000'."""

        def op():
            engine.do(
                uuid.UUID(map_id),
                HollowBox(start=Coord(*start), end=Coord(*end), color=HexColor(color)),
            )
            return "ok"

        return _run(op)

    @mcp.tool()
    def cylinder(
        map_id: str,
        center: list[int],
        radius: int,
        height: int,
        color: str = DEFAULT_COLOR,
    ) -> str:
        """Build a solid vertical cylinder. center is [x, y, z] of the base center;
        it extends upward along y for `height` layers. color is a hex string
        like '#FF0000'."""

        def op():
            engine.do(
                uuid.UUID(map_id),
                Cylinder(
                    center=Coord(*center),
                    radius=radius,
                    height=height,
                    color=HexColor(color),
                ),
            )
            return "ok"

        return _run(op)

    @mcp.tool()
    def map_summary(map_id: str) -> str:
        """Get the size and number of placed blocks of a map."""

        def op():
            m = engine.get_map(uuid.UUID(map_id))
            return f"size={m.size}, active_blocks={m.active_blocks_count()} of {m.blocks_count()}"

        return _run(op)

    return SimpleNamespace(
        mcp=mcp,
        engine=engine,
        create_map=create_map,
        fill=fill,
        hollow_box=hollow_box,
        cylinder=cylinder,
        map_summary=map_summary,
    )


_default = create_server()
mcp = _default.mcp

if __name__ == "__main__":
    mcp.run()
