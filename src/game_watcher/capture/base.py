from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


@dataclass(frozen=True)
class Region:
    left: int
    top: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.left + self.width

    @property
    def bottom(self) -> int:
        return self.top + self.height


class CaptureBackend(Protocol):
    def grab(self, region: Region) -> np.ndarray | None:
        """Return a BGR uint8 image (H,W,3), or None on failure."""
        ...

    def close(self) -> None:
        ...
