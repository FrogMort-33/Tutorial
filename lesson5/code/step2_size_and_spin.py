# ======================================================================
# LESSON 5 - STEP 2: EVERY THING GETS ITS OWN SIZE AND SPIN
# ----------------------------------------------------------------------
# Goal: five shapes, each with its OWN size and its OWN spin speed:
# a big cube, a small cube, a floating cube that tumbles, and more.
#
# What is new since step 1:
#
#   1. Three more keys in every thing's dictionary:
#        "size"   - 1 = normal, 2 = twice as big, 0.5 = half
#        "angles" - its spin right now, [tip, turn, roll] in degrees
#        "speeds" - degrees it spins each frame, (tip, turn, roll)
#
#   2. to_world() grows from ONE step to THREE:
#        size (multiply)  ->  spin (rotate_all)  ->  place (add position)
#      Size and spin happen round the thing's OWN centre, so they must
#      come BEFORE we add the position. (The lesson shows what goes
#      wrong if you place first.)
#
#   3. rotate_all() now takes the angles as a parameter, because each
#      thing has its own.
#
#   4. The light: each face's pointer is spun by the same angles, but
#      NOT sized, so it stays exactly 1 long.
#
#   5. keep_under_360() also handles NEGATIVE angles (for things that
#      spin the other way).
#
# The recipe for one corner of one thing, every frame:
#
#   SHAPE -> * size -> spin -> + position -> - camera -> undo turn -> undo tip -> NEAR -> project
#   (model points)            (WORLD)                                 (CAMERA)           (SCREEN)
#
# Controls:  LEFT / RIGHT = turn,   UP / DOWN = look up / down
#            W / S = walk forward / back,   A / D = step left / right
#            Q / E = go down / up
#            SPACE = pause the spinning,   R = reset
#            L = light on / off,   C = one colour per thing / face colours
# Run:  python step2_size_and_spin.py
# ======================================================================

import math
import pygame

pygame.init()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 5, step 2 - size and spin")
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
CORAL = (250, 120, 100)
LILAC = (190, 140, 255)
TEAL = (60, 210, 200)
ROSE = (255, 110, 170)

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
# (step 1) each face is now THREE things:
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

# ---- (step 1) the pyramid's 5 corners ------------------------------------
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

# ---- (step 1) the pyramid's 5 faces --------------------------------------
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

# ---- (step 1) a MODEL = a shape's points and faces, kept together --------
cube_model = {"points": cube_points, "faces": cube_faces}
pyramid_model = {"points": pyramid_points, "faces": pyramid_faces}


# ======================================================================
# THE WORLD
# ======================================================================

# ---- (step 1) THINGS: every shape in the world, in one list --------------
# Each thing is a dictionary (from the Python lists course):
#   "model"    - which shape (cube_model or pyramid_model)
#   "position" - where its centre is, in WORLD coordinates
#   "size"     - NEW: 1 = normal, 2 = twice as big, 0.5 = half
#   "angles"   - NEW: its spin right now: [tip, turn, roll] in degrees
#   "speeds"   - NEW: how many degrees it spins each frame (tip, turn, roll)
#   "colour"   - its one colour when you press C
#
# There is no floor yet (step 3), but we already place every thing as
# if it stands on one at y = -1, the bottom of the old cube. A thing of
# size s has its bottom s below its centre, so its centre y = (-1 + s):
#   size 1   -> y = (-1 + 1)   = 0
#   size 2   -> y = (-1 + 2)   = 1
#   size 0.5 -> y = (-1 + 0.5) = -0.5
#
# The list order does NOT matter: all faces are sorted together later.
things = [
    # The old cube, in its old place, standing still: corner 5 is at
    # WORLD (1, 1, 4) like in every lesson so far.
    {"model": cube_model, "position": (0, 0, 5), "size": 1,
     "angles": [0, 0, 0], "speeds": (0, 0, 0), "colour": CUBE_GREEN},

    # (step 1) a pyramid behind it and to the left. Its tip is at WORLD
    # (-2.5, 1, 8), which lands on the screen at exactly (275, 250).
    {"model": pyramid_model, "position": (-2.5, 0, 8), "size": 1,
     "angles": [0, 0, 0], "speeds": (0, 1, 0), "colour": SUN_GOLD},

    # NEW: a BIG cube, size 2, standing at y = -1 (centre y = 1). Turns
    # slowly: 0.5 a frame = 30 a second = one turn in 12 seconds.
    {"model": cube_model, "position": (4, 1, 9), "size": 2,
     "angles": [0, 0, 0], "speeds": (0, 0.5, 0), "colour": SKY_BLUE},

    # NEW: a SMALL cube, size 0.5, standing at y = -1 (centre -0.5), just to
    # the right of the old cube. Turns fast: 3 a frame = one turn in 2 s.
    {"model": cube_model, "position": (2, -0.5, 4), "size": 0.5,
     "angles": [0, 0, 0], "speeds": (0, 3, 0), "colour": CORAL},

    # NEW: a cube floating up high, tumbling with Lesson 2B's speeds.
    # It stands on nothing, so it can tip and roll freely.
    {"model": cube_model, "position": (-1.5, 2.5, 9), "size": 0.5,
     "angles": [0, 0, 0], "speeds": (0.5, 1, 0.25), "colour": LILAC},
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

spinning = True        # NEW: SPACE pauses every thing's spin
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


def rotate_all(point_3d, angles):
    """Spin one point: tip, then turn, then roll (Lesson 2B's order).

    CHANGED: the angles come IN as a list [tip, turn, roll],
    because every thing now has its OWN angles. Before, there was only
    one cube, so the angles could live in global variables.
    """
    p = rotate_x(point_3d, angles[0])
    p = rotate_y(p, angles[1])
    p = rotate_z(p, angles[2])
    return p


def to_world(shape_point, thing):
    """NEW: one SHAPE point of a thing -> a WORLD point.

    1. size:  multiply by the thing's size (grow or shrink round its
              own centre).
    2. spin:  turn it by the thing's own angles.
    3. place: add the thing's position.

    Worked example (lesson Part 5): the small cube, size 0.5, still,
    at (2, -0.5, 4). Its corner 5 is SHAPE (1, 1, -1):
        1. ((1 * 0.5), (1 * 0.5), (-1 * 0.5)) = (0.5, 0.5, -0.5)
        2. angles 0                           = no change
        3. ((0.5 + 2), (0.5 + -0.5), (-0.5 + 4)) = (2.5, 0, 3.5)
    """
    x, y, z = shape_point
    size = thing["size"]
    sized = ( (x * size), (y * size), (z * size) )         # 1. size
    spun = rotate_all(sized, thing["angles"])               # 2. spin
    pos_x, pos_y, pos_z = thing["position"]
    sx, sy, sz = spun
    return ( (sx + pos_x), (sy + pos_y), (sz + pos_z) )     # 3. place


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


def keep_under_360(angle):
    """Keep an angle between 0 and 360.
    CHANGED: a NEGATIVE speed (the big pyramid) counts DOWN,
    so we also add 360 when it drops below 0."""
    if angle >= 360:
        angle = (angle - 360)
    if angle < 0:
        angle = (angle + 360)
    return angle


def add_faces_of(thing, faces_to_draw):
    """(step 1) work out every face of ONE thing and add the ones we
    should paint to the shared list faces_to_draw.

    This is Lesson 4's face loop, moved into a function so we can run
    it once for EACH thing. Every thing adds to the SAME list, so the
    painter's sort later sees all faces of all things together.
    """
    model = thing["model"]

    # ---- spin -> place -> camera, for every corner of this thing ----
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
            # NEW: the pointer must spin WITH the thing, so we turn
            # it by the same angles. We do NOT multiply it by the size:
            # a bigger face still points the same way, and the arrow
            # must stay exactly 1 long for the light maths.
            spun_pointer = rotate_all(pointer, thing["angles"])
            colour = shade_colour(colour, spun_pointer)

        faces_to_draw.append( (distance, face_points, colour) )


def to_map(x, z):
    """A WORLD (x, z) -> a pixel on the mini-map (from Lesson 4)."""
    map_x = MAP_CX + (x * MAP_SCALE)
    map_y = MAP_CY - (z * MAP_SCALE)
    return (map_x, map_y)


def draw_map():
    """Draw the mini-map: every thing's base and you, from above.

    (step 1) a loop over ALL things. Corners 0, 1, 2, 3 are the bottom
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
            if event.key == pygame.K_SPACE:
                spinning = not spinning
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
                for thing in things:
                    thing["angles"] = [0, 0, 0]

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

    # ---- NEW: every thing spins at its OWN speeds --------------------
    if spinning:
        for thing in things:
            angles = thing["angles"]
            speeds = thing["speeds"]
            angles[0] = keep_under_360( (angles[0] + speeds[0]) )   # tip
            angles[1] = keep_under_360( (angles[1] + speeds[1]) )   # turn
            angles[2] = keep_under_360( (angles[2] + speeds[2]) )   # roll

    screen.fill(BLACK)

    # ---- (step 1) ONE list for the faces of EVERY thing --------------------
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
    screen.blit(font.render("SPACE = pause,  R = reset,  L = light,  C = colours", True, YELLOW), (20, 80))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

# ----------------------------------------------------------------------
# TRY THIS:
#   * Make the big cube size 3. Where must its centre y go so it still
#     stands at y = -1?  (-1 + 3) = 2.
#   * Give the old cube "speeds": (0, 1, 0) so it turns like Lesson 2.
#   * In to_world(), add the position FIRST and then size it. Watch the
#     big cube jump away to (8, 2, 18). Why?
#   * Size the pointer too (multiply it by size) and look at the big
#     cube's top. Is it brighter than it should be? (Lesson 3: the
#     arrow must be 1 long.)
# ----------------------------------------------------------------------
