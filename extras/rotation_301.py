import array
import math
import random
import pygame

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
clock = pygame.time.Clock()
fps_font = pygame.font.SysFont(None, 32)   # default font, size 32, for the FPS counter


def make_sound(start_pitch, end_pitch, seconds, volume, fade):
    # A short sound made in code, so no sound file is needed: a tone that slides from start_pitch to end_pitch
    # (in Hz), lasting 'seconds'. 'volume' is out of 32767. 'fade' = how fast it dies away (bigger = faster).
    # A sound is just a long list of numbers: how far the speaker is pushed out or in, many thousand times a second.
    mixer_settings = pygame.mixer.get_init()        # (samples per second, format, channels), or None: no sound
    if mixer_settings is None:
        return None                                 # no sound device: stay silent rather than crash
    rate, sample_format, channels = mixer_settings
    if sample_format != -16:
        return None                                 # we build signed 16-bit numbers: anything else, stay silent
    length = int(rate * seconds)
    samples = array.array("h")                      # "h" = signed 16-bit whole numbers
    phase = 0
    for n in range(length):
        progress = n / length                       # 0 at the start of the sound, 1 at the end
        pitch = start_pitch + ((end_pitch - start_pitch) * progress)    # slide from one pitch to the other
        phase = phase + ((2 * math.pi * pitch) / rate)
        loudness = (1 - progress) ** fade           # starts loud, dies away
        value = int(volume * loudness * math.sin(phase))
        for channel in range(channels):             # the same number for each speaker (left, right)
            samples.append(value)
    return pygame.mixer.Sound(buffer=samples.tobytes())


# None if there's no sound: check before playing them
bump_sound = make_sound(220, 110, 0.08, 12000, 3)   # "bonk": low, falling, short - things bumping
ping_sound = make_sound(1800, 1600, 0.25, 7000, 2)  # "ping": high, rings a little longer - a bullet hit
hurt_sound = make_sound(330, 150, 0.7, 11000, 1.2)  # "wahhh": a slow, sad fall - YOU got hit
thud_sound = make_sound(110, 70, 0.12, 14000, 5)    # "thud": very low, short, dies at once - hitting a BOX
ALL_SOUNDS = [bump_sound, ping_sound, hurt_sound, thud_sound]   # every sound, so the volume reaches them all

# ---- VOLUME: one slider for every sound. Keys: - quieter, = louder (10% steps) ----
# Our ears hear loudness on a CURVE, not a straight line: half the strength does NOT sound half as loud.
# So the slider is SQUARED before it's used: 50% on the slider = 0.25 strength, which SOUNDS about half as loud,
# and every step on the slider feels about the same size.
volume = {"slider": 0.20}                           # 0.0 .. 1.0 = 0% .. 100%: starts at 20%


def apply_volume():
    # Set every sound's strength from the slider (squared: see above). Call it whenever the slider changes.
    strength = volume["slider"] * volume["slider"]
    for sound in ALL_SOUNDS:
        if sound:                                   # a sound is None if there's no sound device
            sound.set_volume(strength)


apply_volume()                                      # start at 20%

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
# "collision_spheres": the COLLISION spheres, each ((x, y, z) offset from the centre, radius), in the model's own units.
#   Like the corners, they get sized, spun and placed with the thing, so they turn with the shape.
cube_model = {"points": cube_points, "edges": cube_edges, "faces": cube_faces,
              "collision_spheres": [((0, 0, 0), 1.2)]}                    # between a side (1) and a corner (1.73)

#   5 faces: 0 base (points down), 1 front slope, 2 right slope, 3 back slope, 4 left slope
pyramid_points = [(-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1), (0, 1, 0)]
pyramid_edges = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 4), (1, 4), (2, 4), (3, 4)]
pyramid_faces = [((2, 3, 0, 1), (0, -1, 0)), ((4, 1, 0), (0, 0.447, -0.894)), ((4, 2, 1), (0.894, 0.447, 0)), ((4, 3, 2), (0, 0.447, 0.894)), ((4, 0, 3), (-0.894, 0.447, 0))]
pyramid_model = {"points": pyramid_points, "edges": pyramid_edges, "faces": pyramid_faces,
                 "collision_spheres": [((0, -0.3, 0), 1.0)]}             # lowered: the pyramid is heavier at the bottom

#   8 faces: top half 0 front-left, 1 front-right, 2 back-right, 3 back-left; bottom half 4 front-left, 5 front-right, 6 back-right, 7 back-left
diamond_points = [(0, 1, 0), (0, -1, 0), (-1, 0, 0), (1, 0, 0), (0, 0, -1), (0, 0, 1)]
diamond_edges = [(2, 4), (4, 3), (3, 5), (5, 2), (0, 2), (0, 3), (0, 4), (0, 5), (1, 2), (1, 3), (1, 4), (1, 5)]
diamond_faces = [((0, 4, 2), (-0.577, 0.577, -0.577)), ((0, 3, 4), (0.577, 0.577, -0.577)), ((0, 5, 3), (0.577, 0.577, 0.577)), ((0, 2, 5), (-0.577, 0.577, 0.577)), ((1, 2, 4), (-0.577, -0.577, -0.577)), ((1, 4, 3), (0.577, -0.577, -0.577)), ((1, 3, 5), (0.577, -0.577, 0.577)), ((1, 5, 2), (-0.577, -0.577, 0.577))]
diamond_model = {"points": diamond_points, "edges": diamond_edges, "faces": diamond_faces,
                 "collision_spheres": [((0, 0, 0), 1.0)]}                # tips are exactly 1 from the centre

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
frame_model = {"points": frame_points, "edges": frame_edges, "faces": frame_faces,
               "collision_spheres": [((-0.8,  0.8, 0), 0.45), ((0,  0.8, 0), 0.45), ((0.8,  0.8, 0), 0.45),    # top arm
                           ((-0.8,    0, 0), 0.45),                        ((0.8,    0, 0), 0.45),    # side arms
                           ((-0.8, -0.8, 0), 0.45), ((0, -0.8, 0), 0.45), ((0.8, -0.8, 0), 0.45)]}  # bottom arm
#   8 spheres round the ring, 0.8 apart, so neighbours overlap a little. The middle stays open (about +-0.35).

# ---- TANK HULL (from rotation_101's tank): the tracks and body, facing +z --------
# The tank is now TWO things: this hull, and a turret CHILD that rides on it (see turret_model).
# Faces are (corners, normal): the colours were dropped, because the thing's palette colours them now.
hull_points = [
    (-0.9, -1, -1.3), (0.9, -1, -1.3), (0.9, -1, 1.2), (-0.9, -1, 1.2),                # 0-3   track base
    (-1.1, -0.55, -1.5), (1.1, -0.55, -1.5), (1.1, -0.55, 1.6), (-1.1, -0.55, 1.6),    # 4-7   belt
    (-0.75, -0.1, -1.2), (0.75, -0.1, -1.2), (0.75, -0.1, 0.5), (-0.75, -0.1, 0.5),    # 8-11  deck
]
hull_edges = [
    (0, 1), (0, 4), (1, 2), (1, 5), (2, 3), (2, 6), (3, 0), (3, 7), (4, 5), (4, 8), (5, 6), (5, 9), (6, 7), (6, 10), (7, 4), (7, 11), (8, 9), (9, 10), (10, 11), (11, 8),
]
hull_faces = [
    ((0, 1, 2, 3), (0, -1, 0)), ((0, 4, 5, 1), (0, -0.406, -0.914)), ((1, 5, 6, 2), (0.914, -0.406, 0)), ((2, 6, 7, 3), (0, -0.664, 0.747)), ((3, 7, 4, 0), (-0.914, -0.406, 0)),                   #  0-4  underside, then base -> belt (-z, +x, +z, -x sides)
    ((4, 8, 9, 5), (0, 0.555, -0.832)), ((5, 9, 10, 6), (0.789, 0.614, 0)), ((6, 10, 11, 7), (0, 0.926, 0.379)), ((7, 11, 8, 4), (-0.789, 0.614, 0)), ((8, 11, 10, 9), (0, 1, 0)),                  #  5-9  belt -> deck (-z, +x, +z, -x sides), then the deck
]
#   10 faces, numbered as above for the palette. The hull's front is +z.
hull_model = {"points": hull_points, "edges": hull_edges, "faces": hull_faces,
              "collision_spheres": [((0, -0.4, -0.6), 1.0),     # rear hull (still reaches up round the turret)
                                    ((0, -0.4,  0.7), 1.0)]}    # front hull (overlaps the rear one)

# ---- TANK TURRET: turret + barrel, built round its PIVOT (the middle of the turret's base) ----
# The old tank's numbers moved by y + 0.1, z + 0.3, so (0, 0, 0) is the point it spins round.
# It sits on the hull at (0, -0.1, -0.3) in the HULL's model units: that's the child's "position".
# The barrel is still split in two (z 0.45 -> 1.3 -> 2.2): the painter's sort uses ONE centre point per
# face, and a long barrel face's centre sat right next to the hull's front slope's centre.
turret_points = [
    (-0.5, 0, -0.6), (0.5, 0, -0.6), (0.5, 0, 0.6), (-0.5, 0, 0.6),                    # 0-3   turret: base
    (-0.4, 0.45, -0.5), (0.4, 0.45, -0.5), (0.4, 0.45, 0.3), (-0.4, 0.45, 0.3),        # 4-7   turret: top
    (-0.08, 0.12, 0.45), (0.08, 0.12, 0.45), (0.08, 0.12, 1.3), (-0.08, 0.12, 1.3),    # 8-11  barrel REAR piece: bottom
    (-0.08, 0.28, 0.45), (0.08, 0.28, 0.45), (0.08, 0.28, 1.3), (-0.08, 0.28, 1.3),    # 12-15 barrel REAR piece: top
    (-0.08, 0.12, 1.3), (0.08, 0.12, 1.3), (0.08, 0.12, 2.2), (-0.08, 0.12, 2.2),      # 16-19 barrel FRONT piece: bottom
    (-0.08, 0.28, 1.3), (0.08, 0.28, 1.3), (0.08, 0.28, 2.2), (-0.08, 0.28, 2.2),      # 20-23 barrel FRONT piece: top
]                                                                                      #   (the radar is its own model now: radar_model)
turret_edges = [
    (0, 1), (0, 4), (1, 2), (1, 5), (2, 3), (2, 6), (3, 0), (3, 7), (4, 5), (5, 6), (6, 7), (7, 4),                                                                        # turret
    (8, 9), (9, 10), (10, 11), (11, 8), (12, 13), (13, 14), (14, 15), (15, 12), (8, 12), (9, 13), (10, 14), (11, 15),                                                      # barrel: rear piece
    (16, 17), (17, 18), (18, 19), (19, 16), (20, 21), (21, 22), (22, 23), (23, 20), (16, 20), (17, 21), (18, 22), (19, 23),                                                # barrel: front piece
]
turret_faces = [
    ((0, 4, 5, 1), (0, 0.217, -0.976)), ((1, 5, 6, 2), (0.976, 0.217, 0)), ((2, 6, 7, 3), (0, 0.555, 0.832)), ((3, 7, 4, 0), (-0.976, 0.217, 0)), ((4, 7, 6, 5), (0, 1, 0)),   #  0-4   turret: sides (-z, +x, +z, -x), then top
    ((8, 9, 10, 11), (0, -1, 0)), ((12, 15, 14, 13), (0, 1, 0)), ((9, 13, 14, 10), (1, 0, 0)), ((11, 15, 12, 8), (-1, 0, 0)), ((18, 22, 23, 19), (0, 0, 1)),                 #  5-9   barrel rear piece: bottom, top, +x, -x; 9 = muzzle (+z, on the FRONT piece's tip)
    ((16, 17, 18, 19), (0, -1, 0)), ((20, 23, 22, 21), (0, 1, 0)), ((17, 21, 22, 18), (1, 0, 0)), ((19, 23, 20, 16), (-1, 0, 0)),                                            # 10-13  barrel front piece: bottom, top, +x, -x
]
#   14 faces, numbered as above for the palette. The barrel points to +z (the turret's front).
#   No faces where the two barrel pieces meet: they'd be hidden inside the barrel and only flicker.
turret_model = {"points": turret_points, "edges": turret_edges, "faces": turret_faces,
                "muzzles": [(0, 0.2, 2.2)],                         # where bullets come out: the barrel's tip
                "collision_spheres": [((0, 0.2, 2.05), 0.2)]}      # barrel tip: now swings WITH the turret

# ---- TWIN TURRET: the same turret, with TWO barrels side by side (for the big tank) ----
# Same turret points as turret_model. Its one barrel was moved 0.15 to the left, and a copy
# added 0.15 to the right (the barrels are 0.16 wide, so that leaves a small gap between them).
# Built round the same PIVOT, so it fits the hull at (0, -0.1, -0.3) just like turret_model.
twin_turret_points = [
    (-0.5, 0, -0.6), (0.5, 0, -0.6), (0.5, 0, 0.6), (-0.5, 0, 0.6),                    # 0-3   turret: base
    (-0.4, 0.45, -0.5), (0.4, 0.45, -0.5), (0.4, 0.45, 0.3), (-0.4, 0.45, 0.3),        # 4-7   turret: top
    (-0.23, 0.12, 0.45), (-0.07, 0.12, 0.45), (-0.07, 0.12, 1.3), (-0.23, 0.12, 1.3),    # 8-11 LEFT barrel (x - 0.15): REAR piece: bottom
    (-0.23, 0.28, 0.45), (-0.07, 0.28, 0.45), (-0.07, 0.28, 1.3), (-0.23, 0.28, 1.3),    # 12-15 LEFT barrel (x - 0.15): REAR piece: top
    (-0.23, 0.12, 1.3), (-0.07, 0.12, 1.3), (-0.07, 0.12, 2.2), (-0.23, 0.12, 2.2),    # 16-19 LEFT barrel (x - 0.15): FRONT piece: bottom
    (-0.23, 0.28, 1.3), (-0.07, 0.28, 1.3), (-0.07, 0.28, 2.2), (-0.23, 0.28, 2.2),    # 20-23 LEFT barrel (x - 0.15): FRONT piece: top
    (0.07, 0.12, 0.45), (0.23, 0.12, 0.45), (0.23, 0.12, 1.3), (0.07, 0.12, 1.3),    # 24-27 RIGHT barrel (x + 0.15): REAR piece: bottom
    (0.07, 0.28, 0.45), (0.23, 0.28, 0.45), (0.23, 0.28, 1.3), (0.07, 0.28, 1.3),    # 28-31 RIGHT barrel (x + 0.15): REAR piece: top
    (0.07, 0.12, 1.3), (0.23, 0.12, 1.3), (0.23, 0.12, 2.2), (0.07, 0.12, 2.2),    # 32-35 RIGHT barrel (x + 0.15): FRONT piece: bottom
    (0.07, 0.28, 1.3), (0.23, 0.28, 1.3), (0.23, 0.28, 2.2), (0.07, 0.28, 2.2),    # 36-39 RIGHT barrel (x + 0.15): FRONT piece: top
]
twin_turret_edges = [
    (0, 1), (0, 4), (1, 2), (1, 5), (2, 3), (2, 6), (3, 0), (3, 7), (4, 5), (5, 6), (6, 7), (7, 4),    # turret
    (8, 9), (9, 10), (10, 11), (11, 8), (12, 13), (13, 14), (14, 15), (15, 12), (8, 12), (9, 13), (10, 14), (11, 15),    # left barrel: rear piece
    (16, 17), (17, 18), (18, 19), (19, 16), (20, 21), (21, 22), (22, 23), (23, 20), (16, 20), (17, 21), (18, 22), (19, 23),    # left barrel: front piece
    (24, 25), (25, 26), (26, 27), (27, 24), (28, 29), (29, 30), (30, 31), (31, 28), (24, 28), (25, 29), (26, 30), (27, 31),    # right barrel: rear piece
    (32, 33), (33, 34), (34, 35), (35, 32), (36, 37), (37, 38), (38, 39), (39, 36), (32, 36), (33, 37), (34, 38), (35, 39),    # right barrel: front piece
]
twin_turret_faces = [
    ((0, 4, 5, 1), (0, 0.217, -0.976)), ((1, 5, 6, 2), (0.976, 0.217, 0)), ((2, 6, 7, 3), (0, 0.555, 0.832)), ((3, 7, 4, 0), (-0.976, 0.217, 0)), ((4, 7, 6, 5), (0, 1, 0)),    #  0-4   turret: sides (-z, +x, +z, -x), then top
    ((8, 9, 10, 11), (0, -1, 0)), ((12, 15, 14, 13), (0, 1, 0)), ((9, 13, 14, 10), (1, 0, 0)), ((11, 15, 12, 8), (-1, 0, 0)), ((18, 22, 23, 19), (0, 0, 1)),    #  5-9   LEFT barrel rear piece: bottom, top, +x, -x; 9 = its muzzle
    ((16, 17, 18, 19), (0, -1, 0)), ((20, 23, 22, 21), (0, 1, 0)), ((17, 21, 22, 18), (1, 0, 0)), ((19, 23, 20, 16), (-1, 0, 0)),    # 10-13  LEFT barrel front piece: bottom, top, +x, -x
    ((24, 25, 26, 27), (0, -1, 0)), ((28, 31, 30, 29), (0, 1, 0)), ((25, 29, 30, 26), (1, 0, 0)), ((27, 31, 28, 24), (-1, 0, 0)), ((34, 38, 39, 35), (0, 0, 1)),    # 14-18  RIGHT barrel rear piece: bottom, top, +x, -x; 18 = its muzzle
    ((32, 33, 34, 35), (0, -1, 0)), ((36, 39, 38, 37), (0, 1, 0)), ((33, 37, 38, 34), (1, 0, 0)), ((35, 39, 36, 32), (-1, 0, 0)),    # 19-22  RIGHT barrel front piece: bottom, top, +x, -x
]
#   23 faces, numbered as above for the palette. Both barrels point to +z (the turret's front).
twin_turret_model = {"points": twin_turret_points, "edges": twin_turret_edges, "faces": twin_turret_faces,
                     "muzzles": [(-0.15, 0.2, 2.2), (0.15, 0.2, 2.2)],      # both barrel tips: it takes turns
                     "collision_spheres": [((-0.15, 0.2, 2.05), 0.2),     # left barrel tip
                                           (( 0.15, 0.2, 2.05), 0.2)]}    # right barrel tip

# ---- TANK RADAR: mast + dish, built round the FOOT of its mast ----
# A child of the HULL (not the turret): its mast stands only 0.2 from the turret's pivot, so it always
# stays over the turret's roof however the turret turns. It sits on the hull at (0, 0.35, -0.5).
radar_points = [
    (0, 0, 0), (0, 0.25, 0),                                                           # 0-1  mast (an edge only)
    (-0.22, 0.25, 0), (0.22, 0.25, 0), (0.22, 0.47, 0), (-0.22, 0.47, 0),              # 2-5  dish
]
radar_edges = [(0, 1), (2, 3), (3, 4), (4, 5), (5, 2)]                                 # mast, then dish
radar_faces = [((2, 3, 4, 5), (0, 0, 1)), ((2, 5, 4, 3), (0, 0, -1))]                  # 0-1  dish: front, back
radar_model = {"points": radar_points, "edges": radar_edges, "faces": radar_faces,
               "collision_spheres": []}                    # none: the hull's rear sphere already covers it

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
    {"name": "tank",           "model": hull_model,    "position": [0, 0.5, 16],  "velocity": [0, 0, 0],               "size": 1.5,  "angles": [180, 0, 0],  "speeds": (0, 0, 0),       "colour": (120, 190, 80),  "palette": PALETTE_FOREST, "faces_movement": True},
    {"name": "tank left",      "model": hull_model,    "position": [-3.5, 0, 16], "velocity": [0, 0, 0],               "size": 1,    "angles": [180, 0, 0],  "speeds": (0, 0, 0),       "colour": (120, 190, 80),  "palette": PALETTE_FOREST, "faces_movement": True},
    {"name": "small tank",     "model": hull_model,    "position": [3.5, -0.4, 16], "velocity": [-0.006, 0, -0.008],   "size": 0.6,  "angles": [180, 0, 0],  "speeds": (0, 0, 0),       "colour": (120, 190, 80),  "palette": PALETTE_FOREST, "faces_movement": True},

    # TURRETS: CHILDREN of a tank. "position" and "angles" are RELATIVE to the parent, in its model units.
    # No velocity: a child rides on its parent. "speeds" = its own spin (degrees per frame) - just for testing.
    {"name": "tank turret",       "parent": "tank",       "model": twin_turret_model, "position": [0, -0.1, -0.3], "velocity": [0, 0, 0], "size": 1, "angles": [0, 0, 0], "speeds": (0.3, 0, 0),    "colour": (120, 190, 80), "palette": PALETTE_FOREST, "gun": True, "cooldown": 0, "next_muzzle": 0, "volley_left": 0, "volley_timer": 0},
    {"name": "tank left turret",  "parent": "tank left",  "model": turret_model, "position": [0, -0.1, -0.3], "velocity": [0, 0, 0], "size": 1, "angles": [0, 0, 0], "speeds": (-0.5, 0, 0), "colour": (120, 190, 80), "palette": PALETTE_FOREST, "gun": True, "cooldown": 0, "next_muzzle": 0, "volley_left": 0, "volley_timer": 0},
    {"name": "small tank turret", "parent": "small tank", "model": turret_model, "position": [0, -0.1, -0.3], "velocity": [0, 0, 0], "size": 1, "angles": [0, 0, 0], "speeds": (2, 0, 0),    "colour": (120, 190, 80), "palette": PALETTE_FOREST, "gun": True, "cooldown": 0, "next_muzzle": 0, "volley_left": 0, "volley_timer": 0},

    # RADARS: also children of the HULL (it would stay over the turret roof anyway). Fast spin,
    # the OPPOSITE way to each tank's turret.
    {"name": "tank radar",        "parent": "tank",       "model": radar_model,  "position": [0, 0.35, -0.5], "velocity": [0, 0, 0], "size": 1, "angles": [0, 0, 0], "speeds": (-6, 0, 0),   "colour": (120, 190, 80), "palette": PALETTE_FOREST},
    {"name": "tank left radar",   "parent": "tank left",  "model": radar_model,  "position": [0, 0.35, -0.5], "velocity": [0, 0, 0], "size": 1, "angles": [0, 0, 0], "speeds": (6, 0, 0),    "colour": (120, 190, 80), "palette": PALETTE_FOREST},
    {"name": "small tank radar",  "parent": "small tank", "model": radar_model,  "position": [0, 0.35, -0.5], "velocity": [0, 0, 0], "size": 1, "angles": [0, 0, 0], "speeds": (-6, 0, 0),   "colour": (120, 190, 80), "palette": PALETTE_FOREST},
]

# Connect each child to its parent ONCE, by name, so to_world() doesn't have to look it up every frame.
# A spelling mistake in a "parent" name stops the game here with a KeyError naming it.
things_by_name = {thing["name"]: thing for thing in things}
for thing in things:
    if "parent" in thing:
        thing["parent_thing"] = things_by_name[thing["parent"]]      # the actual parent dictionary

# ---- HEALTH: every shape (not children, not bullets) starts with health that depends on its SIZE ----
# A thing's REACH = how far its shape sticks out from its centre: its furthest collision sphere edge, times size.
# The biggest reach gets MAX_HEALTH; the others get the same share of it as their reach is of the biggest.
MAX_HEALTH = 10
HEALTH_SQUARE = 5         # pixels: each health square
HEALTH_GAP = 2            # pixels between the squares
SPLIT_SIZE = 0.7          # a shape at 0 health splits into 2 pieces, each this much of its size (TO TUNE LATER)
SPLIT_KICK = 0.03         # how fast the two pieces push apart (world units per frame)
for thing in things:
    if "parent" in thing:
        continue
    reach = 0
    for (ox, oy, oz), radius in thing["model"]["collision_spheres"]:
        reach = max(reach, math.sqrt((ox * ox) + (oy * oy) + (oz * oz)) + radius)
    thing["reach"] = reach * thing["size"]
biggest_reach = max(thing["reach"] for thing in things if "parent" not in thing)
for thing in things:
    if "parent" not in thing:
        thing["max_health"] = max(1, round(MAX_HEALTH * thing["reach"] / biggest_reach))   # at least 1
        thing["health"] = thing["max_health"]



cam_x = -7.8   # where YOU (the camera) stand, in WORLD coordinates: the lower-left corner
cam_y = 0      # your height (not shown on the map)
cam_z = -3.2   #   (right by the grid's corner at x = -8, z = -3)
cam_turn = -30        # which way you face, in degrees. 0 = facing +z (up the map). -30 shows as "Facing: 30°"
cam_tip = -1          # looking up / down, in degrees. 0 = level, + = down, - = up. -1 shows as "Tilt: 1°"
cam_vy = 0            # your up / down speed: + = rising, - = falling

TURN_STEP = 1
TURN_SPEED = 1.5      # degrees per frame
TIP_LIMIT = 60        # don't let you look further up or down than this
STAND_Y = 0           # your eye height when standing: 1 above the floor (FLOOR_Y is -1)
JUMP_SPEED = 0.15     # the upward speed a jump starts with (SPACE)
GRAVITY = 0.004       # taken off cam_vy every frame, so you slow, stop, then fall
                      # (halved from 0.008: twice as high AND twice as long a jump)

## MINI MAP !!
MAP_SIZE = HEIGHT/3 *0.50                        # the map is a 160 x 160 pixel square
MAP_LEFT = (WIDTH - 10 - MAP_SIZE)     # its left edge: 10 px in from the right of the screen
MAP_TOP = (HEIGHT - 10 - (MAP_SIZE * 0.25) - MAP_SIZE)     # its top edge: raised 25% of MAP_SIZE above the old 10 px margin
MAP_COLOUR_BACK = (25, 30, 36)         # dark grey-blue, so the map stands out from the black
MAP_BOX_HEIGHT = (MAP_SIZE * 1.25 * 1.33)     # the DRAWN box is 25% taller than wide, then 33% taller again ...
MAP_BOX_TOP = (HEIGHT - 10 - (MAP_SIZE * 0.25) - MAP_BOX_HEIGHT)   # ... and grows UPWARDS (raised by the same 25% as MAP_TOP)
                                       # (MAP_TOP is still used to place WORLD (0, 0), so nothing on the map moves)
# A see-through card the size of the map box. SRCALPHA = this surface has its own alpha (see-through-ness).
map_background = pygame.Surface((MAP_SIZE, MAP_BOX_HEIGHT), pygame.SRCALPHA)
map_background.fill(MAP_COLOUR_BACK + (128,))   # alpha 128: 0 = invisible, 255 = solid, 128 = about 50%

MAP_CX = (MAP_LEFT + (MAP_SIZE / 2))   # WORLD x = 0 goes across the middle of the box
MAP_CY = (MAP_TOP + (MAP_SIZE * 0.8))   # 80% of the way down the box
MAP_SCALE = (MAP_SIZE / 16)             # the box always shows 16 world units across

MOVE_SPEED = 0.05      # how far you move in ONE frame
show_spheres = False   # C key: draw the collision spheres (a debug view)

# ---- SPARKS: a burst of particles where two things bump ----
particles = []            # every live spark: {"position", "velocity", "life", "colour"}
SPARK_COUNT = 14          # sparks per bump
SPARK_SPEED = 0.06        # fastest a spark flies out (world units per frame)
SPARK_LIFE = 30           # frames a spark lasts (half a second at 60 FPS)
SPARK_GRAVITY = 0.002     # taken off a spark's up / down speed every frame, so they arc down
SPARK_SIZE = 0.04         # a spark's radius in world units, when it's brand new

# ---- BULLETS: a tiny solid cube per left click, added to THINGS while the game runs ----
BULLET_SPEED = 0.4        # world units per frame (fast: 24 units a second at 60 FPS)
BULLET_RANGE = 1000       # how far a bullet flies before it's removed: very long, the WORLD BOX stops it first
BULLET_SIZE = 0.05        # a cube of size 0.05 is 0.1 across
BULLET_MARGIN = 1         # bullets die once they're this far OUTSIDE the world box (you can stand just outside it)

# ---- TANK GUNS: turrets fire green bullets at you when they're pointing your way ----
TANK_CONE = 8             # degrees either side of straight ahead: point within this of you = "I see you"
TANK_COOLDOWN = 90        # frames a turret rests after a volley (1.5 seconds at 60 FPS)
TANK_VOLLEY = 3           # shots in one volley
TANK_VOLLEY_GAP = 8       # frames between the shots in a volley
TANK_BULLET_SPEED = 0.15  # slower than yours, so you can dodge
TANK_BULLET_COLOUR = (60, 255, 60)
PALETTE_TANK_BULLET = [(60, 255, 60), (30, 200, 30)]
YOUR_HIT_RADIUS = 0.3     # a tank bullet this close to your eye counts as hitting YOU
you = {"hits_taken": 0, "hurt": 0}   # how many times you've been hit, and frames left of the red flash

# ---- CROSSHAIR: a gap cross + dot in the middle of the screen ----
CROSSHAIR_GAP = 6         # pixels from the centre to where each arm starts
CROSSHAIR_LENGTH = 10     # pixels long, each arm
CROSSHAIR_KICK = 10       # extra gap, in pixels, the moment you fire: the arms jump out, then spring back
CROSSHAIR_HIT_FRAMES = 10 # how many frames the red X "hit marker" shows after a bullet hits
CROSSHAIR_COLOUR = (255, 255, 255)
HIT_MARKER_COLOUR = (255, 70, 70)
crosshair = {"kick": 0, "hit": 0}   # what it's doing right now. A DICTIONARY, so functions can change it
                                    # without needing 'global' (changing what's inside it, not the name)
NEAR = 0.1     # anything closer than this, measured from YOU, is not drawn
MOUSE_SPEED = 0.2      # degrees of turn per pixel the mouse moves

FLOOR_Y = -1                  # the floor's height: the bottom of a full-size cube at y = 0
GRID_LEFT = -8                # the grid runs from x = -8 ...
GRID_RIGHT = 8                # ... to x = 8
GRID_BACK = -3                # and from z = -3 ...
GRID_FAR = 20                 # ... to z = 20: the floor is 23 deep
GRID_COLOUR = (40, 90, 70)    # dim green: the floor is background, so it shouldn't stand out

# ---- FLOOR SHAPES: flat polygons painted ON the floor (not things: no sorting, no collisions) ----
# Each one: ([corners as (x, z)], colour), in WORLD units on the floor (y is always FLOOR_Y).
# Corners go ROUND the shape in order. Drawn in list order, so a later shape is painted on top.
FLOOR_SHAPES = [
    ([(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)], (255, 215, 0)),    # gold 1 x 1 square under WORLD (0, 0, 0)
     ([(7.436, -2.548), (6.596, -1.428), (6.42, -1.56), (6.3, -0.9), (6.9, -1.2), (6.724, -1.332), (7.564, -2.452)], (255, 255, 255)),
]

# ---- BOXES: static structures, NOT things. Each is a box lined up with x, y and z (it never turns),
# given by two opposite corners in WORLD units: "min" = smallest x, y, z and "max" = biggest x, y, z.
# Their 8 corners and 6 face colours are worked out ONCE at start-up (prepare_boxes), because they never change.
BOXES = [
    {"min": (-0.5, -1, -0.125), "max": (0.5, 2, 0.125), "colour": (255, 215, 0), "palette": PALETTE_GOLD},   # gold: on the gold square, 3 tall, 0.25 thick
    {"min": (1.5, -1, -0.125),  "max": (2.5, 2, 0.125), "colour": (255, 215, 0), "palette": PALETTE_GOLD},   # gold: to the RIGHT, 1 unit gap
    {"min": (-2.5, -1, -0.125), "max": (-1.5, 2, 0.125), "colour": (255, 215, 0), "palette": PALETTE_GOLD},  # gold: to the LEFT, 1 unit gap
]
CEILING_Y = 8                 # nothing flies higher than this
SHOW_PIECES = False           # TEST: True = every 1-unit floor piece gets its own colour

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

def face_distance_squared(face_camera_points):
    # How far a face's CENTRE is from your eye, squared. Used for the painter's sort.
    # The points are measured from YOU (camera space), so your eye is at (0, 0, 0)
    # and the distance is just the length of the centre point.
    #
    # Why not average_z?  average_z only measures "straight ahead". When you look level,
    # a face ABOVE another (the tank's barrel over its front slope) gets almost the same
    # number, so the sort is a coin toss and the slope can be painted over the barrel.
    # A straight-line distance also counts up / down and left / right, so the higher
    # barrel really does come out nearer when you're above it.
    #
    # Squared, because sqrt is slower and doesn't change the ORDER:
    #   if a is further than b, then a * a is bigger than b * b too.
    count = len(face_camera_points)
    centre_x = 0
    centre_y = 0
    centre_z = 0
    for x, y, z in face_camera_points:
        centre_x = (centre_x + x)
        centre_y = (centre_y + y)
        centre_z = (centre_z + z)
    centre_x = (centre_x / count)      # the average corner = the face's centre
    centre_y = (centre_y / count)
    centre_z = (centre_z / count)
    return (centre_x * centre_x) + (centre_y * centre_y) + (centre_z * centre_z)   # Pythagoras in 3D, without the sqrt

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
    point = (sx + pos_x, sy + pos_y, sz + pos_z)            # 3. place it (in the WORLD, or in its PARENT's model)
    if "parent" in thing:                                   # 4. a child: now carry it with its parent
        return to_world(point, thing["parent_thing"])       #    (size, spin and place it AGAIN, as the parent)
    return point


def turn_direction(direction, thing):
    # A direction (like a face's normal) only TURNS: no size, no move. Children turn with their parents too.
    turned = rotate_all(direction, thing["angles"])
    if "parent" in thing:
        return turn_direction(turned, thing["parent_thing"])
    return turned


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



def draw_collision_spheres():
    # Debug view: each collision sphere drawn as a thin white circle, on top of everything.
    for thing in things:
        for offset, radius in thing["model"]["collision_spheres"]:
            centre = to_camera(to_world(offset, thing))      # the same size -> spin -> place -> camera as a corner
            if centre[2] < NEAR:                             # behind you or too close: skip it
                continue
            # Further away = smaller, the same way project() shrinks x and y: multiply by FOCAL, divide by depth
            pixel_radius = (radius * thing["size"] * FOCAL) / centre[2]
            pygame.draw.circle(screen, (255, 255, 255), project(centre), max(1, round(pixel_radius)), 1)


def world_spheres(thing):
    # Each collision sphere as (world centre, world radius): moved with the thing like a corner, radius sized.
    spheres = []
    for offset, radius in thing["model"]["collision_spheres"]:
        spheres.append((to_world(offset, thing), radius * thing["size"]))
    return spheres


def prepare_boxes():
    # Once, at start-up: each box's 8 WORLD corners and its 6 shaded face colours. They never change.
    for box in BOXES:
        # The cube's corners are all -1 or +1: -1 -> the box's "min", +1 -> its "max", on each axis.
        # So the box uses the SAME corner order as cube_points, and the cube's faces fit it exactly.
        box["corners"] = [tuple(box["min"][axis] if point[axis] < 0 else box["max"][axis] for axis in range(3))
                          for point in cube_points]
        box["face_colours"] = []
        for face_number, (corners, normal) in enumerate(cube_faces):
            colour = box["palette"][face_number % len(box["palette"])]
            box["face_colours"].append(shade_colour(colour, normal))     # never turns, so the lighting never changes


def add_box_faces(face_paint_order):
    # Every frame: each box's visible faces go into the SAME paint list as the things' faces,
    # so boxes and things are sorted together (a tank in front of a box is painted after it).
    for box in BOXES:
        camera_points = [to_camera(corner) for corner in box["corners"]]       # only this part changes: YOU move
        screen_points = [project(point) if point[2] >= NEAR else None for point in camera_points]
        for face_number, (corners, normal) in enumerate(cube_faces):
            face_points = [screen_points[corner] for corner in corners]
            if None in face_points:
                continue                                                       # a corner behind you: skip the face
            if not is_facing_you(face_points):
                continue                                                       # turned away: skip it
            paint_depth = face_distance_squared([camera_points[corner] for corner in corners])
            face_paint_order.append((paint_depth, box["face_colours"][face_number], face_points, box["colour"]))


def bounce_things_off_boxes():
    # Moving things against BOXES. A box doesn't move, so it's like a wall: the thing bounces off the FACE
    # it hit, the same way things bounce off the world box (only that one direction flips).
    # A bullet that hits a box is used up instead: ping + sparks.
    for thing in things:
        if "parent" in thing:
            continue                                                    # children ride on their parents
        velocity = thing["velocity"]
        if velocity == [0, 0, 0] or thing.get("dead"):
            continue                                                    # parked, or destroyed this frame
        if thing.get("bullet") and thing["range"] <= 0:
            continue                                                    # already used up
        spheres = world_spheres(thing)
        for box in BOXES:
            # SPHERE vs BOX: the closest point IN the box to the sphere's centre = clamp the centre to the box.
            # If that closest point is nearer than the radius, the sphere is touching the box.
            hit = None
            for centre, radius in spheres:
                closest = [max(box["min"][axis], min(centre[axis], box["max"][axis])) for axis in range(3)]
                away = [centre[axis] - closest[axis] for axis in range(3)]     # from the box OUT to the centre
                if (away[0] * away[0]) + (away[1] * away[1]) + (away[2] * away[2]) < (radius * radius):
                    hit = (centre, radius, closest, away)
                    break                                               # first touching sphere wins
            if hit is None:
                continue
            centre, radius, closest, away = hit

            if thing.get("bullet"):                                     # a BULLET: used up, thud + sparks
                thing["range"] = 0
                if thing["owner"] is None:
                    crosshair["hit"] = CROSSHAIR_HIT_FRAMES             # your shot: show the hit marker
                if thud_sound:
                    thud_sound.play()                                   # boxes go THUD (dull), not ping
                spawn_sparks(closest, [box["colour"], (255, 255, 255)])
                break

            # Which FACE was hit? The axis where the centre sticks out of the box the most.
            if away == [0, 0, 0]:
                # The centre is INSIDE the box (something fast): push it out through the NEAREST face
                gaps = []
                for axis in range(3):
                    gaps.append((centre[axis] - box["min"][axis], axis, -1))    # distance to the min face: out = -1
                    gaps.append((box["max"][axis] - centre[axis], axis, 1))     # distance to the max face: out = +1
                gap, axis, out = min(gaps)
                push = gap + radius
            else:
                axis = max(range(3), key=lambda a: abs(away[a]))
                out = 1 if away[axis] > 0 else -1                      # which way is OUT of the box on that axis
                push = radius - abs(away[axis])                        # how far it's sunk in

            if (velocity[axis] * out) < 0:                              # moving INTO that face: bounce off it
                velocity[axis] = abs(velocity[axis]) * out
                if thud_sound:
                    thud_sound.play()                                   # boxes go THUD (dull), not bonk
                spawn_sparks(closest, [thing["colour"], box["colour"], (255, 255, 255)])
            thing["position"][axis] = thing["position"][axis] + (push * out)   # push it out: just touching


def bounce_things_off_each_other():
    # Every PAIR of things, checked once. If any sphere of one touches any sphere of the other,
    # and they're moving TOWARDS each other, both velocities are reversed.
    #   - Reversing both always sends them apart (their speed relative to each other is reversed).
    #   - A parked thing (velocity [0, 0, 0]) stays parked: reversing zero is still zero, so it acts like a wall.
    #   - Children (turrets, radars) are skipped: they ride on their parents.
    movers = [thing for thing in things if "parent" not in thing]
    all_spheres = [world_spheres(thing) for thing in movers]            # each thing's spheres, worked out ONCE
    for i in range(len(movers)):
        for j in range(i + 1, len(movers)):                             # j starts after i: each pair only once
            a, b = movers[i], movers[j]
            va, vb = a["velocity"], b["velocity"]
            if va == [0, 0, 0] and vb == [0, 0, 0]:
                continue                                                # both parked: nothing can happen
            if a.get("dead") or b.get("dead"):
                continue                                                # destroyed this frame: removed at the end
            if a.get("bullet") and b.get("bullet"):
                continue                                                # bullets pass through each other
            if a.get("owner") is b or b.get("owner") is a:
                continue                                                # a tank's bullet never hits its own tank
            if (a.get("bullet") and a["range"] <= 0) or (b.get("bullet") and b["range"] <= 0):
                continue                                                # a bullet that's already used up

            # First touch wins: stop at the first sphere of a that touches a sphere of b
            touching = False
            for centre_a, radius_a in all_spheres[i]:
                for centre_b, radius_b in all_spheres[j]:
                    dx = centre_b[0] - centre_a[0]                      # the line from a's sphere to b's
                    dy = centre_b[1] - centre_a[1]
                    dz = centre_b[2] - centre_a[2]
                    reach = radius_a + radius_b
                    if (dx * dx) + (dy * dy) + (dz * dz) < (reach * reach):   # squared: no sqrt needed
                        touching = True
                        # The IMPACT point: along the line from a's sphere to b's, where a's sphere ends
                        share = radius_a / reach                        # a's part of the gap (0 .. 1)
                        impact = (centre_a[0] + (dx * share), centre_a[1] + (dy * share), centre_a[2] + (dz * share))
                        break
                if touching:
                    break
            if not touching:
                continue                                                # not touching

            # A BULLET hit something: the bullet is used up, the target is left alone. Bonk + sparks.
            if a.get("bullet") or b.get("bullet"):
                bullet, target = (a, b) if a.get("bullet") else (b, a)
                bullet["range"] = 0                                     # removed at the end of this frame
                if bullet["owner"] is None and "health" in target:      # YOUR bullet: the target loses 1 health
                    target["health"] = max(0, target["health"] - 1)
                    if target["health"] == 0:
                        break_apart(target)                             # split in two, or die if it's down to 1
                crosshair["hit"] = CROSSHAIR_HIT_FRAMES                 # flash the red X on the crosshair
                if ping_sound:
                    ping_sound.play()                                   # PING
                spawn_sparks(impact, [target["colour"], (255, 255, 255), (255, 220, 120)])
                continue

            # Moving TOWARDS each other? (b's speed relative to a, along the line from a to b, is negative)
            # Without this, two things still overlapping next frame would flip back into each other.
            # The line is between the two THINGS' centres, not the touching spheres: a big sphere can touch
            # spheres on OPPOSITE sides of a frame's ring, so "which pair touched" can flip from frame to frame.
            dx = b["position"][0] - a["position"][0]
            dy = b["position"][1] - a["position"][1]
            dz = b["position"][2] - a["position"][2]
            closing = ((vb[0] - va[0]) * dx) + ((vb[1] - va[1]) * dy) + ((vb[2] - va[2]) * dz)
            if closing < 0:
                for axis in range(3):
                    va[axis] = -va[axis]                                # reverse both: now they move apart
                    vb[axis] = -vb[axis]
                if bump_sound:
                    bump_sound.play()                                   # BONK (overlapping bumps just play together)
                spawn_sparks(impact, [a["colour"], b["colour"], (255, 255, 255)])   # and a burst of sparks


def draw_crosshair():
    # A gap cross + centre dot, in the exact middle of the screen: where bullets go.
    # Everything is drawn TWICE: first thick and black (a shadow, so it shows on bright shapes), then thin on top.
    cx, cy = CENTRE_X, CENTRE_Y
    gap = CROSSHAIR_GAP + crosshair["kick"]                 # wider just after firing
    end = gap + CROSSHAIR_LENGTH
    arms = [((cx, cy - gap), (cx, cy - end)),               # up
            ((cx, cy + gap), (cx, cy + end)),               # down
            ((cx - gap, cy), (cx - end, cy)),               # left
            ((cx + gap, cy), (cx + end, cy))]               # right
    for colour, width in ((BLACK, 4), (CROSSHAIR_COLOUR, 2)):          # shadow first, then the arms
        for start, finish in arms:
            pygame.draw.line(screen, colour, start, finish, width)
    pygame.draw.circle(screen, BLACK, (cx, cy), 3)                    # the centre dot, with its shadow
    pygame.draw.circle(screen, CROSSHAIR_COLOUR, (cx, cy), 2)

    if crosshair["hit"] > 0:                                # HIT MARKER: a red X, shrinking as it fades
        reach = 6 + crosshair["hit"]                        # starts big, shrinks frame by frame
        for x_way, y_way in ((-1, -1), (1, -1), (-1, 1), (1, 1)):     # the X's four diagonal strokes
            inner = (cx + (x_way * 5), cy + (y_way * 5))
            outer = (cx + (x_way * reach), cy + (y_way * reach))
            pygame.draw.line(screen, BLACK, inner, outer, 4)
            pygame.draw.line(screen, HIT_MARKER_COLOUR, inner, outer, 2)

    # Settle back for next frame: the kick springs back (shrinks to 80% each frame), the hit marker counts down
    crosshair["kick"] = crosshair["kick"] * 0.8
    if crosshair["kick"] < 0.5:
        crosshair["kick"] = 0
    if crosshair["hit"] > 0:
        crosshair["hit"] = crosshair["hit"] - 1


def fire_bullet():
    # A new bullet THING: a tiny spinning cube, flying the way you're looking (turn AND tilt).
    # Your "forward" is (0, 0, 1) in front of your eye. to_camera() undoes your turn then your tilt,
    # so going the other way - tilt, then turn - gives "forward" in the WORLD.
    aim_x, aim_y, aim_z = rotate_y(rotate_x((0, 0, 1), cam_tip), cam_turn)
    start = 0.4                                   # start a little in front of your eye (closer is cut off by NEAR)
    crosshair["kick"] = CROSSHAIR_KICK            # the crosshair's arms jump out
    start_point = (cam_x + (aim_x * start), cam_y + (aim_y * start), cam_z + (aim_z * start))
    spawn_bullet(start_point, (aim_x, aim_y, aim_z), BULLET_SPEED, (255, 215, 0), PALETTE_GOLD, None)   # GOLD


def spawn_bullet(start, aim, speed, colour, palette, owner):
    # A new bullet THING. 'aim' must be length 1. 'owner' = the tank that fired it (None = you):
    # a bullet never hits its own owner, and only TANK bullets can hit you.
    things.append({"name": "bullet", "bullet": True, "model": cube_model, "owner": owner,
                   "position": [start[0], start[1], start[2]],                        # NEW lists
                   "velocity": [aim[0] * speed, aim[1] * speed, aim[2] * speed],      #   each time
                   "range": BULLET_RANGE,
                   "size": BULLET_SIZE, "angles": [0, 0, 0], "speeds": (12, 9, 0),    # spins fast as it flies
                   "colour": colour, "palette": palette})


def tanks_take_aim():
    # Every turret with a gun. When it's ready (cooled down) AND pointing at you (within TANK_CONE degrees,
    # judged flat - turrets only turn left / right), it starts a VOLLEY: TANK_VOLLEY shots, TANK_VOLLEY_GAP
    # frames apart, each one a perfect shot at your eye. Once a volley starts it's finished, even if the
    # turret turns away. THEN it cools down.
    guns = [thing for thing in things if thing.get("gun") and not thing["parent_thing"].get("dead")]   # (a separate
                                                                  #   list: spawn_bullet adds to things)
    for turret in guns:
        if turret["volley_left"] == 0:                            # not in the middle of a volley:
            if turret["cooldown"] > 0:
                turret["cooldown"] = turret["cooldown"] - 1       #   still cooling down
                continue
            if not turret_sees_you(turret):
                continue                                          #   ready, but not pointing at you
            turret["volley_left"] = TANK_VOLLEY                   #   ready AND sees you: start a volley...
            turret["volley_timer"] = 0                            #   ...with the first shot right now
        turret["volley_timer"] = turret["volley_timer"] - 1
        if turret["volley_timer"] > 0:
            continue                                              # waiting for the next shot in the volley
        fire_at_you(turret)
        turret["volley_left"] = turret["volley_left"] - 1
        turret["volley_timer"] = TANK_VOLLEY_GAP
        if turret["volley_left"] == 0:
            turret["cooldown"] = TANK_COOLDOWN                    # volley done: now cool down


def turret_sees_you(turret):
    # True if the turret points within TANK_CONE degrees of you (flat: turrets only turn left / right).
    pivot = to_world((0, 0, 0), turret)                           # the turret's centre, in the world
    forward = turn_direction((0, 0, 1), turret)                   # where its barrels point (hull turn + its own)
    to_you_x, to_you_z = (cam_x - pivot[0]), (cam_z - pivot[2])
    flat = math.sqrt((to_you_x * to_you_x) + (to_you_z * to_you_z))
    if flat == 0:
        return False                                              # you're standing exactly on it: no direction
    # cos(angle between "forward" and "toward you"), both flat: 1 = dead ahead. Compare cosines: no acos needed.
    return ((forward[0] * to_you_x) + (forward[2] * to_you_z)) / flat >= math.cos(math.radians(TANK_CONE))


def fire_at_you(turret):
    # One perfect shot: from the turret's next muzzle, aimed exactly at your eye in 3D (height too).
    muzzles = turret["model"]["muzzles"]
    muzzle = to_world(muzzles[turret["next_muzzle"]], turret)
    turret["next_muzzle"] = (turret["next_muzzle"] + 1) % len(muzzles)     # twin barrels take turns
    dx, dy, dz = (cam_x - muzzle[0]), (cam_y - muzzle[1]), (cam_z - muzzle[2])
    distance = math.sqrt((dx * dx) + (dy * dy) + (dz * dz))
    spawn_bullet(muzzle, (dx / distance, dy / distance, dz / distance), TANK_BULLET_SPEED,
                 TANK_BULLET_COLOUR, PALETTE_TANK_BULLET, turret["parent_thing"])


def break_apart(thing):
    # A shape at 0 health. It's marked "dead" (removed at the end of the frame) with a big burst of sparks.
    # If it had more than 1 health to start with, two smaller pieces of the SAME model take its place:
    # SPLIT_SIZE of its size, half its max health (rounded down), pushed apart. 1-health shapes just die.
    # Tanks don't split (their turret and radar would need copying too): they just die, children and all.
    thing["dead"] = True
    for burst in range(3):                                         # a bigger burst than a normal hit
        spawn_sparks(thing["position"], [thing["colour"], (255, 255, 255), (255, 220, 120)])
    if bump_sound:
        bump_sound.play()
    has_children = any(other.get("parent_thing") is thing for other in things)
    if thing["max_health"] <= 1 or has_children:
        return                                                     # too small (or a tank): it just dies

    # A random direction to push the pieces apart (any direction, then made length 1)
    push = (random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))
    length = math.sqrt((push[0] * push[0]) + (push[1] * push[1]) + (push[2] * push[2])) or 1
    push = (push[0] / length, push[1] / length, push[2] / length)
    piece_reach = thing["reach"] * SPLIT_SIZE
    for side in (1, -1):                                           # one piece each way
        piece = dict(thing)                                        # a COPY of the shape's settings...
        del piece["dead"]
        piece["name"] = thing["name"] + " piece"
        piece["size"] = thing["size"] * SPLIT_SIZE
        piece["reach"] = piece_reach
        piece["max_health"] = thing["max_health"] // 2             # half, rounded down: 10 -> 5 -> 2 -> 1
        piece["health"] = piece["max_health"]
        # ...but NEW lists for what changes every frame, or the two pieces would share (and move) one list
        piece["position"] = [thing["position"][axis] + (push[axis] * piece_reach * side) for axis in range(3)]
        piece["velocity"] = [thing["velocity"][axis] + (push[axis] * SPLIT_KICK * side) for axis in range(3)]
        piece["angles"] = list(thing["angles"])
        things.append(piece)


def draw_health():
    # A row of tiny squares floating just above each shape: filled green = health left, grey outline = lost.
    # The squares are a fixed size on screen (not shrunk by distance), so they stay readable far away.
    for thing in things:
        if "health" not in thing:
            continue                                          # children and bullets have no health
        x, y, z = thing["position"]
        above = to_camera((x, y + thing["reach"] + 0.3, z))  # a point just above the top of the shape
        if above[2] < NEAR:
            continue                                          # behind you: skip it
        centre_x, centre_y = project(above)
        step = HEALTH_SQUARE + HEALTH_GAP
        left = centre_x - ((thing["max_health"] * step) - HEALTH_GAP) / 2      # centre the row over the shape
        for n in range(thing["max_health"]):
            square = pygame.Rect(round(left + (n * step)), round(centre_y), HEALTH_SQUARE, HEALTH_SQUARE)
            if n < thing["health"]:
                pygame.draw.rect(screen, (60, 255, 60), square)               # health left: filled green
            else:
                pygame.draw.rect(screen, (110, 110, 110), square, 1)          # health lost: grey outline


def spawn_sparks(point, colours):
    # SPARK_COUNT sparks at one point, each flying off in a random direction at a random speed.
    for n in range(SPARK_COUNT):
        direction = (random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))
        speed = random.uniform(0.3, 1) * SPARK_SPEED
        particles.append({"position": list(point),                                   # a LIST: it changes every frame
                          "velocity": [direction[0] * speed, (direction[1] * speed) + 0.02, direction[2] * speed],   # + a little upward kick
                          "life": random.randint(SPARK_LIFE // 2, SPARK_LIFE),        # not all die at the same moment
                          "colour": random.choice(colours)})


def update_sparks():
    # Move every spark, pull it down a little, and age it. Dead sparks (and any that hit the floor) are removed.
    for spark in particles[:]:                     # [:] = loop over a COPY, so removing from the real list is safe
        spark["velocity"][1] = spark["velocity"][1] - SPARK_GRAVITY
        for axis in range(3):
            spark["position"][axis] = spark["position"][axis] + spark["velocity"][axis]
        spark["life"] = spark["life"] - 1
        if spark["life"] <= 0 or spark["position"][1] < FLOOR_Y:
            particles.remove(spark)


def draw_sparks():
    # Each spark is a small dot, smaller when further away, and shrinking as it dies.
    # Drawn on top of the shapes (no depth sorting): sparks are quick and bright, so it doesn't show.
    for spark in particles:
        camera_point = to_camera(spark["position"])
        if camera_point[2] < NEAR:                 # behind you or too close: skip it
            continue
        size_now = SPARK_SIZE * (spark["life"] / SPARK_LIFE)                 # shrinks as it dies
        pixel_radius = (size_now * FOCAL) / camera_point[2]                  # further away = smaller
        pygame.draw.circle(screen, spark["colour"], project(camera_point), max(1, round(pixel_radius)))


def draw_floor_shapes():
    # Flat shapes painted on the floor: drawn straight after the grid, before any thing, so they never cover one.
    for corners, colour in FLOOR_SHAPES:
        screen_corners = []
        for x, z in corners:
            camera_point = to_camera((x, FLOOR_Y, z))       # a floor corner, measured from YOU
            if camera_point[2] < NEAR:                      # a corner behind you: skip this shape (no trimming)
                break
            screen_corners.append(project(camera_point))
        if len(screen_corners) == len(corners):             # only draw it if EVERY corner made it
            pygame.draw.polygon(screen, colour, screen_corners)


def draw_floor():
    for z in range(GRID_BACK, GRID_FAR + 1):          # lines ACROSS: one at every z
        for x in range(GRID_LEFT, GRID_RIGHT):        #   cut into pieces: x to x + 1
            draw_floor_line((x, FLOOR_Y, z), (x + 1, FLOOR_Y, z))
    for x in range(GRID_LEFT, GRID_RIGHT + 1):        # lines AWAY: one at every x
        for z in range(GRID_BACK, GRID_FAR):          #   cut into pieces: z to z + 1
            draw_floor_line((x, FLOOR_Y, z), (x, FLOOR_Y, z + 1))





prepare_boxes()                      # boxes never move: work out their corners and colours ONCE

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
        if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
            show_spheres = not show_spheres               # flip: on -> off, off -> on (once per press)
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            volume["slider"] = max(0.0, round(volume["slider"] - 0.1, 1))     # quieter (never below 0%)
            apply_volume()
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_EQUALS, pygame.K_KP_PLUS):
            volume["slider"] = min(1.0, round(volume["slider"] + 0.1, 1))     # louder (never above 100%)
            apply_volume()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            fire_bullet()                                 # left click: FIRE (one bullet per click)
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
        if "parent" in thing:                                   # a child rides on its parent: its position is
            continue                                            #   RELATIVE, so never move or bounce it here
        position = thing["position"]
        velocity = thing["velocity"]
        if thing.get("bullet"):                                 # BULLETS: fly straight, never bounce off the walls
            for axis in range(3):
                position[axis] = position[axis] + velocity[axis]
            thing["range"] = thing["range"] - BULLET_SPEED      # used up a little more of its range
            for axis in range(3):                               # left the WORLD BOX (floor, ceiling, walls)? done.
                # Only if it's still heading OUT, and BULLET_MARGIN past the edge: you can stand just outside
                # the box, so your shots must fly in, and tank shots must still reach you.
                if position[axis] < (WORLD_MIN[axis] - BULLET_MARGIN) and velocity[axis] < 0:
                    thing["range"] = 0
                if position[axis] > (WORLD_MAX[axis] + BULLET_MARGIN) and velocity[axis] > 0:
                    thing["range"] = 0
            if thing["owner"] is not None:                      # a TANK's bullet: has it hit YOU?
                dx, dy, dz = (cam_x - position[0]), (cam_y - position[1]), (cam_z - position[2])
                if (dx * dx) + (dy * dy) + (dz * dz) < (YOUR_HIT_RADIUS * YOUR_HIT_RADIUS):
                    thing["range"] = 0
                    you["hits_taken"] = you["hits_taken"] + 1
                    you["hurt"] = 12                            # frames of red flash round the screen
                    if hurt_sound:
                        hurt_sound.play()                       # a sad "wahhh"
            continue
        smallest, biggest = WORLD_MIN, WORLD_MAX
        for axis in range(3):                                   # 0 = x, 1 = y, 2 = z
            position[axis] = position[axis] + velocity[axis]
            if position[axis] > biggest[axis]:                  # past the top end:
                velocity[axis] = -abs(velocity[axis])           #   head DOWN this axis
            if position[axis] < smallest[axis]:                 # past the bottom end:
                velocity[axis] = abs(velocity[axis])            #   head UP this axis

        # Steering things (like the tanks) point the way they're moving.
        # Done AFTER the bounce, so a tank flips round the moment it bounces (a "snap").
        if thing.get("faces_movement"):                         # .get: things without the flag just keep spinning
            vx, vz = velocity[0], velocity[2]                   # only the flat (x, z) part: no tilting up or down
            if vx != 0 or vz != 0:                              # standing still: keep the angle it already has
                # rotate_y points a model's front (+z) along (-sin a, cos a), so a = atan2(-vx, vz)
                thing["angles"][0] = math.degrees(math.atan2(-vx, vz))

    bounce_things_off_each_other()                  # after moving: things that touch bounce apart
    bounce_things_off_boxes()                       # ...and things that hit a box bounce off it
    update_sparks()                                 # move, drop and age the sparks
    tanks_take_aim()                                # turrets pointing at you fire (after their cooldown)
    # Remove used-up bullets (out of range, hit the floor, or hit something). [:] changes the list itself,
    # rather than making a new list called things, and doing it HERE means we're not looping over things.
    things[:] = [thing for thing in things if not (thing.get("bullet") and thing["range"] <= 0)
                 and not thing.get("dead")                                             # destroyed shapes...
                 and not ("parent_thing" in thing and thing["parent_thing"].get("dead"))]   # ...and their children

    screen.fill(BLACK)

    draw_floor()                                   # the whole grid, before any shape
    draw_floor_shapes()                            # then the flat shapes ON the floor, still before any shape



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

                    # The normal spins WITH its thing (and with its parent, if it has one), but is never sized or moved.
                    turned_normal = turn_direction(normal, thing)

                    # Pick this face's colour from the thing's palette, in order.
                    # % (remainder) wraps round when the palette is shorter than the faces list:
                    #   6 faces, 4 colours -> face 4 uses colour (4 % 4) = 0, face 5 uses (5 % 4) = 1
                    colour = palette[face_number % len(palette)]

                    colour = shade_colour(colour, turned_normal)

                    # OLD: sort by average depth straight ahead. Kept for comparison; swap the comments to go back.
                    # paint_depth = average_z(face_world_points)
                    # NEW: sort by straight-line distance from your eye (squared) - see face_distance_squared
                    paint_depth = face_distance_squared(face_world_points)
                    face_paint_order.append((paint_depth, colour, face_points, thing["colour"]))

        else:

            for a, b in model["edges"]:
                if screen_points[a] is None or screen_points[b] is None:
                    continue                                 # an end too close or behind you
                pygame.draw.line(screen, thing["colour"], screen_points[a], screen_points[b], 2)

    add_box_faces(face_paint_order)                    # the boxes' faces join the same paint list

    # ---- The painter's sort: ALL faces together, furthest from YOU first ----
    face_paint_order.sort(reverse=True)      # biggest number (furthest) first, nearest last: works for BOTH methods
    for paint_depth, colour, face_points, outline_colour in face_paint_order:
        pygame.draw.polygon(screen, colour, face_points)               # filled
        pygame.draw.polygon(screen, outline_colour, face_points, 1)    # outline: 1 pixel

    draw_sparks()                                      # sparks on top of the shapes
    draw_health()                                      # health squares above the shapes

    if show_spheres:                                   # C key: collision spheres on top of the shapes
        draw_collision_spheres()

## MINI MAP
    map_box = pygame.Rect(MAP_LEFT, MAP_BOX_TOP, MAP_SIZE, MAP_BOX_HEIGHT)
    screen.blit(map_background, (MAP_LEFT, MAP_BOX_TOP))        # 50% see-through background: the 3D view shows through

    for corners, colour in FLOOR_SHAPES:                                     # floor shapes, seen from above:
        pygame.draw.polygon(screen, colour, [to_map(x, z) for x, z in corners])   #   under everything else on the map
    for box in BOXES:                                                        # boxes, seen from above: rectangles
        (low_x, low_y, low_z), (high_x, high_y, high_z) = box["min"], box["max"]
        pygame.draw.polygon(screen, box["colour"], [to_map(low_x, low_z), to_map(high_x, low_z),
                                                    to_map(high_x, high_z), to_map(low_x, high_z)])
    pygame.draw.rect(screen, (255, 255, 255), map_box, 1)       # thin white border



    for thing in things:                                          # each thing = its collision spheres, seen from above
        for offset, radius in thing["model"]["collision_spheres"]:
            sphere_x, sphere_y, sphere_z = to_world(offset, thing)       # the sphere's centre in the WORLD
            map_radius = radius * thing["size"] * MAP_SCALE              # world units -> map pixels
            pygame.draw.circle(screen, thing["colour"], to_map(sphere_x, sphere_z), max(1, round(map_radius)))   # no width = filled
    
    pygame.draw.circle(screen, PINK, to_map(cam_x, cam_z), 5)   # pink dot = YOU

    face_x, face_y, face_z = rotate_y((0, 0, 1), cam_turn)            # your "forward" arrow
    nose = to_map(cam_x + (face_x * 1.5), cam_z + (face_z * 1.5))     # 1.5 units in front of you
    pygame.draw.line(screen, PINK, to_map(cam_x, cam_z), nose, 2)

## MINNI MAP 


    draw_crosshair()                                   # the crosshair, on top of everything in the 3D view

    # FPS counter, top-left corner
    fps_text = fps_font.render("FPS: " + str(round(clock.get_fps())), True, GREEN)
    screen.blit(fps_text, (10, 10))

    # Facing, just under the FPS: compass style, 0 = up the map (+z), counting up as you turn RIGHT.
    # cam_turn goes DOWN when you turn right, so flip its sign; % 360 wraps it into 0..359.
    heading = round(-cam_turn) % 360
    heading_text = fps_font.render("Facing: " + str(heading) + "°", True, GREEN)
    screen.blit(heading_text, (10, 40))

    # Camera tilt, under that: 0 = level, + = looking UP, - = looking down.
    # cam_tip is + when looking DOWN, so flip its sign.
    tilt = round(-cam_tip)
    tilt_text = fps_font.render("Tilt: " + str(tilt) + "°", True, GREEN)
    screen.blit(tilt_text, (10, 70))

    # Where you stand in the WORLD (cam_x, cam_y, cam_z), rounded to 1 decimal place.
    position_text = fps_font.render("World x, y, z: " + str(round(cam_x, 1)) + ", " + str(round(cam_y, 1)) + ", " + str(round(cam_z, 1)), True, GREEN)
    screen.blit(position_text, (10, 100))

    # Hits from the tanks, and a red flash round the screen edge for a moment after each one
    hits_text = fps_font.render("Hits taken: " + str(you["hits_taken"]), True, (255, 80, 80))
    screen.blit(hits_text, (10, 130))

    # VOLUME slider: a bar that fills up to the slider's position, with the % beside it ( - and = to change )
    volume_text = fps_font.render("Volume", True, GREEN)
    screen.blit(volume_text, (10, 160))
    bar = pygame.Rect(100, 164, 150, 16)                                   # the slider's track
    pygame.draw.rect(screen, GREEN, (bar.x, bar.y, bar.width * volume["slider"], bar.height))   # filled part
    pygame.draw.rect(screen, GREEN, bar, 1)                                # outline
    percent_text = fps_font.render(str(round(volume["slider"] * 100)) + "%  (- =)", True, GREEN)
    screen.blit(percent_text, (bar.right + 10, 160))
    if you["hurt"] > 0:
        pygame.draw.rect(screen, (255, 0, 0), screen.get_rect(), 12)    # a thick red border: 12 pixels wide
        you["hurt"] = you["hurt"] - 1

    pygame.display.flip()
    clock.tick(60)

pygame.quit()