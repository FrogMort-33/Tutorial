# plan_view.py - PLAN VIEWS: every level seen from straight above, saved as pictures. Run it any time:
#
#   py plan_view.py            -> every level, into screenshots/plans/ (plus all_levels.png: them all on one sheet)
#   py plan_view.py 9 10       -> just levels 9 and 10
#
# It loads each level exactly as the game does (load_level), so what you see is what you get - even the gems,
# which land in their real (random) spots. The window is never shown (SDL's "dummy" video driver).
#
# What's drawn:
#   the room's floor and its grid (the level's grid colour), and the floor decals (lava, ice, slime, custard ...)
#   BOXES: filled in their palette's first colour, LIGHTER the taller they are, outlined in their own colour
#   TANKS: a body with a line showing which way they face (and an arrow: which way they drive)
#   BUNKERS: a square (floor), or a square with a dot (on a wall or the ceiling)
#   SHAPES: a circle the size of the shape;  drippers (scenery): a small x;  GEMS: little gold diamonds
#   YOU: a white dot with an arrow, where you start
import os
import sys
os.environ["SDL_VIDEODRIVER"] = "dummy"          # no window
os.environ["SDL_AUDIODRIVER"] = "dummy"          # no sound
import pygame
import rotation_functions as rf
from rotation_data import *
from rotation_levels import LEVELS

SIZE = 720                    # each plan is SIZE x SIZE pixels, plus the title strip
TITLE = 70                    # the title strip at the top
MARGIN = 30                   # round the room
OUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots", "plans")
pygame.font.init()
title_font = pygame.font.SysFont(None, 40)
small_font = pygame.font.SysFont(None, 24)


def lighter(colour, amount):
    # amount 0 = the colour itself, 1 = white
    return tuple(int(c + (255 - c) * amount) for c in colour)


def plan(number):
    rf.load_level(number)
    level = LEVELS[number]
    width = WORLD_MAX[0] - WORLD_MIN[0]
    depth = WORLD_MAX[2] - WORLD_MIN[2]
    scale = (SIZE - (2 * MARGIN)) / max(width, depth)               # pixels per world unit

    def at(x, z):
        # world (x, z) -> picture (px, py): +x to the right, +z UP the picture (like the mini-map)
        px = MARGIN + ((x - WORLD_MIN[0]) * scale) + ((SIZE - (2 * MARGIN)) - (width * scale)) / 2
        py = TITLE + SIZE - MARGIN - ((z - WORLD_MIN[2]) * scale) - ((SIZE - (2 * MARGIN)) - (depth * scale)) / 2
        return (px, py)

    picture = pygame.Surface((SIZE, SIZE + TITLE))
    picture.fill((12, 14, 18))
    grid = level_look["grid_colour"]

    # the floor and its grid, 1 unit apart
    floor = [at(WORLD_MIN[0], WORLD_MIN[2]), at(WORLD_MAX[0], WORLD_MIN[2]), at(WORLD_MAX[0], WORLD_MAX[2]), at(WORLD_MIN[0], WORLD_MAX[2])]
    pygame.draw.polygon(picture, (0, 0, 0), floor)
    for x in range(int(WORLD_MIN[0]), int(WORLD_MAX[0]) + 1):
        pygame.draw.line(picture, grid, at(x, WORLD_MIN[2]), at(x, WORLD_MAX[2]))
    for z in range(int(WORLD_MIN[2]), int(WORLD_MAX[2]) + 1):
        pygame.draw.line(picture, grid, at(WORLD_MIN[0], z), at(WORLD_MAX[0], z))

    # the floor decals (the gold origin mark too)
    for decal in FLOOR_SHAPES:
        pygame.draw.polygon(picture, decal["colour"], [at(x, z) for x, z in decal["corners"]])

    # the boxes, lowest first, so taller ones are drawn on top; lighter the taller they are
    floor_y, ceiling_y = WORLD_MIN[1], WORLD_MAX[1]
    for box in sorted(BOXES, key=lambda b: b["max"][1]):
        (x0, y0, z0), (x1, y1, z1) = box["min"], box["max"]
        height = (y1 - floor_y) / (ceiling_y - floor_y)              # 0 = flat on the floor, 1 = up to the ceiling
        fill = lighter(box["palette"][0], 0.15 + (0.45 * height))
        corners = [at(x0, z0), at(x1, z0), at(x1, z1), at(x0, z1)]
        pygame.draw.polygon(picture, fill, corners)
        pygame.draw.polygon(picture, box["colour"], corners, 1)

    # the things
    counts = {"tanks": 0, "bunkers": 0, "shapes": 0, "drippers": 0, "gems": 0}
    for thing in things:
        if "parent" in thing:
            continue                                                  # turrets ride on their hull
        x, y, z = thing["position"]
        cx, cy = at(x, z)
        colour = thing["colour"]
        reach = max(3, thing.get("reach", 0.5) * scale)
        if thing.get("gem"):
            counts["gems"] = counts["gems"] + 1
            r = 6
            pygame.draw.polygon(picture, (255, 215, 0), [(cx, cy - r), (cx + r * 0.7, cy), (cx, cy + r), (cx - r * 0.7, cy)])
            pygame.draw.polygon(picture, (255, 255, 255), [(cx, cy - r), (cx + r * 0.7, cy), (cx, cy + r), (cx - r * 0.7, cy)], 1)
        elif thing.get("scenery"):
            counts["drippers"] = counts["drippers"] + 1
            pygame.draw.line(picture, colour, (cx - 6, cy - 6), (cx + 6, cy + 6), 3)
            pygame.draw.line(picture, colour, (cx - 6, cy + 6), (cx + 6, cy - 6), 3)
        elif thing["model"] is DESIGNS_MODEL["bunker"]:
            counts["bunkers"] = counts["bunkers"] + 1
            half = 0.6 * scale
            rect = pygame.Rect(cx - half, cy - half, half * 2, half * 2)
            pygame.draw.rect(picture, colour, rect)
            pygame.draw.rect(picture, (255, 255, 255), rect, 2)
            if y > WORLD_MIN[1] + 1:                                  # on a wall or the ceiling
                pygame.draw.circle(picture, (0, 0, 0), (cx, cy), max(3, half * 0.4))
        elif thing["model"] is DESIGNS_MODEL["tank"]:
            counts["tanks"] = counts["tanks"] + 1
            pygame.draw.circle(picture, colour, (cx, cy), reach * 0.8)
            pygame.draw.circle(picture, (255, 255, 255), (cx, cy), reach * 0.8, 2)
            vx, vz = thing["velocity"][0], thing["velocity"][2]
            speed = (vx * vx + vz * vz) ** 0.5
            if speed > 0:                                             # an ARROW: which way it drives
                ex, ey = at(x + vx / speed * 2.5, z + vz / speed * 2.5)
                pygame.draw.line(picture, (255, 255, 255), (cx, cy), (ex, ey), 2)
                pygame.draw.circle(picture, (255, 255, 255), (ex, ey), 4)
        else:
            counts["shapes"] = counts["shapes"] + 1
            pygame.draw.circle(picture, colour, (cx, cy), reach, 3)

    # YOU: where you start, and which way you face
    start = level["start"]
    sx, sy = at(start["x"], start["z"])
    pygame.draw.circle(picture, (255, 255, 255), (sx, sy), 8)
    face = rf.rotate_y((0, 0, 1), start["turn"])
    fx, fy = at(start["x"] + face[0] * 2.5, start["z"] + face[2] * 2.5)
    pygame.draw.line(picture, (255, 255, 255), (sx, sy), (fx, fy), 3)

    # the title strip
    picture.blit(title_font.render(f"Level {number}: {level['name']}", True, (255, 215, 0)), (16, 10))
    info = (f"{width:g} x {depth:g}   boxes {len(BOXES)}   tanks {counts['tanks']}   bunkers {counts['bunkers']}   "
            f"shapes {counts['shapes']}   drippers {counts['drippers']}   gems {counts['gems']}")
    picture.blit(small_font.render(info, True, (200, 205, 215)), (18, 44))
    return picture


# which models are tanks and bunkers (to tell them apart on the plan)
from rotation_levels import DESIGNS
DESIGNS_MODEL = {"tank": DESIGNS["tank"]["model"], "bunker": DESIGNS["bunker"]["model"]}

if __name__ == "__main__":
    numbers = [int(a) for a in sys.argv[1:]] or sorted(LEVELS)
    os.makedirs(OUT_FOLDER, exist_ok=True)
    plans = []
    for number in numbers:
        picture = plan(number)
        path = os.path.join(OUT_FOLDER, f"level_{number:02d}.png")
        pygame.image.save(picture, path)
        plans.append(picture)
        print("saved", path)
    if len(plans) > 1:                                               # them all on one sheet, 4 across, half size
        across = 4
        tile_w, tile_h = SIZE // 2, (SIZE + TITLE) // 2
        sheet = pygame.Surface((tile_w * across, tile_h * ((len(plans) + across - 1) // across)))
        sheet.fill((30, 32, 38))
        for i, picture in enumerate(plans):
            sheet.blit(pygame.transform.smoothscale(picture, (tile_w, tile_h)), ((i % across) * tile_w, (i // across) * tile_h))
        path = os.path.join(OUT_FOLDER, "all_levels.png")
        pygame.image.save(sheet, path)
        print("saved", path)
