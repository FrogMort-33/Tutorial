# ======================================================================
# LESSON 2 - STEP 3: THE SPINNING CUBE
# ----------------------------------------------------------------------
# Goal: the cube turns BY ITSELF, a little more every frame.
#
# The one new idea:
#
#     every frame:   angle_degrees = (angle_degrees + SPEED)
#
#   The main loop runs 60 times a second (clock.tick(60)). Each time,
#   the angle grows by SPEED degrees and we redraw the cube at the new
#   angle. 60 slightly-turned pictures a second look like smooth spinning
#   - exactly like the frames of a cartoon.
#
#   SPEED = 1 degree per frame
#     -> (1 * 60) = 60 degrees per second
#     -> (360 / 60) = 6 seconds for one full turn: slow and easy to watch.
#
# IMPORTANT: we never change cube_points. Every frame we turn the
# ORIGINAL corners by the TOTAL angle so far. (If we kept turning the
# already-turned corners, tiny rounding errors would pile up and the
# cube would slowly warp out of shape.)
#
# Controls:  SPACE = pause / unpause,  UP / DOWN = push away / pull closer
# Run:  python step3_spin_cube.py
# ======================================================================

import math
import pygame

pygame.init()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 2, step 3 - the spinning cube")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

CENTRE_X = (WIDTH / 2)            # (800 / 2) = 400
CENTRE_Y = (HEIGHT / 2)           # (600 / 2) = 300
FOCAL = 400

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

cube_distance = 5

# ---- The spin --------------------------------------------------------
angle_degrees = 0      # how far the cube has turned so far
SPEED = 1              # degrees added EVERY FRAME (60 frames a second)
paused = False


def rotate_y(point_3d, angle_degrees):
    """Turn one SHAPE point around the y axis (anticlockwise from above)."""
    x, y, z = point_3d
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    new_x = (x * cos_a) - (z * sin_a)
    new_y = y
    new_z = (x * sin_a) + (z * cos_a)
    return (new_x, new_y, new_z)


def project(point_3d):
    """Turn one 3D WORLD point into a 2D SCREEN point (from Lesson 1)."""
    x, y, z = point_3d
    screen_x = CENTRE_X + ( (x * FOCAL) / z )
    screen_y = CENTRE_Y - ( (y * FOCAL) / z )
    return (screen_x, screen_y)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # SPACE flips paused between True and False (one press = one flip).
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            paused = not paused

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        cube_distance = (cube_distance + 0.05)
    if keys[pygame.K_DOWN]:
        cube_distance = (cube_distance - 0.05)
    if cube_distance < 3:
        cube_distance = 3

    # ---- NEW: turn a little more every frame -------------------------
    if not paused:
        angle_degrees = (angle_degrees + SPEED)
    if angle_degrees >= 360:                    # a full turn is the same
        angle_degrees = (angle_degrees - 360)   # as no turn: start again

    screen.fill(BLACK)

    # ---- rotate -> move away -> project, for all 8 corners -----------
    screen_points = []
    for p in cube_points:
        turned = rotate_y(p, angle_degrees)          # SHAPE, turned
        x, y, z = turned
        moved = (x, y, (z + cube_distance))          # WORLD
        screen_points.append(project(moved))         # SCREEN

    for a, b in cube_edges:
        pygame.draw.line(screen, GREEN, screen_points[a], screen_points[b], 2)

    text = "angle = " + str(angle_degrees) + "   SPEED = " + str(SPEED) + " deg/frame"
    screen.blit(font.render(text, True, YELLOW), (20, 20))
    text2 = "SPACE = pause,  UP / DOWN = distance " + str(round(cube_distance, 1))
    screen.blit(font.render(text2, True, YELLOW), (20, 50))

    pygame.display.flip()
    clock.tick(60)                     # 60 frames a second

pygame.quit()

# ----------------------------------------------------------------------
# TRY THIS:
#   * SPEED = 3. How many seconds for one full turn now? (360 / (3 * 60))
#   * SPEED = -1. Which way does it spin now?
#   * Make TWO cubes: draw the loop twice, the second one with
#     ((x + 3), y, (z + cube_distance)) and the angle doubled.
#   * Spin the pyramid you made after Lesson 1 instead of the cube.
# ----------------------------------------------------------------------
