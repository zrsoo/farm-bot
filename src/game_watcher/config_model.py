from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, PositiveFloat, PositiveInt


class AppConfig(BaseModel):
    dry_run: bool = True
    scan_interval_sec: PositiveFloat = 3.5
    cooldown_sec: PositiveFloat = 2.0


class WindowConfig(BaseModel):
    title_regex: str
    require_foreground: bool = True


class CaptureConfig(BaseModel):
    backend: Literal["dxcam", "mss"] = "dxcam"
    capture_window_only: bool = True


class VisionConfig(BaseModel):
    mode: Literal["raw", "edges", "masked"] = "edges"
    threshold: float = Field(0.88, ge=0.0, le=1.0)
    require_consecutive_hits: PositiveInt = 1


class TemplatesConfig(BaseModel):
    active_pack: str
    root_dir: str = "templates"
    files: list[str]


class ActionStep(BaseModel):
    type: Literal["sleep", "key", "click_abs", "click_rel"]
    seconds: float | None = None
    keys: list[str] | None = None
    x: int | None = None
    y: int | None = None


class ActionsConfig(BaseModel):
    sequence: list[ActionStep] = Field(default_factory=list)


class SafetyConfig(BaseModel):
    kill_switch_key: str = "f8"
    pause_toggle_key: str = "f9"
    max_triggers_per_minute: PositiveInt = 6


class DebugConfig(BaseModel):
    save_debug_frames: bool = True
    save_on_match: bool = True
    save_on_near_miss: bool = True
    near_miss_threshold: float = Field(0.80, ge=0.0, le=1.0)


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
