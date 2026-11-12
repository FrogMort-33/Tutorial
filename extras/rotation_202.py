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
CUBE_GREEN = (70, 230, 120)  
PINK = (255, 105, 200)


LIGHT = (0.48, 0.6, -0.64) # THe 'where is the light ' arrow direction of length 1 . 
AMBIENT = 0.2 # Everyone deservers a little light .. 

CENTRE_X = (WIDTH / 2)
CENTRE_Y = (HEIGHT / 2)
FOCAL = WIDTH / 2   # 90 degree horizontal view on any screen

cube_points = [(-1, -1, -1),( 1, -1, -1), ( 1, -1,  1),(-1, -1,  1),(-1,  1, -1),( 1,  1, -1),(1,  1,  1),(-1,  1,  1),]
cube_edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4),(0, 4), (1, 5), (2, 6), (3, 7),]

cube_faces = [
    ((6, 7, 3, 2), PURPLE, (0, 0, 1)),     # back    points away (+z)
    ((7, 4, 0, 3), BLUE,   (-1, 0, 0)),    # left
    ((5, 6, 2, 1), GREEN,  (1, 0, 0)),     # right
    ((7, 6, 5, 4), GOLD,   (0, 1, 0)),     # top
    ((2, 3, 0, 1), ORANGE, (0, -1, 0)),    # bottom
    ((4, 5, 1, 0), RED,    (0, 0, -1)),    # front   points toward you (-z)
    ]

shapes = [
    ('CUBE' , cube_points,    cube_edges, cube_faces,    -2.0, 0.0, 9.0, GREEN ,1),
    ('CUBE' , cube_points,    cube_edges, cube_faces,    +3, 0, 5, CUBE_GREEN ,0.2),
      ]

cube_distance = 0
angle_degrees = tilt_degrees = spin_degrees = 0


cam_x = 0      # where YOU (the camera) stand, in WORLD coordinates
cam_y = 0      # your height (not shown on the map)
cam_z = 0

TURN_STEP = 1

cam_turn = 0          # which way you face, in degrees. 0 = facing +z (up the map)
TURN_SPEED = 1.5      # degrees per frame
cam_tip = 0           # looking up / down, in degrees. 0 = level, + = down, - = up
TIP_LIMIT = 60        # don't let you look further up or down than this


## MINI MAP !!
MAP_SIZE = HEIGHT/3                         # the map is a 160 x 160 pixel square
MAP_LEFT = (WIDTH - 10 - MAP_SIZE)     # its left edge: 10 px in from the right of the screen
MAP_TOP = (HEIGHT - 10 - MAP_SIZE)     # its top edge: 10 px up from the bottom of the screen
MAP_COLOUR_BACK = (25, 30, 36)         # dark grey-blue, so the map stands out from the black

MAP_CX = (MAP_LEFT + (MAP_SIZE / 2))   # WORLD x = 0 goes across the middle of the box
MAP_CY = (MAP_TOP + (MAP_SIZE * 0.8))   # 80% of the way down the box

MAP_SCALE = (MAP_SIZE / 16)             # the box always shows 16 world units across

MOVE_SPEED = 0.05      # how far you move in ONE frame
NEAR = 0.1     # anything closer than this, measured from YOU, is not drawn
MOUSE_SPEED = 0.2      # degrees of turn per pixel the mouse moves


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

    keys = pygame.key.get_pressed()
    if keys[pygame.K_l]:         angle_degrees = (angle_degrees + TURN_STEP)
    if keys[pygame.K_j]:         angle_degrees = (angle_degrees - TURN_STEP)
    if keys[pygame.K_i]:         tilt_degrees = (tilt_degrees + TURN_STEP)
    if keys[pygame.K_k]:         tilt_degrees = (tilt_degrees - TURN_STEP)
    if keys[pygame.K_u]:         spin_degrees = (spin_degrees + TURN_STEP)
    if keys[pygame.K_o]:         spin_degrees = (spin_degrees - TURN_STEP)

    forward_x, forward_y, forward_z = rotate_y((0, 0, 1), cam_turn)   # the way you face
    right_x, right_y, right_z = rotate_y((1, 0, 0), cam_turn)         # your right hand


    if keys[pygame.K_w]:         
        #cam_z = (cam_z + MOVE_SPEED)
        cam_z = (cam_z + (forward_z * MOVE_SPEED))    # ...and a bit forward
        cam_x = (cam_x + (forward_x * MOVE_SPEED))    # a bit sideways...


    if keys[pygame.K_s]:         
        #cam_z = (cam_z - MOVE_SPEED)
        cam_z = (cam_z - (forward_z * MOVE_SPEED))    # ...and a bit forward
        cam_x = (cam_x - (forward_x * MOVE_SPEED))    # a bit sideways...

    if keys[pygame.K_e]:         
        #cam_x = (cam_x + MOVE_SPEED)
        cam_x = (cam_x + (right_x * MOVE_SPEED))
        cam_z = (cam_z + (right_z * MOVE_SPEED))



    if keys[pygame.K_q]:         
       # cam_x = (cam_x - MOVE_SPEED)
        cam_x = (cam_x - (right_x * MOVE_SPEED))
        cam_z = (cam_z - (right_z * MOVE_SPEED))

    if keys[pygame.K_a]:         cam_turn = (cam_turn + TURN_SPEED)    # turn left
    if keys[pygame.K_d]:         cam_turn = (cam_turn - TURN_SPEED)    # turn right

    mouse_dx, mouse_dy = pygame.mouse.get_rel()          # pixels moved since last frame
    cam_turn = (cam_turn - (mouse_dx * MOUSE_SPEED))     # mouse right = turn right

    cam_tip = (cam_tip + (mouse_dy * MOUSE_SPEED))       # mouse up = look up
    if cam_tip > TIP_LIMIT:      cam_tip = TIP_LIMIT     # stop at the limits
    if cam_tip < -TIP_LIMIT:     cam_tip = -TIP_LIMIT

    screen.fill(BLACK)

    #FOR EACH SHAPE ! 
    for shape_name , points, edges, faces,  shape_x, shape_y, shape_z, shape_color ,scale in shapes:  

        world_points = []  # Real GAME WOrld X,Y,Z coordinates for points 
        screen_points = [] # 2D Projected convershion of points 

        #FOR Each Set of SHAPE points ( using 0,0,0 as center of shape ) 
        for p in points:
                #Rotate the points in the SHAPE 

                x,y,z = p
                p = x*scale , y* scale , z* scale 

                x, y, z = rotate_z(rotate_x(rotate_y(p, angle_degrees), tilt_degrees), spin_degrees)
                #Move the shape into is GAME world X,Y,Z locating 
                moved = (shape_x + x, shape_y + y, (shape_z + z + cube_distance))
                #Save location in GAME x,y,z 
                world_points.append(moved)


                #Save PROJECTED to screen 
                #screen_points.append(project(to_camera(moved)))
                camera_point = to_camera(moved)
                if camera_point[2] >= NEAR:                  # [2] is z: how far in front of you
                    screen_points.append(project(camera_point))
                else:
                    screen_points.append(None)              # too close or behind you: no pixel




        if faces:

            face_paint_order =[] 

            for corners, colour, normal in faces:
                face_points = []
                face_world_points = [] 

                for corner_number in corners:
                    face_points.append(screen_points[corner_number])
                    face_world_points.append(world_points[corner_number] )

                if None in face_points:      # a corner is too close or behind you FAST FAIL 
                    continue                 # skip the whole face
                
                #Cross product check 
                if is_facing_you(face_points) : # Only add to draw list if yo are facing me . 

                    turned_normal = rotate_z(rotate_x(rotate_y(normal, angle_degrees), tilt_degrees), spin_degrees)



                    colour = shade_colour(colour, turned_normal)
                    #colour = shade_colour(CUBE_GREEN, turned_normal)


                    average_z_value = average_z(face_world_points)
                    face_paint_order.append((average_z_value, colour, face_points))
            
            face_paint_order.sort(reverse=True)
            for average_z_value, colour, face_points in face_paint_order:
                pygame.draw.polygon(screen, colour, face_points)        # filled     
                pygame.draw.polygon(screen, shape_color, face_points, 2)        # outline

        else: 

            for a, b in edges:
                pygame.draw.line(screen, shape_color, screen_points[a], screen_points[b], 2)

## MINI MAP 
    map_box = pygame.Rect(MAP_LEFT, MAP_TOP, MAP_SIZE, MAP_SIZE)
    pygame.draw.rect(screen, MAP_COLOUR_BACK, map_box)          # filled background
    pygame.draw.rect(screen, (255, 255, 255), map_box, 1)       # thin white border

    pygame.draw.circle(screen, (255, 255, 0), to_map(0, 0), 5)   # yellow dot = WORLD (0, 0, 0)


    #pygame.draw.circle(screen, GREEN, to_map(shape_x, shape_z + cube_distance), 5)   # green dot = the cube
    
    for shape_name, points, edges, faces, shape_x, shape_y, shape_z, shape_color, scale in shapes:
        pygame.draw.circle(screen, GREEN, to_map(shape_x, shape_z + cube_distance), 5)
    
    pygame.draw.circle(screen, PINK, to_map(cam_x, cam_z), 5)   # pink dot = YOU

    face_x, face_y, face_z = rotate_y((0, 0, 1), cam_turn)            # your "forward" arrow
    nose = to_map(cam_x + (face_x * 1.5), cam_z + (face_z * 1.5))     # 1.5 units in front of you
    pygame.draw.line(screen, PINK, to_map(cam_x, cam_z), nose, 2)

## MINNI MAP 


    # FPS counter, top-left corner
    fps_text = fps_font.render("FPS: " + str(round(clock.get_fps())), True, GREEN)
    screen.blit(fps_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()