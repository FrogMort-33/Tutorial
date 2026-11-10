# Draws the course map PNG, one "you are here" version per lesson.
# Usage: python3 course_map.py OUTDIR   -> writes course_map_<key>.png for every lesson
import sys, math
from PIL import Image, ImageDraw, ImageFont

W, H = 1800, 1180
BG = (16, 20, 24)
FG = (232, 238, 234)
MUTED = (150, 162, 156)
DIM = (105, 115, 110)
CARD = (26, 32, 36)
F = "/usr/share/fonts/truetype/dejavu/"
def font(size, bold=False, mono=False):
    name = ("DejaVuSansMono" if mono else "DejaVuSans") + ("-Bold" if bold else "") + ".ttf"
    return ImageFont.truetype(F + name, size)

# key, label, title, colour, "you learn", "the program can now"
LESSONS = [
 ("1",  "LESSON 1",  "From one line to a 3D cube", (75, 224, 140),
        "points, edges, divide by z", "draws a still wire cube"),
 ("2",  "LESSON 2",  "Making the cube spin",       (60, 210, 200),
        "angles, sin and cos, rotate_y", "spins the cube round y"),
 ("2b", "LESSON 2B", "Tip, roll and tumble",       (80, 160, 255),
        "rotate_x, rotate_z, the order", "tumbles on all 3 axes"),
 ("3",  "LESSON 3",  "Solid faces",                (255, 196, 60),
        "painter's sort, clock test, light", "shows a solid, lit cube"),
 ("4",  "LESSON 4",  "Moving the camera",          (255, 110, 170),
        "to_camera(), NEAR, walking", "lets you walk round"),
 ("5",  "LESSON 5",  "A small world",              (180, 120, 255),
        "floor grid, many shapes", "fills a world with shapes"),
 ("6",  "LESSON 6",  "Matrices",                   (110, 140, 255),
        "every turn as one number table", "does the same with tidier maths"),
 ("7",  "LESSON 7",  "A mini game",                (255, 130, 70),
        "distance check, score, timer", "becomes a cube-collecting game"),
]

# ---------- small icons, each drawn inside a box (x, y, w, h) ----------
def proj(p, cx, cy, s, dist=4.0):
    x, y, z = p
    return (cx + (x * s) / (z + dist), cy - (y * s) / (z + dist))

CUBE = [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]
EDGES = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
def turned(ay, ax=0.0):
    out = []
    for x, y, z in CUBE:
        c, s = math.cos(ay), math.sin(ay)
        x, z = (x * c) - (z * s), (x * s) + (z * c)
        c, s = math.cos(ax), math.sin(ax)
        y, z = (y * c) - (z * s), (y * s) + (z * c)
        out.append((x, y, z))
    return out

def wire_cube(d, cx, cy, s, col, ay=0.0, ax=0.0, w=3):
    pts = [proj(p, cx, cy, s) for p in turned(ay, ax)]
    for a, b in EDGES:
        d.line([pts[a], pts[b]], fill=col, width=w)
    return pts

def arc_arrow(d, cx, cy, rx, ry, col, start=200, end=500, w=4):
    box = [cx - rx, cy - ry, cx + rx, cy + ry]
    d.arc(box, start, end, fill=col, width=w)
    t = math.radians(end)
    ex, ey = cx + rx * math.cos(t), cy + ry * math.sin(t)
    d.polygon([(ex + 12, ey), (ex - 4, ey - 9), (ex - 4, ey + 9)], fill=col)

def icon(d, key, x, y, w, h, col, on):
    cx, cy = x + w / 2, y + h / 2
    c = col if on else DIM
    if key == "1":
        wire_cube(d, cx, cy, 150, c)
    elif key == "2":
        wire_cube(d, cx, cy + 12, 120, c, ay=0.5)
        arc_arrow(d, cx, cy - 30, 60, 12, c, 200, 480)
    elif key == "2b":
        wire_cube(d, cx, cy, 140, c, ay=0.5, ax=-0.4)
        if on:
            d.line([cx - 75, cy, cx + 75, cy], fill=(255, 90, 90), width=3)
            d.line([cx, cy - 60, cx, cy + 60], fill=(75, 224, 140), width=3)
            d.line([cx - 35, cy + 40, cx + 35, cy - 40], fill=(90, 160, 255), width=3)
    elif key == "3":
        pts = [proj(p, cx, cy, 150) for p in turned(0.6, -0.45)]
        faces = [((3,2,6,7), 1.0), ((0,1,2,3), 0.7), ((0,3,7,4), 0.45)]
        for f, sh in faces:
            fill = tuple(int(v * sh) for v in (col if on else DIM))
            d.polygon([pts[i] for i in f], fill=fill, outline=BG)
    elif key == "4":
        # a little eye/camera on the left looking at a cube on the right
        ex, ey = x + 40, cy
        d.polygon([(ex, ey), (ex + 120, ey - 45), (ex + 120, ey + 45)], fill=None, outline=c)
        d.ellipse([ex - 22, ey - 14, ex + 22, ey + 14], outline=c, width=3)
        d.ellipse([ex - 6, ey - 6, ex + 6, ey + 6], fill=c)
        wire_cube(d, x + w - 60, cy, 90, c, ay=0.5, w=3)
    elif key == "5":
        # perspective floor grid + three small cubes
        hz = y + 25
        for i in range(-4, 5):
            d.line([cx + i * 10, hz, cx + i * 30, y + h], fill=c if on else DIM, width=2)
        for j, yy in enumerate([hz + 6, hz + 16, hz + 31, hz + 52, y + h]):
            half = 40 + (yy - hz) * 1.0
            d.line([cx - half, yy, cx + half, yy], fill=c, width=2)
        for (px, py, s) in [(cx - 70, y + 62, 40), (cx + 60, y + 54, 34), (cx + 5, y + 40, 26)]:
            wire_cube(d, px, py, s, FG if on else DIM, ay=0.5, w=2)
    elif key == "6":
        f = font(26, mono=True)
        rows = ["cos  0  -sin", " 0   1    0 ", "sin  0  cos"]
        for i, r in enumerate(rows):
            d.text((cx, y + 22 + i * 32), r, font=f, fill=c, anchor="mm")
        for side in (-1, 1):
            bx = cx + side * 115
            d.line([bx, y + 4, bx, y + 104], fill=c, width=3)
            d.line([bx, y + 4, bx - side * 12, y + 4], fill=c, width=3)
            d.line([bx, y + 104, bx - side * 12, y + 104], fill=c, width=3)
    elif key == "7":
        wire_cube(d, cx - 55, cy + 10, 100, c, ay=0.5)
        # star + score
        sx, sy, r1, r2 = cx + 70, cy - 25, 28, 12
        star = []
        for i in range(10):
            r = r1 if i % 2 == 0 else r2
            a = math.radians(-90 + i * 36)
            star.append((sx + r * math.cos(a), sy + r * math.sin(a)))
        d.polygon(star, fill=c)
        d.text((cx + 70, cy + 32), "SCORE 3", font=font(20, True, True), fill=c, anchor="mm")

def fit(d, text, size, maxw, bold=False):
    # shrink the font a point at a time until the text fits inside maxw pixels
    while size > 12 and d.textlength(text, font=font(size, bold)) > maxw:
        size -= 1
    return font(size, bold)

def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = wd
    lines.append(cur)
    return lines

# ---------- the board ----------
CW, CH, GAP, LEFT = 380, 330, 60, 50
ROW_Y = [200, 660]
def card_xy(i):
    # snake: row 1 left->right (lessons 1,2,2B,3), row 2 right->left (4,5,6,7)
    row, col = divmod(i, 4)
    if row == 1: col = 3 - col
    return LEFT + col * (CW + GAP), ROW_Y[row]

def draw(current):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    ci = [l[0] for l in LESSONS].index(current)
    cur = LESSONS[ci]

    d.text((W / 2, 52), "Wireframe 3D course map", font=font(50, True), fill=FG, anchor="mm")
    d.text((W / 2, 108), "8 lessons, one program that grows a little each time. Follow the road from Lesson 1 to the game.",
           font=font(26), fill=MUTED, anchor="mm")

    # road behind the cards: one thick line through every card centre
    centres = [(card_xy(i)[0] + CW / 2, card_xy(i)[1] + CH / 2) for i in range(8)]
    for i in range(7):
        a, b = centres[i], centres[i + 1]
        done = i < ci
        col = LESSONS[i][3] if done else (52, 60, 58)
        if i == 3:   # the bend from Lesson 3 down to Lesson 4, on the right edge
            rx = a[0] + CW / 2 + 28
            d.line([a, (rx, a[1]), (rx, b[1]), b], fill=col, width=14, joint="curve")
            mx, my = rx, (a[1] + b[1]) / 2
            d.polygon([(mx - 16, my - 8), (mx + 16, my - 8), (mx, my + 16)], fill=FG if done else MUTED)
        else:
            d.line([a, b], fill=col, width=14)
            mx, my = (a[0] + b[0]) / 2, a[1]
            s = 1 if b[0] > a[0] else -1
            d.polygon([(mx - s * 10, my - 18), (mx - s * 10, my + 18), (mx + s * 18, my)], fill=FG if done else MUTED)

    for i, (key, label, title, col, learn, can) in enumerate(LESSONS):
        x, y = card_xy(i)
        is_cur, is_done = (i == ci), (i < ci)
        on = is_cur or is_done
        tcol = FG if on else MUTED
        if is_cur:   # glow
            for g in range(5, 0, -1):
                d.rounded_rectangle([x - g * 4, y - g * 4, x + CW + g * 4, y + CH + g * 4], 22 + g * 4,
                                    outline=tuple(int(v * (0.12 * (6 - g))) for v in col), width=4)
        d.rounded_rectangle([x, y, x + CW, y + CH], 20, fill=CARD,
                            outline=col if on else (60, 68, 66), width=6 if is_cur else 3)
        # header band
        band = col if on else tuple(int(v * 0.35) for v in col)   # future lessons: same colour, darker
        d.rounded_rectangle([x, y, x + CW, y + 56], 20, fill=band)
        d.rectangle([x, y + 36, x + CW, y + 56], fill=band)
        d.text((x + 20, y + 28), label, font=font(28, True), fill=BG if on else FG, anchor="lm")
        if is_done:
            d.text((x + CW - 20, y + 28), "done", font=font(22, True), fill=BG, anchor="rm")
        elif is_cur:
            d.text((x + CW - 20, y + 28), "TODAY", font=font(22, True), fill=BG, anchor="rm")
        # title
        d.text((x + CW / 2, y + 86), title, font=fit(d, title, 25, CW - 40, True), fill=tcol, anchor="mm")
        # icon
        icon(d, key, x + 60, y + 108, CW - 120, 110, col, on)
        # two short lines
        t1, t2 = "learn: " + learn, "then it " + can
        d.text((x + 20, y + 245), t1, font=fit(d, t1, 19, CW - 40), fill=tcol)
        d.text((x + 20, y + 280), t2, font=fit(d, t2, 19, CW - 40), fill=(col if on else MUTED))
        if is_cur:
            # "you are here" pin above the card
            px = x + CW / 2
            d.rounded_rectangle([px - 120, y - 62, px + 120, y - 18], 22, fill=col)
            d.polygon([(px - 14, y - 19), (px + 14, y - 19), (px, y - 2)], fill=col)
            d.text((px, y - 40), "YOU ARE HERE", font=font(26, True), fill=BG, anchor="mm")

    # bottom strip: before / today / next
    sy = 1040
    prev = LESSONS[ci - 1] if ci > 0 else None
    nxt = LESSONS[ci + 1] if ci < 7 else None
    parts = [
        ("BEFORE", prev[1] + ": " + prev[2] if prev else "nothing: this is the start", prev[3] if prev else MUTED),
        ("TODAY", cur[1] + ": " + cur[2], cur[3]),
        ("NEXT", nxt[1] + ": " + nxt[2] if nxt else "you have a finished game!", nxt[3] if nxt else MUTED),
    ]
    bw = (W - 2 * LEFT - 2 * 30) / 3
    for k, (tag, text, col) in enumerate(parts):
        bx = LEFT + k * (bw + 30)
        d.rounded_rectangle([bx, sy, bx + bw, sy + 100], 16, fill=CARD, outline=col, width=4 if tag == "TODAY" else 2)
        d.text((bx + 20, sy + 28), tag, font=font(22, True), fill=col, anchor="lm")
        d.text((bx + 20, sy + 68), text, font=font(23, True if tag == "TODAY" else False), fill=FG, anchor="lm")
        if k < 2:
            ax = bx + bw + 15
            d.polygon([(ax - 8, sy + 38), (ax - 8, sy + 62), (ax + 10, sy + 50)], fill=MUTED)
    return img

if __name__ == "__main__":
    out = sys.argv[1]
    for l in LESSONS:
        draw(l[0]).save(f"{out}/course_map_{l[0]}.png", optimize=True)
