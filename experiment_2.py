# experiment 2 increases the sensing sectors to 4 (previously 2)
# with pulling and pushing sectors in alternative order

# 4 is the minimum number of sectors to achieve a "balanced" automaton
# only 2 sectors will make automaton accelerate in an uncontrollable manner

# most code is the same with experiment 1, for an automaton change like this
# only two main parts need to be updated:
# the automaton physics in automaton class, and the graphics for the automaton


# sensing sectors arrangements:
# rotating counter-clockwise from the positive dividing line
# we have a pulling sector first, then pushing, pulling and pushing sectors
# alpha is the same definition that it is the relative angle of positive
# moding direction to the positive dividing direction

############### analysis ###############
# 03/20/2017
# this automaton is balanced as I have desired, the speed won't keep growing
# stronger in specific direction. But the speed of the automata in this simulation
# are more random, some moves very slowly while some still shooting like bullets
# like in the previous automaton.

# the simulation result is not obvious, no recognizable behavior is observed
# rules for automaton 1 and 2 are still not simple enough
# the running speed of the automaton can be kept constant, so as to constrain
# the randomness to a certain manner

import pygame
from random import *
from math import *

from experiment_2_automaton import Automaton
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
pygame.display.set_caption('Continuous Mobile Automata 2')



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
alpha = pi/4


# instantiate the automata swarm
automata = []  # container for all automata
for i in range(automata_quantity):
    # random position, times 0.9 so it is away from boundaries
    pos_temp = ((random()*arena_size[0] - arena_size[0]/2) * 0.9,
                (random()*arena_size[1] - arena_size[1]/2) * 0.9)
    vel_temp = initial_vel  # same initial velocity
    ori_temp = random() * 2*pi - pi  # create random in (-pi, pi)
    radius_temp = sensing_radius  # same radius for all, homogeneous swarm
    alpha_temp = alpha  # same alpha, for homogeneous swarm
    # instantiate an object from the Automaton class
    object_temp = Automaton(pos_temp, vel_temp, ori_temp, radius_temp, alpha_temp)
    automata.append(object_temp)  # append new automaton to the swarm

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
            # 3.prepare end points for positive moving line
            
            mov_ori_temp = automata[i].get_ori()
            mov_arena_pt_temp = [[0, 0], [0, 0]]  # start and end points of positive moving line
            # starting point of positive moving line
            mov_arena_pt_temp[0][0] = pos_arena_temp[0] + 0.2*radius_arena_temp * cos(mov_ori_temp)
            mov_arena_pt_temp[0][1] = pos_arena_temp[1] + 0.2*radius_arena_temp * sin(mov_ori_temp)
            # far end point of positive moving line
            mov_arena_pt_temp[1][0] = pos_arena_temp[0] + 0.8*radius_arena_temp * cos(mov_ori_temp)
            mov_arena_pt_temp[1][1] = pos_arena_temp[1] + 0.8*radius_arena_temp * sin(mov_ori_temp)
            mov_disp_pt_temp = [[0, 0], [0, 0]]
            mov_disp_pt_temp[0] = arena_to_display(mov_arena_pt_temp[0], arena_size, screen_size)
            mov_disp_pt_temp[1] = arena_to_display(mov_arena_pt_temp[1], arena_size, screen_size)
            # 4.prepare end points for the dividing lines for sensing sectors
            alpha_temp = automata[i].get_alpha()
            div_ori_temp = reset_radian(mov_ori_temp - alpha_temp)
            # end points for the four dividing lines
            div_arena_pt_temp = [[[0, 0], [0, 0]],
                                 [[0, 0], [0, 0]],
                                 [[0, 0], [0, 0]],
                                 [[0, 0], [0, 0]]]
            # end points for the dividing line at 0 deg
            div_arena_pt_temp[0][0][0] = pos_arena_temp[0] + 0.15*radius_arena_temp * cos(div_ori_temp)
            div_arena_pt_temp[0][0][1] = pos_arena_temp[1] + 0.15*radius_arena_temp * sin(div_ori_temp)
            div_arena_pt_temp[0][1][0] = pos_arena_temp[0] + 0.85*radius_arena_temp * cos(div_ori_temp)
            div_arena_pt_temp[0][1][1] = pos_arena_temp[1] + 0.85*radius_arena_temp * sin(div_ori_temp)
            # end points for the dividing line at 90 deg
            div_arena_pt_temp[1][0][0] = pos_arena_temp[0] + 0.15*radius_arena_temp * cos(div_ori_temp+pi/2)
            div_arena_pt_temp[1][0][1] = pos_arena_temp[1] + 0.15*radius_arena_temp * sin(div_ori_temp+pi/2)
            div_arena_pt_temp[1][1][0] = pos_arena_temp[0] + 0.85*radius_arena_temp * cos(div_ori_temp+pi/2)
            div_arena_pt_temp[1][1][1] = pos_arena_temp[1] + 0.85*radius_arena_temp * sin(div_ori_temp+pi/2)
            # end points for the dividing line at 180 deg
            div_arena_pt_temp[2][0][0] = pos_arena_temp[0] + 0.15*radius_arena_temp * cos(div_ori_temp+pi)
            div_arena_pt_temp[2][0][1] = pos_arena_temp[1] + 0.15*radius_arena_temp * sin(div_ori_temp+pi)
            div_arena_pt_temp[2][1][0] = pos_arena_temp[0] + 0.85*radius_arena_temp * cos(div_ori_temp+pi)
            div_arena_pt_temp[2][1][1] = pos_arena_temp[1] + 0.85*radius_arena_temp * sin(div_ori_temp+pi)
            # end points for the dividing line at -90 deg
            div_arena_pt_temp[3][0][0] = pos_arena_temp[0] + 0.15*radius_arena_temp * cos(div_ori_temp-pi/2)
            div_arena_pt_temp[3][0][1] = pos_arena_temp[1] + 0.15*radius_arena_temp * sin(div_ori_temp-pi/2)
            div_arena_pt_temp[3][1][0] = pos_arena_temp[0] + 0.85*radius_arena_temp * cos(div_ori_temp-pi/2)
            div_arena_pt_temp[3][1][1] = pos_arena_temp[1] + 0.85*radius_arena_temp * sin(div_ori_temp-pi/2)
            # corresponding points on the display
            div_disp_pt_temp = [[[0, 0], [0, 0]],
                                [[0, 0], [0, 0]],
                                [[0, 0], [0, 0]],
                                [[0, 0], [0, 0]]]
            # dividing line at 0 deg
            div_disp_pt_temp[0][0] = arena_to_display(div_arena_pt_temp[0][0], arena_size, screen_size)
            div_disp_pt_temp[0][1] = arena_to_display(div_arena_pt_temp[0][1], arena_size, screen_size)
            # dividing line at 90 deg
            div_disp_pt_temp[1][0] = arena_to_display(div_arena_pt_temp[1][0], arena_size, screen_size)
            div_disp_pt_temp[1][1] = arena_to_display(div_arena_pt_temp[1][1], arena_size, screen_size)
            # dividing line at 180 deg
            div_disp_pt_temp[2][0] = arena_to_display(div_arena_pt_temp[2][0], arena_size, screen_size)
            div_disp_pt_temp[2][1] = arena_to_display(div_arena_pt_temp[2][1], arena_size, screen_size)
            # dividing line at -90 deg
            div_disp_pt_temp[3][0] = arena_to_display(div_arena_pt_temp[3][0], arena_size, screen_size)
            div_disp_pt_temp[3][1] = arena_to_display(div_arena_pt_temp[3][1], arena_size, screen_size)
            # control the drawing sequency as follows
            # draw the automaton, a solid circle representing the automaton
            pygame.draw.circle(screen, automaton_color, pos_disp_temp, automaton_size, 0)
            # draw the sensing circle, an empty circle representing the sensing range
            pygame.draw.circle(screen, range_color, pos_disp_temp, radius_disp_temp, 1)
            # draw the dividing line segments
            pygame.draw.line(screen, div_line_color, div_disp_pt_temp[0][0], div_disp_pt_temp[0][1], 1)
            pygame.draw.line(screen, range_color, div_disp_pt_temp[1][0], div_disp_pt_temp[1][1], 1)
            pygame.draw.line(screen, range_color, div_disp_pt_temp[2][0], div_disp_pt_temp[2][1], 1)
            pygame.draw.line(screen, range_color, div_disp_pt_temp[3][0], div_disp_pt_temp[3][1], 1)
            # draw the positive moving direction line segment
            pygame.draw.line(screen, mov_line_color, mov_disp_pt_temp[0], mov_disp_pt_temp[1], 3)
        pygame.display.update()  # eqivalent to update() now

        # reset timer_last
        timer_last = timer_now

# quit pygame
pygame.quit()






