# =====================================================================================
# step4_draw_calls.py  -  raylib lesson, Parts 6 and 7: meshes, models, and why DRAW CALLS cost time
# =====================================================================================
#
# WHAT THIS SHOWS
#   The SAME picture, 1,600 cubes (a 40 x 40 field of them), drawn three different ways. Press 1, 2 or 3:
#
#     1  draw_cube x 1,600      raylib's easy shape call, once per cube, every frame.
#                               Python -> raylib 1,600 times; raylib works out 36 corners for each, ON THE CPU.
#     2  draw_model x 1,600     ONE cube mesh, sent to the card ONCE at the start. Each frame we say
#                               "draw that mesh again, here" 1,600 times: 1,600 DRAW CALLS.
#     3  draw_mesh x 1          ALL 1,600 cubes baked into ONE big mesh at the start (57,600 corners),
#                               sent to the card ONCE. Each frame: ONE call. This is what FrogWorld --gpu does
#                               with each chunk of the world.
#
#   The top line shows how many milliseconds the PYTHON side of the drawing took (the average of the last
#   60 frames) and the FPS. On the cloud computer (no graphics card) we measured, in milliseconds:
#   see the lesson page, Part 7. Run it on YOUR PC and compare: that is the real test.
#
# KEYS:  1 / 2 / 3  the three ways      Esc  quit
#
# THE COORDINATE SYSTEMS:
#   WORLD   metres from (0, 0, 0) on the floor, x right, y up, z ahead (the course / FrogWorld)
#   GPU     (-WORLD x, WORLD y, WORLD z): the mirror, function gpu() (step 2, picture r06_mirror.png)
#   SCREEN  pixels from the window's top-left, y down

import time
import numpy as np
import pyray as rl

WIDTH = 800
HEIGHT = 600
FOVY = 73.74                # degrees (= Lesson 1's FOCAL 400, step 2)
N_SIDE = 40                 # cubes along each side: (40 x 40) = 1,600 cubes. Try 80 (6,400) on a fast PC.
GAP = 2.0                   # metres from one cube's centre to the next: a 1 m cube, then 1 m of floor
SIZE = 1.0                  # metres: each cube is 1 x 1 x 1


def gpu(x, y, z):
    """WORLD (x, y, z) -> GPU (-x, y, z): the mirror."""
    return ((-x), y, z)


# -------------------------------------------------------------------------------------
# 1. WHERE THE CUBES ARE, AND THEIR COLOURS (the same for all three ways)
# -------------------------------------------------------------------------------------
# Cube (i, j), i and j from 0 to 39, sits at WORLD x = ((i - 19.5) x 2), z = (10 + (j x 2)), y = 0.5
# (y = half its height, so it stands ON the floor).
#   e.g. cube (0, 0):   x = ((0 - 19.5) x 2) = -39    z = (10 + 0) = 10       -> WORLD (-39, 0.5, 10)
#        cube (39, 39): x = ((39 - 19.5) x 2) = 39    z = (10 + (39 x 2)) = 88 -> WORLD (39, 0.5, 88)
cubes = []
for i in range(N_SIDE):
    for j in range(N_SIDE):
        x = ((i - ((N_SIDE - 1) / 2)) * GAP)
        z = (10 + (j * GAP))
        if ((i + j) % 2) == 0:                          # a chess board of two greens
            colour = (70, 170, 80, 255)
        else:
            colour = (40, 120, 60, 255)
        if (i % 10) == 0 and (j % 10) == 0:             # and a few red ones, to find your way
            colour = (210, 70, 60, 255)
        cubes.append(((x, (SIZE / 2), z), colour))


# -------------------------------------------------------------------------------------
# 2. WAY 3's BIG MESH: every cube's 12 triangles in two flat number lists   (picture r17_mesh_arrays.png)
# -------------------------------------------------------------------------------------
# A graphics card only draws TRIANGLES. A cube = 6 square faces = (6 x 2) = 12 triangles = (12 x 3) = 36
# corners ("vertices"). Each vertex gets:
#     a position  3 numbers, GPU metres:       x, y, z
#     a colour    4 numbers, 0 to 255:         red, green, blue, alpha
# and they all go, one after the other, into two long flat lists:
#     positions  [x0, y0, z0,  x1, y1, z1,  x2, y2, z2,  ...]     (1,600 x 36 x 3) = 172,800 numbers
#     colours    [r0, g0, b0, a0,  r1, g1, b1, a1,  ...]          (1,600 x 36 x 4) = 230,400 numbers
# The card reads them 3 vertices at a time: vertices 0, 1, 2 are triangle 0; 3, 4, 5 triangle 1; ...

# The 6 faces of a cube centred on (0, 0, 0), half-size h = 0.5, in GPU coordinates.
# Each face: its OUT direction (normal), and its 4 corners going round it.
h = (SIZE / 2)
FACES = [
    ((1, 0, 0),  [(h, -h, -h), (h, h, -h), (h, h, h), (h, -h, h)]),       # +x side
    ((-1, 0, 0), [(-h, -h, -h), (-h, -h, h), (-h, h, h), (-h, h, -h)]),   # -x side
    ((0, 1, 0),  [(-h, h, -h), (-h, h, h), (h, h, h), (h, h, -h)]),       # top
    ((0, -1, 0), [(-h, -h, -h), (h, -h, -h), (h, -h, h), (-h, -h, h)]),   # bottom
    ((0, 0, 1),  [(-h, -h, h), (h, -h, h), (h, h, h), (-h, h, h)]),       # +z side
    ((0, 0, -1), [(-h, -h, -h), (-h, h, -h), (h, h, -h), (h, -h, -h)]),   # -z side
]


def front_way_round(a, b, c, normal):
    """THE CLOCK TEST of Lesson 3, in 3D (picture r16_front_faces.png).
    The card only draws a triangle's FRONT: the side from which its corners a -> b -> c go ANTI-clockwise.
    The cross product of the two edges (b - a) and (c - a) points OUT of that front side, so:
        front faces the way we want  when  ((b - a) cross (c - a)) . normal  >  0
      e.g. a = (0, 0, 0), b = (1, 0, 0), c = (0, 1, 0):  (b - a) = (1, 0, 0), (c - a) = (0, 1, 0)
           cross = ((0 x 0) - (0 x 1), (0 x 0) - (1 x 0), (1 x 1) - (0 x 0)) = (0, 0, 1): its front faces +z."""
    ux, uy, uz = (b[0] - a[0]), (b[1] - a[1]), (b[2] - a[2])
    vx, vy, vz = (c[0] - a[0]), (c[1] - a[1]), (c[2] - a[2])
    cx = ((uy * vz) - (uz * vy))
    cy = ((uz * vx) - (ux * vz))
    cz = ((ux * vy) - (uy * vx))
    return (((cx * normal[0]) + (cy * normal[1]) + (cz * normal[2])) > 0)


# Turn each face into 2 triangles going the right way round, ONCE: (p0, p1, p2) and (p0, p2, p3)
CUBE_TRIANGLES = []
for normal, (p0, p1, p2, p3) in FACES:
    if not front_way_round(p0, p1, p2, normal):
        p0, p1, p2, p3 = p3, p2, p1, p0             # the other way round
    CUBE_TRIANGLES.append((p0, p1, p2))
    CUBE_TRIANGLES.append((p0, p2, p3))

# The two long lists, as numpy arrays (numpy makes ONE block of memory the card can copy in one go)
positions = []
colours = []
for (wx, wy, wz), colour in cubes:
    cx, cy, cz = gpu(wx, wy, wz)                    # the cube's centre, GPU metres
    for tri in CUBE_TRIANGLES:
        for (ox, oy, oz) in tri:                    # each corner = centre + its offset
            positions.extend(((cx + ox), (cy + oy), (cz + oz)))
            colours.extend(colour)
pos_array = np.array(positions, dtype=np.float32)   # float32 = the 4-byte numbers the card uses
col_array = np.array(colours, dtype=np.uint8)       # uint8 = whole numbers 0 to 255, 1 byte each

rl.init_window(WIDTH, HEIGHT, "Step 4 - draw calls")
rl.set_target_fps(0)        # 0 = no 60 FPS cap: run flat out, so we can see the real cost

# -------------------------------------------------------------------------------------
# 3. SEND THE BIG MESH TO THE CARD, ONCE   (picture r18_upload_once.png)
# -------------------------------------------------------------------------------------
# rl.ffi is the "bridge" between Python and raylib's C code. A Mesh is a C record; we fill in how many
# vertices and triangles, and WHERE in memory the two lists are, then upload_mesh copies them into the
# card's own memory (VRAM). FrogWorld's gpu_render.make_mesh does exactly this.
big_mesh = rl.ffi.new("Mesh *")
big_mesh.vertexCount = (len(pos_array) // 3)        # (172,800 / 3) = 57,600 vertices
big_mesh.triangleCount = (big_mesh.vertexCount // 3)   # 19,200 triangles
big_mesh.vertices = rl.ffi.cast("float *", rl.ffi.from_buffer(pos_array))
big_mesh.colors = rl.ffi.cast("unsigned char *", rl.ffi.from_buffer(col_array))
rl.upload_mesh(big_mesh, False)                     # False = "this mesh will never change" (static)
material = rl.load_material_default()               # the plain "use the vertex colours" way of filling
no_move = rl.matrix_identity()                      # "draw it where it is": no turn, no slide

# WAY 2's cube: raylib makes the 36 corners of a 1 m cube for us, and a MODEL wraps mesh + material.
cube_model = rl.load_model_from_mesh(rl.gen_mesh_cube(SIZE, SIZE, SIZE))

# The camera: 25 m up, behind the field, looking at its middle (WORLD (0, 0, 49))
camera = rl.Camera3D(gpu(0, 25, -12), gpu(0, 0, 49), (0, 1, 0), FOVY, rl.CAMERA_PERSPECTIVE)

way = 1
times = []                  # the last 60 frames' drawing times, milliseconds
NAMES = {1: "1  draw_cube x 1,600", 2: "2  draw_model x 1,600", 3: "3  draw_mesh x 1 (one big mesh)"}

while not rl.window_should_close():
    if rl.is_key_pressed(rl.KEY_ONE):
        way, times = 1, []
    if rl.is_key_pressed(rl.KEY_TWO):
        way, times = 2, []
    if rl.is_key_pressed(rl.KEY_THREE):
        way, times = 3, []

    rl.begin_drawing()
    rl.clear_background((20, 24, 32, 255))
    rl.begin_mode_3d(camera)

    t0 = time.perf_counter()
    if way == 1:
        for (wx, wy, wz), colour in cubes:
            rl.draw_cube(gpu(wx, wy, wz), SIZE, SIZE, SIZE, colour)
    elif way == 2:
        for (wx, wy, wz), colour in cubes:
            rl.draw_model(cube_model, gpu(wx, wy, wz), 1.0, colour)
    else:
        rl.draw_mesh(big_mesh[0], material, no_move)    # big_mesh[0]: "the Mesh itself", not its address
    rl.end_mode_3d()                                    # also hands raylib's held-back shapes to the card
    ms = ((time.perf_counter() - t0) * 1000)

    times.append(ms)
    if len(times) > 60:
        times.pop(0)
    average = (sum(times) / len(times))

    rl.draw_text("way " + NAMES[way], 20, 20, 20, (255, 214, 90, 255))
    rl.draw_text("Python drawing time: " + str(round(average, 2)) + " ms per frame", 20, 50, 20, (230, 230, 230, 255))
    rl.draw_fps(20, 80)
    rl.draw_text("1 / 2 / 3: the three ways", 20, 570, 18, (140, 150, 170, 255))
    rl.end_drawing()

rl.unload_model(cube_model)
rl.close_window()
