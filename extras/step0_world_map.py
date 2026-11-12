# ======================================================================
# LESSON 4 - STEP 0: THE WORLD, SEEN FROM ABOVE (no walking yet)
# ----------------------------------------------------------------------
# Goal: before anything moves, SEE the world. The cube gets a fixed
# place in the WORLD, you get one too, and a mini-map in the corner
# shows both from above.
#
# This starts from Lesson 3B's lit solid cube (step3_lit_cube.py).
#
# What is new since Lesson 3B:
#
#   1. cube_position = (0, 0, 5)
#        The cube now has a fixed place in the WORLD. This is the same
#        5 as Lesson 1's cube_distance, so the picture looks the same.
#
#   2. cam_x, cam_y, cam_z  (0, 0, 0)
#        Where YOU are standing, in WORLD coordinates. Nothing uses
#        them for the 3D picture yet: that is step 1.
#
#   3. A mini-map in the bottom-right corner: the WORLD seen from
#      above, with the cube's outline and you as a pink dot. The pink
#      line shows the way you face (+z).
#
# The recipe for one corner, every frame:
#
#   SHAPE -> spin -> + cube_position -> project
#   (cube_points)    (WORLD)            (SCREEN)
#
#   You are still sitting at the WORLD centre facing +z, so WORLD and
#   CAMERA are the same thing and project() can use WORLD points.
#
# Controls:  SPACE = spin the cube on / off,   R = reset
#            L = light on / off,   C = six colours / one colour
# Run:  python step0_world_map.py
# ======================================================================

import math
import pygame

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)   # the whole screen
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Lesson 4, step 0 - the world from above")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)
map_font = pygame.font.SysFont(None, 18)    # NEW: small labels on the mini-map

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
PINK = (255, 105, 200)        # NEW: the colour we use for YOU (the camera)
MAP_BACK = (25, 30, 36)       # NEW: dark grey-blue behind the mini-map

# ---- One colour for each face (from Lesson 3) -------------------------
RED = (235, 80, 80)          # front
PURPLE = (160, 100, 230)     # back
BLUE = (70, 150, 255)        # left
GREEN = (70, 210, 120)       # right
GOLD = (245, 200, 60)        # top
ORANGE = (245, 140, 50)      # bottom
CUBE_GREEN = (70, 230, 120)  # one colour for the whole cube (C key)

CENTRE_X = (WIDTH / 2)            # (800 / 2) = 400
CENTRE_Y = (HEIGHT / 2)           # (600 / 2) = 300
FOCAL = (WIDTH / 2)               # 90 degree view on any screen (400 on an 800-wide window)

# ---- The cube's 8 corners, in SHAPE coordinates (same as always) ------
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

# ---- The cube's 6 faces (from Lesson 3) -------------------------------
# Each face lists its 4 corners CLOCKWISE as seen from OUTSIDE the cube,
# its colour, and its NORMAL (from Lesson 3B): the arrow 1 long that
# points straight OUT of the face, in SHAPE coordinates.
cube_faces = [
    ((4, 5, 1, 0), RED,    ( 0,  0, -1)),   # front  -> toward you  (-z)
    ((6, 7, 3, 2), PURPLE, ( 0,  0,  1)),   # back   -> away        (+z)
    ((7, 4, 0, 3), BLUE,   (-1,  0,  0)),   # left   -> left        (-x)
    ((5, 6, 2, 1), GREEN,  ( 1,  0,  0)),   # right  -> right       (+x)
    ((7, 6, 5, 4), GOLD,   ( 0,  1,  0)),   # top    -> up          (+y)
    ((2, 3, 0, 1), ORANGE, ( 0, -1,  0)),   # bottom -> down        (-y)
]

# ---- NEW: where the cube lives in the WORLD ----------------------------
# Before, we added cube_distance to z and that was the whole story,
# because you never moved. Now the cube gets a proper address on the
# map, and YOU get one too (below).
# (0, 0, 5): straight ahead of the starting spot, 5 away - the same 5
# as Lessons 1 to 3, so the picture looks exactly like before.
cube_position = (0, 0, 5)
cube_x, cube_y, cube_z = cube_position      # unpack the 3 numbers

# ---- NEW: where YOU are standing (the camera), in WORLD coordinates ---
# (0, 0, 0): the seat you sat in for Lessons 1 to 3.
# In this step only the mini-map uses them. Step 1 lets you walk.
cam_x = 0
cam_y = 0
cam_z = 0

# ---- The light (from Lesson 3B, unchanged) ----------------------------
# The lamp belongs to the WORLD (like the sun), so it stays put.
LIGHT = (0.48, 0.6, -0.64)
AMBIENT = 0.2

# ---- The cube's own spin (from Lessons 2 and 2B) ----------------------
# NEW: the cube starts STILL, with all angles at 0, so corner 5 is at
# WORLD (1, 1, 4) like in the lesson's worked examples. SPACE spins it.
angle_x = 0
angle_y = 0
angle_z = 0
SPEED_X = 0.5
SPEED_Y = 1
SPEED_Z = 0.25
spinning = False       # NEW: SPACE flips this
use_light = True
one_colour = False     # NEW default: six colours, so you can always
                       # tell WHICH side you see

# ---- NEW: the mini-map ------------------------------------------------
# A 160 x 160 px box, 10 px in from the bottom-right corner of the screen
# (on an 800 x 600 window: left = 630, top = 430, as in the lesson):
MAP_SIZE = 160
MAP_LEFT = (WIDTH - 10 - MAP_SIZE)
MAP_TOP = (HEIGHT - 10 - MAP_SIZE)
# World (0, 0, 0) goes at (MAP_CX, MAP_CY):
#   across: the middle of the box
#   down:   30 px above the bottom of the box
# Why so low? The cube is at z = 5, which lands (5 * 10) = 50 px higher:
# the exact middle of the box. You start at the bottom looking up the
# map at it, just like the lesson's diagrams.
MAP_CX = (MAP_LEFT + (MAP_SIZE / 2))
MAP_CY = (MAP_TOP + 130)
X_AXIS = (70, 150, 255)                 # NEW: axis colours, as in the lesson's maps
Z_AXIS = (245, 140, 50)
Y_AXIS = (255, 255, 0)
MAP_TICK = 2                            # NEW: a number on the map's sides every 2 units
MAP_SCALE = 10                          # 10 px for every 1 world unit
                                        # (the box shows 16 units across)


# ---- The three turns (from Lesson 2B, unchanged) -----------------------
def rotate_x(point_3d, angle_degrees):
    """TIP one point around the x axis (+y swings toward +z)."""
    x, y, z = point_3d
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    new_x = x
    new_y = (y * cos_a) - (z * sin_a)
    new_z = (y * sin_a) + (z * cos_a)
    return (new_x, new_y, new_z)


def rotate_y(point_3d, angle_degrees):
    """TURN one point around the y axis (+x swings toward +z)."""
    x, y, z = point_3d
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    new_x = (x * cos_a) - (z * sin_a)
    new_y = y
    new_z = (x * sin_a) + (z * cos_a)
    return (new_x, new_y, new_z)


def rotate_z(point_3d, angle_degrees):
    """ROLL one point around the z axis (+x swings toward +y)."""
    x, y, z = point_3d
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    new_x = (x * cos_a) - (y * sin_a)
    new_y = (x * sin_a) + (y * cos_a)
    new_z = z
    return (new_x, new_y, new_z)


def rotate_all(point_3d):
    """Spin the cube: tip, then turn, then roll (Lesson 2B's order)."""
    p = rotate_x(point_3d, angle_x)
    p = rotate_y(p, angle_y)
    p = rotate_z(p, angle_z)
    return p


def project(point_3d):
    """Turn one 3D point into a 2D SCREEN point (from Lesson 1).

    You are at the WORLD centre facing +z, so a WORLD point works here.
    """
    x, y, z = point_3d
    screen_x = CENTRE_X + ( (x * FOCAL) / z )
    screen_y = CENTRE_Y - ( (y * FOCAL) / z )
    return (screen_x, screen_y)


def average_z(corners, world_points):
    """How far away is this face? (from Lesson 3)"""
    total = 0
    for corner_number in corners:
        x, y, z = world_points[corner_number]
        total = (total + z)
    return (total / len(corners))          # len(corners) is 4


def is_facing_you(face_points):
    """The clock test (from Lesson 3, unchanged): True if clockwise on
    the SCREEN, which means the face is turned toward you."""
    a_x, a_y = face_points[0]
    b_x, b_y = face_points[1]
    c_x, c_y = face_points[2]
    arrow_a_x = (b_x - a_x)
    arrow_a_y = (b_y - a_y)
    arrow_b_x = (c_x - a_x)
    arrow_b_y = (c_y - a_y)
    cross = ( (arrow_a_x * arrow_b_y) - (arrow_a_y * arrow_b_x) )
    return (cross > 0)


def dot(arrow_1, arrow_2):
    """The dot product (from Lesson 3B)."""
    x1, y1, z1 = arrow_1
    x2, y2, z2 = arrow_2
    return ( (x1 * x2) + (y1 * y2) + (z1 * z2) )


def shade_colour(colour, turned_normal):
    """Brighter when the face points at the light (from Lesson 3B)."""
    brightness = dot(turned_normal, LIGHT)
    if brightness < 0:
        brightness = 0
    shade = ( AMBIENT + ( (1 - AMBIENT) * brightness ) )
    red, green, blue = colour
    return ( round(red * shade), round(green * shade), round(blue * shade) )


def keep_under_360(angle):
    """360 degrees is the same as 0, so start again after a full turn."""
    if angle >= 360:
        angle = (angle - 360)
    return angle


def to_map(x, z):
    """NEW: a WORLD (x, z) -> a pixel on the mini-map.

    Like project(), but with no dividing, because the map is flat.
    +z goes UP the map, and screen y counts DOWN, so we SUBTRACT z.
    Example: you at (2, 0, 1) -> (710 + (2 * 10), 560 - (1 * 10))
                               = (730, 550)
    """
    map_x = MAP_CX + (x * MAP_SCALE)
    map_y = MAP_CY - (z * MAP_SCALE)
    return (map_x, map_y)


def draw_map_axes(box):
    """NEW: the WORLD axes on the mini-map, through WORLD (0, 0, 0).

    Looking DOWN on the world:
      x runs left -> right   (+x to the right)
      z runs bottom -> top   (+z up the map, the way you face at the start)
      y points straight UP out of the map, at you, so it is just a
        dot in a ring at (0, 0, 0): an arrow seen tip-on.
    """
    origin_x, origin_y = to_map(0, 0)        # = (MAP_CX, MAP_CY)
    right = box.right - 4                    # just inside the box
    top = box.top + 4

    # x axis, with an arrowhead at the +x end
    pygame.draw.line(screen, X_AXIS, (box.left + 4, origin_y), (right, origin_y), 1)
    pygame.draw.polygon(screen, X_AXIS, [(right, origin_y), (right - 7, origin_y - 4), (right - 7, origin_y + 4)])
    screen.blit(map_font.render("+x", True, X_AXIS), (right - 16, origin_y - 16))

    # z axis, with an arrowhead at the +z end
    pygame.draw.line(screen, Z_AXIS, (origin_x, box.bottom - 4), (origin_x, top), 1)
    pygame.draw.polygon(screen, Z_AXIS, [(origin_x, top), (origin_x - 4, top + 7), (origin_x + 4, top + 7)])
    screen.blit(map_font.render("+z", True, Z_AXIS), (origin_x + 6, top))

    # y axis: pointing up out of the map, at you
    pygame.draw.circle(screen, Y_AXIS, (origin_x, origin_y), 7, 1)
    pygame.draw.circle(screen, Y_AXIS, (origin_x, origin_y), 2)
    screen.blit(map_font.render("+y up", True, Y_AXIS), (origin_x - 42, origin_y - 16))

    # Numbers on the sides: x along the bottom edge, z up the left edge,
    # every MAP_TICK world units. A small tick mark sits on the edge.
    for x in range(-20, 21, MAP_TICK):
        map_x, map_y = to_map(x, 0)
        if (box.left + 10) < map_x < (box.right - 10):
            pygame.draw.line(screen, X_AXIS, (map_x, box.bottom - 1), (map_x, box.bottom - 5), 1)
            label = map_font.render(str(x), True, X_AXIS)
            screen.blit(label, label.get_rect(center=(map_x, box.bottom - 12)))
    for z in range(-20, 21, MAP_TICK):
        map_x, map_y = to_map(0, z)
        if (box.top + 10) < map_y < (box.bottom - 18):
            pygame.draw.line(screen, Z_AXIS, (box.left + 1, map_y), (box.left + 5, map_y), 1)
            label = map_font.render(str(z), True, Z_AXIS)
            screen.blit(label, label.get_rect(midleft=(box.left + 7, map_y)))


def draw_map(world_points):
    """NEW: draw the mini-map: the cube's outline and you, from above."""
    box = pygame.Rect(MAP_LEFT, MAP_TOP, MAP_SIZE, MAP_SIZE)
    pygame.draw.rect(screen, MAP_BACK, box)
    # set_clip: anything we draw outside the box is cut off, so a dot
    # off the edge of the map just disappears.
    screen.set_clip(box)
    draw_map_axes(box)
    # The cube from above = its 4 BOTTOM corners (0, 1, 2, 3), x and z only.
    outline = []
    for corner_number in (0, 1, 2, 3):
        x, y, z = world_points[corner_number]
        outline.append(to_map(x, z))
    pygame.draw.polygon(screen, GREEN, outline, 2)
    # You: a pink dot, with a short line showing the way you face (+z).
    you = to_map(cam_x, cam_z)
    nose = to_map(cam_x, (cam_z + 1.5))      # 1.5 units in front of you
    pygame.draw.line(screen, PINK, you, nose, 2)
    pygame.draw.circle(screen, PINK, you, 4)
    screen.set_clip(None)                    # stop cutting things off
    pygame.draw.rect(screen, WHITE, box, 1)  # thin white border


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:     # full screen has no close button
                running = False
            if event.key == pygame.K_SPACE:
                spinning = not spinning
            if event.key == pygame.K_l:
                use_light = not use_light
            if event.key == pygame.K_c:
                one_colour = not one_colour
            if event.key == pygame.K_r:          # back to the start
                angle_x = 0
                angle_y = 0
                angle_z = 0

    if spinning:
        angle_x = keep_under_360( (angle_x + SPEED_X) )
        angle_y = keep_under_360( (angle_y + SPEED_Y) )
        angle_z = keep_under_360( (angle_z + SPEED_Z) )

    screen.fill(BLACK)

    # ---- spin -> place, for all 8 corners --------------------------------
    # TWO lists:
    #   world_points  - WORLD         (for the painter's sort and the map)
    #   screen_points - SCREEN        (for the clock test and drawing)
    world_points = []
    screen_points = []
    for p in cube_points:
        turned = rotate_all(p)                         # SHAPE, spun
        x, y, z = turned
        world = ( (x + cube_x), (y + cube_y), (z + cube_z) )   # WORLD
        world_points.append(world)
        screen_points.append(project(world))           # SCREEN

    # ---- Make a list of the faces we will paint ------------------------
    faces_to_draw = []
    for corners, colour, normal in cube_faces:
        face_points = []
        for corner_number in corners:
            face_points.append(screen_points[corner_number])

        # 1. The clock test (Lesson 3).
        if not is_facing_you(face_points):
            continue

        # 2. How far away is it? (Lesson 3)
        distance = average_z(corners, world_points)

        # 3. What colour, after the light? (Lesson 3B)
        if one_colour:
            colour = CUBE_GREEN
        if use_light:
            # Turn the stored normal with the SAME spin as the corners.
            # No cube_position and no camera: a normal is a direction,
            # and the lamp belongs to the world.
            turned_normal = rotate_all(normal)
            colour = shade_colour(colour, turned_normal)

        faces_to_draw.append( (distance, face_points, colour) )

    # ---- The painter's method: furthest first (Lesson 3) ---------------
    faces_to_draw.sort(reverse=True)
    for distance, face_points, colour in faces_to_draw:
        pygame.draw.polygon(screen, colour, face_points)
        pygame.draw.polygon(screen, BLACK, face_points, 2)

    draw_map(world_points)

    text = ("you are at (" + str(round(cam_x, 2)) + ", " +
            str(round(cam_y, 2)) + ", " + str(round(cam_z, 2)) + ")")
    screen.blit(font.render(text, True, PINK), (20, 20))
    screen.blit(font.render("SPACE = spin,  R = reset,  L = light,  C = colours,  ESC = quit", True, YELLOW), (20, 50))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

# ----------------------------------------------------------------------
# TRY THIS:
#   * Press SPACE. The cube spins on the screen AND its outline turns
#     on the map: they are the same WORLD points.
#   * Set cube_position = (3, 0, 8). Where is the cube on the map now?
#     Where is it on the screen? Do the two agree?
#   * Set cam_x = 2. Your dot moves on the map, but the picture does
#     NOT change. Why not? (Nothing in the 3D recipe uses cam_x yet.
#     Part 2 of the lesson fixes that, and step 1 lets you walk.)
# ----------------------------------------------------------------------
