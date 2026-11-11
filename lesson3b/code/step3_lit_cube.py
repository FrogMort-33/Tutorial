# ======================================================================
# LESSON 3B - STEP 3: THE LIT SOLID CUBE (light and shade)
# ----------------------------------------------------------------------
# Goal: the finished lit cube.  Faces that point at the lamp are
# bright, faces that point away are dim, but NEVER fully black.
# This is the final program of Lesson 3B and the starting point
# for Lesson 4.
#
# What is new since step 2:
#
#   1. AMBIENT = 0.2  - light that comes from everywhere.
#
#   2. shade = ( AMBIENT + ( (1 - AMBIENT) * brightness ) )
#        brightness 0   -> shade ( 0.2 + ( 0.8 * 0 ) )   = 0.2
#        brightness 0.5 -> shade ( 0.2 + ( 0.8 * 0.5 ) ) = 0.6
#        brightness 1   -> shade ( 0.2 + ( 0.8 * 1 ) )   = 1.0
#      so a colour never drops below 20% of itself.
#
#   3. L switches the light off and on, to compare.
#
# The full recipe, every frame:
#
#   SHAPE corners -> tip, turn, roll -> add cube_distance -> project
#   then for each face:  clock test (skip?) -> average z
#                        -> turn its normal -> dot with LIGHT -> shade
#   then sort far -> near and paint.
#
# Controls:  SPACE = pause,  R = reset,
#            L = light on / off,   C = one colour / six colours
# Run:  python step3_lit_cube.py
# ======================================================================

import math
import pygame

pygame.init()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Lesson 3B, step 3 - the lit cube')
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# ---- One colour for each face (from Lesson 3) -----------------------
# (red, green, blue), each 0 to 255. Six colours that are easy to tell
# apart, so you can always say WHICH face you are looking at.
RED = (235, 80, 80)          # front
PURPLE = (160, 100, 230)     # back
BLUE = (70, 150, 255)        # left
GREEN = (70, 210, 120)       # right
GOLD = (245, 200, 60)        # top
ORANGE = (245, 140, 50)      # bottom
CUBE_GREEN = (70, 230, 120)  # ONE colour for the whole cube, so the light
                             # is the ONLY thing that makes faces differ.
                             # (C key swaps to the six face colours.)

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

# ---- The cube's 6 faces (from Lesson 3) -----------------------------
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
# ---- NEW in Lesson 3B: each face also stores its NORMAL --------------
# A face's NORMAL is an arrow, exactly 1 long, pointing straight OUT of
# the face.  It is written in SHAPE coordinates (cube not turned yet),
# and it is stored here as DATA, just like the corners.
#
# Each face is now:   ( corners,  colour,  normal )
#
# How a normal is worked out (Lesson 3B, Part 3):
#   a, b, c = the face's first 3 corners
#   A = b - a        B = c - a                  (two edges of the face)
#   cross = ( ((A_y * B_z) - (A_z * B_y)),
#             ((A_z * B_x) - (A_x * B_z)),
#             ((A_x * B_y) - (A_y * B_x)) )     (square-on to both edges)
#   normal = cross divided by its length        (shrink it to 1 long)
#
# Worked example - FRONT face (4, 5, 1, 0):
#   a = corner 4 = (-1, 1, -1)   b = corner 5 = (1, 1, -1)   c = corner 1 = (1, -1, -1)
#   A = (2, 0, 0)                B = (2, -2, 0)
#   cross = ( ((0 * 0) - (0 * -2)), ((0 * 2) - (2 * 0)), ((2 * -2) - (0 * 2)) )
#         = (0, 0, -4)           length 4      normal = (0, 0, -1)
#
# For a cube every answer is one of the 6 axis arrows, so we just write
# them in.  (Other shapes get less round numbers - see the lesson.)
cube_faces = [
    ((4, 5, 1, 0), RED,    ( 0,  0, -1)),   # front  -> toward you  (-z)
    ((6, 7, 3, 2), PURPLE, ( 0,  0,  1)),   # back   -> away        (+z)
    ((7, 4, 0, 3), BLUE,   (-1,  0,  0)),   # left   -> left        (-x)
    ((5, 6, 2, 1), GREEN,  ( 1,  0,  0)),   # right  -> right       (+x)
    ((7, 6, 5, 4), GOLD,   ( 0,  1,  0)),   # top    -> up          (+y)
    ((2, 3, 0, 1), ORANGE, ( 0, -1,  0)),   # bottom -> down        (-y)
]

cube_distance = 5


# ---- NEW: the light ---------------------------------------------------
# LIGHT is an ARROW that points FROM the cube TOWARD the lamp.
# (Careful: it points back up the beam, NOT the way the light travels.)
#
# How we made it:
#   1. Pick where the lamp is:  12 to the RIGHT, 15 UP, 16 TOWARD you.
#      Toward you is -z, so that is the arrow (12, 15, -16).
#   2. Its length:  root( (12 * 12) + (15 * 15) + (16 * 16) )
#                 = root( 144 + 225 + 256 ) = root( 625 ) = 25
#   3. Shrink it to length 1 by dividing every part by 25:
#        ( (12 / 25), (15 / 25), (-16 / 25) ) = (0.48, 0.6, -0.64)
#
#   x =  0.48  -> a little to the RIGHT
#   y =  0.6   -> UP
#   z = -0.64  -> TOWARD you
#
# Why "up, right and toward you"?  It is how a photographer lights an
# object: the three faces you can see at the start pose each get a
# clearly DIFFERENT brightness (top 0.917, front 0.388, left in shadow).
LIGHT = (0.48, 0.6, -0.64)

# ---- NEW: AMBIENT ------------------------------------------------------
# Light that comes from everywhere (bouncing off walls, the sky ...).
# 0.2 means even a face in full shadow keeps 20% of its colour, so it
# never turns pure black and vanishes into the black background.
# Try 0 (step 2's black shadows) and 0.6 (very flat) to compare.
AMBIENT = 0.2

# ---- Angles and speeds (exactly as Lesson 2B, step 3) -----------------
# We START at a pose that shows three faces (front, left and top),
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
one_colour = True      # C key flips this (one colour / six colours)
use_light = True       # NEW: L key flips this



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
    """(Lesson 3) How far away is this face? The average WORLD z of its corners.

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
    """(Lesson 3) The clock test. True if this face is turned toward you.

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




def dot(arrow_1, arrow_2):
    """NEW: the DOT PRODUCT.  How well do two arrows line up?

    Recipe: multiply the matching letters, then add the 3 answers.
        dot = ( (x1 * x2) + (y1 * y2) + (z1 * z2) )

    For two arrows that are both exactly 1 long:
         1   -> they point the SAME way          (face looks right at the lamp)
         0.5 -> 60 degrees apart                  (half the light)
         0   -> at right angles ("side-on")       (light just skims past)
        -1   -> OPPOSITE ways                     (face looks away from the lamp)

    Worked example (front face, cube NOT turned):
        normal = (0, 0, -1),  LIGHT = (0.48, 0.6, -0.64)
        dot = ( (0 * 0.48) + (0 * 0.6) + ((-1) * (-0.64)) )
            = ( 0 + 0 + 0.64 )
            = 0.64
    """
    x1, y1, z1 = arrow_1
    x2, y2, z2 = arrow_2
    return ( (x1 * x2) + (y1 * y2) + (z1 * z2) )

def shade_colour(colour, turned_normal):
    """Make a colour brighter or darker, depending on the light.

    colour  - the face's full colour (red, green, blue)
    turned_normal - the face's normal, turned with rotate_all

    Three small steps:
      1. brightness = dot(turned_normal, LIGHT), never below 0  (step 2)
      2. shade = ( AMBIENT + ( (1 - AMBIENT) * brightness ) ) (NEW)
           AMBIENT is the part every face always gets (0.2).
           (1 - AMBIENT) = 0.8 is the part the lamp can add on top.
      3. multiply red, green and blue by shade                (step 2)

    Worked example, TOP face at the start pose (brightness 0.917):
      shade = ( 0.2 + ( 0.8 * 0.917 ) ) = ( 0.2 + 0.734 ) = 0.934
      green = round(230 * 0.934) = 215
    """
    brightness = dot(turned_normal, LIGHT)  # -1 .. 1
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
            if event.key == pygame.K_c:
                one_colour = not one_colour
            if event.key == pygame.K_l:
                use_light = not use_light
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
    #   world_points  - WORLD   (the painter's method)
    #   screen_points - SCREEN  (the clock test and drawing)
    world_points = []
    screen_points = []
    for p in cube_points:
        x, y, z = rotate_all(p)                      # SHAPE, turned
        moved = (x, y, (z + cube_distance))          # WORLD
        world_points.append(moved)
        screen_points.append(project(moved))         # SCREEN

    # ---- Make a list of the faces we will paint -----------------------
    faces_to_draw = []
    for corners, colour, normal in cube_faces:       # NEW: 3rd item, the normal
        face_points = []
        for corner_number in corners:
            face_points.append(screen_points[corner_number])

        # 1. The clock test (Lesson 3): skip faces with their back to you.
        if not is_facing_you(face_points):
            continue

        # 2. How far away is it? (Lesson 3, the painter's method)
        distance = average_z(corners, world_points)

        # 3. NEW: which way does this face point NOW?
        #    Turn the stored normal with the SAME rotate_all as the corners.
        #    Do NOT add cube_distance: a normal is a direction, not a place.
        turned_normal = rotate_all(normal)

        if one_colour:
            colour = CUBE_GREEN

        # 4. What colour, after the light?
        if use_light:
            colour = shade_colour(colour, turned_normal)

        faces_to_draw.append( (distance, face_points, colour) )

    # ---- The painter's method (Lesson 3): furthest first ---------------
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
#   * Press L to switch the light off.  Without it (and ignoring the
#     outlines), can you still see where one face ends and the next
#     begins?
#   * Move the light: LIGHT = (0, 1, 0) is straight overhead.  Which face
#     is brightest now?  (Keep the length 1 - this one is.)
#   * Set AMBIENT = 0, then AMBIENT = 0.6.  What happens to the dark side?
#   * Delete the outline line.  Does the light alone show the cube's shape?
# ----------------------------------------------------------------------
