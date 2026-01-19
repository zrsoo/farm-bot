from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from .preprocess import edges_from_gray, to_gray


@dataclass(frozen=True)
class LoadedTemplate:
    name: str
    path: Path
    gray: np.ndarray
    edges: np.ndarray

def load_templates(pack_dir: Path, canny_low: int, canny_high: int, blur_ksize: int) -> list[LoadedTemplate]:
    if not pack_dir.exists() or not pack_dir.is_dir():
        raise FileNotFoundError(f"Template pack dir not found: {pack_dir}")

    files = sorted([p for p in pack_dir.iterdir() if p.suffix.lower() in (".png", ".jpg", ".jpeg")])
    if not files:
        raise FileNotFoundError(f"No template images in pack: {pack_dir}")

    out: list[LoadedTemplate] = []
    for p in files:
        bgr = cv2.imread(str(p), cv2.IMREAD_COLOR)
        if bgr is None:
            raise RuntimeError(f"Failed to read template: {p}")

        gray = to_gray(bgr)
        edges = edges_from_gray(gray, canny_low, canny_high, blur_ksize)

        out.append(LoadedTemplate(name=p.stem, path=p, gray=gray, edges=edges))

    return out
