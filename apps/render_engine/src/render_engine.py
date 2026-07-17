import numpy as np
import pyvista as pv

from apps.map_engine.src.map import Map


class RenderEngine:
    def build_scene(self, game_map: Map) -> pv.PolyData:
        """Pure-ish: blocks in, geometry out. No window."""
        items = list(game_map.blocks())
        if not items:
            return pv.PolyData()
        points = pv.PolyData(np.array([(c.x, c.y, c.z) for c, _ in items], dtype=float))
        points["colors"] = np.array(
            [self._hex_to_rgb(b.color.value) for _, b in items], dtype=np.uint8
        )
        return points.glyph(geom=pv.Cube(), scale=False, orient=False)

    def show(self, game_map: Map) -> None:
        """Side effect: opens the window. Thin, untested."""
        plotter = pv.Plotter()
        plotter.add_mesh(
            self.build_scene(game_map), scalars="colors", rgb=True, show_edges=True
        )
        plotter.show()

    @staticmethod
    def _hex_to_rgb(value: str) -> tuple[int, int, int]:
        return tuple(int(value[i : i + 2], 16) for i in (1, 3, 5))
