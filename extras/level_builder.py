# level_builder.py - BUILDS big levels (like The Glacier and The Furnace) as plain level DATA, ready to paste
# into LEVELS in rotation_levels.py. It never changes the game's files: it PRINTS the level's code.
#
#   py level_builder.py glacier 9     -> prints level 9, The Glacier (ice)
#   py level_builder.py furnace 10    -> prints level 10, The Furnace (lava)
#   py level_builder.py slime 11      -> prints level 11, The Sludge Pit (slime)
#   py level_builder.py custard 12    -> prints The Trifle (custard and jelly)
#   py level_builder.py cupid 12      -> prints level 12, Cupid Canyon (the same layout, all PINK)
#   py level_builder.py fortknox 13   -> prints level 13, Fort Knox (a gold VAULT)
#   py level_builder.py glacier 12 > new_level.txt   -> the same, saved in a file to copy from
#
# Why a builder? A big level has ~100 boxes, and every box piece must be SHORT (about 1 unit in x and z, and
# tall things stacked in 1-unit layers) or the painter's sort draws it wrong. The helpers below write those
# pieces for you: a wall from a list of heights, a jagged floor-to-ceiling column, a ring round a bunker, a pile
# of blocks, and your low cover at the start. Each RECIPE (glacier, furnace) uses them; copy one to make more.
#
# The colours it names (ICE_BLOCK, SNOW, OBSIDIAN, EMBER and their palettes) live in rotation_data.py.
import sys


def n(v):
    v = round(v, 3)
    return str(int(v)) if v == int(v) else str(v)


class Boxes:
    def __init__(self, colour, palette):
        self.lines, self.colour, self.palette = [], colour, palette

    def note(self, text):
        self.lines.append("            # " + text)

    def box(self, x0, y0, z0, x1, y1, z1, comment="", colour=None, palette=None):
        c, p = colour or self.colour, palette or self.palette
        line = (f'            {{"min": ({n(x0)}, {n(y0)}, {n(z0)}), "max": ({n(x1)}, {n(y1)}, {n(z1)}), '
                f'"colour": {c}, "palette": {p}}},')
        self.lines.append(line + ("   # " + comment if comment else ""))

    def wall_x(self, x0, z0, z1, tops, comment, window_at=None, **kw):
        # a wall ALONG x, from x0, one 1-unit piece per entry in tops (the top y; None = a gap)
        for i, top in enumerate(tops):
            x = x0 + i
            if top is None:
                continue
            if window_at == i:                         # an eye-height WINDOW in this piece
                self.box(x, -1, z0, x + 1, -0.3, z1, comment + ": under the window", **kw)
                self.box(x, 0.4, z0, x + 1, top, z1, comment + ": over the window (y -0.3 to 0.4)", **kw)
            else:
                self.box(x, -1, z0, x + 1, top, z1, comment if i == 0 else "", **kw)

    def wall_z(self, x0, x1, z0, tops, comment, **kw):
        for i, top in enumerate(tops):
            z = z0 + i
            if top is not None:
                self.box(x0, -1, z, x1, top, z + 1, comment if i == 0 else "", **kw)

    def column(self, cx, cz, half, comment, wobble, **kw):
        # floor to ceiling, 8 layers 1 tall, each a little shifted and resized (jagged sides)
        for layer in range(8):
            dx0, dz0, dx1, dz1, shrink = wobble[layer]
            h = half - shrink
            self.box(cx - h + dx0, layer - 1, cz - h + dz0, cx + h + dx1, layer, cz + h + dz1,
                     f"{comment}: layer {layer + 1}", **kw)

    def ring(self, cx, cz, comment, height=-0.6, **kw):
        # a low 3.5 x 3.5 ring round a floor bunker (like the Canyon's sandbag nests), a GAP facing the back wall
        x0, x1, z0, z1 = cx - 2, cx + 2, cz - 2, cz + 2
        self.box(x0, -1, z1 - 0.5, x0 + 0.5, height, z1, comment + ": corner", **kw)
        self.box(x1 - 0.5, -1, z1 - 0.5, x1, height, z1, "corner", **kw)
        self.box(x0, -1, z0, x0 + 0.5, height, z0 + 0.5, "corner", **kw)
        self.box(x1 - 0.5, -1, z0, x1, height, z0 + 0.5, "corner", **kw)
        for x in (x0 + 0.5, x0 + 1.5, x0 + 2.5):
            self.box(x, -1, z1 - 0.5, x + 1, height, z1, "far side" if x == x0 + 0.5 else "", **kw)
        for z in (z0 + 0.5, z0 + 1.5, z0 + 2.5):
            self.box(x0, -1, z, x0 + 0.5, height, z + 1, "left side" if z == z0 + 0.5 else "", **kw)
            self.box(x1 - 0.5, -1, z, x1, height, z + 1, "right side" if z == z0 + 0.5 else "", **kw)
        self.box(x0 + 0.5, -1, z0, x0 + 1, height, z0 + 0.5, "near side, left part ...", **kw)
        self.box(x1 - 1, -1, z0, x1 - 0.5, height, z0 + 0.5, "... and right part: the GAP is between them", **kw)

    def start_u(self, **kw):
        # a low U round where you start (x 0, z -14), open behind you - like your Canyon sandbags
        self.box(-1.9, -1, -12.6, -1.5, -0.6, -12.2, "front left corner", **kw)
        self.box(1.5, -1, -12.6, 1.9, -0.6, -12.2, "front right corner", **kw)
        for x in (-1.5, -0.5, 0.5):
            self.box(x, -1, -12.6, x + 1, -0.6, -12.2, "front" if x == -1.5 else "", **kw)
        for z in (-13.6, -14.4):
            top = -12.6 if z == -13.6 else -13.6
            self.box(-1.9, -1, z, -1.5, -0.6, top, "left side" if z == -13.6 else "", **kw)
            self.box(1.5, -1, z, 1.9, -0.6, top, "right side" if z == -13.6 else "", **kw)

    def pile(self, x, z, layout, comment, **kw):
        # BLOCKS 1 x 1, stacked: layout = [(dx, dz, height_in_blocks), ...]
        for i, (dx, dz, h) in enumerate(layout):
            for level in range(h):
                self.box(x + dx, -1 + level, z + dz, x + dx + 1, level, z + dz + 1,
                         comment if (i == 0 and level == 0) else "", **kw)

    def mound(self, x0, z0, size, comment, **kw):
        # a STEPPED heap: size x size blocks on the floor (1 tall), then (size - 2) x (size - 2) on top, and so on
        level, inset = 0, 0
        while size - (2 * inset) > 0:
            width = size - (2 * inset)
            for dx in range(width):
                for dz in range(width):
                    first = dx == 0 and dz == 0
                    self.box(x0 + inset + dx, -1 + level, z0 + inset + dz, x0 + inset + dx + 1, level, z0 + inset + dz + 1,
                             f"{comment}: step {level + 1} ({width} x {width})" if first else "", **kw)
            level, inset = level + 1, inset + 1

    def text(self):
        return "\n".join(self.lines)


WOBBLE = [(-0.1, 0, 0.1, 0.1, 0), (0.1, 0.1, 0, 0.1, 0.15), (0, -0.1, -0.1, 0, 0.25), (0.1, 0.1, 0, -0.1, 0.35),
          (0, 0, 0.1, 0.1, 0.3), (-0.1, 0.1, 0, 0, 0.2), (0.1, -0.1, 0.1, 0.1, 0.1), (-0.1, -0.1, 0.1, 0.1, 0)]


ice_floor = '''            # FROZEN POND and ice patches: ICE freezes you (and hurts) - the turrets love a frozen target
            {"type": "ice", "min": (-3, 8), "max": (3, 12)},          # the frozen pond, behind the middle ring
            {"type": "ice", "min": (-15, 1), "max": (-12, 4)},        # a patch by the left wall
            {"type": "ice", "min": (12, 4), "max": (15, 7)},          # a patch by the right wall
            {"type": "ice", "min": (-1, -6), "max": (1, -4)},         # a small patch between the wall's gaps'''

ICE = '"colour": (120, 190, 240), "palette": PALETTE_ICE'
ICICLE = '"colour": (40, 90, 150), "palette": PALETTE_BLACK'
ICE_GUN = '"bullet_colour": (120, 190, 240), "bullet_palette": PALETTE_ICE'
ice_spawn = f'''            # ICE TANKS on patrol in the open lanes: one across the room, one up and down it
            {{"design": "tank", "name": "ice tank",
             "position": [-12, -0.4, LANE_Z], "velocity": [0.015, 0, 0],
             "size": 0.6, "angles": [-90, 0, 0], {ICE},
             "gun": {{"mode": "TRACK", "turret_spin": 0.8, "start_angle": "you", "volley": 3, "cooldown": 150}},
             "radar_spin": -6}},
            {{"design": "tank", "name": "snow tank",
             "position": [LANE_X, -0.4, 12], "velocity": [0, 0, -0.012],
             "size": 0.6, "angles": [180, 0, 0], {ICE},
             "gun": {{"mode": "TRACK", "turret_spin": 0.8, "start_angle": "you", "volley": 3, "cooldown": 150}},
             "radar_spin": 6}},
            # ICE BUNKERS on the floor, in their rings, turrets SPINNING (different speeds and starts)
            {{"design": "bunker", "name": "west ice bunker", "position": [-10, -0.7, -2], "size": 0.6, {ICE},
             "gun": {{"mode": "SPIN", "turret_spin": 1.0, "start_angle": 0, "volley": 3}}}},
            {{"design": "bunker", "name": "east ice bunker", "position": [10, -0.7, -2], "size": 0.6, {ICE},
             "gun": {{"mode": "SPIN", "turret_spin": -1.0, "start_angle": 90, "volley": 3}}}},
            {{"design": "bunker", "name": "middle ice bunker", "position": [0, -0.7, 4], "size": 0.6, {ICE},
             "gun": {{"mode": "SPIN", "turret_spin": 1.2, "start_angle": 45, "volley": 3}}}},
            # ICE BUNKERS on the walls and the ceiling, black with blue edges like the icicles, cupolas TRACKING you
            {{"design": "bunker", "name": "left wall ice bunker", "position": [-15.7, 3, 10], "size": 0.6,
             "angles": [0, 0, -90], {ICICLE},
             "gun": {{"mode": "TRACK", "turret_spin": 1, "volley": 3, {ICE_GUN}}},
             "children": [{{"model": cupola_model}}]}},
            {{"design": "bunker", "name": "right wall ice bunker", "position": [15.7, 3, -4], "size": 0.6,
             "angles": [0, 0, 90], {ICICLE},
             "gun": {{"mode": "TRACK", "turret_spin": 1, "volley": 3, {ICE_GUN}}},
             "children": [{{"model": cupola_model}}]}},
            {{"design": "bunker", "name": "far wall ice bunker", "position": [3, 3, 15.7], "size": 0.6,
             "angles": [0, -90, 0], {ICICLE},
             "gun": {{"mode": "TRACK", "turret_spin": 1, "volley": 3, {ICE_GUN}}},
             "children": [{{"model": cupola_model}}]}},
            {{"design": "bunker", "name": "ceiling ice bunker", "position": [-4, 6.7, 2], "size": 0.6,
             "angles": [0, 180, 0], {ICICLE},
             "gun": {{"mode": "TRACK", "turret_spin": 1, "volley": 3, {ICE_GUN}}},
             "children": [{{"model": cupola_model}}]}},
            # ICE FRAMES and shapes in the air: frames shoot AT you, the diamond drops ice
            {{"design": "frame", "name": "ice frame 1", "position": [-5, 3, 4], "velocity": [0.02, 0.012, -0.015],
             "size": "MEDIUM", "angles": [20, 30, 0], "speeds": (1, 0.6, 0), {ICE},
             "gun": {{"mode": "TARGET", "volley": 1, "cooldown": 120}}}},
            {{"design": "frame", "name": "ice frame 2", "position": [6, 4, 10], "velocity": [-0.018, -0.01, 0.014],
             "size": "MEDIUM", "angles": [-30, 10, 20], "speeds": (0.7, 1, 0.3), {ICE},
             "gun": {{"mode": "TARGET", "volley": 1, "cooldown": 120}}}},
            {{"design": "diamond", "name": "ice diamond", "position": [0, 4.5, -2], "velocity": [0.025, 0, 0.02],
             "size": "MEDIUM", "angles": [0, 0, 0], "speeds": (2, 0, 0), {ICE},
             "gun": {{"mode": "DOWN", "volley": 1}}}},
            {{"design": "cube", "name": "ice cube", "position": [8, 3, 4], "velocity": [-0.02, 0.015, 0.02],
             "size": "LARGE", "angles": [30, 20, 0], "speeds": (0.5, 0.8, 0), {ICE}}},
            # ICICLES on the ceiling, sliding side to side and dripping ice (level dressing: can't be killed)
''' + "\n".join(f'''            {{"design": "pyramid", "name": "icicle {i + 1}",
             "position": [{x}, 6.5, {z}], "velocity": [{v}, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0), {ICICLE},
             "gun": {{"mode": "DOWN", "volley": 3, "cooldown": 60, {ICE_GUN}}},
             "scenery": True}},''' for i, (x, z, v) in enumerate([(-8, -5, 0.02), (6, 0, -0.02), (-3, 7, 0.02), (9, 11, -0.02)]))

lava_floor = '''            # THE LAVA RIVER across the room (z 0 to 2), with two places to cross: x -9 to -7, and x 6 to 8
            {"type": "lava", "min": (-16, 0), "max": (-9, 2)},
            {"type": "lava", "min": (-7, 0), "max": (6, 2)},
            {"type": "lava", "min": (8, 0), "max": (16, 2)},
            # LAVA POOLS: round the volcano's foot, and one in the middle of the far half
            {"type": "lava", "min": (7, 7), "max": (13, 8)},          # in front of the volcano
            {"type": "lava", "min": (7, 8), "max": (8, 13)},          # down its left side
            {"type": "lava", "min": (0, 10), "max": (3, 13)},         # a pool in the far half'''

SUN = '"colour": (255, 120, 60), "palette": PALETTE_SUNSET'
DRIP = '"colour": (140, 35, 30), "palette": PALETTE_BLACK'
LAVA_GUN = '"bullet_colour": (255, 120, 60), "bullet_palette": PALETTE_SUNSET'
lava_spawn = f'''            # LAVA TANKS on patrol (fireproof: they drive straight through the lava)
            {{"design": "tank", "name": "lava tank",
             "position": [-12, -0.4, LANE_Z], "velocity": [0.015, 0, 0],
             "size": 0.6, "angles": [-90, 0, 0], {SUN},
             "gun": {{"mode": "TRACK", "turret_spin": 0.8, "start_angle": "you", "volley": 3, "cooldown": 150}},
             "radar_spin": -6}},
            {{"design": "tank", "name": "magma tank",
             "position": [LANE_X, -0.4, 12], "velocity": [0, 0, -0.012],
             "size": 1, "angles": [180, 0, 0], {SUN},
             "gun": {{"mode": "TRACK", "turret_spin": 0.6, "start_angle": "you", "volley": 3, "cooldown": 170}},
             "radar_spin": 6}},
            # SUNSET BUNKERS on the floor, in their obsidian rings, turrets SPINNING
            {{"design": "bunker", "name": "west lava bunker", "position": [-11, -0.7, -3], "size": 0.6, {SUN},
             "gun": {{"mode": "SPIN", "turret_spin": 1.0, "start_angle": 0, "volley": 3}}}},
            {{"design": "bunker", "name": "east lava bunker", "position": [11, -0.7, -3], "size": 0.6, {SUN},
             "gun": {{"mode": "SPIN", "turret_spin": -1.1, "start_angle": 120, "volley": 3}}}},
            # OBSIDIAN BUNKERS on the walls and ceiling (black, red edges, like the drippers), firing LAVA
            {{"design": "bunker", "name": "left wall lava bunker", "position": [-15.7, 3, -2], "size": 0.6,
             "angles": [0, 0, -90], {DRIP},
             "gun": {{"mode": "TRACK", "turret_spin": 1, "volley": 3, {LAVA_GUN}}},
             "children": [{{"model": cupola_model}}]}},
            {{"design": "bunker", "name": "right wall lava bunker", "position": [15.7, 3, 5], "size": 0.6,
             "angles": [0, 0, 90], {DRIP},
             "gun": {{"mode": "TRACK", "turret_spin": 1, "volley": 3, {LAVA_GUN}}},
             "children": [{{"model": cupola_model}}]}},
            {{"design": "bunker", "name": "far wall lava bunker", "position": [-4, 3, 15.7], "size": 0.6,
             "angles": [0, -90, 0], {DRIP},
             "gun": {{"mode": "TRACK", "turret_spin": 1, "volley": 3, {LAVA_GUN}}},
             "children": [{{"model": cupola_model}}]}},
            {{"design": "bunker", "name": "ceiling lava bunker", "position": [3, 6.7, -3], "size": 0.6,
             "angles": [0, 180, 0], {DRIP},
             "gun": {{"mode": "TRACK", "turret_spin": 1, "volley": 3, {LAVA_GUN}}},
             "children": [{{"model": cupola_model}}]}},
            # SUNSET shapes in the air: frames shoot AT you, the pyramid drops lava
            {{"design": "frame", "name": "lava frame 1", "position": [-4, 3, 7], "velocity": [0.02, -0.012, 0.015],
             "size": "MEDIUM", "angles": [20, 30, 0], "speeds": (1, 0.6, 0), {SUN},
             "gun": {{"mode": "TARGET", "volley": 1, "cooldown": 120}}}},
            {{"design": "frame", "name": "lava frame 2", "position": [5, 4, -2], "velocity": [-0.018, 0.01, -0.014],
             "size": "MEDIUM", "angles": [-30, 10, 20], "speeds": (0.7, 1, 0.3), {SUN},
             "gun": {{"mode": "TARGET", "volley": 1, "cooldown": 120}}}},
            {{"design": "pyramid", "name": "lava pyramid", "position": [0, 4.5, 3], "velocity": [0.025, 0, -0.02],
             "size": "MEDIUM", "angles": [15, 0, 0], "speeds": (1.5, 0, 0), {SUN},
             "gun": {{"mode": "DOWN", "volley": 1}}}},
            {{"design": "diamond", "name": "lava diamond", "position": [-9, 2.5, 4], "velocity": [0.02, 0.02, -0.02],
             "size": "LARGE", "angles": [0, 30, 15], "speeds": (0.8, 0.5, 0.3), {SUN}}},
            # LAVA DRIPPERS on the ceiling, sliding side to side and dripping lava (level dressing: can't be killed)
''' + "\n".join(f'''            {{"design": "pyramid", "name": "lava dripper {i + 1}",
             "position": [{x}, 6.5, {z}], "velocity": [{v}, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0), {DRIP},
             "gun": {{"mode": "DOWN", "volley": 3, "cooldown": 50, {LAVA_GUN}}},
             "scenery": True}},''' for i, (x, z, v) in enumerate([(-6, 1, 0.02), (4, 1, -0.02), (-2, 9, 0.02), (10, -5, -0.02)]))


def find_lanes(box_lines):
    # a clear lane ACROSS (z) and one UP AND DOWN (x), for a tank 0.6 big, away from boxes
    boxes = []
    for line in box_lines:
        if '"min"' not in line:
            continue
        a = line.split('"min": (')[1].split(")")[0].split(", ")
        b = line.split('"max": (')[1].split(")")[0].split(", ")
        boxes.append((float(a[0]), float(a[1]), float(a[2]), float(b[0]), float(b[1]), float(b[2])))
    def clear_z(z):
        return all(not (y0 < 0.5 and z0 < z + 1.3 and z1 > z - 1.3 and x1 > -14 and x0 < 14) for x0, y0, z0, x1, y1, z1 in boxes)
    def clear_x(x):
        return all(not (y0 < 0.5 and x0 < x + 1.3 and x1 > x - 1.3 and z1 > -7 and z0 < 14) for x0, y0, z0, x1, y1, z1 in boxes)
    zs = [z / 2 for z in range(-20, 28) if clear_z(z / 2)]
    xs = [x / 2 for x in range(-26, 27) if clear_x(x / 2)]
    return zs, xs


def level_text(number, title, name, intro, grid, floor, boxes, spawn, lane_z, lane_x):
    spawn = spawn.replace("LANE_Z", n(lane_z)).replace("LANE_X", n(lane_x))
    return f'''    {number}: {{    # ---- LEVEL {number}: {title} ----
        "name": "{name}",
        "intro": "{intro}",
        "world": {{"min": (-16, -1, -16), "max": (16, 7, 16)}},       # 32 wide (x), 32 long (z), 8 tall: the Canyon's size
        "start": {{"x": 0, "y": 0, "z": -14, "turn": 0, "tip": 0}},    # near the back wall, facing the far wall
        "grid_colour": {grid}

        "floor_shapes": [
{floor}
        ],
        "boxes": [
{boxes.text()}
        ],
        "spawn": [
{spawn}
        ],
    }},

'''


def glacier(number=9):
    # THE GLACIER: the Canyon's size, all ICE - ice blocks, spires, an arch, a frozen pond,
    # ice tanks / bunkers / frames, and icicles on the ceiling
    ice = Boxes("ICE_BLOCK", "PALETTE_ICE")
    ice.note("THE GLACIER, built from ICE BLOCKS (ICE_BLOCK edges, PALETTE_ICE). Pieces no longer than 1 unit.")
    ice.note("YOUR SNOW FORT: a low U of packed snow round where you start (x 0, z -14), open behind you")
    ice.start_u(colour="SNOW", palette="PALETTE_SNOW")
    ice.note("THE ICE WALL: cover across the front (z -8.6 to -8.2), x -7 to 7: TALL at both ends, LOW in the middle (see and")
    ice.note("shoot over it), two gaps to run through, and an eye-height WINDOW at x 4 to 5")
    ice.wall_x(-7, -8.6, -8.2, [1.4, 1.9, 1.6, None, -0.3, 0.3, -0.5, None, None, -0.2, 1.8, 2.0, 1.2, 1.6], "the ice wall",
               window_at=11)
    ice.note("ICE BLOCK PILES: 1 x 1 blocks, stacked 1 or 2 high - cover in the open")
    ice.pile(-7, -3, [(0, 0, 2), (1, 0, 1), (0, 1, 1)], "pile, left")
    ice.pile(5, 1, [(0, 0, 1), (1, 0, 2), (1, 1, 1)], "pile, right")
    ice.pile(-3, 9, [(0, 0, 1), (1, 0, 1), (2, 0, 2), (1, 1, 1)], "pile, far")
    ice.note("THE SPIRES: two floor-to-CEILING columns of glacier ice, jagged (8 layers, each 1 tall)")
    ice.column(-10, 7, 1.0, "left spire", WOBBLE)
    ice.column(10, 8, 0.9, "right spire", WOBBLE[::-1])
    ice.note("THE ICE ARCH: two pillars and a lintel at the back right (x 6 to 9, z 12 to 13): run under it")
    for x in (6, 8):
        for layer in range(3):
            ice.box(x, layer - 1, 12, x + 1, layer, 13, "arch pillar" if layer == 0 else "")
    for x in (6, 7, 8):
        ice.box(x, 2, 12, x + 1, 2.6, 13, "arch lintel" if x == 6 else "")
    ice.note("ICE RINGS round the three floor bunkers: low blocks (0.4 tall, under their guns), a GAP facing the back")
    ice.ring(-10, -2, "west ring")
    ice.ring(10, -2, "east ring")
    ice.ring(0, 4, "middle ring")
    lane_z, lane_x = find_lanes(ice.lines)
    return level_text(number, "THE GLACIER - the Canyon's size, all ICE: ice blocks, ice tanks, ice turrets, icicles",
                      "The Glacier", "Ice everywhere. The frozen pond will hold you still - right where the turrets want you.",
                      "(40, 90, 150),                              # an ICE-blue grid", ice_floor, ice, ice_spawn,
                      pick(lane_z, 6), pick(lane_x, 4))


def furnace(number=10):
    # THE FURNACE: the Canyon's size, all LAVA - obsidian, embers, a volcano, a lava river with two crossings,
    # lava tanks / bunkers / frames, and drippers on the ceiling
    lava = Boxes("OBSIDIAN", "PALETTE_OBSIDIAN")
    lava.note("THE FURNACE, built from OBSIDIAN (dark faces, glowing red edges) and EMBER blocks (sunset colours).")
    lava.note("YOUR CINDER WALL: a low U of cooled cinder round where you start (x 0, z -14), open behind you")
    lava.start_u()
    lava.note("THE OBSIDIAN WALL: cover across the front (z -8.6 to -8.2), x -7 to 7: tall ends, a LOW middle, gaps, and a WINDOW at x 3 to 4")
    lava.wall_x(-7, -8.6, -8.2, [1.7, 2.1, 1.3, None, None, -0.2, 0.4, -0.4, None, 0.2, 1.9, 1.6, 2.0, 1.4], "the obsidian wall",
                window_at=10)
    lava.note("THE BROKEN RIDGE: a long obsidian wall down the left side (x -6.4 to -6, z 3 to 12), gaps to slip through")
    lava.wall_z(-6.4, -6, 3, [1.5, 2.2, 1.0, None, 1.8, 2.4, 0.6, None, 1.4], "the ridge")
    lava.note("THE VOLCANO: a stepped cone at the back right (centre x 10, z 10): 4 x 4, then 2 x 2, then the glowing VENT")
    for dx in range(4):
        for dz in range(4):
            lava.box(8 + dx, -1, 8 + dz, 9 + dx, 0, 9 + dz, "volcano: bottom step (4 x 4)" if dx == dz == 0 else "")
    for dx in range(2):
        for dz in range(2):
            lava.box(9 + dx, 0, 9 + dz, 10 + dx, 1, 10 + dz, "volcano: middle step (2 x 2)" if dx == dz == 0 else "")
    lava.box(9.6, 1, 9.6, 10.4, 1.5, 10.4, "volcano: the VENT, glowing", colour="EMBER", palette="PALETTE_SUNSET")
    lava.note("THE BASALT PILLAR: floor to CEILING, jagged (8 layers, each 1 tall)")
    lava.column(-11, 11, 1.0, "basalt pillar", WOBBLE)
    lava.note("EMBER ROCKS: hot sunset-coloured blocks, low cover scattered in the open")
    lava.pile(-9, -6, [(0, 0, 1), (1, 0, 1)], "embers, left", colour="EMBER", palette="PALETTE_SUNSET")
    lava.pile(4, -5, [(0, 0, 1), (0, 1, 1)], "embers, right", colour="EMBER", palette="PALETTE_SUNSET")
    lava.pile(-1, 5, [(0, 0, 2), (1, 0, 1)], "embers, middle", colour="EMBER", palette="PALETTE_SUNSET")
    lava.note("OBSIDIAN RINGS round the floor bunkers: low (0.4 tall, under their guns), a GAP facing the back")
    lava.ring(-11, -3, "west ring")
    lava.ring(11, -3, "east ring")
    lane_z, lane_x = find_lanes(lava.lines)
    return level_text(number, "THE FURNACE - the Canyon's size, all LAVA: obsidian, embers, a volcano, lava tanks and drippers",
                      "The Furnace", "A river of lava and a smoking volcano. Cross at the gaps - and keep moving.",
                      "(140, 35, 30),                              # a LAVA-red grid", lava_floor, lava, lava_spawn,
                      pick(lane_z, 5), pick(lane_x, 3))


def themed_spawn(look, wall_look, bullets, word, tanks, floor_bunkers, wall_bunkers, flyers, drippers):
    # The things for a themed level, all in its colours. Each list holds positions (and a little more):
    #   tanks:         (name, x, z, vx, vz, size, facing)            - patrolling, TRACKING you
    #   floor_bunkers: (name, x, z, spin, start)                     - SPINNING turrets
    #   wall_bunkers:  (name, x, y, z, angles)                       - black, edges in the theme colour, cupolas TRACKING
    #   flyers:        (name, design, x, y, z, velocity, size, look, gun or None)
    #   drippers:      (x, z, vx)                                    - on the ceiling, scenery
    out = []
    for name, x, z, vx, vz, size, facing in tanks:
        y = -1 + size if size >= 1 else -0.4
        out.append(f'''            {{"design": "tank", "name": "{name}",
             "position": [{n(x)}, {n(y)}, {n(z)}], "velocity": [{n(vx)}, 0, {n(vz)}],
             "size": {n(size)}, "angles": [{facing}, 0, 0], {look},
             "gun": {{"mode": "TRACK", "turret_spin": 0.8, "start_angle": "you", "volley": 3, "cooldown": 150}},
             "radar_spin": -6}},''')
    for name, x, z, spin, start in floor_bunkers:
        out.append(f'''            {{"design": "bunker", "name": "{name}", "position": [{n(x)}, -0.7, {n(z)}], "size": 0.6, {look},
             "gun": {{"mode": "SPIN", "turret_spin": {spin}, "start_angle": {start}, "volley": 3}}}},''')
    for name, x, y, z, angles in wall_bunkers:
        out.append(f'''            {{"design": "bunker", "name": "{name}", "position": [{n(x)}, {n(y)}, {n(z)}], "size": 0.6,
             "angles": {angles}, {wall_look},
             "gun": {{"mode": "TRACK", "turret_spin": 1, "volley": 3, {bullets}}},
             "children": [{{"model": cupola_model}}]}},''')
    for name, design, x, y, z, velocity, size, flyer_look, gun in flyers:
        gun_text = f',\n             "gun": {gun}' if gun else ""
        out.append(f'''            {{"design": "{design}", "name": "{name}", "position": [{n(x)}, {n(y)}, {n(z)}], "velocity": {velocity},
             "size": "{size}", "angles": [20, 30, 0], "speeds": (0.9, 0.6, 0.2), {flyer_look}{gun_text}}},''')
    for i, (x, z, vx) in enumerate(drippers):
        out.append(f'''            {{"design": "pyramid", "name": "{word} dripper {i + 1}",
             "position": [{n(x)}, 6.5, {n(z)}], "velocity": [{n(vx)}, 0, 0], "size": "SMALL",
             "angles": [0, 180, 0], "speeds": (0, 0, 0), {wall_look},
             "gun": {{"mode": "DOWN", "volley": 3, "cooldown": 55, {bullets}}},
             "scenery": True}},''')
    return "\n".join(out)


def slime(number=11):
    # THE SLUDGE PIT: the Canyon's size, all SLIME - a slime channel down the middle with walkways across,
    # sludge mounds, toxic barrels, broken sewer walls, slime tanks / bunkers / frames and drippers
    muck = Boxes("SLUDGE", "PALETTE_SLUDGE")
    muck.note("THE SLUDGE PIT, built from SLUDGE (dark green faces, glowing lime edges) and toxic BARRELS (lime).")
    muck.note("YOUR SANDBAGS: a low U round where you start (x 0, z -14), open behind you")
    muck.start_u(colour="SAND", palette="PALETTE_SAND")
    muck.note("THE SEWER WALLS: two broken walls along the slime channel (x -3.4 to -3 and 3 to 3.4), gaps to cross through")
    muck.wall_z(-3.4, -3, -6, [1.2, 0.4, None, 1.6, 1.8, None, 0.2, 1.4, 1.0, None, 1.7, 1.2, None, 0.6, 1.5], "left sewer wall")
    muck.wall_z(3, 3.4, -6, [0.6, 1.5, None, 0.3, 1.7, 1.9, None, 1.1, None, 1.6, 0.4, None, 1.8, 1.0, 1.4], "right sewer wall")
    muck.note("SLUDGE MOUNDS: stepped heaps of muck (3 x 3, then 1 x 1) - cover, and somewhere to stand")
    muck.mound(-12, 6, 3, "left mound")
    muck.mound(9, 9, 3, "right mound")
    muck.note("TOXIC BARRELS: stacks of glowing barrels (1 x 1, 1 or 2 high)")
    muck.pile(-8, -6, [(0, 0, 2), (1, 0, 1)], "barrels, left", colour="SLIME", palette="PALETTE_SLIME")
    muck.pile(7, -5, [(0, 0, 1), (0, 1, 2)], "barrels, right", colour="SLIME", palette="PALETTE_SLIME")
    muck.pile(-7, 11, [(0, 0, 2), (1, 1, 1)], "barrels, far left", colour="SLIME", palette="PALETTE_SLIME")
    muck.pile(11, 2, [(0, 0, 1), (1, 0, 2)], "barrels, far right", colour="SLIME", palette="PALETTE_SLIME")
    muck.note("THE OUTFLOW PIPES: two floor-to-CEILING columns of sludge, jagged (8 layers, each 1 tall)")
    muck.column(-12, -2, 0.9, "left pipe", WOBBLE)
    muck.column(12, 12, 0.9, "right pipe", WOBBLE[::-1])
    muck.note("SLUDGE RINGS round the floor bunkers: low (0.4 tall, under their guns), a GAP facing the back")
    muck.ring(-9, 2, "west ring")
    muck.ring(8, -1, "east ring")
    muck.ring(0, 12, "far ring")

    floor = '''            # THE SLIME CHANNEL down the middle (x -3 to 3), with three WALKWAYS across it (z -3 to -2, 3 to 4, 9 to 10)
            {"type": "slime", "min": (-3, -6), "max": (3, -3)},
            {"type": "slime", "min": (-3, -2), "max": (3, 3)},
            {"type": "slime", "min": (-3, 4), "max": (3, 9)},
            # SLIME POOLS
            {"type": "slime", "min": (-15, 8), "max": (-11, 11)},     # by the left mound
            {"type": "slime", "min": (6, 5), "max": (9, 8)},          # by the right mound
            {"type": "slime", "min": (-11, -11), "max": (-8, -9)},    # near the back left'''
    look = '"colour": SLIME, "palette": PALETTE_SLIME'
    wall_look = '"colour": SLUDGE, "palette": PALETTE_BLACK'
    bullets = '"bullet_colour": (140, 230, 60), "bullet_palette": PALETTE_SLIME'
    lane_z, lane_x = find_lanes(muck.lines)
    spawn = themed_spawn(look, wall_look, bullets, "slime",
        tanks=[("slime tank", -12, pick(lane_z, 7), 0.015, 0, 0.6, -90),
               ("sludge tank", 0, 8, 0, -0.012, 1, 180)],      # up and down the SLIME CHANNEL itself: it's slime-proof
        floor_bunkers=[("west slime bunker", -9, 2, 1.0, 0), ("east slime bunker", 8, -1, -1.1, 90),
                       ("far slime bunker", 0, 12, 1.2, 200)],
        wall_bunkers=[("left wall slime bunker", -15.7, 3, 6, "[0, 0, -90]"),
                      ("right wall slime bunker", 15.7, 3, -3, "[0, 0, 90]"),
                      ("ceiling slime bunker", 6, 6.7, 4, "[0, 180, 0]")],
        flyers=[("slime frame 1", "frame", -6, 3, 3, "[0.02, 0.012, -0.015]", "MEDIUM", look,
                 '{"mode": "TARGET", "volley": 1, "cooldown": 120}'),
                ("slime frame 2", "frame", 7, 4, 10, "[-0.018, -0.01, 0.014]", "MEDIUM", look,
                 '{"mode": "TARGET", "volley": 1, "cooldown": 120}'),
                ("slime pyramid", "pyramid", 0, 4.5, 0, "[0.025, 0, 0.02]", "MEDIUM", look, '{"mode": "DOWN", "volley": 1}'),
                ("slime cube", "cube", -4, 3, 8, "[0.02, 0.015, -0.02]", "LARGE", look, None)],
        drippers=[(-6, -4, 0.02), (5, 1, -0.02), (-2, 7, 0.02), (9, 13, -0.02)])
    return level_text(number, "THE SLUDGE PIT - the Canyon's size, all SLIME: sludge, barrels, a slime channel, slime tanks",
                      "The Sludge Pit", "Toxic slime: it burns AND it sticks. Cross the channel on the walkways.",
                      "(50, 110, 40),                              # a SLIME-green grid", floor, muck, spawn, 0, 0)


PUDDING_THEMES = {
    # One LAYOUT (a giant pudding: walls and steps, three towers to the ceiling, a slow "custard" lake), three LOOKS.
    # Each theme names its colours (from rotation_data.py) and its words. The lake is always a "custard" decal
    # (it slows you to 30%, no harm), just painted in the theme's colour.
    "custard": {
        "title": "THE TRIFLE - the Canyon's size, a giant PUDDING: sponge, jelly towers, a custard lake",
        "name": "The Trifle", "intro": "A giant trifle. The custard won't hurt you - but it's thick, and they WILL.",
        "grid": "(150, 120, 50),                             # a CUSTARD-gold grid",
        "box": ("SPONGE", "PALETTE_SPONGE"), "tower": ("JELLY", "PALETTE_JELLY"),
        "thing": ("CUSTARD", "PALETTE_CUSTARD"), "cube": ("JELLY", "PALETTE_JELLY"), "edge": "CUSTARD",
        "bullet": "(245, 205, 100)", "lake_colour": None,
        "words": {"box": "sponge", "tower": "jelly tower", "lake": "custard", "thing": "custard", "cube": "jelly cube",
                  "tank2": "trifle tank", "giant": "giant jelly"},
    },
    "cupid": {
        "title": "CUPID CANYON - the Trifle's layout, all PINK: candy walls, rose towers, a pink goo lake",
        "name": "Cupid Canyon", "intro": "Everything is pink - and everything still wants you dead. The goo is thick: jump it.",
        "grid": "(150, 60, 100),                             # a PINK grid",
        "box": ("CANDY", "PALETTE_CANDY"), "tower": ("ROSE", "PALETTE_ROSE"),
        "thing": ("CANDY", "PALETTE_CANDY"), "cube": ("ROSE", "PALETTE_ROSE"), "edge": "CANDY",
        "bullet": "(255, 150, 200)", "lake_colour": "(255, 175, 210)",
        "words": {"box": "candy", "tower": "rose tower", "lake": "pink goo", "thing": "cupid", "cube": "heart cube",
                  "tank2": "sweetheart tank", "giant": "giant heart"},
    },
    "fortknox": {
        "title": "FORT KNOX - the Trifle's layout, all GOLD: gold-bar walls, bronze towers, a lake of gold dust",
        "name": "Fort Knox", "intro": "Solid gold. Good luck spotting the gems - and the gold dust slows you right down.",
        "grid": "(130, 100, 30),                             # a GOLD grid",
        "box": ("BULLION", "PALETTE_BULLION"), "tower": ("BRONZE", "PALETTE_BRONZE"),
        "thing": ("BULLION", "PALETTE_BULLION"), "cube": ("BRONZE", "PALETTE_BRONZE"), "edge": "BULLION",
        "bullet": "(255, 215, 60)", "lake_colour": "(235, 190, 60)",
        "words": {"box": "gold bar", "tower": "bronze tower", "lake": "gold dust", "thing": "gold", "cube": "bronze cube",
                  "tank2": "bullion tank", "giant": "giant nugget"},
    },
}


def pudding(number, theme):
    # The PUDDING layout in a theme's colours (see PUDDING_THEMES): walls and steps, three towers, a slow lake,
    # tanks / bunkers / drippers in the theme colour, and cubes that shoot at you
    t = PUDDING_THEMES[theme]
    w = t["words"]
    box_c, box_p = t["box"]
    tower_c, tower_p = t["tower"]
    cake = Boxes(box_c, box_p)
    cake.note(f"{t['name'].upper()}, built from {w['box'].upper()} blocks ({box_c}) and {w['tower'].upper()}S ({tower_c}).")
    cake.note(f"YOUR COVER: a low U of {w['box']} round where you start (x 0, z -14), open behind you")
    cake.start_u()
    cake.note(f"THE {w['box'].upper()} WALL: cover across the front (z -8.6 to -8.2), tall ends, a low middle, gaps, a WINDOW at x 4 to 5")
    cake.wall_x(-7, -8.6, -8.2, [1.5, 1.9, 1.2, None, -0.2, 0.5, -0.4, None, 0.1, None, -0.3, 1.8, 2.0, 1.3],
                f"the {w['box']} wall", window_at=11)
    cake.note(f"THE {w['tower'].upper()}S: three floor-to-CEILING wobbly columns (8 layers, each 1 tall)")
    cake.column(-10, 9, 0.9, f"left {w['tower']}", WOBBLE, colour=tower_c, palette=tower_p)
    cake.column(10, 9, 0.9, f"right {w['tower']}", WOBBLE[::-1], colour=tower_c, palette=tower_p)
    cake.column(0, 13, 0.8, f"back {w['tower']}", WOBBLE, colour=tower_c, palette=tower_p)
    cake.note(f"STEPS: a stepped heap (3 x 3, then 1 x 1) on each side of the {w['lake']} lake")
    cake.mound(-13, -3, 3, "left steps")
    cake.mound(10, -4, 3, "right steps")
    cake.note(f"PILES of {w['box']} blocks to hide behind")
    cake.pile(-6, -4, [(0, 0, 1), (1, 0, 2)], "pile, left")
    cake.pile(4, 7, [(0, 0, 2), (0, 1, 1)], "pile, right")
    cake.pile(-4, 7, [(0, 0, 1), (1, 0, 1), (1, 1, 2)], "pile, middle")
    cake.note("RINGS round the floor bunkers: low (0.4 tall, under their guns), a GAP facing the back")
    cake.ring(-7, 12, "left ring")
    cake.ring(6, 12, "right ring")

    paint = f', "colour": {t["lake_colour"]}' if t["lake_colour"] else ""
    floor = f'''            # THE {w['lake'].upper()} LAKE across the middle (z 0 to 5): a "custard" floor - it doesn't hurt, it SLOWS you right down
            {{"type": "custard", "min": (-16, 0), "max": (16, 5){paint}}},
            # PUDDLES
            {{"type": "custard", "min": (-3, -6), "max": (1, -3){paint}}},     # in front of the wall's gap
            {{"type": "custard", "min": (8, 6), "max": (12, 8){paint}}},       # under the right tower
            {{"type": "custard", "min": (-13, 6), "max": (-9, 8){paint}}},     # under the left tower'''
    thing_c, thing_p = t["thing"]
    cube_c, cube_p = t["cube"]
    look = f'"colour": {thing_c}, "palette": {thing_p}'
    wall_look = f'"colour": {t["edge"]}, "palette": PALETTE_BLACK'
    cube_look = f'"colour": {cube_c}, "palette": {cube_p}'
    bullets = f'"bullet_colour": {t["bullet"]}, "bullet_palette": {thing_p}'
    lane_z, lane_x = find_lanes(cake.lines)
    word = w["thing"]
    spawn = themed_spawn(look, wall_look, bullets, word,
        tanks=[(f"{word} tank", -12, 2.5, 0.015, 0, 0.6, -90),          # it drives through the lake
               (w["tank2"], pick(lane_x, 3), 12, 0, -0.012, 1, 180)],
        floor_bunkers=[(f"left {word} bunker", -7, 12, 1.0, 30), (f"right {word} bunker", 6, 12, -1.0, 150)],
        wall_bunkers=[(f"left wall {word} bunker", -15.7, 3, -6, "[0, 0, -90]"),
                      (f"right wall {word} bunker", 15.7, 3, 4, "[0, 0, 90]"),
                      (f"far wall {word} bunker", -3, 3, 15.7, "[0, -90, 0]"),
                      (f"ceiling {word} bunker", 3, 6.7, -2, "[0, 180, 0]")],
        flyers=[(f"{w['cube']} 1", "cube", -5, 2.5, 3, "[0.022, 0.015, -0.012]", "MEDIUM", cube_look,
                 '{"mode": "TARGET", "volley": 1, "cooldown": 110}'),
                (f"{w['cube']} 2", "cube", 5, 3.5, 6, "[-0.02, -0.012, 0.016]", "MEDIUM", cube_look,
                 '{"mode": "TARGET", "volley": 1, "cooldown": 110}'),
                (f"{word} frame", "frame", 0, 4, 9, "[0.018, 0.01, -0.02]", "MEDIUM", look,
                 '{"mode": "TARGET", "volley": 1, "cooldown": 120}'),
                (f"{word} diamond", "diamond", -8, 4.5, -2, "[0.02, 0, 0.022]", "MEDIUM", look, '{"mode": "DOWN", "volley": 1}'),
                (w["giant"], "cube", 8, 3, 2, "[-0.015, 0.012, 0.02]", "LARGE", cube_look, None)],
        drippers=[(-5, 2, 0.02), (6, 3, -0.02), (-1, -6, 0.02), (5, 9, -0.02)])
    return level_text(number, t["title"], t["name"], t["intro"], t["grid"], floor, cake, spawn, 0, 0)


def custard(number=12):
    # THE TRIFLE: the pudding layout in custard and jelly
    return pudding(number, "custard")


def cupid(number=12):
    # CUPID CANYON: the pudding layout, all pink
    return pudding(number, "cupid")


def fortknox_pudding(number=13):
    # the PUDDING layout, all gold (Fort Knox's first try - the real Fort Knox is vault() below)
    return pudding(number, "fortknox")


def vault(number=13):
    # FORT KNOX: a gold VAULT in the middle (one door, slits to peek through), bunkers guarding it from inside,
    # gold dust on the vault floor (slow), rows of gold-bar stacks outside, tanks patrolling round it.
    # Kept in line with the other big levels: about 100 boxes, every piece 1 unit or less.
    gold = Boxes("BULLION", "PALETTE_BULLION")
    gold.note("FORT KNOX, built from GOLD BARS (BULLION) and BRONZE. The VAULT is x -5 to 5, z -1 to 9, its door facing you.")
    gold.note("YOUR COVER: a low U of gold bars round where you start (x 0, z -14), open behind you")
    gold.start_u()
    gold.note("THE VAULT: walls 0.4 thick, tops at y 1.2 (over your eye: they hide you), a DOOR in the front (x -1 to 1), an eye-height")
    gold.note("SLIT in each side wall (z 4 to 5) to peek and shoot through")
    gold.wall_x(-5, -1, -0.6, [1.2, 1.2, 1.2, 1.2, None, None, 1.2, 1.2, 1.2, 1.2], "vault front wall (the DOOR: x -1 to 1)")
    gold.wall_x(-5, 8.6, 9, [1.2] * 10, "vault back wall")
    for x0, x1, side in ((-5, -4.6, "left"), (4.6, 5, "right")):
        for z in range(-1, 9):
            if z == 4:
                gold.box(x0, -1, z, x1, -0.3, z + 1, f"vault {side} wall: under the SLIT")
                gold.box(x0, 0.4, z, x1, 1.2, z + 1, f"vault {side} wall: over the slit (y -0.3 to 0.4)")
            else:
                gold.box(x0, -1, z, x1, 1.2, z + 1, f"vault {side} wall" if z == -1 else "")
    gold.note("GOLD-BAR STACKS: rows of 1 x 1 stacks (1 or 2 high) down both sides, like a warehouse - cover")
    for x, side in ((-11, "left"), (10, "right")):
        for i, z in enumerate((-7, -3, 1, 5, 9)):
            gold.pile(x, z, [(0, 0, 2 if i % 2 == 0 else 1), (0, 1, 1)], f"bar stack, {side}" if i == 0 else "")
    gold.note("BRONZE PILLARS: two floor-to-CEILING columns at the back corners (8 layers, each 1 tall)")
    gold.column(-13, 13, 0.9, "left pillar", WOBBLE, colour="BRONZE", palette="PALETTE_BRONZE")
    gold.column(13, 13, 0.9, "right pillar", WOBBLE[::-1], colour="BRONZE", palette="PALETTE_BRONZE")
    gold.note("SANDBAG-STYLE BAR WALLS in front of the vault: low cover on the way in")
    gold.wall_x(-4, -5.4, -5, [-0.4, -0.5, None, None, None, None, -0.5, -0.4], "low bar wall")

    floor = '''            # GOLD DUST on the vault floor (a slow "custard" floor in gold): walk in, and you're a slow target
            {"type": "custard", "min": (-4.6, 2), "max": (4.6, 8.6), "colour": (235, 190, 60)},
            # GOLD DUST spilled outside the door
            {"type": "custard", "min": (-2, -3), "max": (2, -1), "colour": (235, 190, 60)}'''
    look = '"colour": BULLION, "palette": PALETTE_BULLION'
    wall_look = '"colour": BULLION, "palette": PALETTE_BLACK'
    cube_look = '"colour": BRONZE, "palette": PALETTE_BRONZE'
    bullets = '"bullet_colour": (255, 215, 60), "bullet_palette": PALETTE_BULLION'
    lane_z, lane_x = find_lanes(gold.lines)
    spawn = themed_spawn(look, wall_look, bullets, "gold",
        tanks=[("guard tank", -12, pick(lane_z, -3), 0.015, 0, 0.6, -90),       # patrols across, in front of the vault
               ("bullion tank", 7, 11.5, -0.012, 0, 1, 90)],                     # patrols BEHIND the vault, between the bar rows
        floor_bunkers=[("vault bunker left", -2.5, 6, 1.0, 0), ("vault bunker right", 2.5, 6, -1.0, 180)],
        wall_bunkers=[("left wall vault bunker", -15.7, 3, 3, "[0, 0, -90]"),
                      ("right wall vault bunker", 15.7, 3, -5, "[0, 0, 90]"),
                      ("far wall vault bunker", 0, 3, 15.7, "[0, -90, 0]"),
                      ("vault ceiling bunker", 0, 6.7, 4, "[0, 180, 0]")],
        flyers=[("bronze cube 1", "cube", -7, 3, 2, "[0.02, 0.012, -0.015]", "MEDIUM", cube_look,
                 '{"mode": "TARGET", "volley": 1, "cooldown": 110}'),
                ("bronze cube 2", "cube", 7, 3.5, 8, "[-0.018, -0.01, 0.016]", "MEDIUM", cube_look,
                 '{"mode": "TARGET", "volley": 1, "cooldown": 110}'),
                ("gold frame", "frame", 0, 4.5, -4, "[0.02, 0.01, 0.018]", "MEDIUM", look,
                 '{"mode": "TARGET", "volley": 1, "cooldown": 120}'),
                ("gold diamond", "diamond", -8, 4.5, 10, "[0.02, 0, -0.02]", "MEDIUM", look, '{"mode": "DOWN", "volley": 1}')],
        drippers=[(-8, -1, 0.02), (8, 3, -0.02), (-6, 11, 0.02), (7, -8, -0.02)])
    return level_text(number, "FORT KNOX - the Canyon's size, a gold VAULT: one door, bunkers inside, gold-bar stacks, tanks on guard",
                      "Fort Knox", "Break into the vault. One door, guards inside - and good luck spotting the gems.",
                      "(130, 100, 30),                             # a GOLD grid", floor, gold, spawn, 0, 0)


def pick(options, wanted):
    # the lane nearest where we'd like it (no clear lane at all? then where we'd like it: tanks bounce off boxes anyway)
    if not options:
        return wanted
    return min(options, key=lambda value: abs(value - wanted))


RECIPES = {"glacier": glacier, "furnace": furnace, "slime": slime, "custard": custard,
           "cupid": cupid, "fortknox": vault, "gold pudding": fortknox_pudding}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in RECIPES:
        print("usage: py level_builder.py " + " | ".join(RECIPES) + " [level number]")
        sys.exit(1)
    recipe = RECIPES[sys.argv[1]]
    print(recipe(int(sys.argv[2])) if len(sys.argv) > 2 else recipe())
