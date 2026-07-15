from dataclasses import dataclass
from .coord import Coord


@dataclass(frozen=True)
class Fill:
    start: Coord
    end: Coord


@dataclass(frozen=True)
class HollowBox:
    start: Coord
    end: Coord


@dataclass(frozen=True)
class Cylinder:
    center: Coord
    radius: int
    height: int


Action = Fill | HollowBox | Cylinder
