# ======================================================================
# LESSON 5 - STEP 1: TWO KINDS OF SHAPE, MANY THINGS
# ----------------------------------------------------------------------
# Goal: a cube AND a pyramid AND a second cube, all in one world, all
# drawn with Lesson 4's camera, with every face in the right order.
#
# What is new since Lesson 4 (step3_look_around.py):
#
#   1. A second shape, the PYRAMID: 5 corners and 5 faces (four
#      triangles and a square base).
#
#   2. Each face now carries its own POINTER (the arrow straight out
#      of it) as a third item: (corners, colour, pointer). Lesson 3's
#      trick of averaging the corners only works for a cube.
#
#   3. A MODEL keeps a shape's points and faces together in one
#      dictionary: {"points": ..., "faces": ...}.
#
#   4. A THING is one shape placed in the world: a dictionary with a
#      model, a position and a colour. All the things live in one list
#      called things.
#
#   5. Lesson 4's face loop moves into a function, add_faces_of(), that
#      runs once for EACH thing. Every thing adds its faces to ONE
#      shared list, so the painter's sort sorts ALL of them together.
#
# The recipe for one corner of one thing, every frame:
#
#   SHAPE -> + position -> - camera -> undo turn -> undo tip -> NEAR -> project
#   (model points)  (WORLD)                         (CAMERA)            (SCREEN)
#
# Controls:  LEFT / RIGHT = turn,   UP / DOWN = look up / down
#            W / S = walk forward / back,   A / D = step left / right
#            Q / E = go down / up
#            R = reset,   L = light on / off,   C = one colour per thing
# Run:  python step1_two_shapes.py
# ======================================================================

import math
import pygame

pygame.init()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 5, step 1 - two shapes")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
PINK = (255, 105, 200)        # the colour we use for YOU (the camera)
MAP_BACK = (25, 30, 36)       # dark grey-blue behind the mini-map

# ---- One colour for each face direction (from Lesson 3) ---------------
RED = (235, 80, 80)          # faces pointing to the front (-z)
PURPLE = (160, 100, 230)     # faces pointing to the back  (+z)
BLUE = (70, 150, 255)        # faces pointing left         (-x)
GREEN = (70, 210, 120)       # faces pointing right        (+x)
GOLD = (245, 200, 60)        # faces pointing up           (+y)
ORANGE = (245, 140, 50)      # faces pointing down         (-y)

# ---- One colour for each THING (C key) --------------------------------
CUBE_GREEN = (70, 230, 120)
SKY_BLUE = (90, 170, 255)
SUN_GOLD = (250, 200, 70)
CENTRE_X = (WIDTH / 2)            # (800 / 2) = 400
CENTRE_Y = (HEIGHT / 2)           # (600 / 2) = 300
FOCAL = 400


# ======================================================================
# MODELS: the shape of a thing, in SHAPE coordinates (its own centre)
# ======================================================================

# ---- The cube's 8 corners (same as every lesson) ----------------------
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

# ---- The cube's 6 faces -----------------------------------------------
# NEW: each face is now THREE things:
#   (corners clockwise from outside,  colour,  pointer)
# The pointer is the arrow straight out of the face, 1 unit long.
# For a cube it is easy: the front face points to -z, so (0, 0, -1).
cube_faces = [
    ((4, 5, 1, 0), RED,    ( 0,  0, -1)),   # front
    ((6, 7, 3, 2), PURPLE, ( 0,  0,  1)),   # back
    ((7, 4, 0, 3), BLUE,   (-1,  0,  0)),   # left
    ((5, 6, 2, 1), GREEN,  ( 1,  0,  0)),   # right
    ((7, 6, 5, 4), GOLD,   ( 0,  1,  0)),   # top
    ((2, 3, 0, 1), ORANGE, ( 0, -1,  0)),   # bottom
]

# ---- NEW: the pyramid's 5 corners ------------------------------------
# Corners 0 to 3 are EXACTLY the cube's 4 bottom corners, with the same
# numbers. Corner 4 is the tip, straight above the centre, at the
# height of the cube's top (y = 1). So a pyramid is the same height and
# width as a cube: 2 units each way.
pyramid_points = [
    (-1, -1, -1),   # 0  bottom-left-front
    ( 1, -1, -1),   # 1  bottom-right-front
    ( 1, -1,  1),   # 2  bottom-right-back
    (-1, -1,  1),   # 3  bottom-left-back
    ( 0,  1,  0),   # 4  the tip
]

# ---- NEW: the pyramid's 5 faces --------------------------------------
# Four TRIANGLES (3 corners each) and one square base (4 corners).
# Still clockwise as seen from outside. Each triangle starts at the tip.
# The sloping pointers were worked out in the lesson (Part 2):
#   the slope rises 2 for every 1 across, so the arrow out of it is
#   (2 out, 1 up), shrunk to 1 unit long: divide by 2.236 (the square
#   root of ((2 * 2) + (1 * 1)) = 5)  ->  (0.894 out, 0.447 up).
pyramid_faces = [
    ((4, 1, 0),    RED,    ( 0,     0.447, -0.894)),   # front slope
    ((4, 3, 2),    PURPLE, ( 0,     0.447,  0.894)),   # back slope
    ((4, 0, 3),    BLUE,   (-0.894, 0.447,  0)),       # left slope
    ((4, 2, 1),    GREEN,  ( 0.894, 0.447,  0)),       # right slope
    ((2, 3, 0, 1), ORANGE, ( 0,    -1,      0)),       # base (bottom)
]

# ---- NEW: a MODEL = a shape's points and faces, kept together --------
cube_model = {"points": cube_points, "faces": cube_faces}
pyramid_model = {"points": pyramid_points, "faces": pyramid_faces}


# ======================================================================
# THE WORLD
# ======================================================================

# ---- NEW: THINGS: every shape in the world, in one list ----------------
# Each thing is a dictionary (from the Python lists course):
#   "model"    - which shape (cube_model or pyramid_model)
#   "position" - where its centre is, in WORLD coordinates
#   "colour"   - its one colour when you press C
# (Step 2 adds a size and a spin to each thing.)
#
# The list order does NOT matter: all faces are sorted together later.
things = [
    # The old cube, in its old place: corner 5 is at WORLD (1, 1, 4)
    # like in every lesson so far.
    {"model": cube_model, "position": (0, 0, 5), "colour": CUBE_GREEN},

    # A pyramid behind it and to the left. Its tip is at WORLD
    # (-2.5, 1, 8), which lands on the screen at exactly (275, 250).
    {"model": pyramid_model, "position": (-2.5, 0, 8), "colour": SUN_GOLD},

    # Lesson 4's practice cube: a second cube at (4, 0, 9).
    {"model": cube_model, "position": (4, 0, 9), "colour": SKY_BLUE},
]

# ---- Where YOU are (from Lesson 4, unchanged) ------------------------
cam_x = 0
cam_y = 0
cam_z = 0
cam_turn = 0        # degrees, positive = turned LEFT
cam_tip = 0         # degrees, positive = looking DOWN
TIP_LIMIT = 60
MOVE_SPEED = 0.05   # (0.05 * 60) = 3 units a second
TURN_SPEED = 1.5    # (1.5 * 60) = 90 degrees a second
NEAR = 0.1          # closer than this (CAMERA z) is not drawn

# ---- The light (from Lesson 3, unchanged) -----------------------------
LIGHT = (0.48, 0.6, -0.64)
AMBIENT = 0.2

use_light = True
one_colour = False     # face colours, so you can watch each face turn

# ---- The mini-map (from Lesson 4, unchanged) --------------------------
MAP_LEFT = 630
MAP_TOP = 430
MAP_SIZE = 160
MAP_CX = (MAP_LEFT + (MAP_SIZE / 2))    # (630 + 80) = 710
MAP_CY = (MAP_TOP + 130)                # (430 + 130) = 560
MAP_SCALE = 10                          # 10 px for every 1 world unit


# ======================================================================
# FUNCTIONS
# ======================================================================

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


# (rotate_z and rotate_all are not needed in step 1: the things stand
#  still. Step 2 brings them back, so each thing can spin.)


def to_world(shape_point, thing):
    """NEW: one SHAPE point of a thing -> a WORLD point.

    Just add the thing's position, the same "+ cube_position" as in
    Lesson 4. Now each thing brings its OWN position.

    Worked example (lesson Part 3): the pyramid's tip is SHAPE (0, 1, 0)
    and the pyramid's position is (-2.5, 0, 8):
        ((0 + -2.5), (1 + 0), (0 + 8)) = (-2.5, 1, 8)
    """
    x, y, z = shape_point
    pos_x, pos_y, pos_z = thing["position"]
    return ( (x + pos_x), (y + pos_y), (z + pos_z) )


def to_camera(world_point):
    """One WORLD point -> one CAMERA point (from Lesson 4, unchanged).
    Subtract where you stand, undo your turn, undo your tip."""
    x, y, z = world_point
    moved = ( (x - cam_x), (y - cam_y), (z - cam_z) )
    turned = rotate_y(moved, (-cam_turn))
    tipped = rotate_x(turned, (-cam_tip))
    return tipped


def project(point_3d):
    """One CAMERA point -> one SCREEN point (from Lesson 1).
    Only ever call this with z >= NEAR, so we never divide by 0."""
    x, y, z = point_3d
    screen_x = CENTRE_X + ( (x * FOCAL) / z )
    screen_y = CENTRE_Y - ( (y * FOCAL) / z )
    return (screen_x, screen_y)


def average_z(corners, camera_points):
    """How far away is this face? (from Lesson 3, uses CAMERA points).

    It divides by len(corners), so it works for a triangle (3 corners)
    just as well as for a square (4). Nothing to change!
    """
    total = 0
    for corner_number in corners:
        x, y, z = camera_points[corner_number]
        total = (total + z)
    return (total / len(corners))


def is_facing_you(face_points):
    """The clock test (from Lesson 3, unchanged). It only looks at the
    first 3 corners, so it works for triangles too."""
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
    """The dot product (from Lesson 3)."""
    x1, y1, z1 = arrow_1
    x2, y2, z2 = arrow_2
    return ( (x1 * x2) + (y1 * y2) + (z1 * z2) )


def shade_colour(colour, pointer):
    """Brighter when the face points at the light (from Lesson 3)."""
    brightness = dot(pointer, LIGHT)
    if brightness < 0:
        brightness = 0
    shade = ( AMBIENT + ( (1 - AMBIENT) * brightness ) )
    red, green, blue = colour
    return ( round(red * shade), round(green * shade), round(blue * shade) )


def add_faces_of(thing, faces_to_draw):
    """NEW: work out every face of ONE thing and add the ones we
    should paint to the shared list faces_to_draw.

    This is Lesson 4's face loop, moved into a function so we can run
    it once for EACH thing. Every thing adds to the SAME list, so the
    painter's sort later sees all faces of all things together.
    """
    model = thing["model"]

    # ---- place -> camera, for every corner of this thing ------------
    camera_points = []
    screen_points = []
    for p in model["points"]:
        world = to_world(p, thing)                     # WORLD
        camera = to_camera(world)                      # CAMERA
        camera_points.append(camera)
        if camera[2] >= NEAR:
            screen_points.append(project(camera))      # SCREEN
        else:
            screen_points.append(None)

    for corners, face_colour, pointer in model["faces"]:
        # 0. skip the face if ANY corner is too close or behind you.
        too_close = False
        for corner_number in corners:
            if camera_points[corner_number][2] < NEAR:
                too_close = True
        if too_close:
            continue

        face_points = []
        for corner_number in corners:
            face_points.append(screen_points[corner_number])

        # 1. The clock test (Lesson 3).
        if not is_facing_you(face_points):
            continue

        # 2. How far away is it? (CAMERA z, Lesson 4)
        distance = average_z(corners, camera_points)

        # 3. What colour?
        colour = face_colour
        if one_colour:
            colour = thing["colour"]
        if use_light:
            # NEW: the pointer now comes from the face list, so it
            # works for the pyramid's slopes too (Lesson 3's averaging
            # trick only worked for the cube). The things stand still
            # in step 1, so the pointer needs no turning yet.
            colour = shade_colour(colour, pointer)

        faces_to_draw.append( (distance, face_points, colour) )


def to_map(x, z):
    """A WORLD (x, z) -> a pixel on the mini-map (from Lesson 4)."""
    map_x = MAP_CX + (x * MAP_SCALE)
    map_y = MAP_CY - (z * MAP_SCALE)
    return (map_x, map_y)


def draw_map():
    """Draw the mini-map: every thing's base and you, from above.

    NEW: a loop over ALL things. Corners 0, 1, 2, 3 are the bottom
    corners of BOTH models (that is why the pyramid's base uses the
    cube's numbers), so the same 4 numbers work for every thing.
    """
    box = pygame.Rect(MAP_LEFT, MAP_TOP, MAP_SIZE, MAP_SIZE)
    pygame.draw.rect(screen, MAP_BACK, box)
    screen.set_clip(box)
    for thing in things:
        outline = []
        for corner_number in (0, 1, 2, 3):
            corner = thing["model"]["points"][corner_number]
            x, y, z = to_world(corner, thing)
            outline.append(to_map(x, z))
        pygame.draw.polygon(screen, thing["colour"], outline, 2)
    forward_x, forward_y, forward_z = rotate_y((0, 0, 1), cam_turn)
    you = to_map(cam_x, cam_z)
    nose = to_map( (cam_x + (forward_x * 1.5)), (cam_z + (forward_z * 1.5)) )
    pygame.draw.line(screen, PINK, you, nose, 2)
    pygame.draw.circle(screen, PINK, you, 4)
    screen.set_clip(None)
    pygame.draw.rect(screen, WHITE, box, 1)


# ======================================================================
# THE MAIN LOOP
# ======================================================================
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_l:
                use_light = not use_light
            if event.key == pygame.K_c:
                one_colour = not one_colour
            if event.key == pygame.K_r:          # back to the start
                cam_x = 0
                cam_y = 0
                cam_z = 0
                cam_turn = 0
                cam_tip = 0

    # ---- Keys you HOLD (from Lesson 4, unchanged) ---------------------
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        cam_turn = (cam_turn + TURN_SPEED)
    if keys[pygame.K_RIGHT]:
        cam_turn = (cam_turn - TURN_SPEED)
    if keys[pygame.K_UP]:
        cam_tip = (cam_tip - TURN_SPEED)
    if keys[pygame.K_DOWN]:
        cam_tip = (cam_tip + TURN_SPEED)
    if cam_tip > TIP_LIMIT:
        cam_tip = TIP_LIMIT
    if cam_tip < (-TIP_LIMIT):
        cam_tip = (-TIP_LIMIT)

    forward_x, forward_y, forward_z = rotate_y((0, 0, 1), cam_turn)
    right_x, right_y, right_z = rotate_y((1, 0, 0), cam_turn)
    if keys[pygame.K_w]:
        cam_x = (cam_x + (forward_x * MOVE_SPEED))
        cam_z = (cam_z + (forward_z * MOVE_SPEED))
    if keys[pygame.K_s]:
        cam_x = (cam_x - (forward_x * MOVE_SPEED))
        cam_z = (cam_z - (forward_z * MOVE_SPEED))
    if keys[pygame.K_d]:
        cam_x = (cam_x + (right_x * MOVE_SPEED))
        cam_z = (cam_z + (right_z * MOVE_SPEED))
    if keys[pygame.K_a]:
        cam_x = (cam_x - (right_x * MOVE_SPEED))
        cam_z = (cam_z - (right_z * MOVE_SPEED))
    if keys[pygame.K_e]:
        cam_y = (cam_y + MOVE_SPEED)
    if keys[pygame.K_q]:
        cam_y = (cam_y - MOVE_SPEED)

    screen.fill(BLACK)

    # ---- NEW: ONE list for the faces of EVERY thing --------------------
    faces_to_draw = []
    for thing in things:
        add_faces_of(thing, faces_to_draw)

    # ---- The painter's method: furthest first, ALL faces together ----
    faces_to_draw.sort(reverse=True)
    for distance, face_points, colour in faces_to_draw:
        pygame.draw.polygon(screen, colour, face_points)
        pygame.draw.polygon(screen, BLACK, face_points, 2)

    draw_map()

    text = ("you are at (" + str(round(cam_x, 2)) + ", " +
            str(round(cam_y, 2)) + ", " + str(round(cam_z, 2)) + ")")
    text = (text + "   turn " + str(round(cam_turn, 1)) +
            "   tip " + str(round(cam_tip, 1)))
    screen.blit(font.render(text, True, PINK), (20, 20))
    screen.blit(font.render("ARROWS = turn and look,  W A S D = walk,  Q / E = down / up", True, YELLOW), (20, 50))
    screen.blit(font.render("R = reset,  L = light,  C = colours", True, YELLOW), (20, 80))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

# ----------------------------------------------------------------------
# TRY THIS:
#   * Move the pyramid to (0, 0, 9), straight behind the cube. Can you
#     still see its tip over the top of the cube? Walk up (E) to check.
#   * Add a fourth thing: another pyramid at (3, 0, 6).
#   * In the main loop, give EACH thing its own faces_to_draw list and
#     sort and paint each list separately. Walk to (-3, 0, 2). What
#     goes wrong? (The lesson's Part 4 shows the answer.)
#   * Change the pyramid's front pointer to (0, 0, -1) (as if it were a
#     cube face). Is the front slope brighter or darker than before?
# ----------------------------------------------------------------------
