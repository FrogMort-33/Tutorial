import math
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



CENTRE_X = (WIDTH / 2)
CENTRE_Y = (HEIGHT / 2)
FOCAL = WIDTH / 2   # 90 degree horizontal view on any screen

cube_points = [(-1, -1, -1),( 1, -1, -1), ( 1, -1,  1),(-1, -1,  1),(-1,  1, -1),( 1,  1, -1),(1,  1,  1),(-1,  1,  1),]
cube_edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4),(0, 4), (1, 5), (2, 6), (3, 7),]

pyramid_points = [ (-1, -1, -1), ( 1, -1, -1), ( 1, -1,  1), (-1, -1,  1), ( 0,  1,  0) ,]
pyramid_edges = [ (0, 1), (1, 2), (2, 3), (3, 0), (0, 4), (1, 4), (2, 4), (3, 4),]

diamond_points = [ ( 0,  1,  0), ( 0, -1,  0), (-1,  0,  0), ( 1,  0,  0), ( 0,  0, -1), ( 0,  0,  1)]
diamond_edges = [ (2, 4), (4, 3), (3, 5), (5, 2), (0, 2), (0, 3), (0, 4), (0, 5), (1, 2), (1, 3), (1, 4), (1, 5)]

# Tank from Wireframe Warfare (tank_geometry at size 1.0), facing +z
tank_points = [
    (-0.9, -1, -1.3), (0.9, -1, -1.3), (0.9, -1, 1.2), (-0.9, -1, 1.2),                      # 0-3   hull: track base
    (-1.1, -0.55, -1.5), (1.1, -0.55, -1.5), (1.1, -0.55, 1.6), (-1.1, -0.55, 1.6),          # 4-7   hull: belt
    (-0.75, -0.1, -1.2), (0.75, -0.1, -1.2), (0.75, -0.1, 0.5), (-0.75, -0.1, 0.5),          # 8-11  hull: deck
    (-0.5, -0.1, -0.9), (0.5, -0.1, -0.9), (0.5, -0.1, 0.3), (-0.5, -0.1, 0.3),              # 12-15 turret: base
    (-0.4, 0.35, -0.8), (0.4, 0.35, -0.8), (0.4, 0.35, 0), (-0.4, 0.35, 0),                  # 16-19 turret: top
    (-0.08, 0.02, 0.15), (0.08, 0.02, 0.15), (0.08, 0.02, 1.9), (-0.08, 0.02, 1.9),          # 20-23 barrel: bottom
    (-0.08, 0.18, 0.15), (0.08, 0.18, 0.15), (0.08, 0.18, 1.9), (-0.08, 0.18, 1.9),          # 24-27 barrel: top
    (0, 0.35, -0.5), (0, 0.6, -0.5),                                                         # 28-29 radar mast
    (-0.22, 0.6, -0.5), (0.22, 0.6, -0.5), (0.22, 0.82, -0.5), (-0.22, 0.82, -0.5),          # 30-33 radar dish
]
tank_edges = [
    (0, 1), (0, 4), (1, 2), (1, 5), (2, 3), (2, 6), (3, 0), (3, 7),                          # hull
    (4, 5), (4, 8), (5, 6), (5, 9), (6, 7), (6, 10), (7, 4), (7, 11),
    (8, 9), (9, 10), (10, 11), (11, 8),
    (12, 13), (12, 16), (13, 14), (13, 17), (14, 15), (14, 18), (15, 12), (15, 19),          # turret
    (16, 17), (17, 18), (18, 19), (19, 16),
    (20, 21), (21, 22), (22, 23), (23, 20), (24, 25), (25, 26), (26, 27), (27, 24),          # barrel
    (20, 24), (21, 25), (22, 26), (23, 27),
    (28, 29),                                                                                # radar mast
    (30, 31), (31, 32), (32, 33), (33, 30),                                                  # radar dish
]

cube_faces = [
    ((6, 7, 3, 2), PURPLE, (0, 0, 1)),     # back    points away (+z)
    ((7, 4, 0, 3), BLUE,   (-1, 0, 0)),    # left
    ((5, 6, 2, 1), GREEN,  (1, 0, 0)),     # right
    ((7, 6, 5, 4), GOLD,   (0, 1, 0)),     # top
    ((2, 3, 0, 1), ORANGE, (0, -1, 0)),    # bottom
    ((4, 5, 1, 0), RED,    (0, 0, -1)),    # front   points toward you (-z)
    ]

pyramid_faces = [
    ((2, 3, 0, 1), ORANGE, (0, -1, 0)),           # base, points down
    ((4, 1, 0), RED,       (0, 0.447, -0.894)),   # front slope: a bit up, mostly toward you
    ((4, 2, 1), GREEN,     (0.894, 0.447, 0)),    # right slope
    ((4, 3, 2), PURPLE,    (0, 0.447, 0.894)),    # back slope
    ((4, 0, 3), GOLD,      (-0.894, 0.447, 0)),   # left slope
    ]

# 0.577 = 1 / sqrt(3): the arrow (1, 1, 1) shrunk to 1 long
diamond_faces = [
    ((0, 4, 2), RED,   (-0.577, 0.577, -0.577)),
    ((0, 3, 4), GOLD,  (0.577, 0.577, -0.577)),
    ((0, 5, 3), GREEN, (0.577, 0.577, 0.577)),
    ((0, 2, 5), CYAN,  (-0.577, 0.577, 0.577)),
    ((1, 2, 4), GREEN, (-0.577, -0.577, -0.577)),
    ((1, 4, 3), CYAN,  (0.577, -0.577, -0.577)),
    ((1, 3, 5), RED,   (0.577, -0.577, 0.577)),
    ((1, 5, 2), GOLD,  (-0.577, -0.577, 0.577)),
    ]

# Tank normals were worked out with the same cross-product recipe as above.
tank_faces = [
    ((0, 1, 2, 3), ORANGE,      (0, -1, 0)),                  # hull: underside
    ((0, 4, 5, 1), BLUE,        (0, -0.406, -0.914)),         # hull: base -> belt
    ((1, 5, 6, 2), BLUE,        (0.914, -0.406, 0)),
    ((2, 6, 7, 3), BLUE,        (0, -0.664, 0.747)),
    ((3, 7, 4, 0), BLUE,        (-0.914, -0.406, 0)),
    ((4, 8, 9, 5), GREEN,       (0, 0.555, -0.832)),          # hull: belt -> deck (front is the prow)
    ((5, 9, 10, 6), GREEN,      (0.789, 0.614, 0)),
    ((6, 10, 11, 7), GREEN,     (0, 0.926, 0.379)),
    ((7, 11, 8, 4), GREEN,      (-0.789, 0.614, 0)),
    ((8, 11, 10, 9), GOLD,      (0, 1, 0)),                   # hull: deck
    ((12, 16, 17, 13), PURPLE,  (0, 0.217, -0.976)),          # turret: sides
    ((13, 17, 18, 14), PURPLE,  (0.976, 0.217, 0)),
    ((14, 18, 19, 15), PURPLE,  (0, 0.555, 0.832)),
    ((15, 19, 16, 12), PURPLE,  (-0.976, 0.217, 0)),
    ((16, 19, 18, 17), CYAN,    (0, 1, 0)),                   # turret: top
    ((20, 21, 22, 23), RED,     (0, -1, 0)),                  # barrel: bottom
    ((24, 27, 26, 25), RED,     (0, 1, 0)),                   # barrel: top
    ((21, 25, 26, 22), RED,     (1, 0, 0)),                   # barrel: sides
    ((23, 27, 24, 20), RED,     (-1, 0, 0)),
    ((22, 26, 27, 23), RED,     (0, 0, 1)),                   # barrel: muzzle
    ((30, 31, 32, 33), CYAN,    (0, 0, 1)),                   # radar dish: front
    ((30, 33, 32, 31), PURPLE,  (0, 0, -1)),                  # radar dish: back (reversed corners)
]



shapes = [
    ('CUBE' , cube_points,    cube_edges, cube_faces,    -2.0, 0.0, 0.0, GREEN),
    ('PYRAMID' , pyramid_points, pyramid_edges, pyramid_faces,  2.0, 0.0, 0.0, CYAN),
    ('DIAMOND', tank_points, tank_edges, tank_faces, 0.0, 2.5, 5.0, ORANGE),
    ('DIAMOND', diamond_points, diamond_edges, diamond_faces, 0.0, -2.5, 3.0, RED)
      ]

cube_distance = 5
angle_degrees = tilt_degrees = spin_degrees = 0

TURN_STEP = 1

def average_z(face_world_points):

    total = 0
    for x, y, z in face_world_points:
        total = (total + z)
    return (total / len(face_world_points))


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


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_d]:         angle_degrees = (angle_degrees + TURN_STEP)
    if keys[pygame.K_a]:         angle_degrees = (angle_degrees - TURN_STEP)
    if keys[pygame.K_w]:         tilt_degrees = (tilt_degrees + TURN_STEP)
    if keys[pygame.K_s]:         tilt_degrees = (tilt_degrees - TURN_STEP)
    if keys[pygame.K_q]:         spin_degrees = (spin_degrees + TURN_STEP)
    if keys[pygame.K_e]:         spin_degrees = (spin_degrees - TURN_STEP)

    if keys[pygame.K_UP]:        cube_distance = (cube_distance + 0.05)
    if keys[pygame.K_DOWN]:      cube_distance = (cube_distance - 0.05)
    if cube_distance < 3:        cube_distance = 3

    screen.fill(BLACK)

    #FOR EACH SHAPE ! 
    for shape_name , points, edges, faces,  shape_x, shape_y, shape_z, shape_color in shapes:  

        world_points = []  # Real GAME WOrld X,Y,Z coordinates for points 
        screen_points = [] # 2D Projected convershion of points 

        #FOR Each Set of SHAPE points ( using 0,0,0 as center of shape ) 
        for p in points:
                #Rotate the points in the SHAPE 
                x, y, z = rotate_z(rotate_x(rotate_y(p, angle_degrees), tilt_degrees), spin_degrees)
                #Move the shape into is GAME world X,Y,Z locating 
                moved = (shape_x + x, shape_y + y, (shape_z + z + cube_distance))
                #Save location in GAME x,y,z 
                world_points.append(moved)
                #Save PROJECTED to screen 
                screen_points.append(project(moved))

        if faces:

            face_paint_order =[] 

            for corners, colour, normal in faces:
                face_points = []
                face_world_points = [] 

                for corner_number in corners:
                    face_points.append(screen_points[corner_number])
                    face_world_points.append(world_points[corner_number] )
                
                
                if is_facing_you(face_points) : # Only add to draw list if yo are facing me . 

                    turned_normal = rotate_z(rotate_x(rotate_y(normal, angle_degrees), tilt_degrees), spin_degrees)

                    average_z_value = average_z(face_world_points)
                    face_paint_order.append((average_z_value, colour, face_points))
            
            face_paint_order.sort(reverse=True)
            for average_z_value, colour, face_points in face_paint_order:
                pygame.draw.polygon(screen, colour, face_points)        # filled     
                pygame.draw.polygon(screen, RED, face_points, 2)        # outline

        else: 

            for a, b in edges:
                pygame.draw.line(screen, shape_color, screen_points[a], screen_points[b], 2)


    # FPS counter, top-left corner
    fps_text = fps_font.render("FPS: " + str(round(clock.get_fps())), True, GREEN)
    screen.blit(fps_text, (10, 10))

    pygame.display.flip()
    clock.tick(200)

pygame.quit()