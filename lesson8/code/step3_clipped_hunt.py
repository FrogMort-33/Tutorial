# ======================================================================
# LESSON 8 - STEP 3: CLIPPING FACES (Cube Hunt, clipped)
# ----------------------------------------------------------------------
# Goal: a face that crosses the NEAR wall is CUT at the wall, not
# skipped. Fly right past a rock and its wall stays solid all the way.
#
# This is the finished script of Lesson 8, and Lesson 9's start.
#
# What is new since step 2:
#
#   1. clip_face(corners)   (lesson Part 3)
#        Walk round the face's corners, one edge at a time. For each
#        edge "previous -> current" there are only 4 cases:
#            in  -> in   keep current
#            in  -> out  keep the cut point
#            out -> in   keep the cut point, then current
#            out -> out  keep nothing
#        ("in" means CAMERA z >= NEAR, in front of the wall.)
#        A 4-corner face can come back with 3, 4 or 5 corners, or
#        with none at all if every corner is behind you.
#
#   2. add_faces_of() clips each face in CAMERA coordinates, THEN
#      projects it (lesson Part 4). The recipe for one face is now:
#        SHAPE -> WORLD -> CAMERA -> clip -> project -> clock test
#
#   3. K turns face clipping on / off too, so you can compare.
#
# The game itself is unchanged: 60 seconds, touch the gold cubes.
#
# Controls:  LEFT / RIGHT = turn,   UP / DOWN = look up / down
#            W / S = fly forward / back (the way you LOOK)
#            A / D = slide left / right,   Q / E = straight down / up
#            R = play again (after TIME UP),   K = clipping on / off
#            G = floor grid on / off,   L = light on / off
# Run:  python step3_clipped_hunt.py
# ======================================================================

import math
import random                 # (Lesson 7) for random.uniform
import pygame

pygame.init()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 8, step 3 - Cube Hunt, clipped")
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
SUN_GOLD = (250, 200, 70)     # (Lesson 7) the colour of every pickup cube
STONE = (150, 150, 160)       # (step 1): the colour of every rock

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

# ---- (Lesson 7) the sizes of the field ------------------------------------
# FIELD = 10: new cubes appear with x and z from -10 to 10, a 20 x 20
#   square. You fly 3 units a second, so edge to edge is
#   (20 / 3) = 6.7 seconds: some flying, but never boring.
# WALL = 12: you can't fly further than 12 from the centre, 2 more than
#   FIELD, so you can always fly round a cube at the edge.
FIELD = 10
WALL = 12

# ---- (Lesson 7) the floor (from Lesson 5), now as big as the walls --------
FLOOR_Y = -1
GRID_LEFT = (-WALL)       # -12
GRID_RIGHT = WALL         # 12
GRID_NEAR = (-WALL)       # -12
GRID_FAR = WALL           # 12

# ---- (Lesson 7) the pickups ------------------------------------------------
# PICKUP_SIZE = 0.5: Lesson 5's "size", so each cube is 1 unit wide
#   (its corners are at -0.5 and 0.5). A 1-unit face 5 away is
#   ((1 * 400) / 5) = 80 px wide; 20 away it is 20 px (lesson Part 1).
PICKUP_SIZE = 0.5

# (Lesson 7) cube heights: their centres float from y = 0 to y = 2.
#   0 is your eye height at the start; the lowest cube's bottom is then
#   at (0 - 0.5) = -0.5, half a unit above the floor (FLOOR_Y = -1).
PICKUP_LOW = 0
PICKUP_HIGH = 2

# (Lesson 7) the 8 spots the cubes start at, in WORLD coordinates.
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

# (Lesson 7) COLLECT_RADIUS = 1.0: you collect a cube when your eye is
#   1 unit or less from its CENTRE. Its faces are 0.5 from the centre,
#   so your nose is then 0.5 from a face, which fills the window:
#   ((1 * 400) / 0.5) = 800 px wide (lesson Part 3).
COLLECT_RADIUS = 1.0

# (Lesson 7) MIN_SPAWN_DISTANCE = 5: a new cube never appears closer than
#   5 to you, so it is at least (5 / 3) = 1.7 seconds of flying away.
MIN_SPAWN_DISTANCE = 5

# ---- (step 1): ROCKS, big scenery cubes (lesson Part 1) -------------------
# ROCK_SIZE = 1.5: Lesson 5's "size", so a rock is (2 * 1.5) = 3 units
#   wide, 3 times a gold cube. Big enough that you can fly right up
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

# ROCK_CLEARANCE = 3: a new gold cube must be at least 3 from every
#   rock's centre: 1.5 (half a rock) + 0.5 (half a gold cube) + 1 (your
#   COLLECT_RADIUS, so you can always reach it) = 3.
ROCK_CLEARANCE = ( (ROCK_SIZE + PICKUP_SIZE) + COLLECT_RADIUS )

# ---- (Lesson 7) how high and low you can fly (lesson Part 5) -----------------
# GROUND = -0.5: your eye stays half a unit above the floor (y = -1).
# CEILING = 4: two more than PICKUP_HIGH, so you can look down on every
#   cube but never fly off where none could be.
GROUND = (FLOOR_Y + 0.5)     # (-1 + 0.5) = -0.5
CEILING = 4

# ---- (Lesson 7) the clock (lesson Part 6) -------------------------------------
# 60 seconds: at 3 units a second that is (3 * 60) = 180 units of
# flying, enough for a good handful of cubes, short enough to retry.
GAME_SECONDS = 60


def make_pickups():
    """(Lesson 7) build a fresh list of 8 pickup THINGS (Lesson 5's
    dictionaries), one at each START_SPOTS position.

    Each one is a small gold cube (size 0.5) that spins slowly so it
    catches your eye: 1 degree a frame of turn = one turn in 6 seconds,
    and 0.5 of tip so it wobbles a little too.
    """
    pickups = []
    for spot in START_SPOTS:
        pickups.append({"model": cube_model, "position": spot,
                        "size": PICKUP_SIZE, "angles": [0, 0, 0],
                        "speeds": (0.5, 1, 0), "colour": SUN_GOLD,
                        "pickup": True})          # (step 1)
    return pickups


def make_rocks():
    """(step 1): build a list of 4 rock THINGS, one at each ROCK_SPOTS position.

    Same dictionary keys as a gold cube, with three differences:
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
    """(step 1): the whole world = 8 gold cubes + 4 rocks.

    "+" joins two lists into one longer list: (8 + 4) = 12 things.
    The gold cubes come first, so things[0] is still cube 0.
    """
    return (make_pickups() + make_rocks())


# "things" is Lesson 5's list of everything in the world.
# (step 1): 8 gold cubes AND 4 rocks.
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
# (step 2): K turns clipping on / off, so you can see the difference.
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

    NEW in Lesson 8: each face is CLIPPED in CAMERA coordinates first,
    and only then projected. So we no longer project every corner up
    front: a face's cut points only exist once that face is clipped.
    """
    model = thing["model"]
    camera_points = []
    for p in model["points"]:
        world = to_world(p, thing)                     # WORLD
        camera_points.append(to_camera(world))         # CAMERA

    for corners, face_colour, pointer in model["faces"]:
        # NEW: this face's corners in CAMERA coordinates, clockwise.
        face_camera = []
        for corner_number in corners:
            face_camera.append(camera_points[corner_number])

        if use_clipping:
            # NEW: cut the face at the NEAR wall (lesson Part 3).
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
    """(step 2): the floor grid as LONG lines, right across the field.

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
    """(step 2): one long floor line, WORLD -> CAMERA -> clip -> SCREEN."""
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
    """(step 2): the CAMERA point where the line from point_a to point_b
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
    """(step 2): keep the part of a CAMERA line that is in front of NEAR.

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
    """NEW: cut one face at the NEAR wall (lesson Part 3).

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


def far_from_rocks(spot):
    """(step 1): True if this WORLD spot is at least ROCK_CLEARANCE (3) from
    the centre of every rock, so a new gold cube never hides inside one.

    Worked example (lesson Part 1): spot (1, 1, 5) and rock 0 at
    (0, 0.5, 4): math.sqrt( (1 * 1) + (0.5 * 0.5) + (1 * 1) ) = 1.5,
    less than 3, so False: try again.
    """
    for rock_spot in ROCK_SPOTS:
        if distance_3d(spot, rock_spot) < ROCK_CLEARANCE:
            return False
    return True


def new_pickup_spot():
    """(Lesson 7) a random WORLD spot for a cube, at least
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
        # (step 1): "and far_from_rocks(spot)": BOTH must be True.
        if (distance_3d(you, spot) >= MIN_SPAWN_DISTANCE) and far_from_rocks(spot):
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
    # (Lesson 7) the walls: from map (-12, 12) to map (12, -12)
    wall_left, wall_top = to_map((-WALL), WALL)          # (638, 438)
    wall_size = ( (2 * WALL) * MAP_SCALE )                # (24 * 6) = 144
    pygame.draw.rect(screen, WALL_RED,
                     pygame.Rect(wall_left, wall_top, wall_size, wall_size), 1)
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
            if event.key == pygame.K_k:                  # (step 2)
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
                things = make_world()      # (step 1): cubes AND rocks
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

        # ---- (Lesson 7) collect any cube you are touching (Part 3) -----
        you = (cam_x, cam_y, cam_z)
        for thing in things:
            # (step 1): rocks have "pickup": False, so they are never collected.
            if not thing["pickup"]:
                continue
            if distance_3d(you, thing["position"]) <= COLLECT_RADIUS:
                score = (score + 1)
                # (Lesson 7) the same cube jumps to a new spot (Part 4):
                # there are always exactly 8 cubes to find.
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

    # ---- (Lesson 7) how far is the nearest cube? -------------------------
    # Start with a huge number, then keep the smallest distance found.
    nearest = 1000
    for thing in things:
        if not thing["pickup"]:          # (step 1): rocks don't count
            continue
        d = distance_3d((cam_x, cam_y, cam_z), thing["position"])
        if d < nearest:
            nearest = d

    # ---- The HUD: words drawn LAST, so no cube can hide them -----------
    # str() turns a number into letters so + can join it to words.
    text = ("score " + str(score) + "   best " + str(best_score))
    screen.blit(font.render(text, True, SUN_GOLD), (20, 20))
    text = ("nearest cube " + str(round(nearest, 1)))
    screen.blit(font.render(text, True, PINK), (20, 50))
    # (step 2): say whether clipping is on, so screenshots are never confusing.
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
#   * Press K while you fly past a rock, to see Lesson 7's skipping
#     again. Then press K to turn clipping back on.
#   * Print len(face_camera) after clip_face() for rock 0 only. Fly
#     round it: can you find a 3, a 4 and a 5?
#   * Set NEAR = 1. Clipping still works, but now you can see the wall
#     slicing the rock 1 unit in front of you. Why is 0.1 a better
#     choice? (Lesson 4, Fig 4.3.3.)
#   * Draw each cut point as a small white circle, so you can watch it
#     slide along the edge as you move.
#   * Lesson 9 loads big models from files. They have many more faces
#     crossing NEAR when you get close: clipping is ready for them.
# ----------------------------------------------------------------------
