# ======================================================================
# LESSON 3 - STEP 2: THE PAINTER'S METHOD (far faces first)
# ----------------------------------------------------------------------
# Goal: paint the faces in the RIGHT order, so the cube looks solid.
#
# THE PAINTER'S METHOD:
#   A painter paints the far-away mountains first, then the hills, then
#   the tree in front. Each new layer covers what is behind it.
#   We do the same with faces: paint the FURTHEST face first and the
#   NEAREST face last.
#
# What is new since step 1:
#
#   1. average_z(corners, world_points)
#        How far away is a face? Add up the WORLD z of its 4 corners
#        and divide by 4:   ( (z_a + z_b + z_c + z_d) / 4 )
#
#   2. A list of faces to draw, each one   (average z, points, colour)
#      faces_to_draw.sort(reverse=True)  puts the BIGGEST z (furthest)
#      first, so the for loop paints far -> near.
#
#   3. Each face's average z is written in its middle, so you can watch
#      the numbers change as it tumbles. The biggest number is painted
#      first and ends up hidden underneath.
#
# Controls:  SPACE = pause,  R = reset,
#            P = painter's method on / off (to compare with step 1)
# Run:  python step2_painter.py
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
small_font = pygame.font.SysFont(None, 24)

BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

# ---- NEW: one colour for each face ----------------------------------
# (red, green, blue), each 0 to 255. Six colours that are easy to tell
# apart, so you can always say WHICH face you are looking at.
RED = (235, 80, 80)          # front
PURPLE = (160, 100, 230)     # back
BLUE = (70, 150, 255)        # left
GREEN = (70, 210, 120)       # right
GOLD = (245, 200, 60)        # top
ORANGE = (245, 140, 50)      # bottom

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
use_painter = True     # NEW: P key flips this, to compare


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


def middle_of(points_2d):
    """The average of some SCREEN points: the middle of a face on screen.
    Only used to decide where to write the face's average z."""
    total_x = 0
    total_y = 0
    for sx, sy in points_2d:
        total_x = (total_x + sx)
        total_y = (total_y + sy)
    return ( (total_x / len(points_2d)), (total_y / len(points_2d)) )


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
            if event.key == pygame.K_p:
                use_painter = not use_painter
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
    # NEW: we now KEEP the WORLD points too (world_points), because
    # average_z() needs each corner's distance from you.
    world_points = []
    screen_points = []
    for p in cube_points:
        turned = rotate_all(p)                       # SHAPE, turned
        x, y, z = turned
        moved = (x, y, (z + cube_distance))          # WORLD
        world_points.append(moved)
        screen_points.append(project(moved))         # SCREEN

    # ---- NEW: make a list of faces, each with its distance -------------
    # Every item is a tuple of 3 things:  (average z, screen points, colour)
    # We put average z FIRST on purpose: sort() sorts tuples by their
    # FIRST item, so the list gets sorted by distance.
    faces_to_draw = []
    for corners, colour in cube_faces:
        face_points = []
        for corner_number in corners:
            face_points.append(screen_points[corner_number])
        distance = average_z(corners, world_points)
        faces_to_draw.append( (distance, face_points, colour) )

    # ---- NEW: the painter's method: furthest first --------------------
    # sort() would put the SMALLEST z first. reverse=True flips it so the
    # BIGGEST z (the furthest face) comes first and is painted first.
    if use_painter:
        faces_to_draw.sort(reverse=True)

    # Paint them in that order. Nearer faces cover the further ones.
    for distance, face_points, colour in faces_to_draw:
        pygame.draw.polygon(screen, colour, face_points)        # filled
        pygame.draw.polygon(screen, BLACK, face_points, 2)      # outline

    # Write each face's average z in its middle (one decimal place).
    # All SIX labels are written, even for faces that ended up covered,
    # so some numbers float on top of a face that is in front of them.
    for distance, face_points, colour in faces_to_draw:
        label = small_font.render(str(round(distance, 1)), True, WHITE)
        mx, my = middle_of(face_points)
        screen.blit(label, ( (mx - 14), (my - 8) ))

    text = ("tip x = " + str(round(angle_x, 1)) +
            "   turn y = " + str(round(angle_y, 1)) +
            "   roll z = " + str(round(angle_z, 1)))
    screen.blit(font.render(text, True, YELLOW), (20, 20))
    if use_painter:
        mode_text = "Painter's method ON: furthest face painted first  (P)"
    else:
        mode_text = "Painter's method OFF: list order, like step 1  (P)"
    screen.blit(font.render(mode_text, True, YELLOW), (20, 50))
    screen.blit(font.render("SPACE = pause,  R = reset", True, YELLOW), (20, 80))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

# ----------------------------------------------------------------------
# TRY THIS:
#   * Pause (SPACE) and read the six numbers. The face with the BIGGEST
#     number is painted first. Can you see it at all?
#   * Press P to switch the painter's method off and on while paused.
#   * Change reverse=True to reverse=False. What goes wrong, and why?
#   * At any moment, how many faces are painted and then completely
#     covered up? (Step 3 stops painting those.)
# ----------------------------------------------------------------------
