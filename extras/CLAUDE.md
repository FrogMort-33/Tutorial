# rotation_301 — notes for Claude

A beginner-tutorial 3D wireframe game in Python + pygame-ce (`pip install pygame-ce`).
Run it with `python rotation_301.py` from this folder. Other `rotation_*.py` / `step0_*.py` files are earlier tutorial steps.

## How the user likes to work
- **"run"** = launch `python rotation_301.py` in the background, then read the output when the game closes and ask how it felt.
- **Small changes** (a setting, colour, tweak): just make the edit and let the user test it. No headless tests or screenshots.
- **Bigger work** (refactors, new systems): verify it, e.g. a seeded headless run (`SDL_VIDEODRIVER=dummy`) comparing state/screen before and after.
- **Propose first** when the user says "propose" / "show proposal", and before any large change.
- **Chime** at the end of longer work, before the final message:
  `powershell -c "[console]::beep(660,180); [console]::beep(880,180); [console]::beep(1320,320)"`
- Explanations aimed at learners. Plain words, short.
- "backup, save, upload to git" = copy `extras` to the backups folder as `extras_<date>_<time>`, then commit and push.
  The backups folder depends on the PC: `e:\python\Tutorial_backups` where there is an E: drive,
  otherwise `C:\Users\enda_\Desktop\Python\Tutorial_backups` (the PC with no E: drive).
- The user works on more than one PC: `git pull` before starting, commit + push when done.

## File split (keep it)
- `rotation_301.py` — the game loop only. `START_LEVEL` at the top picks the level (debug).
- `rotation_data.py` — colours, palettes, models, settings, shared state (`things`, `bullets`, `camera`, `you`, ...). Bullets have their OWN list: `move_bullets()` does everything a bullet does. No pygame.
- `rotation_functions.py` — maths, camera, drawing, clipping, collisions, sounds, `load_level`, HUD, mini-map.
- `rotation_levels.py` — `DESIGNS` (shapes, tanks) and `LEVELS` (data-driven: name, intro, world box, start, floor_shapes, boxes, spawn, optional sizes).

## Icon and .exe
- Icon: the level 6 lava tank on a bright red grid. `rotation_301_icon.png` is the window/taskbar icon (loaded in `rotation_functions.py` from `GAME_FOLDER`, so it works in the .exe too); `rotation_301_icon.ico` (16-256 px) is the .exe's icon.
- Build the .exe from `extras` with `py -m PyInstaller rotation_301.spec` (needs `pip install pyinstaller`). One file, no console window. It lands in `extras/dist/rotation_301.exe`; `build/` and `dist/` are NOT in git, so rebuild on each PC.
otation_301.exe`; `build\` and `dist\` are NOT in git, so rebuild on each PC.
- `WALL_GRID_STEP` (rotation_data.py) sets the wall/ceiling grid spacing; 1 = the same as the floor.

The files share names with `import *`, so shared lists/dicts must be **changed in place** (`list[:] = ...`, `dict.update`), never rebound.

## Fixed decisions
- The floor stays at **y = -1** on purpose (engine stress test).
- Sizes are named: HUGE 4 across / 5 hp → LARGE 2.5 / 4 → **MEDIUM 1.5 / 3** (the user's reference) → SMALL 1 / 2 → TINY 0.5 / 1 (dies). Levels can override with `"sizes"`.
- A level with nothing in `spawn` never "completes".
- Lines are trimmed at NEAR **and** to the screen edges before drawing (`draw_world_line` + `trim_line_to_screen`; decals use `trim_to_near` + `trim_to_screen`). This is what keeps big rooms fast — don't remove it.
- Faces go through `face_on_screen()`: trim at NEAR, project, shoelace back-face test, trim to screen. (Skipping a face with a corner behind NEAR made big pillars vanish up close.)
- Build long level boxes as ~1-unit pieces: the painter's sort uses one distance per face, so long faces draw wrong.
- Simplest working rule first; no clever edge cases unless gameplay needs them.
- Guns: every gun is one config (`GUN_DEFAULTS`). Turrets: SPIN / OSCILLATE / TRACK (aimed in the hull's own frame, so they work on walls and ceilings). Shapes: DOWN (first lowest corner) / TARGET (first corner nearest your eye). Bullets take the firer's colours unless `bullet_colour` / `bullet_palette` are set.
- `"scenery": True` = not counted for clearing, not on the map, can't be killed (drippers, bunkers).
- Your body = a column from feet (eye − 1) to eye, `YOUR_BODY_RADIUS` wide. Boxes block you (x and z checked separately, so you slide) and you can stand on them (`STEP_UP`).
  THINGS block you too (`into_a_thing`: only steps that go DEEPER are refused, so you can always get out). A MOVING thing that touches you hurts you and bounces off (`things_bump_you`, then `BUMP_GRACE` frames).
- Every grid follows `level_look["grid_colour"]`; boxes default to it × `BOX_BRIGHTER`. A gold `ORIGIN_MARK` is at x 0, z 0 in every level.

## Levels so far
1 Training Day · 2 Fire and Ice · 3 Triple Threat · 4 Move or Die (patrolling tank) · 5 Crossfire (two tanks) ·
6 The Floor Is Lava (lava bands, drippers) · 7 Frozen (will not let you go!) (ice clone of 6) ·
8 The Canyon (32 x 32 stone ruins, floor/wall/ceiling bunkers) · 9 The Huge Room (48 x 48, one small cube) ·
99 Skunk works (48 x 48, everything shoots at you). 99 now comes after 9 (`TEST_LEVELS` is empty).
Levels 1–7 use a 16 x 16 x 8 room.

## Open ideas (not built yet)
- Player health / game over (hits only count "Hits taken" for now).
- A `make_box()` helper for building structures; health bars draw through walls; your head isn't stopped when jumping under boxes.
- Publish: screenshots, and where to share it (the .exe and icon are done).
- Named sizes for tanks.
- Things can overhang the world-box walls (bounce uses the centre); a surface-based bounce was proposed, not built.
