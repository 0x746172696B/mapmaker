import json
from pathlib import Path

import pyvista as pv

from apps.map_engine.src.map import Map
from apps.render_engine.src.render_engine import RenderEngine

STATE_FILE = Path(__file__).resolve().parent / "state" / "maps.json"
POLL_MS = 250


def load_latest_map() -> Map | None:
    if not STATE_FILE.exists():
        return None
    try:
        maps = json.loads(STATE_FILE.read_text())
    except json.JSONDecodeError:
        return None  # mid-write or corrupt; try again next poll
    if not maps:
        return None
    latest = list(maps.values())[-1]
    try:
        return Map.from_state(latest)
    except (KeyError, TypeError, ValueError):
        return None  # old-format or hand-edited entry; skip this poll


def main() -> None:
    print(f"Watching {STATE_FILE}")
    print("Viewer open — press 'q' in the window to quit.")

    render_engine = RenderEngine()
    plotter = pv.Plotter(title="mapmaker live — q to quit")
    plotter.show_grid()

    last = {"mtime": 0.0}

    def poll(step) -> None:
        mtime = STATE_FILE.stat().st_mtime if STATE_FILE.exists() else 0.0
        if mtime == last["mtime"]:
            return
        last["mtime"] = mtime

        game_map = load_latest_map()
        plotter.clear_actors()
        if game_map is not None and game_map.active_blocks_count() > 0:
            scene = render_engine.build_scene(game_map)
            plotter.add_mesh(scene, scalars="colors", rgb=True, show_edges=True)
        plotter.show_grid()
        plotter.render()

    plotter.add_timer_event(max_steps=1_000_000, duration=POLL_MS, callback=poll)
    plotter.show()


if __name__ == "__main__":
    main()
