# ======================================================================
# LESSON 6 - STEP 3: THE CAMERA MATRIX (the finished script of Lesson 6)
# ----------------------------------------------------------------------
# Goal: no more separate turns ANYWHERE. Every turn in the program is a
# matrix. The world still looks exactly like Lesson 5.
#
# What is new since step 2:
#
#   1. camera_matrix: Lesson 4's "undo your turn, then undo your tip",
#      joined into ONE grid, built ONCE per frame:
#          camera_matrix = combine(turn_matrix(-cam_turn),
#                                  tip_matrix(-cam_tip))
#      The camera is the same for every thing AND every floor line, so
#      one grid serves them all (over 1,100 points a frame).
#
#   2. to_camera() keeps its name, but now does:
#          subtract where you stand -> matrix_times_point(camera_matrix, ...)
#
#   3. Walking: the forward and right arrows are COLUMNS of your turn
#      matrix (lesson Part 3: a column = where an axis arrow lands):
#          forward = column 2 (where +z lands)
#          right   = column 0 (where +x lands)
#
#   4. rotate_x and rotate_y are GONE. Nothing uses them any more.
#
#   5. M also shows the camera_matrix's 9 numbers. Turn left and right
#      and watch the cos / sin pattern of Part 3 appear in them.
#
# The recipe for one corner of one thing, every frame:
#
#   SHAPE -> * size -> x spin matrix -> + position -> - camera -> x camera_matrix -> NEAR -> project
#   (model points)                     (WORLD)                                    (CAMERA)          (SCREEN)
#
# Controls:  LEFT / RIGHT = turn,   UP / DOWN = look up / down
#            W / S = walk forward / back,   A / D = step left / right
#            Q / E = go down / up
#            SPACE = pause the spinning,   R = reset
#            L = light on / off,   C = one colour per thing / face colours
#            G = floor grid on / off,   M = matrix numbers on / off
# Run:  python step3_camera_matrix.py
# ======================================================================

import math
import pygame

pygame.init()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 6, step 3 - the camera matrix")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
PINK = (255, 105, 200)        # the colour we use for YOU (the camera)
MAP_BACK = (25, 30, 36)       # dark grey-blue behind the mini-map
GRID_COLOUR = (40, 90, 70)    # (Lesson 5) dim green for the floor lines.
                              # Dim on purpose: the floor is background,
                              # so it must not shout louder than the shapes.

# ---- One colour for each face direction (from Lesson 3) ---------------
RED = (235, 80, 80)          # faces pointing to the front (-z)
PURPLE = (160, 100, 230)     # faces pointing to the back  (+z)
BLUE = (70, 150, 255)        # faces pointing left         (-x)
GREEN = (70, 210, 120)       # faces pointing right        (+x)
GOLD = (245, 200, 60)        # faces pointing up           (+y)
ORANGE = (245, 140, 50)      # faces pointing down         (-y)

# ---- One colour for each THING (C key) --------------------------------
CUBE_GREEN = (70, 230, 120)
SKY_BLUE = (90, 170, 255)
SUN_GOLD = (250, 200, 70)
CORAL = (250, 120, 100)
LILAC = (190, 140, 255)
TEAL = (60, 210, 200)
ROSE = (255, 110, 170)

# ---- (step 2) colours for the matrix numbers, like the diagrams ----
ROW_X_BLUE = (90, 170, 255)      # row 0 makes the new x
ROW_Y_YELLOW = (255, 214, 64)    # row 1 makes the new y
ROW_Z_ORANGE = (255, 160, 60)    # row 2 makes the new z

CENTRE_X = (WIDTH / 2)            # (800 / 2) = 400
CENTRE_Y = (HEIGHT / 2)           # (600 / 2) = 300
FOCAL = 400


# ======================================================================
# MODELS: the shape of a thing, in SHAPE coordinates (its own centre)
# ======================================================================

# ---- The cube's 8 corners (same as every lesson) ----------------------
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

# ---- The cube's 6 faces -----------------------------------------------
# (Lesson 5) each face is now THREE things:
#   (corners clockwise from outside,  colour,  pointer)
# The pointer is the arrow straight out of the face, 1 unit long.
# For a cube it is easy: the front face points to -z, so (0, 0, -1).
cube_faces = [
    ((4, 5, 1, 0), RED,    ( 0,  0, -1)),   # front
    ((6, 7, 3, 2), PURPLE, ( 0,  0,  1)),   # back
    ((7, 4, 0, 3), BLUE,   (-1,  0,  0)),   # left
    ((5, 6, 2, 1), GREEN,  ( 1,  0,  0)),   # right
    ((7, 6, 5, 4), GOLD,   ( 0,  1,  0)),   # top
    ((2, 3, 0, 1), ORANGE, ( 0, -1,  0)),   # bottom
]

# ---- (Lesson 5) the pyramid's 5 corners ------------------------------------
# Corners 0 to 3 are EXACTLY the cube's 4 bottom corners, with the same
# numbers. Corner 4 is the tip, straight above the centre, at the
# height of the cube's top (y = 1). So a pyramid is the same height and
# width as a cube: 2 units each way.
pyramid_points = [
    (-1, -1, -1),   # 0  bottom-left-front
    ( 1, -1, -1),   # 1  bottom-right-front
    ( 1, -1,  1),   # 2  bottom-right-back
    (-1, -1,  1),   # 3  bottom-left-back
    ( 0,  1,  0),   # 4  the tip
]

# ---- (Lesson 5) the pyramid's 5 faces --------------------------------------
# Four TRIANGLES (3 corners each) and one square base (4 corners).
# Still clockwise as seen from outside. Each triangle starts at the tip.
# The sloping pointers were worked out in the lesson (Part 2):
#   the slope rises 2 for every 1 across, so the arrow out of it is
#   (2 out, 1 up), shrunk to 1 unit long: divide by 2.236 (the square
#   root of ((2 * 2) + (1 * 1)) = 5)  ->  (0.894 out, 0.447 up).
pyramid_faces = [
    ((4, 1, 0),    RED,    ( 0,     0.447, -0.894)),   # front slope
    ((4, 3, 2),    PURPLE, ( 0,     0.447,  0.894)),   # back slope
    ((4, 0, 3),    BLUE,   (-0.894, 0.447,  0)),       # left slope
    ((4, 2, 1),    GREEN,  ( 0.894, 0.447,  0)),       # right slope
    ((2, 3, 0, 1), ORANGE, ( 0,    -1,      0)),       # base (bottom)
]

# ---- (Lesson 5) a MODEL = a shape's points and faces, kept together --------
cube_model = {"points": cube_points, "faces": cube_faces}
pyramid_model = {"points": pyramid_points, "faces": pyramid_faces}


# ======================================================================
# THE WORLD
# ======================================================================

# ---- (Lesson 5) the floor ------------------------------------------------------
# FLOOR_Y = -1: the bottom of the old cube (centre y 0, half-height 1).
# Your eye starts at y = 0, so you stand 1 unit above the floor.
FLOOR_Y = -1
# The grid covers exactly what the mini-map shows (see MAP_ below):
#   x from -8 to 8   (16 units across)
#   z from -3 to 13  (16 units deep, starting a little behind you)
GRID_LEFT = -8
GRID_RIGHT = 8
GRID_NEAR = -3
GRID_FAR = 13

# ---- (Lesson 5) THINGS: every shape in the world, in one list --------------
# Each thing is a dictionary (from the Python lists course):
#   "model"    - which shape (cube_model or pyramid_model)
#   "position" - where its centre is, in WORLD coordinates
#   "size"     - (Lesson 5) 1 = normal, 2 = twice as big, 0.5 = half
#   "angles"   - (Lesson 5) its spin right now: [tip, turn, roll] in degrees
#   "speeds"   - (Lesson 5) how many degrees it spins each frame (tip, turn, roll)
#   "colour"   - its one colour when you press C
#
# A thing SITS ON THE FLOOR when its centre y = (FLOOR_Y + size):
#   size 1   -> y = (-1 + 1)   = 0
#   size 2   -> y = (-1 + 2)   = 1
#   size 0.5 -> y = (-1 + 0.5) = -0.5
#
# The list order does NOT matter: all faces are sorted together later.
things = [
    # The old cube, in its old place, standing still: corner 5 is at
    # WORLD (1, 1, 4) like in every lesson so far.
    {"model": cube_model, "position": (0, 0, 5), "size": 1,
     "angles": [0, 0, 0], "speeds": (0, 0, 0), "colour": CUBE_GREEN},

    # (Lesson 5) a pyramid behind it and to the left. Its tip is at WORLD
    # (-2.5, 1, 8), which lands on the screen at exactly (275, 250).
    {"model": pyramid_model, "position": (-2.5, 0, 8), "size": 1,
     "angles": [0, 0, 0], "speeds": (0, 1, 0), "colour": SUN_GOLD},

    # (Lesson 5) a BIG cube, size 2, sitting on the floor (y = 1). Turns
    # slowly: 0.5 a frame = 30 a second = one turn in 12 seconds.
    {"model": cube_model, "position": (4, 1, 9), "size": 2,
     "angles": [0, 0, 0], "speeds": (0, 0.5, 0), "colour": SKY_BLUE},

    # (Lesson 5) a SMALL cube, size 0.5, on the floor (y = -0.5), just to
    # the right of the old cube. Turns fast: 3 a frame = one turn in 2 s.
    {"model": cube_model, "position": (2, -0.5, 4), "size": 0.5,
     "angles": [0, 0, 0], "speeds": (0, 3, 0), "colour": CORAL},

    # (Lesson 5) a cube floating up high, tumbling with Lesson 2B's speeds.
    # It is off the floor, so it can tip and roll without hitting it.
    {"model": cube_model, "position": (-1.5, 2.5, 9), "size": 0.5,
     "angles": [0, 0, 0], "speeds": (0.5, 1, 0.25), "colour": LILAC},

    # (Lesson 5) a big pyramid far away on the left, turning the OTHER way
    # (a negative speed turns clockwise seen from above).
    {"model": pyramid_model, "position": (-6, 1, 11), "size": 2,
     "angles": [0, 0, 0], "speeds": (0, -0.5, 0), "colour": TEAL},

    # (Lesson 5) a pyramid BEHIND you at the start (z = -2). Turn round to
    # find it: hold LEFT for 2 seconds (180 degrees).
    {"model": pyramid_model, "position": (0, 0, -2), "size": 1,
     "angles": [0, 0, 0], "speeds": (0, 2, 0), "colour": ROSE},
]

# ---- Where YOU are (from Lesson 4, unchanged) ------------------------
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

spinning = True        # (Lesson 5) SPACE pauses every thing's spin
use_light = True
one_colour = True      # (Lesson 5) default one colour per thing: in a world
                       # full of shapes, it tells the THINGS apart
show_grid = True       # G turns the floor grid off and on (Lesson 5)
show_matrices = True   # (step 2) M hides the matrix numbers

# ---- The mini-map (from Lesson 4, unchanged) --------------------------
MAP_LEFT = 630
MAP_TOP = 430
MAP_SIZE = 160
MAP_CX = (MAP_LEFT + (MAP_SIZE / 2))    # (630 + 80) = 710
MAP_CY = (MAP_TOP + 130)                # (430 + 130) = 560
MAP_SCALE = 10                          # 10 px for every 1 world unit


# ======================================================================
# FUNCTIONS
# ======================================================================

# ======================================================================
# (step 1) MATRIX TOOLS - every turn as a 3 x 3 grid of numbers
# ======================================================================
# A matrix is a tuple of 3 ROWS, each a tuple of 3 numbers.
#   matrix[2][0] means row 2, column 0.
# Row 0 makes the new x, row 1 the new y, row 2 the new z.

def matrix_times_point(matrix, point_3d):
    """(step 1) put one point through a matrix: each ROW is dotted with
    the point (Lesson 3's dot product) to make one new number.

    turn_matrix(30) x corner 5 (1, 1, -1):
        new_x = (0.866 * 1) + (0 * 1) + (-0.5 * -1)  = 1.366
        new_y = (0 * 1)     + (1 * 1) + (0 * -1)     = 1
        new_z = (0.5 * 1)   + (0 * 1) + (0.866 * -1) = -0.366
    """
    row_0, row_1, row_2 = matrix
    new_x = dot(row_0, point_3d)
    new_y = dot(row_1, point_3d)
    new_z = dot(row_2, point_3d)
    return (new_x, new_y, new_z)


def tip_matrix(angle_degrees):
    """(step 1) Lesson 2B's TIP (rotate_x) as a grid. x is the skewer."""
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    return (
        (1, 0,     0         ),
        (0, cos_a, (-sin_a)  ),
        (0, sin_a, cos_a     ),
    )


def turn_matrix(angle_degrees):
    """(step 1) Lesson 2's TURN (rotate_y) as a grid. y is the skewer."""
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    return (
        (cos_a, 0, (-sin_a)),
        (0,     1, 0       ),
        (sin_a, 0, cos_a   ),
    )


def roll_matrix(angle_degrees):
    """(step 1) Lesson 2B's ROLL (rotate_z) as a grid. z is the skewer."""
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    return (
        (cos_a, (-sin_a), 0),
        (sin_a, cos_a,    0),
        (0,     0,        1),
    )


def column(matrix, column_number):
    """(step 1) one COLUMN of a matrix, top to bottom.
    Column 0 = where +x (1, 0, 0) lands, column 1 = where +y lands,
    column 2 = where +z lands."""
    row_0, row_1, row_2 = matrix
    return (row_0[column_number], row_1[column_number], row_2[column_number])


def combine(first, second):
    """(step 1) ONE matrix that does 'first', then 'second'.
    Put each column of 'first' (where it left each axis arrow) through
    'second'. The three answers are the columns of the joined matrix."""
    new_col_0 = matrix_times_point(second, column(first, 0))
    new_col_1 = matrix_times_point(second, column(first, 1))
    new_col_2 = matrix_times_point(second, column(first, 2))
    # Columns worked out -> stored back as rows.
    return (
        (new_col_0[0], new_col_1[0], new_col_2[0]),
        (new_col_0[1], new_col_1[1], new_col_2[1]),
        (new_col_0[2], new_col_1[2], new_col_2[2]),
    )


def spin_matrix(angles):
    """(step 2) a thing's whole spin as ONE matrix: tip, then turn, then
    roll (Lesson 2B's order). It replaces Lesson 5's rotate_all.
    angles is the thing's list [tip, turn, roll] in degrees.
    spin_matrix([30, 30, 30]) x corner 5 = (0.225, 1.708, 0.183),
    the same as Lesson 2B."""
    tip_then_turn = combine(tip_matrix(angles[0]), turn_matrix(angles[1]))
    return combine(tip_then_turn, roll_matrix(angles[2]))


def to_world(shape_point, thing):
    """(Lesson 5) one SHAPE point of a thing -> a WORLD point.

    1. size:  multiply by the thing's size (grow or shrink round its
              own centre).
    2. spin:  CHANGED (Lesson 6): put it through the thing's spin
              matrix, thing["matrix"], built once this frame.
    3. place: add the thing's position.

    Worked example (lesson Part 5): the small cube, size 0.5, still,
    at (2, -0.5, 4). Its corner 5 is SHAPE (1, 1, -1):
        1. ((1 * 0.5), (1 * 0.5), (-1 * 0.5)) = (0.5, 0.5, -0.5)
        2. angles 0 -> the do-nothing matrix   = no change
        3. ((0.5 + 2), (0.5 + -0.5), (-0.5 + 4)) = (2.5, 0, 3.5)
    """
    x, y, z = shape_point
    size = thing["size"]
    sized = ( (x * size), (y * size), (z * size) )         # 1. size
    spun = matrix_times_point(thing["matrix"], sized)       # 2. spin
    pos_x, pos_y, pos_z = thing["position"]
    sx, sy, sz = spun
    return ( (sx + pos_x), (sy + pos_y), (sz + pos_z) )     # 3. place


def to_camera(world_point):
    """One WORLD point -> one CAMERA point (from Lesson 4).

    CHANGED (step 3): subtract where you stand, then ONE matrix does
    both "undo your turn" and "undo your tip". camera_matrix is built
    once per frame in the main loop, before anything is drawn.

    Worked example (lesson Part 5): you at (2, 0, 1), cam_turn 30,
    cam_tip 0, corner 5 at WORLD (1, 1, 4):
        1. ((1 - 2), (1 - 0), (4 - 1))          = (-1, 1, 3)
        2. camera_matrix x (-1, 1, 3)
             new_x = (0.866 * -1) + (0 * 1) + (0.5 * 3)   = 0.634
             new_y = (0 * -1)     + (1 * 1) + (0 * 3)     = 1
             new_z = (-0.5 * -1)  + (0 * 1) + (0.866 * 3) = 3.098
    """
    x, y, z = world_point
    moved = ( (x - cam_x), (y - cam_y), (z - cam_z) )      # 1. subtract
    return matrix_times_point(camera_matrix, moved)        # 2. both undos


def project(point_3d):
    """One CAMERA point -> one SCREEN point (from Lesson 1).
    Only ever call this with z >= NEAR, so we never divide by 0."""
    x, y, z = point_3d
    screen_x = CENTRE_X + ( (x * FOCAL) / z )
    screen_y = CENTRE_Y - ( (y * FOCAL) / z )
    return (screen_x, screen_y)


def average_z(corners, camera_points):
    """How far away is this face? (from Lesson 3, uses CAMERA points).

    It divides by len(corners), so it works for a triangle (3 corners)
    just as well as for a square (4). Nothing to change!
    """
    total = 0
    for corner_number in corners:
        x, y, z = camera_points[corner_number]
        total = (total + z)
    return (total / len(corners))


def is_facing_you(face_points):
    """The clock test (from Lesson 3, unchanged). It only looks at the
    first 3 corners, so it works for triangles too."""
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
    """The dot product (from Lesson 3)."""
    x1, y1, z1 = arrow_1
    x2, y2, z2 = arrow_2
    return ( (x1 * x2) + (y1 * y2) + (z1 * z2) )


def shade_colour(colour, pointer):
    """Brighter when the face points at the light (from Lesson 3)."""
    brightness = dot(pointer, LIGHT)
    if brightness < 0:
        brightness = 0
    shade = ( AMBIENT + ( (1 - AMBIENT) * brightness ) )
    red, green, blue = colour
    return ( round(red * shade), round(green * shade), round(blue * shade) )


def keep_under_360(angle):
    """Keep an angle between 0 and 360.
    (Lesson 5) CHANGED: a NEGATIVE speed (the big pyramid) counts DOWN,
    so we also add 360 when it drops below 0."""
    if angle >= 360:
        angle = (angle - 360)
    if angle < 0:
        angle = (angle + 360)
    return angle


def add_faces_of(thing, faces_to_draw):
    """(Lesson 5) work out every face of ONE thing and add the ones we
    should paint to the shared list faces_to_draw.

    This is Lesson 4's face loop, moved into a function so we can run
    it once for EACH thing. Every thing adds to the SAME list, so the
    painter's sort later sees all faces of all things together.
    """
    model = thing["model"]

    # ---- spin -> place -> camera, for every corner of this thing ----
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
        # 0. skip the face if ANY corner is too close or behind you.
        too_close = False
        for corner_number in corners:
            if camera_points[corner_number][2] < NEAR:
                too_close = True
        if too_close:
            continue

        face_points = []
        for corner_number in corners:
            face_points.append(screen_points[corner_number])

        # 1. The clock test (Lesson 3).
        if not is_facing_you(face_points):
            continue

        # 2. How far away is it? (CAMERA z, Lesson 4)
        distance = average_z(corners, camera_points)

        # 3. What colour?
        colour = face_colour
        if one_colour:
            colour = thing["colour"]
        if use_light:
            # The pointer must spin WITH the thing, so it goes through
            # the SAME spin matrix (Lesson 6). We do NOT multiply it by the size:
            # a bigger face still points the same way, and the arrow
            # must stay exactly 1 long for the light maths.
            spun_pointer = matrix_times_point(thing["matrix"], pointer)
            colour = shade_colour(colour, spun_pointer)

        faces_to_draw.append( (distance, face_points, colour) )


def draw_floor():
    """(Lesson 5) draw the floor grid at y = FLOOR_Y, in 1-unit pieces.

    Two sets of lines:
      * lines running AWAY from you (fixed x, z changes)
      * lines running ACROSS        (fixed z, x changes)
    Each line is cut into pieces 1 unit long. A piece is drawn only if
    BOTH its ends are in front of you (CAMERA z >= NEAR). A short piece
    means only a short gap at your feet, not a missing line.
    """
    # Lines running away: x = -8, -7, ... 8.  range() stops BEFORE the
    # end number, so we add 1 to include 8 itself.
    for x in range(GRID_LEFT, (GRID_RIGHT + 1)):
        for z in range(GRID_NEAR, GRID_FAR):
            draw_floor_piece( (x, FLOOR_Y, z), (x, FLOOR_Y, (z + 1)) )
    # Lines running across: z = -3, -2, ... 13.
    for z in range(GRID_NEAR, (GRID_FAR + 1)):
        for x in range(GRID_LEFT, GRID_RIGHT):
            draw_floor_piece( (x, FLOOR_Y, z), ((x + 1), FLOOR_Y, z) )


def draw_floor_piece(world_start, world_end):
    """(Lesson 5) one 1-unit piece of floor line, WORLD -> CAMERA -> SCREEN."""
    start = to_camera(world_start)
    end = to_camera(world_end)
    if (start[2] < NEAR) or (end[2] < NEAR):
        return                                   # behind you: skip it
    pygame.draw.line(screen, GRID_COLOUR, project(start), project(end), 1)



def draw_matrix(matrix, name, left, top):
    """(step 2) draw a matrix's 9 numbers in a small box, rounded to 2
    places. Rows are coloured like the lesson's diagrams:
    row 0 (new x) blue, row 1 (new y) yellow, row 2 (new z) orange.
    The box is 220 x 110 px."""
    box = pygame.Rect(left, top, 220, 110)
    pygame.draw.rect(screen, MAP_BACK, box)
    pygame.draw.rect(screen, WHITE, box, 1)
    screen.blit(font.render(name, True, WHITE), ((left + 8), (top + 6)))
    row_colours = (ROW_X_BLUE, ROW_Y_YELLOW, ROW_Z_ORANGE)
    for row_number in range(3):
        row = matrix[row_number]
        for column_number in range(3):
            # round(..., 2) + 0 : 2 decimal places, and no "-0.0"
            number = (round(row[column_number], 2) + 0)
            text = font.render(str(number), True, row_colours[row_number])
            x = (left + 12 + (column_number * 70))
            y = (top + 32 + (row_number * 25))
            screen.blit(text, (x, y))


def to_map(x, z):
    """A WORLD (x, z) -> a pixel on the mini-map (from Lesson 4)."""
    map_x = MAP_CX + (x * MAP_SCALE)
    map_y = MAP_CY - (z * MAP_SCALE)
    return (map_x, map_y)


def draw_map():
    """Draw the mini-map: every thing's base and you, from above.

    (Lesson 5) a loop over ALL things. Corners 0, 1, 2, 3 are the bottom
    corners of BOTH models (that is why the pyramid's base uses the
    cube's numbers), so the same 4 numbers work for every thing.
    """
    box = pygame.Rect(MAP_LEFT, MAP_TOP, MAP_SIZE, MAP_SIZE)
    pygame.draw.rect(screen, MAP_BACK, box)
    screen.set_clip(box)
    for thing in things:
        outline = []
        for corner_number in (0, 1, 2, 3):
            corner = thing["model"]["points"][corner_number]
            x, y, z = to_world(corner, thing)
            outline.append(to_map(x, z))
        pygame.draw.polygon(screen, thing["colour"], outline, 2)
    # (step 3) your forward arrow = column 2 of your turn matrix.
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
            if event.key == pygame.K_SPACE:
                spinning = not spinning
            if event.key == pygame.K_l:
                use_light = not use_light
            if event.key == pygame.K_c:
                one_colour = not one_colour
            if event.key == pygame.K_g:
                show_grid = not show_grid
            if event.key == pygame.K_m:          # (step 2)
                show_matrices = not show_matrices
            if event.key == pygame.K_r:          # back to the start
                cam_x = 0
                cam_y = 0
                cam_z = 0
                cam_turn = 0
                cam_tip = 0
                for thing in things:
                    thing["angles"] = [0, 0, 0]

    # ---- Keys you HOLD (from Lesson 4, unchanged) ---------------------
    keys = pygame.key.get_pressed()
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

    # ---- (step 3) which way is forward and right? -------------------
    # Lesson 4 turned the arrows (0, 0, 1) and (1, 0, 0) with rotate_y.
    # A matrix's columns ARE where those arrows land (lesson Part 3),
    # so we just read them out of your turn matrix:
    #   cam_turn 30: forward = column 2 = (-0.5, 0, 0.866)
    #                right   = column 0 = (0.866, 0, 0.5)
    # (Your tip is NOT used, so you still walk level, as in Lesson 4.)
    body_turn = turn_matrix(cam_turn)
    forward_x, forward_y, forward_z = column(body_turn, 2)
    right_x, right_y, right_z = column(body_turn, 0)
    if keys[pygame.K_w]:
        cam_x = (cam_x + (forward_x * MOVE_SPEED))
        cam_z = (cam_z + (forward_z * MOVE_SPEED))
    if keys[pygame.K_s]:
        cam_x = (cam_x - (forward_x * MOVE_SPEED))
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

    # ---- (Lesson 5) every thing spins at its OWN speeds --------------------
    if spinning:
        for thing in things:
            angles = thing["angles"]
            speeds = thing["speeds"]
            angles[0] = keep_under_360( (angles[0] + speeds[0]) )   # tip
            angles[1] = keep_under_360( (angles[1] + speeds[1]) )   # turn
            angles[2] = keep_under_360( (angles[2] + speeds[2]) )   # roll

    # ---- (step 2) build each thing's spin matrix ONCE this frame ----
    # Every corner, every face pointer and the mini-map then reuse it.
    for thing in things:
        thing["matrix"] = spin_matrix(thing["angles"])

    # ---- NEW: build the camera's matrix ONCE this frame -------------
    # Lesson 4's order: undo your turn FIRST, then undo your tip.
    # It is used by to_camera() for every thing and every floor line.
    camera_matrix = combine(turn_matrix(-cam_turn), tip_matrix(-cam_tip))

    screen.fill(BLACK)

    # ---- (Lesson 5) the floor first, so every shape is painted on top of it -
    if show_grid:
        draw_floor()

    # ---- (Lesson 5) ONE list for the faces of EVERY thing --------------------
    faces_to_draw = []
    for thing in things:
        add_faces_of(thing, faces_to_draw)

    # ---- The painter's method: furthest first, ALL faces together ----
    faces_to_draw.sort(reverse=True)
    for distance, face_points, colour in faces_to_draw:
        pygame.draw.polygon(screen, colour, face_points)
        pygame.draw.polygon(screen, BLACK, face_points, 2)

    draw_map()

    # ---- (step 2) the matrix numbers, top-right --------------------
    # things[4] is the floating LILAC cube: the only one that tips,
    # turns AND rolls, so all 9 of its numbers keep changing.
    if show_matrices:
        draw_matrix(things[4]["matrix"], "lilac cube spin", 570, 115)
        # NEW: the camera's grid. Turn with LEFT / RIGHT and watch it.
        draw_matrix(camera_matrix, "camera_matrix", 570, 235)

    text = ("you are at (" + str(round(cam_x, 2)) + ", " +
            str(round(cam_y, 2)) + ", " + str(round(cam_z, 2)) + ")")
    text = (text + "   turn " + str(round(cam_turn, 1)) +
            "   tip " + str(round(cam_tip, 1)))
    screen.blit(font.render(text, True, PINK), (20, 20))
    screen.blit(font.render("ARROWS = turn and look,  W A S D = walk,  Q / E = down / up", True, YELLOW), (20, 50))
    screen.blit(font.render("SPACE = pause,  R = reset,  L = light,  C = colours,  G = grid,  M = matrices", True, YELLOW), (20, 80))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

# ----------------------------------------------------------------------
# TRY THIS:
#   * Stand still, turn LEFT exactly 90 degrees (1 second) and read
#     camera_matrix. Compare it with the 90-degree grids in Part 4.
#   * Look down (DOWN arrow) and watch which numbers change. Why do
#     the middle row and middle column start to move?
#   * Fly where you look: build
#         look = combine(tip_matrix(cam_tip), turn_matrix(cam_turn))
#     and use column(look, 2) as the forward arrow for W and S.
#     (Lesson 7 uses this.)
#   * Count the work: add a counter to tip_matrix, turn_matrix and
#     roll_matrix (a global that goes up by 1 each call) and print it
#     once a second. Compare with the numbers in the lesson's Part 6.
# ----------------------------------------------------------------------
