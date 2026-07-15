from apps.contracts.block_status import BlockStatus


class Map:
    def __init__(self, size: int):
        self.size = size
        self._blocks = {}  # only non-default blocks stored

    def get_block(self, x: int, y: int, z: int) -> BlockStatus:
        self.validate(x, y, z)
        return self._blocks.get((x, y, z), BlockStatus.Inactive)

    def set_block(self, x: int, y: int, z: int, status: BlockStatus):
        self.validate(x, y, z)
        if status == BlockStatus.Inactive:
            self._blocks.pop((x, y, z), None)
        else:
            self._blocks[(x, y, z)] = status

    def blocks_count(self) -> int:
        return self.size**3

    def active_blocks_count(self) -> int:
        return len(self._blocks)

    def validate(self, x: int, y: int, z: int):
        if not all(0 <= c < self.size for c in (x, y, z)):
            raise ValueError(f"({x}, {y}, {z}) out of bounds for size {self.size}")
