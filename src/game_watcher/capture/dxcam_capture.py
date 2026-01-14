from __future__ import annotations

import dxcam
import numpy as np

from .base import CaptureBackend, Region


class DXCamCapture(CaptureBackend):
    def __init__(self) -> None:
        # dxcam usually returns numpy arrays already.
        # We treat output as BGR-like for saving via OpenCV later.
        self._cam = dxcam.create()

    def grab(self, region: Region) -> np.ndarray | None:
        # dxcam region expects (left, top, right, bottom)
        try:
            frame = self._cam.grab(region=(int(region.left), int(region.top), int(region.right), 
                                           int(region.bottom)))
        except Exception:
            return None

        if frame is None:
            return None

        img = np.asarray(frame)
        if img.ndim != 3 or img.shape[2] < 3:
            return None

        # If it has alpha, drop it.
        if img.shape[2] == 4:
            img = img[:, :, :3]

        return img.astype(np.uint8, copy=False)

    def close(self) -> None:
        try:
            self._cam.stop()
        except Exception:
            pass
