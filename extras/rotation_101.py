import math
import pygame

pygame.init()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

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
FOCAL = 400

cube_points = [(-1, -1, -1),( 1, -1, -1), ( 1, -1,  1),(-1, -1,  1),(-1,  1, -1),( 1,  1, -1),(1,  1,  1),(-1,  1,  1),]
cube_edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4),(0, 4), (1, 5), (2, 6), (3, 7),]

pyramid_points = [ (-1, -1, -1), ( 1, -1, -1), ( 1, -1,  1), (-1, -1,  1), ( 0,  1,  0) ,]
pyramid_edges = [ (0, 1), (1, 2), (2, 3), (3, 0), (0, 4), (1, 4), (2, 4), (3, 4),]

diamond_points = [ ( 0,  1,  0), ( 0, -1,  0), (-1,  0,  0), ( 1,  0,  0), ( 0,  0, -1), ( 0,  0,  1)]
diamond_edges = [ (2, 4), (4, 3), (3, 5), (5, 2), (0, 2), (0, 3), (0, 4), (0, 5), (1, 2), (1, 3), (1, 4), (1, 5)]

cube_faces = [
    ((6, 7, 3, 2), PURPLE),((7, 4, 0, 3), BLUE),((5, 6, 2, 1), GREEN), ((7, 6, 5, 4), GOLD), 
    ((2, 3, 0, 1), ORANGE),((4, 5, 1, 0), RED), ]

pyramid_faces = [
    ((2, 3, 0, 1), ORANGE),((4, 1, 0), RED),((4, 2, 1), GREEN),((4, 3, 2), PURPLE),((4, 0, 3), GOLD),]

diamond_faces = [
    ((0, 4, 2), RED),((0, 3, 4), GOLD),((0, 5, 3), GREEN),((0, 2, 5), CYAN),((1, 2, 4), GREEN),
    ((1, 4, 3), CYAN),((1, 3, 5), RED),((1, 5, 2), GOLD),]



shapes = [
    ('CUBE' , cube_points,    cube_edges, cube_faces,    -2.0, 0.0, 0.0, GREEN),
    ('PYRAMID' , pyramid_points, pyramid_edges, pyramid_faces,  2.0, 0.0, 0.0, CYAN),
    ('DIAMOND', diamond_points, diamond_edges, None, 0.0, 2.5, 3.0, ORANGE),
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

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
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

            for corners, colour in faces:
                face_points = []
                face_world_points = [] 

                for corner_number in corners:
                    face_points.append(screen_points[corner_number])
                    face_world_points.append(world_points[corner_number] )
                average_z_value = average_z(face_world_points)
                face_paint_order.append((average_z_value, colour, face_points))
            
            face_paint_order.sort(reverse=True)
            for average_z_value, colour, face_points in face_paint_order:
                pygame.draw.polygon(screen, colour, face_points)        # filled     
                pygame.draw.polygon(screen, RED, face_points, 2)        # outline

        else: 

            for a, b in edges:
                pygame.draw.line(screen, shape_color, screen_points[a], screen_points[b], 2)


    pygame.display.flip()
    clock.tick(200)

pygame.quit()