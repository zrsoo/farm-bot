from __future__ import annotations

import time

from game_watcher.vision.debug import draw_match, save_debug_frame
from game_watcher.vision.matcher import TemplateMatcher
from game_watcher.vision.preprocess import edges_from_gray, to_gray
from game_watcher.vision.templates import load_templates


class TriggerGate:
    def __init__(self, confirm_hits: int, min_interval_s: float):
        self.confirm_hits = max(1, int(confirm_hits))
        self.min_interval_s = float(min_interval_s)
        self._streak = 0
        self._last_trigger_ts = 0.0

    def observe(self, is_hit: bool) -> bool:
        now = time.time()
        if is_hit:
            self._streak += 1
        else:
            self._streak = 0

        if self._streak >= self.confirm_hits and (now - self._last_trigger_ts) >= self.min_interval_s:
            self._last_trigger_ts = now
            self._streak = 0
            return True

        return False

def init_vision(cfg):
    pack_dir = cfg.vision.templates_dir / cfg.vision.active_pack
    templates = load_templates(
        pack_dir,
        cfg.vision.canny.low,
        cfg.vision.canny.high,
        cfg.vision.canny.blur_ksize,
    )
    matcher = TemplateMatcher(templates, cfg.vision.match.method, cfg.vision.match.scales)
    gate = TriggerGate(cfg.vision.match.confirm_hits, cfg.vision.match.min_trigger_interval_s)
    return matcher, gate

def process_frame(cfg, matcher, gate, frame_bgr, client_left, client_top, logger):
    gray = to_gray(frame_bgr)
    edges = edges_from_gray(gray, cfg.vision.canny.low, cfg.vision.canny.high, cfg.vision.canny.blur_ksize)

    best = matcher.match_best(gray, edges, cfg.vision.mode)
    if best is None:
        logger.debug("No match computed (template too large / none loaded).")
        return

    hit = best.score >= cfg.vision.match.threshold
    near = (not hit) and (best.score >= cfg.vision.match.near_miss)

    if hit:
        label = f"HIT {best.template_name} sc={best.score:.4f}"
        logger.info(label)

        annotated = draw_match(frame_bgr, best, label)
        if cfg.debug.save_match_frames:
            save_debug_frame(cfg.debug.out_dir, "hit", annotated)

        # Map to screen coords for future clicking:
        screen_x = client_left + best.center[0]
        screen_y = client_top + best.center[1]

        should_trigger = gate.observe(True)
        if should_trigger:
            if cfg.safety.dry_run:
                logger.warning(f"[DRY-RUN] Would trigger action at ({screen_x},{screen_y})")
            else:
                logger.error("Non-dry-run path not wired here yet (good).")
        else:
            logger.debug("Hit observed but rate-limited / awaiting confirm_hits.")
    elif near:
        label = f"NEAR {best.template_name} sc={best.score:.4f}"
        logger.debug(label)

        annotated = draw_match(frame_bgr, best, label)
        if cfg.debug.save_near_miss_frames:
            save_debug_frame(cfg.debug.out_dir, "near", annotated)

        gate.observe(False)
    else:
        gate.observe(False)
        logger.debug(f"MISS best={best.template_name} sc={best.score:.4f}")
