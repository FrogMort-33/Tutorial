# rotation_functions.py - HOW the world works for rotation_301: maths, drawing, collisions, sounds.
# The data lives in rotation_data.py; the game loop that calls all of this is in rotation_301.py.
# Importing this file opens the game window (everything here needs the screen's size).
import array
import math
import random
import pygame
from rotation_data import *
from rotation_levels import DESIGNS, LEVELS

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
clock = pygame.time.Clock()
fps_font = pygame.font.SysFont(None, 32)   # default font, size 32, for the FPS counter
title_font = pygame.font.SysFont(None, 80)  # the level's name, big, as the level starts
intro_font = pygame.font.SysFont(None, 36)  # the level's intro line, under the name


# ================================ SOUND ================================
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
freeze_sound = make_sound(2600, 2200, 0.35, 5000, 1.5)   # "ting": very high and glassy - ice FREEZES you
ALL_SOUNDS = [bump_sound, ping_sound, hurt_sound, thud_sound, freeze_sound]   # every sound, so the volume reaches them all

# ---- VOLUME: one slider for every sound. Keys: - quieter, = louder (10% steps) ----
# Our ears hear loudness on a CURVE, not a straight line: half the strength does NOT sound half as loud.
# So the slider is SQUARED before it's used: 50% on the slider = 0.25 strength, which SOUNDS about half as loud,
# and every step on the slider feels about the same size.
# (the slider itself, volume["slider"], lives in rotation_data.py)


def apply_volume():
    # Set every sound's strength from the slider (squared: see above). Call it whenever the slider changes.
    strength = volume["slider"] * volume["slider"]
    for sound in ALL_SOUNDS:
        if sound:                                   # a sound is None if there's no sound device
            sound.set_volume(strength)


apply_volume()                                      # start at 20%


# ================================ SCREEN ================================
CENTRE_X = (WIDTH / 2)
CENTRE_Y = (HEIGHT / 2)
FOCAL = WIDTH / 2   # 90 degree horizontal view on any screen

## MINI MAP !!
MAP_SIZE = HEIGHT/3 *0.50                        # the map is a 160 x 160 pixel square
MAP_PADDING = 1.3                      # the DRAWN box is this much wider than MAP_SIZE: padding left and right
MAP_BOX_WIDTH = (MAP_SIZE * MAP_PADDING)   # (the level is still fitted to MAP_SIZE, so the play area keeps its size)
MAP_LEFT = (WIDTH - 10 - MAP_BOX_WIDTH)    # its left edge: the box ends 10 px in from the right of the screen
MAP_TOP = (HEIGHT - 10 - (MAP_SIZE * 0.25) - MAP_SIZE)     # its top edge: raised 25% of MAP_SIZE above the old 10 px margin
MAP_COLOUR_BACK = (25, 30, 36)         # dark grey-blue, so the map stands out from the black
MAP_BOX_HEIGHT = (MAP_SIZE * 1.25 * 1.33)     # the DRAWN box is 25% taller than wide, then 33% taller again ...
MAP_BOX_TOP = (HEIGHT - 10 - (MAP_SIZE * 0.25) - MAP_BOX_HEIGHT)   # ... and grows UPWARDS (raised by the same 25% as MAP_TOP)
                                       # (MAP_TOP is still used to place WORLD (0, 0), so nothing on the map moves)
# A see-through card the size of the map box. SRCALPHA = this surface has its own alpha (see-through-ness).
map_background = pygame.Surface((MAP_BOX_WIDTH, MAP_BOX_HEIGHT), pygame.SRCALPHA)
map_background.fill(MAP_COLOUR_BACK + (128,))   # alpha 128: 0 = invisible, 255 = solid, 128 = about 50%

# YOU on the map: a gold dot, and two gold lines showing the EDGES of your view (what's on screen is between
# them). Half the view's width comes from the screen and FOCAL: the screen's edge is (WIDTH / 2) pixels from
# the middle, and project() puts a point 45 degrees to the side exactly there when FOCAL = WIDTH / 2 -
# so the view is 45 degrees each side (90 wide).
PLAYER_MAP_COLOUR = (255, 215, 0)   # gold
VIEW_HALF_ANGLE = math.degrees(math.atan((WIDTH / 2) / FOCAL))
VIEW_CONE_LENGTH = 5                # world units: how far the two view lines reach on the map
VIEW_ARC_POINTS = 12                # each arc is drawn as this many short straight pieces (more = smoother)
# RADAR PINGS: arcs that travel OUTWARDS across your view, from you out to VIEW_PING_REACH, then start again.
# They fade as they near the end of their trip, so they die away rather than vanish.
VIEW_PING_REACH = 10                # world units: how far out the pings travel (further than the view lines)
VIEW_PINGS = 2                      # how many pings at once (spread evenly: 2 = one halfway behind the other)
VIEW_PING_FRAMES = 100              # frames for one ping to travel all the way out (100 = 1.7 s at 60 FPS)
VIEW_PING_TRAIL = [(0, 255),        # each ping is drawn as these arcs: (how far BEHIND it, in world units, how solid):
                   (0.35, 140),     #   the ping itself, solid; then a trail of two arcs behind it, each fainter
                   (0.7, 60)]       #   (255 = solid, 0 = invisible)
view_arc_timer = {"frame": 0}       # counts frames for the animation (a dictionary: functions can change it)
# Their own see-through layer, the size of the map box (drawing on it can't spill outside the map)
view_cone_layer = pygame.Surface((MAP_BOX_WIDTH, MAP_BOX_HEIGHT), pygame.SRCALPHA)

# Where WORLD (0, 0) lands on the map, and map pixels per world unit. These starting values are replaced
# by fit_mini_map() whenever a level loads, so the WHOLE level's floor fits the map box.
MAP_CX = (MAP_LEFT + (MAP_BOX_WIDTH / 2))   # WORLD x = 0 goes across the middle of the box
MAP_CY = (MAP_TOP + (MAP_SIZE * 0.8))   # 80% of the way down the box
MAP_SCALE = (MAP_SIZE / 16)             # 16 world units across the box
MAP_MARGIN = 0.95                       # the level fills 95% of the box, leaving a thin edge


def fit_mini_map():
    # Make the level's whole floor (the world box's x and z) fit the map box, centred, at the same scale
    # both ways (so squares stay square). Called by load_level().
    # 'global': these three names belong to THIS file, and to_map() reads them from here.
    global MAP_CX, MAP_CY, MAP_SCALE
    width = WORLD_MAX[0] - WORLD_MIN[0]                     # the level's size in x ...
    depth = WORLD_MAX[2] - WORLD_MIN[2]                     # ... and in z (up the map)
    MAP_SCALE = min(MAP_SIZE / width, MAP_BOX_HEIGHT / depth) * MAP_MARGIN   # whichever way is tighter
    level_centre_x = (WORLD_MIN[0] + WORLD_MAX[0]) / 2
    level_centre_z = (WORLD_MIN[2] + WORLD_MAX[2]) / 2
    box_centre_x = MAP_LEFT + (MAP_BOX_WIDTH / 2)
    box_centre_y = MAP_BOX_TOP + (MAP_BOX_HEIGHT / 2)
    MAP_CX = box_centre_x - (level_centre_x * MAP_SCALE)    # so the level's centre lands on the box's centre
    MAP_CY = box_centre_y + (level_centre_z * MAP_SCALE)    #   (+: the map's y goes DOWN as z goes up)


# ================================ LEVELS ================================
def load_level(number):
    # Build level 'number' from rotation_levels.py: its world box, its floor shapes and boxes, where you
    # start, and fresh things from its "spawn" list. Everything is COPIED, so the level data never changes
    # and loading a level again always starts it fresh.
    # Shared lists are refilled IN PLACE ([:] = ...), so every file that imported them sees the new contents.
    level = LEVELS[number]

    WORLD_MIN[:] = list(level["world"]["min"])            # the world box: things bounce inside it
    WORLD_MAX[:] = list(level["world"]["max"])
    if WORLD_MIN[1] != FLOOR_Y:
        print("load_level", number, "- warning: the world's min y should be FLOOR_Y", FLOOR_Y)

    # This level's SIZES: a copy of the main table, with the level's own changes on top
    level_sizes.clear()
    for size_name, values in SIZES.items():
        level_sizes[size_name] = dict(values)
    for size_name, changes in level.get("sizes", {}).items():
        level_sizes[size_name].update(changes)

    FLOOR_SHAPES[:] = [make_decal(entry, number) for entry in level["floor_shapes"]]
    BOXES[:] = [dict(box) for box in level["boxes"]]      # copies: prepare_boxes() adds to each one
    particles[:] = []                                     # no sparks left over
    camera.update(level["start"])                         # where you begin
    camera["vy"] = 0
    you["hits_taken"] = 0
    you["hurt"] = 0
    you["lava_timer"] = 0
    you["frozen"] = 0
    you["freeze_grace"] = 0
    level_progress["number"] = number                     # which level this is, and it's not cleared yet
    level_progress["cleared_frames"] = None
    level_banner["name"] = level.get("name", "")          # the title shown as the level starts
    level_banner["intro"] = level.get("intro", "")
    level_banner["frame"] = 0
    crosshair["kick"] = 0
    crosshair["hit"] = 0

    # THINGS: every spawn first (in order), THEN their children - all the first children (turrets),
    # then all the second children (radars) - so the top-level things come first in the list.
    things[:] = []
    parents = []
    for spawn in level["spawn"]:
        for needed in ("colour", "palette"):              # every spawn must set its own: the designs are GREY
            if needed not in spawn:
                print("level", number, "- warning:", spawn.get("name", spawn["design"]),
                      "has no", '"' + needed + '"', "of its own: it will be GREY")
        # "gun" and "radar_spin" are for the tank's CHILDREN (turret, radar), not the hull itself
        hull_changes = {key: value for key, value in spawn.items() if key not in ("gun", "radar_spin")}
        thing = build_thing(DESIGNS[spawn["design"]], hull_changes)
        if isinstance(thing["size"], str):                # a NAMED size ("MEDIUM"): its scale and health
            apply_size_name(thing, thing["size"])
        elif "health" in spawn:                           # a NUMBER size with its own health: keep it
            thing["fixed_health"] = spawn["health"]
        things.append(thing)
        design_children = DESIGNS[spawn["design"]].get("children", [])
        parents.append((thing, design_children, spawn.get("children", []), spawn))
    most_children = max([len(design_children) for thing, design_children, changes, spawn in parents] + [0])
    for slot in range(most_children):
        for parent, design_children, changes, spawn in parents:
            if slot >= len(design_children):
                continue
            change = changes[slot] if slot < len(changes) else {}
            child = build_thing(design_children[slot], change)
            child["name"] = parent["name"] + " " + design_children[slot]["part"]
            child["parent"] = parent["name"]
            child["parent_thing"] = parent                # connected directly: no looking up by name
            child.setdefault("colour", parent["colour"])
            child.setdefault("palette", parent["palette"])
            if design_children[slot]["part"] == "radar" and "radar_spin" in spawn:
                child["speeds"] = (spawn["radar_spin"], 0, 0)       # the level's "radar_spin"
            if child.get("gun"):
                setup_gun(child, spawn.get("gun", {}), number)
            things.append(child)

    prepare_boxes()                                       # the boxes' corners and colours
    prepare_health()                                      # every shape's health, from its size
    fit_mini_map()                                        # the whole level fits the mini-map
    check_level(number)


def make_decal(entry, level_number):
    # One of a level's "floor_shapes" -> a DECAL: {"type", "corners", "colour", "hurts", "glow"}.
    #   the old style: (corners, colour)                         -> "paint"
    #   the new style: {"type": "lava", "min": (x, z), "max": (x, z)}   (a rectangle) or "corners": [...]
    if not isinstance(entry, dict):
        corners, colour = entry
        entry = {"type": "paint", "corners": corners, "colour": colour}
    decal_type = entry.get("type", "paint")
    if decal_type not in DECAL_TYPES:
        print("level", level_number, "- warning: unknown decal type", decal_type, "- using paint")
        decal_type = "paint"
    kind = DECAL_TYPES[decal_type]
    if "min" in entry:                                    # a rectangle, from two opposite corners (x, z)
        (low_x, low_z), (high_x, high_z) = entry["min"], entry["max"]
        corners = [(low_x, low_z), (high_x, low_z), (high_x, high_z), (low_x, high_z)]
    else:
        corners = entry["corners"]
    colour = entry.get("colour") or kind["colour"]
    if colour is None:
        print("level", level_number, "- warning: a", decal_type, "decal has no colour: it will be GREY")
        colour = GREY
    return {"type": decal_type, "corners": list(corners), "colour": colour,
            "hurts": kind["hurts"], "glow": kind["glow"], "freezes": kind["freezes"]}


def point_in_polygon(x, z, corners):
    # Is the point (x, z) inside the shape? Imagine a line from the point going off to the right (+x):
    # count how many of the shape's edges it crosses. Odd = inside, even = outside. Works for any shape.
    inside = False
    for n in range(len(corners)):
        (x1, z1), (x2, z2) = corners[n], corners[(n + 1) % len(corners)]
        if (z1 > z) != (z2 > z):                          # this edge goes past the point's z ...
            crossing_x = x1 + ((z - z1) * (x2 - x1) / (z2 - z1))
            if crossing_x > x:                            # ... to the RIGHT of the point: it crosses our line
                inside = not inside
    return inside


def update_floor_hazards():
    # Once per frame: are YOU standing (feet on the floor - so jumping over is safe) on a decal that DOES something?
    #   ICE (freezes): you're frozen for FREEZE_FRAMES, then FREEZE_GRACE frames when it can't freeze you again
    #   LAVA (hurts):  one hit as you step in, then one every LAVA_HURT_FRAMES frames while you stay
    on_floor = camera["y"] <= STAND_Y + 0.001
    if you["frozen"] > 0:                                 # frozen: count down; when it ends, the grace starts
        you["frozen"] = you["frozen"] - 1
        if you["frozen"] == 0:
            you["freeze_grace"] = FREEZE_GRACE
    elif you["freeze_grace"] > 0:
        you["freeze_grace"] = you["freeze_grace"] - 1
    elif on_floor and any(decal["freezes"] and point_in_polygon(camera["x"], camera["z"], decal["corners"])
                          for decal in FLOOR_SHAPES):
        you["frozen"] = FREEZE_FRAMES                     # FROZEN!
        if freeze_sound:
            freeze_sound.play()
    in_lava = on_floor and any(decal["hurts"] and point_in_polygon(camera["x"], camera["z"], decal["corners"])
                               for decal in FLOOR_SHAPES)
    if not in_lava:
        you["lava_timer"] = 0                             # out of it: next time it hurts straight away
        return
    if you["lava_timer"] > 0:
        you["lava_timer"] = you["lava_timer"] - 1
        return
    you["hits_taken"] = you["hits_taken"] + 1             # OUCH: counts like a tank hit
    you["hurt"] = 12                                      # the red flash round the screen
    if hurt_sound:
        hurt_sound.play()
    you["lava_timer"] = LAVA_HURT_FRAMES


def setup_gun(turret, changes, level_number):
    # A turret's gun: GUN_DEFAULTS, with the level's "gun": {...} changes on top. Its counters start at 0.
    config = dict(GUN_DEFAULTS)
    config.update(changes)
    if config["mode"] not in GUN_MODES:
        print("level", level_number, "- warning:", turret["name"], "has gun mode", config["mode"],
              "- it should be one of", GUN_MODES, ": using SPIN")
        config["mode"] = "SPIN"
    if config["mode"] == "SPIN":
        if config["turret_spin"] is not None:
            turret["speeds"] = (config["turret_spin"], 0, 0)       # spins this fast, all the way round
    else:
        turret["speeds"] = (0, 0, 0)                  # OSCILLATE and TRACK turn the turret themselves (aim_turret)
        if config["turret_spin"] is None:
            config["turret_spin"] = 1                 # degrees per frame, if the level didn't say
        if config["mode"] == "OSCILLATE":
            turret["angles"][0] = config["centre"]    # start in the middle of its sweep
    if config.get("start_angle") == "you":            # start pointing straight at where YOU start the level
        pivot = to_world((0, 0, 0), turret)           #   (the camera is already at the level's start here)
        towards_you = math.degrees(math.atan2(-(camera["x"] - pivot[0]), camera["z"] - pivot[2]))
        turret["angles"][0] = keep_under_360(towards_you - turret["parent_thing"]["angles"][0])   # relative to hull
    elif config.get("start_angle") is not None:       # or a number: degrees relative to the hull's front
        turret["angles"][0] = config["start_angle"]
    turret["gun_config"] = config
    turret["sweep_direction"] = 1                     # OSCILLATE: +1 or -1, the way it's sweeping
    turret.update({"cooldown": 0, "next_muzzle": 0, "volley_left": 0, "volley_timer": 0})


def build_thing(design, changes):
    # A NEW thing: the design's fields, then the changes on top. Fresh lists for whatever changes every frame,
    # so no two things (and no level data) ever share a list.
    thing = {"velocity": [0, 0, 0], "size": 1, "angles": [0, 0, 0], "speeds": (0, 0, 0)}    # the defaults
    for key, value in list(design.items()) + list(changes.items()):
        if key not in ("design", "children", "part"):
            thing[key] = value
    for key in ("position", "velocity", "angles"):
        thing[key] = list(thing[key])
    return thing


def check_level(number):
    # Warnings for the level designer (printed, the game still runs): a thing whose centre starts
    # outside the world box, or whose spheres start inside a box.
    for thing in things:
        if "parent" in thing:
            continue
        if any(not (WORLD_MIN[axis] <= thing["position"][axis] <= WORLD_MAX[axis]) for axis in range(3)):
            print("level", number, "- warning:", thing["name"], "starts outside the world box")
        for centre, radius in world_spheres(thing):
            for box in BOXES:
                if all(box["min"][axis] - radius < centre[axis] < box["max"][axis] + radius for axis in range(3)):
                    print("level", number, "- warning:", thing["name"], "starts touching a box")


# ================================ START-UP ================================
def model_across(model):
    # How wide a model is at size 1: its biggest stretch along x, y or z (the cube: -1 to 1 = 2).
    return max(max(point[axis] for point in model["points"]) - min(point[axis] for point in model["points"])
               for axis in range(3))


def apply_size_name(thing, size_name):
    # A NAMED size ("MEDIUM") -> the thing's scale and its health, from this level's sizes.
    size = level_sizes[size_name]
    thing["size_name"] = size_name
    thing["size"] = size["across"] / model_across(thing["model"])     # e.g. 1.5 across / a 2-wide cube = 0.75
    thing["max_health"] = size["health"]
    thing["health"] = size["health"]


def thing_reach(thing):
    # REACH = how far its shape sticks out from its centre: its furthest collision sphere edge, times its size.
    reach = 0
    for (ox, oy, oz), radius in thing["model"]["collision_spheres"]:
        reach = max(reach, math.sqrt((ox * ox) + (oy * oy) + (oz * oz)) + radius)
    return reach * thing["size"]


def prepare_health():
    # Once, when a level loads: each shape's REACH, and health for things with a NUMBER for their size
    # (named sizes already got theirs from the size table). The biggest number-sized thing gets MAX_HEALTH;
    # the others get the same share of it as their reach is of the biggest.
    for thing in things:
        if "parent" not in thing:
            thing["reach"] = thing_reach(thing)
    numbered = [thing for thing in things if "parent" not in thing and "size_name" not in thing]
    if not numbered:
        return
    biggest_reach = max(thing["reach"] for thing in numbered)
    for thing in numbered:
        if "fixed_health" in thing:                   # the level gave it its own "health"
            thing["max_health"] = thing["fixed_health"]
        else:
            thing["max_health"] = max(1, round(MAX_HEALTH * thing["reach"] / biggest_reach))   # at least 1
        thing["health"] = thing["max_health"]


# ================================ MATHS, DRAWING, COLLISIONS ================================
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


# SPEED: the cos and sin of your turn and tip are the same for every point in a frame, so they're worked out
# only when your turn or tip CHANGES, and kept here. (to_camera() runs thousands of times a frame.)
camera_trig = {"turn": None, "tip": None}


def to_camera(world_point):
    # A WORLD point -> measured from YOU: 1. measure from where you stand, 2. undo your turn (left / right),
    # 3. undo your tip (up / down). The same sums as rotate_y(moved, -turn) then rotate_x(turned, -tip),
    # written out here so the cos and sin can be reused.
    if camera_trig["turn"] != camera["turn"] or camera_trig["tip"] != camera["tip"]:   # you've turned: redo them
        camera_trig["turn"], camera_trig["tip"] = camera["turn"], camera["tip"]
        turn_radians, tip_radians = math.radians(-camera["turn"]), math.radians(-camera["tip"])
        camera_trig["cos_turn"], camera_trig["sin_turn"] = math.cos(turn_radians), math.sin(turn_radians)
        camera_trig["cos_tip"], camera_trig["sin_tip"] = math.cos(tip_radians), math.sin(tip_radians)
    x, y, z = world_point
    x, y, z = (x - camera["x"]), (y - camera["y"]), (z - camera["z"])    # 1. measure from where you stand
    cos_a, sin_a = camera_trig["cos_turn"], camera_trig["sin_turn"]      # 2. undo your turn (round y)
    x, z = (x * cos_a) - (z * sin_a), (x * sin_a) + (z * cos_a)
    cos_a, sin_a = camera_trig["cos_tip"], camera_trig["sin_tip"]        # 3. undo your tip (round x)
    y, z = (y * cos_a) - (z * sin_a), (y * sin_a) + (z * cos_a)
    return (x, y, z)


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
    aim_x, aim_y, aim_z = rotate_y(rotate_x((0, 0, 1), camera["tip"]), camera["turn"])
    start = 0.4                                   # start a little in front of your eye (closer is cut off by NEAR)
    crosshair["kick"] = CROSSHAIR_KICK            # the crosshair's arms jump out
    start_point = (camera["x"] + (aim_x * start), camera["y"] + (aim_y * start), camera["z"] + (aim_z * start))
    spawn_bullet(start_point, (aim_x, aim_y, aim_z), BULLET_SPEED, (255, 215, 0), PALETTE_GOLD, None)   # GOLD


def spawn_bullet(start, aim, speed, colour, palette, owner):
    # A new bullet THING. 'aim' must be length 1. 'owner' = the tank that fired it (None = you):
    # a bullet never hits its own owner, and only TANK bullets can hit you.
    things.append({"name": "bullet", "bullet": True, "model": bullet_model, "owner": owner,
                   "position": [start[0], start[1], start[2]],                        # NEW lists
                   "velocity": [aim[0] * speed, aim[1] * speed, aim[2] * speed],      #   each time
                   "range": BULLET_RANGE,
                   "size": BULLET_SIZE, "angles": [0, 0, 0], "speeds": (12, 9, 0),    # spins fast as it flies
                   "colour": colour, "palette": palette})


def angle_between(angle):
    # Any angle -> the same direction, as a number from -180 to 180 (e.g. 350 -> -10). Handy for "which way
    # is shorter to turn" and for sweeps either side of a centre.
    return ((angle + 180) % 360) - 180


def aim_turret(turret):
    # Turn the turret for its gun MODE (SPIN turrets are turned by their "speeds" in spin_things() instead).
    # The turret's angle is RELATIVE to its hull: 0 = pointing the way the hull faces.
    config = turret["gun_config"]
    angle = turret["angles"][0]
    if config["mode"] == "OSCILLATE":
        # Sweep from centre - range to centre + range and back, turret_spin degrees a frame
        offset = angle_between(angle - config["centre"]) + (config["turret_spin"] * turret["sweep_direction"])
        if offset > config["range"]:                      # reached one end: turn back
            offset = config["range"]
            turret["sweep_direction"] = -1
        if offset < -config["range"]:                     # reached the other end: turn back
            offset = -config["range"]
            turret["sweep_direction"] = 1
        angle = config["centre"] + offset
    elif config["mode"] == "TRACK":
        # Which way is YOU, from the turret? In the world: the same atan2 the tanks use to face the way they drive.
        pivot = to_world((0, 0, 0), turret)
        towards_you = math.degrees(math.atan2(-(camera["x"] - pivot[0]), camera["z"] - pivot[2]))
        wanted = towards_you - turret["parent_thing"]["angles"][0]          # ... relative to the hull
        turn = angle_between(wanted - angle)                                # the SHORTER way round
        turn = max(-config["turret_spin"], min(config["turret_spin"], turn))   # no faster than turret_spin
        angle = angle + turn
    turret["angles"][0] = keep_under_360(angle)


def tanks_take_aim():
    # Every turret with a gun: first it turns (its gun MODE), then, when it's ready (cooled down) AND pointing
    # at you (within its "cone" degrees, judged flat - turrets only turn left / right), it starts a VOLLEY:
    # "volley" shots, "volley_gap" frames apart, each one a perfect shot at your eye. Once a volley starts
    # it's finished, even if the turret turns away. THEN it cools down for "cooldown" frames.
    # (Each turret's numbers are in its gun_config: GUN_DEFAULTS plus its level's "gun" changes.)
    guns = [thing for thing in things if thing.get("gun") and not thing["parent_thing"].get("dead")]   # (a separate
                                                                  #   list: spawn_bullet adds to things)
    for turret in guns:
        config = turret["gun_config"]
        aim_turret(turret)
        if turret["volley_left"] == 0:                            # not in the middle of a volley:
            if turret["cooldown"] > 0:
                turret["cooldown"] = turret["cooldown"] - 1       #   still cooling down
                continue
            if not turret_sees_you(turret):
                continue                                          #   ready, but not pointing at you
            turret["volley_left"] = config["volley"]              #   ready AND sees you: start a volley...
            turret["volley_timer"] = 0                            #   ...with the first shot right now
        turret["volley_timer"] = turret["volley_timer"] - 1
        if turret["volley_timer"] > 0:
            continue                                              # waiting for the next shot in the volley
        fire_at_you(turret)
        turret["volley_left"] = turret["volley_left"] - 1
        turret["volley_timer"] = config["volley_gap"]
        if turret["volley_left"] == 0:
            turret["cooldown"] = config["cooldown"]               # volley done: now cool down


def turret_sees_you(turret):
    # True if the turret points within its "cone" degrees of you (flat: turrets only turn left / right).
    pivot = to_world((0, 0, 0), turret)                           # the turret's centre, in the world
    forward = turn_direction((0, 0, 1), turret)                   # where its barrels point (hull turn + its own)
    to_you_x, to_you_z = (camera["x"] - pivot[0]), (camera["z"] - pivot[2])
    flat = math.sqrt((to_you_x * to_you_x) + (to_you_z * to_you_z))
    if flat == 0:
        return False                                              # you're standing exactly on it: no direction
    # cos(angle between "forward" and "toward you"), both flat: 1 = dead ahead. Compare cosines: no acos needed.
    cone = turret["gun_config"]["cone"]
    return ((forward[0] * to_you_x) + (forward[2] * to_you_z)) / flat >= math.cos(math.radians(cone))


def fire_at_you(turret):
    # One perfect shot: from the turret's next muzzle, aimed exactly at your eye in 3D (height too).
    muzzles = turret["model"]["muzzles"]
    muzzle = to_world(muzzles[turret["next_muzzle"]], turret)
    turret["next_muzzle"] = (turret["next_muzzle"] + 1) % len(muzzles)     # twin barrels take turns
    dx, dy, dz = (camera["x"] - muzzle[0]), (camera["y"] - muzzle[1]), (camera["z"] - muzzle[2])
    distance = math.sqrt((dx * dx) + (dy * dy) + (dz * dz))
    spawn_bullet(muzzle, (dx / distance, dy / distance, dz / distance), turret["gun_config"]["bullet_speed"],
                 TANK_BULLET_COLOUR, PALETTE_TANK_BULLET, turret["parent_thing"])


def break_apart(thing):
    # A shape at 0 health. It's marked "dead" (removed at the end of the frame) with a big burst of sparks.
    # If its NAMED size splits (this level's sizes: "splits_to"), two pieces of the SAME model take its place,
    # at the smaller named size and with that size's health, pushed apart. Otherwise it just dies:
    #   - a size that splits to None (TINY, or whatever this level ends on)
    #   - a thing with a NUMBER for its size (the tanks, for now)
    #   - a tank (its turret and radar would need copying too): it dies, children and all
    thing["dead"] = True
    for burst in range(3):                                         # a bigger burst than a normal hit
        spawn_sparks(thing["position"], [thing["colour"], (255, 255, 255), (255, 220, 120)])
    if bump_sound:
        bump_sound.play()
    has_children = any(other.get("parent_thing") is thing for other in things)
    splits_to = level_sizes[thing["size_name"]]["splits_to"] if "size_name" in thing else None
    if splits_to is None or has_children:
        return                                                     # it just dies

    # A random direction to push the pieces apart (any direction, then made length 1)
    push = (random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))
    length = math.sqrt((push[0] * push[0]) + (push[1] * push[1]) + (push[2] * push[2])) or 1
    push = (push[0] / length, push[1] / length, push[2] / length)
    for side in (1, -1):                                           # one piece each way
        piece = dict(thing)                                        # a COPY of the shape's settings...
        del piece["dead"]
        piece["name"] = thing["name"] + " piece"
        apply_size_name(piece, splits_to)                          # the smaller size, and its health
        piece["reach"] = thing_reach(piece)
        piece_reach = piece["reach"]
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


decal_glow = {"frame": 0}       # counts frames for the glowing decals' pulse


def decal_colour(decal):
    # A decal's colour this frame: glowing ones (lava) slowly pulse between 70% and 100% bright.
    if not decal["glow"]:
        return decal["colour"]
    brightness = 0.85 + (0.15 * math.sin(2 * math.pi * decal_glow["frame"] / DECAL_GLOW_FRAMES))
    return tuple(round(channel * brightness) for channel in decal["colour"])


def trim_to_near(camera_points):
    # A flat shape's corners, measured from YOU, with any part closer than NEAR (or behind you) TRIMMED off -
    # so a long lava strip you're standing on still shows in front of you. Walk round the corners: keep those
    # in front, and where an edge crosses NEAR, add the crossing point (the right share of the way along it).
    trimmed = []
    for n in range(len(camera_points)):
        a, b = camera_points[n], camera_points[(n + 1) % len(camera_points)]
        if a[2] >= NEAR:
            trimmed.append(a)
        if (a[2] >= NEAR) != (b[2] >= NEAR):              # this edge crosses NEAR
            share = (NEAR - a[2]) / (b[2] - a[2])
            trimmed.append(tuple(a[axis] + ((b[axis] - a[axis]) * share) for axis in range(3)))
    return trimmed


def trim_to_screen(points):
    # A shape's SCREEN corners, cut down to the screen's edges. Points trimmed at NEAR can land thousands of
    # pixels off screen, and filling a shape that big is SLOW (it was dropping the FPS when you looked down at
    # the lava from the air). Same idea as trim_to_near(), once for each edge: keep the corners on the screen's
    # side of that edge, and add the crossing point wherever a side of the shape crosses it.
    edges = [(0, -1, 0),            # (axis, side, limit): x must be >= -1  (a pixel past the left edge)
             (0, 1, WIDTH + 1),     #                      x must be <= WIDTH + 1
             (1, -1, -1),           #                      y must be >= -1
             (1, 1, HEIGHT + 1)]    #                      y must be <= HEIGHT + 1
    for axis, side, limit in edges:
        inside_points = []
        for n in range(len(points)):
            a, b = points[n], points[(n + 1) % len(points)]
            a_in = (a[axis] - limit) * side <= 0
            b_in = (b[axis] - limit) * side <= 0
            if a_in:
                inside_points.append(a)
            if a_in != b_in:                              # this side of the shape crosses the edge
                share = (limit - a[axis]) / (b[axis] - a[axis])
                inside_points.append((a[0] + ((b[0] - a[0]) * share), a[1] + ((b[1] - a[1]) * share)))
        points = inside_points
        if not points:
            break                                         # nothing left on screen
    return points


def draw_floor_shapes():
    # Decals on the floor: drawn straight after the grid, before any thing, so they never cover one.
    decal_glow["frame"] = decal_glow["frame"] + 1
    for decal in FLOOR_SHAPES:
        camera_points = [to_camera((x, FLOOR_Y, z)) for x, z in decal["corners"]]   # each corner, from YOU
        visible = trim_to_near(camera_points)
        if len(visible) < 3:
            continue                                        # all behind you
        on_screen = trim_to_screen([project(point) for point in visible])
        if len(on_screen) >= 3:                             # still a shape on screen: draw it
            pygame.draw.polygon(screen, decal_colour(decal), on_screen)


def draw_world_line(world_start, world_end, colour):
    # A straight line in the WORLD. If part of it is behind you (closer than NEAR), that part is TRIMMED off
    # and the rest is drawn - so only two points are worked out, however long the line is.
    start, end = to_camera(world_start), to_camera(world_end)
    if start[2] < NEAR and end[2] < NEAR:
        return                                       # all of it is behind you: nothing to draw
    if start[2] < NEAR or end[2] < NEAR:
        # One end is behind you. Measured from YOU (camera space) the line is still straight, so the point
        # where it crosses NEAR is just the right share of the way along it: 'share' = 0 at start, 1 at end.
        share = (NEAR - start[2]) / (end[2] - start[2])
        crossing = tuple(start[axis] + ((end[axis] - start[axis]) * share) for axis in range(3))
        if start[2] < NEAR:
            start = crossing                         # trim the start off ...
        else:
            end = crossing                           # ... or the end
    pygame.draw.line(screen, colour, project(start), project(end), 1)


def draw_world_box():
    # The WIREFRAME BOX round the room: a post up from each corner of the floor to the ceiling,
    # and the ceiling's four edges joining their tops. (The floor's own edges are part of the grid.)
    left, floor, near = WORLD_MIN
    right, ceiling, far = WORLD_MAX
    corners = [(left, near), (right, near), (right, far), (left, far)]     # round the floor, in order
    for x, z in corners:
        draw_world_line((x, floor, z), (x, ceiling, z), WORLD_BOX_COLOUR)  # the corner posts
    for n in range(4):
        (x1, z1), (x2, z2) = corners[n], corners[(n + 1) % 4]              # each corner to the next
        draw_world_line((x1, ceiling, z1), (x2, ceiling, z2), WORLD_BOX_COLOUR)   # the ceiling's edges


def grid_steps(start, end, step):
    # The positions BETWEEN start and end, every 'step' (not start or end themselves: those are the room's edges,
    # which draw_world_box() already draws).
    positions = []
    position = start + step
    while position < end - 0.001:
        positions.append(position)
        position = position + step
    return positions


def draw_wall_grid():
    # A grid on the four WALLS and the CEILING, every WALL_GRID_STEP units, in the floor grid's colour.
    left, floor, near = WORLD_MIN
    right, ceiling, far = WORLD_MAX
    heights = grid_steps(floor, ceiling, WALL_GRID_STEP)      # lines ACROSS the walls, at these heights
    across_x = grid_steps(left, right, WALL_GRID_STEP)        # upright lines on the near and far walls
    across_z = grid_steps(near, far, WALL_GRID_STEP)          # upright lines on the left and right walls
    for z in (near, far):                                     # the NEAR and FAR walls
        for x in across_x:
            draw_world_line((x, floor, z), (x, ceiling, z), GRID_COLOUR)
        for y in heights:
            draw_world_line((left, y, z), (right, y, z), GRID_COLOUR)
    for x in (left, right):                                   # the LEFT and RIGHT walls
        for z in across_z:
            draw_world_line((x, floor, z), (x, ceiling, z), GRID_COLOUR)
        for y in heights:
            draw_world_line((x, y, near), (x, y, far), GRID_COLOUR)
    for x in across_x:                                        # the CEILING: lines running away from you ...
        draw_world_line((x, ceiling, near), (x, ceiling, far), GRID_COLOUR)
    for z in across_z:                                        # ... and lines across
        draw_world_line((left, ceiling, z), (right, ceiling, z), GRID_COLOUR)


def draw_floor():
    # The grid covers the level's WORLD BOX in x and z (whole numbers: a line at every one).
    left, right = int(WORLD_MIN[0]), int(WORLD_MAX[0])
    near, far = int(WORLD_MIN[2]), int(WORLD_MAX[2])
    if not SHOW_PIECES:
        # Each grid line drawn WHOLE (draw_world_line trims any part behind you): far fewer points to work out
        for z in range(near, far + 1):                # lines ACROSS: one at every z
            draw_world_line((left, FLOOR_Y, z), (right, FLOOR_Y, z), GRID_COLOUR)
        for x in range(left, right + 1):              # lines AWAY: one at every x
            draw_world_line((x, FLOOR_Y, near), (x, FLOOR_Y, far), GRID_COLOUR)
        return
    # SHOW_PIECES (a test view): every 1-unit piece in its own colour, so the pieces are drawn one by one
    for z in range(near, far + 1):                    # lines ACROSS: one at every z
        for x in range(left, right):                  #   cut into pieces: x to x + 1
            draw_floor_line((x, FLOOR_Y, z), (x + 1, FLOOR_Y, z))
    for x in range(left, right + 1):                  # lines AWAY: one at every x
        for z in range(near, far):                    #   cut into pieces: z to z + 1
            draw_floor_line((x, FLOOR_Y, z), (x, FLOOR_Y, z + 1))



# ================================ ONE FRAME: the steps the game loop calls ================================
def spin_things(keys):
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


def move_camera(keys):
    # You: mouse to look, W A S D to move, and gravity for jumps. (camera is a dictionary: no 'global' needed)
    # ---- CAMERA controls (as in step3_small_world) -------------------
    #   mouse = turn and look up / down
    #   W / S = walk forward / back, A / D = strafe left / right
    mouse_dx, mouse_dy = pygame.mouse.get_rel()          # pixels moved since last frame
    camera["turn"] = (camera["turn"] - (mouse_dx * MOUSE_SPEED))     # mouse right = turn right
    camera["tip"] = (camera["tip"] + (mouse_dy * MOUSE_SPEED))       # mouse up = look up
    if camera["tip"] > TIP_LIMIT:      camera["tip"] = TIP_LIMIT     # stop at the limits
    if camera["tip"] < -TIP_LIMIT:     camera["tip"] = -TIP_LIMIT

    forward_x, forward_y, forward_z = rotate_y((0, 0, 1), camera["turn"])   # the way you face
    right_x, right_y, right_z = rotate_y((1, 0, 0), camera["turn"])         # your right hand

    walk = 0 if you["frozen"] > 0 else MOVE_SPEED          # FROZEN by ice: you can't walk (you can still look)
    if keys[pygame.K_w]:                                  # forward
        camera["x"] = (camera["x"] + (forward_x * walk))
        camera["z"] = (camera["z"] + (forward_z * walk))
    if keys[pygame.K_s]:                                  # back
        camera["x"] = (camera["x"] - (forward_x * walk))
        camera["z"] = (camera["z"] - (forward_z * walk))
    if keys[pygame.K_d]:                                  # strafe right
        camera["x"] = (camera["x"] + (right_x * walk))
        camera["z"] = (camera["z"] + (right_z * walk))
    if keys[pygame.K_a]:                                  # strafe left
        camera["x"] = (camera["x"] - (right_x * walk))
        camera["z"] = (camera["z"] - (right_z * walk))

    # ---- Jumping and falling --------------------------------------------
    camera["vy"] = camera["vy"] - GRAVITY           # gravity pulls your speed DOWN a little each frame
    camera["y"] = camera["y"] + camera["vy"]              # move up (or down) by that speed
    if camera["y"] < STAND_Y:                 # gone below standing height: you've landed
        camera["y"] = STAND_Y
        camera["vy"] = 0


def move_things():
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
                dx, dy, dz = (camera["x"] - position[0]), (camera["y"] - position[1]), (camera["z"] - position[2])
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


def remove_finished_things():
    # Remove used-up bullets (out of range, hit the floor, or hit something). [:] changes the list itself,
    # rather than making a new list called things, and doing it HERE means we're not looping over things.
    things[:] = [thing for thing in things if not (thing.get("bullet") and thing["range"] <= 0)
                 and not thing.get("dead")                                             # destroyed shapes...
                 and not ("parent_thing" in thing and thing["parent_thing"].get("dead"))]   # ...and their children


def add_thing_faces(face_paint_order):
    # Every thing's visible faces go into face_paint_order (things with no faces are drawn as lines right away).
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
                thing["world_points"] = world_points        # kept, so the mini-map can reuse them this frame

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


def paint_faces(face_paint_order):
    # ---- The painter's sort: ALL faces together, furthest from YOU first ----
    face_paint_order.sort(reverse=True)      # biggest number (furthest) first, nearest last: works for BOTH methods
    for paint_depth, colour, face_points, outline_colour in face_paint_order:
        pygame.draw.polygon(screen, colour, face_points)               # filled
        pygame.draw.polygon(screen, outline_colour, face_points, 1)    # outline: 1 pixel


def draw_mini_map():
## MINI MAP
    map_box = pygame.Rect(MAP_LEFT, MAP_BOX_TOP, MAP_BOX_WIDTH, MAP_BOX_HEIGHT)
    screen.blit(map_background, (MAP_LEFT, MAP_BOX_TOP))        # 50% see-through background: the 3D view shows through

    # The PLAY AREA: the level's floor, seen from above, as a hollow green rectangle (the same green as the
    # room's wireframe box). Drawn first, so everything else on the map sits on top of it.
    left, floor, near = WORLD_MIN
    right, ceiling, far = WORLD_MAX
    play_area = [to_map(left, near), to_map(right, near), to_map(right, far), to_map(left, far)]
    pygame.draw.polygon(screen, WORLD_BOX_COLOUR, play_area, 2)  # 2 = a 2-pixel outline, not filled

    for decal in FLOOR_SHAPES:                                               # decals, seen from above:
        pygame.draw.polygon(screen, decal_colour(decal), [to_map(x, z) for x, z in decal["corners"]])   # under all else
    for box in BOXES:                                                        # boxes, seen from above: rectangles
        (low_x, low_y, low_z), (high_x, high_y, high_z) = box["min"], box["max"]
        pygame.draw.polygon(screen, box["colour"], [to_map(low_x, low_z), to_map(high_x, low_z),
                                                    to_map(high_x, high_z), to_map(low_x, high_z)])
    pygame.draw.rect(screen, (255, 255, 255), map_box, 1)       # thin white border



    for thing in things:                                          # each thing = its SHADOW, seen from straight above
        # Every corner in the WORLD (sized, spun, placed - and carried by its parent, for turrets and radars)
        # (add_thing_faces() already worked them out this frame: reuse them; work them out only if missing)
        corners_in_world = thing.get("world_points") or [to_world(point, thing) for point in thing["model"]["points"]]
        # Each face, squashed flat onto the map: keep x and z, drop the height (y). Drawn filled, the faces
        # together make the shape's true outline from above - holes stay holes (the frame), children show (turrets).
        for corners, normal in thing["model"]["faces"]:
            shadow = [to_map(corners_in_world[corner][0], corners_in_world[corner][2]) for corner in corners]
            pygame.draw.polygon(screen, thing["colour"], shadow)

    # YOUR VIEW: two lines, the edges of what's on screen, each VIEW_HALF_ANGLE either side of where you face
    you_on_map = to_map(camera["x"], camera["z"])
    # Drawn on their own layer, in the layer's coordinates (its top-left corner is the map box's top-left),
    # so they stop at the map's edge
    view_cone_layer.fill((0, 0, 0, 0))                                          # clear: fully see-through
    # (the two straight view-edge lines were removed: the pings' arcs show the view's width on their own)
    # The RADAR PINGS: arcs travelling OUTWARDS, each with a fading trail behind it.
    # 'cycle' goes 0 -> 1 as a ping travels out (then back to 0); the pings are spread evenly round that cycle.
    view_arc_timer["frame"] = view_arc_timer["frame"] + 1
    cycle = (view_arc_timer["frame"] % VIEW_PING_FRAMES) / VIEW_PING_FRAMES
    for ping in range(VIEW_PINGS):
        ping_distance = ((cycle + (ping / VIEW_PINGS)) % 1) * VIEW_PING_REACH        # how far out this ping is
        for behind, solid in VIEW_PING_TRAIL:
            distance = ping_distance - behind
            if distance <= 0.2:
                continue                              # not out yet (too close to you to draw)
            solid = round(solid * (1 - (distance / VIEW_PING_REACH)))     # fainter the further out it is
            # One arc: points from one edge of the view round to the other, joined by short lines
            arc = []
            for n in range(VIEW_ARC_POINTS + 1):
                angle = camera["turn"] - VIEW_HALF_ANGLE + ((2 * VIEW_HALF_ANGLE) * n / VIEW_ARC_POINTS)
                point_x, point_y, point_z = rotate_y((0, 0, 1), angle)
                on_map = to_map(camera["x"] + (point_x * distance), camera["z"] + (point_z * distance))
                arc.append((on_map[0] - MAP_LEFT, on_map[1] - MAP_BOX_TOP))
            pygame.draw.lines(view_cone_layer, PLAYER_MAP_COLOUR + (solid,), False, arc, 1)   # False: an open curve
    screen.blit(view_cone_layer, (MAP_LEFT, MAP_BOX_TOP))

    pygame.draw.circle(screen, PLAYER_MAP_COLOUR, you_on_map, 5)                # gold dot = YOU


def next_level_number():
    # The next level after this one, in number order (skipping test levels like 99). None = there isn't one.
    if level_progress["number"] in TEST_LEVELS:
        return None                                   # a test level isn't part of the order: it ends there
    later = [n for n in sorted(LEVELS) if n > level_progress["number"] and n not in TEST_LEVELS]
    return later[0] if later else None


def update_level_progress():
    # Once per frame. When every SHAPE is gone (not counting bullets, or children - they go with their parent),
    # the level is CLEARED: count frames, and after LEVEL_COMPLETE_FRAMES load the next level (if there is one).
    if level_progress["cleared_frames"] is None:
        shapes_left = [thing for thing in things
                       if "parent" not in thing and not thing.get("bullet") and not thing.get("dead")]
        if not shapes_left:
            level_progress["cleared_frames"] = 0          # cleared: the message starts now
        return
    level_progress["cleared_frames"] = level_progress["cleared_frames"] + 1
    if level_progress["cleared_frames"] >= LEVEL_COMPLETE_FRAMES:
        number = next_level_number()
        if number is not None:
            load_level(number)                            # clear everything and start the next level fresh


def draw_level_complete():
    # "Level X completed!" in the middle of the screen once the level is cleared, with what comes next under it.
    if level_progress["cleared_frames"] is None:
        return
    number = next_level_number()
    lines = [(title_font, "Level " + str(level_progress["number"]) + " completed!")]
    if number is not None:
        lines.append((intro_font, "Next: level " + str(number) + " - " + LEVELS[number].get("name", "")))
    else:
        lines.append((intro_font, "All levels completed!"))
    y = HEIGHT * 0.4
    for font, text in lines:
        shadow = font.render(text, True, BLACK)
        words = font.render(text, True, BANNER_COLOUR)
        x = CENTRE_X - (words.get_width() / 2)            # centred across the screen
        screen.blit(shadow, (x + 3, y + 3))               # a black shadow, so it reads on any background
        screen.blit(words, (x, y))
        y = y + words.get_height() + 10


def draw_level_banner():
    # The level's NAME and INTRO as it starts:
    #   first BANNER_HOLD frames:  the name, big, in the middle of the screen, with the intro line under it
    #   next BANNER_MOVE frames:   BOTH rise to the top: the name shrinks to a heading, the intro stays under it
    #   next BANNER_INTRO_HOLD:    the intro stays at the top, under the name
    #   next BANNER_FADE frames:   the intro fades away
    #   after that:                the name stays at the top of the screen
    frame = level_banner["frame"]
    level_banner["frame"] = frame + 1
    if not level_banner["name"]:
        return

    # 'progress' goes 0 -> 1 during the move. 'eased' is the same, but starts and ends gently (no jolt).
    progress = min(1, max(0, (frame - BANNER_HOLD) / BANNER_MOVE))
    eased = progress * progress * (3 - (2 * progress))
    # 'fading' goes 0 -> 1 while the intro fades, once it has had its time at the top
    fade_start = BANNER_HOLD + BANNER_MOVE + BANNER_INTRO_HOLD
    fading = min(1, max(0, (frame - fade_start) / BANNER_FADE))

    # THE NAME: rendered big, then shrunk as it rises (to 45% of its size at the top)
    name_surface = title_font.render(level_banner["name"], True, BANNER_COLOUR)
    shadow_surface = title_font.render(level_banner["name"], True, BLACK)
    scale = 1 - (0.55 * eased)
    if scale < 1:
        size = (round(name_surface.get_width() * scale), round(name_surface.get_height() * scale))
        name_surface = pygame.transform.smoothscale(name_surface, size)
        shadow_surface = pygame.transform.smoothscale(shadow_surface, size)
    middle_y = HEIGHT * 0.3                                   # where it starts: a third of the way down
    top_y = 12                                                # where it ends: just below the top edge
    name_y = middle_y + ((top_y - middle_y) * eased)
    name_x = CENTRE_X - (name_surface.get_width() / 2)        # centred across the screen
    screen.blit(shadow_surface, (name_x + 3, name_y + 3))     # a black shadow, so it reads on any background
    screen.blit(name_surface, (name_x, name_y))

    # THE INTRO: always just under the name (so it rises WITH it), then it fades away
    if fading < 1:
        intro_surface = intro_font.render(level_banner["intro"], True, BANNER_INTRO_COLOUR)
        intro_shadow = intro_font.render(level_banner["intro"], True, BLACK)
        fade = round(255 * (1 - fading))                      # 255 = solid, 0 = gone
        intro_surface.set_alpha(fade)
        intro_shadow.set_alpha(fade)                          # the shadow fades with it
        intro_x = CENTRE_X - (intro_surface.get_width() / 2)
        intro_y = name_y + name_surface.get_height() + 6      # just under the name, wherever it is
        screen.blit(intro_shadow, (intro_x + 2, intro_y + 2)) # a black shadow, like the name's
        screen.blit(intro_surface, (intro_x, intro_y))


def draw_hud():
    # The text and bars in the top-left corner, and the red flash when you're hit.
    # FPS counter, top-left corner
    fps_text = fps_font.render("FPS: " + str(round(clock.get_fps())), True, GREEN)
    screen.blit(fps_text, (10, 10))

    # Facing, just under the FPS: compass style, 0 = up the map (+z), counting up as you turn RIGHT.
    # camera["turn"] goes DOWN when you turn right, so flip its sign; % 360 wraps it into 0..359.
    heading = round(-camera["turn"]) % 360
    heading_text = fps_font.render("Facing: " + str(heading) + "°", True, GREEN)
    screen.blit(heading_text, (10, 40))

    # Camera tilt, under that: 0 = level, + = looking UP, - = looking down.
    # camera["tip"] is + when looking DOWN, so flip its sign.
    tilt = round(-camera["tip"])
    tilt_text = fps_font.render("Tilt: " + str(tilt) + "°", True, GREEN)
    screen.blit(tilt_text, (10, 70))

    # Where you stand in the WORLD (camera["x"], camera["y"], camera["z"]), rounded to 1 decimal place.
    position_text = fps_font.render("World x, y, z: " + str(round(camera["x"], 1)) + ", " + str(round(camera["y"], 1)) + ", " + str(round(camera["z"], 1)), True, GREEN)
    screen.blit(position_text, (10, 100))

    # Hits from the tanks, and a red flash round the screen edge for a moment after each one
    hits_text = fps_font.render("Hits taken: " + str(you["hits_taken"]), True, (255, 80, 80))
    screen.blit(hits_text, (10, 130))

    # VOLUME slider: hidden for now (the - and = keys still change the volume). Set SHOW_VOLUME = True to show it.
    if SHOW_VOLUME:
        volume_text = fps_font.render("Volume", True, GREEN)
        screen.blit(volume_text, (10, 160))
        bar = pygame.Rect(100, 164, 150, 16)                               # the slider's track
        pygame.draw.rect(screen, GREEN, (bar.x, bar.y, bar.width * volume["slider"], bar.height))   # filled part
        pygame.draw.rect(screen, GREEN, bar, 1)                            # outline
        percent_text = fps_font.render(str(round(volume["slider"] * 100)) + "%  (- =)", True, GREEN)
        screen.blit(percent_text, (bar.right + 10, 160))
    if you["frozen"] > 0:
        pygame.draw.rect(screen, FREEZE_COLOUR, screen.get_rect(), 16)  # FROZEN: a thick icy border
    if you["hurt"] > 0:
        pygame.draw.rect(screen, (255, 0, 0), screen.get_rect(), 12)    # a thick red border: 12 pixels wide
        you["hurt"] = you["hurt"] - 1
