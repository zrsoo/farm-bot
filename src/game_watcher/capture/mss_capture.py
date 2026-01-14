from __future__ import annotations

import mss
import numpy as np

from .base import CaptureBackend, Region


class MSSCapture(CaptureBackend):
    def __init__(self) -> None:
        self._sct = mss.mss()

    def grab(self, region: Region) -> np.ndarray | None:
        monitor = {
            "left": int(region.left),
            "top": int(region.top),
            "width": int(region.width),
            "height": int(region.height),
        }

        shot = self._sct.grab(monitor)  # BGRA
        img = np.array(shot, dtype=np.uint8)

        if img.ndim != 3 or img.shape[2] < 3:
            return None

        # Convert BGRA -> BGR (drop alpha)
        return img[:, :, :3]

    def close(self) -> None:
        try:
            self._sct.close()
        except Exception:
            pass
