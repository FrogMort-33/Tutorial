# =====================================================================================
# step1_window.py  -  raylib lesson, Part 2: a window, a loop, and some 2D drawing
# =====================================================================================
#
# WHAT THIS SHOWS
#   The smallest raylib program: open a window, run a loop, wipe the picture, draw a few 2D things, show it.
#   It is the raylib copy of the very first pygame program of Lesson 1 (step1_line.py).
#
# HOW TO RUN (Windows, Python 3.14):
#       py -m pip install raylib          <- once. It gives you the module called "pyray".
#       py step1_window.py
#   Esc or the window's close button ends it.
#
# THE COORDINATE SYSTEM in this file: SCREEN only.
#   SCREEN = pixels from the window's TOP-LEFT corner, x to the right, y DOWN. Exactly the same as pygame.
#     (0, 0) is the top-left pixel, (799, 599) the bottom-right one in an 800 x 600 window.
#
# PICTURE: images/r04_loop_side_by_side.png puts this file next to the pygame version, line by line.

import pyray as rl          # "pyray" = raylib with Python-style names (init_window, not InitWindow).
                            # "as rl" so every raylib call starts with rl. and you can see at once which
                            # lines talk to raylib.

# -------------------------------------------------------------------------------------
# 1. THE WINDOW
# -------------------------------------------------------------------------------------
WIDTH = 800                 # pixels across  (the same 800 x 600 as every lesson of the 3D course)
HEIGHT = 600                # pixels down

rl.init_window(WIDTH, HEIGHT, "Step 1 - a raylib window")
#   pygame needed two lines for this:  pygame.init()  and  screen = pygame.display.set_mode((800, 600))
#   raylib does both in one, AND it quietly asks the graphics card for an OpenGL "context": the card's own
#   memory for this window (the picture, and later the depth memory of Part 5). You never see that object;
#   raylib keeps it inside itself, so there is no "screen" variable to pass around.

rl.set_target_fps(60)
#   = pygame's clock.tick(60), but said ONCE here instead of every frame. end_drawing() (below) waits
#   for the rest of each 1/60 s = 16.7 ms. Set 0 to run flat out (useful when you measure speed: step 4).

# -------------------------------------------------------------------------------------
# 2. COLOURS
# -------------------------------------------------------------------------------------
# A raylib colour has FOUR numbers: red, green, blue, and ALPHA (how solid: 255 = solid, 0 = invisible).
# pygame mostly used three. A plain Python tuple works anywhere raylib wants a colour.
SKY = (135, 190, 235, 255)
FROG_GREEN = (60, 170, 70, 255)
DARK = (25, 30, 40, 255)

x = 100                     # SCREEN x of the moving square's left edge, pixels. It slides right each frame.

# -------------------------------------------------------------------------------------
# 3. THE LOOP
# -------------------------------------------------------------------------------------
# rl.window_should_close() is True once Esc is pressed or the close button clicked.
# pygame needed a "for event in pygame.event.get(): if event.type == pygame.QUIT" loop for that;
# raylib reads the events for you inside end_drawing(), and you just ASK it (rl.is_key_down etc).
while not rl.window_should_close():

    # --- move things (no drawing yet) ---
    x = (x + 2)                                 # 2 pixels per frame = (2 x 60) = 120 pixels per second
    if x > (WIDTH - 100):                       # off the right edge? start again on the left
        x = 0

    # --- draw ONE frame ---
    rl.begin_drawing()
    #   "I am starting a new picture." Everything drawn from here goes into the BACK picture: a hidden
    #   copy that the player cannot see yet (picture r05_frame_steps.png). pygame drew into a hidden copy
    #   too; you just never had to say "begin".

    rl.clear_background(SKY)                    # = screen.fill(SKY): every pixel of the back picture to SKY

    rl.draw_rectangle(x, 250, 100, 100, FROG_GREEN)
    #   left x, top y, width, height, colour  (SCREEN pixels). pygame: pygame.draw.rect(screen, colour, (x, 250, 100, 100))

    rl.draw_line(0, 400, WIDTH, 400, DARK)      # from (0, 400) to (800, 400): the ground line
    rl.draw_circle(650, 120, 40, (250, 220, 80, 255))   # centre (650, 120), radius 40: a sun

    rl.draw_text("Hello from raylib", 20, 20, 30, DARK)
    #   text, left x, top y, size (pixels tall), colour. pygame needed a Font object and a blit for this.

    rl.draw_fps(20, 60)                         # raylib counts the frames per second for you

    rl.end_drawing()
    #   "The picture is finished": the back picture is SWAPPED to the front so the player sees it all at
    #   once (= pygame.display.flip()). It also waits for the 60 FPS beat and reads the keyboard and mouse.

# -------------------------------------------------------------------------------------
# 4. THE END
# -------------------------------------------------------------------------------------
rl.close_window()           # = pygame.quit(): gives the window and the card's memory back
