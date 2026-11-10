# ======================================================================
# LESSON 11 - STEP 3: CRATES YOU BUMP INTO AND STAND ON
# ----------------------------------------------------------------------
# Goal: a world that is SOLID. Brown crates sit on the floor. You can't
# walk through them, you can jump onto them, and two of them make a
# staircase up to a cube you can't reach any other way.
#
# This starts from step2_gravity.py. It is the finished game of
# Lesson 11: "Cube Hunt" with velocity, gravity and solid crates.
#
# What is new since step 2:
#
#   1. CRATES  (lesson Part 4)
#        A second list, crates, of Lesson 5 things that never spin.
#        Small crates are 1 unit tall (jump onto them); tall crates
#        are 2 units tall (too high to jump: climb a small one first).
#
#   2. BOXES  (lesson Part 4)
#        A box is 6 numbers: (min_x, max_x, min_y, max_y, min_z, max_z).
#        player_box() is YOUR body; crate_box(crate) is a crate's.
#
#   3. DO TWO BOXES OVERLAP?  (lesson Part 4)
#        Only if they overlap on the x line AND the y line AND the
#        z line. One line is one test:
#            (a_min < b_max) and (b_min < a_max)
#
#   4. MOVE ONE AXIS AT A TIME, AND PUSH BACK OUT  (lesson Part 5)
#        Move x. Inside a crate? Put your side back ON the crate's side
#        you came from, vel_x = 0. Then the same for z, then y. Landing
#        on a crate's top works exactly like landing on the floor.
#
#   5. NEW CUBES NEVER APPEAR INSIDE A CRATE  (lesson Part 5)
#
# Every frame:
#
#   push (drag, thrust)  ->  move x, bump?  ->  move z, bump?
#   ->  jump?, gravity, move y, land or bump head?  ->  floor  ->  walls
#
# Controls:  LEFT / RIGHT = turn,   UP / DOWN = look up / down
#            W / S = walk forward / back,   A / D = step left / right
#            SPACE = jump
#            R = play again (after TIME UP)
#            G = floor grid on / off,   L = light on / off
# Run:  python step3_crates.py
# ======================================================================

import math
import random                 # (step 2) for random.uniform
import pygame

pygame.init()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 11, step 3 - Cube Hunt with crates")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)
big_font = pygame.font.SysFont(None, 96)    # NEW: for "TIME UP"

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
PINK = (255, 105, 200)        # the colour we use for YOU (the camera)
MAP_BACK = (25, 30, 36)       # dark grey-blue behind the mini-map
GRID_COLOUR = (40, 90, 70)    # (Lesson 5) dim green for the floor lines
WALL_RED = (235, 80, 80)      # (step 1) the wall square on the mini-map
SUN_GOLD = (250, 200, 70)     # (step 1) the colour of every pickup cube
CRATE_BROWN = (170, 115, 60)  # NEW: the colour of every crate

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


# ======================================================================
# THE PLAYING FIELD (lesson Part 1)
# ======================================================================

# ---- (step 1) the sizes of the field ------------------------------------
# FIELD = 10: new cubes appear with x and z from -10 to 10, a 20 x 20
#   square. You move 3 units a second, so edge to edge is
#   (20 / 3) = 6.7 seconds: some running, but never boring.
# WALL = 12: you can't go further than 12 from the centre, 2 more than
#   FIELD, so you can always get round a cube at the edge.
FIELD = 10
WALL = 12

# ---- (step 1) the floor (from Lesson 5), now as big as the walls --------
FLOOR_Y = -1
GRID_LEFT = (-WALL)       # -12
GRID_RIGHT = WALL         # 12
GRID_NEAR = (-WALL)       # -12
GRID_FAR = WALL           # 12

# ---- (step 1) the pickups ------------------------------------------------
# PICKUP_SIZE = 0.5: Lesson 5's "size", so each cube is 1 unit wide
#   (its corners are at -0.5 and 0.5). A 1-unit face 5 away is
#   ((1 * 400) / 5) = 80 px wide; 20 away it is 20 px (lesson Part 1).
PICKUP_SIZE = 0.5

# (step 2) cube heights: their centres float from y = 0 to y = 2.
#   0 is your eye height at the start; the lowest cube's bottom is then
#   at (0 - 0.5) = -0.5, half a unit above the floor (FLOOR_Y = -1).
PICKUP_LOW = 0
PICKUP_HIGH = 2

# (step 1) the 8 spots the cubes start at, in WORLD coordinates.
# The same every game, so you can learn a good route. Cube 0 at
# (3, 1, 5) is the lesson's worked example.
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

# (step 2) COLLECT_RADIUS = 1.0: you collect a cube when your eye is
#   1 unit or less from its CENTRE. Its faces are 0.5 from the centre,
#   so your nose is then 0.5 from a face, which fills the window:
#   ((1 * 400) / 0.5) = 800 px wide (lesson Part 3).
COLLECT_RADIUS = 1.0

# (step 2) MIN_SPAWN_DISTANCE = 5: a new cube never appears closer than
#   5 to you, so it is at least (5 / 3) = 1.7 seconds of running away.
MIN_SPAWN_DISTANCE = 5

# ---- NEW: your body (lesson Part 3) ------------------------------------
# EYE_HEIGHT = 0.5: your eye (the camera) is half a unit above your
#   feet. It is Lesson 7's GROUND number: standing on the floor
#   (FLOOR_Y = -1) your eye is at (-1 + 0.5) = -0.5, as low as Lesson 7
#   let you fly. The lowest cubes (centre y = 0) are then
#   (0 - (-0.5)) = 0.5 above your eye: inside the 1.0 touch bubble, so
#   you can collect them just by walking.
# (Lesson 7's CEILING has gone: gravity is the ceiling now.)
EYE_HEIGHT = 0.5

# ---- NEW: gravity and jumping (lesson Part 3) ---------------------------
# GRAVITY = 0.01: taken off vel_y EVERY frame, so a fall gets faster
#   and faster: 0.01, 0.02, 0.03 ... units a frame.
# JUMP_SPEED = 0.2: the vel_y a jump starts with.
#
# Why these two? Count the frames (lesson Part 3 has the table):
#   going up, vel_y is 0.19, 0.18, 0.17 ... 0.01, 0 (19 moves), so
#   your feet rise ( 0.19 + 0.18 + ... + 0.01 ) = 1.9 units, and the
#   whole jump takes about 39 frames = (39 / 60) = 0.65 seconds.
#   1.9 is enough to jump onto a 1-unit crate (step 3) with 0.9 to
#   spare, but NOT onto a 2-unit one: you'll need a step for that.
#   At the top your eye is at (-0.5 + 1.9) = 1.4: the highest cubes
#   (centre y = 2) are (2 - 1.4) = 0.6 away, inside the 1.0 bubble.
GRAVITY = 0.01
JUMP_SPEED = 0.2

# ---- NEW: how wide YOU are (lesson Part 4) ------------------------------
# PLAYER_RADIUS = 0.25: your body reaches 0.25 to each side of your eye
#   in x and in z, so you are (2 * 0.25) = 0.5 wide and, with
#   EYE_HEIGHT, 0.5 tall: a small box with the camera on its top.
#   Why 0.25? Bumped against a crate your eye stays 0.25 from its face,
#   more than NEAR = 0.1, so the face is never cut away (Lesson 4).
PLAYER_RADIUS = 0.25

# ---- NEW: the crates (lesson Part 4) ------------------------------------
# Each crate is a Lesson 5 thing, made from the same cube_model. The
# cube model goes from -1 to 1, so a crate reaches "size" each way
# from its centre:
#   size 0.5 -> 1 unit wide and tall   (a SMALL crate: jump onto it)
#   size 1   -> 2 units wide and tall  (a TALL crate: too high to jump)
# Every crate sits ON the floor, so its centre y = (FLOOR_Y + size):
#   small: (-1 + 0.5) = -0.5        tall: (-1 + 1) = 0
# Crates NEVER spin: the box test (Part 4) needs their sides to line
# up with the x, y and z axes.
#
# (position, size), in WORLD coordinates:
CRATE_SPOTS = [
    ((0, -0.5, 3), 0.5),       # A  small, straight ahead: the worked example
    ((5, 0, 2), 1),            # B  tall, a wall to walk round
    ((-4, -0.5, -8.5), 0.5),   # C  small: the first step...
    ((-4, 0, -7), 1),          # D  tall: ...up to cube 5, above it at y = 2
    ((-6, -0.5, 7), 0.5),      # E  small
    ((7, -0.5, -6), 0.5),      # F  small
]


def make_crates():
    """NEW: build the list of crate THINGS, one for each CRATE_SPOTS line.

    Their angles stay [0, 0, 0] and speeds (0, 0, 0), so their spin
    matrix never changes: we make it once, here, and never again.
    """
    crates = []
    for position, size in CRATE_SPOTS:
        crates.append({"model": cube_model, "position": position,
                       "size": size, "angles": [0, 0, 0],
                       "speeds": (0, 0, 0), "colour": CRATE_BROWN,
                       "matrix": spin_matrix([0, 0, 0])})
    return crates

# ---- NEW: the clock (lesson Part 6) -------------------------------------
# 60 seconds: at 3 units a second that is (3 * 60) = 180 units of
# running, enough for a good handful of cubes, short enough to retry.
GAME_SECONDS = 60


def make_pickups():
    """(step 1) build a fresh list of 8 pickup THINGS (Lesson 5's
    dictionaries), one at each START_SPOTS position.

    Each one is a small gold cube (size 0.5) that spins slowly so it
    catches your eye: 1 degree a frame of turn = one turn in 6 seconds,
    and 0.5 of tip so it wobbles a little too.
    """
    pickups = []
    for spot in START_SPOTS:
        pickups.append({"model": cube_model, "position": spot,
                        "size": PICKUP_SIZE, "angles": [0, 0, 0],
                        "speeds": (0.5, 1, 0), "colour": SUN_GOLD})
    return pickups


# (step 1) "things" is Lesson 5's list of everything in the world.
# In the game, the world is just the 8 gold cubes.
things = make_pickups()

# ---- Where YOU are (from Lesson 4) ------------------------------------
cam_x = 0
cam_y = (FLOOR_Y + EYE_HEIGHT)   # NEW: standing on the floor: (-1 + 0.5) = -0.5
cam_z = 0
cam_turn = 0        # degrees, positive = turned LEFT
cam_tip = 0         # degrees, positive = looking DOWN
TIP_LIMIT = 60
# MOVE_SPEED has gone: keys now push your VELOCITY instead (below).
TURN_SPEED = 1.5    # (1.5 * 60) = 90 degrees a second
NEAR = 0.1          # closer than this (CAMERA z) is not drawn

# ---- NEW: velocity (lesson Part 1) ------------------------------------
# How far you move EACH FRAME, in WORLD units, along x, y and z.
# 0 = standing still. vel_z = 0.05 means 0.05 units further away
# every frame, which is (0.05 * 60) = 3 units a second.
vel_x = 0
vel_y = 0
vel_z = 0

# ---- NEW: thrust and drag (lesson Part 2) -----------------------------
# THRUST = 0.005: what one held key ADDS to your velocity each frame.
#   Small on purpose: it takes 10 frames of pushing to add 0.05, and
#   drag takes some away too, so you speed up smoothly.
# DRAG = 0.9: every frame your velocity is multiplied by 0.9, so you
#   keep 90% and lose 10%. Without drag you would never slow down.
#
# Why these two numbers? They balance at a top speed of
#   (THRUST / (1 - DRAG)) = (0.005 / (1 - 0.9)) = (0.005 / 0.1) = 0.05
# a frame: exactly Lesson 7's MOVE_SPEED, 3 units a second. You reach
# 90% of it in 22 frames (0.37 s), and glide (0.05 * 9) = 0.45 units
# after letting go (lesson Part 2 works both out).
THRUST = 0.005
DRAG = 0.9

# ---- NEW: are your feet on something? (lesson Part 3) -----------------
# True = standing, so SPACE may jump. False = in the air. Worked out
# again every frame by the floor check: you start standing.
on_ground = True

# ---- The light (from Lesson 3, unchanged) -----------------------------
LIGHT = (0.48, 0.6, -0.64)
AMBIENT = 0.2
use_light = True
show_grid = True

# ---- (step 2) the score ------------------------------------------------
score = 0
# ---- NEW: the clock and the game's two states (lesson Part 6) ----------
best_score = 0                         # NOT reset by R
frames_left = (GAME_SECONDS * 60)      # (60 * 60) = 3600
game_over = False                      # False = PLAYING, True = TIME UP

# ---- The mini-map (lesson Part 1: resized for the whole field) ---------
MAP_LEFT = 630
MAP_TOP = 430
MAP_SIZE = 160
# (step 1) the WORLD centre now sits in the MIDDLE of the box, because
# the field goes the same distance every way (-12 to 12).
MAP_CX = (MAP_LEFT + (MAP_SIZE / 2))    # (630 + 80) = 710
MAP_CY = (MAP_TOP + (MAP_SIZE / 2))     # (430 + 80) = 510
# (step 1) 6 px per unit: the walls are 24 units across, and
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
    paint to the shared list (unchanged from Lesson 6)."""
    model = thing["model"]
    camera_points = []
    screen_points = []
    for p in model["points"]:
        world = to_world(p, thing)                     # WORLD
        camera = to_camera(world)                      # CAMERA
        camera_points.append(camera)
        if camera[2] >= NEAR:
            screen_points.append(project(camera))      # SCREEN
        else:
            screen_points.append(None)

    for corners, face_colour, pointer in model["faces"]:
        too_close = False
        for corner_number in corners:
            if camera_points[corner_number][2] < NEAR:
                too_close = True
        if too_close:
            continue
        face_points = []
        for corner_number in corners:
            face_points.append(screen_points[corner_number])
        if not is_facing_you(face_points):
            continue
        distance = average_z(corners, camera_points)
        colour = thing["colour"]
        if use_light:
            spun_pointer = matrix_times_point(thing["matrix"], pointer)
            colour = shade_colour(colour, spun_pointer)
        faces_to_draw.append( (distance, face_points, colour) )


def draw_floor():
    """(Lesson 5) the floor grid, in 1-unit pieces (now -12 to 12)."""
    for x in range(GRID_LEFT, (GRID_RIGHT + 1)):
        for z in range(GRID_NEAR, GRID_FAR):
            draw_floor_piece( (x, FLOOR_Y, z), (x, FLOOR_Y, (z + 1)) )
    for z in range(GRID_NEAR, (GRID_FAR + 1)):
        for x in range(GRID_LEFT, GRID_RIGHT):
            draw_floor_piece( (x, FLOOR_Y, z), ((x + 1), FLOOR_Y, z) )


def draw_floor_piece(world_start, world_end):
    """(Lesson 5) one 1-unit piece of floor line."""
    start = to_camera(world_start)
    end = to_camera(world_end)
    if (start[2] < NEAR) or (end[2] < NEAR):
        return
    pygame.draw.line(screen, GRID_COLOUR, project(start), project(end), 1)


# ======================================================================
# THE GAME TOOLS (Lesson 7)
# ======================================================================

def distance_3d(point_a, point_b):
    """(step 1) how far apart are two WORLD points? (lesson Part 2)

    Subtract, square each part, add them up, square-root the total:
    Pythagoras done twice, in one line.

    Worked example (lesson Part 2): you at (1, 0, 3), cube 0 at (3, 1, 5)
        dx = (3 - 1) = 2,  dy = (1 - 0) = 1,  dz = (5 - 3) = 2
        math.sqrt( (2 * 2) + (1 * 1) + (2 * 2) ) = math.sqrt(9) = 3
    """
    ax, ay, az = point_a
    bx, by, bz = point_b
    dx = (bx - ax)
    dy = (by - ay)
    dz = (bz - az)
    return math.sqrt( (dx * dx) + (dy * dy) + (dz * dz) )


# ======================================================================
# NEW: BOXES AND BUMPING (lesson Parts 4 and 5)
# ======================================================================

def player_box():
    """NEW: YOUR body as a box, in WORLD coordinates (lesson Part 4).

    A box is 6 numbers: (min_x, max_x, min_y, max_y, min_z, max_z).
    Your eye (the camera) is at the top, in the middle:
        x:  cam_x - 0.25  to  cam_x + 0.25
        y:  your feet (cam_y - 0.5)  to  your eye (cam_y)
        z:  cam_z - 0.25  to  cam_z + 0.25
    Standing at the start, (0, -0.5, 0):
        (-0.25, 0.25,  -1, -0.5,  -0.25, 0.25)
    """
    return ( (cam_x - PLAYER_RADIUS), (cam_x + PLAYER_RADIUS),
             (cam_y - EYE_HEIGHT),    cam_y,
             (cam_z - PLAYER_RADIUS), (cam_z + PLAYER_RADIUS) )


def crate_box(crate):
    """NEW: a crate as a box, in WORLD coordinates (lesson Part 4).

    It reaches "size" each way from its centre. Crate A, centre
    (0, -0.5, 3), size 0.5:
        x: (0 - 0.5) to (0 + 0.5)        = -0.5 to 0.5
        y: (-0.5 - 0.5) to (-0.5 + 0.5)  = -1   to 0     (floor to top)
        z: (3 - 0.5) to (3 + 0.5)        =  2.5 to 3.5
    """
    x, y, z = crate["position"]
    size = crate["size"]
    return ( (x - size), (x + size),
             (y - size), (y + size),
             (z - size), (z + size) )


def overlap_on_line(a_min, a_max, b_min, b_max):
    """NEW: do two pieces of ONE number line overlap? (lesson Part 4)

    They overlap if A starts before B ends AND B starts before A ends.
        A 1 to 3,  B 2 to 5:   (1 < 5) and (2 < 3)  -> True
        A 1 to 3,  B 4 to 5:   (1 < 5) and (4 < 3)  -> False
    "<", not "<=": two pieces that only touch (A 1 to 3, B 3 to 5) do
    NOT overlap. That is what lets you stand exactly ON a crate's top.
    """
    return (a_min < b_max) and (b_min < a_max)


def boxes_overlap(box_a, box_b):
    """NEW: do two boxes overlap? Only if they overlap on the x line
    AND the y line AND the z line (lesson Part 4, the KEY CONCEPT).
    One gap on any one line, and they don't touch."""
    a_min_x, a_max_x, a_min_y, a_max_y, a_min_z, a_max_z = box_a
    b_min_x, b_max_x, b_min_y, b_max_y, b_min_z, b_max_z = box_b
    on_x = overlap_on_line(a_min_x, a_max_x, b_min_x, b_max_x)
    on_y = overlap_on_line(a_min_y, a_max_y, b_min_y, b_max_y)
    on_z = overlap_on_line(a_min_z, a_max_z, b_min_z, b_max_z)
    return (on_x and on_y and on_z)


def crate_you_are_in():
    """NEW: the box of the first crate your body overlaps, or None if
    you are not inside any crate (lesson Part 5)."""
    you = player_box()
    for crate in crates:
        box = crate_box(crate)
        if boxes_overlap(you, box):
            return box
    return None


def new_pickup_spot():
    """(step 2) a random WORLD spot for a cube, at least
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
        # NEW: the gold cube's own box (it reaches 0.5 each way)...
        cube_box = ( (new_x - PICKUP_SIZE), (new_x + PICKUP_SIZE),
                     (new_y - PICKUP_SIZE), (new_y + PICKUP_SIZE),
                     (new_z - PICKUP_SIZE), (new_z + PICKUP_SIZE) )
        # ...must not overlap any crate, or you could never reach it.
        inside_a_crate = False
        for crate in crates:
            if boxes_overlap(cube_box, crate_box(crate)):
                inside_a_crate = True
        if inside_a_crate:
            continue          # "continue" = skip the rest, try again
        if distance_3d(you, spot) >= MIN_SPAWN_DISTANCE:
            return spot


def to_map(x, z):
    """A WORLD (x, z) -> a pixel on the mini-map (from Lesson 4)."""
    map_x = MAP_CX + (x * MAP_SCALE)
    map_y = MAP_CY - (z * MAP_SCALE)
    return (map_x, map_y)


def draw_map():
    """The mini-map: the wall square, every cube, and you, from above."""
    box = pygame.Rect(MAP_LEFT, MAP_TOP, MAP_SIZE, MAP_SIZE)
    pygame.draw.rect(screen, MAP_BACK, box)
    screen.set_clip(box)
    # (step 1) the walls: from map (-12, 12) to map (12, -12)
    wall_left, wall_top = to_map((-WALL), WALL)          # (638, 438)
    wall_size = ( (2 * WALL) * MAP_SCALE )                # (24 * 6) = 144
    pygame.draw.rect(screen, WALL_RED,
                     pygame.Rect(wall_left, wall_top, wall_size, wall_size), 1)
    # NEW: each crate, from above: a filled brown square from its box.
    for crate in crates:
        min_x, max_x, min_y, max_y, min_z, max_z = crate_box(crate)
        corner_left, corner_top = to_map(min_x, max_z)    # top-left on the map
        width = ((max_x - min_x) * MAP_SCALE)             # small: (1 * 6) = 6 px
        pygame.draw.rect(screen, CRATE_BROWN,
                         pygame.Rect(corner_left, corner_top, width, width))
    # Each cube's 4 bottom corners (from Lesson 5): a small gold square.
    for thing in things:
        outline = []
        for corner_number in (0, 1, 2, 3):
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


# NEW: the crates never change, so we make them once, here, after
# spin_matrix() has been defined above.
crates = make_crates()


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
            # NEW: R only works after TIME UP, so you can't restart by
            # accident in the middle of a good game.
            if (event.key == pygame.K_r) and game_over:
                # Every game number back to its start value...
                cam_x = 0
                cam_y = (FLOOR_Y + EYE_HEIGHT)    # NEW: on the floor
                cam_z = 0
                cam_turn = 0
                cam_tip = 0
                vel_x = 0          # NEW: standing still again
                vel_y = 0
                vel_z = 0
                on_ground = True
                things = make_pickups()
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

        # ---- NEW: walk where your BODY faces (lesson Part 3) ----------
        # Lesson 6's level arrows, from cam_turn only. Looking up no
        # longer lifts you: only a jump can do that now.
        forward_x, forward_y, forward_z = column(turn_matrix(cam_turn), 2)
        right_x, right_y, right_z = column(turn_matrix(cam_turn), 0)

        # ==============================================================
        # SIDEWAYS (x and z): exactly step 1's three jobs
        # ==============================================================
        # Job 1: DRAG, now on x and z only. (Drag on vel_y would spoil
        # the jump's neat numbers, and air hardly slows a fall anyway.)
        vel_x = (vel_x * DRAG)
        vel_z = (vel_z * DRAG)

        # Job 2: THRUST along the level arrows. forward_y and right_y
        # are always 0 now, so we only need x and z.
        if keys[pygame.K_w]:
            vel_x = (vel_x + (forward_x * THRUST))
            vel_z = (vel_z + (forward_z * THRUST))
        if keys[pygame.K_s]:
            vel_x = (vel_x - (forward_x * THRUST))
            vel_z = (vel_z - (forward_z * THRUST))
        if keys[pygame.K_d]:
            vel_x = (vel_x + (right_x * THRUST))
            vel_z = (vel_z + (right_z * THRUST))
        if keys[pygame.K_a]:
            vel_x = (vel_x - (right_x * THRUST))
            vel_z = (vel_z - (right_z * THRUST))

        # ==============================================================
        # NEW: MOVE ONE AXIS AT A TIME, AND PUSH BACK OUT (Part 5)
        # ==============================================================
        # Why one at a time? After moving ONLY x, if you are now inside
        # a crate it can only be because of x, so you know which side
        # you came in through: the side your vel_x was heading for.

        # ---- x ------------------------------------------------------
        cam_x = (cam_x + vel_x)
        box = crate_you_are_in()
        if box is not None:
            min_x, max_x, min_y, max_y, min_z, max_z = box
            if vel_x > 0:
                # Moving +x (right): you hit the crate's LEFT side,
                # min_x. Put YOUR right side (cam_x + 0.25) on it.
                cam_x = (min_x - PLAYER_RADIUS)
            else:
                # Moving -x (left): you hit its RIGHT side, max_x.
                cam_x = (max_x + PLAYER_RADIUS)
            vel_x = 0

        # ---- z: exactly the same, with z ----------------------------
        # Worked example (lesson Part 5): walking at you z 2.22 into
        # crate A, vel_z 0.05 -> cam_z 2.27, your far side 2.52 is past
        # its near side 2.5 -> cam_z = (2.5 - 0.25) = 2.25, vel_z = 0.
        cam_z = (cam_z + vel_z)
        box = crate_you_are_in()
        if box is not None:
            min_x, max_x, min_y, max_y, min_z, max_z = box
            if vel_z > 0:
                cam_z = (min_z - PLAYER_RADIUS)    # hit its near side
            else:
                cam_z = (max_z + PLAYER_RADIUS)    # hit its far side
            vel_z = 0

        # Walls (Lesson 7 + step 1): back ON the wall, that velocity 0.
        if cam_x > WALL:
            cam_x = WALL
            vel_x = 0
        if cam_x < (-WALL):
            cam_x = (-WALL)
            vel_x = 0
        if cam_z > WALL:
            cam_z = WALL
            vel_z = 0
        if cam_z < (-WALL):
            cam_z = (-WALL)
            vel_z = 0

        # ==============================================================
        # UP AND DOWN (y): jump, gravity (step 2), then crates and floor
        # ==============================================================
        if keys[pygame.K_SPACE] and on_ground:
            vel_y = JUMP_SPEED                       # 0.2
        vel_y = (vel_y - GRAVITY)

        # ---- y: the same push-out, but the two sides mean different
        # things: falling onto a top is LANDING. -----------------------
        cam_y = (cam_y + vel_y)
        on_ground = False
        box = crate_you_are_in()
        if box is not None:
            min_x, max_x, min_y, max_y, min_z, max_z = box
            if vel_y < 0:
                # Falling: your FEET went into the crate's TOP (max_y).
                # Put them back ON it, exactly like the floor.
                # Crate A: top 0, so cam_y = (0 + 0.5) = 0.5.
                cam_y = (max_y + EYE_HEIGHT)
                on_ground = True
            else:
                # Rising: your HEAD (your eye, cam_y) hit its BOTTOM.
                cam_y = min_y
            vel_y = 0

        # FLOOR (step 2): your feet below the floor -> stand ON it.
        feet_y = (cam_y - EYE_HEIGHT)
        if feet_y < FLOOR_Y:
            cam_y = (FLOOR_Y + EYE_HEIGHT)           # (-1 + 0.5) = -0.5
            vel_y = 0
            on_ground = True

        # ---- (step 2) collect any cube you are touching (Part 3) -----
        you = (cam_x, cam_y, cam_z)
        for thing in things:
            if distance_3d(you, thing["position"]) <= COLLECT_RADIUS:
                score = (score + 1)
                # (step 2) the same cube jumps to a new spot (Part 4):
                # there are always exactly 8 cubes to find.
                thing["position"] = new_pickup_spot()

        # ---- NEW: tick the clock (lesson Part 6) ---------------------
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
    for crate in crates:                       # NEW: the crates too,
        add_faces_of(crate, faces_to_draw)     # in the SAME sort
    faces_to_draw.sort(reverse=True)
    for distance, face_points, colour in faces_to_draw:
        pygame.draw.polygon(screen, colour, face_points)
        pygame.draw.polygon(screen, BLACK, face_points, 2)

    draw_map()

    # ---- (step 1) how far is the nearest cube? -------------------------
    # Start with a huge number, then keep the smallest distance found.
    nearest = 1000
    for thing in things:
        d = distance_3d((cam_x, cam_y, cam_z), thing["position"])
        if d < nearest:
            nearest = d

    # ---- The HUD: words drawn LAST, so no cube can hide them -----------
    # str() turns a number into letters so + can join it to words.
    text = ("score " + str(score) + "   best " + str(best_score))
    screen.blit(font.render(text, True, SUN_GOLD), (20, 20))
    text = ("nearest cube " + str(round(nearest, 1)))
    screen.blit(font.render(text, True, PINK), (20, 50))
    # (step 1) your speed along the floor, in units a second. Only x
    # and z: falling doesn't count as walking speed.
    speed = (distance_3d((0, 0, 0), (vel_x, 0, vel_z)) * 60)
    text = ("speed " + str(round(speed, 1)))
    screen.blit(font.render(text, True, WHITE), (20, 80))
    # NEW: how high your feet are above the floor, and are you standing?
    feet_up = ((cam_y - EYE_HEIGHT) - FLOOR_Y)
    if on_ground:
        text = ("feet up " + str(round(feet_up, 2)) + "   on the ground")
    else:
        text = ("feet up " + str(round(feet_up, 2)) + "   in the air")
    screen.blit(font.render(text, True, WHITE), (20, 110))
    # NEW: math.ceil rounds UP, so the clock never shows 0 while you
    # can still play: 59.98 seconds left shows as 60.
    seconds = math.ceil(frames_left / 60)
    screen.blit(font.render("time " + str(seconds), True, WHITE), (680, 20))
    screen.blit(font.render("ARROWS look,  W / S walk,  A / D step,  SPACE jump",
                            True, YELLOW), (20, 570))

    # ---- NEW: TIME UP on top of everything -------------------------
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
#   * Build a staircase: three small crates in a row, then a tall one.
#     Remember each crate's centre y is (FLOOR_Y + size).
#   * Stack a small crate ON a tall one: centre y = (1 + 0.5) = 1.5.
#     Can you get on top? (Your feet rise 1.9; the top is at 2.)
#   * Make PLAYER_RADIUS = 0.05. Walk into a crate and look: its face
#     is now 0.05 from your eye, closer than NEAR = 0.1. What happens?
#   * A bouncy crate: when you land on it, set vel_y = JUMP_SPEED
#     instead of 0. Hint: give the crate a "bouncy": True key.
#   * Moving platform: give one small crate a speed and add it to its
#     position each frame. (Hard: you also need to move YOU with it
#     while you stand on it.)
# ----------------------------------------------------------------------
