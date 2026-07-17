from dataclasses import dataclass

from .block_status import BlockStatus
from .hex_color import HexColor


@dataclass(frozen=True, kw_only=True)
class Block:
    status: BlockStatus = BlockStatus.Inactive
    color: HexColor | None = None
