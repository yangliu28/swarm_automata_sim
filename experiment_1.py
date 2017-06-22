# experiment 1 is the first attempt on continuous mobile automata

# continuous means the opposite of discrete
# it mainly refer to the rules and how rule varies

# the edge of the window can bounce the automaton and give it opposite velocity
# so I can create more interaction in limited simulation window

# general rules:
# each automaton has a circular sensing range, divided into two equal halves
# each automaton has a moving axis fixed with the body of the automaton
# it can only moves along this axis, front or back
# the orientation of the two-half sensing range is also fixed with the automaton
# if another automaton is detected in one half, it exerts a pulling effect on host
# and pushing effect if it is detected in the other half
# here we make left half the pulling half, right half the pushing half
# the direction we are facing along the dividing line is the front of dividing line
# there could be an angle between the front moving axis and front dividing line
# here we use alpha, indicating angle of front direction of moving axis
# relative to the front direction of dividing line, counter-clockwise is positive

# quantify the pulling and pushing effects:
# the pulling or pushing effect can be finalized as a vectorial acceleration
# since the automaton only moves on moving axis, it has speed only along the axis
# the projected acceleration on the moving axis change the speed
# the projected acceleration perpendicular to the axis change the speed direction
# just like centripetal acceleration
# the direction of the acceleration vector is along the line connecting the host
# automaton and detected automaton, direction depending on pulling or push
# magnetitude is inversely proportional to the distance between the two automata
# the closer they are, the stronger the acceleration
# an upper limit will be exerted, in case the aceleration goes out of control


# 1.physics coordinates, or arena coordinates
# the physics is done in floating numbers, like for the distance
# the origin for the global coordinates is in the middle of the simulation window
# the right direction is the positive of x, top direction is the positive of y

# 2.display coordinates, or screen coordinates 
# the graphics is done with pixels, by converting the floatings to integers
# the origin of the simulation window is at the top left corner
# with horizontal direction being x axis, and vertical direction being y axis

############### analysis ###############
# 03/16/2017
# the sensing circle is bipolar that pulling in one half and pushing another half
# the effect is that automaton will always accelerate toward the pulling half
# the automaton always ends up with uncontrollable speed
# if the initial speed is at pushing sector, the automaton will decelerate to zero
# and accelerate at the opposite direction
# the reason is that both sectors are accelerating automaton toward same direction

# experiment 2 will increase sensing sectors to 4
# so that only same sectors are in opposing directions
# in this way I am looking forward to a "balanced" automaton

import pygame
from random import *
from math import *

from experiment_1_automaton import Automaton
from utilities import *

pygame.init()  # initialize pygame

# set the window icon
icon = pygame.image.load('pacman4_icon.png')
pygame.display.set_icon(icon)

# for display
screen_size = (1200, 900)  # width and height in pixels, even numbers
background_color = (55, 60, 60)  # background in grey
automaton_color = (255, 188, 55)  # automaton in orange
range_color = (255, 255, 255)  # sensing circle in white
mov_line_color = (255, 51, 0)
div_line_color = (51, 102, 255)
automaton_size = 4  # number of pixels of radius, for the size of automaton

# the surface object and the simulation window
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Continuous Mobile Automata 1')



# physics for automata, the virtual world the automata exist
# the size of the world the automata play, proportional to display size, no unit
arena_size = (100, 100 * screen_size[1]/screen_size[0])
# a key size for distance reference
key_dist = arena_size[0] / 20  # 1/10 on both size of x axis

# variables to configure the simulation
automata_quantity = 30
initial_vel = key_dist * 1.0  # per second
sensing_radius = key_dist * 1.0
# fixed angle between positive moving direction and posotive dividing direction
alpha = pi/6


# instantiate the automaton swarm
automata = []  # container for all automata
for i in range(automata_quantity):
    # random position, times 0.9 to be away from boundary
    pos_temp = ((random()*arena_size[0] - arena_size[0]/2) * 0.9,
                (random()*arena_size[1] - arena_size[1]/2) * 0.9)
    vel_temp = initial_vel  # same initial velocity
    ori_temp = random() * 2*pi - pi  # random in (-pi, pi)
    radius_temp = sensing_radius  # same radius for all, homogeneous swarm
    alpha_temp = alpha  # same alpha, for homogeneous swarm
    # instantiate an object from the Automaton class
    object_temp = Automaton(pos_temp, vel_temp, ori_temp, radius_temp, alpha_temp)
    automata.append(object_temp)

# the loop
sim_exit = False  # simulation exit flag
sim_pause = False  # simulation pause flag
timer_last = pygame.time.get_ticks()  # return number of milliseconds after pygame.init()
timer_now = timer_last  # initialize it with timer_last
frame_period = 10  # frame updating period in ms, also used in physics update
delta_t = frame_period / 1000.0  # time period to calculate changes in automata physics
while not sim_exit:
    # exit the program
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sim_exit = True  # exit with the close window button
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                sim_pause = not sim_pause  # reverse the pause flag
            if (event.key == pygame.K_ESCAPE) or (event.key == pygame.K_q):
                sim_exit = True  # exit with ESC key or Q key

    # skip the rest of the loop if paused
    if sim_pause: continue

    # print("******")  # use to check loop freq
    # update automata positions when it's time to update the frame
    timer_now = pygame.time.get_ticks()
    if (timer_now - timer_last) > frame_period:
        # print("***************")  # use to check loop freq
        # calculate physics for automata first
        for i in range(automata_quantity):
            automata[i].reset_detection()  # reset feedback vector
            for j in range(automata_quantity):
                if j == i: continue  # skip checking itself as possible neighbor
                # check if automaton j is a in-range neighbor of automaton i
                automata[i].check_neighbor(automata[j].get_pos())
            if automata[i].get_detection_status():
                # there is at least one in-range neighbor detected
                # calculate acceleration imposed by the neighbors
                automata[i].calculate_accel()
                # update the position with calculated acceleration
                # it also resets detection flag
                automata[i].update_with_accel(delta_t)
            else:
                automata[i].update_without_accel(delta_t)
            # rebound automaton if running out of boundaries
            automata[i].check_boundary(arena_size)

        # update the display surface with background and automata
        screen.fill(background_color)  # prepare the background first
        # convert physics position to display position
        for i in range(automata_quantity):
            # 1.prepare position of this automaton
            pos_arena_temp = automata[i].get_pos()  # get raw position in arena
            # convert arena position to display position
            pos_disp_temp = arena_to_display(pos_arena_temp, arena_size, screen_size)
            # 2.prepare radius for sensing circle
            radius_arena_temp = automata[i].get_radius()  # get raw radius in arena
            radius_disp_temp = int(radius_arena_temp * screen_size[0] / arena_size[0])
            # 3.prepare line for positive moving direction
            mov_ori_temp = automata[i].get_ori()
            mov_arena_pt_temp = [0, 0]  # the positive point
            mov_arena_pt_temp[0] = pos_arena_temp[0] + radius_arena_temp * cos(mov_ori_temp)
            mov_arena_pt_temp[1] = pos_arena_temp[1] + radius_arena_temp * sin(mov_ori_temp)
            mov_disp_pt_temp = arena_to_display(mov_arena_pt_temp, arena_size, screen_size)
            # 4.prepare dividing line for pulling and pushing regions
            alpha_temp = automata[i].get_alpha()
            div_ori_temp = reset_radian(mov_ori_temp - alpha_temp)
            div_arena_pt_temp = [[0, 0], [0, 0]]  # positive and negative point
            div_arena_pt_temp[0][0] = pos_arena_temp[0] + radius_arena_temp * cos(div_ori_temp)
            div_arena_pt_temp[0][1] = pos_arena_temp[1] + radius_arena_temp * sin(div_ori_temp)
            div_arena_pt_temp[1][0] = pos_arena_temp[0] + radius_arena_temp * cos(div_ori_temp + pi)
            div_arena_pt_temp[1][1] = pos_arena_temp[1] + radius_arena_temp * sin(div_ori_temp + pi)
            div_disp_pt_temp = [[0, 0], [0, 0]]
            div_disp_pt_temp[0] = arena_to_display(div_arena_pt_temp[0], arena_size, screen_size)
            div_disp_pt_temp[1] = arena_to_display(div_arena_pt_temp[1], arena_size, screen_size)
            # control the drawing sequency as follows
            # draw the dividing line segment
            pygame.draw.line(screen, div_line_color, div_disp_pt_temp[0], div_disp_pt_temp[1], 2)
            # draw the positive moving direction line segment
            pygame.draw.line(screen, mov_line_color, pos_disp_temp, mov_disp_pt_temp, 3)
            # draw the automaton, a solid circle representing the automaton
            pygame.draw.circle(screen, automaton_color, pos_disp_temp, automaton_size, 0)
            # draw the sensing circle, an empty circle representing the sensing range
            pygame.draw.circle(screen, range_color, pos_disp_temp, radius_disp_temp, 1)
        pygame.display.update()  # eqivalent to update() now

        # reset timer_last
        timer_last = timer_now

# quit pygame
pygame.quit()






