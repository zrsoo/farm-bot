from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, PositiveFloat, PositiveInt


# --- APP ---
class AppConfig(BaseModel):
    dry_run: bool = True
    scan_interval_sec: PositiveFloat = 3.5
    cooldown_sec: PositiveFloat = 2.0

# --- WINDOW ---
class WindowConfig(BaseModel):
    title_regex: str
    require_foreground: bool = True

# --- CAPTURE ---
class CaptureConfig(BaseModel):
    backend: Literal["dxcam", "mss"] = "dxcam"
    capture_window_only: bool = True

# --- VISION ---
class CannyConfig(BaseModel):
    low: int = 60
    high: int = 160
    blur_ksize: int = 3  # 0 disables

class MatchConfig(BaseModel):
    method: str = "TM_CCOEFF_NORMED"
    threshold: float = 0.5
    near_miss: float = 0.4
    scales: list[float] = Field(default_factory=lambda: [1.0])
    confirm_hits: int = 1
    min_trigger_interval_s: float = 10.0

class VisionConfig(BaseModel):
    templates_dir: Path = Path("templates")
    active_pack: str = "default"
    mode: Literal["edges", "gray"] = "edges"
    canny: CannyConfig = CannyConfig()
    match: MatchConfig = MatchConfig()


class TemplatesConfig(BaseModel):
    active_pack: str
    root_dir: str = "templates"
    files: list[str]

# --- ACTION ---
class ActionStep(BaseModel):
    type: Literal["sleep", "key", "click_abs", "click_rel"]
    seconds: float | None = None
    keys: list[str] | None = None
    x: int | None = None
    y: int | None = None


class ActionsConfig(BaseModel):
    sequence: list[ActionStep] = Field(default_factory=list)

# --- SAFETY ---
class SafetyConfig(BaseModel):
    kill_switch_key: str = "f8"
    pause_toggle_key: str = "f9"
    max_triggers_per_minute: PositiveInt = 6

# --- DEBUG ---
class DebugConfig(BaseModel):
    save_debug_frames: bool = True
    save_on_match: bool = True
    save_on_near_miss: bool = True

class Config(BaseModel):
    app: AppConfig
    window: WindowConfig
    capture: CaptureConfig
    vision: VisionConfig
    templates: TemplatesConfig
    actions: ActionsConfig
    safety: SafetyConfig
    debug: DebugConfig


def load_config(path: Path) -> Config:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return Config.model_validate(data)
