from __future__ import annotations

import cv2
import numpy as np


def to_gray(bgr: np.ndarray) -> np.ndarray:
    if bgr.ndim != 3 or bgr.shape[2] != 3:
        raise ValueError(f"Expected BGR image (H,W,3). Got {bgr.shape}")
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

def edges_from_gray(gray: np.ndarray, low: int, high: int, blur_ksize: int) -> np.ndarray:
    if blur_ksize and blur_ksize > 0:
        k = blur_ksize if blur_ksize % 2 == 1 else blur_ksize + 1
        gray = cv2.GaussianBlur(gray, (k, k), 0)
    return cv2.Canny(gray, low, high)
