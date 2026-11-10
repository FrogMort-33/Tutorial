# ======================================================================
# LESSON 1 - STEP 2: A POLYGON MADE OF "POINTS" AND "EDGES"
# ----------------------------------------------------------------------
# Goal: draw a house shape (a square with a triangle roof).
#
# Instead of writing every line by hand, we store a shape in TWO lists:
#
#   points  - WHERE the corners are          (a list of (x, y) pairs)
#   edges   - WHICH corners join with a line (a list of pairs of numbers)
#
# Each edge says "join point number A to point number B".
# This is EXACTLY how Wireframe Warfare stores its shapes - there they
# are called "verts" (vertices = corners) and "edges".
#
# Run:  python step2_polygon.py
# ======================================================================

import pygame

pygame.init()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Step 2 - points and edges")

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

# ---- The shape's corners (points) ------------------------------------
# Each corner gets a number: its position in the list, starting at 0.
points = [
    (300, 450),    # point 0 - bottom-left of the square
    (500, 450),    # point 1 - bottom-right
    (500, 250),    # point 2 - top-right
    (300, 250),    # point 3 - top-left
    (400, 150),    # point 4 - tip of the roof
]

# ---- Which corners are joined (edges) --------------------------------
edges = [
    (0, 1),        # bottom of the square
    (1, 2),        # right wall
    (2, 3),        # top of the square (the ceiling)
    (3, 0),        # left wall
    (3, 4),        # left side of the roof
    (4, 2),        # right side of the roof
]

# A small font so we can write the point numbers on screen.
font = pygame.font.SysFont(None, 28)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)

    # ---- Draw every edge ---------------------------------------------
    # For each edge, look up its two point numbers in the points list,
    # then draw a line between those two positions.
    for edge in edges:
        a = edge[0]                 # number of the first corner
        b = edge[1]                 # number of the second corner
        start = points[a]           # (x, y) of the first corner
        end = points[b]             # (x, y) of the second corner
        pygame.draw.line(screen, GREEN, start, end, LINE_THICKNESS)

    # ---- Label every point with its number (just to help us learn) ---
    for number in range(len(points)):
        x, y = points[number]
        pygame.draw.circle(screen, YELLOW, (x, y), 5)
        label = font.render(str(number), True, YELLOW)
        # Put the label a little to the right of, and above, the dot.
        screen.blit(label, ((x + 8), (y - 22)))

    pygame.display.flip()

pygame.quit()

# ----------------------------------------------------------------------
# TRY THIS:
#   * Delete the edge (2, 3). What disappears?
#   * Add a chimney: two new points and three new edges.
#   * Move point 4 to (400, 50). What happens to the roof?
# ----------------------------------------------------------------------
