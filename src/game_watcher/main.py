from __future__ import annotations

import argparse
import logging
from pathlib import Path

from game_watcher.command.command import create_command

from .config_model import load_config
from .logging_setup import setup_logging


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="game-watcher", description="Screen watcher scaffold")
    p.add_argument("--config", type=str, default="config/default.yaml", help="Path to YAML config")
    p.add_argument("--dry-run", action="store_true", help="Force dry-run (no clicks/keys)")
    p.add_argument("--log-dir", type=str, default="artifacts/logs", help="Log directory")

    p.add_argument("--diag-window", action="store_true", help="Print matched window + client rect and exit")
    p.add_argument(
        "--focus-wait",
        type=float,
        default=0.0,
        help="Seconds to wait before checking foreground (use with --diag-window)",
    )
    
    p.add_argument("--diag-capture", action="store_true", help="Capture window client area and save PNG(s), then exit")
    p.add_argument("--frames", type=int, default=1, help="Number of frames to capture in --diag-capture")
    p.add_argument("--frame-interval", type=float, default=1.0, help="Seconds between frames in --diag-capture")
    
    p.add_argument("--match-pic", type=str, help="Test templates against static image (path to image file)")
    
    return p


def main() -> int:
    args = build_arg_parser().parse_args()

    cfg_path = Path(args.config).resolve()
    log_dir = Path(args.log_dir).resolve()

    logger = setup_logging(log_dir, level=logging.INFO)
    logger.info("Starting game-watcher scaffold")
    logger.info("Config: %s", cfg_path)

    cfg = load_config(cfg_path)

    if args.dry_run:
        cfg.app.dry_run = True

    command = create_command(args)
    return command.execute(cfg, logger)