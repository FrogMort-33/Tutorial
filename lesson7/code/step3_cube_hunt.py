# ======================================================================
# LESSON 7 - STEP 3: CUBE HUNT (the finished game)
# ----------------------------------------------------------------------
# Goal: a real game. Fly round the field, touch as many gold cubes as
# you can in 60 seconds, then try to beat your best score.
#
# This is the LAST script of the course. It is Lesson 6's finished
# script (step3_camera_matrix.py) plus the game parts from Lesson 7.
#
# What is new since step 2:
#
#   1. FLY WHERE YOU LOOK (lesson Part 5)
#        Lesson 6 walked level: forward = column 2 of turn_matrix.
#        Now the forward arrow is made from your tip AND your turn:
#            look    = combine(tip_matrix(cam_tip), turn_matrix(cam_turn))
#            forward = column(look, 2)
#        Look up 30 degrees and W climbs: forward = (0, 0.5, 0.866).
#
#   2. WALLS, GROUND AND CEILING (lesson Part 5)
#        After moving, any number past its limit is put back ON it:
#            cam_x and cam_z stay between -12 and 12  (WALL)
#            cam_y stays between -0.5 and 4           (GROUND, CEILING)
#
#   3. THE CLOCK (lesson Part 6)
#        frames_left starts at (60 * 60) = 3600 and loses 1 a frame.
#        The screen shows math.ceil(frames_left / 60) seconds.
#
#   4. GAME OVER AND PLAY AGAIN (lesson Part 6)
#        game_over = True when the clock hits 0. Nothing moves, the
#        big "TIME UP" shows, and R starts a new game.
#        best_score remembers your best until you close the window.
#
# The game, every frame:
#
#   keys -> fly -> walls -> collect? (distance <= 1) -> clock -> draw world -> HUD
#
# Controls:  LEFT / RIGHT = turn,   UP / DOWN = look up / down
#            W / S = fly forward / back (the way you LOOK)
#            A / D = slide left / right,   Q / E = straight down / up
#            R = play again (after TIME UP)
#            G = floor grid on / off,   L = light on / off
# Run:  python step3_cube_hunt.py
# ======================================================================

import math
import random                 # (step 2) for random.uniform
import pygame

pygame.init()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 7, step 3 - Cube Hunt")
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
#   square. You fly 3 units a second, so edge to edge is
#   (20 / 3) = 6.7 seconds: some flying, but never boring.
# WALL = 12: you can't fly further than 12 from the centre, 2 more than
#   FIELD, so you can always fly round a cube at the edge.
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
#   5 to you, so it is at least (5 / 3) = 1.7 seconds of flying away.
MIN_SPAWN_DISTANCE = 5

# ---- NEW: how high and low you can fly (lesson Part 5) -----------------
# GROUND = -0.5: your eye stays half a unit above the floor (y = -1).
# CEILING = 4: two more than PICKUP_HIGH, so you can look down on every
#   cube but never fly off where none could be.
GROUND = (FLOOR_Y + 0.5)     # (-1 + 0.5) = -0.5
CEILING = 4

# ---- NEW: the clock (lesson Part 6) -------------------------------------
# 60 seconds: at 3 units a second that is (3 * 60) = 180 units of
# flying, enough for a good handful of cubes, short enough to retry.
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
            # NEW: R only works after TIME UP, so you can't restart by
            # accident in the middle of a good game.
            if (event.key == pygame.K_r) and game_over:
                # Every game number back to its start value...
                cam_x = 0
                cam_y = 0
                cam_z = 0
                cam_turn = 0
                cam_tip = 0
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

        # ---- NEW: fly where you LOOK (lesson Part 5) -----------------
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
            cam_y = (cam_y + (forward_y * MOVE_SPEED))   # NEW: y too
            cam_z = (cam_z + (forward_z * MOVE_SPEED))
        if keys[pygame.K_s]:
            cam_x = (cam_x - (forward_x * MOVE_SPEED))
            cam_y = (cam_y - (forward_y * MOVE_SPEED))   # NEW: y too
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

        # ---- NEW: walls, ground and ceiling (lesson Part 5) ----------
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
    # NEW: math.ceil rounds UP, so the clock never shows 0 while you
    # can still play: 59.98 seconds left shows as 60.
    seconds = math.ceil(frames_left / 60)
    screen.blit(font.render("time " + str(seconds), True, WHITE), (680, 20))
    screen.blit(font.render("ARROWS look,  W / S fly,  A / D slide,  Q / E down / up",
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
#   * Make it harder: COLLECT_RADIUS = 0.75, or GAME_SECONDS = 30.
#   * Make a "+1" float up from the middle of the screen for half a
#     second after each collect. Hint: a variable that counts down
#     from 30 frames, set to 30 when you score.
#   * Put Lesson 5's pyramid_model back as scenery (copy its points
#     and faces from Lesson 6), and add a few pyramids to things with
#     a "pickup": False key. Only collect things whose "pickup" is True.
#   * Add a red cube that takes 5 seconds OFF the clock if you touch it.
#   * Show an arrow on the HUD pointing at the nearest cube. Hint:
#     to_camera() its position, then look at the sign of its x.
# ----------------------------------------------------------------------
