# ======================================================================
# LESSON 2B - STEP 1: TIP THE CUBE (turning around the x axis)
# ----------------------------------------------------------------------
# Goal: the cube from Lesson 2, but now the UP / DOWN arrows TIP it
# around its x axis (the left-right line through its middle), like a
# wheel rolling away from you.
#
# What is new since Lesson 2 (everything else is the same):
#
#   1. angle_x_degrees            - how far the cube has tipped
#   2. rotate_x(point, angle)     - tips ONE point around the x axis
#   3. a small "map from the side" in the bottom-left corner, so you
#      can see the tip from the side, like the lesson diagrams.
#
# THE BIG IDEA:
#   rotate_x is Lesson 2's rotate_y with different letters.
#
#       Lesson 2, rotate_y:  +x swings toward +z.   y is the skewer.
#       Today,    rotate_x:  +y swings toward +z.   x is the skewer.
#
#   So every "x" in the old rule becomes a "y", and x is left alone.
#
# THE ORDER IS STILL:
#   rotate (SHAPE coordinates)  ->  move away (WORLD)  ->  project (SCREEN)
#
# Controls:  UP / DOWN = tip the cube,   R = reset the angle to 0
# Run:  python step1_tip_cube.py
# ======================================================================

import math
import pygame

pygame.init()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 2B, step 1 - tip the cube")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GREY = (90, 90, 90)
ORANGE = (255, 160, 60)      # z is always orange, as in Lesson 2

CENTRE_X = (WIDTH / 2)            # (800 / 2) = 400
CENTRE_Y = (HEIGHT / 2)           # (600 / 2) = 300
FOCAL = 400                       # the lens zoom from Lesson 1

# ---- The cube, in SHAPE coordinates (same as Lessons 1 and 2) --------
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

# The cube stays 5 units away all lesson. (In Lesson 2 UP / DOWN moved
# it nearer and further; today UP / DOWN are needed for tipping.)
cube_distance = 5

# ---- NEW: how far the cube has tipped --------------------------------
# Still in DEGREES:  0 = facing you as in Lesson 1,  90 = quarter tip.
angle_x_degrees = 0

# 1 degree per frame of holding a key, 60 frames a second
# -> (1 * 60) = 60 degrees a second -> (360 / 60) = 6 s for a full tip.
TURN_STEP = 1


def rotate_x(point_3d, angle_degrees):
    """Tip one (x, y, z) point around the x axis.

    The point must be in SHAPE coordinates (from the shape's own centre).
    A positive angle swings +y (the top) toward +z (away from you):
    the cube tips its top away from you, like a wheel rolling away.
    """
    x, y, z = point_3d

    # Python's sin and cos need RADIANS, so convert first (as Lesson 2).
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)

    # Lesson 2's rule, with every x swapped for a y:
    #   rotate_y had   new_x = (x * cos_a) - (z * sin_a)
    #                  new_z = (x * sin_a) + (z * cos_a)
    new_x = x                              # the skewer: left/right never changes
    new_y = (y * cos_a) - (z * sin_a)
    new_z = (y * sin_a) + (z * cos_a)

    return (new_x, new_y, new_z)


def project(point_3d):
    """Turn one 3D WORLD point into a 2D SCREEN point (from Lesson 1)."""
    x, y, z = point_3d
    screen_x = CENTRE_X + ( (x * FOCAL) / z )
    screen_y = CENTRE_Y - ( (y * FOCAL) / z )
    return (screen_x, screen_y)


# ---- The little map from the side (bottom-left corner) ---------------
# It shows the cube seen from its LEFT side, in SHAPE coordinates:
#   +z to the RIGHT of the map (away from you),
#   +y UP the map,
#   centre (0, 0) in the middle of the map.
# You (the viewer) are off to the LEFT of the map, looking right.
# Each shape unit is drawn MAP_SCALE pixels long.
MAP_X = 130            # map centre on the screen, in pixels
MAP_Y = 470
MAP_SCALE = 30         # 1 shape unit = 30 pixels, so the cube is 60 px tall


def to_map(z, y):
    """Shape (z, y) -> pixel position on the little side map."""
    map_x = MAP_X + (z * MAP_SCALE)      # +z goes RIGHT on the map
    map_y = MAP_Y - (y * MAP_SCALE)      # minus: +y goes UP the map
    return (map_x, map_y)


def draw_map(turned_points):
    # The axes: z (orange) across the map, y (grey) up the map.
    pygame.draw.line(screen, ORANGE, to_map(-2.5, 0), to_map(2.5, 0), 1)
    pygame.draw.line(screen, GREY, to_map(0, -2.5), to_map(0, 2.5), 1)
    screen.blit(font.render("+z", True, ORANGE), to_map(2.6, 0.3))
    screen.blit(font.render("+y", True, GREY), to_map(0.2, 3.2))
    screen.blit(font.render("you", True, GREY), to_map(-3.9, 0.3))
    # From the side, the right face (corners 1, 2, 6, 5) sits exactly
    # behind the left face, so we only draw the right face's 4 edges.
    # We pick the right face because corner 5 is on it.
    for a, b in [(1, 5), (5, 6), (6, 2), (2, 1)]:
        xa, ya, za = turned_points[a]
        xb, yb, zb = turned_points[b]
        pygame.draw.line(screen, GREEN, to_map(za, ya), to_map(zb, yb), 2)
    # Corner 5 gets a yellow dot, so you can follow it round.
    x5, y5, z5 = turned_points[5]
    pygame.draw.circle(screen, YELLOW, to_map(z5, y5), 5)
    screen.blit(font.render("map from the side", True, GREY), (MAP_X - 85, MAP_Y + 85))


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    # ---- NEW: UP / DOWN change the tip angle -------------------------
    # UP = a positive angle: the front of the cube moves UP the screen
    # (and the top moves away from you).
    if keys[pygame.K_UP]:
        angle_x_degrees = (angle_x_degrees + TURN_STEP)
    if keys[pygame.K_DOWN]:
        angle_x_degrees = (angle_x_degrees - TURN_STEP)
    if keys[pygame.K_r]:
        angle_x_degrees = 0
    # Keep the angle between 0 and 359 (360 is the same as 0).
    if angle_x_degrees >= 360:
        angle_x_degrees = (angle_x_degrees - 360)
    if angle_x_degrees < 0:
        angle_x_degrees = (angle_x_degrees + 360)

    screen.fill(BLACK)

    # ---- Work out where every corner goes ----------------------------
    turned_points = []      # SHAPE coordinates after tipping (for the map)
    screen_points = []      # SCREEN pixels (for the cube)
    for p in cube_points:
        # 1. TIP it around the cube's own centre    (SHAPE coordinates)
        turned = rotate_x(p, angle_x_degrees)
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

    text = "tip angle (x) = " + str(angle_x_degrees) + " degrees   (UP / DOWN,  R = reset)"
    screen.blit(font.render(text, True, YELLOW), (20, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

# ----------------------------------------------------------------------
# TRY THIS:
#   * Tip to exactly 90 degrees. Corner 5 (yellow) is now where which
#     corner was at the start? Check with the lesson's 90-degree diagram.
#   * Tip to exactly 30 degrees. Is corner 5 at about (486, 182) on the
#     screen, as worked out in the lesson?
#   * In rotate_x, change the minus in new_y to a plus. Tip the cube.
#     What goes wrong? (Change it back afterwards!)
#   * Swap the letters back: make it rotate_y again by changing which
#     two letters are used. Does LEFT / RIGHT turning from Lesson 2 come back?
# ----------------------------------------------------------------------
