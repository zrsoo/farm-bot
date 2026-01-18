from __future__ import annotations

import time
from pathlib import Path

import cv2
import numpy as np

from .matcher import MatchResult


def draw_match(bgr: np.ndarray, match: MatchResult, label: str) -> np.ndarray:
    out = bgr.copy()
    x, y = match.top_left
    w, h = match.size
    cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.circle(out, match.center, 4, (0, 255, 0), -1)
    cv2.putText(out, label, (x, max(0, y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    return out

def save_debug_frame(out_dir: Path, prefix: str, bgr: np.ndarray) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = out_dir / f"{prefix}_{ts}.png"
    cv2.imwrite(str(path), bgr)
    return path
