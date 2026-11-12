import math
import pygame

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption('Rotation 201')
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (235, 80, 80)
PURPLE = (160, 100, 230)
BLUE = (70, 150, 255)
GREEN = (70, 210, 120)
GOLD = (245, 200, 60)
ORANGE = (245, 140, 50)
CUBE_GREEN = (70, 230, 120)

CENTRE_X = (WIDTH / 2)
CENTRE_Y = (HEIGHT / 2)
FOCAL = WIDTH / 2

cube_points = [
    (-1, -1, -1), ( 1, -1, -1), ( 1, -1,  1), (-1, -1,  1),
    (-1,  1, -1), ( 1,  1, -1), ( 1,  1,  1), (-1,  1,  1),
]

cube_faces = [
    ((4, 5, 1, 0), RED,    ( 0,  0, -1)),   # front
    ((6, 7, 3, 2), PURPLE, ( 0,  0,  1)),   # back
    ((7, 4, 0, 3), BLUE,   (-1,  0,  0)),   # left
    ((5, 6, 2, 1), GREEN,  ( 1,  0,  0)),   # right
    ((7, 6, 5, 4), GOLD,   ( 0,  1,  0)),   # top
    ((2, 3, 0, 1), ORANGE, ( 0, -1,  0)),   # bottom
]

cube_distance = 5

LIGHT = (0.48, 0.6, -0.64)
AMBIENT = 0.2

START_X = 0
START_Y = 0
START_Z = 0
angle_x = START_X
angle_y = START_Y
angle_z = START_Z
SPEED_X = 0.5
SPEED_Y = 1
SPEED_Z = 0.25
paused = True
one_colour = False
use_light = True


cube_position = (0, 0, 5)     # the cube's centre, in WORLD coordinates
cube_x, cube_y, cube_z = cube_position

cam_x = 0                     # where YOU stand, in WORLD coordinates
cam_y = 0
cam_z = 0


def rotate_x(point_3d, angle_degrees):
    x, y, z = point_3d
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    return (x, (y * cos_a) - (z * sin_a), (y * sin_a) + (z * cos_a))


def rotate_y(point_3d, angle_degrees):
    x, y, z = point_3d
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    return ((x * cos_a) - (z * sin_a), y, (x * sin_a) + (z * cos_a))


def rotate_z(point_3d, angle_degrees):
    x, y, z = point_3d
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    return ((x * cos_a) - (y * sin_a), (x * sin_a) + (y * cos_a), z)


def rotate_all(point_3d):
    return rotate_z(rotate_y(rotate_x(point_3d, angle_x), angle_y), angle_z)


def project(point_3d):
    x, y, z = point_3d
    return (CENTRE_X + ((x * FOCAL) / z), CENTRE_Y - ((y * FOCAL) / z))


def average_z(corners, world_points):
    total = 0
    for corner_number in corners:
        total = total + world_points[corner_number][2]
    return total / len(corners)


def is_facing_you(face_points):
    a_x, a_y = face_points[0]
    b_x, b_y = face_points[1]
    c_x, c_y = face_points[2]
    cross = ((b_x - a_x) * (c_y - a_y)) - ((b_y - a_y) * (c_x - a_x))
    return cross > 0


def dot(arrow_1, arrow_2):
    x1, y1, z1 = arrow_1
    x2, y2, z2 = arrow_2
    return (x1 * x2) + (y1 * y2) + (z1 * z2)


def shade_colour(colour, turned_normal):
    brightness = dot(turned_normal, LIGHT)
    if brightness < 0:
        brightness = 0
    shade = AMBIENT + ((1 - AMBIENT) * brightness)
    red, green, blue = colour
    return (round(red * shade), round(green * shade), round(blue * shade))


def keep_under_360(angle):
    if angle >= 360:
        angle = angle - 360
    return angle


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:             running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE:                 paused = not paused
            if event.key == pygame.K_c:                 one_colour = not one_colour
            if event.key == pygame.K_l:                 use_light = not use_light
            if event.key == pygame.K_r:
                angle_x, angle_y, angle_z = START_X, START_Y, START_Z

    if not paused:
        angle_x = keep_under_360(angle_x + SPEED_X)
        angle_y = keep_under_360(angle_y + SPEED_Y)
        angle_z = keep_under_360(angle_z + SPEED_Z)

    screen.fill(BLACK)

    world_points = []
    screen_points = []
    for p in cube_points:
        x, y, z = rotate_all(p)
        moved = (x, y, z + cube_distance)
        world_points.append(moved)
        screen_points.append(project(moved))

    faces_to_draw = []
    for corners, colour, normal in cube_faces:
        face_points = [screen_points[corner_number] for corner_number in corners]
        if not is_facing_you(face_points):
            continue

        distance = average_z(corners, world_points)
        turned_normal = rotate_all(normal)

        if one_colour:             colour = CUBE_GREEN
        if use_light:              colour = shade_colour(colour, turned_normal)
        faces_to_draw.append((distance, face_points, colour))

    faces_to_draw.sort(reverse=True)
    for distance, face_points, colour in faces_to_draw:
        pygame.draw.polygon(screen, colour, face_points)
        pygame.draw.polygon(screen, BLACK, face_points, 2)


    pygame.display.flip()
    clock.tick(60)

pygame.quit()
