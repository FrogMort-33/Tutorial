# ======================================================================
# LESSON 1 - STEP 1: DRAW ONE LINE
# ----------------------------------------------------------------------
# Goal: open a window and draw a single green line on it.
#
# Every wireframe game (including Wireframe Warfare) is, in the end,
# just LOTS of straight lines drawn on a flat screen. So the very first
# thing to learn is how to draw ONE line.
#
# Install once:   pip install pygame-ce
# Run:            python step1_line.py
# Close the window to quit.
# ======================================================================

import pygame                      # pygame gives us a window and drawing tools

# ---- Set up the window -----------------------------------------------
pygame.init()                      # switch pygame on

WIDTH = 800                        # window width in pixels
HEIGHT = 600                       # window height in pixels
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Step 1 - one line")

# ---- Colours are (Red, Green, Blue), each 0 to 255 -------------------
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# ---- How thick our lines are -------------------------------------------
# pygame.draw.line's last number is the line's thickness in pixels.
# We give it a name instead of typing 2 every time, so:
#   * the code says WHAT the number means, and
#   * changing this ONE line makes every line thicker or thinner.
# 2 pixels is thick enough to see clearly on an 800 x 600 window
# but thin enough to keep the "wireframe" look. Try 1 or 5.
LINE_THICKNESS = 2

# ---- The two ends of our line ----------------------------------------
# A point on the screen is (x, y), measured in pixels.
#   x counts from the LEFT edge, going right.
#   y counts from the TOP edge, going DOWN  (this surprises everyone!).
# So (0, 0) is the top-left corner of the window.
start_point = (100, 500)           # near the bottom-left
end_point = (700, 100)             # near the top-right

# ---- The main loop ----------------------------------------------------
# A game keeps redrawing the screen over and over until you quit.
running = True
while running:

    # 1. Check if the user clicked the window's close button.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. Wipe the screen black (start each picture fresh).
    screen.fill(BLACK)

    # 3. Draw the line:  where, colour, start, end, thickness in pixels
    pygame.draw.line(screen, GREEN, start_point, end_point, LINE_THICKNESS)

    # 4. Show what we just drew.
    pygame.display.flip()

pygame.quit()

# ----------------------------------------------------------------------
# TRY THIS:
#   * Change end_point to (700, 500). Which way does the line go now?
#   * Change GREEN to (255, 0, 0). What colour is the line?
#   * Change LINE_THICKNESS to 10. How wide is the line now?
#   * Draw a second line by copying the pygame.draw.line(...) row.
# ----------------------------------------------------------------------
