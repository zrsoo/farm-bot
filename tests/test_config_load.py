from pathlib import Path

from game_watcher.config_model import load_config


def test_load_default_config():
    cfg = load_config(Path("config/default.yaml"))
    assert cfg.app.scan_interval_sec > 0
    assert cfg.capture.backend in ("dxcam", "mss")
    assert 0.0 <= cfg.vision.threshold <= 1.0
