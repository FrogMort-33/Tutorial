# ======================================================================
# LESSON 2B - STEP 3: THE TUMBLING CUBE (all three turns at once)
# ----------------------------------------------------------------------
# Goal: the cube tips, turns AND rolls by itself, each at its own speed,
# so it tumbles through the air and shows you every side.
#
# What is new since step 2:
#
#   1. THREE angles:   angle_x, angle_y, angle_z   (all in degrees)
#   2. THREE speeds:   SPEED_X, SPEED_Y, SPEED_Z   (degrees per frame)
#   3. rotate_all(point)  - does the three turns ONE AFTER ANOTHER:
#
#          tip (x)  ->  turn (y)  ->  roll (z)
#
#      Each turn starts from the answer of the turn before.
#
#   4. Press O to swap the ORDER to  roll (z) -> turn (y) -> tip (x).
#      The cube JUMPS to a different position, even though the three
#      angles are exactly the same. That is the lesson's "order matters".
#
# The full recipe for one corner, every frame:
#
#   SHAPE corner -> tip -> turn -> roll -> add cube_distance -> project
#   (all three turns in SHAPE coordinates)   (WORLD)           (SCREEN)
#
# Controls:  SPACE = pause / unpause,   O = swap the order,
#            R = reset all three angles to 0
# Run:  python step3_tumble_cube.py
# ======================================================================

import math
import pygame

pygame.init()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 2B, step 3 - the tumbling cube")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

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

# A turned corner can now reach root(3) = 1.732 in front of the centre
# (all three numbers of a corner can swing toward you at once), so the
# nearest a corner gets is (5 - 1.732) = 3.268 away. Safe.
cube_distance = 5

# ---- NEW: three angles and three speeds ------------------------------
angle_x = 0            # tip  so far, degrees
angle_y = 0            # turn so far, degrees
angle_z = 0            # roll so far, degrees

# Degrees added EVERY FRAME (60 frames a second). Three DIFFERENT
# speeds, so the cube does not just repeat the same wobble:
#   SPEED_Y = 1    -> (1 * 60)    = 60  deg/s -> (360 / 60) =  6 s a turn
#   SPEED_X = 0.5  -> (0.5 * 60)  = 30  deg/s -> (360 / 30) = 12 s a tip
#   SPEED_Z = 0.25 -> (0.25 * 60) = 15  deg/s -> (360 / 15) = 24 s a roll
# Turning stays at Lesson 2's speed; tipping is half that and rolling a
# quarter, so the tumble is slow enough to follow with your eyes.
SPEED_X = 0.5
SPEED_Y = 1
SPEED_Z = 0.25

paused = False
x_first = True         # True: tip -> turn -> roll.  False: roll -> turn -> tip.


# ---- The three turns. Same rule, three sets of letters ----------------
#   rotate_x: +y swings toward +z  (x is the skewer)   = TIP
#   rotate_y: +x swings toward +z  (y is the skewer)   = TURN (Lesson 2)
#   rotate_z: +x swings toward +y  (z is the skewer)   = ROLL

def rotate_x(point_3d, angle_degrees):
    """TIP one SHAPE point around the x axis (top swings away)."""
    x, y, z = point_3d
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    new_x = x
    new_y = (y * cos_a) - (z * sin_a)
    new_z = (y * sin_a) + (z * cos_a)
    return (new_x, new_y, new_z)


def rotate_y(point_3d, angle_degrees):
    """TURN one SHAPE point around the y axis (anticlockwise from above)."""
    x, y, z = point_3d
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    new_x = (x * cos_a) - (z * sin_a)
    new_y = y
    new_z = (x * sin_a) + (z * cos_a)
    return (new_x, new_y, new_z)


def rotate_z(point_3d, angle_degrees):
    """ROLL one SHAPE point around the z axis (anticlockwise as you see it)."""
    x, y, z = point_3d
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    new_x = (x * cos_a) - (y * sin_a)
    new_y = (x * sin_a) + (y * cos_a)
    new_z = z
    return (new_x, new_y, new_z)


def rotate_all(point_3d):
    """Do all three turns, one after another, in SHAPE coordinates.

    Each line feeds its answer into the next line, like passing a
    parcel along: the turn only ever sees the corner as the previous
    turn left it.
    """
    if x_first:
        p = rotate_x(point_3d, angle_x)    # 1. tip
        p = rotate_y(p, angle_y)           # 2. turn
        p = rotate_z(p, angle_z)           # 3. roll
    else:
        p = rotate_z(point_3d, angle_z)    # 1. roll
        p = rotate_y(p, angle_y)           # 2. turn
        p = rotate_x(p, angle_x)           # 3. tip
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
                paused = not paused            # one press = one flip
            if event.key == pygame.K_o:
                x_first = not x_first          # swap the order
            if event.key == pygame.K_r:
                angle_x = 0
                angle_y = 0
                angle_z = 0

    # ---- NEW: all three angles grow every frame ----------------------
    if not paused:
        angle_x = keep_under_360( (angle_x + SPEED_X) )
        angle_y = keep_under_360( (angle_y + SPEED_Y) )
        angle_z = keep_under_360( (angle_z + SPEED_Z) )

    screen.fill(BLACK)

    # ---- turn x3 -> move away -> project, for all 8 corners ----------
    # As always, we turn the ORIGINAL cube_points by the TOTAL angles.
    screen_points = []
    for p in cube_points:
        turned = rotate_all(p)                       # SHAPE, turned 3 times
        x, y, z = turned
        moved = (x, y, (z + cube_distance))          # WORLD
        screen_points.append(project(moved))         # SCREEN

    for a, b in cube_edges:
        pygame.draw.line(screen, GREEN, screen_points[a], screen_points[b], 2)
    pygame.draw.circle(screen, YELLOW, screen_points[5], 5)

    text = ("tip x = " + str(round(angle_x, 1)) +
            "   turn y = " + str(round(angle_y, 1)) +
            "   roll z = " + str(round(angle_z, 1)))
    screen.blit(font.render(text, True, YELLOW), (20, 20))
    if x_first:
        order_text = "order: tip -> turn -> roll   (O = swap)"
    else:
        order_text = "order: roll -> turn -> tip   (O = swap)"
    screen.blit(font.render(order_text, True, YELLOW), (20, 50))
    screen.blit(font.render("SPACE = pause,  R = reset", True, YELLOW), (20, 80))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

# ----------------------------------------------------------------------
# TRY THIS:
#   * Pause (SPACE), then press O a few times. The angles do not change,
#     but the cube jumps. Why? (Lesson Part 3.)
#   * Set SPEED_X = 0 and SPEED_Z = 0. You should get Lesson 2's spin back.
#   * Set all three speeds to 1. Does the tumble look more or less
#     interesting than with three different speeds?
#   * Write a 4th order, e.g. turn -> tip -> roll, and try it.
# ----------------------------------------------------------------------
