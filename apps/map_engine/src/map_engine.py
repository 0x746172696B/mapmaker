import uuid
from collections.abc import Iterator

from apps.contracts.action import Action, Cylinder, Fill, HollowBox
from apps.contracts.block_status import BlockStatus
from apps.contracts.coord import Coord

from .map import Map


class MapEngine:
    def __init__(self) -> None:
        self._maps: dict[uuid.UUID, Map] = {}

    def create_map(self, size: int) -> uuid.UUID:
        if size <= 0:
            raise ValueError(f"size must be positive, got {size}")
        map_id = uuid.uuid4()
        self._maps[map_id] = Map(size)
        return map_id

    def get_map(self, map_id: uuid.UUID) -> Map:
        try:
            return self._maps[map_id]
        except KeyError:
            raise KeyError(f"No map with id {map_id}")

    def do(self, map_id: uuid.UUID, action: Action) -> None:
        game_map = self.get_map(map_id)
        match action:
            case Fill(start=start, end=end):
                self._fill(game_map, start, end)
            case HollowBox(start=start, end=end):
                self._hollow_box(game_map, start, end)
            case Cylinder(center=center, radius=radius, height=height):
                self._cylinder(game_map, center, radius, height)
            case _:
                raise NotImplementedError(f"Unhandled action: {action}")

    def _fill(self, game_map: Map, start: Coord, end: Coord) -> None:
        for c, _, _ in self._box_coords(game_map, start, end):
            game_map.set_block(c.x, c.y, c.z, BlockStatus.Active)

    def _hollow_box(self, game_map: Map, start: Coord, end: Coord) -> None:
        for c, lo, hi in self._box_coords(game_map, start, end):
            if c.x in (lo.x, hi.x) or c.y in (lo.y, hi.y) or c.z in (lo.z, hi.z):
                game_map.set_block(c.x, c.y, c.z, BlockStatus.Active)

    def _cylinder(self, game_map: Map, center: Coord, radius: int, height: int) -> None:
        if radius <= 0:
            raise ValueError(f"radius must be positive, got {radius}")
        if height <= 0:
            raise ValueError(f"height must be positive, got {height}")
        game_map.validate(center.x - radius, center.y, center.z - radius)
        game_map.validate(center.x + radius, center.y + height - 1, center.z + radius)
        for y in range(center.y, center.y + height):
            for x in range(center.x - radius, center.x + radius + 1):
                for z in range(center.z - radius, center.z + radius + 1):
                    if (x - center.x) ** 2 + (z - center.z) ** 2 <= radius**2:
                        game_map.set_block(x, y, z, BlockStatus.Active)

    def maps(self) -> dict[uuid.UUID, "Map"]:
        """Snapshot of all maps by id."""
        return dict(self._maps)

    @staticmethod
    def _box_coords(
        game_map: Map, start: Coord, end: Coord
    ) -> Iterator[tuple[Coord, Coord, Coord]]:
        """Normalize corners, validate bounds, then yield every coord in the box.

        Yields (coord, lo, hi) so callers can test against the box edges.
        Note: validation runs when iteration begins, not at call time.
        """
        lo, hi = MapEngine._normalize(start, end)
        game_map.validate(*lo)
        game_map.validate(*hi)
        for x in range(lo.x, hi.x + 1):
            for y in range(lo.y, hi.y + 1):
                for z in range(lo.z, hi.z + 1):
                    yield Coord(x, y, z), lo, hi

    @staticmethod
    def _normalize(start: Coord, end: Coord) -> tuple[Coord, Coord]:
        """Sort two opposite corners into (low corner, high corner) per axis."""
        return (
            Coord(*(min(a, b) for a, b in zip(start, end))),
            Coord(*(max(a, b) for a, b in zip(start, end))),
        )
