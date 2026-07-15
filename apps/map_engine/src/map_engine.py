import uuid

from .map import Map


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
