# rotation_levels.py - the LEVELS for rotation_301: what each level holds, and where.
#   DESIGNS - what each kind of thing IS (a tank, a cube ...), written ONCE.
#   LEVELS  - each level: its size, where you start, its floor shapes, its boxes, and what it SPAWNS.
# load_level(number) in rotation_functions.py builds a level from this data. It always COPIES:
# the data here is never changed by the game, so loading a level again always starts it fresh.
from rotation_data import *          # the models and palettes


# ================================ DESIGNS ================================
# What each kind of thing IS. A level's "spawn" entry names a design, then lists only what's DIFFERENT
# (where it is, how it moves, its size ...). Any field a thing can have may go in a design (see THINGS in
# rotation_data.py). Fields a design leaves out get these defaults when it's built:
#   "velocity" [0, 0, 0] (parked)   "size" 1   "angles" [0, 0, 0] (facing +z)   "speeds" (0, 0, 0) (no spin)
#
# COLOURS: every design is GREY ("colour": GREY, "palette": PALETTE_GREY) on purpose. EVERY spawn in a level must
# give its own "colour" and "palette": a thing that shows up grey has been missed (load_level prints a warning).
#
# "children": parts built ON the thing, that ride on it (a tank's turret and radar).
#   Each child is a small design of its own: "position" and "angles" are in the PARENT's model units.
#   "part" names it: a child's name is its parent's name + " " + its part ("tank" -> "tank turret").
#   A child with no "colour" / "palette" uses its parent's.
#   "gun": True = it shoots at you (its shooting counters are added when it's built).
DESIGNS = {
    # ---- SHAPES: one model each ----
    "cube":    {"model": cube_model,    "colour": GREY, "palette": PALETTE_GREY},
    "pyramid": {"model": pyramid_model, "colour": GREY, "palette": PALETTE_GREY},
    "wire pyramid": {"model": pyramid_wire_model, "colour": GREY, "palette": PALETTE_GREY},   # edges only, no faces
    "diamond": {"model": diamond_model, "colour": GREY, "palette": PALETTE_GREY},
    "frame":   {"model": frame_model,   "colour": GREY, "palette": PALETTE_GREY},

    # ---- TANKS: a hull that turns to face the way it moves, with a turret and a radar riding on it ----
    "tank": {
        "model": hull_model,
        "colour": GREY,
        "palette": PALETTE_GREY,
        "faces_movement": True,
        "children": [
            {"part": "turret", "model": turret_model, "position": [0, -0.1, -0.3], "gun": True},   # its pivot, on the deck
            {"part": "radar",  "model": radar_model,  "position": [0, 0.35, -0.5], "speeds": (6, 0, 0)},   # mast foot, on the turret roof
        ],
    },
    # ---- BUNKERS: a LOW BOX that never moves, with a tank turret on its lid ----
    # A child's position is in its PARENT's model units: the low box's lid is at y = 0.5, and the turret's base
    # is at its own y = 0, so [0, 0.5, 0] sits it right on top. At size 0.6 it matches the small tank exactly.
    "bunker": {
        "model": low_box_model,
        "colour": GREY,
        "palette": PALETTE_GREY,
        "children": [
            {"part": "turret", "model": turret_model, "position": [0, 0.5, 0], "gun": True},
        ],
    },
    "twin tank": {                   # the same tank, with the TWO-barrelled turret
        "model": hull_model,
        "colour": GREY,
        "palette": PALETTE_GREY,
        "faces_movement": True,
        "children": [
            {"part": "turret", "model": twin_turret_model, "position": [0, -0.1, -0.3], "gun": True},
            {"part": "radar",  "model": radar_model,       "position": [0, 0.35, -0.5], "speeds": (6, 0, 0)},
        ],
    },
}


# ================================ LEVELS ================================
# Each level, by NUMBER. What a level holds:
#   "name"         - the level's title: shown big in the middle as the level starts, then at the top of the screen
#   "intro"        - one line shown under the name as the level starts, then it fades away
#   "grid_colour"  - (optional) the colour of EVERY grid (floor, walls, mini-map), e.g. (140, 35, 30) for red (left out = GRID_COLOUR, green)
#   "target_time"  - (optional) seconds to beat: the TARGET TIME counts down from it, top right
#                    (left out = DEFAULT_TARGET_TIME in rotation_data.py)
#   "world"        - the WORLD BOX: two opposite corners, "min" (smallest x, y, z) and "max" (biggest x, y, z).
#                    min y is the FLOOR (keep it at FLOOR_Y, -1), max y the CEILING. Keep x and z whole numbers:
#                    the floor grid has a line at every whole number. Things' CENTRES bounce inside it.
#   "start"        - where YOU begin: x, y (eye height: STAND_Y when standing), z, turn and tip (see player)
#   "floor_shapes" - DECALS on the floor. (Every level also gets a tiny GOLD square at x 0, z 0, automatically:
#                    ORIGIN_MARK in rotation_data.py. Don't add gold squares of your own.)
#                    Each decal is either plain paint: ([corners as (x, z)], colour)
#                    or a decal TYPE that does something (see DECAL_TYPES in rotation_data.py):
#                    {"type": "lava", "min": (x, z), "max": (x, z)}   - a rectangle from two opposite corners
#                    {"type": "lava", "corners": [(x, z), ...]}        - any shape
#                    ("lava" hurts you; "ice" freezes you for a moment)
#   "boxes"        - static boxes (see BOXES in rotation_data.py)
#   "sizes"        - (optional) this level's changes to the named SIZES (see rotation_data.py), e.g.
#                    {"SMALL": {"splits_to": None}} = in this level, SMALL shapes die instead of splitting
#   "spawn"        - the things in the level, in order: a "design" name + only what's different.
#                    "scenery": True = LEVEL DRESSING: it still draws, moves and shoots, but it isn't counted for
#                    "level complete", isn't drawn on the mini-map, and can't be killed (bullets just stop on it).
#                    ALWAYS give "colour" and "palette" (the designs are grey, to show when they're missing).
#                    "size": a NAMED size ("TINY" "SMALL" "MEDIUM" "LARGE" "HUGE") for shapes: it sets how big the
#                    shape is, its health, and what it splits into. (A plain number still works: tanks use one.)
#                    "children": [ {...}, {...} ] changes the design's children, in the same order.
#                    TANKS can also have:
#                      "gun": {...}      - its gun: "mode" ("SPIN", "OSCILLATE" or "TRACK"), "turret_spin", "range",
#                                          "centre", "cone", "cooldown", "volley", "volley_gap", "bullet_speed",
#                                          "start_angle" (a number, or "you" = start aimed at you).
#                                          Anything left out = GUN_DEFAULTS (rotation_data.py), which explains each one.
#                      "health": 6       - its own health (otherwise: its share of MAX_HEALTH, by size)
#                      "radar_spin": -6  - how fast its radar spins (degrees per frame)
#                    SHAPES can have a "gun" too, mode "DOWN" (drops bullets straight down from its lowest point) or
#                      "TARGET" (fires straight at you), every time it's cooled down,
#                      e.g. "gun": {"mode": "DOWN", "cooldown": 120, "volley": 1}
#                      (the same firing settings as a tank: cooldown, volley, volley_gap, bullet_speed).
#                      When a shape with a gun splits, both pieces keep the gun.
LEVELS = {
    1: {    # ---- LEVEL 1: TRAINING DAY - one big blue cube to practise on ----
        "name": "Training Day",
        "intro": "One big cube. Shoot it - and every piece it breaks into.",
        "world": {"min": (-8, -1, -8), "max": (8, 7, 8)},           # 16 wide (x), 16 long (z), 8 tall: floor -1, ceiling 7
        "start": {"x": 0, "y": 0, "z": -7, "turn": 0, "tip": 0},     # on the gold square, facing the far wall (+z)

        "floor_shapes": [
        ],

        "boxes": [],

        "sizes": {"SMALL": {"splits_to": None}},        # in this level: MEDIUM -> 2 SMALLs, which DIE

        "spawn": [
            # one MEDIUM ice-blue cube (was LARGE) near the far ("top" on the map) wall. It keeps the LARGE spot, so it floats a little higher.
            # It spins on the spot but never moves (no velocity).
            # Tilted, its corners stick out further than when it's flat (LARGE = cube size 1.25, tilt 20 degrees,
            # spinning): up to 1.78 below its centre and 2.09 behind it, instead of 1.25. So its centre is at y 1.28
            # (lowest corner 0.5 above the floor at -1) and z 5.86 (furthest corner just inside the far wall at z = 8).
            {"design": "cube", "name": "training cube",
             "position": [0, 1.28, 5.86],
             "size": "MEDIUM",                      # 1.5 across, 3 health (see SIZES)
             "angles": [30, 20, 0],                 # turned 30 degrees (two sides show) and TILTED 20 degrees
             "speeds": (0.5, 0, 0),                 # spins slowly round its upright axis only, so its tilt stays
                                                    #   the same (one full turn every 12 seconds at 60 FPS)
             "colour": (120, 190, 240), "palette": PALETTE_ICE},

            # a PRACTICE TANK: small, parked, in ice colours, its turret turning slowly. It fires a single shot
            # (not a volley) when it points at you, and waits longer between shots - a gentle first taste.
            {"design": "tank", "name": "practice tank",
             "position": [4, -0.4, 2], "size": 0.6, "angles": [200, 0, 0],    # parked, facing roughly towards you
             "colour": (120, 190, 240), "palette": PALETTE_ICE,
             "gun": {"mode": "SPIN", "turret_spin": 0.5, "volley": 1, "cooldown": 180},
             "radar_spin": -6},
        ],
    },

    2: {    # ---- LEVEL 2: FIRE AND ICE - two big cubes: one ice, one sunset ----
        "name": "Fire and Ice",
        "intro": "Two big cubes this time - one of ice, one of fire. Break them all.",
        "world": {"min": (-8, -1, -8), "max": (8, 7, 8)},           # the same room as level 1
        "start": {"x": 0, "y": 0, "z": -7, "turn": 0, "tip": 0},

        "floor_shapes": [
        ],

        "boxes": [],

        "sizes": {"SMALL": {"splits_to": None}},        # as level 1: MEDIUM -> 2 SMALLs, which DIE

        "spawn": [
            # two MEDIUM cubes (were LARGE) along the far wall, floating like level 1's (same height and distance from the wall),
            # 7 units apart so their tilted corners never touch, spinning opposite ways
            {"design": "cube", "name": "left cube",
             "position": [-3.5, 1.78, 5.86], "size": "MEDIUM",
             "angles": [30, 20, 0], "speeds": (0.5, 0, 0),
             "colour": (120, 190, 240), "palette": PALETTE_ICE,
             "gun": {"mode": "DOWN", "volley": 1}},     # drops ONE bullet straight down each time it fires
            {"design": "cube", "name": "right cube",              # the FIRE cube
             "position": [3.5, 1.78, 5.86], "size": "MEDIUM",
             "angles": [-30, 20, 0], "speeds": (-0.5, 0, 0),
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET,
             "gun": {"mode": "DOWN", "volley": 1}},     # drops ONE bullet straight down each time it fires

            # FIRE AND ICE tanks: one of each, parked on opposite sides, turrets turning opposite ways
            {"design": "tank", "name": "ice tank",
             "position": [-5.5, -0.4, 1], "size": 0.6, "angles": [150, 0, 0],
             "colour": (120, 190, 240), "palette": PALETTE_ICE,
             "gun": {"mode": "SPIN", "turret_spin": 0.8, "volley": 2},
             "radar_spin": -6},
            {"design": "tank", "name": "fire tank",
             "position": [5.5, -0.4, 1], "size": 0.6, "angles": [210, 0, 0],
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET,
             "gun": {"mode": "SPIN", "turret_spin": -0.8, "start_angle": 180, "volley": 2},
             "radar_spin": 6},
        ],
    },

    3: {    # ---- LEVEL 3: TRIPLE THREAT - three large shapes: ice, fire, and fire-and-ice ----
        "name": "Triple Threat",
        "intro": "A cube, a pyramid and a diamond - ice, fire, and both. Keep shooting!",
        "world": {"min": (-8, -1, -8), "max": (8, 7, 8)},           # the same room as level 1
        "start": {"x": 0, "y": 0, "z": -7, "turn": 0, "tip": 0},

        "floor_shapes": [
        ],

        "boxes": [],

        "sizes": {"SMALL": {"splits_to": None}},        # as level 1: MEDIUM -> 2 SMALLs, which DIE

        "spawn": [
            # three MEDIUM shapes (were LARGE) along the far wall, 5 units apart, floating half a unit off the floor, spins alternating.
            # A tilted LARGE cube or pyramid reaches up to 1.78 below its centre and 2.09 behind it (and about 2.1
            # sideways, so 5 apart they never touch), so: y 1.28, z 5.86 - like level 1's cube.
            # A diamond's tips are all 1 from its centre (1.25 at LARGE), whichever way it turns, so it sits at y 0.75.
            {"design": "cube", "name": "ice cube",                # ICE
             "position": [-5, 1.78, 5.86], "size": "MEDIUM",
             "angles": [30, 20, 0], "speeds": (0.5, 0, 0),
             "colour": (120, 190, 240), "palette": PALETTE_ICE,
             "gun": {"mode": "DOWN", "volley": 1}},     # drops ONE bullet straight down each time it fires
            {"design": "diamond", "name": "fire and ice diamond",  # FIRE AND ICE
             "position": [0, 1.25, 5.86], "size": "MEDIUM",
             "angles": [0, 20, 0], "speeds": (-0.5, 0, 0),
             "colour": FIRE_AND_ICE, "palette": PALETTE_FIRE_AND_ICE,
             "gun": {"mode": "DOWN", "volley": 1}},     # drops ONE bullet straight down each time it fires
            {"design": "pyramid", "name": "fire pyramid",          # FIRE
             "position": [5, 1.78, 5.86], "size": "MEDIUM",
             "angles": [-30, 20, 0], "speeds": (0.5, 0, 0),
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET,
             "gun": {"mode": "DOWN", "volley": 1}},     # drops ONE bullet straight down each time it fires

            # a BUNKER on the floor in front of each shape, in the same colours: a gun post for each threat
            {"design": "bunker", "name": "ice bunker",
             "position": [-5, -0.7, 3.5], "size": 0.6,
             "colour": (120, 190, 240), "palette": PALETTE_ICE,
             "gun": {"mode": "SPIN", "turret_spin": 1.0, "start_angle": 0, "volley": 2}},
            {"design": "bunker", "name": "fire and ice bunker",
             "position": [0, -0.7, 3.5], "size": 0.6,
             "colour": (120, 190, 240), "palette": PALETTE_FIRE_AND_ICE,
             "gun": {"mode": "SPIN", "turret_spin": -1.2, "start_angle": 120, "volley": 2}},
            {"design": "bunker", "name": "fire bunker",
             "position": [5, -0.7, 3.5], "size": 0.6,
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET,
             "gun": {"mode": "SPIN", "turret_spin": 1.0, "start_angle": 240, "volley": 2}},
        ],
    },

    4: {    # ---- LEVEL 4: MOVE OR DIE - a tank that shoots back, and three flying fire cubes ----
        "name": "Move or Die",
        "intro": "This one shoots back. Keep moving - and take out the tank.",
        "world": {"min": (-8, -1, -8), "max": (8, 7, 8)},           # the same room as levels 1 - 3
        "start": {"x": 0, "y": 0, "z": -7, "turn": 0, "tip": 0},

        "floor_shapes": [
        ],

        "boxes": [],

        "sizes": {"SMALL": {"splits_to": None}},        # as levels 1 - 3: MEDIUM -> 2 SMALLs, which DIE

        "spawn": [
            # a SMALL tank at the far end, driving SIDE TO SIDE: left to right, then back when it hits the wall.
            # It turns to face the way it drives, and its turret sweeps round firing volleys when it sees you.
            {"design": "tank", "name": "small tank",
             "position": [0, -0.4, 6],                  # y -0.4 = FLOOR_Y + size: on the floor
             "velocity": [0.015, 0, 0],                 # left to right (+x)
             "size": 0.6, "angles": [-90, 0, 0],        # facing +x, the way it drives (tanks still use a NUMBER for size)
             "colour": (120, 190, 80), "palette": PALETTE_FOREST,
             "gun": {"mode": "SPIN", "turret_spin": 1},  # its turret spins round, 1 degree a frame (see GUN_DEFAULTS)
             "radar_spin": -6},                         # its radar spins the other way, fast

            # three MEDIUM fire cubes, each flying a different diagonal at medium speed, bouncing round the room
            {"design": "cube", "name": "fire cube 1",
             "position": [-4, 2, 2], "velocity": [0.03, 0.02, 0.025], "size": "MEDIUM",
             "angles": [20, 10, 0], "speeds": (1, 0.5, 0),
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET,
             "gun": {"mode": "DOWN", "volley": 1}},     # drops ONE bullet straight down each time it fires
            {"design": "cube", "name": "fire cube 2",
             "position": [0, 3.5, 0], "velocity": [-0.025, 0.03, -0.02], "size": "MEDIUM",
             "angles": [45, 0, 20], "speeds": (0.5, 1, 0.5),
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET,
             "gun": {"mode": "DOWN", "volley": 1}},     # drops ONE bullet straight down each time it fires
            {"design": "cube", "name": "fire cube 3",
             "position": [4, 1.5, -2], "velocity": [0.02, -0.025, 0.03], "size": "MEDIUM",
             "angles": [0, 30, 10], "speeds": (1.5, 0, 1),
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET,
             "gun": {"mode": "DOWN", "volley": 1}},     # drops ONE bullet straight down each time it fires

            # a CEILING BUNKER in sunset colours, hanging over the middle, its cupola TRACKING you from above
            {"design": "bunker", "name": "ceiling bunker",
             "position": [0, 6.7, 1], "size": 0.6,
             "angles": [0, 180, 0],                             # upside down: lid facing the floor
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 2},
             "children": [{"model": cupola_model}]},           # the CUPOLA: no barrel
        ],
    },

    5: {    # ---- LEVEL 5: CROSSFIRE - two tanks patrolling in opposite directions, and four flying shapes ----
        "name": "Crossfire",
        "intro": "Two tanks crossing the room, and one of every shape. Stay on the move!",
        "world": {"min": (-8, -1, -8), "max": (8, 7, 8)},           # the same room as levels 1 - 4
        "start": {"x": 0, "y": 0, "z": -7, "turn": 0, "tip": 0},

        "floor_shapes": [
        ],

        "boxes": [],

        "sizes": {"SMALL": {"splits_to": None}},        # as levels 1 - 4: MEDIUM -> 2 SMALLs, which DIE

        "spawn": [
            # a PAIR of small tanks starting on OPPOSITE sides, driving back and forth across the room (bouncing off
            # the side walls), first towards each other. Two lanes (z 6 and z 3), so they pass rather than crash.
            {"design": "tank", "name": "left tank",
             "position": [-6, -0.4, 6], "velocity": [0.015, 0, 0],      # starts on the LEFT, drives right first
             "size": 0.6, "angles": [-90, 0, 0],
             "colour": (120, 190, 80), "palette": PALETTE_FOREST,
             "gun": {"mode": "SPIN", "turret_spin": 1, "start_angle": "you"},   # starts aimed at you: fires early
             "radar_spin": -6},
            {"design": "tank", "name": "right tank",
             "position": [6, -0.4, 3], "velocity": [-0.015, 0, 0],      # starts on the RIGHT, drives left first
             "size": 0.6, "angles": [90, 0, 0],
             "colour": (120, 190, 80), "palette": PALETTE_FOREST,
             "gun": {"mode": "SPIN", "turret_spin": -1, "start_angle": "you"},  # the other way round; aimed at you
             "radar_spin": 6},

            # one MEDIUM of each shape, all flying (medium speed) and spinning from the start
            {"design": "cube", "name": "ice cube",
             "position": [-4, 2, 0], "velocity": [0.03, 0.02, 0.025], "size": "MEDIUM",
             "angles": [20, 10, 0], "speeds": (1, 0.5, 0),
             "colour": (120, 190, 240), "palette": PALETTE_ICE,
             "gun": {"mode": "DOWN", "volley": 1}},     # drops ONE bullet straight down each time it fires
            {"design": "pyramid", "name": "fire pyramid",
             "position": [4, 1.5, -1], "velocity": [-0.025, 0.03, 0.02], "size": "MEDIUM",
             "angles": [0, 0, 0], "speeds": (1.5, 0, 0),
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET,
             "gun": {"mode": "DOWN", "volley": 1}},     # drops ONE bullet straight down each time it fires
            {"design": "diamond", "name": "fire and ice diamond",
             "position": [-2, 3.5, -3], "velocity": [0.02, -0.025, 0.03], "size": "MEDIUM",
             "angles": [0, 20, 0], "speeds": (2, 0, 0.5),
             "colour": FIRE_AND_ICE, "palette": PALETTE_FIRE_AND_ICE,
             "gun": {"mode": "DOWN", "volley": 1}},     # drops ONE bullet straight down each time it fires
            {"design": "frame", "name": "fire and ice frame",
             "position": [3, 3, 1], "velocity": [-0.03, -0.02, -0.025], "size": "MEDIUM",
             "angles": [30, 0, 0], "speeds": (0.8, 0.5, 0),
             "colour": FIRE_AND_ICE, "palette": PALETTE_FIRE_AND_ICE,
             "gun": {"mode": "TARGET", "volley": 1}},   # fires ONE bullet straight AT YOU each time it fires

            # WALL BUNKERS, one on each side wall, both TRACKING you: fire from the left AND the right
            {"design": "bunker", "name": "left wall bunker",          # on the LEFT wall (x = -8)
             "position": [-7.7, 3, 2], "size": 0.6,
             "angles": [0, 0, -90],                             # rolled -90: lid facing into the room (+x)
             "colour": (120, 190, 240), "palette": PALETTE_ICE,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 2},
             "children": [{"model": cupola_model}]},
            {"design": "bunker", "name": "right wall bunker",         # on the RIGHT wall (x = 8)
             "position": [7.7, 3, -1], "size": 0.6,
             "angles": [0, 0, 90],                              # rolled 90: lid facing into the room (-x)
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 2},
             "children": [{"model": cupola_model}]},
        ],
    },

    6: {    # ---- LEVEL 6: THE FLOOR IS LAVA - lava strips to jump, and a tank that follows you ----
        "name": "The Floor Is Lava",
        "intro": "Don't stand in the lava - jump it (SPACE). And watch that tank: it follows you.",
        "world": {"min": (-8, -1, -8), "max": (8, 7, 8)},           # the same room as levels 1 - 5
        "start": {"x": 0.5, "y": 0, "z": -7, "turn": 0, "tip": 0},   # on the gold strip, in line with the drips (z -7)
        "grid_colour": (140, 35, 30),                               # a RED floor grid: the floor is lava

        "floor_shapes": [
            # EVERY edge sits on a whole grid line, in bands 2 squares deep, from the far wall down:
            #   z 6 to 8 LAVA (the fireproof tank drives along it), 4 to 6 clear, 2 to 4 LAVA, 0 to 2 clear,
            #   -2 to 0 LAVA, -4 to -2 clear, -6 to -4 LAVA, -8 to -6 clear (where you START, against the near wall)
            # Plus a LAVA border 1 square wide down each side wall.
            {"type": "lava", "min": (-8, 6),  "max": (8, 8)},
            {"type": "lava", "min": (-8, 2),  "max": (8, 4)},
            {"type": "lava", "min": (-8, -2), "max": (8, 0)},
            {"type": "lava", "min": (-8, -6), "max": (8, -4)},
            {"type": "lava", "min": (-8, -8), "max": (-7, 8)},        # the left wall's border
            {"type": "lava", "min": (7, -8),  "max": (8, 8)},         # the right wall's border
        ],

        "boxes": [],

        "sizes": {"SMALL": {"splits_to": None}},        # as before: MEDIUM -> 2 SMALLs, which DIE

        "spawn": [
            # a small tank patrolling the far end, its turret TRACKING you (turning towards you, 0.7 degrees a frame)
            {"design": "tank", "name": "lava tank",                 # sunset colours: it's immune to fire
             "position": [0, -0.4, 6.5], "velocity": [0.012, 0, 0],
             "size": 0.6, "angles": [-90, 0, 0],
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET,
             "gun": {"mode": "TRACK", "turret_spin": 0.7, "start_angle": "you", "cooldown": 150},
             "radar_spin": -6},

            # one MEDIUM of each basic shape, all in SUNSET colours (lava creatures!), flying and spinning over the lava
            {"design": "cube", "name": "lava cube",
             "position": [-4, 2, 2], "velocity": [0.02, 0.015, -0.02], "size": "MEDIUM",
             "angles": [20, 10, 0], "speeds": (1, 0.5, 0),
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET},
            {"design": "pyramid", "name": "lava pyramid",
             "position": [4, 2.5, -2], "velocity": [-0.02, 0.02, 0.015], "size": "MEDIUM",
             "angles": [0, 0, 0], "speeds": (1.5, 0, 0),
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET},
            {"design": "diamond", "name": "lava diamond",
             "position": [-2, 3.5, -3], "velocity": [0.025, -0.02, 0.02], "size": "MEDIUM",
             "angles": [0, 20, 0], "speeds": (2, 0, 0.5),
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET},
            {"design": "frame", "name": "lava frame",
             "position": [3, 3, 1], "velocity": [-0.025, -0.02, -0.025], "size": "MEDIUM",
             "angles": [30, 0, 0], "speeds": (0.8, 0.5, 0),
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET},

            # LAVA DRIPPERS: SMALL pyramids turned UPSIDE DOWN (tilted 180), hanging from the ceiling, one over
            # the exact middle (in z) of EACH clear strip, the one you start in too, sliding side to side (x only).
            # BLACK faces with a RED outline (the level's grid red): they look like wireframes, but hide their
            # back edges. Each starts at a different x, and they take turns going left and right.
            # Their tip is their lowest corner, so each DOWN gun drips SUNSET lava from the tip.
            #   SMALL = 1 across (size 0.5): the pyramid is 1 tall, so its centre is 0.5 under the ceiling (y 7)
            #   The clear strips are 2 squares deep: their middles are z 5, 1, -3 and -7 (where you start)
            {"design": "pyramid", "name": "lava dripper 1",
             "position": [-5, 6.5, 5], "velocity": [0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0),          # upside down, and never spins
             "colour": (140, 35, 30), "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 45, "bullet_colour": (255, 120, 60), "bullet_palette": PALETTE_SUNSET},
             "scenery": True},                               # level dressing: not counted, not on the map, can't be killed
            {"design": "pyramid", "name": "lava dripper 2",
             "position": [3, 6.5, 1], "velocity": [-0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0),          # upside down, and never spins
             "colour": (140, 35, 30), "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 45, "bullet_colour": (255, 120, 60), "bullet_palette": PALETTE_SUNSET},
             "scenery": True},                               # level dressing: not counted, not on the map, can't be killed
            {"design": "pyramid", "name": "lava dripper 3",
             "position": [-2, 6.5, -3], "velocity": [0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0),          # upside down, and never spins
             "colour": (140, 35, 30), "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 45, "bullet_colour": (255, 120, 60), "bullet_palette": PALETTE_SUNSET},
             "scenery": True},                               # level dressing: not counted, not on the map, can't be killed
            {"design": "pyramid", "name": "lava dripper 4",             # over the strip you START in
             "position": [5, 6.5, -7], "velocity": [-0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0),          # upside down, and never spins
             "colour": (140, 35, 30), "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 45, "bullet_colour": (255, 120, 60), "bullet_palette": PALETTE_SUNSET},
             "scenery": True},                               # level dressing: not counted, not on the map, can't be killed

            # WALL BUNKERS in the drippers' style (black, with edges in the grid's colour), firing lava bullets,
            # over two of the clear strips (z 1 and -3), so you're shot at while you hop
            {"design": "bunker", "name": "left lava bunker",
             "position": [-7.7, 3, 1], "size": 0.6,
             "angles": [0, 0, -90],                             # on the LEFT wall, lid facing into the room
             "colour": (140, 35, 30), "palette": PALETTE_BLACK,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 2, "bullet_colour": (255, 120, 60), "bullet_palette": PALETTE_SUNSET},
             "children": [{"model": cupola_model}]},
            {"design": "bunker", "name": "right lava bunker",
             "position": [7.7, 3, -3], "size": 0.6,
             "angles": [0, 0, 90],                              # on the RIGHT wall, lid facing into the room
             "colour": (140, 35, 30), "palette": PALETTE_BLACK,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 2, "bullet_colour": (255, 120, 60), "bullet_palette": PALETTE_SUNSET},
             "children": [{"model": cupola_model}]},
        ],
    },

    7: {    # ---- LEVEL 7: FROZEN - a clone of level 6, frozen: ICE bands freeze you so the tank can line you up ----
        "name": "Frozen (will not let you go!)",
        "intro": "Ice freezes you in place - and that tank is waiting. Jump it (SPACE)!",
        "world": {"min": (-8, -1, -8), "max": (8, 7, 8)},           # the same room as levels 1 - 5
        "start": {"x": 0.5, "y": 0, "z": -7, "turn": 0, "tip": 0},   # on the gold strip, in line with the drips (z -7)
        "grid_colour": (40, 90, 150),                               # a BLUE floor grid: the floor is ice

        "floor_shapes": [
            # EVERY edge sits on a whole grid line, in bands 2 squares deep, from the far wall down:
            #   z 6 to 8 ICE (the frost-proof tank drives along it), 4 to 6 clear, 2 to 4 ICE, 0 to 2 clear,
            #   -2 to 0 ICE, -4 to -2 clear, -6 to -4 ICE, -8 to -6 clear (where you START, against the near wall)
            # Plus a ICE border 1 square wide down each side wall.
            {"type": "ice", "min": (-8, 6),  "max": (8, 8)},
            {"type": "ice", "min": (-8, 2),  "max": (8, 4)},
            {"type": "ice", "min": (-8, -2), "max": (8, 0)},
            {"type": "ice", "min": (-8, -6), "max": (8, -4)},
            {"type": "ice", "min": (-8, -8), "max": (-7, 8)},        # the left wall's border
            {"type": "ice", "min": (7, -8),  "max": (8, 8)},         # the right wall's border
        ],

        "boxes": [],

        "sizes": {"SMALL": {"splits_to": None}},        # as before: MEDIUM -> 2 SMALLs, which DIE

        "spawn": [
            # a small tank patrolling the far end, its turret TRACKING you (turning towards you, 0.7 degrees a frame)
            {"design": "tank", "name": "ice tank",                 # ice colours: it doesn't freeze
             "position": [0, -0.4, 6.5], "velocity": [0.012, 0, 0],
             "size": 0.6, "angles": [-90, 0, 0],
             "colour": (120, 190, 240), "palette": PALETTE_ICE,
             "gun": {"mode": "TRACK", "turret_spin": 0.7, "start_angle": "you", "cooldown": 150},
             "radar_spin": -6},

            # one MEDIUM of each basic shape, all in ICE colours (ice creatures!), flying and spinning over the ice
            {"design": "cube", "name": "ice cube",
             "position": [-4, 2, 2], "velocity": [0.02, 0.015, -0.02], "size": "MEDIUM",
             "angles": [20, 10, 0], "speeds": (1, 0.5, 0),
             "colour": (120, 190, 240), "palette": PALETTE_ICE},
            {"design": "pyramid", "name": "ice pyramid",
             "position": [4, 2.5, -2], "velocity": [-0.02, 0.02, 0.015], "size": "MEDIUM",
             "angles": [0, 0, 0], "speeds": (1.5, 0, 0),
             "colour": (120, 190, 240), "palette": PALETTE_ICE},
            {"design": "diamond", "name": "ice diamond",
             "position": [-2, 3.5, -3], "velocity": [0.025, -0.02, 0.02], "size": "MEDIUM",
             "angles": [0, 20, 0], "speeds": (2, 0, 0.5),
             "colour": (120, 190, 240), "palette": PALETTE_ICE},
            {"design": "frame", "name": "ice frame",
             "position": [3, 3, 1], "velocity": [-0.025, -0.02, -0.025], "size": "MEDIUM",
             "angles": [30, 0, 0], "speeds": (0.8, 0.5, 0),
             "colour": (120, 190, 240), "palette": PALETTE_ICE},

            # ICE DRIPPERS: SMALL pyramids turned UPSIDE DOWN (tilted 180), hanging from the ceiling, one over
            # the exact middle (in z) of EACH clear strip, the one you start in too, sliding side to side (x only).
            # BLACK faces with a BLUE outline (the level's grid blue): they look like wireframes, but hide their
            # back edges. Each starts at a different x, and they take turns going left and right.
            # Their tip is their lowest corner, so each DOWN gun drips ICE ice from the tip.
            #   SMALL = 1 across (size 0.5): the pyramid is 1 tall, so its centre is 0.5 under the ceiling (y 7)
            #   The clear strips are 2 squares deep: their middles are z 5, 1, -3 and -7 (where you start)
            {"design": "pyramid", "name": "icicle 1",
             "position": [-5, 6.5, 5], "velocity": [0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0),          # upside down, and never spins
             "colour": (40, 90, 150), "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 45, "bullet_colour": (120, 190, 240), "bullet_palette": PALETTE_ICE},
             "scenery": True},                               # level dressing: not counted, not on the map, can't be killed
            {"design": "pyramid", "name": "icicle 2",
             "position": [3, 6.5, 1], "velocity": [-0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0),          # upside down, and never spins
             "colour": (40, 90, 150), "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 45, "bullet_colour": (120, 190, 240), "bullet_palette": PALETTE_ICE},
             "scenery": True},                               # level dressing: not counted, not on the map, can't be killed
            {"design": "pyramid", "name": "icicle 3",
             "position": [-2, 6.5, -3], "velocity": [0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0),          # upside down, and never spins
             "colour": (40, 90, 150), "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 45, "bullet_colour": (120, 190, 240), "bullet_palette": PALETTE_ICE},
             "scenery": True},                               # level dressing: not counted, not on the map, can't be killed
            {"design": "pyramid", "name": "icicle 4",             # over the strip you START in
             "position": [5, 6.5, -7], "velocity": [-0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0),          # upside down, and never spins
             "colour": (40, 90, 150), "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 45, "bullet_colour": (120, 190, 240), "bullet_palette": PALETTE_ICE},
             "scenery": True},                               # level dressing: not counted, not on the map, can't be killed

            # WALL BUNKERS in the drippers' style (black, with edges in the grid's colour), firing ice bullets,
            # over two of the clear strips (z 1 and -3), so you're shot at while you hop
            {"design": "bunker", "name": "left ice bunker",
             "position": [-7.7, 3, 1], "size": 0.6,
             "angles": [0, 0, -90],                             # on the LEFT wall, lid facing into the room
             "colour": (40, 90, 150), "palette": PALETTE_BLACK,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 2, "bullet_colour": (120, 190, 240), "bullet_palette": PALETTE_ICE},
             "children": [{"model": cupola_model}]},
            {"design": "bunker", "name": "right ice bunker",
             "position": [7.7, 3, -3], "size": 0.6,
             "angles": [0, 0, 90],                              # on the RIGHT wall, lid facing into the room
             "colour": (40, 90, 150), "palette": PALETTE_BLACK,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 2, "bullet_colour": (120, 190, 240), "bullet_palette": PALETTE_ICE},
             "children": [{"model": cupola_model}]},
        ],
    },

    8: {    # ---- LEVEL 8: THE CANYON - a big room (32 x 32) of stone ruins, with bunkers on the floor, walls and ceiling ----
        "name": "The Canyon",
        "intro": "Bunkers on the floor, the walls and the ceiling. Use the ruins for cover.",
        "world": {"min": (-16, -1, -16), "max": (16, 7, 16)},       # 32 wide (x), 32 long (z), 8 tall
        "start": {"x": 0, "y": 0, "z": -14, "turn": 0, "tip": 0},    # near the back wall, facing the far wall
        "grid_colour": (60, 70, 55),                                # a dim STONE grey-green grid (from the stone palette)

        "floor_shapes": [],
        "boxes": [
            # JUNGLE RUINS in mossy stone (STONE, PALETTE_STONE). Every edge on a whole or half unit.
            # THE FOUNDATIONS: where the gate stood - the LOW outline of a fallen building (x -3 to 3, z 6 to 10):
            # wall stubs 0.2 to 1 tall with gaps where stones are missing, a fallen block and a step. Low enough to
            # see and shoot over, cover close to the ground. Pieces no longer than 1 unit.
            {"min": (-3, -1, 6), "max": (-2, 0.0, 6.4), "colour": STONE, "palette": PALETTE_STONE},   # front: corner stub
            {"min": (-2, -1, 6), "max": (-1, -0.5, 6.4), "colour": STONE, "palette": PALETTE_STONE},   # front: low
            {"min": (0, -1, 6), "max": (1, -0.2, 6.4), "colour": STONE, "palette": PALETTE_STONE},   # front (a gap at x -1 to 0: a missing stone)
            {"min": (1, -1, 6), "max": (2, -0.7, 6.4), "colour": STONE, "palette": PALETTE_STONE},   # front: almost gone
            {"min": (2, -1, 6), "max": (3, 0.0, 6.4), "colour": STONE, "palette": PALETTE_STONE},   # front: corner stub
            {"min": (-3, -1, 6.4), "max": (-2.6, -0.3, 7.4), "colour": STONE, "palette": PALETTE_STONE},   # left side
            {"min": (-3, -1, 8.4), "max": (-2.6, -0.6, 9.4), "colour": STONE, "palette": PALETTE_STONE},   # left side (gap from z 7.4 to 8.4)
            {"min": (2.6, -1, 6.4), "max": (3, -0.4, 7.4), "colour": STONE, "palette": PALETTE_STONE},   # right side
            {"min": (2.6, -1, 7.4), "max": (3, -0.8, 8.4), "colour": STONE, "palette": PALETTE_STONE},   # right side, almost gone
            {"min": (-3, -1, 9.6), "max": (-2, -0.2, 10), "colour": STONE, "palette": PALETTE_STONE},   # back: corner stub
            {"min": (-1, -1, 9.6), "max": (0, -0.5, 10), "colour": STONE, "palette": PALETTE_STONE},   # back
            {"min": (1, -1, 9.6), "max": (2, -0.3, 10), "colour": STONE, "palette": PALETTE_STONE},   # back
            {"min": (2, -1, 9.6), "max": (3, 0.0, 10), "colour": STONE, "palette": PALETTE_STONE},   # back: corner stub
            {"min": (-0.6, -1, 7.6), "max": (0.4, -0.6, 8.2), "colour": STONE, "palette": PALETTE_STONE},   # a fallen block inside
            {"min": (-1.5, -1, 8.6), "max": (-0.5, -0.8, 9.2), "colour": STONE, "palette": PALETTE_STONE},   # a step
            # THE RUIN: two walls (0.4 thick) meeting at a corner (x -12, z 12): a DOORWAY in one, a WINDOW in the
            # other, broken tops at different heights, and rubble. (Turned 90 clockwise about x -9, z 9.)
            {"min": (-12, -1, 9.5), "max": (-11.6, 2, 12), "colour": STONE, "palette": PALETTE_STONE},   # wall A (along z): left of the doorway, full height
            {"min": (-12, -1, 7), "max": (-11.6, 1.5, 8.5), "colour": STONE, "palette": PALETTE_STONE},   # wall A: right of the doorway, broken lower
            {"min": (-12, -1, 6), "max": (-11.6, 0.5, 7), "colour": STONE, "palette": PALETTE_STONE},   # wall A: the crumbled end
            {"min": (-12, 1.2, 8.5), "max": (-11.6, 2, 9.5), "colour": STONE, "palette": PALETTE_STONE},   # wall A: the lintel over the doorway
            {"min": (-11.6, -1, 11.6), "max": (-9.5, 2, 12), "colour": STONE, "palette": PALETTE_STONE},   # wall B (along x): up to the window
            {"min": (-9.5, -1, 11.6), "max": (-8.5, 0.3, 12), "colour": STONE, "palette": PALETTE_STONE},   # wall B: under the window
            {"min": (-9.5, 1, 11.6), "max": (-8.5, 1.6, 12), "colour": STONE, "palette": PALETTE_STONE},   # wall B: over the window
            {"min": (-8.5, -1, 11.6), "max": (-6, 1.2, 12), "colour": STONE, "palette": PALETTE_STONE},   # wall B: past the window, broken lower
            {"min": (-11, -1, 6.8), "max": (-10.4, -0.6, 7.4), "colour": STONE, "palette": PALETTE_STONE},   # rubble
            {"min": (-10, -1, 10.1), "max": (-9.6, -0.7, 10.6), "colour": STONE, "palette": PALETTE_STONE},   # rubble
            # THE ROCK COLUMN: a floor-to-CEILING column of weathered rock (where the stump was), x about 9.5 to
            # 11.5, z about 8.5 to 10.5. Eight layers, each 1 tall, each a little shifted and resized, so its sides
            # are jagged. (Short layers, not one 8-tall box: long faces draw wrong next to short ones.)
            {"min": (9.4, -1, 8.4), "max": (11.6, 0, 10.6), "colour": STONE, "palette": PALETTE_STONE},   # layer 1: y -1 to 0
            {"min": (9.6, 0, 8.6), "max": (11.5, 1, 10.6), "colour": STONE, "palette": PALETTE_STONE},   # layer 2: y 0 to 1
            {"min": (9.5, 1, 8.5), "max": (11.3, 2, 10.4), "colour": STONE, "palette": PALETTE_STONE},   # layer 3: y 1 to 2
            {"min": (9.7, 2, 8.7), "max": (11.4, 3, 10.5), "colour": STONE, "palette": PALETTE_STONE},   # layer 4: y 2 to 3
            {"min": (9.6, 3, 8.6), "max": (11.2, 4, 10.3), "colour": STONE, "palette": PALETTE_STONE},   # layer 5: y 3 to 4
            {"min": (9.5, 4, 8.5), "max": (11.3, 5, 10.4), "colour": STONE, "palette": PALETTE_STONE},   # layer 6: y 4 to 5
            {"min": (9.6, 5, 8.4), "max": (11.5, 6, 10.5), "colour": STONE, "palette": PALETTE_STONE},   # layer 7: y 5 to 6
            {"min": (9.4, 6, 8.3), "max": (11.6, 7, 10.6), "colour": STONE, "palette": PALETTE_STONE},   # layer 8: y 6 to 7
            # YOUR SANDBAGS: a U round where you start (x 0, z -14), open BEHIND you. The normal sandbag height
            # (0.4 tall, top at y -0.6), like the bunkers' nests: low cover you can see and shoot over.
            {"min": (-1.9, -1, -12.6), "max": (-1.5, -0.6, -12.2), "colour": SAND, "palette": PALETTE_SAND},   # front left corner
            {"min": (1.5, -1, -12.6), "max": (1.9, -0.6, -12.2), "colour": SAND, "palette": PALETTE_SAND},   # front right corner
            {"min": (-1.5, -1, -12.6), "max": (-0.5, -0.6, -12.2), "colour": SAND, "palette": PALETTE_SAND},   # front
            {"min": (-0.5, -1, -12.6), "max": (0.5, -0.6, -12.2), "colour": SAND, "palette": PALETTE_SAND},   # front
            {"min": (0.5, -1, -12.6), "max": (1.5, -0.6, -12.2), "colour": SAND, "palette": PALETTE_SAND},   # front
            {"min": (-1.9, -1, -13.6), "max": (-1.5, -0.6, -12.6), "colour": SAND, "palette": PALETTE_SAND},   # left side
            {"min": (1.5, -1, -13.6), "max": (1.9, -0.6, -12.6), "colour": SAND, "palette": PALETTE_SAND},   # right side
            {"min": (-1.9, -1, -14.4), "max": (-1.5, -0.6, -13.6), "colour": SAND, "palette": PALETTE_SAND},   # left side
            {"min": (1.5, -1, -14.4), "max": (1.9, -0.6, -13.6), "colour": SAND, "palette": PALETTE_SAND},   # right side
            # THE FRONT RUIN: COVER between where you start and the bunkers. A broken wall across the front
            # right (z -9 to -8.6, 0.4 thick) with a DOORWAY and an eye-height WINDOW to shoot through, and a
            # short return wall at its end. Built in pieces no longer than 1 unit (so it always draws right).
            # Your eye is at y 0: walls taller than that hide you.
            {"min": (5, -1, -9), "max": (6, 1.2, -8.6), "colour": STONE, "palette": PALETTE_STONE},   # wall, broken lower (peek over it)
            {"min": (6, -1, -9), "max": (7, -0.3, -8.6), "colour": STONE, "palette": PALETTE_STONE},   # wall under the WINDOW
            {"min": (6, 0.4, -9), "max": (7, 2.0, -8.6), "colour": STONE, "palette": PALETTE_STONE},   # wall over the WINDOW (the window: y -0.3 to 0.4, at your eye)
            {"min": (7, -1, -9), "max": (7.5, 1.6, -8.6), "colour": STONE, "palette": PALETTE_STONE},   # wall, left of the DOORWAY
            {"min": (7.5, 1.4, -9), "max": (8.5, 1.9, -8.6), "colour": STONE, "palette": PALETTE_STONE},   # lintel over the DOORWAY (x 7.5 to 8.5)
            {"min": (8.5, -1, -9), "max": (9.5, 1.8, -8.6), "colour": STONE, "palette": PALETTE_STONE},   # wall, right of the doorway
            {"min": (9.5, -1, -9), "max": (10.5, 1.4, -8.6), "colour": STONE, "palette": PALETTE_STONE},   # wall
            {"min": (10.5, -1, -9), "max": (11, 2.0, -8.6), "colour": STONE, "palette": PALETTE_STONE},   # the corner, full height
            {"min": (10.6, -1, -10), "max": (11, 2.0, -9), "colour": STONE, "palette": PALETTE_STONE},   # return wall (along z)
            {"min": (10.6, -1, -11), "max": (11, 1.0, -10), "colour": STONE, "palette": PALETTE_STONE},   # return wall, broken lower
            {"min": (5.6, -1, -10.2), "max": (6.2, -0.5, -9.6), "colour": STONE, "palette": PALETTE_STONE},   # rubble behind the wall
            {"min": (9.0, -1, -10.0), "max": (9.5, -0.6, -9.5), "colour": STONE, "palette": PALETTE_STONE},   # rubble
            # THE WEST NEST: a low SANDBAG wall (0.4 tall: just under the bunker's gun, so it can fire over) round the west
            # floor bunker (x -10, z -4), with a GAP facing the back wall
            {"min": (-12, -1, -2.5), "max": (-11.5, -0.6, -2), "colour": SAND, "palette": PALETTE_SAND},   # corner
            {"min": (-8.5, -1, -2.5), "max": (-8, -0.6, -2), "colour": SAND, "palette": PALETTE_SAND},   # corner
            {"min": (-12, -1, -6), "max": (-11.5, -0.6, -5.5), "colour": SAND, "palette": PALETTE_SAND},   # corner
            {"min": (-8.5, -1, -6), "max": (-8, -0.6, -5.5), "colour": SAND, "palette": PALETTE_SAND},   # corner
            {"min": (-11.5, -1, -2.5), "max": (-10.5, -0.6, -2), "colour": SAND, "palette": PALETTE_SAND},   # far side
            {"min": (-10.5, -1, -2.5), "max": (-9.5, -0.6, -2), "colour": SAND, "palette": PALETTE_SAND},   # far side
            {"min": (-9.5, -1, -2.5), "max": (-8.5, -0.6, -2), "colour": SAND, "palette": PALETTE_SAND},   # far side
            {"min": (-12, -1, -5.5), "max": (-11.5, -0.6, -4.5), "colour": SAND, "palette": PALETTE_SAND},   # left side
            {"min": (-8.5, -1, -5.5), "max": (-8, -0.6, -4.5), "colour": SAND, "palette": PALETTE_SAND},   # right side
            {"min": (-12, -1, -4.5), "max": (-11.5, -0.6, -3.5), "colour": SAND, "palette": PALETTE_SAND},   # left side
            {"min": (-8.5, -1, -4.5), "max": (-8, -0.6, -3.5), "colour": SAND, "palette": PALETTE_SAND},   # right side
            {"min": (-12, -1, -3.5), "max": (-11.5, -0.6, -2.5), "colour": SAND, "palette": PALETTE_SAND},   # left side
            {"min": (-8.5, -1, -3.5), "max": (-8, -0.6, -2.5), "colour": SAND, "palette": PALETTE_SAND},   # right side
            {"min": (-11.5, -1, -6), "max": (-11, -0.6, -5.5), "colour": SAND, "palette": PALETTE_SAND},   # near side, left part ...
            {"min": (-9, -1, -6), "max": (-8.5, -0.6, -5.5), "colour": SAND, "palette": PALETTE_SAND},   # ... and right part: the GAP is between them
            # EAST NEST: the same sandbag nest round the east floor bunker (x 10, z -4)
            {"min": (8, -1, -2.5), "max": (8.5, -0.6, -2), "colour": SAND, "palette": PALETTE_SAND},   # corner
            {"min": (11.5, -1, -2.5), "max": (12, -0.6, -2), "colour": SAND, "palette": PALETTE_SAND},   # corner
            {"min": (8, -1, -6), "max": (8.5, -0.6, -5.5), "colour": SAND, "palette": PALETTE_SAND},   # corner
            {"min": (11.5, -1, -6), "max": (12, -0.6, -5.5), "colour": SAND, "palette": PALETTE_SAND},   # corner
            {"min": (8.5, -1, -2.5), "max": (9.5, -0.6, -2), "colour": SAND, "palette": PALETTE_SAND},   # far side
            {"min": (9.5, -1, -2.5), "max": (10.5, -0.6, -2), "colour": SAND, "palette": PALETTE_SAND},   # far side
            {"min": (10.5, -1, -2.5), "max": (11.5, -0.6, -2), "colour": SAND, "palette": PALETTE_SAND},   # far side
            {"min": (8, -1, -5.5), "max": (8.5, -0.6, -4.5), "colour": SAND, "palette": PALETTE_SAND},   # left side
            {"min": (11.5, -1, -5.5), "max": (12, -0.6, -4.5), "colour": SAND, "palette": PALETTE_SAND},   # right side
            {"min": (8, -1, -4.5), "max": (8.5, -0.6, -3.5), "colour": SAND, "palette": PALETTE_SAND},   # left side
            {"min": (11.5, -1, -4.5), "max": (12, -0.6, -3.5), "colour": SAND, "palette": PALETTE_SAND},   # right side
            {"min": (8, -1, -3.5), "max": (8.5, -0.6, -2.5), "colour": SAND, "palette": PALETTE_SAND},   # left side
            {"min": (11.5, -1, -3.5), "max": (12, -0.6, -2.5), "colour": SAND, "palette": PALETTE_SAND},   # right side
            {"min": (8.5, -1, -6), "max": (9, -0.6, -5.5), "colour": SAND, "palette": PALETTE_SAND},   # near side, left part ...
            {"min": (11, -1, -6), "max": (11.5, -0.6, -5.5), "colour": SAND, "palette": PALETTE_SAND},   # ... and right part: the GAP is between them
            # MIDDLE NEST: the same sandbag nest round the middle floor bunker (x 0, z -2)
            {"min": (-2, -1, -0.5), "max": (-1.5, -0.6, 0), "colour": SAND, "palette": PALETTE_SAND},   # corner
            {"min": (1.5, -1, -0.5), "max": (2, -0.6, 0), "colour": SAND, "palette": PALETTE_SAND},   # corner
            {"min": (-2, -1, -4), "max": (-1.5, -0.6, -3.5), "colour": SAND, "palette": PALETTE_SAND},   # corner
            {"min": (1.5, -1, -4), "max": (2, -0.6, -3.5), "colour": SAND, "palette": PALETTE_SAND},   # corner
            {"min": (-1.5, -1, -0.5), "max": (-0.5, -0.6, 0), "colour": SAND, "palette": PALETTE_SAND},   # far side
            {"min": (-0.5, -1, -0.5), "max": (0.5, -0.6, 0), "colour": SAND, "palette": PALETTE_SAND},   # far side
            {"min": (0.5, -1, -0.5), "max": (1.5, -0.6, 0), "colour": SAND, "palette": PALETTE_SAND},   # far side
            {"min": (-2, -1, -3.5), "max": (-1.5, -0.6, -2.5), "colour": SAND, "palette": PALETTE_SAND},   # left side
            {"min": (1.5, -1, -3.5), "max": (2, -0.6, -2.5), "colour": SAND, "palette": PALETTE_SAND},   # right side
            {"min": (-2, -1, -2.5), "max": (-1.5, -0.6, -1.5), "colour": SAND, "palette": PALETTE_SAND},   # left side
            {"min": (1.5, -1, -2.5), "max": (2, -0.6, -1.5), "colour": SAND, "palette": PALETTE_SAND},   # right side
            {"min": (-2, -1, -1.5), "max": (-1.5, -0.6, -0.5), "colour": SAND, "palette": PALETTE_SAND},   # left side
            {"min": (1.5, -1, -1.5), "max": (2, -0.6, -0.5), "colour": SAND, "palette": PALETTE_SAND},   # right side
            {"min": (-1.5, -1, -4), "max": (-1, -0.6, -3.5), "colour": SAND, "palette": PALETTE_SAND},   # near side, left part ...
            {"min": (1, -1, -4), "max": (1.5, -0.6, -3.5), "colour": SAND, "palette": PALETTE_SAND},   # ... and right part: the GAP is between them
            # THE SHRINE: a ruined three-sided stone room at the front left - COVER from the bunkers. Its FRONT
            # wall (z -8.4 to -8) faces the bunkers; its open side faces the back wall, where you come in.
            # An ARROW SLIT and a BREACH in the front wall, side walls crumbling lower towards you, a low ALTAR
            # inside to crouch behind, fallen stones outside. Pieces no longer than 1 unit.
            {"min": (-13, -1, -8.4), "max": (-12, 2.2, -8), "colour": STONE, "palette": PALETTE_STONE},   # front wall: the tall corner
            {"min": (-12, -1, -8.4), "max": (-11.2, 1.8, -8), "colour": STONE, "palette": PALETTE_STONE},   # front wall
            {"min": (-11.2, -1, -8.4), "max": (-10.8, -0.4, -8), "colour": STONE, "palette": PALETTE_STONE},   # under the ARROW SLIT
            {"min": (-11.2, 0.6, -8.4), "max": (-10.8, 1.8, -8), "colour": STONE, "palette": PALETTE_STONE},   # over the arrow slit (the slit: y -0.4 to 0.6, at your eye)
            {"min": (-10.8, -1, -8.4), "max": (-10, 1.8, -8), "colour": STONE, "palette": PALETTE_STONE},   # front wall
            {"min": (-10, -1, -8.4), "max": (-9, 0.8, -8), "colour": STONE, "palette": PALETTE_STONE},   # front wall, broken low (peek over it)
            {"min": (-8, -1, -8.4), "max": (-7.6, 1.5, -8), "colour": STONE, "palette": PALETTE_STONE},   # front wall's right end (the BREACH is x -9 to -8)
            {"min": (-13.4, -1, -9), "max": (-13, 2.2, -8), "colour": STONE, "palette": PALETTE_STONE},   # left wall, full height
            {"min": (-13.4, -1, -10), "max": (-13, 1.6, -9), "colour": STONE, "palette": PALETTE_STONE},   # left wall, crumbling
            {"min": (-13.4, -1, -11), "max": (-13, 0.9, -10), "colour": STONE, "palette": PALETTE_STONE},   # left wall, crumbled low
            {"min": (-8, -1, -9), "max": (-7.6, 1.5, -8.4), "colour": STONE, "palette": PALETTE_STONE},   # right wall
            {"min": (-8, -1, -10), "max": (-7.6, 0.6, -9), "colour": STONE, "palette": PALETTE_STONE},   # right wall, crumbled low
            {"min": (-11.5, -1, -10), "max": (-10.5, -0.3, -9.2), "colour": STONE, "palette": PALETTE_STONE},   # the ALTAR: crouch behind it
            {"min": (-12.5, -1, -7.4), "max": (-11.5, -0.6, -7.0), "colour": STONE, "palette": PALETTE_STONE},   # a fallen stone outside the front wall
            {"min": (-8.8, -1, -7.6), "max": (-8.2, -0.6, -7.1), "colour": STONE, "palette": PALETTE_STONE},   # rubble from the breach
            {"min": (-9.6, -1, -7.4), "max": (-9.2, -0.7, -7.0), "colour": STONE, "palette": PALETTE_STONE},   # rubble from the breach
        ],
        "spawn": [
            # FLOOR BUNKERS (3), and wall and ceiling bunkers (4). The floor ones: low green boxes at the SMALL
            # TANK's size (0.6: 1.2 across,
            # 0.6 tall - y -0.7 = sitting on the floor), each with a small tank's turret on top
            # whose turret SPINS round (SPIN mode) and fires a volley of 3 whenever it points at you.
            # Different start angles and spin directions, so they never sweep in step.
            {"design": "bunker", "name": "west bunker",
             "position": [-10, -0.7, -4], "size": 0.6,
             "colour": (60, 140, 70), "palette": PALETTE_FOREST,
             "gun": {"mode": "SPIN", "turret_spin": 1.0, "start_angle": 0, "volley": 3}},
            {"design": "bunker", "name": "east bunker",
             "position": [10, -0.7, -4], "size": 0.6,
             "colour": (60, 140, 70), "palette": PALETTE_FOREST,
             "gun": {"mode": "SPIN", "turret_spin": -1.0, "start_angle": 90, "volley": 3}},
            {"design": "bunker", "name": "left wall bunker",          # on the LEFT wall (x = -16)
             "position": [-15.7, 3, 4], "size": 0.6,
             "angles": [0, 0, -90],                             # rolled -90: lid facing into the room (+x)
             "colour": (60, 140, 70), "palette": PALETTE_FOREST,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 3},
             "children": [{"model": cupola_model, "palette": PALETTE_CUPOLA}]},   # the CUPOLA: no barrel   # its turret turns to follow you
            {"design": "bunker", "name": "ceiling bunker",            # hanging from the CEILING (y = 7)
             "position": [6, 6.7, 4], "size": 0.6,
             "angles": [0, 180, 0],                             # upside down: lid facing the floor
             "colour": (60, 140, 70), "palette": PALETTE_FOREST,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 3},
             "children": [{"model": cupola_model, "palette": PALETTE_CUPOLA}]},   # the CUPOLA: no barrel
            {"design": "bunker", "name": "middle bunker",
             "position": [0, -0.7, -2], "size": 0.6,
             "colour": (60, 140, 70), "palette": PALETTE_FOREST,
             "gun": {"mode": "SPIN", "turret_spin": 1.2, "start_angle": 45, "volley": 3}},
            {"design": "bunker", "name": "far wall bunker",           # on the FAR wall (z = 16)
             "position": [0, 3, 15.7], "size": 0.6,
             "angles": [0, -90, 0],                             # tilted -90: lid facing into the room (-z)
             "colour": (60, 140, 70), "palette": PALETTE_FOREST,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 3},
             "children": [{"model": cupola_model, "palette": PALETTE_CUPOLA}]},   # the CUPOLA: no barrel
            # WALL and CEILING BUNKERS: the same bunker turned so its lid faces into the room, its low box 0.3 in
            # from the surface. Each has a CUPOLA (no barrel, gold visor on its front, bullets from its roof)
            # that TRACKS you (turns to follow you) in the plane of its wall.
            {"design": "bunker", "name": "right wall bunker",         # on the RIGHT wall (x = 16)
             "position": [15.7, 3, 0], "size": 0.6,
             "angles": [0, 0, 90],                              # rolled 90: lid facing into the room (-x)
             "colour": (60, 140, 70), "palette": PALETTE_FOREST,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 3},
             "children": [{"model": cupola_model, "palette": PALETTE_CUPOLA}]},   # the CUPOLA: no barrel

            # TANKS on patrol, in the two lanes the ruins leave open: one across the room (z = 3), one up and
            # down it (x = -4.5). They turn to face the way they drive, and TRACK you with their turrets.
            {"design": "tank", "name": "lane tank",
             "position": [-12, -0.4, 3], "velocity": [0.015, 0, 0],
             "size": 0.6, "angles": [-90, 0, 0],
             "colour": (120, 190, 80), "palette": PALETTE_FOREST,
             "gun": {"mode": "TRACK", "turret_spin": 0.8, "start_angle": "you", "volley": 3, "cooldown": 150},
             "radar_spin": -6},
            {"design": "tank", "name": "canyon tank",
             "position": [-4.5, -0.4, 12], "velocity": [0, 0, -0.012],
             "size": 0.6, "angles": [180, 0, 0],
             "colour": (120, 190, 80), "palette": PALETTE_FOREST,
             "gun": {"mode": "TRACK", "turret_spin": 0.8, "start_angle": "you", "volley": 3, "cooldown": 150},
             "radar_spin": 6},
        ],
    },

    9: {    # ---- LEVEL 9: THE GLACIER - the Canyon's size, all ICE: ice blocks, ice tanks, ice turrets, icicles ----
        "name": "The Glacier",
        "intro": "Ice everywhere. The frozen pond will hold you still - right where the turrets want you.",
        "world": {"min": (-16, -1, -16), "max": (16, 7, 16)},       # 32 wide (x), 32 long (z), 8 tall: the Canyon's size
        "start": {"x": 0, "y": 0, "z": -14, "turn": 0, "tip": 0},    # near the back wall, facing the far wall
        "grid_colour": (40, 90, 150),                              # an ICE-blue grid

        "floor_shapes": [
            # FROZEN POND and ice patches: ICE freezes you (and hurts) - the turrets love a frozen target
            {"type": "ice", "min": (-3, 8), "max": (3, 12)},          # the frozen pond, behind the middle ring
            {"type": "ice", "min": (-15, 1), "max": (-12, 4)},        # a patch by the left wall
            {"type": "ice", "min": (12, 4), "max": (15, 7)},          # a patch by the right wall
            {"type": "ice", "min": (-1, -6), "max": (1, -4)},         # a small patch between the wall's gaps
        ],
        "boxes": [
            # THE GLACIER, built from ICE BLOCKS (ICE_BLOCK edges, PALETTE_ICE). Pieces no longer than 1 unit.
            # YOUR SNOW FORT: a low U of packed snow round where you start (x 0, z -14), open behind you
            {"min": (-1.9, -1, -12.6), "max": (-1.5, -0.6, -12.2), "colour": SNOW, "palette": PALETTE_SNOW},   # front left corner
            {"min": (1.5, -1, -12.6), "max": (1.9, -0.6, -12.2), "colour": SNOW, "palette": PALETTE_SNOW},   # front right corner
            {"min": (-1.5, -1, -12.6), "max": (-0.5, -0.6, -12.2), "colour": SNOW, "palette": PALETTE_SNOW},   # front
            {"min": (-0.5, -1, -12.6), "max": (0.5, -0.6, -12.2), "colour": SNOW, "palette": PALETTE_SNOW},
            {"min": (0.5, -1, -12.6), "max": (1.5, -0.6, -12.2), "colour": SNOW, "palette": PALETTE_SNOW},
            {"min": (-1.9, -1, -13.6), "max": (-1.5, -0.6, -12.6), "colour": SNOW, "palette": PALETTE_SNOW},   # left side
            {"min": (1.5, -1, -13.6), "max": (1.9, -0.6, -12.6), "colour": SNOW, "palette": PALETTE_SNOW},   # right side
            {"min": (-1.9, -1, -14.4), "max": (-1.5, -0.6, -13.6), "colour": SNOW, "palette": PALETTE_SNOW},
            {"min": (1.5, -1, -14.4), "max": (1.9, -0.6, -13.6), "colour": SNOW, "palette": PALETTE_SNOW},
            # THE ICE WALL: cover across the front (z -8.6 to -8.2), x -7 to 7: TALL at both ends, LOW in the middle (see and
            # shoot over it), two gaps to run through, and an eye-height WINDOW at x 4 to 5
            {"min": (-7, -1, -8.6), "max": (-6, 1.4, -8.2), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # the ice wall
            {"min": (-6, -1, -8.6), "max": (-5, 1.9, -8.2), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (-5, -1, -8.6), "max": (-4, 1.6, -8.2), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (-3, -1, -8.6), "max": (-2, -0.3, -8.2), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (-2, -1, -8.6), "max": (-1, 0.3, -8.2), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (-1, -1, -8.6), "max": (0, -0.5, -8.2), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (2, -1, -8.6), "max": (3, -0.2, -8.2), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (3, -1, -8.6), "max": (4, 1.8, -8.2), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (4, -1, -8.6), "max": (5, -0.3, -8.2), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # the ice wall: under the window
            {"min": (4, 0.4, -8.6), "max": (5, 2, -8.2), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # the ice wall: over the window (y -0.3 to 0.4)
            {"min": (5, -1, -8.6), "max": (6, 1.2, -8.2), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (6, -1, -8.6), "max": (7, 1.6, -8.2), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            # ICE BLOCK PILES: 1 x 1 blocks, stacked 1 or 2 high - cover in the open
            {"min": (-7, -1, -3), "max": (-6, 0, -2), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # pile, left
            {"min": (-7, 0, -3), "max": (-6, 1, -2), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (-6, -1, -3), "max": (-5, 0, -2), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (-7, -1, -2), "max": (-6, 0, -1), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (5, -1, 1), "max": (6, 0, 2), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # pile, right
            {"min": (6, -1, 1), "max": (7, 0, 2), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (6, 0, 1), "max": (7, 1, 2), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (6, -1, 2), "max": (7, 0, 3), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (-3, -1, 9), "max": (-2, 0, 10), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # pile, far
            {"min": (-2, -1, 9), "max": (-1, 0, 10), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (-1, -1, 9), "max": (0, 0, 10), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (-1, 0, 9), "max": (0, 1, 10), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (-2, -1, 10), "max": (-1, 0, 11), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            # THE SPIRES: two floor-to-CEILING columns of glacier ice, jagged (8 layers, each 1 tall)
            {"min": (-11.1, -1, 6), "max": (-8.9, 0, 8.1), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # left spire: layer 1
            {"min": (-10.75, 0, 6.25), "max": (-9.15, 1, 7.95), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # left spire: layer 2
            {"min": (-10.75, 1, 6.15), "max": (-9.35, 2, 7.75), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # left spire: layer 3
            {"min": (-10.55, 2, 6.45), "max": (-9.35, 3, 7.55), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # left spire: layer 4
            {"min": (-10.7, 3, 6.3), "max": (-9.2, 4, 7.8), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # left spire: layer 5
            {"min": (-10.9, 4, 6.3), "max": (-9.2, 5, 7.8), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # left spire: layer 6
            {"min": (-10.8, 5, 6), "max": (-9, 6, 8), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # left spire: layer 7
            {"min": (-11.1, 6, 5.9), "max": (-8.9, 7, 8.1), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # left spire: layer 8
            {"min": (9, -1, 7), "max": (11, 0, 9), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # right spire: layer 1
            {"min": (9.3, 0, 7.1), "max": (10.9, 1, 8.9), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # right spire: layer 2
            {"min": (9.2, 1, 7.4), "max": (10.7, 2, 8.7), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # right spire: layer 3
            {"min": (9.4, 2, 7.4), "max": (10.7, 3, 8.7), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # right spire: layer 4
            {"min": (9.55, 3, 7.55), "max": (10.55, 4, 8.45), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # right spire: layer 5
            {"min": (9.35, 4, 7.25), "max": (10.55, 5, 8.65), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # right spire: layer 6
            {"min": (9.35, 5, 7.35), "max": (10.75, 6, 8.85), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # right spire: layer 7
            {"min": (9, 6, 7.1), "max": (11, 7, 9), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # right spire: layer 8
            # THE ICE ARCH: two pillars and a lintel at the back right (x 6 to 9, z 12 to 13): run under it
            {"min": (6, -1, 12), "max": (7, 0, 13), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # arch pillar
            {"min": (6, 0, 12), "max": (7, 1, 13), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (6, 1, 12), "max": (7, 2, 13), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (8, -1, 12), "max": (9, 0, 13), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # arch pillar
            {"min": (8, 0, 12), "max": (9, 1, 13), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (8, 1, 12), "max": (9, 2, 13), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (6, 2, 12), "max": (7, 2.6, 13), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # arch lintel
            {"min": (7, 2, 12), "max": (8, 2.6, 13), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (8, 2, 12), "max": (9, 2.6, 13), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            # ICE RINGS round the three floor bunkers: low blocks (0.4 tall, under their guns), a GAP facing the back
            {"min": (-12, -1, -0.5), "max": (-11.5, -0.6, 0), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # west ring: corner
            {"min": (-8.5, -1, -0.5), "max": (-8, -0.6, 0), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # corner
            {"min": (-12, -1, -4), "max": (-11.5, -0.6, -3.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # corner
            {"min": (-8.5, -1, -4), "max": (-8, -0.6, -3.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # corner
            {"min": (-11.5, -1, -0.5), "max": (-10.5, -0.6, 0), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # far side
            {"min": (-10.5, -1, -0.5), "max": (-9.5, -0.6, 0), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (-9.5, -1, -0.5), "max": (-8.5, -0.6, 0), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (-12, -1, -3.5), "max": (-11.5, -0.6, -2.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # left side
            {"min": (-8.5, -1, -3.5), "max": (-8, -0.6, -2.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # right side
            {"min": (-12, -1, -2.5), "max": (-11.5, -0.6, -1.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (-8.5, -1, -2.5), "max": (-8, -0.6, -1.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (-12, -1, -1.5), "max": (-11.5, -0.6, -0.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (-8.5, -1, -1.5), "max": (-8, -0.6, -0.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (-11.5, -1, -4), "max": (-11, -0.6, -3.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # near side, left part ...
            {"min": (-9, -1, -4), "max": (-8.5, -0.6, -3.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # ... and right part: the GAP is between them
            {"min": (8, -1, -0.5), "max": (8.5, -0.6, 0), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # east ring: corner
            {"min": (11.5, -1, -0.5), "max": (12, -0.6, 0), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # corner
            {"min": (8, -1, -4), "max": (8.5, -0.6, -3.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # corner
            {"min": (11.5, -1, -4), "max": (12, -0.6, -3.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # corner
            {"min": (8.5, -1, -0.5), "max": (9.5, -0.6, 0), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # far side
            {"min": (9.5, -1, -0.5), "max": (10.5, -0.6, 0), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (10.5, -1, -0.5), "max": (11.5, -0.6, 0), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (8, -1, -3.5), "max": (8.5, -0.6, -2.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # left side
            {"min": (11.5, -1, -3.5), "max": (12, -0.6, -2.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # right side
            {"min": (8, -1, -2.5), "max": (8.5, -0.6, -1.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (11.5, -1, -2.5), "max": (12, -0.6, -1.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (8, -1, -1.5), "max": (8.5, -0.6, -0.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (11.5, -1, -1.5), "max": (12, -0.6, -0.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (8.5, -1, -4), "max": (9, -0.6, -3.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # near side, left part ...
            {"min": (11, -1, -4), "max": (11.5, -0.6, -3.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # ... and right part: the GAP is between them
            {"min": (-2, -1, 5.5), "max": (-1.5, -0.6, 6), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # middle ring: corner
            {"min": (1.5, -1, 5.5), "max": (2, -0.6, 6), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # corner
            {"min": (-2, -1, 2), "max": (-1.5, -0.6, 2.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # corner
            {"min": (1.5, -1, 2), "max": (2, -0.6, 2.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # corner
            {"min": (-1.5, -1, 5.5), "max": (-0.5, -0.6, 6), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # far side
            {"min": (-0.5, -1, 5.5), "max": (0.5, -0.6, 6), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (0.5, -1, 5.5), "max": (1.5, -0.6, 6), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (-2, -1, 2.5), "max": (-1.5, -0.6, 3.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # left side
            {"min": (1.5, -1, 2.5), "max": (2, -0.6, 3.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # right side
            {"min": (-2, -1, 3.5), "max": (-1.5, -0.6, 4.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (1.5, -1, 3.5), "max": (2, -0.6, 4.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (-2, -1, 4.5), "max": (-1.5, -0.6, 5.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (1.5, -1, 4.5), "max": (2, -0.6, 5.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},
            {"min": (-1.5, -1, 2), "max": (-1, -0.6, 2.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # near side, left part ...
            {"min": (1, -1, 2), "max": (1.5, -0.6, 2.5), "colour": ICE_BLOCK, "palette": PALETTE_ICE},   # ... and right part: the GAP is between them
        ],
        "spawn": [
            # ICE TANKS on patrol in the open lanes: one across the room, one up and down it
            {"design": "tank", "name": "ice tank",
             "position": [-12, -0.4, -5.5], "velocity": [0.015, 0, 0],
             "size": 0.6, "angles": [-90, 0, 0], "colour": (120, 190, 240), "palette": PALETTE_ICE,
             "gun": {"mode": "TRACK", "turret_spin": 0.8, "start_angle": "you", "volley": 3, "cooldown": 150},
             "radar_spin": -6},
            {"design": "tank", "name": "snow tank",
             "position": [3.5, -0.4, 12], "velocity": [0, 0, -0.012],
             "size": 0.6, "angles": [180, 0, 0], "colour": (120, 190, 240), "palette": PALETTE_ICE,
             "gun": {"mode": "TRACK", "turret_spin": 0.8, "start_angle": "you", "volley": 3, "cooldown": 150},
             "radar_spin": 6},
            # ICE BUNKERS on the floor, in their rings, turrets SPINNING (different speeds and starts)
            {"design": "bunker", "name": "west ice bunker", "position": [-10, -0.7, -2], "size": 0.6, "colour": (120, 190, 240), "palette": PALETTE_ICE,
             "gun": {"mode": "SPIN", "turret_spin": 1.0, "start_angle": 0, "volley": 3}},
            {"design": "bunker", "name": "east ice bunker", "position": [10, -0.7, -2], "size": 0.6, "colour": (120, 190, 240), "palette": PALETTE_ICE,
             "gun": {"mode": "SPIN", "turret_spin": -1.0, "start_angle": 90, "volley": 3}},
            {"design": "bunker", "name": "middle ice bunker", "position": [0, -0.7, 4], "size": 0.6, "colour": (120, 190, 240), "palette": PALETTE_ICE,
             "gun": {"mode": "SPIN", "turret_spin": 1.2, "start_angle": 45, "volley": 3}},
            # ICE BUNKERS on the walls and the ceiling, black with blue edges like the icicles, cupolas TRACKING you
            {"design": "bunker", "name": "left wall ice bunker", "position": [-15.7, 3, 10], "size": 0.6,
             "angles": [0, 0, -90], "colour": (40, 90, 150), "palette": PALETTE_BLACK,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 3, "bullet_colour": (120, 190, 240), "bullet_palette": PALETTE_ICE},
             "children": [{"model": cupola_model}]},
            {"design": "bunker", "name": "right wall ice bunker", "position": [15.7, 3, -4], "size": 0.6,
             "angles": [0, 0, 90], "colour": (40, 90, 150), "palette": PALETTE_BLACK,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 3, "bullet_colour": (120, 190, 240), "bullet_palette": PALETTE_ICE},
             "children": [{"model": cupola_model}]},
            {"design": "bunker", "name": "far wall ice bunker", "position": [3, 3, 15.7], "size": 0.6,
             "angles": [0, -90, 0], "colour": (40, 90, 150), "palette": PALETTE_BLACK,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 3, "bullet_colour": (120, 190, 240), "bullet_palette": PALETTE_ICE},
             "children": [{"model": cupola_model}]},
            {"design": "bunker", "name": "ceiling ice bunker", "position": [-4, 6.7, 2], "size": 0.6,
             "angles": [0, 180, 0], "colour": (40, 90, 150), "palette": PALETTE_BLACK,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 3, "bullet_colour": (120, 190, 240), "bullet_palette": PALETTE_ICE},
             "children": [{"model": cupola_model}]},
            # ICE FRAMES and shapes in the air: frames shoot AT you, the diamond drops ice
            {"design": "frame", "name": "ice frame 1", "position": [-5, 3, 4], "velocity": [0.02, 0.012, -0.015],
             "size": "MEDIUM", "angles": [20, 30, 0], "speeds": (1, 0.6, 0), "colour": (120, 190, 240), "palette": PALETTE_ICE,
             "gun": {"mode": "TARGET", "volley": 1, "cooldown": 120}},
            {"design": "frame", "name": "ice frame 2", "position": [6, 4, 10], "velocity": [-0.018, -0.01, 0.014],
             "size": "MEDIUM", "angles": [-30, 10, 20], "speeds": (0.7, 1, 0.3), "colour": (120, 190, 240), "palette": PALETTE_ICE,
             "gun": {"mode": "TARGET", "volley": 1, "cooldown": 120}},
            {"design": "diamond", "name": "ice diamond", "position": [0, 4.5, -2], "velocity": [0.025, 0, 0.02],
             "size": "MEDIUM", "angles": [0, 0, 0], "speeds": (2, 0, 0), "colour": (120, 190, 240), "palette": PALETTE_ICE,
             "gun": {"mode": "DOWN", "volley": 1}},
            {"design": "cube", "name": "ice cube", "position": [8, 3, 4], "velocity": [-0.02, 0.015, 0.02],
             "size": "LARGE", "angles": [30, 20, 0], "speeds": (0.5, 0.8, 0), "colour": (120, 190, 240), "palette": PALETTE_ICE},
            # ICICLES on the ceiling, sliding side to side and dripping ice (level dressing: can't be killed)
            {"design": "pyramid", "name": "icicle 1",
             "position": [-8, 6.5, -5], "velocity": [0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0), "colour": (40, 90, 150), "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 60, "bullet_colour": (120, 190, 240), "bullet_palette": PALETTE_ICE},
             "scenery": True},
            {"design": "pyramid", "name": "icicle 2",
             "position": [6, 6.5, 0], "velocity": [-0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0), "colour": (40, 90, 150), "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 60, "bullet_colour": (120, 190, 240), "bullet_palette": PALETTE_ICE},
             "scenery": True},
            {"design": "pyramid", "name": "icicle 3",
             "position": [-3, 6.5, 7], "velocity": [0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0), "colour": (40, 90, 150), "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 60, "bullet_colour": (120, 190, 240), "bullet_palette": PALETTE_ICE},
             "scenery": True},
            {"design": "pyramid", "name": "icicle 4",
             "position": [9, 6.5, 11], "velocity": [-0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0), "colour": (40, 90, 150), "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 60, "bullet_colour": (120, 190, 240), "bullet_palette": PALETTE_ICE},
             "scenery": True},
        ],
    },

    10: {    # ---- LEVEL 10: THE FURNACE - the Canyon's size, all LAVA: obsidian, embers, a volcano, lava tanks and drippers ----
        "name": "The Furnace",
        "intro": "A river of lava and a smoking volcano. Cross at the gaps - and keep moving.",
        "world": {"min": (-16, -1, -16), "max": (16, 7, 16)},       # 32 wide (x), 32 long (z), 8 tall: the Canyon's size
        "start": {"x": 0, "y": 0, "z": -14, "turn": 0, "tip": 0},    # near the back wall, facing the far wall
        "grid_colour": (140, 35, 30),                              # a LAVA-red grid

        "floor_shapes": [
            # THE LAVA RIVER across the room (z 0 to 2), with two places to cross: x -9 to -7, and x 6 to 8
            {"type": "lava", "min": (-16, 0), "max": (-9, 2)},
            {"type": "lava", "min": (-7, 0), "max": (6, 2)},
            {"type": "lava", "min": (8, 0), "max": (16, 2)},
            # LAVA POOLS: round the volcano's foot, and one in the middle of the far half
            {"type": "lava", "min": (7, 7), "max": (13, 8)},          # in front of the volcano
            {"type": "lava", "min": (7, 8), "max": (8, 13)},          # down its left side
            {"type": "lava", "min": (0, 10), "max": (3, 13)},         # a pool in the far half
        ],
        "boxes": [
            # THE FURNACE, built from OBSIDIAN (dark faces, glowing red edges) and EMBER blocks (sunset colours).
            # YOUR CINDER WALL: a low U of cooled cinder round where you start (x 0, z -14), open behind you
            {"min": (-1.9, -1, -12.6), "max": (-1.5, -0.6, -12.2), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # front left corner
            {"min": (1.5, -1, -12.6), "max": (1.9, -0.6, -12.2), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # front right corner
            {"min": (-1.5, -1, -12.6), "max": (-0.5, -0.6, -12.2), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # front
            {"min": (-0.5, -1, -12.6), "max": (0.5, -0.6, -12.2), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (0.5, -1, -12.6), "max": (1.5, -0.6, -12.2), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (-1.9, -1, -13.6), "max": (-1.5, -0.6, -12.6), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # left side
            {"min": (1.5, -1, -13.6), "max": (1.9, -0.6, -12.6), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # right side
            {"min": (-1.9, -1, -14.4), "max": (-1.5, -0.6, -13.6), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (1.5, -1, -14.4), "max": (1.9, -0.6, -13.6), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            # THE OBSIDIAN WALL: cover across the front (z -8.6 to -8.2), x -7 to 7: tall ends, a LOW middle, gaps, and a WINDOW at x 3 to 4
            {"min": (-7, -1, -8.6), "max": (-6, 1.7, -8.2), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # the obsidian wall
            {"min": (-6, -1, -8.6), "max": (-5, 2.1, -8.2), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (-5, -1, -8.6), "max": (-4, 1.3, -8.2), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (-2, -1, -8.6), "max": (-1, -0.2, -8.2), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (-1, -1, -8.6), "max": (0, 0.4, -8.2), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (0, -1, -8.6), "max": (1, -0.4, -8.2), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (2, -1, -8.6), "max": (3, 0.2, -8.2), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (3, -1, -8.6), "max": (4, -0.3, -8.2), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # the obsidian wall: under the window
            {"min": (3, 0.4, -8.6), "max": (4, 1.9, -8.2), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # the obsidian wall: over the window (y -0.3 to 0.4)
            {"min": (4, -1, -8.6), "max": (5, 1.6, -8.2), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (5, -1, -8.6), "max": (6, 2, -8.2), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (6, -1, -8.6), "max": (7, 1.4, -8.2), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            # THE BROKEN RIDGE: a long obsidian wall down the left side (x -6.4 to -6, z 3 to 12), gaps to slip through
            {"min": (-6.4, -1, 3), "max": (-6, 1.5, 4), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # the ridge
            {"min": (-6.4, -1, 4), "max": (-6, 2.2, 5), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (-6.4, -1, 5), "max": (-6, 1, 6), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (-6.4, -1, 7), "max": (-6, 1.8, 8), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (-6.4, -1, 8), "max": (-6, 2.4, 9), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (-6.4, -1, 9), "max": (-6, 0.6, 10), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (-6.4, -1, 11), "max": (-6, 1.4, 12), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            # THE VOLCANO: a stepped cone at the back right (centre x 10, z 10): 4 x 4, then 2 x 2, then the glowing VENT
            {"min": (8, -1, 8), "max": (9, 0, 9), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # volcano: bottom step (4 x 4)
            {"min": (8, -1, 9), "max": (9, 0, 10), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (8, -1, 10), "max": (9, 0, 11), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (8, -1, 11), "max": (9, 0, 12), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (9, -1, 8), "max": (10, 0, 9), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (9, -1, 9), "max": (10, 0, 10), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (9, -1, 10), "max": (10, 0, 11), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (9, -1, 11), "max": (10, 0, 12), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (10, -1, 8), "max": (11, 0, 9), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (10, -1, 9), "max": (11, 0, 10), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (10, -1, 10), "max": (11, 0, 11), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (10, -1, 11), "max": (11, 0, 12), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (11, -1, 8), "max": (12, 0, 9), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (11, -1, 9), "max": (12, 0, 10), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (11, -1, 10), "max": (12, 0, 11), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (11, -1, 11), "max": (12, 0, 12), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (9, 0, 9), "max": (10, 1, 10), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # volcano: middle step (2 x 2)
            {"min": (9, 0, 10), "max": (10, 1, 11), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (10, 0, 9), "max": (11, 1, 10), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (10, 0, 10), "max": (11, 1, 11), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (9.6, 1, 9.6), "max": (10.4, 1.5, 10.4), "colour": EMBER, "palette": PALETTE_SUNSET},   # volcano: the VENT, glowing
            # THE BASALT PILLAR: floor to CEILING, jagged (8 layers, each 1 tall)
            {"min": (-12.1, -1, 10), "max": (-9.9, 0, 12.1), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # basalt pillar: layer 1
            {"min": (-11.75, 0, 10.25), "max": (-10.15, 1, 11.95), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # basalt pillar: layer 2
            {"min": (-11.75, 1, 10.15), "max": (-10.35, 2, 11.75), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # basalt pillar: layer 3
            {"min": (-11.55, 2, 10.45), "max": (-10.35, 3, 11.55), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # basalt pillar: layer 4
            {"min": (-11.7, 3, 10.3), "max": (-10.2, 4, 11.8), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # basalt pillar: layer 5
            {"min": (-11.9, 4, 10.3), "max": (-10.2, 5, 11.8), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # basalt pillar: layer 6
            {"min": (-11.8, 5, 10), "max": (-10, 6, 12), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # basalt pillar: layer 7
            {"min": (-12.1, 6, 9.9), "max": (-9.9, 7, 12.1), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # basalt pillar: layer 8
            # EMBER ROCKS: hot sunset-coloured blocks, low cover scattered in the open
            {"min": (-9, -1, -6), "max": (-8, 0, -5), "colour": EMBER, "palette": PALETTE_SUNSET},   # embers, left
            {"min": (-8, -1, -6), "max": (-7, 0, -5), "colour": EMBER, "palette": PALETTE_SUNSET},
            {"min": (4, -1, -5), "max": (5, 0, -4), "colour": EMBER, "palette": PALETTE_SUNSET},   # embers, right
            {"min": (4, -1, -4), "max": (5, 0, -3), "colour": EMBER, "palette": PALETTE_SUNSET},
            {"min": (-1, -1, 5), "max": (0, 0, 6), "colour": EMBER, "palette": PALETTE_SUNSET},   # embers, middle
            {"min": (-1, 0, 5), "max": (0, 1, 6), "colour": EMBER, "palette": PALETTE_SUNSET},
            {"min": (0, -1, 5), "max": (1, 0, 6), "colour": EMBER, "palette": PALETTE_SUNSET},
            # OBSIDIAN RINGS round the floor bunkers: low (0.4 tall, under their guns), a GAP facing the back
            {"min": (-13, -1, -1.5), "max": (-12.5, -0.6, -1), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # west ring: corner
            {"min": (-9.5, -1, -1.5), "max": (-9, -0.6, -1), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # corner
            {"min": (-13, -1, -5), "max": (-12.5, -0.6, -4.5), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # corner
            {"min": (-9.5, -1, -5), "max": (-9, -0.6, -4.5), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # corner
            {"min": (-12.5, -1, -1.5), "max": (-11.5, -0.6, -1), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # far side
            {"min": (-11.5, -1, -1.5), "max": (-10.5, -0.6, -1), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (-10.5, -1, -1.5), "max": (-9.5, -0.6, -1), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (-13, -1, -4.5), "max": (-12.5, -0.6, -3.5), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # left side
            {"min": (-9.5, -1, -4.5), "max": (-9, -0.6, -3.5), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # right side
            {"min": (-13, -1, -3.5), "max": (-12.5, -0.6, -2.5), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (-9.5, -1, -3.5), "max": (-9, -0.6, -2.5), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (-13, -1, -2.5), "max": (-12.5, -0.6, -1.5), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (-9.5, -1, -2.5), "max": (-9, -0.6, -1.5), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (-12.5, -1, -5), "max": (-12, -0.6, -4.5), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # near side, left part ...
            {"min": (-10, -1, -5), "max": (-9.5, -0.6, -4.5), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # ... and right part: the GAP is between them
            {"min": (9, -1, -1.5), "max": (9.5, -0.6, -1), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # east ring: corner
            {"min": (12.5, -1, -1.5), "max": (13, -0.6, -1), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # corner
            {"min": (9, -1, -5), "max": (9.5, -0.6, -4.5), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # corner
            {"min": (12.5, -1, -5), "max": (13, -0.6, -4.5), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # corner
            {"min": (9.5, -1, -1.5), "max": (10.5, -0.6, -1), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # far side
            {"min": (10.5, -1, -1.5), "max": (11.5, -0.6, -1), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (11.5, -1, -1.5), "max": (12.5, -0.6, -1), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (9, -1, -4.5), "max": (9.5, -0.6, -3.5), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # left side
            {"min": (12.5, -1, -4.5), "max": (13, -0.6, -3.5), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # right side
            {"min": (9, -1, -3.5), "max": (9.5, -0.6, -2.5), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (12.5, -1, -3.5), "max": (13, -0.6, -2.5), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (9, -1, -2.5), "max": (9.5, -0.6, -1.5), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (12.5, -1, -2.5), "max": (13, -0.6, -1.5), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},
            {"min": (9.5, -1, -5), "max": (10, -0.6, -4.5), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # near side, left part ...
            {"min": (12, -1, -5), "max": (12.5, -0.6, -4.5), "colour": OBSIDIAN, "palette": PALETTE_OBSIDIAN},   # ... and right part: the GAP is between them
        ],
        "spawn": [
            # LAVA TANKS on patrol (fireproof: they drive straight through the lava)
            {"design": "tank", "name": "lava tank",
             "position": [-12, -0.4, 1.5], "velocity": [0.015, 0, 0],
             "size": 0.6, "angles": [-90, 0, 0], "colour": (255, 120, 60), "palette": PALETTE_SUNSET,
             "gun": {"mode": "TRACK", "turret_spin": 0.8, "start_angle": "you", "volley": 3, "cooldown": 150},
             "radar_spin": -6},
            {"design": "tank", "name": "magma tank",
             "position": [2.5, -0.4, 12], "velocity": [0, 0, -0.012],
             "size": 1, "angles": [180, 0, 0], "colour": (255, 120, 60), "palette": PALETTE_SUNSET,
             "gun": {"mode": "TRACK", "turret_spin": 0.6, "start_angle": "you", "volley": 3, "cooldown": 170},
             "radar_spin": 6},
            # SUNSET BUNKERS on the floor, in their obsidian rings, turrets SPINNING
            {"design": "bunker", "name": "west lava bunker", "position": [-11, -0.7, -3], "size": 0.6, "colour": (255, 120, 60), "palette": PALETTE_SUNSET,
             "gun": {"mode": "SPIN", "turret_spin": 1.0, "start_angle": 0, "volley": 3}},
            {"design": "bunker", "name": "east lava bunker", "position": [11, -0.7, -3], "size": 0.6, "colour": (255, 120, 60), "palette": PALETTE_SUNSET,
             "gun": {"mode": "SPIN", "turret_spin": -1.1, "start_angle": 120, "volley": 3}},
            # OBSIDIAN BUNKERS on the walls and ceiling (black, red edges, like the drippers), firing LAVA
            {"design": "bunker", "name": "left wall lava bunker", "position": [-15.7, 3, -2], "size": 0.6,
             "angles": [0, 0, -90], "colour": (140, 35, 30), "palette": PALETTE_BLACK,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 3, "bullet_colour": (255, 120, 60), "bullet_palette": PALETTE_SUNSET},
             "children": [{"model": cupola_model}]},
            {"design": "bunker", "name": "right wall lava bunker", "position": [15.7, 3, 5], "size": 0.6,
             "angles": [0, 0, 90], "colour": (140, 35, 30), "palette": PALETTE_BLACK,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 3, "bullet_colour": (255, 120, 60), "bullet_palette": PALETTE_SUNSET},
             "children": [{"model": cupola_model}]},
            {"design": "bunker", "name": "far wall lava bunker", "position": [-4, 3, 15.7], "size": 0.6,
             "angles": [0, -90, 0], "colour": (140, 35, 30), "palette": PALETTE_BLACK,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 3, "bullet_colour": (255, 120, 60), "bullet_palette": PALETTE_SUNSET},
             "children": [{"model": cupola_model}]},
            {"design": "bunker", "name": "ceiling lava bunker", "position": [3, 6.7, -3], "size": 0.6,
             "angles": [0, 180, 0], "colour": (140, 35, 30), "palette": PALETTE_BLACK,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 3, "bullet_colour": (255, 120, 60), "bullet_palette": PALETTE_SUNSET},
             "children": [{"model": cupola_model}]},
            # SUNSET shapes in the air: frames shoot AT you, the pyramid drops lava
            {"design": "frame", "name": "lava frame 1", "position": [-4, 3, 7], "velocity": [0.02, -0.012, 0.015],
             "size": "MEDIUM", "angles": [20, 30, 0], "speeds": (1, 0.6, 0), "colour": (255, 120, 60), "palette": PALETTE_SUNSET,
             "gun": {"mode": "TARGET", "volley": 1, "cooldown": 120}},
            {"design": "frame", "name": "lava frame 2", "position": [5, 4, -2], "velocity": [-0.018, 0.01, -0.014],
             "size": "MEDIUM", "angles": [-30, 10, 20], "speeds": (0.7, 1, 0.3), "colour": (255, 120, 60), "palette": PALETTE_SUNSET,
             "gun": {"mode": "TARGET", "volley": 1, "cooldown": 120}},
            {"design": "pyramid", "name": "lava pyramid", "position": [0, 4.5, 3], "velocity": [0.025, 0, -0.02],
             "size": "MEDIUM", "angles": [15, 0, 0], "speeds": (1.5, 0, 0), "colour": (255, 120, 60), "palette": PALETTE_SUNSET,
             "gun": {"mode": "DOWN", "volley": 1}},
            {"design": "diamond", "name": "lava diamond", "position": [-9, 2.5, 4], "velocity": [0.02, 0.02, -0.02],
             "size": "LARGE", "angles": [0, 30, 15], "speeds": (0.8, 0.5, 0.3), "colour": (255, 120, 60), "palette": PALETTE_SUNSET},
            # LAVA DRIPPERS on the ceiling, sliding side to side and dripping lava (level dressing: can't be killed)
            {"design": "pyramid", "name": "lava dripper 1",
             "position": [-6, 6.5, 1], "velocity": [0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0), "colour": (140, 35, 30), "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 50, "bullet_colour": (255, 120, 60), "bullet_palette": PALETTE_SUNSET},
             "scenery": True},
            {"design": "pyramid", "name": "lava dripper 2",
             "position": [4, 6.5, 1], "velocity": [-0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0), "colour": (140, 35, 30), "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 50, "bullet_colour": (255, 120, 60), "bullet_palette": PALETTE_SUNSET},
             "scenery": True},
            {"design": "pyramid", "name": "lava dripper 3",
             "position": [-2, 6.5, 9], "velocity": [0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0), "colour": (140, 35, 30), "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 50, "bullet_colour": (255, 120, 60), "bullet_palette": PALETTE_SUNSET},
             "scenery": True},
            {"design": "pyramid", "name": "lava dripper 4",
             "position": [10, 6.5, -5], "velocity": [-0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0), "colour": (140, 35, 30), "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 50, "bullet_colour": (255, 120, 60), "bullet_palette": PALETTE_SUNSET},
             "scenery": True},
        ],
    },

    11: {    # ---- LEVEL 11: THE SLUDGE PIT - the Canyon's size, all SLIME: sludge, barrels, a slime channel, slime tanks ----
        "name": "The Sludge Pit",
        "intro": "Toxic slime: it burns AND it sticks. Cross the channel on the walkways.",
        "world": {"min": (-16, -1, -16), "max": (16, 7, 16)},       # 32 wide (x), 32 long (z), 8 tall: the Canyon's size
        "start": {"x": 0, "y": 0, "z": -14, "turn": 0, "tip": 0},    # near the back wall, facing the far wall
        "grid_colour": (50, 110, 40),                              # a SLIME-green grid

        "floor_shapes": [
            # THE SLIME CHANNEL down the middle (x -3 to 3), with three WALKWAYS across it (z -3 to -2, 3 to 4, 9 to 10)
            {"type": "slime", "min": (-3, -6), "max": (3, -3)},
            {"type": "slime", "min": (-3, -2), "max": (3, 3)},
            {"type": "slime", "min": (-3, 4), "max": (3, 9)},
            # SLIME POOLS
            {"type": "slime", "min": (-15, 8), "max": (-11, 11)},     # by the left mound
            {"type": "slime", "min": (6, 5), "max": (9, 8)},          # by the right mound
            {"type": "slime", "min": (-11, -11), "max": (-8, -9)},    # near the back left
        ],
        "boxes": [
            # THE SLUDGE PIT, built from SLUDGE (dark green faces, glowing lime edges) and toxic BARRELS (lime).
            # YOUR SANDBAGS: a low U round where you start (x 0, z -14), open behind you
            {"min": (-1.9, -1, -12.6), "max": (-1.5, -0.6, -12.2), "colour": SAND, "palette": PALETTE_SAND},   # front left corner
            {"min": (1.5, -1, -12.6), "max": (1.9, -0.6, -12.2), "colour": SAND, "palette": PALETTE_SAND},   # front right corner
            {"min": (-1.5, -1, -12.6), "max": (-0.5, -0.6, -12.2), "colour": SAND, "palette": PALETTE_SAND},   # front
            {"min": (-0.5, -1, -12.6), "max": (0.5, -0.6, -12.2), "colour": SAND, "palette": PALETTE_SAND},
            {"min": (0.5, -1, -12.6), "max": (1.5, -0.6, -12.2), "colour": SAND, "palette": PALETTE_SAND},
            {"min": (-1.9, -1, -13.6), "max": (-1.5, -0.6, -12.6), "colour": SAND, "palette": PALETTE_SAND},   # left side
            {"min": (1.5, -1, -13.6), "max": (1.9, -0.6, -12.6), "colour": SAND, "palette": PALETTE_SAND},   # right side
            {"min": (-1.9, -1, -14.4), "max": (-1.5, -0.6, -13.6), "colour": SAND, "palette": PALETTE_SAND},
            {"min": (1.5, -1, -14.4), "max": (1.9, -0.6, -13.6), "colour": SAND, "palette": PALETTE_SAND},
            # THE SEWER WALLS: two broken walls along the slime channel (x -3.4 to -3 and 3 to 3.4), gaps to cross through
            {"min": (-3.4, -1, -6), "max": (-3, 1.2, -5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # left sewer wall
            {"min": (-3.4, -1, -5), "max": (-3, 0.4, -4), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (-3.4, -1, -3), "max": (-3, 1.6, -2), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (-3.4, -1, -2), "max": (-3, 1.8, -1), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (-3.4, -1, 0), "max": (-3, 0.2, 1), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (-3.4, -1, 1), "max": (-3, 1.4, 2), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (-3.4, -1, 2), "max": (-3, 1, 3), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (-3.4, -1, 4), "max": (-3, 1.7, 5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (-3.4, -1, 5), "max": (-3, 1.2, 6), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (-3.4, -1, 7), "max": (-3, 0.6, 8), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (-3.4, -1, 8), "max": (-3, 1.5, 9), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (3, -1, -6), "max": (3.4, 0.6, -5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # right sewer wall
            {"min": (3, -1, -5), "max": (3.4, 1.5, -4), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (3, -1, -3), "max": (3.4, 0.3, -2), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (3, -1, -2), "max": (3.4, 1.7, -1), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (3, -1, -1), "max": (3.4, 1.9, 0), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (3, -1, 1), "max": (3.4, 1.1, 2), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (3, -1, 3), "max": (3.4, 1.6, 4), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (3, -1, 4), "max": (3.4, 0.4, 5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (3, -1, 6), "max": (3.4, 1.8, 7), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (3, -1, 7), "max": (3.4, 1, 8), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (3, -1, 8), "max": (3.4, 1.4, 9), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            # SLUDGE MOUNDS: stepped heaps of muck (3 x 3, then 1 x 1) - cover, and somewhere to stand
            {"min": (-12, -1, 6), "max": (-11, 0, 7), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # left mound: step 1 (3 x 3)
            {"min": (-12, -1, 7), "max": (-11, 0, 8), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (-12, -1, 8), "max": (-11, 0, 9), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (-11, -1, 6), "max": (-10, 0, 7), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (-11, -1, 7), "max": (-10, 0, 8), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (-11, -1, 8), "max": (-10, 0, 9), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (-10, -1, 6), "max": (-9, 0, 7), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (-10, -1, 7), "max": (-9, 0, 8), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (-10, -1, 8), "max": (-9, 0, 9), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (-11, 0, 7), "max": (-10, 1, 8), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # left mound: step 2 (1 x 1)
            {"min": (9, -1, 9), "max": (10, 0, 10), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # right mound: step 1 (3 x 3)
            {"min": (9, -1, 10), "max": (10, 0, 11), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (9, -1, 11), "max": (10, 0, 12), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (10, -1, 9), "max": (11, 0, 10), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (10, -1, 10), "max": (11, 0, 11), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (10, -1, 11), "max": (11, 0, 12), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (11, -1, 9), "max": (12, 0, 10), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (11, -1, 10), "max": (12, 0, 11), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (11, -1, 11), "max": (12, 0, 12), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (10, 0, 10), "max": (11, 1, 11), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # right mound: step 2 (1 x 1)
            # TOXIC BARRELS: stacks of glowing barrels (1 x 1, 1 or 2 high)
            {"min": (-8, -1, -6), "max": (-7, 0, -5), "colour": SLIME, "palette": PALETTE_SLIME},   # barrels, left
            {"min": (-8, 0, -6), "max": (-7, 1, -5), "colour": SLIME, "palette": PALETTE_SLIME},
            {"min": (-7, -1, -6), "max": (-6, 0, -5), "colour": SLIME, "palette": PALETTE_SLIME},
            {"min": (7, -1, -5), "max": (8, 0, -4), "colour": SLIME, "palette": PALETTE_SLIME},   # barrels, right
            {"min": (7, -1, -4), "max": (8, 0, -3), "colour": SLIME, "palette": PALETTE_SLIME},
            {"min": (7, 0, -4), "max": (8, 1, -3), "colour": SLIME, "palette": PALETTE_SLIME},
            {"min": (-7, -1, 11), "max": (-6, 0, 12), "colour": SLIME, "palette": PALETTE_SLIME},   # barrels, far left
            {"min": (-7, 0, 11), "max": (-6, 1, 12), "colour": SLIME, "palette": PALETTE_SLIME},
            {"min": (-6, -1, 12), "max": (-5, 0, 13), "colour": SLIME, "palette": PALETTE_SLIME},
            {"min": (11, -1, 2), "max": (12, 0, 3), "colour": SLIME, "palette": PALETTE_SLIME},   # barrels, far right
            {"min": (12, -1, 2), "max": (13, 0, 3), "colour": SLIME, "palette": PALETTE_SLIME},
            {"min": (12, 0, 2), "max": (13, 1, 3), "colour": SLIME, "palette": PALETTE_SLIME},
            # THE OUTFLOW PIPES: two floor-to-CEILING columns of sludge, jagged (8 layers, each 1 tall)
            {"min": (-13, -1, -2.9), "max": (-11, 0, -1), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # left pipe: layer 1
            {"min": (-12.65, 0, -2.65), "max": (-11.25, 1, -1.15), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # left pipe: layer 2
            {"min": (-12.65, 1, -2.75), "max": (-11.45, 2, -1.35), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # left pipe: layer 3
            {"min": (-12.45, 2, -2.45), "max": (-11.45, 3, -1.55), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # left pipe: layer 4
            {"min": (-12.6, 3, -2.6), "max": (-11.3, 4, -1.3), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # left pipe: layer 5
            {"min": (-12.8, 4, -2.6), "max": (-11.3, 5, -1.3), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # left pipe: layer 6
            {"min": (-12.7, 5, -2.9), "max": (-11.1, 6, -1.1), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # left pipe: layer 7
            {"min": (-13, 6, -3), "max": (-11, 7, -1), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # left pipe: layer 8
            {"min": (11, -1, 11), "max": (13, 0, 13), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # right pipe: layer 1
            {"min": (11.3, 0, 11.1), "max": (12.9, 1, 12.9), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # right pipe: layer 2
            {"min": (11.2, 1, 11.4), "max": (12.7, 2, 12.7), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # right pipe: layer 3
            {"min": (11.4, 2, 11.4), "max": (12.7, 3, 12.7), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # right pipe: layer 4
            {"min": (11.55, 3, 11.55), "max": (12.55, 4, 12.45), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # right pipe: layer 5
            {"min": (11.35, 4, 11.25), "max": (12.55, 5, 12.65), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # right pipe: layer 6
            {"min": (11.35, 5, 11.35), "max": (12.75, 6, 12.85), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # right pipe: layer 7
            {"min": (11, 6, 11.1), "max": (13, 7, 13), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # right pipe: layer 8
            # SLUDGE RINGS round the floor bunkers: low (0.4 tall, under their guns), a GAP facing the back
            {"min": (-11, -1, 3.5), "max": (-10.5, -0.6, 4), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # west ring: corner
            {"min": (-7.5, -1, 3.5), "max": (-7, -0.6, 4), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # corner
            {"min": (-11, -1, 0), "max": (-10.5, -0.6, 0.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # corner
            {"min": (-7.5, -1, 0), "max": (-7, -0.6, 0.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # corner
            {"min": (-10.5, -1, 3.5), "max": (-9.5, -0.6, 4), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # far side
            {"min": (-9.5, -1, 3.5), "max": (-8.5, -0.6, 4), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (-8.5, -1, 3.5), "max": (-7.5, -0.6, 4), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (-11, -1, 0.5), "max": (-10.5, -0.6, 1.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # left side
            {"min": (-7.5, -1, 0.5), "max": (-7, -0.6, 1.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # right side
            {"min": (-11, -1, 1.5), "max": (-10.5, -0.6, 2.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (-7.5, -1, 1.5), "max": (-7, -0.6, 2.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (-11, -1, 2.5), "max": (-10.5, -0.6, 3.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (-7.5, -1, 2.5), "max": (-7, -0.6, 3.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (-10.5, -1, 0), "max": (-10, -0.6, 0.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # near side, left part ...
            {"min": (-8, -1, 0), "max": (-7.5, -0.6, 0.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # ... and right part: the GAP is between them
            {"min": (6, -1, 0.5), "max": (6.5, -0.6, 1), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # east ring: corner
            {"min": (9.5, -1, 0.5), "max": (10, -0.6, 1), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # corner
            {"min": (6, -1, -3), "max": (6.5, -0.6, -2.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # corner
            {"min": (9.5, -1, -3), "max": (10, -0.6, -2.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # corner
            {"min": (6.5, -1, 0.5), "max": (7.5, -0.6, 1), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # far side
            {"min": (7.5, -1, 0.5), "max": (8.5, -0.6, 1), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (8.5, -1, 0.5), "max": (9.5, -0.6, 1), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (6, -1, -2.5), "max": (6.5, -0.6, -1.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # left side
            {"min": (9.5, -1, -2.5), "max": (10, -0.6, -1.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # right side
            {"min": (6, -1, -1.5), "max": (6.5, -0.6, -0.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (9.5, -1, -1.5), "max": (10, -0.6, -0.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (6, -1, -0.5), "max": (6.5, -0.6, 0.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (9.5, -1, -0.5), "max": (10, -0.6, 0.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (6.5, -1, -3), "max": (7, -0.6, -2.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # near side, left part ...
            {"min": (9, -1, -3), "max": (9.5, -0.6, -2.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # ... and right part: the GAP is between them
            {"min": (-2, -1, 13.5), "max": (-1.5, -0.6, 14), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # far ring: corner
            {"min": (1.5, -1, 13.5), "max": (2, -0.6, 14), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # corner
            {"min": (-2, -1, 10), "max": (-1.5, -0.6, 10.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # corner
            {"min": (1.5, -1, 10), "max": (2, -0.6, 10.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # corner
            {"min": (-1.5, -1, 13.5), "max": (-0.5, -0.6, 14), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # far side
            {"min": (-0.5, -1, 13.5), "max": (0.5, -0.6, 14), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (0.5, -1, 13.5), "max": (1.5, -0.6, 14), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (-2, -1, 10.5), "max": (-1.5, -0.6, 11.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # left side
            {"min": (1.5, -1, 10.5), "max": (2, -0.6, 11.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # right side
            {"min": (-2, -1, 11.5), "max": (-1.5, -0.6, 12.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (1.5, -1, 11.5), "max": (2, -0.6, 12.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (-2, -1, 12.5), "max": (-1.5, -0.6, 13.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (1.5, -1, 12.5), "max": (2, -0.6, 13.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},
            {"min": (-1.5, -1, 10), "max": (-1, -0.6, 10.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # near side, left part ...
            {"min": (1, -1, 10), "max": (1.5, -0.6, 10.5), "colour": SLUDGE, "palette": PALETTE_SLUDGE},   # ... and right part: the GAP is between them
        ],
        "spawn": [
            {"design": "tank", "name": "slime tank",
             "position": [-12, -0.4, -7.5], "velocity": [0.015, 0, 0],
             "size": 0.6, "angles": [-90, 0, 0], "colour": SLIME, "palette": PALETTE_SLIME,
             "gun": {"mode": "TRACK", "turret_spin": 0.8, "start_angle": "you", "volley": 3, "cooldown": 150},
             "radar_spin": -6},
            {"design": "tank", "name": "sludge tank",
             "position": [0, 0, 8], "velocity": [0, 0, -0.012],
             "size": 1, "angles": [180, 0, 0], "colour": SLIME, "palette": PALETTE_SLIME,
             "gun": {"mode": "TRACK", "turret_spin": 0.8, "start_angle": "you", "volley": 3, "cooldown": 150},
             "radar_spin": -6},
            {"design": "bunker", "name": "west slime bunker", "position": [-9, -0.7, 2], "size": 0.6, "colour": SLIME, "palette": PALETTE_SLIME,
             "gun": {"mode": "SPIN", "turret_spin": 1.0, "start_angle": 0, "volley": 3}},
            {"design": "bunker", "name": "east slime bunker", "position": [8, -0.7, -1], "size": 0.6, "colour": SLIME, "palette": PALETTE_SLIME,
             "gun": {"mode": "SPIN", "turret_spin": -1.1, "start_angle": 90, "volley": 3}},
            {"design": "bunker", "name": "far slime bunker", "position": [0, -0.7, 12], "size": 0.6, "colour": SLIME, "palette": PALETTE_SLIME,
             "gun": {"mode": "SPIN", "turret_spin": 1.2, "start_angle": 200, "volley": 3}},
            {"design": "bunker", "name": "left wall slime bunker", "position": [-15.7, 3, 6], "size": 0.6,
             "angles": [0, 0, -90], "colour": SLUDGE, "palette": PALETTE_BLACK,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 3, "bullet_colour": (140, 230, 60), "bullet_palette": PALETTE_SLIME},
             "children": [{"model": cupola_model}]},
            {"design": "bunker", "name": "right wall slime bunker", "position": [15.7, 3, -3], "size": 0.6,
             "angles": [0, 0, 90], "colour": SLUDGE, "palette": PALETTE_BLACK,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 3, "bullet_colour": (140, 230, 60), "bullet_palette": PALETTE_SLIME},
             "children": [{"model": cupola_model}]},
            {"design": "bunker", "name": "ceiling slime bunker", "position": [6, 6.7, 4], "size": 0.6,
             "angles": [0, 180, 0], "colour": SLUDGE, "palette": PALETTE_BLACK,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 3, "bullet_colour": (140, 230, 60), "bullet_palette": PALETTE_SLIME},
             "children": [{"model": cupola_model}]},
            {"design": "frame", "name": "slime frame 1", "position": [-6, 3, 3], "velocity": [0.02, 0.012, -0.015],
             "size": "MEDIUM", "angles": [20, 30, 0], "speeds": (0.9, 0.6, 0.2), "colour": SLIME, "palette": PALETTE_SLIME,
             "gun": {"mode": "TARGET", "volley": 1, "cooldown": 120}},
            {"design": "frame", "name": "slime frame 2", "position": [7, 4, 10], "velocity": [-0.018, -0.01, 0.014],
             "size": "MEDIUM", "angles": [20, 30, 0], "speeds": (0.9, 0.6, 0.2), "colour": SLIME, "palette": PALETTE_SLIME,
             "gun": {"mode": "TARGET", "volley": 1, "cooldown": 120}},
            {"design": "pyramid", "name": "slime pyramid", "position": [0, 4.5, 0], "velocity": [0.025, 0, 0.02],
             "size": "MEDIUM", "angles": [20, 30, 0], "speeds": (0.9, 0.6, 0.2), "colour": SLIME, "palette": PALETTE_SLIME,
             "gun": {"mode": "DOWN", "volley": 1}},
            {"design": "cube", "name": "slime cube", "position": [-4, 3, 8], "velocity": [0.02, 0.015, -0.02],
             "size": "LARGE", "angles": [20, 30, 0], "speeds": (0.9, 0.6, 0.2), "colour": SLIME, "palette": PALETTE_SLIME},
            {"design": "pyramid", "name": "slime dripper 1",
             "position": [-6, 6.5, -4], "velocity": [0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0), "colour": SLUDGE, "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 55, "bullet_colour": (140, 230, 60), "bullet_palette": PALETTE_SLIME},
             "scenery": True},
            {"design": "pyramid", "name": "slime dripper 2",
             "position": [5, 6.5, 1], "velocity": [-0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0), "colour": SLUDGE, "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 55, "bullet_colour": (140, 230, 60), "bullet_palette": PALETTE_SLIME},
             "scenery": True},
            {"design": "pyramid", "name": "slime dripper 3",
             "position": [-2, 6.5, 7], "velocity": [0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0), "colour": SLUDGE, "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 55, "bullet_colour": (140, 230, 60), "bullet_palette": PALETTE_SLIME},
             "scenery": True},
            {"design": "pyramid", "name": "slime dripper 4",
             "position": [9, 6.5, 13], "velocity": [-0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0), "colour": SLUDGE, "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 55, "bullet_colour": (140, 230, 60), "bullet_palette": PALETTE_SLIME},
             "scenery": True},
        ],
    },

    12: {    # ---- LEVEL 12: CUPID CANYON - the Trifle's layout, all PINK: candy walls, rose towers, a pink goo lake ----
        "name": "Cupid Canyon",
        "intro": "Everything is pink - and everything still wants you dead. The goo is thick: jump it.",
        "world": {"min": (-16, -1, -16), "max": (16, 7, 16)},       # 32 wide (x), 32 long (z), 8 tall: the Canyon's size
        "start": {"x": 0, "y": 0, "z": -14, "turn": 0, "tip": 0},    # near the back wall, facing the far wall
        "grid_colour": (150, 60, 100),                             # a PINK grid

        "floor_shapes": [
            # THE PINK GOO LAKE across the middle (z 0 to 5): a "custard" floor - it doesn't hurt, it SLOWS you right down
            {"type": "custard", "min": (-16, 0), "max": (16, 5), "colour": (255, 175, 210)},
            # PUDDLES
            {"type": "custard", "min": (-3, -6), "max": (1, -3), "colour": (255, 175, 210)},     # in front of the wall's gap
            {"type": "custard", "min": (8, 6), "max": (12, 8), "colour": (255, 175, 210)},       # under the right tower
            {"type": "custard", "min": (-13, 6), "max": (-9, 8), "colour": (255, 175, 210)},     # under the left tower
        ],
        "boxes": [
            # CUPID CANYON, built from CANDY blocks (CANDY) and ROSE TOWERS (ROSE).
            # YOUR COVER: a low U of candy round where you start (x 0, z -14), open behind you
            {"min": (-1.9, -1, -12.6), "max": (-1.5, -0.6, -12.2), "colour": CANDY, "palette": PALETTE_CANDY},   # front left corner
            {"min": (1.5, -1, -12.6), "max": (1.9, -0.6, -12.2), "colour": CANDY, "palette": PALETTE_CANDY},   # front right corner
            {"min": (-1.5, -1, -12.6), "max": (-0.5, -0.6, -12.2), "colour": CANDY, "palette": PALETTE_CANDY},   # front
            {"min": (-0.5, -1, -12.6), "max": (0.5, -0.6, -12.2), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (0.5, -1, -12.6), "max": (1.5, -0.6, -12.2), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (-1.9, -1, -13.6), "max": (-1.5, -0.6, -12.6), "colour": CANDY, "palette": PALETTE_CANDY},   # left side
            {"min": (1.5, -1, -13.6), "max": (1.9, -0.6, -12.6), "colour": CANDY, "palette": PALETTE_CANDY},   # right side
            {"min": (-1.9, -1, -14.4), "max": (-1.5, -0.6, -13.6), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (1.5, -1, -14.4), "max": (1.9, -0.6, -13.6), "colour": CANDY, "palette": PALETTE_CANDY},
            # THE CANDY WALL: cover across the front (z -8.6 to -8.2), tall ends, a low middle, gaps, a WINDOW at x 4 to 5
            {"min": (-7, -1, -8.6), "max": (-6, 1.5, -8.2), "colour": CANDY, "palette": PALETTE_CANDY},   # the candy wall
            {"min": (-6, -1, -8.6), "max": (-5, 1.9, -8.2), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (-5, -1, -8.6), "max": (-4, 1.2, -8.2), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (-3, -1, -8.6), "max": (-2, -0.2, -8.2), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (-2, -1, -8.6), "max": (-1, 0.5, -8.2), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (-1, -1, -8.6), "max": (0, -0.4, -8.2), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (1, -1, -8.6), "max": (2, 0.1, -8.2), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (3, -1, -8.6), "max": (4, -0.3, -8.2), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (4, -1, -8.6), "max": (5, -0.3, -8.2), "colour": CANDY, "palette": PALETTE_CANDY},   # the candy wall: under the window
            {"min": (4, 0.4, -8.6), "max": (5, 1.8, -8.2), "colour": CANDY, "palette": PALETTE_CANDY},   # the candy wall: over the window (y -0.3 to 0.4)
            {"min": (5, -1, -8.6), "max": (6, 2, -8.2), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (6, -1, -8.6), "max": (7, 1.3, -8.2), "colour": CANDY, "palette": PALETTE_CANDY},
            # THE ROSE TOWERS: three floor-to-CEILING wobbly columns (8 layers, each 1 tall)
            {"min": (-11, -1, 8.1), "max": (-9, 0, 10), "colour": ROSE, "palette": PALETTE_ROSE},   # left rose tower: layer 1
            {"min": (-10.65, 0, 8.35), "max": (-9.25, 1, 9.85), "colour": ROSE, "palette": PALETTE_ROSE},   # left rose tower: layer 2
            {"min": (-10.65, 1, 8.25), "max": (-9.45, 2, 9.65), "colour": ROSE, "palette": PALETTE_ROSE},   # left rose tower: layer 3
            {"min": (-10.45, 2, 8.55), "max": (-9.45, 3, 9.45), "colour": ROSE, "palette": PALETTE_ROSE},   # left rose tower: layer 4
            {"min": (-10.6, 3, 8.4), "max": (-9.3, 4, 9.7), "colour": ROSE, "palette": PALETTE_ROSE},   # left rose tower: layer 5
            {"min": (-10.8, 4, 8.4), "max": (-9.3, 5, 9.7), "colour": ROSE, "palette": PALETTE_ROSE},   # left rose tower: layer 6
            {"min": (-10.7, 5, 8.1), "max": (-9.1, 6, 9.9), "colour": ROSE, "palette": PALETTE_ROSE},   # left rose tower: layer 7
            {"min": (-11, 6, 8), "max": (-9, 7, 10), "colour": ROSE, "palette": PALETTE_ROSE},   # left rose tower: layer 8
            {"min": (9, -1, 8), "max": (11, 0, 10), "colour": ROSE, "palette": PALETTE_ROSE},   # right rose tower: layer 1
            {"min": (9.3, 0, 8.1), "max": (10.9, 1, 9.9), "colour": ROSE, "palette": PALETTE_ROSE},   # right rose tower: layer 2
            {"min": (9.2, 1, 8.4), "max": (10.7, 2, 9.7), "colour": ROSE, "palette": PALETTE_ROSE},   # right rose tower: layer 3
            {"min": (9.4, 2, 8.4), "max": (10.7, 3, 9.7), "colour": ROSE, "palette": PALETTE_ROSE},   # right rose tower: layer 4
            {"min": (9.55, 3, 8.55), "max": (10.55, 4, 9.45), "colour": ROSE, "palette": PALETTE_ROSE},   # right rose tower: layer 5
            {"min": (9.35, 4, 8.25), "max": (10.55, 5, 9.65), "colour": ROSE, "palette": PALETTE_ROSE},   # right rose tower: layer 6
            {"min": (9.35, 5, 8.35), "max": (10.75, 6, 9.85), "colour": ROSE, "palette": PALETTE_ROSE},   # right rose tower: layer 7
            {"min": (9, 6, 8.1), "max": (11, 7, 10), "colour": ROSE, "palette": PALETTE_ROSE},   # right rose tower: layer 8
            {"min": (-0.9, -1, 12.2), "max": (0.9, 0, 13.9), "colour": ROSE, "palette": PALETTE_ROSE},   # back rose tower: layer 1
            {"min": (-0.55, 0, 12.45), "max": (0.65, 1, 13.75), "colour": ROSE, "palette": PALETTE_ROSE},   # back rose tower: layer 2
            {"min": (-0.55, 1, 12.35), "max": (0.45, 2, 13.55), "colour": ROSE, "palette": PALETTE_ROSE},   # back rose tower: layer 3
            {"min": (-0.35, 2, 12.65), "max": (0.45, 3, 13.35), "colour": ROSE, "palette": PALETTE_ROSE},   # back rose tower: layer 4
            {"min": (-0.5, 3, 12.5), "max": (0.6, 4, 13.6), "colour": ROSE, "palette": PALETTE_ROSE},   # back rose tower: layer 5
            {"min": (-0.7, 4, 12.5), "max": (0.6, 5, 13.6), "colour": ROSE, "palette": PALETTE_ROSE},   # back rose tower: layer 6
            {"min": (-0.6, 5, 12.2), "max": (0.8, 6, 13.8), "colour": ROSE, "palette": PALETTE_ROSE},   # back rose tower: layer 7
            {"min": (-0.9, 6, 12.1), "max": (0.9, 7, 13.9), "colour": ROSE, "palette": PALETTE_ROSE},   # back rose tower: layer 8
            # STEPS: a stepped heap (3 x 3, then 1 x 1) on each side of the pink goo lake
            {"min": (-13, -1, -3), "max": (-12, 0, -2), "colour": CANDY, "palette": PALETTE_CANDY},   # left steps: step 1 (3 x 3)
            {"min": (-13, -1, -2), "max": (-12, 0, -1), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (-13, -1, -1), "max": (-12, 0, 0), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (-12, -1, -3), "max": (-11, 0, -2), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (-12, -1, -2), "max": (-11, 0, -1), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (-12, -1, -1), "max": (-11, 0, 0), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (-11, -1, -3), "max": (-10, 0, -2), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (-11, -1, -2), "max": (-10, 0, -1), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (-11, -1, -1), "max": (-10, 0, 0), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (-12, 0, -2), "max": (-11, 1, -1), "colour": CANDY, "palette": PALETTE_CANDY},   # left steps: step 2 (1 x 1)
            {"min": (10, -1, -4), "max": (11, 0, -3), "colour": CANDY, "palette": PALETTE_CANDY},   # right steps: step 1 (3 x 3)
            {"min": (10, -1, -3), "max": (11, 0, -2), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (10, -1, -2), "max": (11, 0, -1), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (11, -1, -4), "max": (12, 0, -3), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (11, -1, -3), "max": (12, 0, -2), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (11, -1, -2), "max": (12, 0, -1), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (12, -1, -4), "max": (13, 0, -3), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (12, -1, -3), "max": (13, 0, -2), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (12, -1, -2), "max": (13, 0, -1), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (11, 0, -3), "max": (12, 1, -2), "colour": CANDY, "palette": PALETTE_CANDY},   # right steps: step 2 (1 x 1)
            # PILES of candy blocks to hide behind
            {"min": (-6, -1, -4), "max": (-5, 0, -3), "colour": CANDY, "palette": PALETTE_CANDY},   # pile, left
            {"min": (-5, -1, -4), "max": (-4, 0, -3), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (-5, 0, -4), "max": (-4, 1, -3), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (4, -1, 7), "max": (5, 0, 8), "colour": CANDY, "palette": PALETTE_CANDY},   # pile, right
            {"min": (4, 0, 7), "max": (5, 1, 8), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (4, -1, 8), "max": (5, 0, 9), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (-4, -1, 7), "max": (-3, 0, 8), "colour": CANDY, "palette": PALETTE_CANDY},   # pile, middle
            {"min": (-3, -1, 7), "max": (-2, 0, 8), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (-3, -1, 8), "max": (-2, 0, 9), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (-3, 0, 8), "max": (-2, 1, 9), "colour": CANDY, "palette": PALETTE_CANDY},
            # RINGS round the floor bunkers: low (0.4 tall, under their guns), a GAP facing the back
            {"min": (-9, -1, 13.5), "max": (-8.5, -0.6, 14), "colour": CANDY, "palette": PALETTE_CANDY},   # left ring: corner
            {"min": (-5.5, -1, 13.5), "max": (-5, -0.6, 14), "colour": CANDY, "palette": PALETTE_CANDY},   # corner
            {"min": (-9, -1, 10), "max": (-8.5, -0.6, 10.5), "colour": CANDY, "palette": PALETTE_CANDY},   # corner
            {"min": (-5.5, -1, 10), "max": (-5, -0.6, 10.5), "colour": CANDY, "palette": PALETTE_CANDY},   # corner
            {"min": (-8.5, -1, 13.5), "max": (-7.5, -0.6, 14), "colour": CANDY, "palette": PALETTE_CANDY},   # far side
            {"min": (-7.5, -1, 13.5), "max": (-6.5, -0.6, 14), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (-6.5, -1, 13.5), "max": (-5.5, -0.6, 14), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (-9, -1, 10.5), "max": (-8.5, -0.6, 11.5), "colour": CANDY, "palette": PALETTE_CANDY},   # left side
            {"min": (-5.5, -1, 10.5), "max": (-5, -0.6, 11.5), "colour": CANDY, "palette": PALETTE_CANDY},   # right side
            {"min": (-9, -1, 11.5), "max": (-8.5, -0.6, 12.5), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (-5.5, -1, 11.5), "max": (-5, -0.6, 12.5), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (-9, -1, 12.5), "max": (-8.5, -0.6, 13.5), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (-5.5, -1, 12.5), "max": (-5, -0.6, 13.5), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (-8.5, -1, 10), "max": (-8, -0.6, 10.5), "colour": CANDY, "palette": PALETTE_CANDY},   # near side, left part ...
            {"min": (-6, -1, 10), "max": (-5.5, -0.6, 10.5), "colour": CANDY, "palette": PALETTE_CANDY},   # ... and right part: the GAP is between them
            {"min": (4, -1, 13.5), "max": (4.5, -0.6, 14), "colour": CANDY, "palette": PALETTE_CANDY},   # right ring: corner
            {"min": (7.5, -1, 13.5), "max": (8, -0.6, 14), "colour": CANDY, "palette": PALETTE_CANDY},   # corner
            {"min": (4, -1, 10), "max": (4.5, -0.6, 10.5), "colour": CANDY, "palette": PALETTE_CANDY},   # corner
            {"min": (7.5, -1, 10), "max": (8, -0.6, 10.5), "colour": CANDY, "palette": PALETTE_CANDY},   # corner
            {"min": (4.5, -1, 13.5), "max": (5.5, -0.6, 14), "colour": CANDY, "palette": PALETTE_CANDY},   # far side
            {"min": (5.5, -1, 13.5), "max": (6.5, -0.6, 14), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (6.5, -1, 13.5), "max": (7.5, -0.6, 14), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (4, -1, 10.5), "max": (4.5, -0.6, 11.5), "colour": CANDY, "palette": PALETTE_CANDY},   # left side
            {"min": (7.5, -1, 10.5), "max": (8, -0.6, 11.5), "colour": CANDY, "palette": PALETTE_CANDY},   # right side
            {"min": (4, -1, 11.5), "max": (4.5, -0.6, 12.5), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (7.5, -1, 11.5), "max": (8, -0.6, 12.5), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (4, -1, 12.5), "max": (4.5, -0.6, 13.5), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (7.5, -1, 12.5), "max": (8, -0.6, 13.5), "colour": CANDY, "palette": PALETTE_CANDY},
            {"min": (4.5, -1, 10), "max": (5, -0.6, 10.5), "colour": CANDY, "palette": PALETTE_CANDY},   # near side, left part ...
            {"min": (7, -1, 10), "max": (7.5, -0.6, 10.5), "colour": CANDY, "palette": PALETTE_CANDY},   # ... and right part: the GAP is between them
        ],
        "spawn": [
            {"design": "tank", "name": "cupid tank",
             "position": [-12, -0.4, 2.5], "velocity": [0.015, 0, 0],
             "size": 0.6, "angles": [-90, 0, 0], "colour": CANDY, "palette": PALETTE_CANDY,
             "gun": {"mode": "TRACK", "turret_spin": 0.8, "start_angle": "you", "volley": 3, "cooldown": 150},
             "radar_spin": -6},
            {"design": "tank", "name": "sweetheart tank",
             "position": [2.5, 0, 12], "velocity": [0, 0, -0.012],
             "size": 1, "angles": [180, 0, 0], "colour": CANDY, "palette": PALETTE_CANDY,
             "gun": {"mode": "TRACK", "turret_spin": 0.8, "start_angle": "you", "volley": 3, "cooldown": 150},
             "radar_spin": -6},
            {"design": "bunker", "name": "left cupid bunker", "position": [-7, -0.7, 12], "size": 0.6, "colour": CANDY, "palette": PALETTE_CANDY,
             "gun": {"mode": "SPIN", "turret_spin": 1.0, "start_angle": 30, "volley": 3}},
            {"design": "bunker", "name": "right cupid bunker", "position": [6, -0.7, 12], "size": 0.6, "colour": CANDY, "palette": PALETTE_CANDY,
             "gun": {"mode": "SPIN", "turret_spin": -1.0, "start_angle": 150, "volley": 3}},
            {"design": "bunker", "name": "left wall cupid bunker", "position": [-15.7, 3, -6], "size": 0.6,
             "angles": [0, 0, -90], "colour": CANDY, "palette": PALETTE_BLACK,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 3, "bullet_colour": (255, 150, 200), "bullet_palette": PALETTE_CANDY},
             "children": [{"model": cupola_model}]},
            {"design": "bunker", "name": "right wall cupid bunker", "position": [15.7, 3, 4], "size": 0.6,
             "angles": [0, 0, 90], "colour": CANDY, "palette": PALETTE_BLACK,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 3, "bullet_colour": (255, 150, 200), "bullet_palette": PALETTE_CANDY},
             "children": [{"model": cupola_model}]},
            {"design": "bunker", "name": "far wall cupid bunker", "position": [-3, 3, 15.7], "size": 0.6,
             "angles": [0, -90, 0], "colour": CANDY, "palette": PALETTE_BLACK,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 3, "bullet_colour": (255, 150, 200), "bullet_palette": PALETTE_CANDY},
             "children": [{"model": cupola_model}]},
            {"design": "bunker", "name": "ceiling cupid bunker", "position": [3, 6.7, -2], "size": 0.6,
             "angles": [0, 180, 0], "colour": CANDY, "palette": PALETTE_BLACK,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 3, "bullet_colour": (255, 150, 200), "bullet_palette": PALETTE_CANDY},
             "children": [{"model": cupola_model}]},
            {"design": "cube", "name": "heart cube 1", "position": [-5, 2.5, 3], "velocity": [0.022, 0.015, -0.012],
             "size": "MEDIUM", "angles": [20, 30, 0], "speeds": (0.9, 0.6, 0.2), "colour": ROSE, "palette": PALETTE_ROSE,
             "gun": {"mode": "TARGET", "volley": 1, "cooldown": 110}},
            {"design": "cube", "name": "heart cube 2", "position": [5, 3.5, 6], "velocity": [-0.02, -0.012, 0.016],
             "size": "MEDIUM", "angles": [20, 30, 0], "speeds": (0.9, 0.6, 0.2), "colour": ROSE, "palette": PALETTE_ROSE,
             "gun": {"mode": "TARGET", "volley": 1, "cooldown": 110}},
            {"design": "frame", "name": "cupid frame", "position": [0, 4, 9], "velocity": [0.018, 0.01, -0.02],
             "size": "MEDIUM", "angles": [20, 30, 0], "speeds": (0.9, 0.6, 0.2), "colour": CANDY, "palette": PALETTE_CANDY,
             "gun": {"mode": "TARGET", "volley": 1, "cooldown": 120}},
            {"design": "diamond", "name": "cupid diamond", "position": [-8, 4.5, -2], "velocity": [0.02, 0, 0.022],
             "size": "MEDIUM", "angles": [20, 30, 0], "speeds": (0.9, 0.6, 0.2), "colour": CANDY, "palette": PALETTE_CANDY,
             "gun": {"mode": "DOWN", "volley": 1}},
            {"design": "cube", "name": "giant heart", "position": [8, 3, 2], "velocity": [-0.015, 0.012, 0.02],
             "size": "LARGE", "angles": [20, 30, 0], "speeds": (0.9, 0.6, 0.2), "colour": ROSE, "palette": PALETTE_ROSE},
            {"design": "pyramid", "name": "cupid dripper 1",
             "position": [-5, 6.5, 2], "velocity": [0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0), "colour": CANDY, "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 55, "bullet_colour": (255, 150, 200), "bullet_palette": PALETTE_CANDY},
             "scenery": True},
            {"design": "pyramid", "name": "cupid dripper 2",
             "position": [6, 6.5, 3], "velocity": [-0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0), "colour": CANDY, "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 55, "bullet_colour": (255, 150, 200), "bullet_palette": PALETTE_CANDY},
             "scenery": True},
            {"design": "pyramid", "name": "cupid dripper 3",
             "position": [-1, 6.5, -6], "velocity": [0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0), "colour": CANDY, "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 55, "bullet_colour": (255, 150, 200), "bullet_palette": PALETTE_CANDY},
             "scenery": True},
            {"design": "pyramid", "name": "cupid dripper 4",
             "position": [5, 6.5, 9], "velocity": [-0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0), "colour": CANDY, "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 55, "bullet_colour": (255, 150, 200), "bullet_palette": PALETTE_CANDY},
             "scenery": True},
        ],
    },

    13: {    # ---- LEVEL 13: FORT KNOX - the Canyon's size, a gold VAULT: one door, bunkers inside, gold-bar stacks, tanks on guard ----
        "name": "Fort Knox",
        "intro": "Break into the vault. One door, guards inside - and good luck spotting the gems.",
        "world": {"min": (-16, -1, -16), "max": (16, 7, 16)},       # 32 wide (x), 32 long (z), 8 tall: the Canyon's size
        "start": {"x": 0, "y": 0, "z": -14, "turn": 0, "tip": 0},    # near the back wall, facing the far wall
        "grid_colour": (130, 100, 30),                             # a GOLD grid

        "floor_shapes": [
            # GOLD DUST on the vault floor (a slow "custard" floor in gold): walk in, and you're a slow target
            {"type": "custard", "min": (-4.6, 2), "max": (4.6, 8.6), "colour": (235, 190, 60)},
            # GOLD DUST spilled outside the door
            {"type": "custard", "min": (-2, -3), "max": (2, -1), "colour": (235, 190, 60)}
        ],
        "boxes": [
            # FORT KNOX, built from GOLD BARS (BULLION) and BRONZE. The VAULT is x -5 to 5, z -1 to 9, its door facing you.
            # YOUR COVER: a low U of gold bars round where you start (x 0, z -14), open behind you
            {"min": (-1.9, -1, -12.6), "max": (-1.5, -0.6, -12.2), "colour": BULLION, "palette": PALETTE_BULLION},   # front left corner
            {"min": (1.5, -1, -12.6), "max": (1.9, -0.6, -12.2), "colour": BULLION, "palette": PALETTE_BULLION},   # front right corner
            {"min": (-1.5, -1, -12.6), "max": (-0.5, -0.6, -12.2), "colour": BULLION, "palette": PALETTE_BULLION},   # front
            {"min": (-0.5, -1, -12.6), "max": (0.5, -0.6, -12.2), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (0.5, -1, -12.6), "max": (1.5, -0.6, -12.2), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (-1.9, -1, -13.6), "max": (-1.5, -0.6, -12.6), "colour": BULLION, "palette": PALETTE_BULLION},   # left side
            {"min": (1.5, -1, -13.6), "max": (1.9, -0.6, -12.6), "colour": BULLION, "palette": PALETTE_BULLION},   # right side
            {"min": (-1.9, -1, -14.4), "max": (-1.5, -0.6, -13.6), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (1.5, -1, -14.4), "max": (1.9, -0.6, -13.6), "colour": BULLION, "palette": PALETTE_BULLION},
            # THE VAULT: walls 0.4 thick, tops at y 1.2 (over your eye: they hide you), a DOOR in the front (x -1 to 1), an eye-height
            # SLIT in each side wall (z 4 to 5) to peek and shoot through
            {"min": (-5, -1, -1), "max": (-4, 1.2, -0.6), "colour": BULLION, "palette": PALETTE_BULLION},   # vault front wall (the DOOR: x -1 to 1)
            {"min": (-4, -1, -1), "max": (-3, 1.2, -0.6), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (-3, -1, -1), "max": (-2, 1.2, -0.6), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (-2, -1, -1), "max": (-1, 1.2, -0.6), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (1, -1, -1), "max": (2, 1.2, -0.6), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (2, -1, -1), "max": (3, 1.2, -0.6), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (3, -1, -1), "max": (4, 1.2, -0.6), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (4, -1, -1), "max": (5, 1.2, -0.6), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (-5, -1, 8.6), "max": (-4, 1.2, 9), "colour": BULLION, "palette": PALETTE_BULLION},   # vault back wall
            {"min": (-4, -1, 8.6), "max": (-3, 1.2, 9), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (-3, -1, 8.6), "max": (-2, 1.2, 9), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (-2, -1, 8.6), "max": (-1, 1.2, 9), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (-1, -1, 8.6), "max": (0, 1.2, 9), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (0, -1, 8.6), "max": (1, 1.2, 9), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (1, -1, 8.6), "max": (2, 1.2, 9), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (2, -1, 8.6), "max": (3, 1.2, 9), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (3, -1, 8.6), "max": (4, 1.2, 9), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (4, -1, 8.6), "max": (5, 1.2, 9), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (-5, -1, -1), "max": (-4.6, 1.2, 0), "colour": BULLION, "palette": PALETTE_BULLION},   # vault left wall
            {"min": (-5, -1, 0), "max": (-4.6, 1.2, 1), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (-5, -1, 1), "max": (-4.6, 1.2, 2), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (-5, -1, 2), "max": (-4.6, 1.2, 3), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (-5, -1, 3), "max": (-4.6, 1.2, 4), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (-5, -1, 4), "max": (-4.6, -0.3, 5), "colour": BULLION, "palette": PALETTE_BULLION},   # vault left wall: under the SLIT
            {"min": (-5, 0.4, 4), "max": (-4.6, 1.2, 5), "colour": BULLION, "palette": PALETTE_BULLION},   # vault left wall: over the slit (y -0.3 to 0.4)
            {"min": (-5, -1, 5), "max": (-4.6, 1.2, 6), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (-5, -1, 6), "max": (-4.6, 1.2, 7), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (-5, -1, 7), "max": (-4.6, 1.2, 8), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (-5, -1, 8), "max": (-4.6, 1.2, 9), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (4.6, -1, -1), "max": (5, 1.2, 0), "colour": BULLION, "palette": PALETTE_BULLION},   # vault right wall
            {"min": (4.6, -1, 0), "max": (5, 1.2, 1), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (4.6, -1, 1), "max": (5, 1.2, 2), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (4.6, -1, 2), "max": (5, 1.2, 3), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (4.6, -1, 3), "max": (5, 1.2, 4), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (4.6, -1, 4), "max": (5, -0.3, 5), "colour": BULLION, "palette": PALETTE_BULLION},   # vault right wall: under the SLIT
            {"min": (4.6, 0.4, 4), "max": (5, 1.2, 5), "colour": BULLION, "palette": PALETTE_BULLION},   # vault right wall: over the slit (y -0.3 to 0.4)
            {"min": (4.6, -1, 5), "max": (5, 1.2, 6), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (4.6, -1, 6), "max": (5, 1.2, 7), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (4.6, -1, 7), "max": (5, 1.2, 8), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (4.6, -1, 8), "max": (5, 1.2, 9), "colour": BULLION, "palette": PALETTE_BULLION},
            # GOLD-BAR STACKS: rows of 1 x 1 stacks (1 or 2 high) down both sides, like a warehouse - cover
            {"min": (-11, -1, -7), "max": (-10, 0, -6), "colour": BULLION, "palette": PALETTE_BULLION},   # bar stack, left
            {"min": (-11, 0, -7), "max": (-10, 1, -6), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (-11, -1, -6), "max": (-10, 0, -5), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (-11, -1, -3), "max": (-10, 0, -2), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (-11, -1, -2), "max": (-10, 0, -1), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (-11, -1, 1), "max": (-10, 0, 2), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (-11, 0, 1), "max": (-10, 1, 2), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (-11, -1, 2), "max": (-10, 0, 3), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (-11, -1, 5), "max": (-10, 0, 6), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (-11, -1, 6), "max": (-10, 0, 7), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (-11, -1, 9), "max": (-10, 0, 10), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (-11, 0, 9), "max": (-10, 1, 10), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (-11, -1, 10), "max": (-10, 0, 11), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (10, -1, -7), "max": (11, 0, -6), "colour": BULLION, "palette": PALETTE_BULLION},   # bar stack, right
            {"min": (10, 0, -7), "max": (11, 1, -6), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (10, -1, -6), "max": (11, 0, -5), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (10, -1, -3), "max": (11, 0, -2), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (10, -1, -2), "max": (11, 0, -1), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (10, -1, 1), "max": (11, 0, 2), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (10, 0, 1), "max": (11, 1, 2), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (10, -1, 2), "max": (11, 0, 3), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (10, -1, 5), "max": (11, 0, 6), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (10, -1, 6), "max": (11, 0, 7), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (10, -1, 9), "max": (11, 0, 10), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (10, 0, 9), "max": (11, 1, 10), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (10, -1, 10), "max": (11, 0, 11), "colour": BULLION, "palette": PALETTE_BULLION},
            # BRONZE PILLARS: two floor-to-CEILING columns at the back corners (8 layers, each 1 tall)
            {"min": (-14, -1, 12.1), "max": (-12, 0, 14), "colour": BRONZE, "palette": PALETTE_BRONZE},   # left pillar: layer 1
            {"min": (-13.65, 0, 12.35), "max": (-12.25, 1, 13.85), "colour": BRONZE, "palette": PALETTE_BRONZE},   # left pillar: layer 2
            {"min": (-13.65, 1, 12.25), "max": (-12.45, 2, 13.65), "colour": BRONZE, "palette": PALETTE_BRONZE},   # left pillar: layer 3
            {"min": (-13.45, 2, 12.55), "max": (-12.45, 3, 13.45), "colour": BRONZE, "palette": PALETTE_BRONZE},   # left pillar: layer 4
            {"min": (-13.6, 3, 12.4), "max": (-12.3, 4, 13.7), "colour": BRONZE, "palette": PALETTE_BRONZE},   # left pillar: layer 5
            {"min": (-13.8, 4, 12.4), "max": (-12.3, 5, 13.7), "colour": BRONZE, "palette": PALETTE_BRONZE},   # left pillar: layer 6
            {"min": (-13.7, 5, 12.1), "max": (-12.1, 6, 13.9), "colour": BRONZE, "palette": PALETTE_BRONZE},   # left pillar: layer 7
            {"min": (-14, 6, 12), "max": (-12, 7, 14), "colour": BRONZE, "palette": PALETTE_BRONZE},   # left pillar: layer 8
            {"min": (12, -1, 12), "max": (14, 0, 14), "colour": BRONZE, "palette": PALETTE_BRONZE},   # right pillar: layer 1
            {"min": (12.3, 0, 12.1), "max": (13.9, 1, 13.9), "colour": BRONZE, "palette": PALETTE_BRONZE},   # right pillar: layer 2
            {"min": (12.2, 1, 12.4), "max": (13.7, 2, 13.7), "colour": BRONZE, "palette": PALETTE_BRONZE},   # right pillar: layer 3
            {"min": (12.4, 2, 12.4), "max": (13.7, 3, 13.7), "colour": BRONZE, "palette": PALETTE_BRONZE},   # right pillar: layer 4
            {"min": (12.55, 3, 12.55), "max": (13.55, 4, 13.45), "colour": BRONZE, "palette": PALETTE_BRONZE},   # right pillar: layer 5
            {"min": (12.35, 4, 12.25), "max": (13.55, 5, 13.65), "colour": BRONZE, "palette": PALETTE_BRONZE},   # right pillar: layer 6
            {"min": (12.35, 5, 12.35), "max": (13.75, 6, 13.85), "colour": BRONZE, "palette": PALETTE_BRONZE},   # right pillar: layer 7
            {"min": (12, 6, 12.1), "max": (14, 7, 14), "colour": BRONZE, "palette": PALETTE_BRONZE},   # right pillar: layer 8
            # SANDBAG-STYLE BAR WALLS in front of the vault: low cover on the way in
            {"min": (-4, -1, -5.4), "max": (-3, -0.4, -5), "colour": BULLION, "palette": PALETTE_BULLION},   # low bar wall
            {"min": (-3, -1, -5.4), "max": (-2, -0.5, -5), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (2, -1, -5.4), "max": (3, -0.5, -5), "colour": BULLION, "palette": PALETTE_BULLION},
            {"min": (3, -1, -5.4), "max": (4, -0.4, -5), "colour": BULLION, "palette": PALETTE_BULLION},
        ],
        "spawn": [
            {"design": "tank", "name": "guard tank",
             "position": [-12, -0.4, -8.5], "velocity": [0.015, 0, 0],
             "size": 0.6, "angles": [-90, 0, 0], "colour": BULLION, "palette": PALETTE_BULLION,
             "gun": {"mode": "TRACK", "turret_spin": 0.8, "start_angle": "you", "volley": 3, "cooldown": 150},
             "radar_spin": -6},
            {"design": "tank", "name": "bullion tank",
             "position": [7, 0, 11.5], "velocity": [-0.012, 0, 0],
             "size": 1, "angles": [90, 0, 0], "colour": BULLION, "palette": PALETTE_BULLION,
             "gun": {"mode": "TRACK", "turret_spin": 0.8, "start_angle": "you", "volley": 3, "cooldown": 150},
             "radar_spin": -6},
            {"design": "bunker", "name": "vault bunker left", "position": [-2.5, -0.7, 6], "size": 0.6, "colour": BULLION, "palette": PALETTE_BULLION,
             "gun": {"mode": "SPIN", "turret_spin": 1.0, "start_angle": 0, "volley": 3}},
            {"design": "bunker", "name": "vault bunker right", "position": [2.5, -0.7, 6], "size": 0.6, "colour": BULLION, "palette": PALETTE_BULLION,
             "gun": {"mode": "SPIN", "turret_spin": -1.0, "start_angle": 180, "volley": 3}},
            {"design": "bunker", "name": "left wall vault bunker", "position": [-15.7, 3, 3], "size": 0.6,
             "angles": [0, 0, -90], "colour": BULLION, "palette": PALETTE_BLACK,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 3, "bullet_colour": (255, 215, 60), "bullet_palette": PALETTE_BULLION},
             "children": [{"model": cupola_model}]},
            {"design": "bunker", "name": "right wall vault bunker", "position": [15.7, 3, -5], "size": 0.6,
             "angles": [0, 0, 90], "colour": BULLION, "palette": PALETTE_BLACK,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 3, "bullet_colour": (255, 215, 60), "bullet_palette": PALETTE_BULLION},
             "children": [{"model": cupola_model}]},
            {"design": "bunker", "name": "far wall vault bunker", "position": [0, 3, 15.7], "size": 0.6,
             "angles": [0, -90, 0], "colour": BULLION, "palette": PALETTE_BLACK,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 3, "bullet_colour": (255, 215, 60), "bullet_palette": PALETTE_BULLION},
             "children": [{"model": cupola_model}]},
            {"design": "bunker", "name": "vault ceiling bunker", "position": [0, 6.7, 4], "size": 0.6,
             "angles": [0, 180, 0], "colour": BULLION, "palette": PALETTE_BLACK,
             "gun": {"mode": "TRACK", "turret_spin": 1, "volley": 3, "bullet_colour": (255, 215, 60), "bullet_palette": PALETTE_BULLION},
             "children": [{"model": cupola_model}]},
            {"design": "cube", "name": "bronze cube 1", "position": [-7, 3, 2], "velocity": [0.02, 0.012, -0.015],
             "size": "MEDIUM", "angles": [20, 30, 0], "speeds": (0.9, 0.6, 0.2), "colour": BRONZE, "palette": PALETTE_BRONZE,
             "gun": {"mode": "TARGET", "volley": 1, "cooldown": 110}},
            {"design": "cube", "name": "bronze cube 2", "position": [7, 3.5, 8], "velocity": [-0.018, -0.01, 0.016],
             "size": "MEDIUM", "angles": [20, 30, 0], "speeds": (0.9, 0.6, 0.2), "colour": BRONZE, "palette": PALETTE_BRONZE,
             "gun": {"mode": "TARGET", "volley": 1, "cooldown": 110}},
            {"design": "frame", "name": "gold frame", "position": [0, 4.5, -4], "velocity": [0.02, 0.01, 0.018],
             "size": "MEDIUM", "angles": [20, 30, 0], "speeds": (0.9, 0.6, 0.2), "colour": BULLION, "palette": PALETTE_BULLION,
             "gun": {"mode": "TARGET", "volley": 1, "cooldown": 120}},
            {"design": "diamond", "name": "gold diamond", "position": [-8, 4.5, 10], "velocity": [0.02, 0, -0.02],
             "size": "MEDIUM", "angles": [20, 30, 0], "speeds": (0.9, 0.6, 0.2), "colour": BULLION, "palette": PALETTE_BULLION,
             "gun": {"mode": "DOWN", "volley": 1}},
            {"design": "pyramid", "name": "gold dripper 1",
             "position": [-8, 6.5, -1], "velocity": [0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0), "colour": BULLION, "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 55, "bullet_colour": (255, 215, 60), "bullet_palette": PALETTE_BULLION},
             "scenery": True},
            {"design": "pyramid", "name": "gold dripper 2",
             "position": [8, 6.5, 3], "velocity": [-0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0), "colour": BULLION, "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 55, "bullet_colour": (255, 215, 60), "bullet_palette": PALETTE_BULLION},
             "scenery": True},
            {"design": "pyramid", "name": "gold dripper 3",
             "position": [-6, 6.5, 11], "velocity": [0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0), "colour": BULLION, "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 55, "bullet_colour": (255, 215, 60), "bullet_palette": PALETTE_BULLION},
             "scenery": True},
            {"design": "pyramid", "name": "gold dripper 4",
             "position": [7, 6.5, -8], "velocity": [-0.02, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0), "colour": BULLION, "palette": PALETTE_BLACK,
             "gun": {"mode": "DOWN", "volley": 3, "cooldown": 55, "bullet_colour": (255, 215, 60), "bullet_palette": PALETTE_BULLION},
             "scenery": True},
        ],
    },

    14: {    # ---- LEVEL 14: THE HUGE ROOM - an EMPTY room three times as wide and long (48 x 48) ----
        "name": "The Huge Room",
        "intro": "Just even more space - and one small cube to find and kill.",
        "world": {"min": (-24, -1, -24), "max": (24, 7, 24)},       # 48 wide (x), 48 long (z), 8 tall
        "start": {"x": 0, "y": 0, "z": -22, "turn": 0, "tip": 0},    # near the back wall, facing the far wall

        "floor_shapes": [],
        "boxes": [],
        "spawn": [
            # ONE small cube to kill, so the level can be cleared and you go on to 99. Parked, spinning, in front of you.
            {"design": "cube", "name": "lonely cube",
             "position": [0, 0.5, -12], "size": "SMALL", "angles": [30, 20, 0], "speeds": (1, 0, 0),
             "colour": (120, 190, 240), "palette": PALETTE_ICE},

            # a COLUMN of three tanks - big, medium, small - rolling across the far end of the huge room, in line
            {"design": "twin tank", "name": "lead tank",
             "position": [-6, 0.5, 18], "velocity": [0.012, 0, 0],
             "size": 1.5, "angles": [-90, 0, 0],
             "colour": (120, 190, 80), "palette": PALETTE_FOREST,
             "gun": {"mode": "TRACK", "turret_spin": 0.6, "start_angle": "you", "volley": 6, "cooldown": 180},
             "radar_spin": -6},
            {"design": "tank", "name": "middle tank",
             "position": [-11, 0, 18], "velocity": [0.012, 0, 0],
             "size": 1, "angles": [-90, 0, 0],
             "colour": (120, 190, 80), "palette": PALETTE_FOREST,
             "gun": {"mode": "TRACK", "turret_spin": 0.8, "start_angle": "you", "volley": 3, "cooldown": 150},
             "radar_spin": 6},
            {"design": "tank", "name": "tail tank",
             "position": [-15, -0.4, 18], "velocity": [0.012, 0, 0],
             "size": 0.6, "angles": [-90, 0, 0],
             "colour": (120, 190, 80), "palette": PALETTE_FOREST,
             "gun": {"mode": "TRACK", "turret_spin": 1, "start_angle": "you", "volley": 3, "cooldown": 150},
             "radar_spin": -6},
        ],
    },

    99: {   # ---- LEVEL 99: SKUNK WORKS - the test level: the world as built so far ----
        "name": "Skunk works",
        "intro": "Everything built so far, all at once - and ALL of it is trying to kill you.",
        "world": {"min": (-24, -1, -24), "max": (24, 8, 24)},       # 48 wide (x), 48 long (z), 9 high
        "start": {"x": -7.8, "y": 0, "z": -3.2, "turn": -30, "tip": -1},   # just outside the near-left corner

        "floor_shapes": [
            # white arrow: the way the light TRAVELS, in the lower-right corner of the floor.
            # Hard-coded for LIGHT = (0.48, 0.6, -0.64): from its tail at (7.5, -2.5) to its tip at (6.3, -0.9).
            ([(7.436, -2.548), (6.596, -1.428), (6.42, -1.56),        # shaft one side, out to the head
              (6.3, -0.9),                                            # the tip
              (6.9, -1.2), (6.724, -1.332), (7.564, -2.452)],         # head other side, back down the shaft
             (255, 255, 255)),
        ],

        "boxes": [
            # three gold pillars in a row, 1 wide, 3 tall (y -1 to 2), 0.25 thick, with a 1 unit gap between them
            {"min": (-0.5, -1, -0.125), "max": (0.5, 2, 0.125),     # middle: on the gold square
             "colour": (255, 215, 0), "palette": PALETTE_GOLD},
            {"min": (1.5, -1, -0.125),  "max": (2.5, 2, 0.125),     # to the RIGHT
             "colour": (255, 215, 0), "palette": PALETTE_GOLD},
            {"min": (-2.5, -1, -0.125), "max": (-1.5, 2, 0.125),    # to the LEFT
             "colour": (255, 215, 0), "palette": PALETTE_GOLD},
        ],

        "spawn": [
            # ---- CUBES ----
            {"design": "cube", "name": "big cube",
             "position": [-2, 0, 9], "velocity": [0.02, 0.01, -0.015],
             "size": "LARGE", "angles": [35, 0, 0], "speeds": (0, 1, 2),
             "colour": (120, 190, 240), "palette": PALETTE_ICE,
             "gun": {"mode": "TARGET", "volley": 1}},          # shoots AT YOU

            {"design": "cube", "name": "small cube",
             "position": [3, -0.8, 5], "velocity": [-0.03, 0.02, 0.025],
             "size": "TINY", "angles": [-50, 0, 0], "speeds": (2, 0, 0),
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET,
             "gun": {"mode": "TARGET", "volley": 1}},          # shoots AT YOU

            {"design": "cube", "name": "floor mini",
             "position": [-3, -0.7, 4], "velocity": [0.025, 0.03, 0.02],
             "size": "TINY", "angles": [20, 0, 0], "speeds": (1, 0, 0),
             "colour": (120, 190, 240), "palette": PALETTE_ICE,
             "gun": {"mode": "TARGET", "volley": 1}},          # shoots AT YOU

            {"design": "cube", "name": "hover mini",
             "position": [0, 0.6, 6], "velocity": [-0.02, -0.015, 0.03],
             "size": "TINY", "angles": [10, 30, 0], "speeds": (1.5, 1, 0.5),
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET,
             "gun": {"mode": "TARGET", "volley": 1}},          # shoots AT YOU

            {"design": "cube", "name": "high mini",
             "position": [5, 2.5, 10], "velocity": [-0.035, -0.02, -0.01],
             "size": "SMALL", "angles": [45, 20, 10], "speeds": (0.5, 2, 1),
             "colour": (120, 190, 240), "palette": PALETTE_ICE,
             "gun": {"mode": "TARGET", "volley": 1}},          # shoots AT YOU

            {"design": "cube", "name": "mid mini",
             "position": [-5, 1.2, 11], "velocity": [0.015, 0.025, -0.03],
             "size": "TINY", "angles": [0, 45, 45], "speeds": (3, 0, 1),
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET,
             "gun": {"mode": "TARGET", "volley": 1}},          # shoots AT YOU

            {"design": "cube", "name": "gold mini",             # (named "gold", but it's an ice-blue cube)
             "position": [1.5, 1, 3.5], "velocity": [0.04, 0.035, 0.03],
             "size": "TINY", "angles": [30, 0, 0], "speeds": (1, 1, 1),
             "colour": (120, 190, 240), "palette": PALETTE_ICE,
             "gun": {"mode": "TARGET", "volley": 1}},          # shoots AT YOU

            # ---- PYRAMIDS ----
            {"design": "pyramid", "name": "big pyramid",
             "position": [4, 1, 8], "velocity": [-0.015, 0.005, 0.01],
             "size": "LARGE", "angles": [15, 0, 0], "speeds": (0.7, 0, 0),
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET,
             "gun": {"mode": "TARGET", "volley": 1}},          # shoots AT YOU

            {"design": "pyramid", "name": "tumble pyramid",
             "position": [-3, 2.5, 7], "velocity": [0.03, -0.02, 0.02],
             "size": "SMALL", "angles": [0, 60, 20], "speeds": (1, 2.5, 0.5),
             "colour": (120, 190, 240), "palette": PALETTE_ICE,
             "gun": {"mode": "TARGET", "volley": 1}},          # shoots AT YOU

            # ---- DIAMONDS ----
            {"design": "diamond", "name": "sunset diamond",
             "position": [-1, 1.5, 6], "velocity": [0.02, 0.03, -0.02],
             "size": "SMALL", "angles": [0, 0, 0], "speeds": (2, 0, 0),
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET,
             "gun": {"mode": "TARGET", "volley": 1}},          # shoots AT YOU

            {"design": "diamond", "name": "ice diamond",
             "position": [2, 2, 10], "velocity": [-0.025, -0.015, -0.03],
             "size": "MEDIUM", "angles": [45, 30, 0], "speeds": (1.5, 0.8, 1.2),
             "colour": (120, 190, 240), "palette": PALETTE_ICE,
             "gun": {"mode": "TARGET", "volley": 1}},          # shoots AT YOU

            {"design": "diamond", "name": "spark diamond",
             "position": [5, 0.5, 4], "velocity": [-0.04, 0.025, 0.035],
             "size": "TINY", "angles": [10, 20, 30], "speeds": (4, 3, 2),
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET,
             "gun": {"mode": "TARGET", "volley": 1}},          # shoots AT YOU

            # ---- FRAMES ----
            {"design": "frame", "name": "big frame",
             "position": [0, 1, 8], "velocity": [0.05, 0.015, -0.008],
             "size": "LARGE", "angles": [20, 0, 0], "speeds": (0.5, 0, 0),
             "colour": (120, 190, 240), "palette": PALETTE_ICE,
             "gun": {"mode": "TARGET", "volley": 1}},          # shoots AT YOU

            {"design": "frame", "name": "tumble frame",
             "position": [-4, 2, 6], "velocity": [0.025, -0.02, 0.015],
             "size": "MEDIUM", "angles": [0, 30, 15], "speeds": (1, 1.5, 0.7),
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET,
             "gun": {"mode": "TARGET", "volley": 1}},          # shoots AT YOU

            # ---- TANKS: they sit on the floor (centre y = FLOOR_Y + size), turned round to face you (-z) ----
            {"design": "twin tank", "name": "tank",             # the BIG tank, parked
             "position": [0, 0.5, 16], "size": 1.5, "angles": [180, 0, 0],
             "colour": (120, 190, 80), "palette": PALETTE_FOREST,
             "gun": {"mode": "TRACK", "turret_spin": 1, "start_angle": "you", "volley": 6},   # TWO barrels, TRACKS you
             "radar_spin": -6},

            {"design": "tank", "name": "tank left",             # parked
             "position": [-3.5, 0, 16], "size": 1, "angles": [180, 0, 0],
             "colour": (120, 190, 80), "palette": PALETTE_FOREST,
             "gun": {"mode": "TRACK", "turret_spin": 1, "start_angle": "you"},   # TRACKS you
             "radar_spin": 6},

            {"design": "tank", "name": "small tank",            # drives at an angle: speed 0.01 (a 3-4-5 triangle)
             "position": [3.5, -0.4, 16], "velocity": [-0.006, 0, -0.008],
             "size": 0.6, "angles": [180, 0, 0],
             "colour": (120, 190, 80), "palette": PALETTE_FOREST,
             "gun": {"mode": "TRACK", "turret_spin": 1.5, "start_angle": "you"},   # TRACKS you, fast
             "radar_spin": -6},
        ],
    },
}
