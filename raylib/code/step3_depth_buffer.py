# =====================================================================================
# step3_depth_buffer.py  -  raylib lesson, Part 5: the depth buffer, done by the graphics card
# =====================================================================================
#
# WHAT THIS SHOWS
#   Lesson 10's depth buffer (one "how far away" number kept for every pixel), but now the GRAPHICS CARD
#   keeps it, for free, and we never sort anything.
#   Things are drawn in a deliberately BAD order:  red bar, blue bar, floor grid, and the FAR wall LAST.
#     * a red bar and a blue bar that pass THROUGH each other (a cross). Lesson 10 showed there is no
#       right painter's order for these: each bar is partly in front of the other.
#     * the floor grid's lines, drawn AFTER the bars although the bars stand on top of them
#     * a grey wall 1 m behind them, drawn last of all
#   With the depth test ON  : the picture is right anyway (the card compares distances pixel by pixel).
#   With the depth test OFF : the card just paints in the order we drew: the blue bar covers ALL of the red
#                             one, and the floor lines are painted across both bars.
#                             (The wall never overlaps the bars on screen from up here, so it shows no
#                             change: it is there to prove the card does not care that we drew it last.)
#
# KEYS
#   D              depth test on / off
#   LEFT / RIGHT   walk the camera round the cross (to see the bars pass through each other)
#   Esc            quit
#
# THE COORDINATE SYSTEMS (as step 2):
#   WORLD   metres from (0, 0, 0) on the floor, x right, y up, z ahead (the course / FrogWorld)
#   GPU     (-WORLD x, WORLD y, WORLD z): the mirror, function gpu()
#   SCREEN  pixels from the window's top-left, y down

import math
import pyray as rl

WIDTH = 800
HEIGHT = 600
FOVY = 73.74                # degrees, = Lesson 1's FOCAL 400 in an 800 x 600 window (step 2 worked it out)


def gpu(x, y, z):
    """WORLD (x, y, z) -> GPU (-x, y, z): the mirror (step 2, picture r06_mirror.png)."""
    return ((-x), y, z)


depth_on = True
angle = 0.5                 # radians: where the camera stands on its circle round the cross (0 = straight south of it)

rl.init_window(WIDTH, HEIGHT, "Step 3 - the GPU depth buffer")
rl.set_target_fps(60)

while not rl.window_should_close():

    if rl.is_key_pressed(rl.KEY_D):                 # is_key_pressed: True only on the frame the key goes DOWN
        depth_on = (not depth_on)
    if rl.is_key_down(rl.KEY_RIGHT):
        angle = (angle + 0.02)
    if rl.is_key_down(rl.KEY_LEFT):
        angle = (angle - 0.02)

    # The camera walks round a circle, radius 6 m, round the cross's centre WORLD (0, 1, 6), 3.4 m up,
    # always looking at that centre.
    #   e.g. angle 0.5:  x = (6 x sin(0.5)) = (6 x 0.479) = 2.88    z = (6 - (6 x cos(0.5))) = (6 - 5.27) = 0.73
    eye = ((6 * math.sin(angle)), 3.4, (6 - (6 * math.cos(angle))))
    camera = rl.Camera3D(gpu(*eye), gpu(0, 1, 6), (0, 1, 0), FOVY, rl.CAMERA_PERSPECTIVE)

    rl.begin_drawing()
    rl.clear_background((20, 24, 32, 255))
    #   clear_background wipes the colours AND the card's depth memory: every pixel's "nearest so far"
    #   goes back to "as far as can be". (Lesson 10: depth[...] = infinity at the start of every frame.)

    rl.begin_mode_3d(camera)

    if not depth_on:
        rl.rl_draw_render_batch_active()    # draw anything raylib is still holding, with the OLD setting
        rl.rl_disable_depth_test()          # from now on: no distance test, last drawn wins (painter's)

    # 1. the red bar: 6 m long along WORLD x, 0.6 m tall, 0.6 m deep, centre WORLD (0, 1, 6)
    rl.draw_cube(gpu(0, 1, 6), 6.0, 0.6, 0.6, (210, 60, 60, 255))
    # 2. the blue bar: 6 m long along WORLD z, through the SAME centre: the two bars pass through each other
    rl.draw_cube(gpu(0, 1, 6), 0.6, 0.6, 6.0, (60, 110, 220, 255))
    rl.draw_grid(20, 1.0)                   # the floor, y = 0
    # 3. the grey wall, drawn LAST although it is the FURTHEST thing: 10 m wide, 4 m tall, 1 m behind the
    #    blue bar's far end (that end is at WORLD z = (6 + 3) = 9; the wall at z = 10)
    rl.draw_cube(gpu(0, 2, 10), 10.0, 4.0, 0.2, (120, 125, 135, 255))

    if not depth_on:
        rl.rl_draw_render_batch_active()    # draw the held shapes NOW, while the test is still off
        rl.rl_enable_depth_test()           # and put it back the way raylib expects

    rl.end_mode_3d()

    if depth_on:
        rl.draw_text("depth test ON: the card keeps the nearest distance per pixel", 20, 20, 20, (120, 230, 140, 255))
    else:
        rl.draw_text("depth test OFF: last drawn wins (blue over red, lines over both)", 20, 20, 20, (250, 140, 110, 255))
    rl.draw_text("D depth on/off    LEFT/RIGHT walk round", 20, 570, 18, (140, 150, 170, 255))
    rl.end_drawing()

rl.close_window()
