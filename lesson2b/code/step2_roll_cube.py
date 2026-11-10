# ======================================================================
# LESSON 2B - STEP 2: ROLL THE CUBE (turning around the z axis)
# ----------------------------------------------------------------------
# Goal: the LEFT / RIGHT arrows ROLL the cube around its z axis (the
# line through its middle that points straight at you), like turning
# a steering wheel.
#
# What is new since step 1:
#
#   1. angle_z_degrees            - how far the cube has rolled
#   2. rotate_z(point, angle)     - rolls ONE point around the z axis
#   3. a faint circle on the screen showing the path corner 5 travels
#
# THE BIG IDEA (again!):
#   rotate_z is Lesson 2's rotate_y with different letters.
#
#       Lesson 2, rotate_y:  +x swings toward +z.   y is the skewer.
#       Today,    rotate_z:  +x swings toward +y.   z is the skewer.
#
#   So every "z" in the old rule becomes a "y", and z is left alone.
#
# No map this time: the z skewer points straight at you, so the screen
# itself is already the "map from the front".
#
# Controls:  LEFT / RIGHT = roll the cube,   R = reset the angle to 0
# Run:  python step2_roll_cube.py
# ======================================================================

import math
import pygame

pygame.init()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 2B, step 2 - roll the cube")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GREY = (90, 90, 90)

CENTRE_X = (WIDTH / 2)            # (800 / 2) = 400
CENTRE_Y = (HEIGHT / 2)           # (600 / 2) = 300
FOCAL = 400

# ---- The cube, in SHAPE coordinates (same as always) ------------------
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
cube_edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),   # bottom square
    (4, 5), (5, 6), (6, 7), (7, 4),   # top square
    (0, 4), (1, 5), (2, 6), (3, 7),   # upright edges
]

cube_distance = 5

# ---- NEW: how far the cube has rolled --------------------------------
angle_z_degrees = 0
TURN_STEP = 1          # 1 degree per frame -> 6 seconds for a full roll


def rotate_z(point_3d, angle_degrees):
    """Roll one (x, y, z) point around the z axis.

    The point must be in SHAPE coordinates (from the shape's own centre).
    A positive angle swings +x (the right side) toward +y (up):
    as YOU look at it, that is ANTICLOCKWISE, like steering left.
    """
    x, y, z = point_3d

    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)

    # Lesson 2's rule, with every z swapped for a y:
    #   rotate_y had   new_x = (x * cos_a) - (z * sin_a)
    #                  new_z = (x * sin_a) + (z * cos_a)
    new_x = (x * cos_a) - (y * sin_a)
    new_y = (x * sin_a) + (y * cos_a)
    new_z = z                              # the skewer: near/far never changes

    return (new_x, new_y, new_z)


def project(point_3d):
    """Turn one 3D WORLD point into a 2D SCREEN point (from Lesson 1)."""
    x, y, z = point_3d
    screen_x = CENTRE_X + ( (x * FOCAL) / z )
    screen_y = CENTRE_Y - ( (y * FOCAL) / z )
    return (screen_x, screen_y)


# ---- The path of corner 5 --------------------------------------------
# Rolling never changes z, so corner 5 stays at world z = (-1 + 5) = 4.
# Its distance from the skewer is root( (1 * 1) + (1 * 1) ) = 1.414.
# On screen that distance becomes ( (1.414 * FOCAL) / 4 ) = 141.4 px,
# so corner 5 always travels round a circle of radius 141 px.
PATH_RADIUS = ( (math.sqrt(2) * FOCAL) / (-1 + cube_distance) )


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    # ---- NEW: LEFT / RIGHT change the roll angle ---------------------
    # LEFT = a positive angle = anticlockwise, like steering left:
    # the top of the cube leans to the LEFT.
    if keys[pygame.K_LEFT]:
        angle_z_degrees = (angle_z_degrees + TURN_STEP)
    if keys[pygame.K_RIGHT]:
        angle_z_degrees = (angle_z_degrees - TURN_STEP)
    if keys[pygame.K_r]:
        angle_z_degrees = 0
    if angle_z_degrees >= 360:
        angle_z_degrees = (angle_z_degrees - 360)
    if angle_z_degrees < 0:
        angle_z_degrees = (angle_z_degrees + 360)

    screen.fill(BLACK)

    # The faint circle that corner 5 rides round.
    pygame.draw.circle(screen, GREY, (CENTRE_X, CENTRE_Y), PATH_RADIUS, 1)

    # ---- rotate -> move away -> project, for all 8 corners -----------
    screen_points = []
    for p in cube_points:
        turned = rotate_z(p, angle_z_degrees)        # 1. ROLL   (SHAPE)
        x, y, z = turned
        moved = (x, y, (z + cube_distance))          # 2. MOVE   (WORLD)
        screen_points.append(project(moved))         # 3. PROJECT (SCREEN)

    for a, b in cube_edges:
        pygame.draw.line(screen, GREEN, screen_points[a], screen_points[b], 2)

    pygame.draw.circle(screen, YELLOW, screen_points[5], 5)

    text = "roll angle (z) = " + str(angle_z_degrees) + " degrees   (LEFT / RIGHT,  R = reset)"
    screen.blit(font.render(text, True, YELLOW), (20, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

# ----------------------------------------------------------------------
# TRY THIS:
#   * Roll to exactly 90 degrees. Corner 5 is now where which corner was?
#   * Roll to 30 degrees. Is corner 5 at about (437, 163), as worked out
#     in the lesson? Is it on the grey circle?
#   * Look at the BACK square of the cube (the smaller one). Does it
#     roll round a smaller circle? Why? (Hint: its z is 6, not 4.)
#   * Change cube_distance to 8. What radius is the circle now?
#     ( (1.414 * 400) / 7 ) = ?
# ----------------------------------------------------------------------
