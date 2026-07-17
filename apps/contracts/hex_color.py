import re
from dataclasses import dataclass

_HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


@dataclass(frozen=True)
class HexColor:
    value: str

    def __post_init__(self) -> None:
        if not _HEX_RE.fullmatch(self.value):
            raise ValueError(f"Invalid hex color: {self.value!r}")
        object.__setattr__(self, "value", self.value.upper())
