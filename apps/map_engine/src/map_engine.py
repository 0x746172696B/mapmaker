import uuid

from apps.contracts.block_status import BlockStatus


class Map:
    def __init__(self, size: int):
        self.size = size
        self._blocks = {}  # only non-default blocks stored

    def get_block(self, x: int, y: int, z: int) -> BlockStatus:
        self._validate(x, y, z)
        return self._blocks.get((x, y, z), BlockStatus.Inactive)

    def set_block(self, x: int, y: int, z: int, status: BlockStatus):
        self._validate(x, y, z)
        if status == BlockStatus.Inactive:
            self._blocks.pop((x, y, z), None)
        else:
            self._blocks[(x, y, z)] = status

    def blocks_count(self) -> int:
        return self.size**3

    def active_blocks_count(self) -> int:
        return len(self._blocks)

    def _validate(self, x: int, y: int, z: int):
        if not all(0 <= c < self.size for c in (x, y, z)):
            raise ValueError(f"({x}, {y}, {z}) out of bounds for size {self.size}")


class MapEngine:
    def __init__(self):
        self._maps = {}

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
