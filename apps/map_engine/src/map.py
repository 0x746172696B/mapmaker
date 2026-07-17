from collections.abc import Iterator

from apps.contracts.block import Block
from apps.contracts.block_status import BlockStatus
from apps.contracts.coord import Coord
from apps.contracts.hex_color import HexColor

_INACTIVE = Block()


class Map:
    def __init__(self, size: int):
        self.size = size
        self._blocks: dict[Coord, Block] = {}  # only non-default blocks stored

    def get_block(self, coord: Coord) -> Block:
        self.validate(coord)
        return self._blocks.get(coord, _INACTIVE)

    def set_block(self, coord: Coord, *, color: HexColor, status: BlockStatus) -> None:
        self.validate(coord)
        if status is BlockStatus.Inactive:
            self._blocks.pop(coord, None)
        else:
            self._blocks[coord] = Block(status=status, color=color)

    def active_blocks(self) -> Iterator[Coord]:
        yield from self._blocks

    def blocks(self) -> Iterator[tuple[Coord, Block]]:
        """(coord, block) pairs for every active block."""
        yield from self._blocks.items()

    def blocks_count(self) -> int:
        return self.size**3

    def active_blocks_count(self) -> int:
        return len(self._blocks)

    def validate(self, coord: Coord) -> None:
        if not all(0 <= c < self.size for c in (coord.x, coord.y, coord.z)):
            raise ValueError(f"{coord} out of bounds for size {self.size}")

    @classmethod
    def from_state(cls, entry: dict) -> "Map":
        """Rebuild a Map from one persisted entry: {"size": int, "blocks": [...]}."""
        m = cls(entry["size"])
        for b in entry["blocks"]:
            m.set_block(
                Coord(*b["pos"]),
                status=BlockStatus.Active,
                color=HexColor(b["color"]),
            )
        return m
