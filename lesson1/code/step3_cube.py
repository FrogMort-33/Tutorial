# ======================================================================
# LESSON 1 - STEP 3: A 3D CUBE ON A FLAT SCREEN
# ----------------------------------------------------------------------
# Goal: describe a cube in 3D, then draw it on the 2D screen.
#
# Three new ideas:
#
#   1. A 3D point has THREE numbers: (x, y, z)
#        x = left / right      (+ is right)
#        y = down / up         (+ is UP - the opposite of the screen!)
#        z = distance away     (+ is further into the screen)
#      Wireframe Warfare uses this same layout.
#
#   2. A 3D shape is still just points + edges (like the house in step 2),
#      only now each point has a z.
#
#   3. PROJECTION turns a 3D point into a 2D screen point. The rule:
#
#           screen_x = centre_x + ( (x * FOCAL) / z )
#           screen_y = centre_y - ( (y * FOCAL) / z )
#
#      Read the brackets from the INSIDE out:
#        first  (x * FOCAL)        - scale the point up by the lens zoom
#        then   ( ... / z)         - shrink it by its distance
#        last   centre_x + ( ... ) - move it to the middle of the window
#
#      BRACKETS RULE FOR THIS COURSE: we put brackets around every part
#      of every calculation, so you never have to remember which of
#      + - * / Python does first. The brackets show the order.
#
#      Dividing by z is the whole trick: the further away something is
#      (bigger z), the closer to the centre it lands - so it looks smaller.
#      That is "perspective", and it is how your eyes see the world too.
#
# Controls:  UP arrow = push the cube away,  DOWN arrow = pull it closer
# Run:  python step3_cube.py
# ======================================================================

import pygame

pygame.init()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Step 3 - a 3D cube")
clock = pygame.time.Clock()        # used to slow the loop to 60 frames/sec

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# ---- How thick our lines are -------------------------------------------
# pygame.draw.line's last number is the line's thickness in pixels.
# We give it a name instead of typing 2 every time, so:
#   * the code says WHAT the number means, and
#   * changing this ONE line makes every line thicker or thinner.
# 2 pixels is thick enough to see clearly on an 800 x 600 window
# but thin enough to keep the "wireframe" look. Try 1 or 5.
LINE_THICKNESS = 2

# The middle of the screen. In 3D, (x=0, y=0) appears here.
CENTRE_X = (WIDTH / 2)            # (800 / 2) = 400
CENTRE_Y = (HEIGHT / 2)           # (600 / 2) = 300

# FOCAL is like the zoom on a camera lens. Bigger = more zoomed in.
FOCAL = 400

# ---- The cube's 8 corners, in 3D -------------------------------------
# These are SHAPE coordinates: measured from the cube's OWN centre.
# The x, y and z axes go right through the middle of the cube, so the
# middle is (0, 0, 0) and every corner is 1 step away: -1 or +1.
# (Later we add cube_distance to turn them into WORLD coordinates,
#  measured from you, and project() turns those into SCREEN pixels.)
# The cube is 2 units wide.
# Bottom 4 corners have y = -1, top 4 have y = +1.
# Front 4 corners have z = -1, back 4 have z = +1.
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

# ---- The cube's 12 edges ---------------------------------------------
cube_edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),   # the 4 edges of the bottom square
    (4, 5), (5, 6), (6, 7), (7, 4),   # the 4 edges of the top square
    (0, 4), (1, 5), (2, 6), (3, 7),   # the 4 upright edges joining them
]

# ---- Where the cube is -----------------------------------------------
# We are standing at z = 0 looking along +z. The cube starts 5 units away.
cube_distance = 5


def project(point_3d):
    """Turn one 3D point (x, y, z) into a 2D screen point (sx, sy).

    This is the most important function in all 3D graphics.
    Wireframe Warfare has the same one - also called project().
    """
    x, y, z = point_3d

    # Divide by z: far things move toward the centre (look smaller).
    #   step 1: (x * FOCAL)          scale by the lens zoom
    #   step 2: ((x * FOCAL) / z)    shrink by the distance
    #   step 3: CENTRE_X + (...)     start from the middle of the window
    screen_x = CENTRE_X + ( (x * FOCAL) / z )

    # Same steps for y, but MINUS because 3D y goes UP
    # while screen y goes DOWN.
    screen_y = CENTRE_Y - ( (y * FOCAL) / z )

    return (screen_x, screen_y)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ---- Keys move the cube nearer / further -------------------------
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        cube_distance = (cube_distance + 0.05)
    if keys[pygame.K_DOWN]:
        cube_distance = (cube_distance - 0.05)
    if cube_distance < 2:            # don't let it come through the screen
        cube_distance = 2            # (z must stay above 0 or we'd divide by 0)

    screen.fill(BLACK)

    # ---- Step A: work out where every corner lands on the screen -----
    screen_points = []               # will hold 8 (sx, sy) pairs
    for p in cube_points:
        x, y, z = p
        moved = (x, y, (z + cube_distance))      # slide the cube away from us
        screen_points.append(project(moved))     # 3D -> 2D

    # ---- Step B: draw the edges, exactly like the house in step 2 ----
    for a, b in cube_edges:
        pygame.draw.line(screen, GREEN, screen_points[a], screen_points[b], LINE_THICKNESS)

    # A little text so we know the distance.
    font = pygame.font.SysFont(None, 28)
    text = "distance = " + str(round(cube_distance, 1)) + "   (UP / DOWN arrows)"
    screen.blit(font.render(text, True, YELLOW), (20, 20))

    pygame.display.flip()
    clock.tick(60)                   # at most 60 pictures per second

pygame.quit()

# ----------------------------------------------------------------------
# TRY THIS:
#   * Change FOCAL to 200, then 800. What does it do?
#   * Change the 1s in cube_points to 2s. What happens?
#   * Add 3 to every x (moved = ((x + 3), y, (z + cube_distance))). Where does it go?
#   * Turn the cube into a pyramid: 4 bottom corners + 1 top point (0, 1, 0).
# ----------------------------------------------------------------------
