# =====================================================================================
# step2_camera_cube.py  -  raylib lesson, Parts 3 and 4: Camera3D and Lesson 1's cube, drawn by the GPU
# =====================================================================================
#
# WHAT THIS SHOWS
#   Lesson 1's cube (2 m wide, centre 5 m ahead), but this time we never call project() ourselves.
#   We describe a CAMERA to raylib once per frame, say "draw a cube here", and the graphics card does the
#   turning, projecting and filling of every corner.
#   To PROVE it is the same maths as Lesson 1, corner 5 is worked out BOTH ways:
#       * by our own Lesson 1 formula  (a white cross on the screen)
#       * by raylib's own projection   (a yellow ball in 3D, and rl.get_world_to_screen)
#   They land on the same pixel: SCREEN (500, 200) at the start.
#
# KEYS
#   UP / DOWN      cube further / nearer        (cube_distance, as in Lesson 1)
#   LEFT / RIGHT   turn the camera left / right (yaw)
#   Z / X          narrower / wider view        (fovy, raylib's version of FOCAL; Part 3)
#   Esc            quit
#
# THE COORDINATE SYSTEMS in this file (picture images/r06_mirror.png):
#   SHAPE   metres from the cube's own centre:   cube_points, corner 5 = (1, 1, -1)
#   WORLD   metres from the viewer at (0, 0, 0): the COURSE's system. x right, y up, z AHEAD (into the screen).
#   GPU     what raylib is given: (-WORLD x, WORLD y, WORLD z). One minus sign: THE MIRROR (function gpu below)
#   SCREEN  pixels from the window's top-left, y DOWN.

import math
import pyray as rl

WIDTH = 800
HEIGHT = 600
CENTRE_X = (WIDTH / 2)      # 400: SCREEN x of the middle of the window
CENTRE_Y = (HEIGHT / 2)     # 300: SCREEN y of the middle
FOCAL = 400                 # Lesson 1's zoom: half the window's width -> a 90 degree view across

# -------------------------------------------------------------------------------------
# 1. THE MIRROR: WORLD -> GPU   (picture images/r06_mirror.png)
# -------------------------------------------------------------------------------------
# The course (and FrogWorld) use x RIGHT, y UP, z AHEAD.
# OpenGL, inside raylib, is the mirror image: stand at (0, 0, 0) looking along +z with +y up, and +x is
# on your LEFT. If we gave raylib our numbers as they are, every picture would come out flipped left for
# right (corner 5 would appear top-LEFT).
# The fix is one minus sign on x for every point we hand over. FrogWorld's gpu_render.gpu_point does the same.
#   e.g. corner 5 in WORLD (1, 1, 4) -> GPU (-1, 1, 4)
def gpu(x, y, z):
    """WORLD (x, y, z) -> GPU (-x, y, z)."""
    return ((-x), y, z)


# -------------------------------------------------------------------------------------
# 2. LESSON 1's PROJECTION, kept only to CHECK raylib's answer
# -------------------------------------------------------------------------------------
def project(x, y, z):
    """WORLD (camera at (0, 0, 0) looking along +z) -> SCREEN pixels. Lesson 1, unchanged.
       e.g. corner 5 WORLD (1, 1, 4):  sx = (400 + ((1 x 400) / 4)) = (400 + 100) = 500
                                       sy = (300 - ((1 x 400) / 4)) = (300 - 100) = 200"""
    sx = (CENTRE_X + ((x * FOCAL) / z))
    sy = (CENTRE_Y - ((y * FOCAL) / z))
    return (sx, sy)


# -------------------------------------------------------------------------------------
# 3. fovy: raylib's zoom   (picture images/r08_fovy.png)
# -------------------------------------------------------------------------------------
# raylib does not use FOCAL. It wants the camera's view angle from the TOP edge of the window to the BOTTOM
# edge, in DEGREES: "field of view, y" = fovy.
# The top edge is CENTRE_Y = 300 pixels above the middle, at FOCAL = 400 pixels "in front of the eye", so
# half the angle is atan(300 / 400):
#       fovy = (2 x atan(CENTRE_Y / FOCAL)) = (2 x atan(300 / 400)) = (2 x 36.87) = 73.74 degrees
# With this fovy raylib draws EXACTLY the picture Lesson 1's FOCAL 400 drew.
def fovy_from_focal(focal):
    return math.degrees((2 * math.atan((CENTRE_Y / focal))))


fovy = fovy_from_focal(FOCAL)               # 73.74 degrees
cube_distance = 5                           # metres: WORLD z of the cube's centre (Lesson 1's number)
yaw = 0.0                                   # radians: + turns the camera RIGHT (the course's rule)

# The cube's 8 corners, SHAPE coordinates (metres from its centre), numbered as in Lesson 1
cube_points = [
    (-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1),   # 0 1 2 3: the bottom four
    (-1, 1, -1), (1, 1, -1), (1, 1, 1), (-1, 1, 1),       # 4 5 6 7: the top four
]

rl.init_window(WIDTH, HEIGHT, "Step 2 - Camera3D and Lesson 1's cube")
rl.set_target_fps(60)

while not rl.window_should_close():

    # --- keys (rl.is_key_down = "held this frame", like pygame.key.get_pressed()) ---
    if rl.is_key_down(rl.KEY_UP):
        cube_distance = (cube_distance + 0.05)
    if rl.is_key_down(rl.KEY_DOWN):
        cube_distance = max(2.0, (cube_distance - 0.05))
    if rl.is_key_down(rl.KEY_RIGHT):
        yaw = (yaw + 0.02)
    if rl.is_key_down(rl.KEY_LEFT):
        yaw = (yaw - 0.02)
    if rl.is_key_down(rl.KEY_Z):
        fovy = max(20.0, (fovy - 0.5))
    if rl.is_key_down(rl.KEY_X):
        fovy = min(120.0, (fovy + 0.5))

    # --- THE CAMERA (picture images/r07_camera3d.png) ---
    # position  where the eye is                 WORLD (0, 0, 0)  -> GPU (0, 0, 0)
    # target    ANY point straight ahead of it   WORLD 1 m ahead along the facing direction
    #           facing = (sin(yaw), 0, cos(yaw)) (the course's rule); at yaw 0 that is (0, 0, 1)
    # up        which way is "up" for the eye    (0, 1, 0): the top of the window shows +y
    # fovy      the view angle top-to-bottom     73.74 degrees (= FOCAL 400)
    # CAMERA_PERSPECTIVE: far things smaller (divide by z). CAMERA_ORTHOGRAPHIC would not divide.
    eye = gpu(0, 0, 0)
    look_at = gpu(math.sin(yaw), 0, math.cos(yaw))
    camera = rl.Camera3D(eye, look_at, (0, 1, 0), fovy, rl.CAMERA_PERSPECTIVE)

    centre = gpu(0, 0, cube_distance)       # the cube's centre: WORLD (0, 0, 5) -> GPU (0, 0, 5)
    sx5, sy5, sz5 = cube_points[5]
    corner5 = (sx5, sy5, (sz5 + cube_distance))   # SHAPE (1, 1, -1) -> WORLD (1, 1, 4): slide it away, Lesson 1

    rl.begin_drawing()
    rl.clear_background((20, 24, 32, 255))

    # ======== 3D: everything between begin_mode_3d and end_mode_3d goes through the camera ========
    rl.begin_mode_3d(camera)
    #   From here on, positions are GPU METRES, not pixels. raylib turns them to pixels on the card.

    rl.draw_cube(centre, 2, 2, 2, (200, 60, 60, 255))
    #   centre (GPU metres), width (along x), height (along y), length (along z), colour.
    #   2 x 2 x 2 metres: corners at +-1 from the centre, exactly cube_points. The card fills all 6 faces.
    rl.draw_cube_wires(centre, 2, 2, 2, (255, 255, 255, 255))   # its 12 edges, as Lesson 1 drew them
    rl.draw_sphere(gpu(*corner5), 0.08, (255, 214, 90, 255))    # a small yellow ball ON corner 5 (radius 8 cm)
    rl.draw_grid(20, 1.0)
    #   a floor grid at GPU y = 0: 20 squares each way, 1 m each, centred on (0, 0, 0). Our eye is ALSO at
    #   y = 0, so we see it exactly edge-on (one line across the middle). Lift the eye to see it as a floor.

    rl.end_mode_3d()
    # ======== back to 2D: positions are SCREEN pixels again (good for the HUD) ========

    # Lesson 1's own answer for corner 5 (only true at yaw 0: our project() has no turning in it)
    if yaw == 0.0:
        px, py = project(*corner5)
        rl.draw_line(int(px - 12), int(py), int(px + 12), int(py), (255, 255, 255, 255))
        rl.draw_line(int(px), int(py - 12), int(px), int(py + 12), (255, 255, 255, 255))
        rl.draw_text("Lesson 1 formula: (" + str(round(px)) + ", " + str(round(py)) + ")", 20, 50, 20, (255, 255, 255, 255))

    # raylib's own answer: the same sums the card does, asked for on the CPU
    p = rl.get_world_to_screen(gpu(*corner5), camera)
    rl.draw_text("raylib get_world_to_screen: (" + str(round(p.x)) + ", " + str(round(p.y)) + ")", 20, 80, 20, (255, 214, 90, 255))

    rl.draw_text("cube_distance " + str(round(cube_distance, 2)) + " m   fovy " + str(round(fovy, 2)) + " deg   yaw " + str(round(yaw, 2)),
                 20, 20, 20, (180, 200, 230, 255))
    rl.draw_text("UP/DOWN distance   LEFT/RIGHT turn   Z/X fovy", 20, 570, 18, (140, 150, 170, 255))
    rl.end_drawing()

rl.close_window()
