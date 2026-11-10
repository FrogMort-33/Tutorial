# ======================================================================
# LESSON 9 - STEP 2: SHIPS FROM A FILE
# ----------------------------------------------------------------------
# Goal: the game's pickups are no longer typed-in cubes. They are
# ships, read from the text file ship.obj when the game starts.
#
# This starts from Lesson 8's finished game (step3_clipped_hunt.py):
# Cube Hunt with 4 stone rocks and faces clipped at the NEAR wall.
# The game itself does not change at all: same field, same clock,
# same collecting. Only WHERE THE SHAPE COMES FROM changes.
#
# What is new:
#
#   1. load_obj("ship.obj")  (lesson Parts 2 to 4)
#        Reads the file and builds the same {"points", "faces"}
#        dictionary Lesson 5 typed in by hand, making five changes
#        on the way in:
#          CHANGE 1  corner numbers count from 0, not 1   (minus 1)
#          CHANGE 2  z = -z, and each face's corners reversed
#          CHANGE 3  each face's pointer from cross()
#          CHANGE 4  centred on (0, 0, 0), biggest side 2 units
#          CHANGE 5  skip other lines; "7/2/9" -> 7
#
#   2. cross(arrow_a, arrow_b)  (lesson Part 4)
#        The one new piece of maths: an arrow straight out of a face.
#
#   3. The pickups use ship_model instead of cube_model, and the
#        mini-map draws each ship's nose and two wing tips.
#
# Controls:  LEFT / RIGHT = turn,   UP / DOWN = look up / down
#            W / S = fly forward / back (the way you LOOK)
#            A / D = slide left / right,   Q / E = straight down / up
#            R = play again (after TIME UP)
#            G = floor grid on / off,   L = light on / off
# Run:  python step2_ship_from_file.py
#       (ship.obj must be in the same folder as this script)
# ======================================================================

import math
import random                 # (Lesson 7) for random.uniform
import os                     # NEW: to find the .obj files next to this script
import pygame

pygame.init()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 9, step 2 - ships from a file")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)
big_font = pygame.font.SysFont(None, 96)    # (Lesson 7) for "TIME UP"

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
PINK = (255, 105, 200)        # the colour we use for YOU (the camera)
MAP_BACK = (25, 30, 36)       # dark grey-blue behind the mini-map
GRID_COLOUR = (40, 90, 70)    # (Lesson 5) dim green for the floor lines
WALL_RED = (235, 80, 80)      # (Lesson 7) the wall square on the mini-map
SUN_GOLD = (250, 200, 70)     # (Lesson 7) the colour of every pickup
STONE = (150, 150, 160)       # (Lesson 8): the colour of every rock

# ---- One colour for each face direction (from Lesson 3) ---------------
RED = (235, 80, 80)          # front (-z)
PURPLE = (160, 100, 230)     # back  (+z)
BLUE = (70, 150, 255)        # left  (-x)
GREEN = (70, 210, 120)       # right (+x)
GOLD = (245, 200, 60)        # top   (+y)
ORANGE = (245, 140, 50)      # bottom (-y)

CENTRE_X = (WIDTH / 2)            # (800 / 2) = 400
CENTRE_Y = (HEIGHT / 2)           # (600 / 2) = 300
FOCAL = 400


# ======================================================================
# MODELS (from Lesson 5, unchanged)
# ======================================================================
cube_points = [
    (-1, -1, -1),   # 0  bottom-left-front
    ( 1, -1, -1),   # 1  bottom-right-front
    ( 1, -1,  1),   # 2  bottom-right-back
    (-1, -1,  1),   # 3  bottom-left-back
    (-1,  1, -1),   # 4  top-left-front
    ( 1,  1, -1),   # 5  top-right-front
    ( 1,  1,  1),   # 6  top-right-back
    (-1,  1,  1),   # 7  top-left-back
]
# (corners clockwise from outside,  colour,  pointer)
cube_faces = [
    ((4, 5, 1, 0), RED,    ( 0,  0, -1)),   # front
    ((6, 7, 3, 2), PURPLE, ( 0,  0,  1)),   # back
    ((7, 4, 0, 3), BLUE,   (-1,  0,  0)),   # left
    ((5, 6, 2, 1), GREEN,  ( 1,  0,  0)),   # right
    ((7, 6, 5, 4), GOLD,   ( 0,  1,  0)),   # top
    ((2, 3, 0, 1), ORANGE, ( 0, -1,  0)),   # bottom
]
cube_model = {"points": cube_points, "faces": cube_faces}
# (Lesson 9) the rocks still use cube_model; the pickups do not.


# ======================================================================
# NEW: LOADING MODELS FROM .obj FILES (Lesson 9)
# ======================================================================
# An .obj file is plain text. The two kinds of line we use:
#     v x y z         one corner        e.g.  v 0.0 0.6 -1.0
#     f a b c ...     one face          e.g.  f 1 4 2
# load_obj() reads them and makes the SAME model dictionary that
# Lesson 5 typed in by hand:
#     {"points": [...], "faces": [ (corners, colour, pointer), ... ]}
# so the rest of the program can't tell a loaded model from cube_model.
#
# On the way in it makes FIVE changes (lesson Part 3):
#   CHANGE 1  corner numbers: .obj counts from 1, Python from 0 -> minus 1
#   CHANGE 2  .obj's +z points AT you, ours points AWAY:
#               z = -z on every corner, and because that is a mirror,
#               each face's corner list is turned round (.reverse())
#               so it stays clockwise from outside (Lesson 3's rule)
#   CHANGE 3  no pointers in the file: work each one out with cross()
#   CHANGE 4  every file uses its own size: centre the model on
#               (0, 0, 0) and make its biggest side 2 units, like the cube
#   CHANGE 5  skip every line that is not "v" or "f", and in a face
#               keep only the number before the first "/"

# Where are the .obj files? In the same folder as this script.
# __file__ = this script's full path; os.path.dirname() = its folder.
CODE_FOLDER = os.path.dirname(os.path.abspath(__file__))


def cross(arrow_a, arrow_b):
    """NEW: the CROSS PRODUCT of two arrows (lesson Part 4).

    Give it two arrows that lie flat ON a face, and it gives back an
    arrow that sticks straight OUT of the face: the face's pointer.

    Each part uses the OTHER two parts of the arrows:
        x = (a_y * b_z) - (a_z * b_y)
        y = (a_z * b_x) - (a_x * b_z)
        z = (a_x * b_y) - (a_y * b_x)   <- Lesson 3's clock test!

    Worked example (lesson Part 4), the ship's top-left face:
        arrow_a = (1, 0.4, 0),  arrow_b = (1, 0, -2)
        x = (0.4 * -2) - (0 * 0)  = -0.8
        y = (0 * 1)    - (1 * -2) =  2
        z = (1 * 0)    - (0.4 * 1) = -0.4      -> (-0.8, 2, -0.4)
    """
    a_x, a_y, a_z = arrow_a
    b_x, b_y, b_z = arrow_b
    out_x = ( (a_y * b_z) - (a_z * b_y) )
    out_y = ( (a_z * b_x) - (a_x * b_z) )
    out_z = ( (a_x * b_y) - (a_y * b_x) )
    return (out_x, out_y, out_z)


def face_pointer(corners, points):
    """NEW (CHANGE 3): the 1-unit pointer straight out of one face.

    Uses the face's first 3 corners, a, b and c:
        arrow_a = b - a,   arrow_b = c - a      (two arrows along the face)
        pointer = cross(arrow_a, arrow_b)        (sticks out of the face)
    then shrinks the pointer to 1 unit long, because Lesson 3's light
    needs 1-unit pointers (a dot of 1 = full brightness).

    Returns None for a face with no area (all corners in a line):
    its pointer has length 0, and we can't divide by 0.
    """
    a_x, a_y, a_z = points[corners[0]]
    b_x, b_y, b_z = points[corners[1]]
    c_x, c_y, c_z = points[corners[2]]
    arrow_a = ( (b_x - a_x), (b_y - a_y), (b_z - a_z) )
    arrow_b = ( (c_x - a_x), (c_y - a_y), (c_z - a_z) )
    p_x, p_y, p_z = cross(arrow_a, arrow_b)
    # How long is it? Lesson 7's Pythagoras, done on one arrow.
    length = math.sqrt( (p_x * p_x) + (p_y * p_y) + (p_z * p_z) )
    if length == 0:
        return None
    return ( (p_x / length), (p_y / length), (p_z / length) )


def centre_and_size(raw_points):
    """NEW (CHANGE 4): move the model so its middle is SHAPE (0, 0, 0),
    and scale it so its biggest side is 2 units (the cube is 2 wide).

    Worked example (lesson Part 3), the teapot:
        x from -3 to 3.434   ->  middle 0.217,  width 6.434
        y from  0 to 3.15    ->  middle 1.575,  height 3.15
        z from -2 to 2       ->  middle 0,      depth 4
        biggest side = 6.434,  scale = (2 / 6.434) = 0.311
    """
    # Start the smallest and biggest at the first corner, then let
    # every other corner push them out (like Lesson 7's "nearest").
    min_x, min_y, min_z = raw_points[0]
    max_x, max_y, max_z = raw_points[0]
    for x, y, z in raw_points:
        if x < min_x:
            min_x = x
        if x > max_x:
            max_x = x
        if y < min_y:
            min_y = y
        if y > max_y:
            max_y = y
        if z < min_z:
            min_z = z
        if z > max_z:
            max_z = z

    # The middle of each side is halfway between its two ends.
    middle_x = ( (min_x + max_x) / 2 )
    middle_y = ( (min_y + max_y) / 2 )
    middle_z = ( (min_z + max_z) / 2 )

    # The biggest of the three sides decides the scale.
    biggest = max( (max_x - min_x), (max_y - min_y), (max_z - min_z) )
    scale = (2 / biggest)

    # Subtract the middle (so it moves to 0, 0, 0), then scale.
    points = []
    for x, y, z in raw_points:
        points.append( ( ((x - middle_x) * scale),
                         ((y - middle_y) * scale),
                         ((z - middle_z) * scale) ) )
    return points


def load_obj(file_name):
    """NEW: read an .obj file and return a Lesson 5 model dictionary:
        {"points": [(x, y, z), ...],
         "faces":  [(corners, colour, pointer), ...]}

    Every face gets WHITE as its colour: the game paints each thing in
    its own thing["colour"] anyway (Lesson 5).
    """
    raw_points = []
    file_faces = []
    with open(os.path.join(CODE_FOLDER, file_name)) as file:
        for line in file:
            parts = line.split()        # "v 0 0.6 -1" -> ["v", "0", "0.6", "-1"]
            if len(parts) == 0:
                continue                # empty line

            if parts[0] == "v":
                x = float(parts[1])
                y = float(parts[2])
                z = float(parts[3])
                # CHANGE 2 (first half): flip z, so +z points away.
                raw_points.append( (x, y, (-z)) )

            elif parts[0] == "f":
                corners = []
                for word in parts[1:]:
                    # CHANGE 5: "739/1/12" -> "739".  .split("/") cuts
                    # at each "/", and [0] keeps the first piece.
                    # "4" has no "/", so it stays "4".
                    number_text = word.split("/")[0]
                    # CHANGE 1: count from 0, not 1.
                    corners.append( (int(number_text) - 1) )
                # CHANGE 2 (second half): the z flip was a mirror, and a
                # mirror turns clockwise into anticlockwise. Turning the
                # list round puts it back to clockwise from outside.
                #     [0, 3, 1]  ->  [1, 3, 0]
                corners.reverse()
                file_faces.append(tuple(corners))

            # CHANGE 5: any other line ("#", "vn", "vt", "s", "o",
            # "usemtl" ...) falls through to here and is skipped.

    # CHANGE 4: centre the corners and make the model 2 units big.
    points = centre_and_size(raw_points)

    # CHANGE 3: one pointer per face, worked out from the corners.
    faces = []
    for corners in file_faces:
        pointer = face_pointer(corners, points)
        if pointer is None:
            continue                    # no area: nothing to draw
        faces.append( (corners, WHITE, pointer) )

    return {"points": points, "faces": faces}


# ---- NEW: the pickups' shape, read from ship.obj ----------------------
# 5 corners and 5 faces (4 triangles and a diamond at the back).
# After load_obj(), in SHAPE coordinates (lesson Part 3):
#   corner 0 = nose (0, 0, -1)          points at -z, towards you
#   corner 1 = left wing (-1, 0, 1),    corner 2 = right wing (1, 0, 1)
#   corner 3 = top fin (0, 0.4, 1),     corner 4 = bottom fin (0, -0.4, 1)
ship_model = load_obj("ship.obj")


# ======================================================================
# THE PLAYING FIELD (lesson Part 1)
# ======================================================================

# ---- (Lesson 7) the sizes of the field ------------------------------------
# FIELD = 10: new ships appear with x and z from -10 to 10, a 20 x 20
#   square. You fly 3 units a second, so edge to edge is
#   (20 / 3) = 6.7 seconds: some flying, but never boring.
# WALL = 12: you can't fly further than 12 from the centre, 2 more than
#   FIELD, so you can always fly round a ship at the edge.
FIELD = 10
WALL = 12

# ---- (Lesson 7) the floor (from Lesson 5), now as big as the walls --------
FLOOR_Y = -1
GRID_LEFT = (-WALL)       # -12
GRID_RIGHT = WALL         # 12
GRID_NEAR = (-WALL)       # -12
GRID_FAR = WALL           # 12

# ---- (Lesson 7) the pickups ------------------------------------------------
# PICKUP_SIZE = 0.5: Lesson 5's "size". Lesson 7's pickup cubes were 1
#   unit wide; the ship is loaded 2 units long (Lesson 9, CHANGE 4), so
#   size 0.5 makes it 1 unit long too: nose at -0.5, tail at 0.5.
#   1 unit 5 away is ((1 * 400) / 5) = 80 px; 20 away it is 20 px.
PICKUP_SIZE = 0.5

# (Lesson 7) pickup heights: their centres float from y = 0 to y = 2.
#   0 is your eye height at the start; the lowest ship's bottom fin is
#   then at (0 - (0.4 * 0.5)) = -0.2, above the floor (FLOOR_Y = -1).
PICKUP_LOW = 0
PICKUP_HIGH = 2

# (Lesson 7) the 8 spots the ships start at, in WORLD coordinates.
# The same every game, so you can learn a good route. Ship 0 at
# (3, 1, 5) is Lesson 7's worked example.
START_SPOTS = [
    (3, 1, 5),      # 0  ahead and to the right: the first one you see
    (-2, 0, 8),     # 1
    (0, 0, 10),     # 2  straight ahead, at the far edge
    (-6, 1, 3),     # 3
    (6, 0, -2),     # 4  behind you, to the right
    (-4, 2, -7),    # 5  behind you, up high
    (8, 0, 7),      # 6
    (2, 1, -9),     # 7  far behind you
]

# (Lesson 7) COLLECT_RADIUS = 1.0: you collect a ship when your eye is
#   1 unit or less from its CENTRE. (Lesson 7 chose 1.0 for a 1-unit
#   cube; a 1-unit ship is the same length, so 1.0 still fits.)
COLLECT_RADIUS = 1.0

# (Lesson 7) MIN_SPAWN_DISTANCE = 5: a new ship never appears closer than
#   5 to you, so it is at least (5 / 3) = 1.7 seconds of flying away.
MIN_SPAWN_DISTANCE = 5

# ---- (Lesson 8): ROCKS, big scenery cubes (lesson Part 1) -------------------
# ROCK_SIZE = 1.5: Lesson 5's "size", so a rock is (2 * 1.5) = 3 units
#   wide, 3 times a gold ship's length. Big enough that you can fly right up
#   beside one while most of it is still on the screen: its front face,
#   2.5 away, is ((3 * 400) / 2.5) = 480 px wide.
ROCK_SIZE = 1.5

# Each rock SITS on the floor: its centre is ROCK_SIZE above FLOOR_Y,
#   so centre y = (-1 + 1.5) = 0.5, bottom at -1, top at 2.
ROCK_Y = (FLOOR_Y + ROCK_SIZE)

# Where the 4 rocks are, in WORLD coordinates. Rock 0 is straight ahead
# of where you start: the lesson's worked example.
ROCK_SPOTS = [
    (0, ROCK_Y, 4),       # 0  straight ahead, its front face at z = 2.5
    (-5, ROCK_Y, -3),     # 1  behind you, to the left
    (5, ROCK_Y, 10),      # 2  far ahead, to the right
    (7, ROCK_Y, -7),      # 3  behind you, to the right
]

# ROCK_CLEARANCE = 3: a new gold ship must be at least 3 from every
#   rock's centre: 1.5 (half a rock) + 0.5 (half a gold ship) + 1 (your
#   COLLECT_RADIUS, so you can always reach it) = 3.
ROCK_CLEARANCE = ( (ROCK_SIZE + PICKUP_SIZE) + COLLECT_RADIUS )

# ---- (Lesson 7) how high and low you can fly (lesson Part 5) -----------------
# GROUND = -0.5: your eye stays half a unit above the floor (y = -1).
# CEILING = 4: two more than PICKUP_HIGH, so you can look down on every
#   ship but never fly off where none could be.
GROUND = (FLOOR_Y + 0.5)     # (-1 + 0.5) = -0.5
CEILING = 4

# ---- (Lesson 7) the clock (lesson Part 6) -------------------------------------
# 60 seconds: at 3 units a second that is (3 * 60) = 180 units of
# flying, enough for a good handful of ships, short enough to retry.
GAME_SECONDS = 60


def make_pickups():
    """(Lesson 7) build a fresh list of 8 pickup THINGS (Lesson 5's
    dictionaries), one at each START_SPOTS position.

    NEW: each one is now a small gold SHIP from ship.obj. Size 0.5
    makes it 1 unit long, nose to tail, the same as the old 1-unit
    cube. It spins slowly so it catches your eye: 1 degree a frame of
    turn = one turn in 6 seconds, and 0.5 of tip so it wobbles too.
    """
    pickups = []
    for spot in START_SPOTS:
        pickups.append({"model": ship_model, "position": spot,   # NEW: ship
                        "size": PICKUP_SIZE, "angles": [0, 0, 0],
                        "speeds": (0.5, 1, 0), "colour": SUN_GOLD,
                        "pickup": True})          # (Lesson 8)
    return pickups


def make_rocks():
    """(Lesson 8): build a list of 4 rock THINGS, one at each ROCK_SPOTS position.

    Same dictionary keys as a gold ship, with three differences:
    size 1.5, speeds (0, 0, 0) so they never spin, and "pickup": False
    so you can't collect them.
    """
    rocks = []
    for spot in ROCK_SPOTS:
        rocks.append({"model": cube_model, "position": spot,
                      "size": ROCK_SIZE, "angles": [0, 0, 0],
                      "speeds": (0, 0, 0), "colour": STONE,
                      "pickup": False})
    return rocks


def make_world():
    """(Lesson 8): the whole world = 8 gold ships + 4 rocks.

    "+" joins two lists into one longer list: (8 + 4) = 12 things.
    The gold ships come first, so things[0] is ship 0.
    """
    return (make_pickups() + make_rocks())


# "things" is Lesson 5's list of everything in the world.
# (Lesson 8): 8 gold ships AND 4 rocks.
things = make_world()

# ---- Where YOU are (from Lesson 4) ------------------------------------
cam_x = 0
cam_y = 0
cam_z = 0
cam_turn = 0        # degrees, positive = turned LEFT
cam_tip = 0         # degrees, positive = looking DOWN
TIP_LIMIT = 60
MOVE_SPEED = 0.05   # (0.05 * 60) = 3 units a second
TURN_SPEED = 1.5    # (1.5 * 60) = 90 degrees a second
NEAR = 0.1          # closer than this (CAMERA z) is not drawn

# ---- The light (from Lesson 3, unchanged) -----------------------------
LIGHT = (0.48, 0.6, -0.64)
AMBIENT = 0.2
use_light = True
show_grid = True
# (Lesson 8): K turns clipping on / off, so you can see the difference.
use_clipping = True

# ---- (Lesson 7) the score ------------------------------------------------
score = 0
# ---- (Lesson 7) the clock and the game's two states (lesson Part 6) ----------
best_score = 0                         # NOT reset by R
frames_left = (GAME_SECONDS * 60)      # (60 * 60) = 3600
game_over = False                      # False = PLAYING, True = TIME UP

# ---- The mini-map (lesson Part 1: resized for the whole field) ---------
MAP_LEFT = 630
MAP_TOP = 430
MAP_SIZE = 160
# (Lesson 7) the WORLD centre now sits in the MIDDLE of the box, because
# the field goes the same distance every way (-12 to 12).
MAP_CX = (MAP_LEFT + (MAP_SIZE / 2))    # (630 + 80) = 710
MAP_CY = (MAP_TOP + (MAP_SIZE / 2))     # (430 + 80) = 510
# (Lesson 7) 6 px per unit: the walls are 24 units across, and
# (24 * 6) = 144 px fits the 160 px box with 8 px to spare.
MAP_SCALE = 6


# ======================================================================
# MATRIX TOOLS (from Lesson 6, unchanged)
# ======================================================================

def matrix_times_point(matrix, point_3d):
    """Put one point through a matrix: each ROW dotted with the point."""
    row_0, row_1, row_2 = matrix
    new_x = dot(row_0, point_3d)
    new_y = dot(row_1, point_3d)
    new_z = dot(row_2, point_3d)
    return (new_x, new_y, new_z)


def tip_matrix(angle_degrees):
    """Lesson 2B's TIP as a grid. x is the skewer."""
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    return (
        (1, 0,     0         ),
        (0, cos_a, (-sin_a)  ),
        (0, sin_a, cos_a     ),
    )


def turn_matrix(angle_degrees):
    """Lesson 2's TURN as a grid. y is the skewer."""
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    return (
        (cos_a, 0, (-sin_a)),
        (0,     1, 0       ),
        (sin_a, 0, cos_a   ),
    )


def roll_matrix(angle_degrees):
    """Lesson 2B's ROLL as a grid. z is the skewer."""
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    return (
        (cos_a, (-sin_a), 0),
        (sin_a, cos_a,    0),
        (0,     0,        1),
    )


def column(matrix, column_number):
    """One COLUMN of a matrix = where that axis arrow lands."""
    row_0, row_1, row_2 = matrix
    return (row_0[column_number], row_1[column_number], row_2[column_number])


def combine(first, second):
    """ONE matrix that does 'first', then 'second' (Lesson 6)."""
    new_col_0 = matrix_times_point(second, column(first, 0))
    new_col_1 = matrix_times_point(second, column(first, 1))
    new_col_2 = matrix_times_point(second, column(first, 2))
    return (
        (new_col_0[0], new_col_1[0], new_col_2[0]),
        (new_col_0[1], new_col_1[1], new_col_2[1]),
        (new_col_0[2], new_col_1[2], new_col_2[2]),
    )


def spin_matrix(angles):
    """A thing's whole spin as ONE matrix: tip, then turn, then roll."""
    tip_then_turn = combine(tip_matrix(angles[0]), turn_matrix(angles[1]))
    return combine(tip_then_turn, roll_matrix(angles[2]))


# ======================================================================
# THE 3D PIPELINE (Lessons 1 to 6, unchanged)
# ======================================================================

def to_world(shape_point, thing):
    """(Lesson 5) SHAPE -> WORLD: size, then spin, then place."""
    x, y, z = shape_point
    size = thing["size"]
    sized = ( (x * size), (y * size), (z * size) )
    spun = matrix_times_point(thing["matrix"], sized)
    pos_x, pos_y, pos_z = thing["position"]
    sx, sy, sz = spun
    return ( (sx + pos_x), (sy + pos_y), (sz + pos_z) )


def to_camera(world_point):
    """(Lessons 4 and 6) WORLD -> CAMERA: subtract you, then camera_matrix."""
    x, y, z = world_point
    moved = ( (x - cam_x), (y - cam_y), (z - cam_z) )
    return matrix_times_point(camera_matrix, moved)


def project(point_3d):
    """(Lesson 1) CAMERA -> SCREEN. Only call it with z >= NEAR."""
    x, y, z = point_3d
    screen_x = CENTRE_X + ( (x * FOCAL) / z )
    screen_y = CENTRE_Y - ( (y * FOCAL) / z )
    return (screen_x, screen_y)


def average_z(corners, camera_points):
    """(Lesson 3) how far away is this face? Uses CAMERA z."""
    total = 0
    for corner_number in corners:
        x, y, z = camera_points[corner_number]
        total = (total + z)
    return (total / len(corners))


def is_facing_you(face_points):
    """(Lesson 3) the clock test: True if clockwise on the screen."""
    a_x, a_y = face_points[0]
    b_x, b_y = face_points[1]
    c_x, c_y = face_points[2]
    arrow_a_x = (b_x - a_x)
    arrow_a_y = (b_y - a_y)
    arrow_b_x = (c_x - a_x)
    arrow_b_y = (c_y - a_y)
    cross = ( (arrow_a_x * arrow_b_y) - (arrow_a_y * arrow_b_x) )
    return (cross > 0)


def dot(arrow_1, arrow_2):
    """(Lesson 3) the dot product."""
    x1, y1, z1 = arrow_1
    x2, y2, z2 = arrow_2
    return ( (x1 * x2) + (y1 * y2) + (z1 * z2) )


def shade_colour(colour, pointer):
    """(Lesson 3) brighter when the face points at the light."""
    brightness = dot(pointer, LIGHT)
    if brightness < 0:
        brightness = 0
    shade = ( AMBIENT + ( (1 - AMBIENT) * brightness ) )
    red, green, blue = colour
    return ( round(red * shade), round(green * shade), round(blue * shade) )


def keep_under_360(angle):
    """Keep an angle between 0 and 360."""
    if angle >= 360:
        angle = (angle - 360)
    if angle < 0:
        angle = (angle + 360)
    return angle


def add_faces_of(thing, faces_to_draw):
    """(Lesson 5) work out every face of ONE thing and add the ones to
    paint to the shared list.

    (Lesson 8) each face is CLIPPED in CAMERA coordinates first,
    and only then projected. So we no longer project every corner up
    front: a face's cut points only exist once that face is clipped.
    """
    model = thing["model"]
    camera_points = []
    for p in model["points"]:
        world = to_world(p, thing)                     # WORLD
        camera_points.append(to_camera(world))         # CAMERA

    for corners, face_colour, pointer in model["faces"]:
        # (Lesson 8) this face's corners in CAMERA coordinates, clockwise.
        face_camera = []
        for corner_number in corners:
            face_camera.append(camera_points[corner_number])

        if use_clipping:
            # (Lesson 8) cut the face at the NEAR wall (lesson Part 3).
            face_camera = clip_face(face_camera)
            # Fewer than 3 corners left: nothing to paint.
            if len(face_camera) < 3:
                continue
        else:
            # Lesson 4's old rule, for comparing (K): any corner behind
            # the NEAR wall? Skip the whole face.
            too_close = False
            for camera in face_camera:
                if camera[2] < NEAR:
                    too_close = True
            if too_close:
                continue

        # Every corner left is now in front of NEAR, so project() is safe.
        face_points = []
        for camera in face_camera:
            face_points.append(project(camera))        # SCREEN
        # The clock test works on any number of corners (it only looks
        # at the first 3), and clipping keeps them clockwise.
        if not is_facing_you(face_points):
            continue
        distance = average_z(corners, camera_points)
        colour = thing["colour"]
        if use_light:
            spun_pointer = matrix_times_point(thing["matrix"], pointer)
            colour = shade_colour(colour, spun_pointer)
        faces_to_draw.append( (distance, face_points, colour) )


def draw_floor():
    """(Lesson 8): the floor grid as LONG lines, right across the field.

    25 lines running away from you (x = -12 to 12) and 25 lines running
    across (z = -12 to 12): (25 + 25) = 50 lines a frame. Lesson 5 had
    to cut them into 1-unit pieces, (25 * 24) * 2 = 1,200 of them, so
    that only the pieces behind you were lost. Clipping keeps the part
    of a long line in front of you, so the pieces are not needed.

    A long line is still exactly right on the screen: a straight line
    in 3D projects to a straight line on the screen, so its two ends
    are all we need (lesson Part 2).
    """
    for x in range(GRID_LEFT, (GRID_RIGHT + 1)):
        draw_floor_line( (x, FLOOR_Y, GRID_NEAR), (x, FLOOR_Y, GRID_FAR) )
    for z in range(GRID_NEAR, (GRID_FAR + 1)):
        draw_floor_line( (GRID_LEFT, FLOOR_Y, z), (GRID_RIGHT, FLOOR_Y, z) )


def draw_floor_line(world_start, world_end):
    """(Lesson 8): one long floor line, WORLD -> CAMERA -> clip -> SCREEN."""
    start = to_camera(world_start)
    end = to_camera(world_end)
    if use_clipping:
        clipped = clip_line(start, end)
        if clipped is None:              # both ends behind you
            return
        start, end = clipped
    else:
        # Lesson 4's old rule, for comparing (K): any end behind? skip.
        if (start[2] < NEAR) or (end[2] < NEAR):
            return
    pygame.draw.line(screen, GRID_COLOUR, project(start), project(end), 1)

# ======================================================================
# CLIPPING (Lesson 8)
# ======================================================================
# Everything here works in CAMERA coordinates: (0, 0, 0) is your eye,
# +x is right, +y is up, +z is straight ahead. The NEAR wall is the
# flat sheet z = NEAR (0.1) just in front of your eye.
#   "in"  = in front of the wall:  z >= NEAR   (safe to project)
#   "out" = behind the wall:       z <  NEAR   (must never be projected)

def cut_at_near(point_a, point_b):
    """(Lesson 8): the CAMERA point where the line from point_a to point_b
    crosses the NEAR wall. One end must be in, the other out.

    t says how far along the line the wall is: 0 = at point_a,
    1 = at point_b, 0.5 = halfway (lesson Part 2).

        t = ( (NEAR - a_z) / (b_z - a_z) )

    Then each of x and y moves the same fraction t of its own gap:

        x = ( a_x + (t * (b_x - a_x)) )

    Worked example (lesson Part 2): a = (-2, -1, -1), b = (2, -1, 3)
        t = ( (0.1 - (-1)) / (3 - (-1)) ) = (1.1 / 4) = 0.275
        x = ( -2 + (0.275 * (2 - (-2))) ) = ( -2 + 1.1 ) = -0.9
        y = ( -1 + (0.275 * (-1 - (-1))) ) = -1
        z = NEAR = 0.1          -> (-0.9, -1, 0.1)
    """
    a_x, a_y, a_z = point_a
    b_x, b_y, b_z = point_b
    t = ( (NEAR - a_z) / (b_z - a_z) )
    cut_x = ( a_x + (t * (b_x - a_x)) )
    cut_y = ( a_y + (t * (b_y - a_y)) )
    # The same sum for z would give exactly NEAR, which is the whole
    # point of t, so we just use NEAR.
    return (cut_x, cut_y, NEAR)


def clip_line(start, end):
    """(Lesson 8): keep the part of a CAMERA line that is in front of NEAR.

    Gives back (start, end) with any end behind you swapped for the
    cut point, or None ("nothing to draw") if both ends are behind.
    """
    start_in = (start[2] >= NEAR)
    end_in = (end[2] >= NEAR)
    if start_in and end_in:
        return (start, end)                       # all in front: keep it all
    if (not start_in) and (not end_in):
        return None                               # all behind: nothing
    cut = cut_at_near(start, end)
    if start_in:
        return (start, cut)                       # end was behind
    return (cut, end)                             # start was behind


def clip_face(face_corners):
    """(Lesson 8) cut one face at the NEAR wall (lesson Part 3).

    face_corners: the face's corners in CAMERA coordinates, clockwise.
    Gives back the corners of the part in front of NEAR, still in
    clockwise order. That can be 3, 4 or 5 corners, or an empty list
    if the whole face is behind you.

    We walk round the face one edge at a time. Each edge goes from the
    PREVIOUS corner to the CURRENT one, and there are only 4 cases:

        previous  current   keep
        in        in        current
        in        out       the cut point
        out       in        the cut point, then current
        out       out       nothing

    face_corners[-1] means "the LAST item in the list". Starting with
    it as "previous" makes the first edge go last corner -> first
    corner, so the walk goes all the way round and closes the face.

    Worked example (lesson Part 3): the right face of rock 0, seen from
    WORLD (2.5, 0, 3). CAMERA corners in clockwise order:
        5 (-1, 2, -0.5) out    6 (-1, 2, 2.5) in
        2 (-1, -1, 2.5) in     1 (-1, -1, -0.5) out
    Edges 1->5 nothing,  5->6 cut (-1, 2, 0.1) then 6,
          6->2 keep 2,    2->1 cut (-1, -1, 0.1)
    Result: 4 corners  (-1, 2, 0.1) (-1, 2, 2.5) (-1, -1, 2.5) (-1, -1, 0.1)
    """
    kept = []
    previous = face_corners[-1]
    for current in face_corners:
        previous_in = (previous[2] >= NEAR)
        current_in = (current[2] >= NEAR)
        if previous_in and current_in:
            kept.append(current)
        elif previous_in and (not current_in):
            kept.append(cut_at_near(previous, current))
        elif (not previous_in) and current_in:
            kept.append(cut_at_near(previous, current))
            kept.append(current)
        # out -> out: keep nothing
        previous = current
    return kept


# ======================================================================
# THE GAME TOOLS (Lesson 7)
# ======================================================================

def distance_3d(point_a, point_b):
    """(Lesson 7) how far apart are two WORLD points? (lesson Part 2)

    Subtract, square each part, add them up, square-root the total:
    Pythagoras done twice, in one line.

    Worked example (lesson Part 2): you at (1, 0, 3), ship 0 at (3, 1, 5)
        dx = (3 - 1) = 2,  dy = (1 - 0) = 1,  dz = (5 - 3) = 2
        math.sqrt( (2 * 2) + (1 * 1) + (2 * 2) ) = math.sqrt(9) = 3
    """
    ax, ay, az = point_a
    bx, by, bz = point_b
    dx = (bx - ax)
    dy = (by - ay)
    dz = (bz - az)
    return math.sqrt( (dx * dx) + (dy * dy) + (dz * dz) )


def far_from_rocks(spot):
    """(Lesson 8): True if this WORLD spot is at least ROCK_CLEARANCE (3) from
    the centre of every rock, so a new gold ship never hides inside one.

    Worked example (lesson Part 1): spot (1, 1, 5) and rock 0 at
    (0, 0.5, 4): math.sqrt( (1 * 1) + (0.5 * 0.5) + (1 * 1) ) = 1.5,
    less than 3, so False: try again.
    """
    for rock_spot in ROCK_SPOTS:
        if distance_3d(spot, rock_spot) < ROCK_CLEARANCE:
            return False
    return True


def new_pickup_spot():
    """(Lesson 7) a random WORLD spot for a ship, at least
    MIN_SPAWN_DISTANCE from you (lesson Part 4).

    "while True" repeats for ever, until "return" jumps out. Usually the
    first try is far enough; about 1 try in 5 is too close and we
    simply pick again.
    """
    you = (cam_x, cam_y, cam_z)
    while True:
        new_x = random.uniform((-FIELD), FIELD)
        new_y = random.uniform(PICKUP_LOW, PICKUP_HIGH)
        new_z = random.uniform((-FIELD), FIELD)
        spot = (new_x, new_y, new_z)
        # (Lesson 8): "and far_from_rocks(spot)": BOTH must be True.
        if (distance_3d(you, spot) >= MIN_SPAWN_DISTANCE) and far_from_rocks(spot):
            return spot


def to_map(x, z):
    """A WORLD (x, z) -> a pixel on the mini-map (from Lesson 4)."""
    map_x = MAP_CX + (x * MAP_SCALE)
    map_y = MAP_CY - (z * MAP_SCALE)
    return (map_x, map_y)


def draw_map():
    """The mini-map: the wall square, every ship and rock, and you, from above."""
    box = pygame.Rect(MAP_LEFT, MAP_TOP, MAP_SIZE, MAP_SIZE)
    pygame.draw.rect(screen, MAP_BACK, box)
    screen.set_clip(box)
    # (Lesson 7) the walls: from map (-12, 12) to map (12, -12)
    wall_left, wall_top = to_map((-WALL), WALL)          # (638, 438)
    wall_size = ( (2 * WALL) * MAP_SCALE )                # (24 * 6) = 144
    pygame.draw.rect(screen, WALL_RED,
                     pygame.Rect(wall_left, wall_top, wall_size, wall_size), 1)
    # Which corners to draw for each thing, seen from above:
    #   a rock (cube_model): its 4 bottom corners, a square (Lesson 5)
    #   NEW: a ship: its nose and two wing tips (corners 0, 1 and 2),
    #        a small triangle that points the way the ship faces
    #   anything else: not on the map (the teapot in step 3)
    for thing in things:
        if thing["model"] == cube_model:
            map_corners = (0, 1, 2, 3)
        elif thing["model"] == ship_model:
            map_corners = (0, 1, 2)
        else:
            continue
        outline = []
        for corner_number in map_corners:
            corner = thing["model"]["points"][corner_number]
            x, y, z = to_world(corner, thing)
            outline.append(to_map(x, z))
        pygame.draw.polygon(screen, thing["colour"], outline, 2)
    # You: pink dot and a line the way your BODY faces.
    forward_x, forward_y, forward_z = column(turn_matrix(cam_turn), 2)
    you = to_map(cam_x, cam_z)
    nose = to_map( (cam_x + (forward_x * 1.5)), (cam_z + (forward_z * 1.5)) )
    pygame.draw.line(screen, PINK, you, nose, 2)
    pygame.draw.circle(screen, PINK, you, 4)
    screen.set_clip(None)
    pygame.draw.rect(screen, WHITE, box, 1)


# ======================================================================
# THE MAIN LOOP
# ======================================================================
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_l:
                use_light = not use_light
            if event.key == pygame.K_g:
                show_grid = not show_grid
            if event.key == pygame.K_k:                  # (Lesson 8)
                use_clipping = not use_clipping
            # (Lesson 7) R only works after TIME UP, so you can't restart by
            # accident in the middle of a good game.
            if (event.key == pygame.K_r) and game_over:
                # Every game number back to its start value...
                cam_x = 0
                cam_y = 0
                cam_z = 0
                cam_turn = 0
                cam_tip = 0
                things = make_world()      # (Lesson 8): ships AND rocks
                score = 0
                frames_left = (GAME_SECONDS * 60)
                game_over = False
                # ...but NOT best_score: it remembers your best.

    # ==================================================================
    # PLAYING: everything in this "if" stops when game_over is True.
    # ==================================================================
    if not game_over:
        keys = pygame.key.get_pressed()

        # ---- Turning and looking (from Lesson 4, unchanged) ----------
        if keys[pygame.K_LEFT]:
            cam_turn = (cam_turn + TURN_SPEED)
        if keys[pygame.K_RIGHT]:
            cam_turn = (cam_turn - TURN_SPEED)
        if keys[pygame.K_UP]:
            cam_tip = (cam_tip - TURN_SPEED)
        if keys[pygame.K_DOWN]:
            cam_tip = (cam_tip + TURN_SPEED)
        if cam_tip > TIP_LIMIT:
            cam_tip = TIP_LIMIT
        if cam_tip < (-TIP_LIMIT):
            cam_tip = (-TIP_LIMIT)

        # ---- (Lesson 7) fly where you LOOK (lesson Part 5) -----------------
        # Build the arrow the way your head points: tip first (the head
        # nods), then turn (the body turns), and read off column 2,
        # where the +z arrow lands (Lesson 6).
        #   cam_tip -30, cam_turn 0:   forward = (0, 0.5, 0.866)   climbing
        #   cam_tip -30, cam_turn 90:  forward = (-0.866, 0.5, 0)  left + up
        # Right stays level (from your body only), so A and D slide
        # sideways without climbing.
        look = combine(tip_matrix(cam_tip), turn_matrix(cam_turn))
        forward_x, forward_y, forward_z = column(look, 2)
        right_x, right_y, right_z = column(turn_matrix(cam_turn), 0)
        if keys[pygame.K_w]:
            cam_x = (cam_x + (forward_x * MOVE_SPEED))
            cam_y = (cam_y + (forward_y * MOVE_SPEED))   # (Lesson 7) y too
            cam_z = (cam_z + (forward_z * MOVE_SPEED))
        if keys[pygame.K_s]:
            cam_x = (cam_x - (forward_x * MOVE_SPEED))
            cam_y = (cam_y - (forward_y * MOVE_SPEED))   # (Lesson 7) y too
            cam_z = (cam_z - (forward_z * MOVE_SPEED))
        if keys[pygame.K_d]:
            cam_x = (cam_x + (right_x * MOVE_SPEED))
            cam_z = (cam_z + (right_z * MOVE_SPEED))
        if keys[pygame.K_a]:
            cam_x = (cam_x - (right_x * MOVE_SPEED))
            cam_z = (cam_z - (right_z * MOVE_SPEED))
        if keys[pygame.K_e]:
            cam_y = (cam_y + MOVE_SPEED)
        if keys[pygame.K_q]:
            cam_y = (cam_y - MOVE_SPEED)

        # ---- (Lesson 7) walls, ground and ceiling (lesson Part 5) ----------
        # Past a limit? Put it back ON the limit. You slide along the
        # wall instead of going through it.
        if cam_x > WALL:
            cam_x = WALL
        if cam_x < (-WALL):
            cam_x = (-WALL)
        if cam_z > WALL:
            cam_z = WALL
        if cam_z < (-WALL):
            cam_z = (-WALL)
        if cam_y > CEILING:
            cam_y = CEILING
        if cam_y < GROUND:
            cam_y = GROUND

        # ---- (Lesson 7) collect any ship you are touching (Part 3) -----
        you = (cam_x, cam_y, cam_z)
        for thing in things:
            # (Lesson 8): rocks have "pickup": False, so they are never collected.
            if not thing["pickup"]:
                continue
            if distance_3d(you, thing["position"]) <= COLLECT_RADIUS:
                score = (score + 1)
                # (Lesson 7) the same ship jumps to a new spot (Part 4):
                # there are always exactly 8 ships to find.
                thing["position"] = new_pickup_spot()

        # ---- (Lesson 7) tick the clock (lesson Part 6) ---------------------
        frames_left = (frames_left - 1)
        if frames_left <= 0:
            frames_left = 0
            game_over = True
            if score > best_score:
                best_score = score

    # ---- Every pickup spins (Lesson 5), even after TIME UP -------------
    for thing in things:
        angles = thing["angles"]
        speeds = thing["speeds"]
        angles[0] = keep_under_360( (angles[0] + speeds[0]) )
        angles[1] = keep_under_360( (angles[1] + speeds[1]) )
        angles[2] = keep_under_360( (angles[2] + speeds[2]) )
        thing["matrix"] = spin_matrix(angles)

    # ---- The camera's matrix, once a frame (Lesson 6) ------------------
    camera_matrix = combine(turn_matrix(-cam_turn), tip_matrix(-cam_tip))

    # ==================================================================
    # DRAW: the world first, then the HUD on top (lesson Part 2)
    # ==================================================================
    screen.fill(BLACK)
    if show_grid:
        draw_floor()
    faces_to_draw = []
    for thing in things:
        add_faces_of(thing, faces_to_draw)
    faces_to_draw.sort(reverse=True)
    for distance, face_points, colour in faces_to_draw:
        pygame.draw.polygon(screen, colour, face_points)
        pygame.draw.polygon(screen, BLACK, face_points, 2)

    draw_map()

    # ---- (Lesson 7) how far is the nearest ship? -------------------------
    # Start with a huge number, then keep the smallest distance found.
    nearest = 1000
    for thing in things:
        if not thing["pickup"]:          # (Lesson 8): rocks don't count
            continue
        d = distance_3d((cam_x, cam_y, cam_z), thing["position"])
        if d < nearest:
            nearest = d

    # ---- The HUD: words drawn LAST, so nothing in the world can hide them -----------
    # str() turns a number into letters so + can join it to words.
    text = ("score " + str(score) + "   best " + str(best_score))
    screen.blit(font.render(text, True, SUN_GOLD), (20, 20))
    text = ("nearest ship " + str(round(nearest, 1)))
    screen.blit(font.render(text, True, PINK), (20, 50))
    # (Lesson 8): say whether clipping is on, so screenshots are never confusing.
    if use_clipping:
        text = "clipping ON (K)"
    else:
        text = "clipping OFF (K)"
    screen.blit(font.render(text, True, WHITE), (20, 80))
    # (Lesson 7) math.ceil rounds UP, so the clock never shows 0 while you
    # can still play: 59.98 seconds left shows as 60.
    seconds = math.ceil(frames_left / 60)
    screen.blit(font.render("time " + str(seconds), True, WHITE), (680, 20))
    screen.blit(font.render("ARROWS look,  W / S fly,  A / D slide,  Q / E down / up",
                            True, YELLOW), (20, 570))

    # ---- (Lesson 7) TIME UP on top of everything -------------------------
    if game_over:
        words = big_font.render("TIME UP", True, WHITE)
        # Centre it: half its width to the left of the screen's middle.
        # get_width() is how many pixels wide the words came out.
        left = (CENTRE_X - (words.get_width() / 2))
        screen.blit(words, (left, 200))
        words = font.render("score " + str(score) + "   best " + str(best_score) +
                            "      press R to play again", True, YELLOW)
        left = (CENTRE_X - (words.get_width() / 2))
        screen.blit(words, (left, 290))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

# ----------------------------------------------------------------------
# TRY THIS:
#   * Swap ship_model back to cube_model in make_pickups(). The game is
#     Lesson 8's clipped Cube Hunt again: load_obj() changed nothing else.
#   * Open ship.obj in a text editor and make the wings longer:
#     change -1.5 and 1.5 to -3.0 and 3.0. Run again. Is the ship
#     longer or shorter on screen than before? Why? (Hint: CHANGE 4.)
#   * In load_obj(), delete the line  corners.reverse() . Fly up to a
#     ship. What do you see, and which Lesson 3 rule explains it?
#   * Make your own .obj: a pyramid. Copy Lesson 5's pyramid_points
#     (add 1 to every corner number for the f lines!) into pyramid.obj.
# ----------------------------------------------------------------------
