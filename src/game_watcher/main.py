from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .config_model import load_config
from .logging_setup import setup_logging
from .windowing import find_window_by_title_regex, get_client_rect_in_screen, is_foreground


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="game-watcher", description="Screen watcher scaffold")
    p.add_argument("--config", type=str, default="config/default.yaml", help="Path to YAML config")
    p.add_argument("--dry-run", action="store_true", help="Force dry-run (no clicks/keys)")
    p.add_argument("--log-dir", type=str, default="artifacts/logs", help="Log directory")
    p.add_argument("--diag-window", action="store_true", help="Print matched window + client rect" +
                   " and exit")
    return p


def main() -> int:
    args = build_arg_parser().parse_args()

    cfg_path = Path(args.config).resolve()
    log_dir = Path(args.log_dir).resolve()

    logger = setup_logging(log_dir, level=logging.INFO)
    logger.info("Starting game-watcher scaffold")
    logger.info("Config: %s", cfg_path)

    cfg = load_config(cfg_path)

    if args.diag_window:
        hwnds = find_window_by_title_regex(cfg.window.title_regex)
        if not hwnds:
            logger.error("No windows matched title_regex=%s", cfg.window.title_regex)
            return 2

        # Pick the first for now (later we can pick largest client area)
        hwnd = hwnds[0]
        info = get_client_rect_in_screen(hwnd)

        logger.info("Matched window: hwnd=%s title=%r", info.hwnd, info.title)
        logger.info("Client rect (screen): L=%d T=%d W=%d H=%d", info.client_left, info.client_top, 
                    info.client_width, info.client_height)
        logger.info("Foreground=%s", is_foreground(hwnd))
        return 0

    if args.dry_run:
        cfg.app.dry_run = True

    logger.info("dry_run=%s scan_interval=%.2fs cooldown=%.2fs",
                cfg.app.dry_run, cfg.app.scan_interval_sec, cfg.app.cooldown_sec)
    logger.info("window.title_regex=%s require_foreground=%s",
                cfg.window.title_regex, cfg.window.require_foreground)
    logger.info("capture.backend=%s capture_window_only=%s",
                cfg.capture.backend, cfg.capture.capture_window_only)
    logger.info("vision.mode=%s threshold=%.3f consecutive_hits=%d",
                cfg.vision.mode, cfg.vision.threshold, cfg.vision.require_consecutive_hits)
    logger.info("templates.pack=%s files=%s",
                cfg.templates.active_pack, cfg.templates.files)
    logger.info("actions.steps=%d", len(cfg.actions.sequence))
    logger.info("safety.kill=%s pause=%s max_triggers/min=%d",
                cfg.safety.kill_switch_key, cfg.safety.pause_toggle_key, 
                cfg.safety.max_triggers_per_minute)

    logger.warning("Scaffold only: capture/matching/actions not implemented yet.")
    logger.warning("Next step: implement dry-run capture + match + debug frame saving.")

    return 0
