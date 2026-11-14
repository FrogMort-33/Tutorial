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
- "backup, save, upload to git" = copy `extras` to `e:\python\Tutorial_backups\extras_<date>_<time>`, then commit and push.
- The user works on more than one PC: `git pull` before starting, commit + push when done.

## File split (keep it)
- `rotation_301.py` — the game loop only. `START_LEVEL` at the top picks the level (debug).
- `rotation_data.py` — colours, palettes, models, settings, shared state (`things`, `camera`, `you`, ...). No pygame.
- `rotation_functions.py` — maths, camera, drawing, clipping, collisions, sounds, `load_level`, HUD, mini-map.
- `rotation_levels.py` — `DESIGNS` (shapes, tanks) and `LEVELS` (data-driven: name, intro, world box, start, floor_shapes, boxes, spawn, optional sizes).

The files share names with `import *`, so shared lists/dicts must be **changed in place** (`list[:] = ...`, `dict.update`), never rebound.

## Fixed decisions
- The floor stays at **y = -1** on purpose (engine stress test).
- Sizes are named: HUGE 4 across / 5 hp → LARGE 2.5 / 4 → **MEDIUM 1.5 / 3** (the user's reference) → SMALL 1 / 2 → TINY 0.5 / 1 (dies). Levels can override with `"sizes"`.
- A level with nothing in `spawn` never "completes".
- Lines are trimmed at NEAR **and** to the screen edges before drawing (`draw_world_line` + `trim_line_to_screen`; decals use `trim_to_near` + `trim_to_screen`). This is what keeps big rooms fast — don't remove it.

## Levels so far
1 Training Day · 2 Fire and Ice · 3 Triple Threat · 4 Move or Die (patrolling tank) · 5 Crossfire (two tanks) ·
6 The Floor Is Lava · 7 Frozen (will not let you go!) (ice clone of 6) · 8 The Big Room (empty, 32 x 32) ·
9 The Huge Room (empty, 48 x 48) · 99 Skunk works (test level, now 48 x 48).
Levels 1–7 use a 16 x 16 x 8 room.

## Open ideas (not built yet)
- Player health / game over (lava and tank hits only count "Hits taken" for now).
- Named sizes for tanks.
- Things can overhang the world-box walls (bounce uses the centre); a surface-based bounce was proposed, not built.
