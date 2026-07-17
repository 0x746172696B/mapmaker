from dataclasses import dataclass
from .coord import Coord
from .hex_color import HexColor


@dataclass(frozen=True, kw_only=True)
class BaseAction:
    color: HexColor = HexColor("#808080")


@dataclass(frozen=True, kw_only=True)
class Fill(BaseAction):
    start: Coord
    end: Coord


@dataclass(frozen=True, kw_only=True)
class HollowBox(BaseAction):
    start: Coord
    end: Coord


@dataclass(frozen=True, kw_only=True)
class Cylinder(BaseAction):
    center: Coord
    radius: int
    height: int


Action = Fill | HollowBox | Cylinder
