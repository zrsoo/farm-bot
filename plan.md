* [x] 0. Pre-flight decisions (scope + approach)

  * [x] 0.1 Confirm detection strategy: template matching (not OCR)
  * [x] 0.2 Confirm constraints: fixed resolution/UI scale; borderless windowed required
  * [x] 0.3 Define safety baseline: dry-run first, kill switch + pause toggle
  * [x] 0.4 Draft and agree on architecture: state machine + capture + vision + actions + safety + debug

* [x] 1. Environment setup (Windows)

  * [x] 1.1 Install Python 3.11+ (3.11/3.12)
  * [x] 1.2 Create project folder (MetinFarmBot / game_watcher)
  * [x] 1.3 Create and activate virtual environment (.venv)
  * [x] 1.4 Install dependencies (opencv, numpy, dxcam, mss, pywin32, pydirectinput, pynput, pydantic, pyyaml, etc.)
  * [x] 1.5 Verify imports / sanity-check environment
  * [x] 1.6 Confirm tooling works (pytest runs)

* [x] 2. Project scaffold (codebase wiring)

  * [x] 2.1 Create folder structure (src/, config/, templates/, artifacts/, tests/)
  * [x] 2.2 Add pyproject.toml (dependencies, scripts, src layout)
  * [x] 2.3 Add config/default.yaml (dry_run enabled, placeholder window title regex, template pack placeholder)
  * [x] 2.4 Implement config schema + loader (Pydantic + YAML)
  * [x] 2.5 Implement logging (console + rotating log file)
  * [x] 2.6 Implement CLI entrypoint (python -m game_watcher --config ... --dry-run)
  * [x] 2.7 Add basic unit test for config load (tests/test_config_load.py)
  * [x] 2.8 Validate scaffold end-to-end

    * [x] 2.8.1 pytest -q passes
    * [x] 2.8.2 python -m game_watcher runs and prints config/log info

* [x] 3. Window targeting (find correct game window reliably)

  * [ ] 3.1 Decide the targeting key
    * [x] 3.1.1 Use window title regex (default) and/or process name (optional later)
  * [x] 3.2 Implement window discovery (pywin32)

    * [ ] 3.2.1 Enumerate top-level windows
    * [ ] 3.2.2 Filter by title regex
    * [ ] 3.2.3 Select best candidate (first match or “largest client area”)
  * [x] 3.3 Implement client-area geometry

    * [x] 3.3.1 Get window rect + client rect
    * [x] 3.3.2 Convert client coords -> screen coords (ClientToScreen)
    * [x] 3.3.3 Return (client_left, client_top, client_width, client_height)
  * [x] 3.4 Implement focus/visibility checks

    * [x] 3.4.1 require_foreground: verify GetForegroundWindow == target
    * [x] 3.4.2 verify window is not minimized
  * [x] 3.5 Add a CLI “diagnostic” run mode (no vision yet)

    * [x] 3.5.1 Print selected window title + geometry each tick (or once)
    * [x] 3.5.2 Save results in logs
  * [x] 3.6 Update config/default.yaml with real title_regex for the game window

* [x] 4. Frame capture (dry-run: capture only, no matching yet)

  * [x] 4.1 Implement capture interface (base class)

    * [x] 4.1.1 capture_frame(region) -> numpy image (BGR/RGB defined)
    * [x] 4.1.2 backend selection via config (dxcam/mss)
  * [x] 4.2 Implement dxcam backend

    * [x] 4.2.1 Initialize dxcam camera
    * [x] 4.2.2 Capture region = window client area
    * [x] 4.2.3 Handle failure/None frames robustly
  * [x] 4.3 Implement mss backend (fallback)

    * [x] 4.3.1 Capture region = window client area
    * [x] 4.3.2 Convert to numpy array
  * [ ] 4.4 Implement capture sanity checks

    * [ ] 4.4.1 Detect “black frame” / near-blank frame
    * [x] 4.4.2 Log backend + frame size + basic stats
  * [x] 4.5 Add capture-only command path

    * [x] 4.5.1 Save frame to artifacts/debug_frames/
    * [x] 4.5.2 Save at least one timestamped PNG
  * [x] 4.6 Manual validation

    * [x] 4.6.1 Run with game open and focused
    * [x] 4.6.2 Confirm saved images show the game correctly (not black)

* [ ] 5. Template pack setup (assets + conventions)

  * [ ] 5.1 Create first real template pack

    * [ ] 5.1.1 templates/<pack_name>/t1.png (tight crop)
    * [ ] 5.1.2 (optional) t2.png, t3.png captured in slightly different scenes
  * [ ] 5.2 Template design rules

    * [ ] 5.2.1 Crop tightly around stable text glyphs/outline
    * [ ] 5.2.2 Avoid large translucent panel fill pixels
    * [ ] 5.2.3 Keep resolution/UI scale unchanged between capture and runtime
  * [ ] 5.3 Update config/default.yaml

    * [ ] 5.3.1 templates.active_pack = <pack_name>
    * [ ] 5.3.2 templates.files = ["t1.png", ...]
  * [ ] 5.4 Add a “template loader” utility

    * [ ] 5.4.1 Validate template files exist
    * [ ] 5.4.2 Load templates into memory (numpy arrays)
    * [ ] 5.4.3 Log loaded template sizes

* [ ] 6. Vision preprocessing + matching (dry-run detection only)

  * [ ] 6.1 Define image format conventions

    * [ ] 6.1.1 Decide BGR vs RGB internally
    * [ ] 6.1.2 Normalize grayscale conversion
  * [ ] 6.2 Implement preprocessing modes

    * [ ] 6.2.1 raw: grayscale
    * [ ] 6.2.2 edges: grayscale -> blur -> Canny
    * [ ] 6.2.3 masked: (later) apply mask to ignore unstable pixels
  * [ ] 6.3 Implement template matching

    * [ ] 6.3.1 For each template in active pack:

      * [ ] 6.3.1.1 Run cv2.matchTemplate on preprocessed frame/template
      * [ ] 6.3.1.2 Extract best score + location
    * [ ] 6.3.2 Choose best template match overall (max score)
    * [ ] 6.3.3 Apply threshold + (optional) consecutive-hit requirement
  * [ ] 6.4 Implement debug artifacts for vision

    * [ ] 6.4.1 On match: save annotated frame (box + score + template name)
    * [ ] 6.4.2 On near-miss: save annotated frame when score >= near_miss_threshold
    * [ ] 6.4.3 Log score, location, template id, frame size
  * [ ] 6.5 Manual tuning loop (still dry-run)

    * [ ] 6.5.1 Adjust vision.threshold
    * [ ] 6.5.2 Adjust require_consecutive_hits (0/1/2)
    * [ ] 6.5.3 Add more templates to pack if needed
    * [ ] 6.5.4 Confirm low false positives over time

* [ ] 7. Coordinate mapping (turn match location into click point)

  * [ ] 7.1 Compute click target

    * [ ] 7.1.1 Use match top-left + template size -> center point (frame-local)
  * [ ] 7.2 Convert to absolute screen coords

    * [ ] 7.2.1 screen_x = client_left + local_x
    * [ ] 7.2.2 screen_y = client_top + local_y
  * [ ] 7.3 Validate mapping (still dry-run)

    * [ ] 7.3.1 Log computed screen coords
    * [ ] 7.3.2 Save annotated image with center point
    * [ ] 7.3.3 Optional: show a “mouse move only” mode (no clicks)

* [ ] 8. Safety controls (kill/pause/rate limit) — implement before live actions

  * [ ] 8.1 Kill switch (global hotkey)

    * [ ] 8.1.1 Press F8 -> immediate stop
  * [ ] 8.2 Pause toggle

    * [ ] 8.2.1 Press F9 -> pause scanning and actions
    * [ ] 8.2.2 Press F9 again -> resume
  * [ ] 8.3 Rate limiting

    * [ ] 8.3.1 Track triggers in sliding 60s window
    * [ ] 8.3.2 If exceeded: skip actions and log
  * [ ] 8.4 Foreground enforcement

    * [ ] 8.4.1 If require_foreground and not focused: skip actions and log

* [ ] 9. Actions engine (still safe: dry-run + then live)

  * [ ] 9.1 Define supported action steps

    * [ ] 9.1.1 sleep(seconds)
    * [ ] 9.1.2 key(keys[])
    * [ ] 9.1.3 click_abs(x,y)
    * [ ] 9.1.4 click_rel(x,y) relative to window client area
    * [ ] 9.1.5 click_detected(center of match)
  * [ ] 9.2 Implement executor

    * [ ] 9.2.1 Dry-run: log every action only
    * [ ] 9.2.2 Live: perform using pydirectinput (fallback pyautogui if needed)
  * [ ] 9.3 Add configurable delays between actions
  * [ ] 9.4 Manual validation (first with harmless actions)

    * [ ] 9.4.1 Live test: single key press
    * [ ] 9.4.2 Live test: click_rel on a safe UI spot
    * [ ] 9.4.3 Live test: click_detected (only after stable detection proven)

* [ ] 10. State machine integration (full loop)

  * [ ] 10.1 Implement states

    * [ ] 10.1.1 STANDBY: capture + match every scan_interval_sec
    * [ ] 10.1.2 TRIGGERED: confirmed match -> click_detected
    * [ ] 10.1.3 ACTION_SEQUENCE: run actions.sequence
    * [ ] 10.1.4 COOLDOWN: sleep cooldown_sec
  * [ ] 10.2 Add transition logging (state changes + reasons)
  * [ ] 10.3 Ensure pause/kill works in every state

* [ ] 11. Robustness & tuning (make it survive real use)

  * [ ] 11.1 Add “consecutive hit at same-ish location” option

    * [ ] 11.1.1 Location tolerance (e.g., within N pixels) across scans
  * [ ] 11.2 Add “best-vs-second-best” margin check (optional)
  * [ ] 11.3 Add periodic health logging

    * [ ] 11.3.1 window size changes
    * [ ] 11.3.2 capture backend failures
    * [ ] 11.3.3 match score stats (avg/max over time)
  * [ ] 11.4 Add automatic fallback capture backend (dxcam -> mss)
  * [ ] 11.5 Add template pack validation command

    * [ ] 11.5.1 verify templates load + sizes
    * [ ] 11.5.2 run offline test against a stored screenshot

* [ ] 12. Packaging and operational runbook

  * [ ] 12.1 Document “how to create templates” with examples
  * [ ] 12.2 Document “safe first run” checklist

    * [ ] 12.2.1 Dry-run only
    * [ ] 12.2.2 Confirm debug frames look right
    * [ ] 12.2.3 Tune threshold and consecutive hits
    * [ ] 12.2.4 Enable live actions with strict rate limit
    * [ ] 12.2.5 Keep kill switch reachable
  * [ ] 12.3 Add a release checklist (pin deps, tag version, etc.)
  * [ ] 12.4 Optional: build a single-file runner (later) if needed

* [ ] 13. Done criteria (definition of “works”)

  * [ ] 13.1 Detect target text reliably for N minutes with near-zero false positives (dry-run)
  * [ ] 13.2 Click detected text correctly (live) without misclicks in repeated trials
  * [ ] 13.3 Execute action sequence reliably after each trigger
  * [ ] 13.4 Pause/resume works reliably
  * [ ] 13.5 Kill switch stops immediately
  * [ ] 13.6 Runs indefinitely without memory growth or log spam
