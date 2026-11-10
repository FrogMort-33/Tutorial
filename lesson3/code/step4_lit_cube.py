# ======================================================================
# LESSON 3 - STEP 4: THE LIT SOLID CUBE (light and shade)
# ----------------------------------------------------------------------
# Goal: light the cube, so faces that point at the light are bright
# and faces that point away are dim. This is the final cube of Lesson 3
# and the starting point for Lesson 4.
#
# What is new since step 3:
#
#   1. face_pointer(corners, turned_points)
#        Every face of our cube has a "pointing arrow": the arrow from
#        the cube's centre (0, 0, 0) to the middle of the face. It points
#        straight OUT of the face and is exactly 1 long.
#        We find it by AVERAGING the face's 4 turned SHAPE corners.
#        Example, front face, not turned:  (0, 0, -1)  (straight at you)
#
#   2. LIGHT = (0.48, 0.6, -0.64)
#        An arrow pointing TOWARD the light: up, a little right, and
#        toward you. It is exactly 1 long too.
#
#   3. dot(arrow_1, arrow_2) - the DOT PRODUCT:
#        ( (x1 * x2) + (y1 * y2) + (z1 * z2) )
#        For two arrows of length 1 it tells you how much they point the
#        same way:   1 = same way,  0 = side-on,  -1 = opposite.
#
#   4. brightness = dot(pointer, LIGHT), never below 0
#      shade      = ( AMBIENT + ( (1 - AMBIENT) * brightness ) )
#      colour     = each of (red, green, blue) times shade
#
# The full recipe, every frame:
#
#   SHAPE corners -> tip, turn, roll -> add cube_distance -> project
#   then for each face:  clock test (skip?) -> average z -> light
#   then sort far -> near and paint.
#
# Controls:  SPACE = pause,  R = reset,
#            L = light on / off,   C = six colours / one colour
# Run:  python step4_lit_cube.py
# ======================================================================

import math
import pygame

pygame.init()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 3, step 2 - the painter's method")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# ---- NEW: one colour for each face ----------------------------------
# (red, green, blue), each 0 to 255. Six colours that are easy to tell
# apart, so you can always say WHICH face you are looking at.
RED = (235, 80, 80)          # front
PURPLE = (160, 100, 230)     # back
BLUE = (70, 150, 255)        # left
GREEN = (70, 210, 120)       # right
GOLD = (245, 200, 60)        # top
ORANGE = (245, 140, 50)      # bottom
CUBE_GREEN = (70, 230, 120)  # NEW: one colour for the whole cube, so you
                             # can see the light without six colours
                             # getting in the way. (C key swaps.)

CENTRE_X = (WIDTH / 2)            # (800 / 2) = 400
CENTRE_Y = (HEIGHT / 2)           # (600 / 2) = 300
FOCAL = 400

# ---- The cube's 8 corners, in SHAPE coordinates (same as always) ----
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

# ---- NEW: the cube's 6 faces -----------------------------------------
# An EDGE joins 2 corners.  A FACE joins 4 corners in a loop.
#
# Each face lists its 4 corners CLOCKWISE as you see that face from
# OUTSIDE the cube (stand in front of the face and look at it).
#   Example - the FRONT face, seen from in front:
#
#        4 -----> 5          4 = top-left,     5 = top-right
#        ^        |          1 = bottom-right, 0 = bottom-left
#        |        v
#        0 <----- 1          4 -> 5 -> 1 -> 0 goes round like a clock
#
# We do NOT need cube_edges any more: the outline of each face
# already includes all of the cube's edges.
cube_faces = [
    ((4, 5, 1, 0), RED),       # front  (all have z = -1)
    ((6, 7, 3, 2), PURPLE),    # back   (all have z = +1)
    ((7, 4, 0, 3), BLUE),      # left   (all have x = -1)
    ((5, 6, 2, 1), GREEN),     # right  (all have x = +1)
    ((7, 6, 5, 4), GOLD),      # top    (all have y = +1)
    ((2, 3, 0, 1), ORANGE),    # bottom (all have y = -1)
]

cube_distance = 5

# ---- NEW: the light ---------------------------------------------------
# LIGHT is an arrow pointing TOWARD the light (from the cube to the lamp):
#   x =  0.48  -> a little to the RIGHT
#   y =  0.6   -> UP
#   z = -0.64  -> TOWARD you (remember -z is toward you)
# Its length is root( (0.48 * 0.48) + (0.6 * 0.6) + (0.64 * 0.64) )
#             = root( 0.2304 + 0.36 + 0.4096 ) = root(1) = 1  exactly.
# Why these numbers? A lamp up, to the right and behind your shoulder is
# the classic way to light a model. At the start pose it gives the three
# faces you can see three very DIFFERENT brightnesses:
#   top 0.917 (bright),  front 0.388 (medium),  left -0.096 (in shadow)
LIGHT = (0.48, 0.6, -0.64)

# AMBIENT: light that comes from everywhere (the room, the sky).
# 0.2 means even a face in total shadow keeps 20% of its colour, so it
# never turns pure black and vanishes into the black background.
AMBIENT = 0.2

# ---- Angles and speeds (exactly as Lesson 2B, step 3) -----------------
# NEW: we START at a pose that shows three faces (front, left and top),
# the same pose as the lesson's diagrams: tipped -30 (top toward you)
# and turned 30. At 0, 0, 0 you would only see the front face.
START_X = -30
START_Y = 30
START_Z = 0
angle_x = START_X      # tip  so far, degrees
angle_y = START_Y      # turn so far, degrees
angle_z = START_Z      # roll so far, degrees
SPEED_X = 0.5          # 12 s per full tip
SPEED_Y = 1            #  6 s per full turn
SPEED_Z = 0.25         # 24 s per full roll
paused = False
use_light = True       # NEW: L key flips this
one_colour = True      # NEW: C key flips this (one colour / six colours)


# ---- The three turns (copied from Lesson 2B, unchanged) ---------------
def rotate_x(point_3d, angle_degrees):
    """TIP one SHAPE point around the x axis (+y swings toward +z)."""
    x, y, z = point_3d
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    new_x = x
    new_y = (y * cos_a) - (z * sin_a)
    new_z = (y * sin_a) + (z * cos_a)
    return (new_x, new_y, new_z)


def rotate_y(point_3d, angle_degrees):
    """TURN one SHAPE point around the y axis (+x swings toward +z)."""
    x, y, z = point_3d
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    new_x = (x * cos_a) - (z * sin_a)
    new_y = y
    new_z = (x * sin_a) + (z * cos_a)
    return (new_x, new_y, new_z)


def rotate_z(point_3d, angle_degrees):
    """ROLL one SHAPE point around the z axis (+x swings toward +y)."""
    x, y, z = point_3d
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    new_x = (x * cos_a) - (y * sin_a)
    new_y = (x * sin_a) + (y * cos_a)
    new_z = z
    return (new_x, new_y, new_z)


def rotate_all(point_3d):
    """Tip, then turn, then roll (the fixed order from Lesson 2B)."""
    p = rotate_x(point_3d, angle_x)    # 1. tip
    p = rotate_y(p, angle_y)           # 2. turn
    p = rotate_z(p, angle_z)           # 3. roll
    return p


def project(point_3d):
    """Turn one 3D WORLD point into a 2D SCREEN point (from Lesson 1)."""
    x, y, z = point_3d
    screen_x = CENTRE_X + ( (x * FOCAL) / z )
    screen_y = CENTRE_Y - ( (y * FOCAL) / z )
    return (screen_x, screen_y)


def average_z(corners, world_points):
    """NEW: how far away is this face? The average WORLD z of its corners.

    corners      - the face's 4 corner NUMBERS, e.g. (4, 5, 1, 0)
    world_points - all 8 corners in WORLD coordinates (after adding
                   cube_distance), so z means "distance in front of you"
    """
    total = 0
    for corner_number in corners:
        x, y, z = world_points[corner_number]
        total = (total + z)
    return (total / len(corners))          # len(corners) is 4


def is_facing_you(face_points):
    """NEW: the clock test. True if this face is turned toward you.

    face_points - the face's corners as SCREEN points, in the face's
                  own order (clockwise when seen from outside).

    We only need the first 3 corners, a, b and c: three corners are
    enough to tell which way round the face goes.
    Remember SCREEN y points DOWN, which is why clockwise gives a
    POSITIVE answer here.
    """
    a_x, a_y = face_points[0]
    b_x, b_y = face_points[1]
    c_x, c_y = face_points[2]

    # Arrow A goes from corner a to corner b.
    arrow_a_x = (b_x - a_x)
    arrow_a_y = (b_y - a_y)
    # Arrow B goes from corner a to corner c.
    arrow_b_x = (c_x - a_x)
    arrow_b_y = (c_y - a_y)

    # The cross product: positive when B is a CLOCKWISE turn from A.
    cross = ( (arrow_a_x * arrow_b_y) - (arrow_a_y * arrow_b_x) )
    return (cross > 0)


def face_pointer(corners, turned_points):
    """NEW: the arrow pointing straight OUT of a face.

    For our cube this is simply the MIDDLE of the face in SHAPE
    coordinates (the average of its 4 corners), because the cube's
    centre is (0, 0, 0) and every face is 1 step from that centre.

    corners       - the face's 4 corner NUMBERS, e.g. (4, 5, 1, 0)
    turned_points - all 8 corners, turned, in SHAPE coordinates
                    (BEFORE cube_distance is added!)
    """
    total_x = 0
    total_y = 0
    total_z = 0
    for corner_number in corners:
        x, y, z = turned_points[corner_number]
        total_x = (total_x + x)
        total_y = (total_y + y)
        total_z = (total_z + z)
    count = len(corners)                    # 4
    return ( (total_x / count), (total_y / count), (total_z / count) )


def dot(arrow_1, arrow_2):
    """NEW: the dot product. How much do two arrows point the same way?
    For arrows of length 1:  1 = same way, 0 = side-on, -1 = opposite."""
    x1, y1, z1 = arrow_1
    x2, y2, z2 = arrow_2
    return ( (x1 * x2) + (y1 * y2) + (z1 * z2) )


def shade_colour(colour, pointer):
    """NEW: make a colour brighter or darker, depending on the light.

    colour  - the face's full colour (red, green, blue)
    pointer - the face's pointing arrow (from face_pointer)
    """
    brightness = dot(pointer, LIGHT)        # -1 .. 1
    if brightness < 0:
        brightness = 0                      # facing away from the light
    shade = ( AMBIENT + ( (1 - AMBIENT) * brightness ) )   # 0.2 .. 1
    red, green, blue = colour
    return ( round(red * shade), round(green * shade), round(blue * shade) )


def keep_under_360(angle):
    """360 degrees is the same as 0, so start again after a full turn."""
    if angle >= 360:
        angle = (angle - 360)
    return angle


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            if event.key == pygame.K_l:
                use_light = not use_light
            if event.key == pygame.K_c:
                one_colour = not one_colour
            if event.key == pygame.K_r:
                angle_x = START_X
                angle_y = START_Y
                angle_z = START_Z

    if not paused:
        angle_x = keep_under_360( (angle_x + SPEED_X) )
        angle_y = keep_under_360( (angle_y + SPEED_Y) )
        angle_z = keep_under_360( (angle_z + SPEED_Z) )

    screen.fill(BLACK)

    # ---- turn -> move away -> project, for all 8 corners -------------
    # NEW: we keep THREE lists now, one for each kind of coordinates:
    #   turned_points - SHAPE, turned  (for the light)
    #   world_points  - WORLD          (for the painter's method)
    #   screen_points - SCREEN         (for the clock test and drawing)
    turned_points = []
    world_points = []
    screen_points = []
    for p in cube_points:
        turned = rotate_all(p)                       # SHAPE, turned
        turned_points.append(turned)
        x, y, z = turned
        moved = (x, y, (z + cube_distance))          # WORLD
        world_points.append(moved)
        screen_points.append(project(moved))         # SCREEN

    # ---- Make a list of the faces we will paint -----------------------
    faces_to_draw = []
    for corners, colour in cube_faces:
        face_points = []
        for corner_number in corners:
            face_points.append(screen_points[corner_number])

        # 1. The clock test (step 3): skip faces with their back to you.
        if not is_facing_you(face_points):
            continue

        # 2. How far away is it? (step 2)
        distance = average_z(corners, world_points)

        # 3. NEW: what colour, after the light?
        if one_colour:
            colour = CUBE_GREEN
        if use_light:
            pointer = face_pointer(corners, turned_points)
            colour = shade_colour(colour, pointer)

        faces_to_draw.append( (distance, face_points, colour) )

    # ---- The painter's method (step 2): furthest first ----------------
    faces_to_draw.sort(reverse=True)

    for distance, face_points, colour in faces_to_draw:
        pygame.draw.polygon(screen, colour, face_points)        # filled
        pygame.draw.polygon(screen, BLACK, face_points, 2)      # outline

    text = ("tip x = " + str(round(angle_x, 1)) +
            "   turn y = " + str(round(angle_y, 1)) +
            "   roll z = " + str(round(angle_z, 1)))
    screen.blit(font.render(text, True, YELLOW), (20, 20))
    if use_light:
        mode_text = "Light ON (L)    C = one colour / six colours"
    else:
        mode_text = "Light OFF (L)   C = one colour / six colours"
    screen.blit(font.render(mode_text, True, YELLOW), (20, 50))
    screen.blit(font.render("SPACE = pause,  R = reset", True, YELLOW), (20, 80))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

# ----------------------------------------------------------------------
# TRY THIS:
#   * Press L to switch the light off. Without it, can you still see
#     where one face ends and the next begins (ignore the outlines)?
#   * Move the light: LIGHT = (0, 1, 0) is straight overhead. Which face
#     is brightest now? (Keep the length 1 - this one is.)
#   * Set AMBIENT = 0, then AMBIENT = 0.6. What happens to the dark side?
#   * Delete the outline line. Does the light alone show the cube's shape?
# ----------------------------------------------------------------------
