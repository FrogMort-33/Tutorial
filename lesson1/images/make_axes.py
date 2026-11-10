# Draws the two Lesson 1 diagrams with SCREEN axes:
#   d1b_line_axes.png  (Fig 1.1.2)  and  d2_points_and_edges.png (Fig 1.2.1)
from PIL import Image, ImageDraw, ImageFont
F = "/usr/share/fonts/truetype/dejavu/"
def font(sz, bold=False, mono=False):
    n = "DejaVuSansMono" + ("-Bold" if bold else "") if mono else "DejaVuSans" + ("-Bold" if bold else "")
    return ImageFont.truetype(F + n + ".ttf", sz)
BG=(17,20,25); FG=(235,235,235); GREY=(130,138,148); DIM=(60,66,76)
BLUE=(80,160,255); YEL=(255,210,60); RED=(255,95,95); GRN=(60,220,110)

def arrow(d, a, b, col, w=5, head=18):
    d.line([a, b], fill=col, width=w)
    (x1,y1),(x2,y2) = a,b
    if x1 == x2:   # vertical, pointing down or up
        s = 1 if y2 > y1 else -1
        d.polygon([(x2, y2+s*4), (x2-head*0.6, y2-s*head), (x2+head*0.6, y2-s*head)], fill=col)
    else:
        s = 1 if x2 > x1 else -1
        d.polygon([(x2+s*4, y2), (x2-s*head, y2-head*0.6), (x2-s*head, y2+head*0.6)], fill=col)

def window_frame(d, ox, oy, S, title_y=None):
    """Draw the 800 x 600 window with SCREEN axes, ticks every 100 px.
    ox, oy = where pixel (0, 0) goes on the picture; S = picture px per screen px."""
    W, H = 800, 600
    P = lambda x, y: (ox + x*S, oy + y*S)
    # faint grid every 100 px
    for x in range(100, W, 100): d.line([P(x,0), P(x,H)], fill=DIM, width=1)
    for y in range(100, H, 100): d.line([P(0,y), P(W,y)], fill=DIM, width=1)
    d.rectangle([P(0,0), P(W,H)], outline=GREY, width=3)
    f = font(22)
    # x axis along the top edge, ticks and numbers above it
    for x in range(100, W+1, 100):   # 0 is the origin, labelled (0, 0)
        X, Y = P(x, 0); d.line([(X, Y-10), (X, Y)], fill=BLUE, width=3)
        t = str(x); tw = d.textlength(t, font=f); d.text((X-tw/2, Y-38), t, font=f, fill=BLUE)
    # y axis down the left edge, ticks and numbers left of it
    for y in range(100, H+1, 100):
        X, Y = P(0, y); d.line([(X-10, Y), (X, Y)], fill=YEL, width=3)
        t = str(y); tw = d.textlength(t, font=f); d.text((X-18-tw, Y-13), t, font=f, fill=YEL)
    # axis arrows: +x right (past the window), +y down (past the window)
    arrow(d, P(0,0), (P(W,0)[0]+60, P(0,0)[1]), BLUE)
    arrow(d, P(0,0), (P(0,0)[0], P(0,H)[1]+60), YEL)
    fb = font(26, True)
    d.text((P(W,0)[0]+70, P(0,0)[1]-16), "+x", font=fb, fill=BLUE)
    d.text((P(W,0)[0]+70, P(0,0)[1]+16), "right", font=font(20), fill=BLUE)
    d.text((P(0,H)[0]-22, P(0,H)[1]+66), "+y down", font=fb, fill=YEL)
    # the - ends: off the window, drawn short and grey
    X0, Y0 = P(0,0)
    d.line([(X0-70, Y0), (X0, Y0)], fill=GREY, width=2); d.text((X0-120, Y0-46), "-x", font=font(22,True), fill=GREY)
    d.line([(X0, Y0-70), (X0, Y0)], fill=GREY, width=2); d.text((X0+10, Y0-92), "-y", font=font(22,True), fill=GREY)
    # origin
    d.ellipse([X0-9, Y0-9, X0+9, Y0+9], fill=RED)
    d.text((X0-112, Y0+8), "(0, 0)", font=font(22,True), fill=RED)
    # far corner
    Xc, Yc = P(W,H); d.text((Xc-60, Yc+12), "(800, 600)", font=font(20), fill=GREY)
    return P

def point(d, P, x, y, label, col, dx=14, dy=-40):
    X, Y = P(x, y)
    d.ellipse([X-9, Y-9, X+9, Y+9], fill=col)
    d.text((X+dx, Y+dy), label, font=font(26, True), fill=col)

# ---------------- Fig 1.1.2: one line ----------------
S = 1.25; ox, oy = 170, 200
img = Image.new("RGB", (int(ox + 800*S + 220), int(oy + 600*S + 170)), BG); d = ImageDraw.Draw(img)
t = "step1_line.py on SCREEN coordinates (pixels)"
d.text(((img.width - d.textlength(t, font=font(34,True)))/2, 30), t, font=font(34,True), fill=FG)
P = window_frame(d, ox, oy, S)
LINE_THICKNESS = 2
d.line([P(100,500), P(700,100)], fill=GRN, width=round(LINE_THICKNESS*S))
# dashed guides from each point to both axes, so the numbers can be read off
def guides(x, y):
    X, Y = P(x, y); X0, Y0 = P(0, 0)
    for a in range(int(Y0), int(Y), 12): d.line([(X, a), (X, min(a+6, Y))], fill=GREY, width=2)
    for a in range(int(X0), int(X), 12): d.line([(a, Y), (min(a+6, X), Y)], fill=GREY, width=2)
guides(100, 500); guides(700, 100)
point(d, P, 100, 500, "start_point (100, 500)", GRN, dx=14, dy=8)
point(d, P, 700, 100, "end_point (700, 100)", GRN, dx=-160, dy=-48)
note = "green line: LINE_THICKNESS = 2 pixels wide"
d.text((P(0,600)[0], P(0,600)[1]+110), note, font=font(24), fill=GRN)
img.save("d1b_line_axes.png")

# ---------------- Fig 1.2.1: points and edges ----------------
S = 1.1; ox, oy = 170, 200
img = Image.new("RGB", (int(ox + 800*S + 820), int(oy + 600*S + 170)), BG); d = ImageDraw.Draw(img)
t = "A shape = POINTS (where) + EDGES (what joins), on SCREEN coordinates"
d.text(((img.width - d.textlength(t, font=font(34,True)))/2, 30), t, font=font(34,True), fill=FG)
P = window_frame(d, ox, oy, S)
pts = [(300,450),(500,450),(500,250),(300,250),(400,150)]
edges = [(0,1),(1,2),(2,3),(3,0),(3,4),(4,2)]
for a, b in edges: d.line([P(*pts[a]), P(*pts[b])], fill=GRN, width=4)
offs = [(-180,10),(14,10),(14,-44),(-185,-44),(14,-48)]   # where each label sits
for n,(x,y) in enumerate(pts):
    point(d, P, x, y, f"{n} ({x}, {y})", YEL, *offs[n])
# code panel on the right
cx = int(ox + 800*S + 150); cy = 230; m = font(28, mono=True)
d.text((cx, cy), "points = [", font=m, fill=FG)
for n,(x,y) in enumerate(pts):
    d.text((cx+40, cy+48*(n+1)), f"({x}, {y}),  # {n}", font=m, fill=YEL)
d.text((cx, cy+48*6), "]", font=m, fill=FG)
d.text((cx, cy+380), "edges = [(0,1), (1,2), (2,3),", font=m, fill=FG)
d.text((cx, cy+420), "         (3,0), (3,4), (4,2)]", font=m, fill=FG)
d.text((cx, cy+500), "edge (3, 4) means:", font=font(28,True), fill=GRN)
d.text((cx, cy+540), "draw a line from point 3", font=font(26), fill=GRN)
d.text((cx, cy+574), "(300, 250) to point 4 (400, 150)", font=font(26), fill=GRN)
img.save("d2_points_and_edges.png")
print("ok")
