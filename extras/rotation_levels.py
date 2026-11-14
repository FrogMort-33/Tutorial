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
#   "start"        - where YOU begin: x, y (eye height: STAND_Y when standing), z, turn and tip (see camera)
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

        "sizes": {"SMALL": {"splits_to": None}},        # in this level: LARGE -> 2 MEDIUMs -> 4 SMALLs, which DIE

        "spawn": [
            # one LARGE ice-blue cube near the far ("top" on the map) wall, floating half a unit off the floor.
            # It spins on the spot but never moves (no velocity).
            # Tilted, its corners stick out further than when it's flat (LARGE = cube size 1.25, tilt 20 degrees,
            # spinning): up to 1.78 below its centre and 2.09 behind it, instead of 1.25. So its centre is at y 1.28
            # (lowest corner 0.5 above the floor at -1) and z 5.86 (furthest corner just inside the far wall at z = 8).
            {"design": "cube", "name": "training cube",
             "position": [0, 1.28, 5.86],
             "size": "LARGE",                       # 2.5 across, 4 health (see SIZES)
             "angles": [30, 20, 0],                 # turned 30 degrees (two sides show) and TILTED 20 degrees
             "speeds": (0.5, 0, 0),                 # spins slowly round its upright axis only, so its tilt stays
                                                    #   the same (one full turn every 12 seconds at 60 FPS)
             "colour": (120, 190, 240), "palette": PALETTE_ICE},
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

        "sizes": {"SMALL": {"splits_to": None}},        # as level 1: LARGE -> 2 MEDIUMs -> 4 SMALLs, which DIE

        "spawn": [
            # two LARGE cubes along the far wall, floating like level 1's (same height and distance from the wall),
            # 7 units apart so their tilted corners never touch, spinning opposite ways
            {"design": "cube", "name": "left cube",
             "position": [-3.5, 1.78, 5.86], "size": "LARGE",
             "angles": [30, 20, 0], "speeds": (0.5, 0, 0),
             "colour": (120, 190, 240), "palette": PALETTE_ICE,
             "gun": {"mode": "DOWN", "volley": 1}},     # drops ONE bullet straight down each time it fires
            {"design": "cube", "name": "right cube",              # the FIRE cube
             "position": [3.5, 1.78, 5.86], "size": "LARGE",
             "angles": [-30, 20, 0], "speeds": (-0.5, 0, 0),
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET,
             "gun": {"mode": "DOWN", "volley": 1}},     # drops ONE bullet straight down each time it fires
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

        "sizes": {"SMALL": {"splits_to": None}},        # as level 1: LARGE -> 2 MEDIUMs -> 4 SMALLs, which DIE

        "spawn": [
            # three LARGE shapes along the far wall, 5 units apart, floating half a unit off the floor, spins alternating.
            # A tilted LARGE cube or pyramid reaches up to 1.78 below its centre and 2.09 behind it (and about 2.1
            # sideways, so 5 apart they never touch), so: y 1.28, z 5.86 - like level 1's cube.
            # A diamond's tips are all 1 from its centre (1.25 at LARGE), whichever way it turns, so it sits at y 0.75.
            {"design": "cube", "name": "ice cube",                # ICE
             "position": [-5, 1.78, 5.86], "size": "LARGE",
             "angles": [30, 20, 0], "speeds": (0.5, 0, 0),
             "colour": (120, 190, 240), "palette": PALETTE_ICE,
             "gun": {"mode": "DOWN", "volley": 1}},     # drops ONE bullet straight down each time it fires
            {"design": "diamond", "name": "fire and ice diamond",  # FIRE AND ICE
             "position": [0, 1.25, 5.86], "size": "LARGE",
             "angles": [0, 20, 0], "speeds": (-0.5, 0, 0),
             "colour": FIRE_AND_ICE, "palette": PALETTE_FIRE_AND_ICE,
             "gun": {"mode": "DOWN", "volley": 1}},     # drops ONE bullet straight down each time it fires
            {"design": "pyramid", "name": "fire pyramid",          # FIRE
             "position": [5, 1.78, 5.86], "size": "LARGE",
             "angles": [-30, 20, 0], "speeds": (0.5, 0, 0),
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET,
             "gun": {"mode": "DOWN", "volley": 1}},     # drops ONE bullet straight down each time it fires
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
        ],
    },

    8: {    # ---- LEVEL 8: THE BIG ROOM - an EMPTY room twice as wide and long (32 x 32): how does big feel? ----
        "name": "The Big Room",
        "intro": "Nothing here yet - just space. How does a 32 x 32 room feel?",
        "world": {"min": (-16, -1, -16), "max": (16, 7, 16)},       # 32 wide (x), 32 long (z), 8 tall
        "start": {"x": 0, "y": 0, "z": -14, "turn": 0, "tip": 0},    # near the back wall, facing the far wall

        "floor_shapes": [],
        "boxes": [],
        "spawn": [],                                    # EMPTY: a level with nothing to destroy never "completes"
    },

    9: {    # ---- LEVEL 9: THE HUGE ROOM - a clone of level 8, but three times as wide and long (48 x 48) ----
        "name": "The Huge Room",
        "intro": "Still nothing here - just even more space. How does a 48 x 48 room feel?",
        "world": {"min": (-24, -1, -24), "max": (24, 7, 24)},       # 48 wide (x), 48 long (z), 8 tall
        "start": {"x": 0, "y": 0, "z": -22, "turn": 0, "tip": 0},    # near the back wall, facing the far wall

        "floor_shapes": [],
        "boxes": [],
        "spawn": [],                                    # EMPTY: a level with nothing to destroy never "completes"
    },

    99: {   # ---- LEVEL 99: SKUNK WORKS - the test level: the world as built so far ----
        "name": "Skunk works",
        "intro": "The test level: everything built so far, all at once.",
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
             "colour": (120, 190, 240), "palette": PALETTE_ICE},

            {"design": "cube", "name": "small cube",
             "position": [3, -0.8, 5], "velocity": [-0.03, 0.02, 0.025],
             "size": "TINY", "angles": [-50, 0, 0], "speeds": (2, 0, 0),
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET},

            {"design": "cube", "name": "floor mini",
             "position": [-3, -0.7, 4], "velocity": [0.025, 0.03, 0.02],
             "size": "TINY", "angles": [20, 0, 0], "speeds": (1, 0, 0),
             "colour": (120, 190, 240), "palette": PALETTE_ICE},

            {"design": "cube", "name": "hover mini",
             "position": [0, 0.6, 6], "velocity": [-0.02, -0.015, 0.03],
             "size": "TINY", "angles": [10, 30, 0], "speeds": (1.5, 1, 0.5),
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET},

            {"design": "cube", "name": "high mini",
             "position": [5, 2.5, 10], "velocity": [-0.035, -0.02, -0.01],
             "size": "SMALL", "angles": [45, 20, 10], "speeds": (0.5, 2, 1),
             "colour": (120, 190, 240), "palette": PALETTE_ICE},

            {"design": "cube", "name": "mid mini",
             "position": [-5, 1.2, 11], "velocity": [0.015, 0.025, -0.03],
             "size": "TINY", "angles": [0, 45, 45], "speeds": (3, 0, 1),
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET},

            {"design": "cube", "name": "gold mini",             # (named "gold", but it's an ice-blue cube)
             "position": [1.5, 1, 3.5], "velocity": [0.04, 0.035, 0.03],
             "size": "TINY", "angles": [30, 0, 0], "speeds": (1, 1, 1),
             "colour": (120, 190, 240), "palette": PALETTE_ICE},

            # ---- PYRAMIDS ----
            {"design": "pyramid", "name": "big pyramid",
             "position": [4, 1, 8], "velocity": [-0.015, 0.005, 0.01],
             "size": "LARGE", "angles": [15, 0, 0], "speeds": (0.7, 0, 0),
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET},

            {"design": "pyramid", "name": "tumble pyramid",
             "position": [-3, 2.5, 7], "velocity": [0.03, -0.02, 0.02],
             "size": "SMALL", "angles": [0, 60, 20], "speeds": (1, 2.5, 0.5),
             "colour": (120, 190, 240), "palette": PALETTE_ICE},

            # ---- DIAMONDS ----
            {"design": "diamond", "name": "sunset diamond",
             "position": [-1, 1.5, 6], "velocity": [0.02, 0.03, -0.02],
             "size": "SMALL", "angles": [0, 0, 0], "speeds": (2, 0, 0),
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET},

            {"design": "diamond", "name": "ice diamond",
             "position": [2, 2, 10], "velocity": [-0.025, -0.015, -0.03],
             "size": "MEDIUM", "angles": [45, 30, 0], "speeds": (1.5, 0.8, 1.2),
             "colour": (120, 190, 240), "palette": PALETTE_ICE},

            {"design": "diamond", "name": "spark diamond",
             "position": [5, 0.5, 4], "velocity": [-0.04, 0.025, 0.035],
             "size": "TINY", "angles": [10, 20, 30], "speeds": (4, 3, 2),
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET},

            # ---- FRAMES ----
            {"design": "frame", "name": "big frame",
             "position": [0, 1, 8], "velocity": [0.05, 0.015, -0.008],
             "size": "LARGE", "angles": [20, 0, 0], "speeds": (0.5, 0, 0),
             "colour": (120, 190, 240), "palette": PALETTE_ICE},

            {"design": "frame", "name": "tumble frame",
             "position": [-4, 2, 6], "velocity": [0.025, -0.02, 0.015],
             "size": "MEDIUM", "angles": [0, 30, 15], "speeds": (1, 1.5, 0.7),
             "colour": (255, 120, 60), "palette": PALETTE_SUNSET},

            # ---- TANKS: they sit on the floor (centre y = FLOOR_Y + size), turned round to face you (-z) ----
            {"design": "twin tank", "name": "tank",             # the BIG tank, parked
             "position": [0, 0.5, 16], "size": 1.5, "angles": [180, 0, 0],
             "colour": (120, 190, 80), "palette": PALETTE_FOREST,
             "gun": {"volley": 6},                              #   TWO barrels: 6 shots a volley (3 each)
             "children": [{"speeds": (0.3, 0, 0)},              #   its turret turns slowly
                          {"speeds": (-6, 0, 0)}]},             #   its radar spins the OPPOSITE way, fast

            {"design": "tank", "name": "tank left",             # parked
             "position": [-3.5, 0, 16], "size": 1, "angles": [180, 0, 0],
             "colour": (120, 190, 80), "palette": PALETTE_FOREST,
             "children": [{"speeds": (-0.5, 0, 0)},
                          {"speeds": (6, 0, 0)}]},

            {"design": "tank", "name": "small tank",            # drives at an angle: speed 0.01 (a 3-4-5 triangle)
             "position": [3.5, -0.4, 16], "velocity": [-0.006, 0, -0.008],
             "size": 0.6, "angles": [180, 0, 0],
             "colour": (120, 190, 80), "palette": PALETTE_FOREST,
             "children": [{"speeds": (2, 0, 0)},                #   its turret turns fast
                          {"speeds": (-6, 0, 0)}]},
        ],
    },
}
