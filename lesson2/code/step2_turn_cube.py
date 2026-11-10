# ======================================================================
# LESSON 2 - STEP 2: TURN THE CUBE BY HAND
# ----------------------------------------------------------------------
# Goal: the cube from Lesson 1, but now LEFT / RIGHT arrows turn it
# around its y axis (the up-down line through its middle).
#
# What is new since Lesson 1 (everything else is the same):
#
#   1. import math                  - for sin, cos and radians
#   2. angle_degrees                - how far the cube has turned
#   3. rotate_y(point, angle)       - turns ONE point around the y axis
#   4. the corner loop now does:    rotate -> move away -> project
#   5. a small "map from above" in the bottom-left corner, so you can
#      see the same turning from the top, like the lesson diagrams.
#
# THE ORDER MATTERS:
#   rotate first (in SHAPE coordinates, around the cube's own centre),
#   THEN add cube_distance (WORLD coordinates),
#   THEN project (SCREEN pixels).
#   If you moved first and rotated second, the cube would swing round
#   YOU instead of spinning on the spot.
#
# Controls:  LEFT / RIGHT = turn the cube,  UP / DOWN = push away / pull closer
#            R = reset the angle to 0
# Run:  python step2_turn_cube.py
# ======================================================================

import math
import pygame

pygame.init()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 2, step 2 - turn the cube")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GREY = (90, 90, 90)
BLUE = (90, 170, 255)
ORANGE = (255, 160, 60)

CENTRE_X = (WIDTH / 2)            # (800 / 2) = 400
CENTRE_Y = (HEIGHT / 2)           # (600 / 2) = 300
FOCAL = 400                       # the lens zoom from Lesson 1

# ---- The cube, in SHAPE coordinates (same as Lesson 1) ---------------
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

cube_distance = 5      # how far away the cube's centre is (world z)

# ---- NEW: how far the cube has turned --------------------------------
# Measured in DEGREES, because degrees are easy to picture:
#   0 = facing you as in Lesson 1, 90 = quarter turn, 360 = full turn.
angle_degrees = 0

# How many degrees one frame of holding an arrow key turns the cube.
# 1 degree x 60 frames per second = 60 degrees per second,
# so holding the key for 6 seconds makes one full turn (360).
TURN_STEP = 1


def rotate_y(point_3d, angle_degrees):
    """Turn one (x, y, z) point around the y axis.

    The point must be in SHAPE coordinates (from the shape's own centre).
    Seen from above, a positive angle turns it ANTICLOCKWISE.
    """
    x, y, z = point_3d

    # Python's sin and cos need RADIANS, so convert first.
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)

    new_x = (x * cos_a) - (z * sin_a)
    new_y = y                              # up/down never changes
    new_z = (x * sin_a) + (z * cos_a)

    return (new_x, new_y, new_z)


def project(point_3d):
    """Turn one 3D WORLD point into a 2D SCREEN point (from Lesson 1)."""
    x, y, z = point_3d
    screen_x = CENTRE_X + ( (x * FOCAL) / z )
    screen_y = CENTRE_Y - ( (y * FOCAL) / z )
    return (screen_x, screen_y)


# ---- The little map from above (bottom-left corner) ------------------
# It shows the cube seen from ABOVE, in SHAPE coordinates:
#   +x to the right, +z UP the map (away from you), centre (0, 0).
# Each shape unit is drawn MAP_SCALE pixels long.
MAP_X = 100            # map centre on the screen, in pixels
MAP_Y = 490
MAP_SCALE = 30         # 1 shape unit = 30 pixels, so the cube is 60 px wide


def to_map(x, z):
    """Shape (x, z) -> pixel position on the little map."""
    map_x = MAP_X + (x * MAP_SCALE)
    map_y = MAP_Y - (z * MAP_SCALE)      # minus: +z goes UP the map
    return (map_x, map_y)


def draw_map(turned_points):
    # The axes: x (blue) across, z (orange) up the map.
    pygame.draw.line(screen, BLUE, to_map(-2.5, 0), to_map(2.5, 0), 1)
    pygame.draw.line(screen, ORANGE, to_map(0, -2.5), to_map(0, 2.5), 1)
    screen.blit(font.render("+x", True, BLUE), to_map(2.6, 0.3))
    screen.blit(font.render("+z", True, ORANGE), to_map(0.2, 3.2))
    # From above, the top square hides the bottom one, so we only need
    # the 4 top corners (numbers 4, 5, 6, 7) and the 4 top edges.
    for a, b in [(4, 5), (5, 6), (6, 7), (7, 4)]:
        xa, ya, za = turned_points[a]
        xb, yb, zb = turned_points[b]
        pygame.draw.line(screen, GREEN, to_map(xa, za), to_map(xb, zb), 2)
    # Corner 5 gets a yellow dot, so you can follow it round.
    x5, y5, z5 = turned_points[5]
    pygame.draw.circle(screen, YELLOW, to_map(x5, z5), 5)
    screen.blit(font.render("map from above", True, GREY), (MAP_X - 70, MAP_Y + 85))


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    # ---- NEW: LEFT / RIGHT change the angle --------------------------
    if keys[pygame.K_RIGHT]:
        angle_degrees = (angle_degrees + TURN_STEP)
    if keys[pygame.K_LEFT]:
        angle_degrees = (angle_degrees - TURN_STEP)
    if keys[pygame.K_r]:
        angle_degrees = 0
    # Keep the angle between 0 and 359, so the number on screen stays
    # readable. 360 degrees is the same as 0 (a full turn).
    if angle_degrees >= 360:
        angle_degrees = (angle_degrees - 360)
    if angle_degrees < 0:
        angle_degrees = (angle_degrees + 360)

    # ---- UP / DOWN still move the cube, as in Lesson 1 ---------------
    if keys[pygame.K_UP]:
        cube_distance = (cube_distance + 0.05)
    if keys[pygame.K_DOWN]:
        cube_distance = (cube_distance - 0.05)
    if cube_distance < 3:              # corners reach 1.414 from the centre
        cube_distance = 3              # when turned, so keep z well above 0

    screen.fill(BLACK)

    # ---- Work out where every corner goes ----------------------------
    turned_points = []      # SHAPE coordinates after turning (for the map)
    screen_points = []      # SCREEN pixels (for the cube)
    for p in cube_points:
        # 1. ROTATE around the cube's own centre   (SHAPE coordinates)
        turned = rotate_y(p, angle_degrees)
        turned_points.append(turned)

        # 2. MOVE it away from us                   (WORLD coordinates)
        x, y, z = turned
        moved = (x, y, (z + cube_distance))

        # 3. PROJECT it onto the screen             (SCREEN pixels)
        screen_points.append(project(moved))

    # ---- Draw the edges (exactly as in Lesson 1) ---------------------
    for a, b in cube_edges:
        pygame.draw.line(screen, GREEN, screen_points[a], screen_points[b], 2)

    # Corner 5 gets a yellow dot here too.
    pygame.draw.circle(screen, YELLOW, screen_points[5], 5)

    draw_map(turned_points)

    text = "angle = " + str(angle_degrees) + " degrees   (LEFT / RIGHT,  R = reset)"
    screen.blit(font.render(text, True, YELLOW), (20, 20))
    text2 = "distance = " + str(round(cube_distance, 1)) + "   (UP / DOWN)"
    screen.blit(font.render(text2, True, YELLOW), (20, 50))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

# ----------------------------------------------------------------------
# TRY THIS:
#   * Turn to exactly 90 degrees. Corner 5 (yellow) is now where which
#     corner was at the start? Check with the lesson's 90-degree diagram.
#   * Change TURN_STEP to 5. How long does a full turn take now?
#   * In rotate_y, change the minus in new_x to a plus. Turn the cube.
#     What goes wrong? (Change it back afterwards!)
#   * Swap steps 1 and 2: move first, rotate second. What happens?
# ----------------------------------------------------------------------
