from __future__ import annotations

from .base import CaptureBackend, Region
from .dxcam_capture import DXCamCapture
from .mss_capture import MSSCapture


def create_capture_backend(name: str) -> CaptureBackend:
    name = name.lower().strip()
    if name == "dxcam":
        return DXCamCapture()
    if name == "mss":
        return MSSCapture()
    raise ValueError(f"Unknown capture backend: {name}")
