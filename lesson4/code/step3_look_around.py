# ======================================================================
# LESSON 4 - STEP 3: LOOK UP AND DOWN (the finished camera)
# ----------------------------------------------------------------------
# Goal: the UP and DOWN arrows tilt your head, so you can look down onto
# the top of the cube or up at it from underneath. This is the final
# script of Lesson 4: a camera you can walk, turn and look with.
#
# What is new since step 2:
#
#   1. cam_tip  (degrees, starts at 0 = looking level)
#        Positive = nod FORWARD = look DOWN, the same way rotate_x tips
#        things (+y swings toward +z). UP arrow takes away, DOWN adds.
#
#   2. to_camera() gets a THIRD line, the same trick again:
#
#           rotate_x(point, (-cam_tip))
#
#      Your head tips AFTER your body has turned, so we undo the tip
#      AFTER we undo the turn: subtract -> undo turn -> undo tip.
#
#   3. cam_tip is kept between -60 and 60. At 90 you would stare
#      straight up or down and LEFT / RIGHT would start to feel like
#      rolling, so we stop well short of that.
#
#   4. Walking ignores cam_tip on purpose: looking down at the floor
#      does not make W walk you into it. (Most games work like this.)
#
# The recipe for one corner, every frame:
#
#   SHAPE -> spin -> + cube_position -> - camera -> undo turn -> undo tip -> NEAR -> project
#   (cube_points)    (WORLD)                                    (CAMERA)            (SCREEN)
#
# Controls:  LEFT / RIGHT = turn,   UP / DOWN = look up / down
#            W / S = walk forward / back,   A / D = step left / right
#            Q / E = go down / up
#            SPACE = spin the cube on / off,   R = reset
#            L = light on / off,   C = six colours / one colour
# Run:  python step3_look_around.py
# ======================================================================

import math
import pygame

pygame.init()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 4, step 3 - look around")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
PINK = (255, 105, 200)        # (step 1) the colour we use for YOU (the camera)
MAP_BACK = (25, 30, 36)       # (step 1) dark grey-blue behind the mini-map

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
FOCAL = 400

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
# Each face lists its 4 corners CLOCKWISE as seen from OUTSIDE the cube.
cube_faces = [
    ((4, 5, 1, 0), RED),       # front  (all have z = -1)
    ((6, 7, 3, 2), PURPLE),    # back   (all have z = +1)
    ((7, 4, 0, 3), BLUE),      # left   (all have x = -1)
    ((5, 6, 2, 1), GREEN),     # right  (all have x = +1)
    ((7, 6, 5, 4), GOLD),      # top    (all have y = +1)
    ((2, 3, 0, 1), ORANGE),    # bottom (all have y = -1)
]

# ---- (step 1) where the cube lives in the WORLD ----------------------------
# Before, we added cube_distance to z and that was the whole story,
# because you never moved. Now the cube gets a proper address on the
# map, and YOU get one too (below).
# (0, 0, 5): straight ahead of the starting spot, 5 away - the same 5
# as Lessons 1 to 3, so the first frame looks exactly like before.
cube_position = (0, 0, 5)
cube_x, cube_y, cube_z = cube_position      # unpack the 3 numbers

# ---- (step 1) where YOU are standing (the camera), in WORLD coordinates ---
# Start at (0, 0, 0): the seat you sat in for Lessons 1 to 3.
cam_x = 0
cam_y = 0
cam_z = 0

# (step 2) which way you are facing, in degrees. 0 = facing +z, straight
# at the cube, like Lessons 1 to 3. Positive = turned LEFT.
cam_turn = 0

# NEW: how far you are looking up or down, in degrees. 0 = level.
# Positive = nod forward = look DOWN (the same way rotate_x tips).
cam_tip = 0

# NEW: the furthest you can look up or down. 60 lets you look down onto
# the cube's top from close by, and stays safely short of 90 (straight
# up / down), where turning left and right starts to feel like rolling.
TIP_LIMIT = 60

# How far you move in ONE frame (60 frames a second).
#   (0.05 * 60) = 3 units a second.
# From the start the cube's front face is 4 away, so you reach it in
# (4 / 3) = 1.3 seconds: quick, but easy to stop in time.
MOVE_SPEED = 0.05

# (step 2) how many degrees you turn in ONE frame.
#   (1.5 * 60) = 90 degrees a second: a quarter turn takes 1 second
#   and a full look round takes (360 / 90) = 4 seconds.
TURN_SPEED = 1.5

# (step 1) anything closer than this (in CAMERA z) is not drawn.
# At z = 0.1 a point just 1 unit to the side lands
# ((1 * 400) / 0.1) = 4000 px from the centre: ten half-windows away.
# Nothing closer than that could ever be useful to draw.
NEAR = 0.1

# ---- The light (from Lesson 3B, unchanged) ----------------------------
# The lamp belongs to the WORLD (like the sun), so it does NOT move when
# you walk. The top of the cube stays the brightest face from anywhere.
LIGHT = (0.48, 0.6, -0.64)
AMBIENT = 0.2

# ---- The cube's own spin (from Lessons 2 and 2B) ----------------------
# (step 1) the cube starts STILL, with all angles at 0, so corner 5 is at
# WORLD (1, 1, 4) like in the lesson's worked examples. SPACE spins it.
angle_x = 0
angle_y = 0
angle_z = 0
SPEED_X = 0.5
SPEED_Y = 1
SPEED_Z = 0.25
spinning = False       # (step 1) SPACE flips this
use_light = True
one_colour = False     # Step 1 default: six colours, so when you walk
                       # round you can always tell WHICH side you see

# ---- (step 1) the mini-map ------------------------------------------------
# A 160 x 160 px box, 10 px in from the bottom-right corner:
#   left = (800 - 10 - 160) = 630,   top = (600 - 10 - 160) = 430
MAP_LEFT = 630
MAP_TOP = 430
MAP_SIZE = 160
# World (0, 0, 0) goes at (MAP_CX, MAP_CY):
#   across: the middle of the box,  (630 + 80) = 710
#   down:   30 px above the bottom, (430 + 130) = 560
# Why so low? The cube is at z = 5, which lands (5 * 10) = 50 px higher,
# at y = 510: the exact middle of the box. You start at the bottom
# looking up the map at it, just like the lesson's diagrams.
MAP_CX = (MAP_LEFT + (MAP_SIZE / 2))    # (630 + 80) = 710
MAP_CY = (MAP_TOP + 130)                # (430 + 130) = 560
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


def to_camera(world_point):
    """Turn one WORLD point into a CAMERA point (measured from YOU).

    1. Subtract where you are standing (step 1).
    2. Undo your turn: turn the world the OPPOSITE way (step 2).
    3. NEW: undo your tip: tip the world the OPPOSITE way.

    Worked example (lesson Part 6): you at (2, 0, 1), cam_turn = 30,
    cam_tip = 0, corner 5 at WORLD (1, 1, 4):
        1. ((1 - 2), (1 - 0), (4 - 1))   = (-1, 1, 3)
        2. rotate_y((-1, 1, 3), (-30))   = (0.634, 1, 3.098)
        3. rotate_x(that, (-0))          = no change
    """
    x, y, z = world_point
    # 1. Subtract: now YOU are the centre (0, 0, 0).
    moved = ( (x - cam_x), (y - cam_y), (z - cam_z) )
    # 2. Undo your turn. Because step 1 already made YOU the centre,
    #    the world swings round where you stand (not round the map's
    #    centre). Swap these two lines and corners jump behind you!
    turned = rotate_y(moved, (-cam_turn))
    # 3. NEW: undo your tip. The head nods AFTER the body turns, so it
    #    is undone after the turn is undone (last on, first off).
    tipped = rotate_x(turned, (-cam_tip))
    return tipped


def project(point_3d):
    """Turn one 3D CAMERA point into a 2D SCREEN point (from Lesson 1).

    Only ever call this with z >= NEAR, so we never divide by 0.
    """
    x, y, z = point_3d
    screen_x = CENTRE_X + ( (x * FOCAL) / z )
    screen_y = CENTRE_Y - ( (y * FOCAL) / z )
    return (screen_x, screen_y)


def average_z(corners, camera_points):
    """How far away is this face? (from Lesson 3)

    CHANGED in step 1: we pass in CAMERA points, so z means "distance in
    front of YOU", wherever you are standing. (WORLD z would give the
    wrong answer as soon as you walk round behind the cube.)
    """
    total = 0
    for corner_number in corners:
        x, y, z = camera_points[corner_number]
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


def face_pointer(corners, turned_points):
    """The arrow straight out of a face (from Lesson 3B, unchanged).
    Uses turned SHAPE points, so the light stays fixed in the world."""
    total_x = 0
    total_y = 0
    total_z = 0
    for corner_number in corners:
        x, y, z = turned_points[corner_number]
        total_x = (total_x + x)
        total_y = (total_y + y)
        total_z = (total_z + z)
    count = len(corners)
    return ( (total_x / count), (total_y / count), (total_z / count) )


def dot(arrow_1, arrow_2):
    """The dot product (from Lesson 3B)."""
    x1, y1, z1 = arrow_1
    x2, y2, z2 = arrow_2
    return ( (x1 * x2) + (y1 * y2) + (z1 * z2) )


def shade_colour(colour, pointer):
    """Brighter when the face points at the light (from Lesson 3B)."""
    brightness = dot(pointer, LIGHT)
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
    """(step 1) a WORLD (x, z) -> a pixel on the mini-map.

    Like project(), but with no dividing, because the map is flat.
    +z goes UP the map, and screen y counts DOWN, so we SUBTRACT z.
    Example: you at (2, 0, 1) -> (710 + (2 * 10), 560 - (1 * 10))
                               = (730, 550)
    """
    map_x = MAP_CX + (x * MAP_SCALE)
    map_y = MAP_CY - (z * MAP_SCALE)
    return (map_x, map_y)


def draw_map(world_points):
    """(step 1) draw the mini-map: the cube's outline and you, from above."""
    box = pygame.Rect(MAP_LEFT, MAP_TOP, MAP_SIZE, MAP_SIZE)
    pygame.draw.rect(screen, MAP_BACK, box)
    # set_clip: anything we draw outside the box is cut off, so if you
    # walk off the edge of the map your dot just disappears.
    screen.set_clip(box)
    # The cube from above = its 4 BOTTOM corners (0, 1, 2, 3), x and z only.
    outline = []
    for corner_number in (0, 1, 2, 3):
        x, y, z = world_points[corner_number]
        outline.append(to_map(x, z))
    pygame.draw.polygon(screen, GREEN, outline, 2)
    # You: a pink dot, with a short line showing the way you face.
    # (step 2) the line follows your forward arrow.
    forward_x, forward_y, forward_z = rotate_y((0, 0, 1), cam_turn)
    you = to_map(cam_x, cam_z)
    nose = to_map( (cam_x + (forward_x * 1.5)), (cam_z + (forward_z * 1.5)) )
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
                angle_x = 0
                angle_y = 0
                angle_z = 0

    # ---- Keys you HOLD use get_pressed() (True on every held frame) ---
    keys = pygame.key.get_pressed()

    # ---- (step 2) turning --------------------------------------------------
    if keys[pygame.K_LEFT]:
        cam_turn = (cam_turn + TURN_SPEED)    # left  = positive
    if keys[pygame.K_RIGHT]:
        cam_turn = (cam_turn - TURN_SPEED)    # right = negative

    # ---- NEW: looking up and down --------------------------------------
    if keys[pygame.K_UP]:
        cam_tip = (cam_tip - TURN_SPEED)      # look up   = negative
    if keys[pygame.K_DOWN]:
        cam_tip = (cam_tip + TURN_SPEED)      # look down = positive
    # Keep it between -TIP_LIMIT and +TIP_LIMIT (-60 and 60).
    if cam_tip > TIP_LIMIT:
        cam_tip = TIP_LIMIT
    if cam_tip < (-TIP_LIMIT):
        cam_tip = (-TIP_LIMIT)

    # ---- (step 2) which way is "forward" and "right" right now? ------------
    # Turn the two start arrows by the SAME angle you turned.
    #   cam_turn 0:  forward (0, 0, 1)        right (1, 0, 0)
    #   cam_turn 30: forward (-0.5, 0, 0.866) right (0.866, 0, 0.5)
    # Both arrows are exactly 1 long, so MOVE_SPEED alone decides how
    # far one step goes, whichever way you face.
    # (cam_tip is NOT used here, so you always walk level.)
    forward_x, forward_y, forward_z = rotate_y((0, 0, 1), cam_turn)
    right_x, right_y, right_z = rotate_y((1, 0, 0), cam_turn)

    # ---- (step 2) walking follows the arrows ---------------------------
    if keys[pygame.K_w]:                       # forward
        cam_x = (cam_x + (forward_x * MOVE_SPEED))
        cam_z = (cam_z + (forward_z * MOVE_SPEED))
    if keys[pygame.K_s]:                       # back = minus forward
        cam_x = (cam_x - (forward_x * MOVE_SPEED))
        cam_z = (cam_z - (forward_z * MOVE_SPEED))
    if keys[pygame.K_d]:                       # step right
        cam_x = (cam_x + (right_x * MOVE_SPEED))
        cam_z = (cam_z + (right_z * MOVE_SPEED))
    if keys[pygame.K_a]:                       # step left = minus right
        cam_x = (cam_x - (right_x * MOVE_SPEED))
        cam_z = (cam_z - (right_z * MOVE_SPEED))
    # Up and down stay the same: straight along y.
    if keys[pygame.K_e]:
        cam_y = (cam_y + MOVE_SPEED)
    if keys[pygame.K_q]:
        cam_y = (cam_y - MOVE_SPEED)

    if spinning:
        angle_x = keep_under_360( (angle_x + SPEED_X) )
        angle_y = keep_under_360( (angle_y + SPEED_Y) )
        angle_z = keep_under_360( (angle_z + SPEED_Z) )

    screen.fill(BLACK)

    # ---- spin -> place -> camera, for all 8 corners --------------------
    # FOUR lists now, one for each kind of coordinates:
    #   turned_points - SHAPE, spun   (for the light)
    #   world_points  - WORLD         (for the mini-map)
    #   camera_points - CAMERA        (for NEAR and the painter's sort)
    #   screen_points - SCREEN        (for the clock test and drawing)
    turned_points = []
    world_points = []
    camera_points = []
    screen_points = []
    for p in cube_points:
        turned = rotate_all(p)                         # SHAPE, spun
        turned_points.append(turned)
        x, y, z = turned
        world = ( (x + cube_x), (y + cube_y), (z + cube_z) )   # WORLD
        world_points.append(world)
        camera = to_camera(world)                      # CAMERA
        camera_points.append(camera)
        # Only project corners that are in front of you. A corner
        # closer than NEAR gets None ("nothing") instead of a pixel.
        if camera[2] >= NEAR:
            screen_points.append(project(camera))      # SCREEN
        else:
            screen_points.append(None)

    # ---- Make a list of the faces we will paint ------------------------
    faces_to_draw = []
    for corners, colour in cube_faces:
        # (step 1) 0. skip the face if ANY corner is too close or behind you.
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

        # 2. How far away is it? CHANGED in step 1: CAMERA z, distance from YOU.
        distance = average_z(corners, camera_points)

        # 3. What colour, after the light? (Lesson 3B)
        if one_colour:
            colour = CUBE_GREEN
        if use_light:
            pointer = face_pointer(corners, turned_points)
            colour = shade_colour(colour, pointer)

        faces_to_draw.append( (distance, face_points, colour) )

    # ---- The painter's method: furthest first (Lesson 3) ---------------
    faces_to_draw.sort(reverse=True)
    for distance, face_points, colour in faces_to_draw:
        pygame.draw.polygon(screen, colour, face_points)
        pygame.draw.polygon(screen, BLACK, face_points, 2)

    draw_map(world_points)

    text = ("you are at (" + str(round(cam_x, 2)) + ", " +
            str(round(cam_y, 2)) + ", " + str(round(cam_z, 2)) + ")")
    text = (text + "   turn " + str(round(cam_turn, 1)) +
            "   tip " + str(round(cam_tip, 1)))
    screen.blit(font.render(text, True, PINK), (20, 20))
    screen.blit(font.render("ARROWS = turn and look,  W A S D = walk,  Q / E = down / up", True, YELLOW), (20, 50))
    screen.blit(font.render("SPACE = spin,  R = reset,  L = light,  C = colours", True, YELLOW), (20, 80))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

# ----------------------------------------------------------------------
# TRY THIS:
#   * Press E to rise about 3 units, then DOWN to look down onto the top
#     of the cube. Is the top (GOLD) the brightest face? (Lesson 3B.)
#   * Set TIP_LIMIT = 89 and look right up. Now turn with LEFT / RIGHT.
#     How does it feel?
#   * In to_camera(), swap steps 2 and 3 (tip before turn). Look down a
#     little, then turn. What happens to the cube?
#   * Make W follow cam_tip too, so you fly where you look. Hint: make
#     forward with rotate_x((0, 0, 1), cam_tip) first, then rotate_y it.
# ----------------------------------------------------------------------
