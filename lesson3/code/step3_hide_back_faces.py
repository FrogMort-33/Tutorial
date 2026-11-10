# ======================================================================
# LESSON 3 - STEP 3: HIDE THE BACK FACES (the clock test)
# ----------------------------------------------------------------------
# Goal: stop painting the faces that point AWAY from you.
#
# A cube always has its back turned on at least 3 of its 6 faces.
# In step 2 we painted all 6 and then covered 3 of them up: wasted work.
# Now we find those faces and skip them.
#
# THE CLOCK TEST:
#   Every face lists its corners CLOCKWISE, as seen from OUTSIDE.
#   If a face turns its back on you, you are seeing it from BEHIND, and
#   the very same corners now go round ANTICLOCKWISE on the screen.
#   (Like a clock painted on glass: from behind, it runs backwards.)
#
# What is new since step 2:
#
#   1. is_facing_you(face_points)  - the clock test, done with two
#      ARROWS on the screen and one small sum called the CROSS PRODUCT:
#
#        arrow A = corner b - corner a      (a -> b)
#        arrow B = corner c - corner a      (a -> c)
#        cross   = ( (A_x * B_y) - (A_y * B_x) )
#
#        cross > 0  -> the corners go CLOCKWISE  -> facing you -> paint
#        cross <= 0 -> ANTICLOCKWISE (or edge-on) -> back turned -> skip
#
#   2. The painter's method from step 2 is KEPT. With one cube the clock
#      test alone is enough, but with many shapes (later lessons) we need
#      both, so we keep the habit.
#
# Controls:  SPACE = pause,  R = reset,
#            B = hide back faces on / off (off = see-through "x-ray")
# Run:  python step3_hide_back_faces.py
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
hide_back = True       # NEW: B key flips this, to compare


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
            if event.key == pygame.K_b:
                hide_back = not hide_back
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

    # ---- Make a list of the faces we will paint -----------------------
    # Same as step 2, with ONE new check: the clock test.
    faces_to_draw = []
    for corners, colour in cube_faces:
        face_points = []
        for corner_number in corners:
            face_points.append(screen_points[corner_number])

        # NEW: skip any face that has its back to you.
        # "continue" means: stop here and go on to the NEXT face.
        if hide_back and not is_facing_you(face_points):
            continue

        distance = average_z(corners, world_points)
        faces_to_draw.append( (distance, face_points, colour) )

    # ---- The painter's method (from step 2): furthest first ----------
    faces_to_draw.sort(reverse=True)

    for distance, face_points, colour in faces_to_draw:
        if hide_back:
            pygame.draw.polygon(screen, colour, face_points)        # filled
            pygame.draw.polygon(screen, BLACK, face_points, 2)      # outline
        else:
            # X-ray mode: outlines only, so you can see ALL six faces
            # (including the back ones) through the cube.
            pygame.draw.polygon(screen, colour, face_points, 3)

    text = ("tip x = " + str(round(angle_x, 1)) +
            "   turn y = " + str(round(angle_y, 1)) +
            "   roll z = " + str(round(angle_z, 1)))
    screen.blit(font.render(text, True, YELLOW), (20, 20))
    if hide_back:
        mode_text = ("Faces painted: " + str(len(faces_to_draw)) +
                     " of 6   (B = x-ray)")
    else:
        mode_text = "X-ray: all 6 face outlines   (B = solid)"
    screen.blit(font.render(mode_text, True, YELLOW), (20, 50))
    screen.blit(font.render("SPACE = pause,  R = reset", True, YELLOW), (20, 80))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

# ----------------------------------------------------------------------
# TRY THIS:
#   * Watch the "Faces painted" number. Is it ever more than 3? Ever 1?
#   * Change  (cross > 0)  to  (cross < 0). What do you see now, and why?
#   * Swap two corner numbers in ONE face, e.g. front (4, 5, 1, 0) to
#     (5, 4, 0, 1). That face is now listed anticlockwise. What happens?
#   * Press B for x-ray mode, pause, and find the 3 hidden faces.
# ----------------------------------------------------------------------
