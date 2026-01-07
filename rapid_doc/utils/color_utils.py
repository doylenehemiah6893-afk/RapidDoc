from __future__ import annotations

from typing import Iterable, Optional, Tuple

import numpy as np


def _normalize_bbox(bbox: object) -> Optional[Tuple[int, int, int, int]]:
    if bbox is None:
        return None
    if hasattr(bbox, "bbox"):
        bbox = bbox.bbox
    if isinstance(bbox, np.ndarray):
        bbox = bbox.tolist()
    if not isinstance(bbox, (list, tuple)):
        return None
    if len(bbox) == 4 and all(isinstance(v, (int, float)) for v in bbox):
        x0, y0, x1, y1 = bbox
        return int(min(x0, x1)), int(min(y0, y1)), int(max(x0, x1)), int(max(y0, y1))
    if len(bbox) == 4 and all(isinstance(v, (list, tuple, np.ndarray)) for v in bbox):
        points = np.array(bbox, dtype=np.float32).reshape(-1, 2)
        x0, y0 = np.min(points, axis=0)
        x1, y1 = np.max(points, axis=0)
        return int(x0), int(y0), int(x1), int(y1)
    return None


def _clip_rect(rect: Tuple[int, int, int, int], shape: Tuple[int, ...]) -> Optional[Tuple[int, int, int, int]]:
    height, width = shape[:2]
    x0, y0, x1, y1 = rect
    x0 = max(0, min(x0, width))
    x1 = max(0, min(x1, width))
    y0 = max(0, min(y0, height))
    y1 = max(0, min(y1, height))
    if x1 <= x0 or y1 <= y0:
        return None
    return x0, y0, x1, y1


def _to_rgb(img: np.ndarray, img_mode: str) -> np.ndarray:
    if img_mode.lower() == "bgr":
        return img[..., ::-1]
    return img


def _median_color(pixels: np.ndarray) -> Tuple[int, int, int]:
    if pixels.size == 0:
        return (0, 0, 0)
    med = np.median(pixels, axis=0)
    return tuple(int(v) for v in med.tolist())


def estimate_text_colors(
    img: np.ndarray,
    bbox: object,
    img_mode: str = "rgb",
    min_pixels: int = 16,
) -> Tuple[Optional[Tuple[int, int, int]], Optional[Tuple[int, int, int]]]:
    rect = _normalize_bbox(bbox)
    if rect is None:
        return None, None
    rect = _clip_rect(rect, img.shape)
    if rect is None:
        return None, None
    x0, y0, x1, y1 = rect
    region = img[y0:y1, x0:x1]
    if region.size == 0:
        return None, None
    region = _to_rgb(region, img_mode)
    pixels = region.reshape(-1, 3)
    if pixels.shape[0] < min_pixels:
        median_color = _median_color(pixels)
        return median_color, median_color

    luminance = (
        0.299 * pixels[:, 0] + 0.587 * pixels[:, 1] + 0.114 * pixels[:, 2]
    )
    threshold = np.median(luminance)
    bg_mask = luminance >= threshold
    fg_mask = ~bg_mask
    if np.count_nonzero(bg_mask) < min_pixels:
        bg_mask = ~bg_mask
        fg_mask = ~bg_mask
    if np.count_nonzero(fg_mask) < min_pixels:
        fg_mask = ~bg_mask

    bg_color = _median_color(pixels[bg_mask])
    fg_color = _median_color(pixels[fg_mask])
    return bg_color, fg_color
