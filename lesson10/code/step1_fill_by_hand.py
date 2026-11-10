# ======================================================================
# LESSON 10 - STEP 1: FILLING FACES YOURSELF, BLOCK BY BLOCK
# ----------------------------------------------------------------------
# Goal: stop asking pygame.draw.polygon() to fill our faces, and fill
# them ourselves, one small block at a time. Then look at a scene the
# painter's order can NOT draw: a board pushed through a gold cube.
#
# This starts from Lesson 7's finished game (step3_cube_hunt.py). The
# game parts (score, clock, collecting) are taken out for now, so we
# can look closely at two shapes. They come back in step 3.
#
# What is new since Lesson 7:
#
#   1. THE TEST SCENE (lesson Part 1)
#        A flat blue board (a squashed cube model) and a gold cube that
#        share the same centre, WORLD (0, 0, 6). The board cuts through
#        the middle of the cube.
#
#   2. THE SMALL PICTURE (lesson Part 2)
#        BLOCK = 4. We fill a 200 x 150 picture (one pixel per 4 x 4
#        block of the window) and stretch it to 800 x 600 at the end.
#        200 x 150 = 30,000 blocks instead of 480,000 pixels.
#
#   3. side_of_edge() (lesson Part 3)
#        Lesson 3's clock test, for any 3 points. is_facing_you() now
#        uses it too.
#
#   4. fill_triangle() and draw_face() (lesson Part 3)
#        A face is cut into triangles. A block is inside a triangle
#        when side_of_edge() says "inside" for all 3 of its edges.
#
#   Still the painter's order: faces are sorted far to near, as in
#   Lesson 7. Fly round the board and the cube: the board is always
#   drawn ALL in front of the cube or ALL behind it. Step 2 fixes that.
#
# Controls:  LEFT / RIGHT = turn,   UP / DOWN = look up / down
#            W / S = fly forward / back,   A / D = slide left / right
#            Q / E = straight down / up
#            F = our own fill / pygame.draw.polygon (Lesson 7)
#            SPACE = pause the cube's spin
#            G = floor grid on / off,   L = light on / off
# Run:  python step1_fill_by_hand.py
# ======================================================================

import math
import pygame

pygame.init()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lesson 10, step 1 - filling faces yourself")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
PINK = (255, 105, 200)        # the colour we use for YOU (the camera)
MAP_BACK = (25, 30, 36)       # dark grey-blue behind the mini-map
GRID_COLOUR = (40, 90, 70)    # (Lesson 5) dim green for the floor lines
SUN_GOLD = (250, 200, 70)     # (Lesson 7) the gold cube
BOARD_BLUE = (70, 150, 255)   # NEW: the board

# ---- One colour for each face direction (from Lesson 3) ---------------
RED = (235, 80, 80)          # front (-z)
PURPLE = (160, 100, 230)     # back  (+z)
BLUE = (70, 150, 255)        # left  (-x)
GREEN = (70, 210, 120)       # right (+x)
GOLD = (245, 200, 60)        # top   (+y)
ORANGE = (245, 140, 50)      # bottom (-y)

CENTRE_X = (WIDTH / 2)            # (800 / 2) = 400
CENTRE_Y = (HEIGHT / 2)           # (600 / 2) = 300
FOCAL = 400


# ======================================================================
# NEW: THE SMALL PICTURE (lesson Part 2)
# ======================================================================
# BLOCK = 4: we fill the window in 4 x 4 squares of real pixels, called
# BLOCKS. Python checks about 1 block in a microsecond or two, so:
#     full size: (800 * 600) = 480,000 checks   -> far too slow
#     blocks:    (200 * 150) =  30,000 checks   -> 16 times fewer
# We paint the blocks into a SMALL picture, 200 x 150 pixels, and
# stretch it 4 times bigger onto the window at the end of the frame.
BLOCK = 4
BLOCKS_ACROSS = (WIDTH // BLOCK)    # (800 // 4) = 200
BLOCKS_DOWN = (HEIGHT // BLOCK)     # (600 // 4) = 150
small = pygame.Surface((BLOCKS_ACROSS, BLOCKS_DOWN))
# Black blocks are see-through, so the floor lines (drawn on the
# window first) show between the shapes.
small.set_colorkey(BLACK)


# ======================================================================
# MODELS
# ======================================================================
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
# (corners clockwise from outside,  colour,  pointer)
cube_faces = [
    ((4, 5, 1, 0), RED,    ( 0,  0, -1)),   # front
    ((6, 7, 3, 2), PURPLE, ( 0,  0,  1)),   # back
    ((7, 4, 0, 3), BLUE,   (-1,  0,  0)),   # left
    ((5, 6, 2, 1), GREEN,  ( 1,  0,  0)),   # right
    ((7, 6, 5, 4), GOLD,   ( 0,  1,  0)),   # top
    ((2, 3, 0, 1), ORANGE, ( 0, -1,  0)),   # bottom
]
cube_model = {"points": cube_points, "faces": cube_faces}

# NEW: THE BOARD: a flat box 5 wide, 0.2 thick and 5 deep.
# It has the SAME 8 corner numbers as the cube, in the same places, just
# squashed: x and z go to 2.5, y only to 0.1. So it can use cube_faces
# exactly as they are (Lesson 5: a model is just points + faces).
board_points = [
    (-2.5, -0.1, -2.5),   # 0
    ( 2.5, -0.1, -2.5),   # 1
    ( 2.5, -0.1,  2.5),   # 2
    (-2.5, -0.1,  2.5),   # 3
    (-2.5,  0.1, -2.5),   # 4
    ( 2.5,  0.1, -2.5),   # 5
    ( 2.5,  0.1,  2.5),   # 6
    (-2.5,  0.1,  2.5),   # 7
]
board_model = {"points": board_points, "faces": cube_faces}

# NEW: THE TEST SCENE, in WORLD coordinates.
# Both things share the centre (0, 0, 6): 6 in front of where you start.
# The board is tipped -20 degrees (front edge DOWN, back edge UP), so
# from the start you look down onto its top. It cuts right through the
# middle of the gold cube.
things = [
    {"model": board_model, "position": (0, 0, 6), "size": 1,
     "angles": [-20, 0, 0], "speeds": (0, 0, 0), "colour": BOARD_BLUE},
    {"model": cube_model, "position": (0, 0, 6), "size": 1,
     "angles": [0, 30, 0], "speeds": (0, 0.5, 0), "colour": SUN_GOLD},
]

# ---- The floor (from Lesson 5) ----------------------------------------
FLOOR_Y = -2                  # NEW: lower, so the board clears it
GRID_LEFT = -8
GRID_RIGHT = 8
GRID_NEAR = -3
GRID_FAR = 13

# ---- Where YOU are (from Lesson 4) ------------------------------------
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
show_grid = True
spinning = True

# ---- NEW: F switches between our fill and pygame's ---------------------
fill_by_hand = True

# ---- The mini-map (from Lesson 4) -------------------------------------
MAP_LEFT = 630
MAP_TOP = 430
MAP_SIZE = 160
MAP_CX = (MAP_LEFT + (MAP_SIZE / 2))    # (630 + 80) = 710
MAP_CY = (MAP_TOP + (MAP_SIZE / 2))     # (430 + 80) = 510
MAP_SCALE = 10


# ======================================================================
# MATRIX TOOLS (from Lesson 6, unchanged)
# ======================================================================

def matrix_times_point(matrix, point_3d):
    """Put one point through a matrix: each ROW dotted with the point."""
    row_0, row_1, row_2 = matrix
    new_x = dot(row_0, point_3d)
    new_y = dot(row_1, point_3d)
    new_z = dot(row_2, point_3d)
    return (new_x, new_y, new_z)


def tip_matrix(angle_degrees):
    """Lesson 2B's TIP as a grid. x is the skewer."""
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    return (
        (1, 0,     0         ),
        (0, cos_a, (-sin_a)  ),
        (0, sin_a, cos_a     ),
    )


def turn_matrix(angle_degrees):
    """Lesson 2's TURN as a grid. y is the skewer."""
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    return (
        (cos_a, 0, (-sin_a)),
        (0,     1, 0       ),
        (sin_a, 0, cos_a   ),
    )


def roll_matrix(angle_degrees):
    """Lesson 2B's ROLL as a grid. z is the skewer."""
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    return (
        (cos_a, (-sin_a), 0),
        (sin_a, cos_a,    0),
        (0,     0,        1),
    )


def column(matrix, column_number):
    """One COLUMN of a matrix = where that axis arrow lands."""
    row_0, row_1, row_2 = matrix
    return (row_0[column_number], row_1[column_number], row_2[column_number])


def combine(first, second):
    """ONE matrix that does 'first', then 'second' (Lesson 6)."""
    new_col_0 = matrix_times_point(second, column(first, 0))
    new_col_1 = matrix_times_point(second, column(first, 1))
    new_col_2 = matrix_times_point(second, column(first, 2))
    return (
        (new_col_0[0], new_col_1[0], new_col_2[0]),
        (new_col_0[1], new_col_1[1], new_col_2[1]),
        (new_col_0[2], new_col_1[2], new_col_2[2]),
    )


def spin_matrix(angles):
    """A thing's whole spin as ONE matrix: tip, then turn, then roll."""
    tip_then_turn = combine(tip_matrix(angles[0]), turn_matrix(angles[1]))
    return combine(tip_then_turn, roll_matrix(angles[2]))


# ======================================================================
# THE 3D PIPELINE (Lessons 1 to 6, unchanged)
# ======================================================================

def to_world(shape_point, thing):
    """(Lesson 5) SHAPE -> WORLD: size, then spin, then place."""
    x, y, z = shape_point
    size = thing["size"]
    sized = ( (x * size), (y * size), (z * size) )
    spun = matrix_times_point(thing["matrix"], sized)
    pos_x, pos_y, pos_z = thing["position"]
    sx, sy, sz = spun
    return ( (sx + pos_x), (sy + pos_y), (sz + pos_z) )


def to_camera(world_point):
    """(Lessons 4 and 6) WORLD -> CAMERA: subtract you, then camera_matrix."""
    x, y, z = world_point
    moved = ( (x - cam_x), (y - cam_y), (z - cam_z) )
    return matrix_times_point(camera_matrix, moved)


def project(point_3d):
    """(Lesson 1) CAMERA -> SCREEN. Only call it with z >= NEAR."""
    x, y, z = point_3d
    screen_x = CENTRE_X + ( (x * FOCAL) / z )
    screen_y = CENTRE_Y - ( (y * FOCAL) / z )
    return (screen_x, screen_y)


def average_z(corners, camera_points):
    """(Lesson 3) how far away is this face? Uses CAMERA z."""
    total = 0
    for corner_number in corners:
        x, y, z = camera_points[corner_number]
        total = (total + z)
    return (total / len(corners))


def side_of_edge(start, end, point):
    """NEW (lesson Part 3): Lesson 3's clock test, for ANY 3 points.

    Walk along the edge from 'start' to 'end'. Is 'point' on your
    right-hand side (the inside of a clockwise face)?
        bigger than 0  -> yes, inside this edge
        exactly 0      -> right on the edge
        less than 0    -> no, outside

    The number is also TWICE the area of the triangle start, end, point
    (in pixels or blocks squared). Step 2 uses that.

    Worked example (lesson Part 3), in BLOCK coordinates:
        side_of_edge((100, 50), (125, 50), (110.5, 60.5))
        = ( ((125 - 100) * (60.5 - 50)) - ((50 - 50) * (110.5 - 100)) )
        = ( (25 * 10.5) - (0 * 10.5) ) = 262.5      -> inside
    """
    start_x, start_y = start
    end_x, end_y = end
    point_x, point_y = point
    arrow_a_x = (end_x - start_x)
    arrow_a_y = (end_y - start_y)
    arrow_b_x = (point_x - start_x)
    arrow_b_y = (point_y - start_y)
    return ( (arrow_a_x * arrow_b_y) - (arrow_a_y * arrow_b_x) )


def is_facing_you(face_points):
    """(Lesson 3) the clock test: True if clockwise on the screen.
    NEW: now just side_of_edge() on the face's first 3 corners."""
    return (side_of_edge(face_points[0], face_points[1], face_points[2]) > 0)


def dot(arrow_1, arrow_2):
    """(Lesson 3) the dot product."""
    x1, y1, z1 = arrow_1
    x2, y2, z2 = arrow_2
    return ( (x1 * x2) + (y1 * y2) + (z1 * z2) )


def shade_colour(colour, pointer):
    """(Lesson 3) brighter when the face points at the light."""
    brightness = dot(pointer, LIGHT)
    if brightness < 0:
        brightness = 0
    shade = ( AMBIENT + ( (1 - AMBIENT) * brightness ) )
    red, green, blue = colour
    return ( round(red * shade), round(green * shade), round(blue * shade) )


def keep_under_360(angle):
    """Keep an angle between 0 and 360."""
    if angle >= 360:
        angle = (angle - 360)
    if angle < 0:
        angle = (angle + 360)
    return angle


def add_faces_of(thing, faces_to_draw):
    """(Lesson 5) work out every face of ONE thing and add the ones to
    paint to the shared list (unchanged from Lesson 7)."""
    model = thing["model"]
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
        too_close = False
        for corner_number in corners:
            if camera_points[corner_number][2] < NEAR:
                too_close = True
        if too_close:
            continue
        face_points = []
        for corner_number in corners:
            face_points.append(screen_points[corner_number])
        if not is_facing_you(face_points):
            continue
        distance = average_z(corners, camera_points)
        colour = thing["colour"]
        if use_light:
            spun_pointer = matrix_times_point(thing["matrix"], pointer)
            colour = shade_colour(colour, spun_pointer)
        faces_to_draw.append( (distance, face_points, colour) )


# ======================================================================
# NEW: FILLING FACES YOURSELF (lesson Part 3)
# ======================================================================

def fill_triangle(a, b, c, colour):
    """NEW (lesson Part 3): fill one triangle, block by block.

    a, b, c : the corners in BLOCK coordinates (block_x, block_y),
              clockwise on the screen
    colour  : the shaded colour of the face

    1. Only look at blocks inside the triangle's bounding box.
    2. For each block, test its CENTRE (block_x + 0.5, block_y + 0.5)
       against the 3 edges, a->b, b->c and c->a.
    3. Inside all 3?  Paint it.
    """
    # Twice the area of the whole triangle. Corners in a line (a thin
    # sliver) give 0: nothing to fill.
    total = side_of_edge(a, b, c)
    if total <= 0:
        return

    a_x, a_y = a
    b_x, b_y = b
    c_x, c_y = c
    # ---- 1. the bounding box, kept inside the 200 x 150 picture ------
    # int() chops off the decimals: block 37.8 is in block 37.
    left = int(min(a_x, b_x, c_x))
    right = int(max(a_x, b_x, c_x))
    top = int(min(a_y, b_y, c_y))
    bottom = int(max(a_y, b_y, c_y))
    if left < 0:
        left = 0
    if top < 0:
        top = 0
    if right > (BLOCKS_ACROSS - 1):
        right = (BLOCKS_ACROSS - 1)
    if bottom > (BLOCKS_DOWN - 1):
        bottom = (BLOCKS_DOWN - 1)

    for block_y in range(top, (bottom + 1)):
        for block_x in range(left, (right + 1)):
            # ---- 2. the inside test, on the block's centre ------------
            # (Step 2 will call these three numbers "weights".)
            centre = ( (block_x + 0.5), (block_y + 0.5) )
            weight_a = side_of_edge(b, c, centre)   # the edge b -> c
            weight_b = side_of_edge(c, a, centre)   # the edge c -> a
            weight_c = side_of_edge(a, b, centre)   # the edge a -> b
            if (weight_a < 0) or (weight_b < 0) or (weight_c < 0):
                continue                            # outside: next block
            # ---- 3. inside all three edges: paint it -----------------
            small.set_at((block_x, block_y), colour)


def draw_face(face_points, colour):
    """NEW (lesson Part 3): fill one face. A 4-corner face is cut into
    2 triangles, both starting at corner 0:
        corners 0, 1, 2   and   corners 0, 2, 3
    Both stay clockwise, like the face.

    The face's corners come in SCREEN pixels. Dividing by BLOCK (4)
    turns them into BLOCK coordinates: SCREEN (500, 200) -> (125, 50).
    """
    blocks = []
    for screen_x, screen_y in face_points:
        blocks.append( ((screen_x / BLOCK), (screen_y / BLOCK)) )
    fill_triangle(blocks[0], blocks[1], blocks[2], colour)
    if len(blocks) == 4:
        fill_triangle(blocks[0], blocks[2], blocks[3], colour)


def draw_floor():
    """(Lesson 5) the floor grid, in 1-unit pieces."""
    for x in range(GRID_LEFT, (GRID_RIGHT + 1)):
        for z in range(GRID_NEAR, GRID_FAR):
            draw_floor_piece( (x, FLOOR_Y, z), (x, FLOOR_Y, (z + 1)) )
    for z in range(GRID_NEAR, (GRID_FAR + 1)):
        for x in range(GRID_LEFT, GRID_RIGHT):
            draw_floor_piece( (x, FLOOR_Y, z), ((x + 1), FLOOR_Y, z) )


def draw_floor_piece(world_start, world_end):
    """(Lesson 5) one 1-unit piece of floor line, straight onto the
    window. The floor is below everything, so nothing ever hides
    behind it: it can be drawn first, straight onto the window."""
    start = to_camera(world_start)
    end = to_camera(world_end)
    if (start[2] < NEAR) or (end[2] < NEAR):
        return
    pygame.draw.line(screen, GRID_COLOUR, project(start), project(end), 1)


def to_map(x, z):
    """A WORLD (x, z) -> a pixel on the mini-map (from Lesson 4)."""
    map_x = MAP_CX + (x * MAP_SCALE)
    map_y = MAP_CY - (z * MAP_SCALE)
    return (map_x, map_y)


def draw_map():
    """The mini-map: every thing, and you, from above (Lesson 4)."""
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
    forward_x, forward_y, forward_z = column(turn_matrix(cam_turn), 2)
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
            if event.key == pygame.K_g:
                show_grid = not show_grid
            if event.key == pygame.K_SPACE:
                spinning = not spinning
            if event.key == pygame.K_f:              # NEW
                fill_by_hand = not fill_by_hand

    keys = pygame.key.get_pressed()

    # ---- Turning and looking (from Lesson 4, unchanged) ----------------
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

    # ---- Fly where you look (from Lesson 7, unchanged) -----------------
    look = combine(tip_matrix(cam_tip), turn_matrix(cam_turn))
    forward_x, forward_y, forward_z = column(look, 2)
    right_x, right_y, right_z = column(turn_matrix(cam_turn), 0)
    if keys[pygame.K_w]:
        cam_x = (cam_x + (forward_x * MOVE_SPEED))
        cam_y = (cam_y + (forward_y * MOVE_SPEED))
        cam_z = (cam_z + (forward_z * MOVE_SPEED))
    if keys[pygame.K_s]:
        cam_x = (cam_x - (forward_x * MOVE_SPEED))
        cam_y = (cam_y - (forward_y * MOVE_SPEED))
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

    # ---- Every thing spins (Lesson 5), unless paused --------------------
    for thing in things:
        angles = thing["angles"]
        speeds = thing["speeds"]
        if spinning:
            angles[0] = keep_under_360( (angles[0] + speeds[0]) )
            angles[1] = keep_under_360( (angles[1] + speeds[1]) )
            angles[2] = keep_under_360( (angles[2] + speeds[2]) )
        thing["matrix"] = spin_matrix(angles)

    # ---- The camera's matrix, once a frame (Lesson 6) ------------------
    camera_matrix = combine(turn_matrix(-cam_turn), tip_matrix(-cam_tip))

    # ==================================================================
    # DRAW
    # ==================================================================
    screen.fill(BLACK)
    if show_grid:
        draw_floor()                       # straight onto the window

    # The painter's order (Lesson 3): sort far to near, paint in turn.
    faces_to_draw = []
    for thing in things:
        add_faces_of(thing, faces_to_draw)
    faces_to_draw.sort(reverse=True)

    if fill_by_hand:
        # NEW: fill every face ourselves into the small 200 x 150
        # picture, then stretch it 4 times to 800 x 600 and put it on
        # top of the floor lines (black blocks are see-through).
        small.fill(BLACK)
        for distance, face_points, colour in faces_to_draw:
            draw_face(face_points, colour)
        big = pygame.transform.scale(small, (WIDTH, HEIGHT))
        screen.blit(big, (0, 0))
    else:
        # F pressed: Lesson 7's way, pygame fills each face for us.
        for distance, face_points, colour in faces_to_draw:
            pygame.draw.polygon(screen, colour, face_points)

    draw_map()

    # ---- The HUD ---------------------------------------------------------
    if fill_by_hand:
        mode = "OUR OWN FILL, 4 x 4 BLOCKS   (F = pygame's fill)"
    else:
        mode = "PYGAME'S FILL   (F = our own fill)"
    screen.blit(font.render(mode, True, YELLOW), (20, 20))
    # clock.get_fps() = frames per second, averaged over the last few.
    text = ("frames a second " + str(round(clock.get_fps())))
    screen.blit(font.render(text, True, WHITE), (20, 50))
    screen.blit(font.render("painter's order: always ALL in front or ALL behind", True, PINK),
                (20, 570))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

# ----------------------------------------------------------------------
# TRY THIS:
#   * Fly round the board (A / D and the arrows). Is the board EVER
#     drawn partly in front of the cube and partly behind it?
#   * Press F to compare our fill with pygame's. Same colours, but ours
#     is made of 4 x 4 blocks.
#   * Change BLOCK to 8. The blocks are bigger. Are the frames a second
#     higher or lower? Then try 2.
#   * Paint only the blocks where (block_x + block_y) is even. What do
#     you see, and why?
# ----------------------------------------------------------------------
