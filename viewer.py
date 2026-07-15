import json
from pathlib import Path

import pyvista as pv

STATE_FILE = Path(__file__).resolve().parent / "state" / "maps.json"
POLL_MS = 250


def load_latest_blocks() -> list[tuple[float, float, float]]:
    if not STATE_FILE.exists():
        return []
    try:
        maps = json.loads(STATE_FILE.read_text())
    except json.JSONDecodeError:
        return []
    if not maps:
        return []
    latest = list(maps.values())[-1]
    return [tuple(float(v) for v in block) for block in latest["blocks"]]


def main() -> None:
    print(f"Watching {STATE_FILE}")
    print("Viewer open — press 'q' in the window to quit.")

    plotter = pv.Plotter(title="mapmaker live — q to quit")
    plotter.show_grid()

    last = {"mtime": 0.0}

    def poll(step) -> None:
        mtime = STATE_FILE.stat().st_mtime if STATE_FILE.exists() else 0.0
        if mtime == last["mtime"]:
            return
        last["mtime"] = mtime
        blocks = load_latest_blocks()
        plotter.clear_actors()
        if blocks:
            cubes = pv.PolyData(blocks).glyph(geom=pv.Cube(), scale=False, orient=False)
            plotter.add_mesh(cubes, color="tan", show_edges=True)
        plotter.show_grid()
        plotter.render()

    plotter.add_timer_event(max_steps=1_000_000, duration=POLL_MS, callback=poll)
    plotter.show()


if __name__ == "__main__":
    main()
