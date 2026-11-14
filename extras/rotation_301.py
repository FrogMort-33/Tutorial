# rotation_301.py - the GAME: start-up and the main loop. Run this file.
#   rotation_data.py      - the world's data: colours, models, things, settings, shared state
#   rotation_functions.py - how it all works: maths, drawing, collisions, sounds
import pygame
from rotation_data import *
from rotation_functions import *        # (this also opens the game window)

START_LEVEL = 7 # DEBUG: which level to play (see LEVELS in rotation_levels.py). 99 = skunk works, the test level
show_spheres = False   # C key: draw the collision spheres (a debug view)
show_wall_grid = True  # G key: the grid on the walls and ceiling (watch the FPS counter as you switch it)

load_level(START_LEVEL)              # build the level: its world, boxes, floor shapes, things, and where you start

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
        if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
            show_spheres = not show_spheres               # flip: on -> off, off -> on (once per press)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_g:
            show_wall_grid = not show_wall_grid           # the wall and ceiling grid: on / off
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            volume["slider"] = max(0.0, round(volume["slider"] - 0.1, 1))     # quieter (never below 0%)
            apply_volume()
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_EQUALS, pygame.K_KP_PLUS):
            volume["slider"] = min(1.0, round(volume["slider"] + 0.1, 1))     # louder (never above 100%)
            apply_volume()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            fire_bullet()                                 # left click: FIRE (one bullet per click)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if camera["y"] <= STAND_Y and you["frozen"] == 0:   # only jump with your feet on the floor (not frozen)
                camera["vy"] = JUMP_SPEED


    keys = pygame.key.get_pressed()
    spin_things(keys)                               # each thing's own spin, plus the I J K L U O keys
    move_camera(keys)                               # you: look, walk, jump
    update_floor_hazards()                          # standing in lava (feet on the floor)? it hurts
    move_things()                                   # every thing moves (and bounces off the world box)

    bounce_things_off_each_other()                  # after moving: things that touch bounce apart
    bounce_things_off_boxes()                       # ...and things that hit a box bounce off it
    update_sparks()                                 # move, drop and age the sparks
    tanks_take_aim()                                # turrets pointing at you fire (after their cooldown)
    remove_finished_things()                        # used-up bullets and destroyed shapes go
    update_level_progress()                         # every shape gone? "completed" message, then the next level

    screen.fill(BLACK)

    draw_floor()                                   # the whole grid, before any shape
    if show_wall_grid:
        draw_wall_grid()                           # G key: the grid on the walls and ceiling
    draw_world_box()                               # the wireframe box round the room: corner posts and ceiling
    draw_floor_shapes()                            # then the flat shapes ON the floor, still before any shape

    face_paint_order = []          # EVERY face of EVERY thing, painted together after the loop
    add_thing_faces(face_paint_order)               # every thing's visible faces...
    add_box_faces(face_paint_order)                    # the boxes' faces join the same paint list
    paint_faces(face_paint_order)                   # ...sorted far to near and painted

    draw_sparks()                                      # sparks on top of the shapes
    draw_health()                                      # health squares above the shapes

    if show_spheres:                                   # C key: collision spheres on top of the shapes
        draw_collision_spheres()

    draw_mini_map()
    draw_crosshair()                                   # the crosshair, on top of everything in the 3D view
    draw_hud()
    draw_level_banner()                            # the level's name and intro: centre, then the name at the top
    draw_level_complete()                          # "Level X completed!" once every shape is gone

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
