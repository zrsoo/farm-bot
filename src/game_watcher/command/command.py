from abc import ABC, abstractmethod
from pathlib import Path


class Command(ABC):
    @abstractmethod
    def execute(self, cfg, logger) -> int:
        pass


class DiagWindowCommand(Command):
    def __init__(self, focus_wait: float):
        self.focus_wait = focus_wait

    def execute(self, cfg, logger) -> int:
        import time

        from ..windowing.win32_window import (
            find_window_by_title_regex,
            get_client_rect_in_screen,
            is_foreground,
        )

        hwnds = find_window_by_title_regex(cfg.window.title_regex)
        if not hwnds:
            logger.error("No windows matched title_regex=%s", cfg.window.title_regex)
            return 2

        hwnd = hwnds[0]
        info = get_client_rect_in_screen(hwnd)

        logger.info("Matched window: hwnd=%s title=%r", info.hwnd, info.title)
        logger.info(
            "Client rect (screen): L=%d T=%d W=%d H=%d",
            info.client_left,
            info.client_top,
            info.client_width,
            info.client_height,
        )

        if self.focus_wait > 0:
            logger.info("Focus-wait: %.2fs. Switch to the game window now.", self.focus_wait)
            time.sleep(self.focus_wait)

        logger.info("Foreground=%s", is_foreground(hwnd))
        return 0


class DiagCaptureCommand(Command):
    def __init__(self, focus_wait: float, frames: int, frame_interval: float):
        self.focus_wait = focus_wait
        self.frames = frames
        self.frame_interval = frame_interval

    def execute(self, cfg, logger) -> int:
        import time

        from ..capture import Region, create_capture_backend
        from ..debug.artifacts import save_bgr_png
        from ..windowing.win32_window import (
            find_window_by_title_regex,
            get_client_rect_in_screen,
            is_foreground,
        )

        hwnds = find_window_by_title_regex(cfg.window.title_regex)
        if not hwnds:
            logger.error("No windows matched title_regex=%s", cfg.window.title_regex)
            return 2

        hwnd = hwnds[0]
        win = get_client_rect_in_screen(hwnd)

        logger.info("Matched window: hwnd=%s title=%r", win.hwnd, win.title)
        logger.info("Client rect (screen): L=%d T=%d W=%d H=%d", 
                   win.client_left, win.client_top, win.client_width, win.client_height)

        if self.focus_wait > 0:
            logger.info("Focus-wait: %.2fs. Switch to the game window now.", self.focus_wait)
            time.sleep(self.focus_wait)

        fg = is_foreground(hwnd)
        logger.info("Foreground=%s", fg)

        region = Region(left=win.client_left, top=win.client_top, 
                       width=win.client_width, height=win.client_height)

        cap = create_capture_backend(cfg.capture.backend)
        try:
            for i in range(max(1, self.frames)):
                frame = cap.grab(region)
                if frame is None:
                    logger.error("Capture failed (backend=%s). Try switching backend to mss or ensure borderless windowed.", cfg.capture.backend)
                    return 3

                logger.info("Captured frame #%d: shape=%s dtype=%s", i + 1, frame.shape, frame.dtype)

                out_path = save_bgr_png(Path("artifacts/debug_frames"), "capture", frame)
                logger.info("Saved: %s", out_path)

                if i + 1 < self.frames:
                    time.sleep(max(0.0, self.frame_interval))
        finally:
            try:
                cap.close()
            except Exception:
                pass

        return 0


class MatchPicCommand(Command):
    def __init__(self, image_path: str):
        self.image_path = Path(image_path)

    def execute(self, cfg, logger) -> int:
        import cv2
        
        if not self.image_path.exists():
            logger.error("Image file not found: %s", self.image_path)
            return 2

        # Load image
        try:
            frame_bgr = cv2.imread(str(self.image_path))
            if frame_bgr is None:
                logger.error("Failed to load image: %s", self.image_path)
                return 2
            logger.info("Loaded image: %s (shape=%s)", self.image_path, frame_bgr.shape)
        except Exception as e:
            logger.error("Error loading image: %s", e)
            return 2

        # Load templates from all packs in templates directory
        from ..vision.debug import draw_match, save_debug_frame
        from ..vision.matcher import TemplateMatcher
        from ..vision.preprocess import edges_from_gray, to_gray
        from ..vision.templates import load_templates

        templates_dir = Path("templates")  # Hardcoded as per requirement
        if not templates_dir.exists():
            logger.error("Templates directory not found: %s", templates_dir.absolute())
            return 2

        # Load all templates from templates directory
        all_templates = []
        for pack_dir in templates_dir.iterdir():
            logger.info("MUIE")
            if pack_dir.is_dir():
                try:
                    logger.info("MUIE")
                    
                    all_templates = load_templates(
                        pack_dir,
                        cfg.vision.canny.low,
                        cfg.vision.canny.high,
                        cfg.vision.canny.blur_ksize,
                    )
                    logger.info("Loaded %d templates from pack: %s", len(all_templates), pack_dir.name)
                except Exception as e:
                    logger.warning("Failed to load templates from %s: %s", pack_dir, e)

        if not all_templates:
            logger.error("No templates loaded from %s", templates_dir.absolute())
            return 2

        logger.info("Total templates loaded: %d", len(all_templates))

        # Initialize matcher
        matcher = TemplateMatcher(all_templates, cfg.vision.match.method, cfg.vision.match.scales)

        # Process image
        gray = to_gray(frame_bgr)
        edges = edges_from_gray(gray, cfg.vision.canny.low, cfg.vision.canny.high, cfg.vision.canny.blur_ksize)

        # Find best match
        best = matcher.match_best(gray, edges, cfg.vision.mode)
        if best is None:
            logger.info("No match computed (templates too large or none loaded)")
            return 0

        # Determine match quality
        hit = best.score >= cfg.vision.match.threshold
        near = (not hit) and (best.score >= cfg.vision.match.near_miss)

        # Create debug output directory
        debug_dir = Path("artifacts/debug_hits")
        debug_dir.mkdir(parents=True, exist_ok=True)

        if hit:
            label = f"HIT {best.template_name} score={best.score:.4f}"
            logger.info("✓ %s at position (%d, %d)", label, best.center[0], best.center[1])
            
            annotated = draw_match(frame_bgr, best, label)
            save_debug_frame(debug_dir, "static_hit", annotated)
            logger.info("Saved annotated image to: %s", debug_dir / "static_hit_*.png")
            
        elif near:
            label = f"NEAR {best.template_name} score={best.score:.4f}"
            logger.info("~ %s at position (%d, %d)", label, best.center[0], best.center[1])
            
            annotated = draw_match(frame_bgr, best, label)
            save_debug_frame(debug_dir, "static_near", annotated)
            logger.info("Saved annotated image to: %s", debug_dir / "static_near_*.png")
            
        else:
            logger.info("✗ MISS - best match: %s score={%.4f} (threshold=%.4f)", 
                       best.template_name, best.score, cfg.vision.match.threshold)

        return 0


class RunCommand(Command):
    def execute(self, cfg, logger) -> int:
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
                    cfg.safety.kill_switch_key, cfg.safety.pause_toggle_key, cfg.safety.max_triggers_per_minute)

        logger.warning("Scaffold only: capture/matching/actions not implemented yet.")
        logger.warning("Next step: implement dry-run capture + match + debug frame saving.")
        return 0
    
    
def create_command(args) -> Command:
    if args.diag_window:
        return DiagWindowCommand(args.focus_wait)
    elif args.diag_capture:
        return DiagCaptureCommand(args.focus_wait, args.frames, args.frame_interval)
    elif args.match_pic:
        return MatchPicCommand(args.match_pic)
    else:
        return RunCommand()