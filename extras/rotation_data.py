# rotation_data.py - the WORLD's data for rotation_301: colours, models, things, settings and shared state.
#
# No pygame here and no drawing: just numbers, lists and dictionaries that the other two files use.
#   rotation_functions.py - HOW things work (maths, drawing, collisions, sounds)
#   rotation_301.py       - the GAME: the main loop that runs it all
#
# A few words used all through this file:
#   WORLD units  - the game's own measure of distance. One floor grid square is 1 x 1 world unit.
#   frame        - one trip round the game loop. The game runs at 60 frames a second, so a speed of
#                  0.05 "per frame" is 0.05 x 60 = 3 world units a second.
#   x, y, z      - x = left / right, y = up / down, z = forward / back (+z is "up the map").
#   model units  - a model's own measurements, round its centre (0, 0, 0), BEFORE its thing sizes it.
import math


# ================================ COLOURS ================================
# A colour is (red, green, blue), each from 0 (none) to 255 (full).
BLACK = (0, 0, 0)               # the background
GREEN = (0, 255, 0)             # the text and bars in the top-left corner
ORANGE = (255, 150, 0)          # (spare: not used at the moment)
CYAN = (0, 255, 255)            # (spare)
RED = (255, 60, 60)             # (spare)
PURPLE = (160, 100, 230)        # (spare)
BLUE = (70, 150, 255)           # (spare)
GOLD = (245, 200, 60)           # (spare: the gold things use PALETTE_GOLD and (255, 215, 0))
CUBE_GREEN = (70, 230, 120)     # (spare)
PINK = (255, 105, 200)          # (spare: YOU on the mini-map are gold now - PLAYER_MAP_COLOUR in rotation_functions.py)


# ---- PALETTES: a list of colours for a shape's FACES ----
# Face 0 gets colour 0, face 1 gets colour 1, and so on, in order.
#   MORE colours than faces  -> the extra colours are simply not used.
#   FEWER colours than faces -> start again from colour 0 (wrap round).
PALETTE_WARM = [                # (spare: not used at the moment)
    (235, 80, 80), (245, 140, 50), (245, 200, 60), (250, 120, 100),
    (255, 110, 170), (200, 60, 60), (255, 180, 120),
]
PALETTE_COOL = [                # (spare)
    (70, 150, 255), (60, 210, 200), (160, 100, 230), (90, 170, 255),
]
PALETTE_GOLD = [                # just one colour: every face gold (the lighting still shades each side)
    (245, 200, 60),
]
STONE = (110, 125, 95)         # mossy stone: the outline colour for jungle ruins (boxes)
PALETTE_STONE = [(120, 130, 105), (95, 108, 85), (140, 150, 120), (85, 98, 78), (150, 160, 130), (75, 88, 68)]
SAND = (170, 150, 100)          # sandbags: the outline colour for jungle defences (boxes)
PALETTE_SAND = [(180, 160, 110), (150, 132, 90), (200, 180, 125), (140, 122, 82), (210, 190, 135), (130, 112, 75)]
PALETTE_BLACK = [               # every face BLACK, like the background: with a coloured outline it looks like a
    (0, 0, 0),                  #   wireframe, but the faces still HIDE the edges behind them ("hidden lines")
]
PALETTE_GREY = [                # "NOT SET": the designs' own palette. A thing that shows up grey is missing its
    (128, 128, 128),            #   own "palette" in a level's spawn list (load_level warns about it too)
]
GREY = (128, 128, 128)          # "NOT SET": the designs' own outline colour, for the same reason
PALETTE_FOREST = [              # greens and browns: the tanks
    (60, 140, 70), (120, 190, 80), (190, 220, 110), (90, 160, 140), (150, 110, 60),
]
PALETTE_SUNSET = [              # orange, pink, purple
    (255, 120, 60), (230, 70, 110), (130, 70, 170),
]
PALETTE_FIRE_AND_ICE = [        # ice and sunset colours taking turns, face by face (level 3's diamond)
    (220, 245, 255), (255, 120, 60), (120, 190, 240), (230, 70, 110),
    (80, 150, 220), (130, 70, 170),
]
FIRE_AND_ICE = (200, 170, 255)  # its outline colour: between the ice blue and the sunset orange
ICE_BLOCK = (170, 225, 255)     # the outline of ICE BLOCK boxes (level 9)
SNOW = (235, 245, 255)          # the outline of packed SNOW boxes (your fort, level 9)
PALETTE_SNOW = [(235, 245, 255), (210, 225, 240), (195, 212, 232), (225, 235, 250)]   # snow: white to pale blue-grey
OBSIDIAN = (200, 60, 35)        # the outline of OBSIDIAN boxes (level 10): a red glow round dark rock
PALETTE_OBSIDIAN = [(45, 32, 38), (60, 40, 46), (34, 24, 30), (72, 46, 44), (52, 36, 42), (40, 28, 34)]   # near-black rock
EMBER = (255, 170, 90)          # the outline of hot EMBER blocks (level 10), faces in PALETTE_SUNSET
SLIME = (140, 230, 60)          # SLIME things' outline: toxic lime (level 11)
PALETTE_SLIME = [(140, 230, 60), (90, 200, 70), (60, 160, 60), (170, 240, 90), (110, 210, 120)]   # toxic greens
SLUDGE = (120, 220, 60)         # the outline of SLUDGE boxes (level 11): glowing lime round dark muck
PALETTE_SLUDGE = [(32, 58, 30), (42, 72, 36), (26, 46, 28), (52, 84, 42), (36, 64, 34)]           # dark sewer greens
CUSTARD = (245, 205, 100)       # CUSTARD things' outline (level 12)
PALETTE_CUSTARD = [(255, 228, 140), (245, 205, 100), (230, 180, 80), (255, 240, 180), (220, 165, 75)]   # custard yellows
SPONGE = (225, 185, 115)        # the outline of SPONGE CAKE boxes (level 12)
PALETTE_SPONGE = [(235, 200, 130), (215, 175, 105), (245, 215, 150), (200, 160, 95), (225, 190, 120)]   # golden sponge
JELLY = (255, 90, 120)          # JELLY's outline: red jelly towers and jelly cubes (level 12)
PALETTE_JELLY = [(230, 40, 80), (200, 30, 70), (250, 80, 110), (180, 25, 60), (240, 60, 95)]           # red jellies
CANDY = (255, 150, 195)         # CUPID CANYON (level 12): candy pink outlines
PALETTE_CANDY = [(255, 170, 205), (240, 140, 185), (255, 195, 220), (225, 120, 170), (250, 160, 200)]   # candy pinks
ROSE = (255, 95, 170)           # CUPID CANYON: hot-pink outlines (the towers and the heart cubes)
PALETTE_ROSE = [(235, 70, 150), (205, 45, 125), (250, 100, 170), (185, 35, 110), (240, 85, 160)]        # rose pinks
BULLION = (255, 215, 90)        # FORT KNOX (level 13): gold-bar outlines
PALETTE_BULLION = [(232, 186, 62), (205, 158, 42), (250, 212, 92), (182, 138, 32), (242, 198, 72)]     # gold bars
BRONZE = (225, 150, 75)         # FORT KNOX: bronze outlines (the towers and cubes)
PALETTE_BRONZE = [(195, 122, 52), (165, 98, 38), (215, 142, 68), (142, 82, 32), (205, 132, 60)]        # bronzes
PALETTE_ICE = [                 # pale blues
    (220, 245, 255), (170, 220, 250), (120, 190, 240), (80, 150, 220),
    (180, 240, 230), (130, 210, 210), (200, 200, 255), (150, 170, 230),
]


# ---- LIGHT: one lamp, far away like the sun ----
LIGHT = (0.48, 0.6, -0.64)      # the direction TOWARDS the light, length 1: from +x, from above, and from -z.
                                #   A face pointing this way is lit fully; a face pointing away gets AMBIENT only.
AMBIENT = 0.2                   # everyone deserves a little light: even a face turned away is 20% bright


SHOW_VOLUME = False   # True = show the volume slider on screen (the - and = keys work either way)
# ---- VOLUME: the slider for every sound (- and = keys). How it's applied: apply_volume() in rotation_functions.py
volume = {"slider": 0.20}       # 0.0 .. 1.0 = 0% .. 100%: starts at 20%


# ================================ MODELS ================================
# A MODEL is a shape's own description, built round its centre (0, 0, 0), in model units.
# Many things can share one model (all three tanks share hull_model) - each thing sizes, turns and places it.
# Every model is built FACING +z (its front), with +y up and +x to its right.
#
# A model dictionary has:
#   "points"            - its corners, as (x, y, z). A corner's NUMBER is its place in this list: 0, 1, 2 ...
#   "edges"             - lines between two corners, as (corner, corner). Only drawn for a model with NO faces.
#   "faces"             - the flat sides, each (corners, normal):
#                           corners = the corner numbers, going ROUND the face. Seen from outside, they go the
#                                     way that makes is_facing_you() say yes - backwards faces are skipped.
#                           normal  = the direction the face points, length 1 (used for the lighting).
#                         A face's place in this list picks its colour from the thing's palette.
#   "collision_spheres" - the spheres used for bumping into things, each ((x, y, z) offset from the centre, radius).
#                         Like the corners, they get sized, spun and placed with the thing, so they turn with the shape.
#   "muzzles"           - (turrets only) where bullets come out, as (x, y, z).


# ---- CUBE: 8 corners, 6 square faces ----
cube_points = [
    (-1, -1, -1), ( 1, -1, -1), ( 1, -1,  1), (-1, -1,  1),     # 0-3  bottom: corners at y = -1
    (-1,  1, -1), ( 1,  1, -1), ( 1,  1,  1), (-1,  1,  1),     # 4-7  top: the same four, at y = +1
]
cube_edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),         # bottom square
    (4, 5), (5, 6), (6, 7), (7, 4),         # top square
    (0, 4), (1, 5), (2, 6), (3, 7),         # the four upright edges
]
cube_faces = [
    ((6, 7, 3, 2), (0, 0, 1)),              # 0  +z side (the cube's front: away from you when you look up the map)
    ((7, 4, 0, 3), (-1, 0, 0)),             # 1  -x side (left)
    ((5, 6, 2, 1), (1, 0, 0)),              # 2  +x side (right)
    ((7, 6, 5, 4), (0, 1, 0)),              # 3  top
    ((2, 3, 0, 1), (0, -1, 0)),             # 4  bottom
    ((4, 5, 1, 0), (0, 0, -1)),             # 5  -z side (the cube's back: toward you when you look up the map)
]
cube_model = {
    "points": cube_points,
    "edges": cube_edges,
    "faces": cube_faces,
    "collision_spheres": [((0, 0, 0), 1.2)],    # one sphere: between a side (1 away) and a corner (1.73 away)
}

# ---- LOW BOX: the cube squashed to HALF height (2 wide, 2 deep, 1 tall): a bunker's base ----
# The same corner order as the cube, so the cube's edges and faces (and their normals) fit it exactly:
# squashing it straight down doesn't change which way any face points.
low_box_points = [
    (-1, -0.5, -1), ( 1, -0.5, -1), ( 1, -0.5,  1), (-1, -0.5,  1),     # 0-3  bottom: y = -0.5
    (-1,  0.5, -1), ( 1,  0.5, -1), ( 1,  0.5,  1), (-1,  0.5,  1),     # 4-7  top (the lid): y = +0.5
]
low_box_model = {
    "points": low_box_points,
    "edges": cube_edges,
    "faces": cube_faces,
    "collision_spheres": [((-0.5, 0, 0), 0.75), ((0.5, 0, 0), 0.75)],    # two side by side: it's wide, not tall
}


# ---- PYRAMID: a square base and a point on top ----
pyramid_points = [
    (-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1),     # 0-3  the square base, at y = -1
    (0, 1, 0),                                              # 4    the tip, at y = +1
]
pyramid_edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),         # the base
    (0, 4), (1, 4), (2, 4), (3, 4),         # up to the tip
]
pyramid_faces = [
    ((2, 3, 0, 1), (0, -1, 0)),             # 0  base (points down)
    ((4, 1, 0), (0, 0.447, -0.894)),        # 1  -z slope
    ((4, 2, 1), (0.894, 0.447, 0)),         # 2  +x slope
    ((4, 3, 2), (0, 0.447, 0.894)),         # 3  +z slope
    ((4, 0, 3), (-0.894, 0.447, 0)),        # 4  -x slope
]
pyramid_model = {
    "points": pyramid_points,
    "edges": pyramid_edges,
    "faces": pyramid_faces,
    "collision_spheres": [((0, -0.3, 0), 1.0)],     # lowered: the pyramid is heavier at the bottom
}

# The same pyramid as a WIREFRAME: no faces, so it's drawn as its edges (lines in the thing's colour).
# Everything else is the pyramid's: its corners, edges and collision sphere.
pyramid_wire_model = {
    "points": pyramid_points,
    "edges": pyramid_edges,
    "faces": [],                                    # no faces = drawn as lines
    "collision_spheres": pyramid_model["collision_spheres"],
}


# ---- DIAMOND: two pyramids back to back, 8 triangle faces ----
diamond_points = [
    (0, 1, 0), (0, -1, 0),                  # 0-1  top tip, bottom tip
    (-1, 0, 0), (1, 0, 0),                  # 2-3  left and right points of the middle
    (0, 0, -1), (0, 0, 1),                  # 4-5  back and front points of the middle
]
diamond_edges = [
    (2, 4), (4, 3), (3, 5), (5, 2),         # the middle square
    (0, 2), (0, 3), (0, 4), (0, 5),         # up to the top tip
    (1, 2), (1, 3), (1, 4), (1, 5),         # down to the bottom tip
]
diamond_faces = [
    ((0, 4, 2), (-0.577, 0.577, -0.577)),   # 0  top half: -x, -z
    ((0, 3, 4), (0.577, 0.577, -0.577)),    # 1  top half: +x, -z
    ((0, 5, 3), (0.577, 0.577, 0.577)),     # 2  top half: +x, +z
    ((0, 2, 5), (-0.577, 0.577, 0.577)),    # 3  top half: -x, +z
    ((1, 2, 4), (-0.577, -0.577, -0.577)),  # 4  bottom half: -x, -z
    ((1, 4, 3), (0.577, -0.577, -0.577)),   # 5  bottom half: +x, -z
    ((1, 3, 5), (0.577, -0.577, 0.577)),    # 6  bottom half: +x, +z
    ((1, 5, 2), (-0.577, -0.577, 0.577)),   # 7  bottom half: -x, +z
]
diamond_model = {
    "points": diamond_points,
    "edges": diamond_edges,
    "faces": diamond_faces,
    "collision_spheres": [((0, 0, 0), 1.0)],    # the tips are exactly 1 from the centre
}


# ---- FRAME: a square with a hole in the middle, made of 4 long boxes ----
# Each box uses the same corner order and the same faces as the cube, with its corner numbers moved along by 8.
frame_points = [
    # 0-7 TOP box (y 0.6 to 1)
    (-1, 0.6, -0.2), (1, 0.6, -0.2), (1, 0.6, 0.2), (-1, 0.6, 0.2),
    (-1, 1, -0.2), (1, 1, -0.2), (1, 1, 0.2), (-1, 1, 0.2),
    # 8-15 BOTTOM box (y -1 to -0.6)
    (-1, -1, -0.2), (1, -1, -0.2), (1, -1, 0.2), (-1, -1, 0.2),
    (-1, -0.6, -0.2), (1, -0.6, -0.2), (1, -0.6, 0.2), (-1, -0.6, 0.2),
    # 16-23 LEFT box (x -1 to -0.6, between the top and bottom boxes)
    (-1, -0.6, -0.2), (-0.6, -0.6, -0.2), (-0.6, -0.6, 0.2), (-1, -0.6, 0.2),
    (-1, 0.6, -0.2), (-0.6, 0.6, -0.2), (-0.6, 0.6, 0.2), (-1, 0.6, 0.2),
    # 24-31 RIGHT box (x 0.6 to 1)
    (0.6, -0.6, -0.2), (1, -0.6, -0.2), (1, -0.6, 0.2), (0.6, -0.6, 0.2),
    (0.6, 0.6, -0.2), (1, 0.6, -0.2), (1, 0.6, 0.2), (0.6, 0.6, 0.2),
]
frame_edges = [
    (0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7),                  # top box
    (8, 9), (9, 10), (10, 11), (11, 8), (12, 13), (13, 14), (14, 15), (15, 12), (8, 12), (9, 13), (10, 14), (11, 15),    # bottom box
    (16, 17), (17, 18), (18, 19), (19, 16), (20, 21), (21, 22), (22, 23), (23, 20), (16, 20), (17, 21), (18, 22), (19, 23),    # left box
    (24, 25), (25, 26), (26, 27), (27, 24), (28, 29), (29, 30), (30, 31), (31, 28), (24, 28), (25, 29), (26, 30), (27, 31),    # right box
]
frame_faces = [
    # TOP box: all 6 sides
    ((6, 7, 3, 2), (0, 0, 1)),              # 0   +z side
    ((7, 4, 0, 3), (-1, 0, 0)),             # 1   -x side
    ((5, 6, 2, 1), (1, 0, 0)),              # 2   +x side
    ((7, 6, 5, 4), (0, 1, 0)),              # 3   top
    ((2, 3, 0, 1), (0, -1, 0)),             # 4   bottom
    ((4, 5, 1, 0), (0, 0, -1)),             # 5   -z side
    # BOTTOM box: all 6 sides
    ((14, 15, 11, 10), (0, 0, 1)),          # 6   +z side
    ((15, 12, 8, 11), (-1, 0, 0)),          # 7   -x side
    ((13, 14, 10, 9), (1, 0, 0)),           # 8   +x side
    ((15, 14, 13, 12), (0, 1, 0)),          # 9   top
    ((10, 11, 8, 9), (0, -1, 0)),           # 10  bottom
    ((12, 13, 9, 8), (0, 0, -1)),           # 11  -z side
    # LEFT box: 4 sides (no top / bottom: they touch the top and bottom boxes)
    ((22, 23, 19, 18), (0, 0, 1)),          # 12  +z side
    ((23, 20, 16, 19), (-1, 0, 0)),         # 13  -x side
    ((21, 22, 18, 17), (1, 0, 0)),          # 14  +x side
    ((20, 21, 17, 16), (0, 0, -1)),         # 15  -z side
    # RIGHT box: 4 sides
    ((30, 31, 27, 26), (0, 0, 1)),          # 16  +z side
    ((31, 28, 24, 27), (-1, 0, 0)),         # 17  -x side
    ((29, 30, 26, 25), (1, 0, 0)),          # 18  +x side
    ((28, 29, 25, 24), (0, 0, -1)),         # 19  -z side
]
#   20 faces: the top and bottom boxes have all 6, the left and right boxes only 4. Their top and bottom
#   faces were removed: they sit flat against the top and bottom boxes, hidden inside the frame,
#   and only caused flickering lines where the boxes meet.
frame_model = {
    "points": frame_points,
    "edges": frame_edges,
    "faces": frame_faces,
    # 8 spheres round the ring, 0.8 apart, so neighbours overlap a little. The middle stays open (about +-0.35).
    "collision_spheres": [
        ((-0.8,  0.8, 0), 0.45), ((0,  0.8, 0), 0.45), ((0.8,  0.8, 0), 0.45),     # top arm
        ((-0.8,    0, 0), 0.45),                         ((0.8,    0, 0), 0.45),     # side arms
        ((-0.8, -0.8, 0), 0.45), ((0, -0.8, 0), 0.45), ((0.8, -0.8, 0), 0.45),     # bottom arm
    ],
}


# ---- TANK HULL (from rotation_101's tank): the tracks and body, facing +z ----
# The tank is THREE things: this hull, plus a turret and a radar that are CHILDREN riding on it.
hull_points = [
    (-0.9, -1, -1.3), (0.9, -1, -1.3), (0.9, -1, 1.2), (-0.9, -1, 1.2),                # 0-3   track base (on the floor)
    (-1.1, -0.55, -1.5), (1.1, -0.55, -1.5), (1.1, -0.55, 1.6), (-1.1, -0.55, 1.6),    # 4-7   belt (the widest part)
    (-0.75, -0.1, -1.2), (0.75, -0.1, -1.2), (0.75, -0.1, 0.5), (-0.75, -0.1, 0.5),    # 8-11  deck (the flat top)
]
hull_edges = [
    # each base corner: along the base, and up to the belt
    (0, 1), (0, 4), (1, 2), (1, 5), (2, 3), (2, 6), (3, 0), (3, 7),
    # each belt corner: along the belt, and up to the deck
    (4, 5), (4, 8), (5, 6), (5, 9), (6, 7), (6, 10), (7, 4), (7, 11),
    # round the deck
    (8, 9), (9, 10), (10, 11), (11, 8),
]
hull_faces = [
    ((0, 1, 2, 3), (0, -1, 0)),             # 0  underside
    ((0, 4, 5, 1), (0, -0.406, -0.914)),    # 1  base -> belt, -z side (rear)
    ((1, 5, 6, 2), (0.914, -0.406, 0)),     # 2  base -> belt, +x side
    ((2, 6, 7, 3), (0, -0.664, 0.747)),     # 3  base -> belt, +z side (front)
    ((3, 7, 4, 0), (-0.914, -0.406, 0)),    # 4  base -> belt, -x side
    ((4, 8, 9, 5), (0, 0.555, -0.832)),     # 5  belt -> deck, -z side (rear slope)
    ((5, 9, 10, 6), (0.789, 0.614, 0)),     # 6  belt -> deck, +x side
    ((6, 10, 11, 7), (0, 0.926, 0.379)),    # 7  belt -> deck, +z side (the front slope)
    ((7, 11, 8, 4), (-0.789, 0.614, 0)),    # 8  belt -> deck, -x side
    ((8, 11, 10, 9), (0, 1, 0)),            # 9  the deck
]
hull_model = {
    "points": hull_points,
    "edges": hull_edges,
    "faces": hull_faces,
    "collision_spheres": [
        ((0, -0.4, -0.6), 1.0),             # rear hull (still reaches up round the turret)
        ((0, -0.4,  0.7), 1.0),             # front hull (overlaps the rear one)
    ],
}


# ---- TANK TURRET: turret + barrel, built round its PIVOT (the middle of the turret's base) ----
# The old tank's numbers moved by y + 0.1, z + 0.3, so (0, 0, 0) is the point it spins round.
# It sits on the hull at (0, -0.1, -0.3) in the HULL's model units: that's the child's "position".
# The barrel is split in two (z 0.45 -> 1.3 -> 2.2): the painter's sort uses ONE centre point per
# face, and a long barrel face's centre sat right next to the hull's front slope's centre.
# (The radar is its own model: radar_model.)
turret_points = [
    (-0.5, 0, -0.6), (0.5, 0, -0.6), (0.5, 0, 0.6), (-0.5, 0, 0.6),                    # 0-3   turret: base
    (-0.4, 0.45, -0.5), (0.4, 0.45, -0.5), (0.4, 0.45, 0.3), (-0.4, 0.45, 0.3),        # 4-7   turret: top
    (-0.08, 0.12, 0.45), (0.08, 0.12, 0.45), (0.08, 0.12, 1.3), (-0.08, 0.12, 1.3),    # 8-11  barrel REAR piece: bottom
    (-0.08, 0.28, 0.45), (0.08, 0.28, 0.45), (0.08, 0.28, 1.3), (-0.08, 0.28, 1.3),    # 12-15 barrel REAR piece: top
    (-0.08, 0.12, 1.3), (0.08, 0.12, 1.3), (0.08, 0.12, 2.2), (-0.08, 0.12, 2.2),      # 16-19 barrel FRONT piece: bottom
    (-0.08, 0.28, 1.3), (0.08, 0.28, 1.3), (0.08, 0.28, 2.2), (-0.08, 0.28, 2.2),      # 20-23 barrel FRONT piece: top
]
turret_edges = [
    (0, 1), (0, 4), (1, 2), (1, 5), (2, 3), (2, 6), (3, 0), (3, 7), (4, 5), (5, 6), (6, 7), (7, 4),                 # turret
    (8, 9), (9, 10), (10, 11), (11, 8), (12, 13), (13, 14), (14, 15), (15, 12), (8, 12), (9, 13), (10, 14), (11, 15),    # barrel: rear piece
    (16, 17), (17, 18), (18, 19), (19, 16), (20, 21), (21, 22), (22, 23), (23, 20), (16, 20), (17, 21), (18, 22), (19, 23),    # barrel: front piece
]
turret_faces = [
    # turret
    ((0, 4, 5, 1), (0, 0.217, -0.976)),     # 0   -z side (rear)
    ((1, 5, 6, 2), (0.976, 0.217, 0)),      # 1   +x side
    ((2, 6, 7, 3), (0, 0.555, 0.832)),      # 2   +z side (front, sloped)
    ((3, 7, 4, 0), (-0.976, 0.217, 0)),     # 3   -x side
    ((4, 7, 6, 5), (0, 1, 0)),              # 4   top
    # barrel REAR piece
    ((8, 9, 10, 11), (0, -1, 0)),           # 5   bottom
    ((12, 15, 14, 13), (0, 1, 0)),          # 6   top
    ((9, 13, 14, 10), (1, 0, 0)),           # 7   +x side
    ((11, 15, 12, 8), (-1, 0, 0)),          # 8   -x side
    ((18, 22, 23, 19), (0, 0, 1)),          # 9   the MUZZLE (+z end) - on the FRONT piece's tip
    # barrel FRONT piece
    ((16, 17, 18, 19), (0, -1, 0)),         # 10  bottom
    ((20, 23, 22, 21), (0, 1, 0)),          # 11  top
    ((17, 21, 22, 18), (1, 0, 0)),          # 12  +x side
    ((19, 23, 20, 16), (-1, 0, 0)),         # 13  -x side
]
#   14 faces, numbered as above for the palette. The barrel points to +z (the turret's front).
#   No faces where the two barrel pieces meet: they'd be hidden inside the barrel and only flicker.
turret_model = {
    "points": turret_points,
    "edges": turret_edges,
    "faces": turret_faces,
    "muzzles": [(0, 0.2, 2.2)],                     # where bullets come out: the barrel's tip
    "collision_spheres": [((0, 0.2, 2.05), 0.2)],   # barrel tip: swings WITH the turret
}

# ---- CUPOLA: a turret with NO barrel (for bunkers on walls and ceilings) ----
# The turret's body only: its first 8 corners, its first 12 edges and its first 5 faces (no barrel).
# Its FRONT is still +z (the sloped side): aiming turns +z towards you, exactly as with a barrel.
# Bullets come out of its ROOF instead of a barrel tip: "muzzles" is just a point, anywhere on the model.
cupola_model = {
    "points": turret_points[:8],
    "edges": turret_edges[:12],
    "faces": turret_faces[:5],                      # 0 rear, 1 +x, 2 FRONT (sloped, +z), 3 -x, 4 roof
    "muzzles": [(0, 0.45, -0.1)],                   # the middle of its roof
    "collision_spheres": [((0, 0.25, 0), 0.5)],
}
# Its colours: forest green, with a bright GOLD VISOR on the front (face 2), so you can see which way it faces
PALETTE_CUPOLA = [(60, 140, 70), (60, 140, 70), (255, 215, 0), (60, 140, 70), (90, 160, 80)]


# ---- TWIN TURRET: the same turret, with TWO barrels side by side (for the big tank) ----
# Same turret points as turret_model. Its one barrel was moved 0.15 to the left, and a copy
# added 0.15 to the right (the barrels are 0.16 wide, so that leaves a small gap between them).
# Built round the same PIVOT, so it fits the hull at (0, -0.1, -0.3) just like turret_model.
twin_turret_points = [
    (-0.5, 0, -0.6), (0.5, 0, -0.6), (0.5, 0, 0.6), (-0.5, 0, 0.6),                        # 0-3   turret: base
    (-0.4, 0.45, -0.5), (0.4, 0.45, -0.5), (0.4, 0.45, 0.3), (-0.4, 0.45, 0.3),            # 4-7   turret: top
    (-0.23, 0.12, 0.45), (-0.07, 0.12, 0.45), (-0.07, 0.12, 1.3), (-0.23, 0.12, 1.3),      # 8-11  LEFT barrel (x - 0.15): REAR piece: bottom
    (-0.23, 0.28, 0.45), (-0.07, 0.28, 0.45), (-0.07, 0.28, 1.3), (-0.23, 0.28, 1.3),      # 12-15 LEFT barrel: REAR piece: top
    (-0.23, 0.12, 1.3), (-0.07, 0.12, 1.3), (-0.07, 0.12, 2.2), (-0.23, 0.12, 2.2),        # 16-19 LEFT barrel: FRONT piece: bottom
    (-0.23, 0.28, 1.3), (-0.07, 0.28, 1.3), (-0.07, 0.28, 2.2), (-0.23, 0.28, 2.2),        # 20-23 LEFT barrel: FRONT piece: top
    (0.07, 0.12, 0.45), (0.23, 0.12, 0.45), (0.23, 0.12, 1.3), (0.07, 0.12, 1.3),          # 24-27 RIGHT barrel (x + 0.15): REAR piece: bottom
    (0.07, 0.28, 0.45), (0.23, 0.28, 0.45), (0.23, 0.28, 1.3), (0.07, 0.28, 1.3),          # 28-31 RIGHT barrel: REAR piece: top
    (0.07, 0.12, 1.3), (0.23, 0.12, 1.3), (0.23, 0.12, 2.2), (0.07, 0.12, 2.2),            # 32-35 RIGHT barrel: FRONT piece: bottom
    (0.07, 0.28, 1.3), (0.23, 0.28, 1.3), (0.23, 0.28, 2.2), (0.07, 0.28, 2.2),            # 36-39 RIGHT barrel: FRONT piece: top
]
twin_turret_edges = [
    (0, 1), (0, 4), (1, 2), (1, 5), (2, 3), (2, 6), (3, 0), (3, 7), (4, 5), (5, 6), (6, 7), (7, 4),                 # turret
    (8, 9), (9, 10), (10, 11), (11, 8), (12, 13), (13, 14), (14, 15), (15, 12), (8, 12), (9, 13), (10, 14), (11, 15),    # left barrel: rear piece
    (16, 17), (17, 18), (18, 19), (19, 16), (20, 21), (21, 22), (22, 23), (23, 20), (16, 20), (17, 21), (18, 22), (19, 23),    # left barrel: front piece
    (24, 25), (25, 26), (26, 27), (27, 24), (28, 29), (29, 30), (30, 31), (31, 28), (24, 28), (25, 29), (26, 30), (27, 31),    # right barrel: rear piece
    (32, 33), (33, 34), (34, 35), (35, 32), (36, 37), (37, 38), (38, 39), (39, 36), (32, 36), (33, 37), (34, 38), (35, 39),    # right barrel: front piece
]
twin_turret_faces = [
    # turret
    ((0, 4, 5, 1), (0, 0.217, -0.976)),     # 0   -z side (rear)
    ((1, 5, 6, 2), (0.976, 0.217, 0)),      # 1   +x side
    ((2, 6, 7, 3), (0, 0.555, 0.832)),      # 2   +z side (front, sloped)
    ((3, 7, 4, 0), (-0.976, 0.217, 0)),     # 3   -x side
    ((4, 7, 6, 5), (0, 1, 0)),              # 4   top
    # LEFT barrel, REAR piece
    ((8, 9, 10, 11), (0, -1, 0)),           # 5   bottom
    ((12, 15, 14, 13), (0, 1, 0)),          # 6   top
    ((9, 13, 14, 10), (1, 0, 0)),           # 7   +x side
    ((11, 15, 12, 8), (-1, 0, 0)),          # 8   -x side
    ((18, 22, 23, 19), (0, 0, 1)),          # 9   the left barrel's MUZZLE (on its FRONT piece's tip)
    # LEFT barrel, FRONT piece
    ((16, 17, 18, 19), (0, -1, 0)),         # 10  bottom
    ((20, 23, 22, 21), (0, 1, 0)),          # 11  top
    ((17, 21, 22, 18), (1, 0, 0)),          # 12  +x side
    ((19, 23, 20, 16), (-1, 0, 0)),         # 13  -x side
    # RIGHT barrel, REAR piece
    ((24, 25, 26, 27), (0, -1, 0)),         # 14  bottom
    ((28, 31, 30, 29), (0, 1, 0)),          # 15  top
    ((25, 29, 30, 26), (1, 0, 0)),          # 16  +x side
    ((27, 31, 28, 24), (-1, 0, 0)),         # 17  -x side
    ((34, 38, 39, 35), (0, 0, 1)),          # 18  the right barrel's MUZZLE (on its FRONT piece's tip)
    # RIGHT barrel, FRONT piece
    ((32, 33, 34, 35), (0, -1, 0)),         # 19  bottom
    ((36, 39, 38, 37), (0, 1, 0)),          # 20  top
    ((33, 37, 38, 34), (1, 0, 0)),          # 21  +x side
    ((35, 39, 36, 32), (-1, 0, 0)),         # 22  -x side
]
#   23 faces, numbered as above for the palette. Both barrels point to +z (the turret's front).
twin_turret_model = {
    "points": twin_turret_points,
    "edges": twin_turret_edges,
    "faces": twin_turret_faces,
    "muzzles": [(-0.15, 0.2, 2.2), (0.15, 0.2, 2.2)],      # both barrel tips: they take turns
    "collision_spheres": [
        ((-0.15, 0.2, 2.05), 0.2),          # left barrel tip
        (( 0.15, 0.2, 2.05), 0.2),          # right barrel tip
    ],
}


# ---- TANK RADAR: mast + dish, built round the FOOT of its mast ----
# A child of the HULL (not the turret): its mast stands only 0.2 from the turret's pivot, so it always
# stays over the turret's roof however the turret turns. It sits on the hull at (0, 0.35, -0.5).
radar_points = [
    (0, 0, 0), (0, 0.25, 0),                                                # 0-1  mast (an edge only)
    (-0.22, 0.25, 0), (0.22, 0.25, 0), (0.22, 0.47, 0), (-0.22, 0.47, 0),   # 2-5  dish
]
radar_edges = [
    (0, 1),                                 # mast
    (2, 3), (3, 4), (4, 5), (5, 2),         # dish
]
radar_faces = [
    ((2, 3, 4, 5), (0, 0, 1)),              # 0  dish: front
    ((2, 5, 4, 3), (0, 0, -1)),             # 1  dish: back (the same corners, the other way round)
]
radar_model = {
    "points": radar_points,
    "edges": radar_edges,
    "faces": radar_faces,
    "collision_spheres": [],                # none: the hull's rear sphere already covers it
}


# ================================ THINGS ================================
# THINGS: every object in the world, one dictionary each. A thing = a MODEL + where it is + how it moves.
#   "name"           - its name. Children find their parent by it, so names in this list must be different.
#   "model"          - which model it is drawn with (several things can share one model)
#   "position"       - where its centre is, [x, y, z] in WORLD units (a child: in its PARENT's model units)
#   "velocity"       - how far it moves each frame, [x, y, z] in world units per frame. [0, 0, 0] = parked.
#   "size"           - how much its model is scaled up: 1 = as built, 0.5 = half size
#   "angles"         - which way it is turned, [turn, tilt, spin] in degrees (round y, then x, then z)
#   "speeds"         - how fast it spins, (turn, tilt, spin) in degrees per frame
#   "colour"         - its outline colour (also its dot on the mini-map, and its sparks)
#   "palette"        - the colours for its faces (see PALETTES)
#   "faces_movement" - (tanks) True = it turns to face the way it's moving
#   "parent"         - (children) the NAME of the thing it rides on ("parent_thing" = that thing itself)
#   "gun", "cooldown", "next_muzzle", "volley_left", "volley_timer" - (turrets) it shoots at you; the rest
#                      keep track of its shooting while the game runs, so they all start at 0
# "position", "velocity" and "angles" are LISTS [ ], because they change every frame.
# A thing SITS ON THE FLOOR when its centre y = (FLOOR_Y + size) - for models whose lowest point is -1.
#
# The list starts EMPTY: load_level() in rotation_functions.py fills it from a level in rotation_levels.py
# (and broken pieces are added while the game runs).
things = []

# BULLETS in flight: their OWN list, not things. A bullet only flies straight and HITS: it never bounces, spins
# under your keys, has health or splits. move_bullets() in rotation_functions.py does everything a bullet does.
# Each bullet is a dictionary: "position", "velocity", "range" (how far it can still fly), "owner" (the thing
# that fired it; None = you), "colour", "palette", and "model", "size", "angles", "speeds" so it can be drawn.
bullets = []


# ---- SIZES: the NAMED sizes. A level spawns a shape at a named size: "size": "MEDIUM" ----
#   "across"    - how big it is, in world units (a cube of "across" 1.5 is 1.5 wide, tall and deep)
#   "health"    - how many of YOUR hits it takes to break it
#   "splits_to" - what it breaks into: TWO shapes of that size. None = it doesn't split, it just dies.
# A LEVEL can change any of these for itself, in its own "sizes" (see LEVELS in rotation_levels.py);
# load_level() puts the level's version in level_sizes. This table itself is never changed.
SIZES = {
    "HUGE":   {"across": 4,   "health": 5, "splits_to": "LARGE"},
    "LARGE":  {"across": 2.5, "health": 4, "splits_to": "MEDIUM"},
    "MEDIUM": {"across": 1.5, "health": 3, "splits_to": "SMALL"},
    "SMALL":  {"across": 1,   "health": 2, "splits_to": "TINY"},
    "TINY":   {"across": 0.5, "health": 1, "splits_to": None},        # the smallest: it just dies
}
level_sizes = {}          # this level's sizes: SIZES with the level's changes - filled by load_level()

# ---- HEALTH ----
# Shapes with a NAMED size get their health from the table above. Anything with a plain NUMBER for its
# size (the tanks, for now) gets its health from its reach instead: the biggest of those gets MAX_HEALTH.
MAX_HEALTH = 10           # health of the biggest number-sized thing; smaller ones get their share (at least 1)
HEALTH_SQUARE = 5         # pixels: each health square above a shape
HEALTH_GAP = 2            # pixels between the squares
SPLIT_KICK = 0.03         # how fast the two pieces of a broken shape push apart (world units per frame)


# ================================ YOU (the player) ================================
# One DICTIONARY, so functions in rotation_functions.py can change it (they can't change the main file's names).
#
# THIRD PERSON: this used to be called "camera", because the camera WAS you. Now there are TWO dictionaries:
#   player - where YOUR BODY is and which way it faces. Walking, jumping, boxes, being shot, turrets aiming
#            at you, gems, the mini-map: ALL of these read player.
#   camera - where the picture is drawn FROM (further down). Only to_camera() reads it.
# In first person the camera sits on your eye (camera = player). In third person it sits behind you.
player = {
    "x": -7.8,      # where YOU stand, in WORLD coordinates: the lower-left corner
    "y": 0,         # your eye height (not shown on the map)
    "z": -3.2,      #   (right by the grid's corner at x = -8, z = -3)
    "turn": -30,    # which way you face, in degrees. 0 = facing +z (up the map). -30 shows as "Facing: 30°"
    "tip": -1,      # looking up / down, in degrees. 0 = level, + = down, - = up. -1 shows as "Tilt: 1°"
    "vy": 0,        # your up / down speed: + = rising, - = falling
}

TURN_STEP = 1         # degrees per frame that the I J K L U O keys turn every thing by hand
TURN_SPEED = 1.5      # degrees per frame (not used at the moment: you turn with the mouse, MOUSE_SPEED)
TIP_LIMIT_DOWN = 60   # degrees: how far you can look DOWN at the floor
TIP_LIMIT_UP = 85     # degrees: how far you can look UP at the ceiling (keep under 90: past it the view flips over)
TIP_LIMIT_UP_THIRD = 60   # ...in THIRD PERSON: any steeper and the floor pushes the camera down beside your tank,
                          #   into it (the camera is held 0.2 above the floor, behind a pivot 0.5 over your eye)
STAND_Y = 0           # your eye height when standing: 1 above the floor (FLOOR_Y is -1)
JUMP_SPEED = 0.15     # the upward speed a jump starts with (SPACE), in world units per frame
GRAVITY = 0.004       # taken off player["vy"] every frame, so you slow, stop, then fall
                      # (halved from 0.008: twice as high AND twice as long a jump)

MOVE_SPEED = 0.05     # how far you walk in ONE frame (W A S D), in world units


# ================================ THE CAMERA (third person) ================================
# Where the picture is drawn FROM. update_camera() (rotation_functions.py) fills it in EVERY frame, from player:
#   first person: the camera is ON your eye          -> camera x, y, z = player x, y, z
#   third person: the camera is CAMERA_BACK behind   -> on the line you are AIMING along, but backwards
# It always faces the SAME way as you (same turn, same tip), so the crosshair still points where bullets go.
# The numbers here are only a starting point: update_camera() overwrites them before anything is drawn.
camera = {
    "x": 0,         # WORLD coordinates of the camera's eye
    "y": 0,
    "z": 0,
    "turn": 0,      # degrees: the same as player["turn"] (+ = turned LEFT)
    "tip": 0,       # degrees: the same as player["tip"] (+ = looking DOWN)
}
view = {"third_person": True,    # V key flips it.
        "distance": 3.0}          # how far BEHIND your eye the third-person camera is: the SCROLL WHEEL changes it
                                #   (starts at CAMERA_BACK; CAMERA_NEAREST to CAMERA_FURTHEST)
                                #   view is a DICTIONARY (not a plain True), so the game loop can change it
                                #   and rotation_functions.py sees the change (see "import *" in CLAUDE.md)

CAMERA_BACK = 3.0     # world units from your EYE back to the camera. Why 3? Your tank is 1.16 long at
                      #   AVATAR_SIZE 0.4, so 3 back shows the whole tank with room in front of it to aim.
                      #   Bigger = you look smaller on screen (6 = half the size); smaller = the tank fills more.
CAMERA_NEAREST = 1.5      # SCROLL WHEEL: the closest the camera comes (up: closer)
CAMERA_FURTHEST = 8.0     # ...and the furthest it goes (down: further)
CAMERA_SCROLL_STEP = 0.5  # ...this much per click of the wheel
CAMERA_PIVOT_UP = 0.5     # THIRD PERSON: the camera swings round a PIVOT this far ABOVE your eye - just over
                          #   your tank. The tank then sits BELOW the crosshair on screen instead of on it, and
                          #   when the camera slides all the way in (looking steeply up or down) it stops at the
                          #   pivot, ABOVE the tank - never inside it.
CAMERA_FLOOR_GAP = 0.2     # Looking UP swings the camera DOWN behind you: keep it at least 0.2 ABOVE the floor
                           #   (so never under (FLOOR_Y + 0.2) = (-1 + 0.2) = -0.8), or you'd see the floor from underneath.
CAMERA_CEILING_GAP = 0.2   # ...and at least 0.2 UNDER the ceiling (the world box's top), for the same reason.

# ---- YOUR AVATAR: the tank you drive in third person ----
# A tank built from the "tank" design (rotation_levels.py): a hull, its turret and its radar.
# It is NOT in the things list on purpose: nothing collides with it, shoots it, or counts it for clearing
# the level. You still get hit the same way as before (bullets near your EYE, see YOUR_HIT_RADIUS).
# update_avatar() moves it to where you stand every frame; add_thing_faces() draws it with everything else.
AVATAR_SIZE = 0.4     # the tank's size. The hull model is 2.2 wide, 2.9 long and its base is 1 below its centre,
                      #   so at 0.4 it is (2.2 * 0.4) = 0.88 wide, (2.9 * 0.4) = 1.16 long, and its centre sits
                      #   0.4 above your feet. (Your body for BOXES is still 0.5 wide: YOUR_BODY_RADIUS 0.25.)
avatar = []           # [hull, turret, radar] once build_avatar() has run. Changed IN PLACE (avatar[:] = ...).


# ================================ SPARKS ================================
# A burst of particles where two things bump (and bigger bursts when a shape breaks).
particles = []            # every live spark: {"position", "velocity", "life", "colour"} - filled while the game runs
SPARK_COUNT = 14          # sparks per bump
SPARK_SPEED = 0.06        # fastest a spark flies out (world units per frame)
SPARK_LIFE = 30           # frames a spark lasts (half a second at 60 FPS)
SPARK_GRAVITY = 0.002     # taken off a spark's up / down speed every frame, so they arc down
SPARK_SIZE = 0.04         # a spark's radius in world units, when it's brand new


# ================================ BULLETS ================================
# YOUR bullets: a tiny solid gold cube per left click, added to THINGS while the game runs.
BULLET_SPEED = 0.4        # world units per frame (fast: 24 units a second at 60 FPS)
BULLET_RANGE = 1000       # how far a bullet flies before it's removed: very long, the WORLD BOX stops it first
BULLET_SIZE = 0.05        # a cube of size 0.05 is 0.1 across
BULLET_MARGIN = 0         # bullets stop this far OUTSIDE the world box: 0 = right AT the walls, floor and ceiling
                          #   (with a puff of sparks). Every bullet - yours, a tank's or a dropper's.
BULLET_HIT_RADIUS = 0.2   # world units: how close a bullet has to get to HIT something. Bigger than the bullet
                          #   looks (0.1 across), so shots that clip a shape's corner still count, and a fast
                          #   bullet can't jump right over a TINY shape between two frames.

# The bullet MODEL: the cube's points and faces, but its own, bigger collision sphere (in model units:
# BULLET_HIT_RADIUS / BULLET_SIZE, because a thing's spheres are scaled by its size like its corners).
# Tank bullets use it too.
bullet_model = {"points": cube_points, "edges": cube_edges, "faces": cube_faces,
                "collision_spheres": [((0, 0, 0), BULLET_HIT_RADIUS / BULLET_SIZE)]}


# ---- TANK GUNS: turrets fire bullets (in their own colours) at you when they're pointing your way ----
TANK_CONE = 8             # degrees either side of straight ahead: point within this of you = "I see you"
TANK_COOLDOWN = 90        # frames a turret rests after a volley (1.5 seconds at 60 FPS)
TANK_VOLLEY = 3           # shots in one volley
TANK_VOLLEY_GAP = 8       # frames between the shots in a volley
TANK_BULLET_SPEED = 0.15  # world units per frame: slower than yours, so you can dodge
# Bullets take the SHOOTER's colour and palette: a tank's turret (its tank's colours), a shape, or you (gold).
YOUR_HIT_RADIUS = 0.3     # a tank bullet this close to your eye counts as hitting YOU
YOUR_BODY_RADIUS = 0.25   # BOXES: how close your body can get to a box's side (see you_hit_a_box)
BUMP_GRACE = 45           # THINGS: frames after a moving thing hits you before one can hurt you again (0.75 s)
STEP_UP = 0.3             # BOXES: a box top this far above your feet (or less) you just WALK up onto, like a
                          #   step. Anything taller blocks you (jump onto it). Sandbags are 0.4: jump them.
# A tiny GOLD square on the floor under WORLD x 0, z 0, added to EVERY level by load_level() (0.2 across).
ORIGIN_MARK = ([(-0.1, -0.1), (0.1, -0.1), (0.1, 0.1), (-0.1, 0.1)], (255, 215, 0))
SHOW_YOUR_SHADOW = True   # TEST: a ring on the floor under you, YOUR_HIT_RADIUS wide (look down to see it)

# ---- A TANK's GUN: the DEFAULTS. A tank in a level can change any of these in its own "gun": {...} ----
#   "mode"         - how the turret turns:
#                    "SPIN"      round and round, all 360 degrees (it fires when it happens to point at you)
#                    "OSCILLATE" sweeps back and forth between centre - range and centre + range (a cone)
#                    "TRACK"     turns towards YOU and locks on (at most turret_spin degrees a frame)
#                    "DOWN"      never turns or aims: fires STRAIGHT DOWN from the thing's lowest point, every
#                                time it's cooled down.
#                    "TARGET"    never turns, but fires STRAIGHT AT YOU from the edge of the thing nearest you,
#                                every time it's cooled down.
#                    DOWN and TARGET are the only modes a SHAPE can have (a shape has no turret to turn).
#                    (Any thing can have a gun: a tank's goes on its turret, a shape's on the shape itself.
#                     All modes share the FIRING settings: cooldown, volley, volley_gap, bullet_speed.)
#   "turret_spin"  - degrees per frame: how fast it spins (SPIN), sweeps (OSCILLATE) or turns to follow you (TRACK).
#                    None (SPIN only) = keep the spin the design or the level's "children" gave it.
#   "range"        - OSCILLATE: degrees either side of "centre" it sweeps
#   "centre"       - OSCILLATE: the middle of the sweep, in degrees, relative to the hull's front (0 = straight ahead)
#   "cone", "cooldown", "volley", "volley_gap", "bullet_speed" - as the TANK_ settings above, for this tank only
#   "bullet_colour", "bullet_palette" - its BULLETS' outline colour and face palette. None = the shooter's own
#                    colours (a lava dripper with black faces can still drip SUNSET bullets).
#   "start_angle"  - where the turret points when the level starts: degrees relative to the hull's front, or "you"
#                    = straight at where you start (so it fires straight away). None = straight ahead (OSCILLATE:
#                    the middle of its sweep).
GUN_DEFAULTS = {
    "start_angle": None,
    "mode": "SPIN",
    "turret_spin": None,
    "range": 90,
    "centre": 0,
    "cone": TANK_CONE,
    "cooldown": TANK_COOLDOWN,
    "volley": TANK_VOLLEY,
    "volley_gap": TANK_VOLLEY_GAP,
    "bullet_speed": TANK_BULLET_SPEED,
    "bullet_colour": None,
    "bullet_palette": None,
}
GUN_MODES = ("SPIN", "OSCILLATE", "TRACK", "DOWN", "TARGET")
SHAPE_GUN_MODES = ("DOWN", "TARGET")    # the modes that need no turret: they never turn, and fire every cooldown
you = {"hits_taken": 0, "hurt": 0,   # how many times you've been hit, and frames left of the flash
       "hurt_colour": (255, 0, 0),   # the flash's colour: what hit you (a bullet's, or the lava's / ice's)
       "lava_timer": 0,              # frames until standing in lava hurts you again (0 = straight away)
       "outside_timer": 0,           # frames until being OUTSIDE the play grid hurts you again (0 = straight away)
       "frozen": 0,                  # frames left FROZEN by ice (0 = free to move)
       "freeze_grace": 0,            # frames left when ice can't freeze you again
       "bump_grace": 0}              # frames left before a moving THING can hurt you again


# ================================ CROSSHAIR ================================
# A gap cross + dot in the middle of the screen: where your bullets go.
CROSSHAIR_GAP = 6         # pixels from the centre to where each arm starts
CROSSHAIR_LENGTH = 10     # pixels long, each arm
CROSSHAIR_KICK = 10       # extra gap, in pixels, the moment you fire: the arms jump out, then spring back
CROSSHAIR_HIT_FRAMES = 10 # how many frames the red X "hit marker" shows after a bullet hits
CROSSHAIR_COLOUR = (255, 255, 255)
HIT_MARKER_COLOUR = (255, 70, 70)
# ---- LEVEL TITLE: the level's name and intro as it starts; then the intro fades and the name rises to the top ----
BANNER_HOLD = 120         # frames the name and intro stay in the middle (2 seconds at 60 FPS)
BANNER_MOVE = 60          # frames to move them BOTH up to the top (1 second)
BANNER_INTRO_HOLD = 300   # frames the intro then stays at the top, under the name (5 seconds)
BANNER_FADE = 60          # frames for the intro to fade away (1 second). The name stays for the whole level.
BANNER_COLOUR = (255, 215, 0)          # the name: gold
BANNER_INTRO_COLOUR = BANNER_COLOUR    # the intro line: the same gold as the name (both have a black shadow)
level_banner = {"name": "", "intro": "", "frame": 0}   # what's showing now: set by load_level(), frame counts up

# ---- LEVEL COMPLETED: when every shape is destroyed (and every GEM collected), a message shows, then the NEXT level loads ----
LEVEL_COMPLETE_FRAMES = 180   # frames the "Level X completed!" message shows before the next level (3 seconds)
TEST_LEVELS = ()           # levels that aren't part of the normal 1, 2, 3 ... order (finishing one ends there)
level_progress = {"number": None, "cleared_frames": None,    # this level's number, and frames since it was cleared
                  "frames": 0,                              # frames PLAYED on this level (stops when cleared): the LEVEL TIME
                  "gems_total": 0, "gems_collected": 0,     # GEMS: how many this level has, and how many you've got
                  "hits_total": 0}                          # KILL: hits it took to clear the level at the START (0 = not worked out yet)
DEFAULT_TARGET_TIME = 120     # seconds: a level's TARGET TIME if it doesn't give its own "target_time"
                                                            #   (None = not cleared yet)

crosshair = {"kick": 0, "hit": 0}   # what it's doing right now. A DICTIONARY, so functions can change it
                                    # without needing 'global' (changing what's inside it, not the name)


# ================================ VIEW ================================
NEAR = 0.1            # anything closer than this, measured from YOU, is not drawn
MOUSE_SPEED = 0.2     # degrees of turn per pixel the mouse moves


# ================================ THE FLOOR ================================
FLOOR_Y = -1                  # the floor's height: the bottom of a full-size cube at y = 0
                              # (every level's "world" min y should be this; the grid's size comes from the level)
GRID_COLOUR = (40, 90, 70)    # dim green: the floor is background, so it shouldn't stand out
# This level's look: set by load_level() from the level's optional settings (a DICT, changed in place,
# so every file sees the new level's values).
level_look = {"grid_colour": GRID_COLOUR,
              "box_colour": GRID_COLOUR}   # the room's OUTER box and the map's play area: the grid colour, BRIGHTER
BOX_BRIGHTER = 1.6            # the outer box is the grid colour times this (capped at 255): it stands out a little   # EVERY grid's colour: floor, walls (G) and mini-map (a level's "grid_colour", or GRID_COLOUR)
WALL_GRID_STEP = 1                  # world units between the grid lines on the WALLS and CEILING (G key: on / off). 1 = the same as the floor
                                    #   (the 4 corner posts up to the ceiling, and the ceiling's 4 edges)


# ---- FLOOR SHAPES: flat polygons painted ON the floor (not things: no sorting, no collisions) ----
# Each one: ([corners as (x, z)], colour), in WORLD units on the floor (y is always FLOOR_Y).
# Corners go ROUND the shape in order. Drawn in list order, so a later shape is painted on top.
FLOOR_SHAPES = []     # filled by load_level() from the level's "floor_shapes" (each one a DECAL: see DECAL_TYPES)

# ---- DECAL TYPES: what each KIND of floor shape is, and what it DOES (like DESIGNS do for things) ----
# A level places a decal by its "type" - see "floor_shapes" in rotation_levels.py. The old style, a plain
# (corners, colour) pair, is still "paint".
#   "colour" - its colour (None = the level gives it one)
#   "hurts"  - True = standing on it (feet on the floor) counts as being HIT, every LAVA_HURT_FRAMES frames
#   "glow"   - True = its brightness slowly pulses up and down (every DECAL_GLOW_FRAMES frames)
#   "freezes" - True = stepping on it (feet on the floor) FREEZES you for FREEZE_FRAMES: you can't walk or jump
#              (you can still look and shoot). Then FREEZE_GRACE frames when it can't freeze you again.
DECAL_TYPES = {
    # "slows": how fast you can WALK while you stand on it (1 = normal, 0.3 = under a third of your speed)
    "paint":   {"colour": None,            "hurts": False, "glow": False, "freezes": False, "slows": 1},     # just a mark
    "lava":    {"colour": (255, 70, 20),   "hurts": True,  "glow": True,  "freezes": False, "slows": 1},     # jump over it!
    "ice":     {"colour": (170, 225, 255), "hurts": True,  "glow": True,  "freezes": True,  "slows": 1},     # it freezes AND hurts you!
    "slime":   {"colour": (120, 220, 50),  "hurts": True,  "glow": True,  "freezes": False, "slows": 0.6},   # sticky POISON: hurts, slows
    "custard": {"colour": (245, 205, 100), "hurts": False, "glow": False, "freezes": False, "slows": 0.3},   # THICK: no harm, but SO slow
}
FREEZE_FRAMES = 60        # frames ice freezes you for (1 second): long enough for a tank to lock on
FREEZE_GRACE = 60         # frames after thawing when ice can't freeze you again (so you can walk off it)
FREEZE_COLOUR = (120, 200, 255)   # the icy border round the screen while you're frozen
LAVA_HURT_FRAMES = 30     # while you stand in lava: one hit as you step in, then one every 30 frames (half a second)
OUTSIDE_HURT_FRAMES = 30  # while you're OUTSIDE the play grid (the world box in x and z): the same, one hit every 30 frames
OUTSIDE_COLOUR = (200, 0, 255)   # the flash when being outside hurts you: purple, so you can tell it from lava
DECAL_GLOW_FRAMES = 90    # frames for one slow pulse of a glowing decal (1.5 seconds)


# ---- BOXES: static structures, NOT things. Each is a box lined up with x, y and z (it never turns),
# given by two opposite corners in WORLD units: "min" = smallest x, y, z and "max" = biggest x, y, z.
# Their 8 corners and 6 face colours are worked out ONCE at start-up (prepare_boxes), because they never change.
#   "colour"  - the outline colour (and its rectangle on the mini-map)
#   "palette" - the colours for its 6 faces (see PALETTES)
BOXES = []            # filled by load_level() from the level's "boxes"

SHOW_PIECES = False           # TEST: True = every 1-unit floor piece gets its own colour (slow: see draw_floor_line)


# ---- The WORLD BOX: every thing's CENTRE bounces inside it ----
#   x: the floor's left and right edges,  y: floor to ceiling,  z: the floor's near and far edges
# (Only the centre: a big shape can hang over the edges by up to its own size.)
# Set by load_level() from the level's "world" - LISTS, changed in place, so every file sees the new size.
# The floor grid is drawn across the same x and z.
WORLD_MIN = [0, FLOOR_Y, 0]     # smallest x, y, z
WORLD_MAX = [0, 0, 0]           # biggest  x, y, z (y = the ceiling: an invisible limit, nothing draws it)

# THE ROPE: a bullet from the RIGHT mouse button, tied to you by a line
PLAYER_COLOUR = (240, 240, 255)      # YOUR colour: your bullets and the rope (white - gold is for gems)
PALETTE_PLAYER = [PLAYER_COLOUR]     # every face of your bullets that colour (the lighting still shades each side)
PALETTE_AVATAR = [(240, 240, 255), (200, 210, 230), (170, 180, 205), (220, 225, 245)]   # YOUR TANK: whites to blue-grey
ROPE_HAND = (0.2, -0.25, 0.3)        # where the line leaves you, from your eye: a bit right, down and forward
rope = {"bullet": None,              # the rope's bullet while it's out (None = no rope)
        "start": (0, 0, 0),          # where it was thrown from (to measure how far it has flown)
        "frames": 0}                 # frames left before it's gone (counts down from ROPE_LIFE)
ROPE_RANGE = 10                      # the rope flies this far (world units); hit nothing by then and it's gone
ROPE_LIFE = 300                      # frames from throwing until the rope is gone, hooked or not (5 seconds)
lock_on = {"degrees": 2}             # LOCK-ON: while the rope is hooked on a THING (not a gem), your bullets turn
                                     #   up to this many degrees a frame towards its centre (0 = off). A dict, so a
                                     #   settings tab can change it later.
ROPE_GEM_PULL = 0.05                 # a GEM on the rope is reeled in towards you this far each frame (3 units a second)


# ================================ GEMS: little gold diamonds to COLLECT ================================
# GEMS are THINGS with "gem": True, so they're drawn, spun, moved and shown on the mini-map like any thing.
# What's DIFFERENT about a gem: it never blocks you, never hurts you, bullets fly through it, it has no health,
# and it doesn't bounce off other things. Walk into it and it's COLLECTED: gold sparks and a note of the scale.
# A level needs ALL its gems collected (as well as every shape gone) before it's completed.
# They're scattered at RANDOM by place_gems() each time a level loads, after its boxes and floor shapes are in.
# A level can set its own number: "gems": 12 (or 0 for none) - see LEVELS in rotation_levels.py.
# Gems can be given a velocity later: they'll move and bounce off the world box and boxes like other things.
GEMS_PER_LEVEL = 8            # how many gems a level gets, unless it gives its own "gems"
GEM_ACROSS = 0.3              # world units across, tip to tip (a TINY shape is 0.5)
GEM_HOVER = 0.5               # the LOWEST a gem's centre floats over the floor: knee-high, so walking into it collects it
GEM_HIGHEST = 0.8            # the HIGHEST: this much of the way from the floor to the CEILING (0.8 = 80%), so the
                              #   high ones need the ROPE. Each gem gets a random height in between.
GEM_BOB = 0.25                # how far it bobs up and down from there
GEM_BOB_FRAMES = 120          # frames for one bob, up and back down (2 seconds)
GEM_SPIN = (2, 0, 0)          # (turn, tilt, spin) degrees per frame: turns slowly round its upright axis
GEM_COLOUR = (255, 240, 150)  # its outline (and its dot on the mini-map): pale gold
GEM_PALETTE = PALETTE_GOLD    # its faces
GEM_PICKUP_EXTRA = 0.1        # world units: a little extra reach, so you don't have to hit it dead on
# Where a gem may go (so every one can be reached):
GEM_WALL_GAP = 1.0            # at least this far in from the world box's walls
GEM_BOX_GAP = 0.6             # at least this far from any box (seen from above)
GEM_THING_GAP = 0.8           # at least this far from the edge of any thing (seen from above)
GEM_START_GAP = 2.0           # at least this far from where you start
GEM_APART = 2.0               # at least this far from each other
GEM_TRIES = 3000              # random spots tried per level before giving up (then it uses fewer, with a warning)
# Each gem you collect plays the NEXT note of the C major scale: do re mi fa so la ti do (in Hz).
# With more than 8 gems, the scale starts again from the bottom.
GEM_NOTES = [523.25, 587.33, 659.25, 698.46, 783.99, 880.00, 987.77, 1046.50]
