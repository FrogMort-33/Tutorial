# Fig 1.4.6 (new): how screen_x is worked out, seen from ABOVE.
# Same point as the side view (Fig 1.4.5): x = 1, y = 1, z = 4, FOCAL 400.
from PIL import Image, ImageDraw, ImageFont
F = "/usr/share/fonts/truetype/dejavu/"
def font(sz, bold=False, mono=False):
    n = ("DejaVuSansMono" if mono else "DejaVuSans") + ("-Bold" if bold else "")
    return ImageFont.truetype(F + n + ".ttf", sz)
BG=(17,20,25); FG=(235,235,235); GREY=(130,138,148); DIM=(60,66,76)
BLUE=(80,160,255); YEL=(255,210,60); ORA=(255,150,50); GRN=(60,220,110); RED=(255,95,95)

def arrow(d, a, b, col, w=4, head=18):
    import math
    d.line([a, b], fill=col, width=w)
    ang = math.atan2(b[1]-a[1], b[0]-a[0])
    p1 = (b[0]-head*math.cos(ang-0.4), b[1]-head*math.sin(ang-0.4))
    p2 = (b[0]-head*math.cos(ang+0.4), b[1]-head*math.sin(ang+0.4))
    d.polygon([b, p1, p2], fill=col)
def darrow(d, a, b, col, w=4):
    arrow(d, a, b, col, w); arrow(d, b, a, col, w)

img = Image.new("RGB", (1800, 1200), BG); d = ImageDraw.Draw(img, "RGBA")
t = "Working out x: the same two triangles, seen from ABOVE"
d.text(((1800 - d.textlength(t, font=font(40,True)))/2, 28), t, font=font(40,True), fill=FG)

# ---- the top-down picture. Eye = (0, 0, 0). +x right, +z up the page ----
EX, EY = 440, 1000          # where the eye is drawn
U = 180                     # drawing pixels per world unit (z = 4 -> 720)
SCR = 300                   # drawing distance from eye to the screen line
P = lambda x, z: (EX + x*U, EY - z*U)          # world (x, z) -> drawing
# axes through the eye, both ends labelled
arrow(d, (EX, EY), (EX + 330, EY), BLUE); d.line([(EX-360, EY), (EX, EY)], fill=GREY, width=2)
d.text((EX+340, EY-18), "+x right", font=font(26,True), fill=BLUE)
d.text((EX-410, EY-18), "-x", font=font(26,True), fill=GREY)
arrow(d, (EX, EY), (EX, EY-830), ORA); d.line([(EX, EY), (EX, EY+80)], fill=GREY, width=2)
d.text((EX-150, EY-880), "+z away from you", font=font(26,True), fill=ORA)
d.text((EX-60, EY+80), "-z", font=font(26,True), fill=GREY)
# the screen (glass) as a line across, FOCAL from the eye
sy = EY - SCR
d.line([(EX-60, sy), (EX+250, sy)], fill=FG, width=4)
d.text((EX+262, sy-18), "screen (glass)", font=font(26,True), fill=FG)
# point and triangles
px, pz = P(1, 4)
off_draw = (1*U) * SCR / (4*U)                     # where the sight line crosses the glass
d.polygon([(EX, EY), (EX, pz), (px, pz)], fill=(60,220,110,40))
d.polygon([(EX, EY), (EX, sy), (EX+off_draw, sy)], fill=(255,210,60,90))
d.line([(EX, EY), (px, pz)], fill=FG, width=3)                 # sight line eye -> point
d.line([(EX, pz), (px, pz)], fill=GRN, width=7)                # x = 1
d.line([(EX, sy), (EX+off_draw, sy)], fill=YEL, width=9)       # offset_x
d.ellipse([px-14, pz-14, px+14, pz+14], fill=GRN)
d.text((px+22, pz-36), "point", font=font(28,True), fill=GRN)
d.text((px+22, pz+2), "x = 1, z = 4", font=font(26), fill=GRN)
d.text((EX+20, pz-50), "x = 1", font=font(30,True), fill=GRN)
d.text((EX+off_draw+14, sy+8), "offset_x", font=font(26,True), fill=YEL)
d.ellipse([EX-14, EY-14, EX+14, EY+14], fill=BLUE)
d.text((EX+20, EY+16), "eye (0, 0, 0)", font=font(26,True), fill=BLUE)
# distance arrows on the left
darrow(d, (EX-90, EY), (EX-90, sy), ORA)
d.text((EX-290, (EY+sy)/2-40), "FOCAL =", font=font(26,True), fill=ORA)
d.text((EX-290, (EY+sy)/2-6), "400 pixels", font=font(26,True), fill=ORA)
darrow(d, (EX-330, EY), (EX-330, pz), GRN)
d.text((EX-310, (sy+pz)/2-40), "z = 4", font=font(26,True), fill=GRN)
d.text((EX-310, (sy+pz)/2-6), "world units", font=font(24), fill=GRN)
d.text((EX-400, EY+130), "WORLD seen from above. y (up) points out of the page at you.", font=font(24), fill=GREY)

# ---- the sums on the right ----
X0 = 960; m = font(30, mono=True); mb = font(30, True, True)
d.text((X0, 180), "small triangle  =  big triangle", font=font(30,True), fill=FG)
d.text((X0, 240), "( offset_x / FOCAL ) = ( x / z )", font=m, fill=FG)
d.text((X0, 300), "offset_x = ( (x * FOCAL) / z )", font=mb, fill=YEL)
d.text((X0, 360), "         = ( (1 * 400) / 4 )", font=m, fill=FG)
d.text((X0, 410), "         = ( 400 / 4 ) = 100 px", font=m, fill=FG)
d.text((X0, 500), "then add the centre of the window:", font=font(28,True), fill=FG)
d.text((X0, 556), "screen_x = CENTRE_X + offset_x", font=mb, fill=YEL)
d.text((X0, 606), "         = 400 + 100 = 500", font=m, fill=FG)
d.text((X0, 690), "No minus sign for x: +x is right in", font=font(26), fill=FG)
d.text((X0, 726), "the world AND on the screen.", font=font(26), fill=FG)
d.text((X0, 762), "(y needs one, because screen y goes down.)", font=font(26), fill=GREY)

# ---- SCREEN strip: where it lands in the 800-wide window ----
L, R, Y = 960, 1740, 990; s = (R-L)/800
d.text((L, 830), "SCREEN: the window's top edge, x in pixels", font=font(26,True), fill=FG)
d.line([(L, Y), (R, Y)], fill=GREY, width=3)
for xv, lab, col in [(0,"0",GREY),(400,"400\nCENTRE_X",FG),(500,"500",YEL),(800,"800",GREY)]:
    X = L + xv*s; d.line([(X, Y-14), (X, Y+14)], fill=col, width=3)
    d.multiline_text((X - d.textlength(lab.split("\n")[0], font=font(24))/2, Y+22), lab, font=font(24), fill=col, align="center")
d.line([(L+400*s, Y-40), (L+500*s, Y-40)], fill=YEL, width=6)
d.text((L+400*s, Y-82), "offset_x = 100", font=font(24,True), fill=YEL)
d.ellipse([L+500*s-11, Y-11, L+500*s+11, Y+11], fill=GRN)
arrow(d, (L, Y+110), (L+160, Y+110), BLUE); d.text((L+170, Y+94), "+x right", font=font(24,True), fill=BLUE)
img.save("p4d2_triangles_x.png"); print("ok")
