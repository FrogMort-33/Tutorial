# ======================================================================
# LESSON 3B - STEP 1: FACE NORMALS
# ----------------------------------------------------------------------
# Goal: SEE the normal: the arrow that sticks straight out of each face.
# Nothing is lit yet.  This step only answers the question
# "which way does each face point?"
#
# Starts from Lesson 3's last program, step3_hide_back_faces.py.
#
# What is new:
#
#   1. cube_faces now stores each face's NORMAL as a third item:
#        ( corners, colour, normal ).  Front face: (0, 0, -1) = toward you.
#
#   2. Every frame each normal is turned with rotate_all, exactly like
#      the corners (but never moved by cube_distance).
#
#   3. A white arrow is drawn out of every face you can see, and the
#      turned normal's three numbers are written beside it, so you can
#      watch the numbers change as the cube tumbles.
#
#   4. CUBE_GREEN: one colour for the whole cube (C swaps back to six).
#
# Controls:  SPACE = pause,  R = back to the start pose,
#            C = one colour / six colours,  N = normals on / off
# Run:  python step1_face_normals.py
# ======================================================================

import math
import pygame

pygame.init()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Lesson 3B, step 1 - face normals')
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
one_colour = True      # NEW: C key flips this (one colour / six colours)
show_normals = True    # NEW: N key flips this

WHITE = (255, 255, 255)
small_font = pygame.font.SysFont(None, 24)

# How far the drawn arrow sticks OUT of the face, in SHAPE units.
# 0.8 is long enough to see clearly, short enough to stay on screen.
NORMAL_DRAW_LENGTH = 0.8



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




def face_middle(corners, world_points):
    """NEW (for drawing only): the middle of a face, in WORLD coordinates.

    The middle of 4 corners is their average: add the 4 x's and divide
    by 4, then the same for y and for z.  We only use it to know WHERE
    to draw the normal's arrow.  (It is NOT the normal.)
    """
    total_x = 0
    total_y = 0
    total_z = 0
    for corner_number in corners:
        x, y, z = world_points[corner_number]
        total_x = (total_x + x)
        total_y = (total_y + y)
        total_z = (total_z + z)
    count = len(corners)                    # 4 corners
    return ( (total_x / count), (total_y / count), (total_z / count) )


def normal_tip(middle, turned_normal):
    """NEW (for drawing only): where the arrow's TIP is, in WORLD.

    Start at the face's middle and step NORMAL_DRAW_LENGTH units along
    the normal:   tip = middle + ( normal * NORMAL_DRAW_LENGTH )
    """
    mx, my, mz = middle
    nx, ny, nz = turned_normal
    return ( (mx + (nx * NORMAL_DRAW_LENGTH)),
             (my + (ny * NORMAL_DRAW_LENGTH)),
             (mz + (nz * NORMAL_DRAW_LENGTH)) )

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
            if event.key == pygame.K_n:
                show_normals = not show_normals
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

        faces_to_draw.append( (distance, face_points, colour, corners, turned_normal) )

    # ---- The painter's method (Lesson 3): furthest first ---------------
    # key= : sort on the distance only (the 1st item of each tuple)
    faces_to_draw.sort(key=lambda face: face[0], reverse=True)

    for distance, face_points, colour, corners, turned_normal in faces_to_draw:
        pygame.draw.polygon(screen, colour, face_points)        # filled
        pygame.draw.polygon(screen, BLACK, face_points, 2)      # outline

    # ---- NEW: draw each visible face's normal on top -------------------
    # (Drawn AFTER all the faces, so no face can paint over an arrow.)
    if show_normals:
        for distance, face_points, colour, corners, turned_normal in faces_to_draw:
            middle = face_middle(corners, world_points)    # WORLD
            tip = normal_tip(middle, turned_normal)        # WORLD
            start = project(middle)                        # SCREEN
            end = project(tip)                             # SCREEN
            pygame.draw.line(screen, WHITE, start, end, 3)
            pygame.draw.circle(screen, WHITE, end, 5)      # a blob for the tip
            # Write the normal's numbers, rounded to 2 places, at the tip.
            x, y, z = turned_normal
            label = ("(" + str(round(x, 2)) + ", " + str(round(y, 2)) +
                     ", " + str(round(z, 2)) + ")")
            picture = small_font.render(label, True, WHITE)
            if end[0] >= start[0]:
                # arrow points right: write the numbers to the RIGHT of the tip
                text_x = (end[0] + 8)
            else:
                # arrow points left: write them to the LEFT of the tip, so
                # the text doesn't sit on top of the arrow
                text_x = ( (end[0] - 8) - picture.get_width() )
            screen.blit(picture, (text_x, (end[1] - 8)))

    text = ("tip x = " + str(round(angle_x, 1)) +
            "   turn y = " + str(round(angle_y, 1)) +
            "   roll z = " + str(round(angle_z, 1)))
    screen.blit(font.render(text, True, YELLOW), (20, 20))
    screen.blit(font.render("White arrows = turned face normals", True, YELLOW), (20, 50))
    screen.blit(font.render("SPACE = pause,  R = reset,  C = colours,  N = normals", True, YELLOW), (20, 80))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

# ----------------------------------------------------------------------
# TRY THIS:
#   * Press R, then SPACE to pause.  Read the FRONT face's normal.
#     It should say (0.43, -0.5, -0.75), as in the lesson.
#   * Watch ONE arrow as the cube tumbles.  Do its three numbers ever go
#     above 1 or below -1?  (They can't: the arrow is always 1 long.)
#   * Change the FRONT face's stored normal to (0, 0, 1) (the wrong way).
#     Where does its arrow point now?
#   * Change "turned_normal = rotate_all(normal)" to "turned_normal = normal".
#     Do the arrows still follow their faces as the cube tumbles?
# ----------------------------------------------------------------------
