# MetinFarmBot / `game_watcher` 🕵️‍♂️🖥️🎮

A Windows tool that watches a game window, detects a specific UI text label via **template matching** (no OCR), then performs a deterministic sequence of clicks/keys. Built to be **safe, debuggable, and configurable**.

---

## What it does ✅

* Captures the game window every **3–4 seconds**
* Searches the frame for a **known UI text** (same phrase per run) using **OpenCV template matching**
* Clicks the detected text (it can appear **anywhere** on screen)
* Performs a configured action sequence (keys + fixed/relative clicks)
* Waits a cooldown and repeats **forever** 🔁

---

## Why template matching (not OCR) 🧠

The target text is visually consistent:

* same color, scale, font, outline
* shown inside a UI box that may be semi-transparent (background changes)

Template matching treats the target as pixels (not “readable text”), which is often **more reliable than OCR** for tiny game fonts.

---

## Key idea: “background” means pixels inside the matched patch 🎯

Even if the UI panel looks “constant,” the semi-transparent fill blends with the landscape. If your template includes too much of that blended area, matches get unstable.

**Rule:** crop templates tight around stable features:

* text glyphs and outline ✅
* border edges ✅
* avoid large translucent fill regions ❌

---

## How it’s built 🧩

### Architecture (high level)

* **State machine**: standby → triggered → action sequence → cooldown
* **Vision engine**: capture + preprocess + template match + hit confirmation
* **Action executor**: click/keys/sleeps (config-driven)
* **Safety controls**: kill switch, pause toggle, rate limit
* **Debug artifacts**: saved frames + annotated matches for tuning

---

## Tech stack 🧰

* Python 3.11+
* `opencv-python`, `numpy` (vision)
* `dxcam` (primary capture), `mss` (fallback)
* `pywin32` (window targeting + coords)
* `pydirectinput` / `pyautogui` (input)
* `pynput` (global hotkeys)
* `pydantic` + `pyyaml` (validated YAML config)
* `logging` + rotating file logs

---

## Project structure 📁

```
config/                 # YAML configs
templates/<pack>/       # template packs (swap target text by pack)
artifacts/logs/         # logs
artifacts/debug_frames/ # saved frames + annotated matches

src/game_watcher/       # package code
tests/                  # unit tests (config + later offline vision tests)
```

---

## Configuration 🔧

Everything important is config-driven (validated with Pydantic):

* scan interval / cooldown
* window title regex + “must be foreground”
* capture backend (`dxcam` or `mss`)
* vision mode + thresholds
* active template pack + template files
* action sequence
* kill/pause keys + rate limits
* debug frame saving

See: `config/default.yaml`

---

## Vision modes 👀

* **edges** (default ✅): grayscale → blur → Canny edges → match edges
  Best for semi-transparent UI boxes since it focuses on outlines.
* **raw**: direct grayscale match (more fragile)
* **masked**: match only stable pixels (most robust, more setup)

---

## Safety features 🛑

Non-negotiable:

* **Dry-run mode** (default): logs actions but doesn’t click/type
* **Kill switch** (e.g., `F8`): hard stop
* **Pause toggle** (e.g., `F9`)
* **Rate limiting**: max triggers/minute
* **Foreground enforcement**: won’t act unless game window is focused

---

## Requirements / Assumptions ⚠️

For template matching to be reliable:

* Game must run **Borderless Windowed**
* Resolution + UI scale + Windows scaling must stay **fixed**
* Target text appearance must be consistent within a run
* Capture must return real frames (not black frames)

---

## Setup & run ▶️

### Install deps (inside venv)

```powershell
pip install -e ".[dev]"
```

### Run scaffold (dry-run)

```powershell
python -m game_watcher --config config/default.yaml --dry-run
```

### Tests

```powershell
pytest -q
```

---

## Tuning workflow 🧪

1. Create a template pack:

* `templates/my_target/t1.png` (tight crop around text/outline)

2. Run in **dry-run**:

* verify stable match scores + correct match location
* inspect `artifacts/debug_frames/` (when enabled)

3. Tune:

* `vision.threshold`
* `vision.require_consecutive_hits`
* add more templates to the pack if needed

4. Only then enable live actions (remove dry-run) 🚀

---

## What’s implemented so far ✅

* Project scaffold + config validation + logging
* CLI entrypoint (`python -m game_watcher`)
* A basic unit test confirming config load

**Not implemented yet:** capture/matching/actions loop (next milestone).

---

## Notes 📝

* This project is intentionally deterministic — no “AI agent” logic.
* If the game blocks capture or input injection, we adapt within legit methods (e.g., borderless windowing, backend fallback). No tampering/injection.

---