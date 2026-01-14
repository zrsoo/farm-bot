from __future__ import annotations

from datetime import datetime
from pathlib import Path

import cv2
import numpy as np


def _ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def save_bgr_png(out_dir: Path, prefix: str, frame_bgr: np.ndarray) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{prefix}_{_ts()}.png"
    ok = cv2.imwrite(str(path), frame_bgr)
    if not ok:
        raise RuntimeError(f"Failed to write image: {path}")
    return path
