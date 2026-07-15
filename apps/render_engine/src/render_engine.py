import pyvista as pv
from apps.map_engine.src.map import Map


class RenderEngine:
    def build_scene(self, game_map: Map) -> pv.PolyData:
        """Pure-ish: blocks in, geometry out. No window."""
        points = pv.PolyData(
            [(float(c.x), float(c.y), float(c.z)) for c in game_map.active_blocks()]
        )
        return points.glyph(geom=pv.Cube(), scale=False, orient=False)

    def show(self, game_map: Map) -> None:
        """Side effect: opens the window. Thin, untested."""
        plotter = pv.Plotter()
        plotter.add_mesh(self.build_scene(game_map), color="tan", show_edges=True)
        plotter.show()
