import math
import random
import pygame

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
clock = pygame.time.Clock()
fps_font = pygame.font.SysFont(None, 32)   # default font, size 32, for the FPS counter

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 150, 0)
CYAN = (0, 255, 255)
RED = (255, 60, 60)
PURPLE = (160, 100, 230)
BLUE = (70, 150, 255) 
GOLD = (245, 200, 60)
CUBE_GREEN = (70, 230, 120)  
PINK = (255, 105, 200)

# PALETTES: # Face 0 gets colour 0, face 1 gets colour 1, and so on, in order.
# MORE colours than faces  -> the extra colours are simply not used .#   FEWER colours than faces -> start again from colour 0 (wrap round)
PALETTE_WARM   = [(235, 80, 80), (245, 140, 50), (245, 200, 60), (250, 120, 100), (255, 110, 170), (200, 60, 60), (255, 180, 120)]
PALETTE_COOL   = [(70, 150, 255), (60, 210, 200), (160, 100, 230), (90, 170, 255)]
PALETTE_GOLD   = [(245, 200, 60)]
PALETTE_FOREST = [(60, 140, 70), (120, 190, 80), (190, 220, 110), (90, 160, 140), (150, 110, 60)]
PALETTE_SUNSET = [(255, 120, 60), (230, 70, 110), (130, 70, 170)]
PALETTE_ICE    = [(220, 245, 255), (170, 220, 250), (120, 190, 240), (80, 150, 220), (180, 240, 230), (130, 210, 210), (200, 200, 255), (150, 170, 230)]

LIGHT = (0.48, 0.6, -0.64) # THe 'where is the light ' arrow direction of length 1 . 
AMBIENT = 0.2 # Everyone deservers a little light .. 

CENTRE_X = (WIDTH / 2)
CENTRE_Y = (HEIGHT / 2)
FOCAL = WIDTH / 2   # 90 degree horizontal view on any screen


#   6 faces: 0 back (+z, away from you), 1 left, 2 right, 3 top, 4 bottom, 5 front (-z, toward you)
cube_points = [(-1, -1, -1),( 1, -1, -1), ( 1, -1,  1),(-1, -1,  1),(-1,  1, -1),( 1,  1, -1),(1,  1,  1),(-1,  1,  1),]
cube_edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4),(0, 4), (1, 5), (2, 6), (3, 7),]
cube_faces = [((6, 7, 3, 2), (0, 0, 1)), ((7, 4, 0, 3), (-1, 0, 0)), ((5, 6, 2, 1), (1, 0, 0)), ((7, 6, 5, 4), (0, 1, 0)), ((2, 3, 0, 1), (0, -1, 0)), ((4, 5, 1, 0), (0, 0, -1))]
cube_model = {"points": cube_points, "edges": cube_edges, "faces": cube_faces}

#   5 faces: 0 base (points down), 1 front slope, 2 right slope, 3 back slope, 4 left slope
pyramid_points = [(-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1), (0, 1, 0)]
pyramid_edges = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 4), (1, 4), (2, 4), (3, 4)]
pyramid_faces = [((2, 3, 0, 1), (0, -1, 0)), ((4, 1, 0), (0, 0.447, -0.894)), ((4, 2, 1), (0.894, 0.447, 0)), ((4, 3, 2), (0, 0.447, 0.894)), ((4, 0, 3), (-0.894, 0.447, 0))]
pyramid_model = {"points": pyramid_points, "edges": pyramid_edges, "faces": pyramid_faces}

#   8 faces: top half 0 front-left, 1 front-right, 2 back-right, 3 back-left; bottom half 4 front-left, 5 front-right, 6 back-right, 7 back-left
diamond_points = [(0, 1, 0), (0, -1, 0), (-1, 0, 0), (1, 0, 0), (0, 0, -1), (0, 0, 1)]
diamond_edges = [(2, 4), (4, 3), (3, 5), (5, 2), (0, 2), (0, 3), (0, 4), (0, 5), (1, 2), (1, 3), (1, 4), (1, 5)]
diamond_faces = [((0, 4, 2), (-0.577, 0.577, -0.577)), ((0, 3, 4), (0.577, 0.577, -0.577)), ((0, 5, 3), (0.577, 0.577, 0.577)), ((0, 2, 5), (-0.577, 0.577, 0.577)), ((1, 2, 4), (-0.577, -0.577, -0.577)), ((1, 4, 3), (0.577, -0.577, -0.577)), ((1, 3, 5), (0.577, -0.577, 0.577)), ((1, 5, 2), (-0.577, -0.577, 0.577))]
diamond_model = {"points": diamond_points, "edges": diamond_edges, "faces": diamond_faces}

# ---- FRAME: a square with a hole in the middle, made of 4 long boxes ------
# same corner order and same faces as the cube, with its corner numbers moved along by 8.
frame_points = [
    (-1, 0.6, -0.2), (1, 0.6, -0.2), (1, 0.6, 0.2), (-1, 0.6, 0.2), (-1, 1, -0.2), (1, 1, -0.2), (1, 1, 0.2), (-1, 1, 0.2),    # 0-7 top box
    (-1, -1, -0.2), (1, -1, -0.2), (1, -1, 0.2), (-1, -1, 0.2), (-1, -0.6, -0.2), (1, -0.6, -0.2), (1, -0.6, 0.2), (-1, -0.6, 0.2),    # 8-15 bottom box
    (-1, -0.6, -0.2), (-0.6, -0.6, -0.2), (-0.6, -0.6, 0.2), (-1, -0.6, 0.2), (-1, 0.6, -0.2), (-0.6, 0.6, -0.2), (-0.6, 0.6, 0.2), (-1, 0.6, 0.2),    # 16-23 left box
    (0.6, -0.6, -0.2), (1, -0.6, -0.2), (1, -0.6, 0.2), (0.6, -0.6, 0.2), (0.6, 0.6, -0.2), (1, 0.6, -0.2), (1, 0.6, 0.2), (0.6, 0.6, 0.2),    # 24-31 right box
]
frame_edges = [
    (0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7),    # top
    (8, 9), (9, 10), (10, 11), (11, 8), (12, 13), (13, 14), (14, 15), (15, 12), (8, 12), (9, 13), (10, 14), (11, 15),    # bottom
    (16, 17), (17, 18), (18, 19), (19, 16), (20, 21), (21, 22), (22, 23), (23, 20), (16, 20), (17, 21), (18, 22), (19, 23),    # left
    (24, 25), (25, 26), (26, 27), (27, 24), (28, 29), (29, 30), (30, 31), (31, 28), (24, 28), (25, 29), (26, 30), (27, 31),    # right
]
frame_faces = [
    ((6, 7, 3, 2), (0, 0, 1)), ((7, 4, 0, 3), (-1, 0, 0)), ((5, 6, 2, 1), (1, 0, 0)), ((7, 6, 5, 4), (0, 1, 0)), ((2, 3, 0, 1), (0, -1, 0)), ((4, 5, 1, 0), (0, 0, -1)),    # 0-5 top: back, left, right, top, bottom, front
    ((14, 15, 11, 10), (0, 0, 1)), ((15, 12, 8, 11), (-1, 0, 0)), ((13, 14, 10, 9), (1, 0, 0)), ((15, 14, 13, 12), (0, 1, 0)), ((10, 11, 8, 9), (0, -1, 0)), ((12, 13, 9, 8), (0, 0, -1)),    # 6-11 bottom: back, left, right, top, bottom, front
    ((22, 23, 19, 18), (0, 0, 1)), ((23, 20, 16, 19), (-1, 0, 0)), ((21, 22, 18, 17), (1, 0, 0)), ((20, 21, 17, 16), (0, 0, -1)),    # 12-15 left: back, left, right, front (no top / bottom: they touch the top and bottom boxes)
    ((30, 31, 27, 26), (0, 0, 1)), ((31, 28, 24, 27), (-1, 0, 0)), ((29, 30, 26, 25), (1, 0, 0)), ((28, 29, 25, 24), (0, 0, -1)),    # 16-19 right: back, left, right, front (no top / bottom: they touch the top and bottom boxes)
]
#   20 faces: the top and bottom boxes have all 6, the left and right boxes only 4. Their top and bottom
#   faces were removed: they sit flat against the top and bottom boxes, hidden inside the frame,
#   and only caused flickering lines where the boxes meet.
frame_model = {"points": frame_points, "edges": frame_edges, "faces": frame_faces}

# ---- TANK (from rotation_101): Wireframe Warfare's tank, facing +z --------
# Same points and edges as rotation_101. Faces are (corners, normal): the colours were dropped,
# because the thing's palette colours them now. 22 faces, in the order listed.
tank_points = [
    (-0.9, -1, -1.3), (0.9, -1, -1.3), (0.9, -1, 1.2), (-0.9, -1, 1.2),                # 0-3   hull: track base
    (-1.1, -0.55, -1.5), (1.1, -0.55, -1.5), (1.1, -0.55, 1.6), (-1.1, -0.55, 1.6),    # 4-7   hull: belt
    (-0.75, -0.1, -1.2), (0.75, -0.1, -1.2), (0.75, -0.1, 0.5), (-0.75, -0.1, 0.5),    # 8-11  hull: deck
    (-0.5, -0.1, -0.9), (0.5, -0.1, -0.9), (0.5, -0.1, 0.3), (-0.5, -0.1, 0.3),        # 12-15 turret: base
    (-0.4, 0.35, -0.8), (0.4, 0.35, -0.8), (0.4, 0.35, 0), (-0.4, 0.35, 0),            # 16-19 turret: top
    (-0.08, 0.02, 0.15), (0.08, 0.02, 0.15), (0.08, 0.02, 1.9), (-0.08, 0.02, 1.9),    # 20-23 barrel: bottom
    (-0.08, 0.18, 0.15), (0.08, 0.18, 0.15), (0.08, 0.18, 1.9), (-0.08, 0.18, 1.9),    # 24-27 barrel: top
    (0, 0.35, -0.5), (0, 0.6, -0.5),                                                   # 28-29 radar mast
    (-0.22, 0.6, -0.5), (0.22, 0.6, -0.5), (0.22, 0.82, -0.5), (-0.22, 0.82, -0.5),    # 30-33 radar dish
]
tank_edges = [
    (0, 1), (0, 4), (1, 2), (1, 5), (2, 3), (2, 6), (3, 0), (3, 7), (4, 5), (4, 8), (5, 6), (5, 9), (6, 7), (6, 10), (7, 4), (7, 11), (8, 9), (9, 10), (10, 11), (11, 8),    # hull
    (12, 13), (12, 16), (13, 14), (13, 17), (14, 15), (14, 18), (15, 12), (15, 19), (16, 17), (17, 18), (18, 19), (19, 16),                                                  # turret
    (20, 21), (21, 22), (22, 23), (23, 20), (24, 25), (25, 26), (26, 27), (27, 24), (20, 24), (21, 25), (22, 26), (23, 27),                                                  # barrel
    (28, 29), (30, 31), (31, 32), (32, 33), (33, 30),                                                                                                                        # radar: mast, then dish
]
tank_faces = [
    ((0, 1, 2, 3), (0, -1, 0)), ((0, 4, 5, 1), (0, -0.406, -0.914)), ((1, 5, 6, 2), (0.914, -0.406, 0)), ((2, 6, 7, 3), (0, -0.664, 0.747)), ((3, 7, 4, 0), (-0.914, -0.406, 0)),                   #  0-4  hull: underside, then base -> belt (-z, +x, +z, -x sides)
    ((4, 8, 9, 5), (0, 0.555, -0.832)), ((5, 9, 10, 6), (0.789, 0.614, 0)), ((6, 10, 11, 7), (0, 0.926, 0.379)), ((7, 11, 8, 4), (-0.789, 0.614, 0)), ((8, 11, 10, 9), (0, 1, 0)),                  #  5-9  hull: belt -> deck (-z, +x, +z, -x sides), then the deck
    ((12, 16, 17, 13), (0, 0.217, -0.976)), ((13, 17, 18, 14), (0.976, 0.217, 0)), ((14, 18, 19, 15), (0, 0.555, 0.832)), ((15, 19, 16, 12), (-0.976, 0.217, 0)), ((16, 19, 18, 17), (0, 1, 0)),    # 10-14 turret: sides (-z, +x, +z, -x sides), then the top
    ((20, 21, 22, 23), (0, -1, 0)), ((24, 27, 26, 25), (0, 1, 0)), ((21, 25, 26, 22), (1, 0, 0)), ((23, 27, 24, 20), (-1, 0, 0)), ((22, 26, 27, 23), (0, 0, 1)),                                    # 15-19 barrel: bottom, top, +x side, -x side, muzzle (+z)
    ((30, 31, 32, 33), (0, 0, 1)), ((30, 33, 32, 31), (0, 0, -1)),                                                                                                                                  # 20-21 radar dish: front, back
]
#   22 faces, numbered as above for the palette. The tank's barrel points to +z (its front).
tank_model = {"points": tank_points, "edges": tank_edges, "faces": tank_faces}

# ---- THINGS: every object in the world, one dictionary each --------------
# "position" and "velocity" are LISTS [ ], because they change every frame.
# A thing SITS ON THE FLOOR when its centre y = (FLOOR_Y + size):
things = [
    {"name": "big cube",       "model": cube_model,    "position": [-2, 0, 9],    "velocity": [0.02, 0.01, -0.015],    "size": 1,    "angles": [35, 0, 0],   "speeds": (0, 1, 2),       "colour": (120, 190, 240), "palette": PALETTE_ICE},
    {"name": "small cube",     "model": cube_model,    "position": [3, -0.8, 5],  "velocity": [-0.03, 0.02, 0.025],    "size": 0.2,  "angles": [-50, 0, 0],  "speeds": (2, 0, 0),       "colour": (255, 120, 60),  "palette": PALETTE_SUNSET},
    {"name": "floor mini",     "model": cube_model,    "position": [-3, -0.7, 4], "velocity": [0.025, 0.03, 0.02],     "size": 0.3,  "angles": [20, 0, 0],   "speeds": (1, 0, 0),       "colour": (120, 190, 240), "palette": PALETTE_ICE},
    {"name": "hover mini",     "model": cube_model,    "position": [0, 0.6, 6],   "velocity": [-0.02, -0.015, 0.03],   "size": 0.3,  "angles": [10, 30, 0],  "speeds": (1.5, 1, 0.5),   "colour": (255, 120, 60),  "palette": PALETTE_SUNSET},
    {"name": "high mini",      "model": cube_model,    "position": [5, 2.5, 10],  "velocity": [-0.035, -0.02, -0.01],  "size": 0.4,  "angles": [45, 20, 10], "speeds": (0.5, 2, 1),     "colour": (120, 190, 240), "palette": PALETTE_ICE},
    {"name": "mid mini",       "model": cube_model,    "position": [-5, 1.2, 11], "velocity": [0.015, 0.025, -0.03],   "size": 0.25, "angles": [0, 45, 45],  "speeds": (3, 0, 1),       "colour": (255, 120, 60),  "palette": PALETTE_SUNSET},
    {"name": "gold mini",      "model": cube_model,    "position": [1.5, 1, 3.5], "velocity": [0.04, 0.035, 0.03],     "size": 0.1,  "angles": [30, 0, 0],   "speeds": (1, 1, 1),       "colour": (120, 190, 240), "palette": PALETTE_ICE},
    {"name": "big pyramid",    "model": pyramid_model, "position": [4, 1, 8],     "velocity": [-0.015, 0.005, 0.01],   "size": 1.2,  "angles": [15, 0, 0],   "speeds": (0.7, 0, 0),     "colour": (255, 120, 60),  "palette": PALETTE_SUNSET},
    {"name": "tumble pyramid", "model": pyramid_model, "position": [-3, 2.5, 7],  "velocity": [0.03, -0.02, 0.02],     "size": 0.4,  "angles": [0, 60, 20],  "speeds": (1, 2.5, 0.5),   "colour": (120, 190, 240), "palette": PALETTE_ICE},
    {"name": "sunset diamond", "model": diamond_model, "position": [-1, 1.5, 6],  "velocity": [0.02, 0.03, -0.02],     "size": 0.6,  "angles": [0, 0, 0],    "speeds": (2, 0, 0),       "colour": (255, 120, 60),  "palette": PALETTE_SUNSET},
    {"name": "ice diamond",    "model": diamond_model, "position": [2, 2, 10],    "velocity": [-0.025, -0.015, -0.03], "size": 0.8,  "angles": [45, 30, 0],  "speeds": (1.5, 0.8, 1.2), "colour": (120, 190, 240), "palette": PALETTE_ICE},
    {"name": "spark diamond",  "model": diamond_model, "position": [5, 0.5, 4],   "velocity": [-0.04, 0.025, 0.035],   "size": 0.25, "angles": [10, 20, 30], "speeds": (4, 3, 2),       "colour": (255, 120, 60),  "palette": PALETTE_SUNSET},
    {"name": "big frame",      "model": frame_model,   "position": [0, 1, 8],     "velocity": [0.05, 0.015, -0.008],   "size": 1,    "angles": [20, 0, 0],   "speeds": (0.5, 0, 0),     "colour": (120, 190, 240), "palette": PALETTE_ICE},
    {"name": "tumble frame",   "model": frame_model,   "position": [-4, 2, 6],    "velocity": [0.025, -0.02, 0.015],   "size": 0.7,  "angles": [0, 30, 15],  "speeds": (1, 1.5, 0.7),   "colour": (255, 120, 60),  "palette": PALETTE_SUNSET},
    {"name": "tank",           "model": tank_model,    "position": [0, 0.5, 16],  "velocity": [0, 0, 0],               "size": 1.5,  "angles": [180, 0, 0],  "speeds": (0, 0, 0),       "colour": (120, 190, 80),  "palette": PALETTE_FOREST},
    {"name": "tank left",      "model": tank_model,    "position": [-3.5, 0, 16], "velocity": [0, 0, 0],               "size": 1,    "angles": [180, 0, 0],  "speeds": (0, 0, 0),       "colour": (120, 190, 80),  "palette": PALETTE_FOREST},
    {"name": "tank right",     "model": tank_model,    "position": [3.5, 0, 16],  "velocity": [0, 0, 0],               "size": 1,    "angles": [180, 0, 0],  "speeds": (0, 0, 0),       "colour": (120, 190, 80),  "palette": PALETTE_FOREST},
]



cam_x = 0      # where YOU (the camera) stand, in WORLD coordinates
cam_y = 0      # your height (not shown on the map)
cam_z = 0
cam_turn = 0          # which way you face, in degrees. 0 = facing +z (up the map)
cam_tip = 0           # looking up / down, in degrees. 0 = level, + = down, - = up
cam_vy = 0            # your up / down speed: + = rising, - = falling

TURN_STEP = 1
TURN_SPEED = 1.5      # degrees per frame
TIP_LIMIT = 60        # don't let you look further up or down than this
STAND_Y = 0           # your eye height when standing: 1 above the floor (FLOOR_Y is -1)
JUMP_SPEED = 0.15     # the upward speed a jump starts with (SPACE)
GRAVITY = 0.004       # taken off cam_vy every frame, so you slow, stop, then fall
                      # (halved from 0.008: twice as high AND twice as long a jump)

## MINI MAP !!
MAP_SIZE = HEIGHT/3                         # the map is a 160 x 160 pixel square
MAP_LEFT = (WIDTH - 10 - MAP_SIZE)     # its left edge: 10 px in from the right of the screen
MAP_TOP = (HEIGHT - 10 - MAP_SIZE)     # its top edge: 10 px up from the bottom of the screen
MAP_COLOUR_BACK = (25, 30, 36)         # dark grey-blue, so the map stands out from the black

MAP_CX = (MAP_LEFT + (MAP_SIZE / 2))   # WORLD x = 0 goes across the middle of the box
MAP_CY = (MAP_TOP + (MAP_SIZE * 0.8))   # 80% of the way down the box
MAP_SCALE = (MAP_SIZE / 16)             # the box always shows 16 world units across

MOVE_SPEED = 0.05      # how far you move in ONE frame
NEAR = 0.1     # anything closer than this, measured from YOU, is not drawn
MOUSE_SPEED = 0.2      # degrees of turn per pixel the mouse moves

FLOOR_Y = -1                  # the floor's height: the bottom of a full-size cube at y = 0
GRID_LEFT = -8                # the grid runs from x = -8 ...
GRID_RIGHT = 8                # ... to x = 8
GRID_BACK = -3                # and from z = -3 ...
GRID_FAR = 13                 # ... to z = 13
GRID_COLOUR = (40, 90, 70)    # dim green: the floor is background, so it shouldn't stand out
CEILING_Y = 4                 # nothing flies higher than this
SHOW_PIECES = True            # TEST: True = every 1-unit floor piece gets its own colour

# ---- The WORLD BOX: every thing's centre bounces inside it ---------------
#   x: the grid's left and right edges,  y: floor to ceiling,  z: the grid's back and far edges
WORLD_MIN = [GRID_LEFT,  FLOOR_Y,   GRID_BACK]     # smallest x, y, z
WORLD_MAX = [GRID_RIGHT, CEILING_Y, GRID_FAR]      # biggest  x, y, z

def rotate_y(point_3d, angle):
    x, y, z = point_3d

    angle_radians = math.radians(angle)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)

    new_x = (x * cos_a) - (z * sin_a)
    new_z = (x * sin_a) + (z * cos_a)
    return (new_x, y, new_z)

def rotate_x(point_3d, angle):
    x, y, z = point_3d

    angle_radians = math.radians(angle)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)

    new_y = (y * cos_a) - (z * sin_a)
    new_z = (y * sin_a) + (z * cos_a)
    return (x, new_y, new_z)

def rotate_z(point_3d, angle):
    x, y, z = point_3d

    angle_radians = math.radians(angle)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)

    new_x = (x * cos_a) - (y * sin_a)
    new_y = (x * sin_a) + (y * cos_a)
    return (new_x, new_y, z)

def project(point_3d):
    x, y, z = point_3d
    screen_x = CENTRE_X + ( (x * FOCAL) / z )
    screen_y = CENTRE_Y - ( (y * FOCAL) / z )
    return (screen_x, screen_y)

def average_z(face_world_points):
    total = 0
    for x, y, z in face_world_points:
        total = (total + z)
    return (total / len(face_world_points))

def is_facing_you(face_points): # Cross Product of the two SCREEN arrow vectors ! Send in full face ( only reads 0,1,2)
    a_x, a_y = face_points[0]
    b_x, b_y = face_points[1]
    c_x, c_y = face_points[2]
    arrow_a_x = (b_x - a_x)
    arrow_a_y = (b_y - a_y)
    arrow_b_x = (c_x - a_x)
    arrow_b_y = (c_y - a_y)
    cross = ( (arrow_a_x * arrow_b_y) - (arrow_a_y * arrow_b_x) )
    return (cross > 0)

def dot(arrow_1, arrow_2):  # DOT PRODUCT: how well do two arrows line up? (both must be 1 long)
    x1, y1, z1 = arrow_1
    x2, y2, z2 = arrow_2
    return ( (x1 * x2) + (y1 * y2) + (z1 * z2) )


def shade_colour(colour, turned_normal):  # LIGHTING: how bright is this face? Returns the shaded colour

    # Take the dot product of the turned normal and LIGHT: multiply x by x, y by y and z by z, then add the three results.
    # dot product will show how aligned our NORMAL is with the light 
    brightness = dot(turned_normal, LIGHT)                  # -1 .. 1  (how well the face lines up with the lamp)
    if brightness < 0:         brightness = 0               # turned away from the lamp = no lamp light
    brightness = AMBIENT + ( (1 - AMBIENT) * brightness )   # 0.2 .. 1.0  (everyone gets a little light)
    red, green, blue = colour
    return ( int(red * brightness), int(green * brightness), int(blue * brightness) )


def to_map(x, z):
    map_x = MAP_CX + (x * MAP_SCALE)   # start at the map centre, move right by x
    map_y = MAP_CY - (z * MAP_SCALE)   # start at the map centre, move UP by z
    return (map_x, map_y)


def to_camera(world_point):
    x, y, z = world_point
    #return (x - cam_x, y - cam_y, z - cam_z)   # where the point is, measured from YOU

    moved = (x - cam_x, y - cam_y, z - cam_z)    # 1. measure from where you stand
   # return rotate_y(moved, -cam_turn)            # 2. turn the world the OPPOSITE way to you

    turned = rotate_y(moved, -cam_turn)          # 2. undo your turn (left / right)
    return rotate_x(turned, -cam_tip)            # 3. undo your tip (up / down)


def rotate_all(point_3d, angles):
    # Spin one point by a thing's OWN angles: turn (y), then tilt (x), then spin (z).
    turn, tilt, spin = angles
    return rotate_z(rotate_x(rotate_y(point_3d, turn), tilt), spin)


def to_world(shape_point, thing):
    # One SHAPE point of a thing -> a WORLD point: size, then spin, then place.
    x, y, z = shape_point
    size = thing["size"]
    sized = (x * size, y * size, z * size)                  # 1. size (round its own centre)
    sx, sy, sz = rotate_all(sized, thing["angles"])         # 2. spin by its own angles
    pos_x, pos_y, pos_z = thing["position"]
    return (sx + pos_x, sy + pos_y, sz + pos_z)             # 3. place it in the WORLD


def keep_under_360(angle):
    # 360 degrees is the same as 0, so keep every angle between 0 and 360.
    if angle >= 360:    angle = angle - 360
    if angle < 0:       angle = angle + 360
    return angle


def draw_floor_line(world_start, world_end):
    start = to_camera(world_start)               # both ends, measured from YOU
    end = to_camera(world_end)
    if start[2] < NEAR or end[2] < NEAR:         # an end too close or behind you:
        return                                   #   don't draw it (for now)
    colour = GRID_COLOUR
    if SHOW_PIECES:
        # Same piece -> same "random" colour every frame: the piece's own
        # start and end points are the seed, so the colours don't flicker.
        piece_random = random.Random(str((world_start, world_end)))
        colour = (piece_random.randint(60, 255), piece_random.randint(60, 255), piece_random.randint(60, 255))
    pygame.draw.line(screen, colour, project(start), project(end), 1)



def draw_floor():
    for z in range(GRID_BACK, GRID_FAR + 1):          # lines ACROSS: one at every z
        for x in range(GRID_LEFT, GRID_RIGHT):        #   cut into pieces: x to x + 1
            draw_floor_line((x, FLOOR_Y, z), (x + 1, FLOOR_Y, z))
    for x in range(GRID_LEFT, GRID_RIGHT + 1):        # lines AWAY: one at every x
        for z in range(GRID_BACK, GRID_FAR):          #   cut into pieces: z to z + 1
            draw_floor_line((x, FLOOR_Y, z), (x, FLOOR_Y, z + 1))





pygame.mouse.set_visible(False)      # hide the mouse pointer
pygame.event.set_grab(True)          # keep the mouse locked to the window
pygame.mouse.get_rel()               # reset, so the first frame doesn't jump

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if cam_y <= STAND_Y:                          # only jump when your feet are on the floor
                cam_vy = JUMP_SPEED

    keys = pygame.key.get_pressed()
    # ---- Spin the things: I J K L U O by hand, plus each one's own speeds ----
    for thing in things:
        angles = thing["angles"]                          # [turn, tilt, spin]
        if keys[pygame.K_l]:         angles[0] = angles[0] + TURN_STEP
        if keys[pygame.K_j]:         angles[0] = angles[0] - TURN_STEP
        if keys[pygame.K_i]:         angles[1] = angles[1] + TURN_STEP
        if keys[pygame.K_k]:         angles[1] = angles[1] - TURN_STEP
        if keys[pygame.K_u]:         angles[2] = angles[2] + TURN_STEP
        if keys[pygame.K_o]:         angles[2] = angles[2] - TURN_STEP
        speeds = thing["speeds"]
        angles[0] = angles[0] + speeds[0]
        angles[1] = angles[1] + speeds[1]
        angles[2] = angles[2] + speeds[2]
        angles[0] = keep_under_360(angles[0])
        angles[1] = keep_under_360(angles[1])
        angles[2] = keep_under_360(angles[2])

    # ---- CAMERA controls (as in step3_small_world) -------------------
    #   mouse = turn and look up / down
    #   W / S = walk forward / back, A / D = strafe left / right
    mouse_dx, mouse_dy = pygame.mouse.get_rel()          # pixels moved since last frame
    cam_turn = (cam_turn - (mouse_dx * MOUSE_SPEED))     # mouse right = turn right
    cam_tip = (cam_tip + (mouse_dy * MOUSE_SPEED))       # mouse up = look up
    if cam_tip > TIP_LIMIT:      cam_tip = TIP_LIMIT     # stop at the limits
    if cam_tip < -TIP_LIMIT:     cam_tip = -TIP_LIMIT

    forward_x, forward_y, forward_z = rotate_y((0, 0, 1), cam_turn)   # the way you face
    right_x, right_y, right_z = rotate_y((1, 0, 0), cam_turn)         # your right hand

    if keys[pygame.K_w]:                                  # forward
        cam_x = (cam_x + (forward_x * MOVE_SPEED))
        cam_z = (cam_z + (forward_z * MOVE_SPEED))
    if keys[pygame.K_s]:                                  # back
        cam_x = (cam_x - (forward_x * MOVE_SPEED))
        cam_z = (cam_z - (forward_z * MOVE_SPEED))
    if keys[pygame.K_d]:                                  # strafe right
        cam_x = (cam_x + (right_x * MOVE_SPEED))
        cam_z = (cam_z + (right_z * MOVE_SPEED))
    if keys[pygame.K_a]:                                  # strafe left
        cam_x = (cam_x - (right_x * MOVE_SPEED))
        cam_z = (cam_z - (right_z * MOVE_SPEED))

    # ---- Jumping and falling --------------------------------------------
    cam_vy = cam_vy - GRAVITY           # gravity pulls your speed DOWN a little each frame
    cam_y = cam_y + cam_vy              # move up (or down) by that speed
    if cam_y < STAND_Y:                 # gone below standing height: you've landed
        cam_y = STAND_Y
        cam_vy = 0

    # ---- Move every thing by its velocity, bouncing inside the WORLD BOX ----
    for thing in things:
        position = thing["position"]
        velocity = thing["velocity"]
        smallest, biggest = WORLD_MIN, WORLD_MAX
        for axis in range(3):                                   # 0 = x, 1 = y, 2 = z
            position[axis] = position[axis] + velocity[axis]
            if position[axis] > biggest[axis]:                  # past the top end:
                velocity[axis] = -abs(velocity[axis])           #   head DOWN this axis
            if position[axis] < smallest[axis]:                 # past the bottom end:
                velocity[axis] = abs(velocity[axis])            #   head UP this axis

    screen.fill(BLACK)

    draw_floor()                                   # the whole grid, before any shape



    face_paint_order = []          # EVERY face of EVERY thing, painted together after the loop

    #FOR EACH THING !
    for thing in things:
        model = thing["model"]

        world_points = []  # Real GAME WOrld X,Y,Z coordinates for points
        screen_points = [] # 2D Projected convershion of points
        camera_points = [] # the same corners measured from YOU (CAMERA): used for the painter's sort


        #FOR Each SHAPE point ( using 0,0,0 as center of shape )
        for p in model["points"]:
                moved = to_world(p, thing)                   # size, spin, place: WORLD
                world_points.append(moved)

                camera_point = to_camera(moved)
                camera_points.append(camera_point)          # keep it, so faces can use it later


                if camera_point[2] >= NEAR:                  # [2] is z: how far in front of you
                    screen_points.append(project(camera_point))
                else:
                    screen_points.append(None)              # too close or behind you: no pixel

        if model["faces"]:

            palette = thing["palette"]
            # enumerate counts as it goes: face_number is 0 for the first face, 1 for the next ...
            for face_number, (corners, normal) in enumerate(model["faces"]):
                face_points = []
                face_world_points = []

                for corner_number in corners:
                    face_points.append(screen_points[corner_number])
                    face_world_points.append(camera_points[corner_number] )

                if None in face_points:      # a corner is too close or behind you FAST FAIL
                    continue                 # skip the whole face

                #Cross product check
                if is_facing_you(face_points) : # Only add to draw list if yo are facing me .

                    # The normal spins WITH its thing (same angles), but is never sized or moved.
                    turned_normal = rotate_all(normal, thing["angles"])

                    # Pick this face's colour from the thing's palette, in order.
                    # % (remainder) wraps round when the palette is shorter than the faces list:
                    #   6 faces, 4 colours -> face 4 uses colour (4 % 4) = 0, face 5 uses (5 % 4) = 1
                    colour = palette[face_number % len(palette)]

                    colour = shade_colour(colour, turned_normal)

                    average_z_value = average_z(face_world_points)
                    face_paint_order.append((average_z_value, colour, face_points, thing["colour"]))

        else:

            for a, b in model["edges"]:
                if screen_points[a] is None or screen_points[b] is None:
                    continue                                 # an end too close or behind you
                pygame.draw.line(screen, thing["colour"], screen_points[a], screen_points[b], 2)

    # ---- The painter's sort: ALL faces together, furthest from YOU first ----
    face_paint_order.sort(reverse=True)
    for average_z_value, colour, face_points, outline_colour in face_paint_order:
        pygame.draw.polygon(screen, colour, face_points)               # filled
        pygame.draw.polygon(screen, outline_colour, face_points, 2)    # outline

## MINI MAP
    map_box = pygame.Rect(MAP_LEFT, MAP_TOP, MAP_SIZE, MAP_SIZE)
    pygame.draw.rect(screen, MAP_COLOUR_BACK, map_box)          # filled background
    pygame.draw.rect(screen, (255, 255, 255), map_box, 1)       # thin white border

    pygame.draw.circle(screen, (255, 255, 0), to_map(0, 0), 5)   # yellow dot = WORLD (0, 0, 0)


    for thing in things:                                          # one dot per thing
        thing_x, thing_y, thing_z = thing["position"]
        pygame.draw.circle(screen, thing["colour"], to_map(thing_x, thing_z), 5)
    
    pygame.draw.circle(screen, PINK, to_map(cam_x, cam_z), 5)   # pink dot = YOU

    face_x, face_y, face_z = rotate_y((0, 0, 1), cam_turn)            # your "forward" arrow
    nose = to_map(cam_x + (face_x * 1.5), cam_z + (face_z * 1.5))     # 1.5 units in front of you
    pygame.draw.line(screen, PINK, to_map(cam_x, cam_z), nose, 2)

## MINNI MAP 


    # FPS counter, top-left corner
    fps_text = fps_font.render("FPS: " + str(round(clock.get_fps())), True, GREEN)
    screen.blit(fps_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()