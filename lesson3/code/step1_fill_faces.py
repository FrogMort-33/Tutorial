# ======================================================================
# LESSON 3 - STEP 1: FROM EDGES TO FACES (and the first problem)
# ----------------------------------------------------------------------
# Goal: stop drawing the cube as 12 lines and start drawing it as
# 6 coloured, FILLED faces.
#
# What is new since Lesson 2B, step 3:
#
#   1. cube_faces - a list of the cube's 6 faces. Each face is
#        ( (4 corner numbers), colour )
#      The 4 corner numbers are listed CLOCKWISE, as you see the face
#      when you look at it from OUTSIDE the cube. (Part 1 of the lesson
#      shows why the order matters. Step 3 uses it to hide faces.)
#
#   2. pygame.draw.polygon(screen, colour, list_of_screen_points)
#      Joins the points in a loop and FILLS the inside with colour.
#
# The recipe for one corner is exactly Lesson 2B's:
#
#   SHAPE corner -> tip -> turn -> roll -> add cube_distance -> project
#   (SHAPE coordinates)               (WORLD coordinates)     (SCREEN)
#
# THE PROBLEM THIS STEP SHOWS YOU:
#   We paint the faces in the order they sit in the list: front first,
#   then back, then left... So the BACK face is painted ON TOP of the
#   front face, and the cube looks inside-out. Watch it tumble and see.
#   Step 2 fixes it.
#
# Controls:  SPACE = pause / unpause,   R = back to the start pose
# Run:  python step1_fill_faces.py
# ======================================================================

import math
import pygame

pygame.init()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 3, step 1 - filled faces (wrong order!)")
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
    # (Same as Lesson 2B. screen_points[5] is still corner 5, and so on.)
    screen_points = []
    for p in cube_points:
        turned = rotate_all(p)                       # SHAPE, turned
        x, y, z = turned
        moved = (x, y, (z + cube_distance))          # WORLD
        screen_points.append(project(moved))         # SCREEN

    # ---- NEW: draw each face as a filled polygon ----------------------
    # For each face we swap its 4 corner NUMBERS for their 4 SCREEN
    # points, then let pygame fill the shape between them.
    #
    # The faces are painted IN LIST ORDER: front, back, left, right,
    # top, bottom. Each new face is painted over the ones before it.
    # That is the bug: the back face is painted after (on top of) the
    # front face. Step 2 fixes the order.
    for corners, colour in cube_faces:
        face_points = []
        for corner_number in corners:
            face_points.append(screen_points[corner_number])
        pygame.draw.polygon(screen, colour, face_points)        # filled
        pygame.draw.polygon(screen, BLACK, face_points, 2)      # outline

    text = ("tip x = " + str(round(angle_x, 1)) +
            "   turn y = " + str(round(angle_y, 1)) +
            "   roll z = " + str(round(angle_z, 1)))
    screen.blit(font.render(text, True, YELLOW), (20, 20))
    screen.blit(font.render("Faces painted in LIST order - looks wrong!",
                            True, YELLOW), (20, 50))
    screen.blit(font.render("SPACE = pause,  R = reset", True, YELLOW), (20, 80))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

# ----------------------------------------------------------------------
# TRY THIS:
#   * Pause (SPACE) when the RED front face should be at the front.
#     Which colour is drawn on top of it? Why? (Look at the list order.)
#   * Move the front face to the END of cube_faces. Does that fix it
#     for every angle, or only some? (Step 2 shows the real fix.)
#   * Delete the "outline" line. Can you still see where faces meet?
#   * Swap two corner numbers in the front face, e.g. (4, 5, 0, 1).
#     What strange shape do you get? (Lesson Part 1 calls it a bow tie.)
# ----------------------------------------------------------------------
