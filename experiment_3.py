# (with the purpose to further simply the automaton rules based on experiment 2)
# experiment 3 implements an environment-interactive automaton
# based on a new concept of "2-D pheromone", or "interactive vector field"

# there are researches simulating pheromone the way ant colony uses it
# to study the application of dispersion in swarm robots
# this simulation increase pheromone dimension to 2, strength and direction
# or x and y components of a vector in Cartesian coordinates

# to quantify the pheromone vector, there is no analytic formula to represent it
# the arena needs to be discretized to high density such that automata can
# use pheromone data smoothly under the influence of the vector field
# here I store vector field information in display coordinates
# the minimum position unit is a pixel, this should be dense enough for pheromone
# the physical motions of the automata are still carried in the arena coordinates

# how the pheromone is propogated?
# I think of two ways to emit pheromone from automata to environment:
    # 1.first method is to leave pheromone seed on the path of the automata
    # the pheromone seed propogates pheromone to neighbors over time
    # this can be done together with the time dissipation of pheromone
    # one seed will propogate pheromone into a circular area
    # 2.second method(adopted here), which is not so intuitive and natural
    # is to calculate propogated area in advanced
    # and assign desired pheromone value according to its distance to automaton
    # time dissipation is done individually

############### analysis ###############
# 03/26/2017
# it's time consuming to implement pheromone discretely and in a good-enough
# definition, experiment 3_1 implements pheromone in the continuous arena coordinates

import pygame
import pygame.gfxdraw
import random
import math

from experiment_3_automaton import Automaton
# from experiment_3_pheromone import Pheromone
from utilities import *

pygame.init()  # initialize pygame

# for display
screen_size = (1200, 900)  # width and height in pixels, even numbers
# black background, white automaton, pheromone is visualized as different colors
# it's like colored pheromone is radiated from white automaton
background_color = (0, 0, 0)  # background in black
automaton_color = (255, 255, 255)  # automaton in white
automaton_size = 4  # number of pixels of radius, for the size of automaton

# set up the simulation window and surface object
icon = pygame.image.load('pacman4_icon.png')
pygame.display.set_icon(icon)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Continuous Mobile Automata 3')
# define frame updating period, also used in automata physics
frame_period = 100  # in ms

# physics for automata, the virtual world the automata exist
# the size of the world the automata play, proportional to display size, no unit
arena_size = (100.0, 100.0 * screen_size[1]/screen_size[0])
# a key size for reference of distance
key_dist = arena_size[0] / 20  # 1/10 on both size of x axis

# variables to configure the simulation
automata_quantity = 30
const_vel = key_dist * 1.0  # constant velocity, per second
# 2-D pheromone is only radiated to left and right along the path
# be aware that I use "radius" in the variable, but pheromone only radiates to
# its left and right, not radiate into a circle
radia_radius = key_dist * 1.0  # the distance to the left or right of radiation
# alpha is the relative angle of the generated pheromone vector to the moving direction
alpha = math.pi/6
# inside one ecosystem, pheromone from all automata should have same gradient
# that means given a radiation length, we should be able to calculate
# the strongest radiation strength for that automaton, vice verse
# so the ratio of radiation strength over distance is an attribute of the system
# and the maximum strength or distance is an attribute of the automaton
# here I choose maximum radiation length as the attribute
# so maximum radiation strength need to be calculated for each automaton
radia_ratio = 0.2  # change of pheromone strength over distance
# the pheromone propogation rule is that it's strongest on the line
# and decrease linearly with distance until reach zero
# pheromone dissipation speed is an attribute of pheromone map
# following controls how long it takes to dissipate clear the strongest emission
dissi_delta = (radia_radius*radia_ratio) / (3000/frame_period)  # 3 seconds
# predict a maximum length for pheromone vector, for color density in visualization
pheromone_visual_max = (radia_radius*radia_ratio) * 1.0

# instantiate the automata swarm
automata = []  # container for all automata
for i in range(automata_quantity):
    # random position, away from the boundaries
    pos_temp = ((random.random()*arena_size[0] - arena_size[0]/2) * 0.9,
                (random.random()*arena_size[1] - arena_size[1]/2) * 0.9)
    vel_temp = const_vel
    ori_temp = random.random() * 2*math.pi - math.pi  # create random in (-pi, pi)
    radia_radius_temp = radia_radius  # same radiation length, homogeneous swarm
    alpha_temp = alpha  # same alpha, homogeneous swarm
    object_temp = Automaton(pos_temp, vel_temp, ori_temp, radia_radius_temp, alpha_temp)
    automata.append(object_temp)

# variables for the pheromone map
# to be indexed in [x][y], x and y are in display coordinates
# length of the pheromone vector
p_len = [[0 for j in range(screen_size[1])] for i in range(screen_size[0])]
# orientation of the pheromone vector
p_ori = [[0 for j in range(screen_size[1])] for i in range(screen_size[0])]

# the loop
sim_exit = False  # simulation exit flag
sim_pause = True  # simulation pause flag
timer_last = pygame.time.get_ticks()  # return number of milliseconds after pygame.init()
timer_now = timer_last  # initialize it with timer_last
delta_t = frame_period / 1000.0  # time period to calculate changes in automata physics
ii_i = 0
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

    ii_i = ii_i + 1
    print("\nin the loop %d"% ii_i)

    # update automata positions when it's time to update the frame
    timer_now = pygame.time.get_ticks()
    if (timer_now - timer_last) > frame_period:
        # update automata physics(position, orientation), speed is constant
        # by translate pheromone data to centripetal acceleration
        for i in range(automata_quantity):
            # print("##########################")  # start of debug message
            # get position and orientation in arena coordinates before update
            pos_a_before = automata[i].get_pos()  # "a" for in arena coordinates
            ori_a_before = automata[i].get_ori()
            radia_radius_temp = automata[i].get_radia_radius()
            alpha_temp = automata[i].get_alpha()
            # get automaton display coordinates to read pheromone
            pos_disp_temp = arena_to_display(pos_a_before, arena_size, screen_size)
            p_len_temp = p_len[pos_disp_temp[0]][pos_disp_temp[1]]
            p_ori_temp = p_ori[pos_disp_temp[0]][pos_disp_temp[1]]
            # update automaton physics with pheromone reading
            if p_len_temp == 0:  # no pheromone detected
                automata[i].update_without_accel(delta_t)
            else:
                # calculate centripetal acceleration from pheromone vector projection
                rot_temp = reset_radian(p_ori_temp - automata[i].get_ori())
                accel_r = p_len_temp * math.sin(rot_temp)  # centripetal acceleration is signed
                automata[i].update_with_accel(accel_r, delta_t)

            # update pheromone map from new pheromone emission
            # first we need to find the pixels that are inside the swept area
            # get position and orientation in arena coordinates after update
            pos_a_after = automata[i].get_pos()
            ori_a_after = automata[i].get_ori()
            # calculate the left and right end points of radiation length
            # for both automaton positions before and after the physics update
            # together the four points form a quadrilateral
            # the sequence are defined such that they follow a counter-clockwise order
                # (left and right are regarding to the moving direction)
                # point 1 is on the left of automaton before update
                # point 2 is on the right of automaton before update
                # point 3 is on the right of automaton after update
                # point 4 is on the left of automaton after update
            # vertices for the quadrilateral in arena coordinates
            # 'p' for point, 'a' for arena coordinates, 'q' for quadrilateral
            paq1 = [pos_a_before[0] + radia_radius_temp * math.cos(ori_a_before+math.pi/2),
                    pos_a_before[1] + radia_radius_temp * math.sin(ori_a_before+math.pi/2)]
            paq2 = [pos_a_before[0] + radia_radius_temp * math.cos(ori_a_before-math.pi/2),
                    pos_a_before[1] + radia_radius_temp * math.sin(ori_a_before-math.pi/2)]
            paq3 = [pos_a_after[0] + radia_radius_temp * math.cos(ori_a_after-math.pi/2),
                    pos_a_after[1] + radia_radius_temp * math.sin(ori_a_after-math.pi/2)]
            paq4 = [pos_a_after[0] + radia_radius_temp * math.cos(ori_a_after+math.pi/2),
                    pos_a_after[1] + radia_radius_temp * math.sin(ori_a_after+math.pi/2)]
            # it's possible that line 1-2(by point 1 & 2) and line 3-4 may intersect
            # in this case the swept area is a triangle instead of a quadrilateral
            # the euqation to check if a point p(x,y) is on which side of
            # the line formed by point A(x1,y1) and B(x2,y2) is:
                # (y-y1)(x2-x1)-(x-x1)(y2-y1) > 0
                # can be derived from the cross product of vector AB and AP
            # polarity of paq3 and paq4 regarding to line paq1-paq2
            paq3_pole = ((paq3[1]-paq1[1])*(paq2[0]-paq1[0])-
                         (paq3[0]-paq1[0])*(paq2[1]-paq1[1]))
            paq4_pole = ((paq4[1]-paq1[1])*(paq2[0]-paq1[0])-
                         (paq4[0]-paq1[0])*(paq2[1]-paq1[1]))
            if paq3_pole*paq4_pole > 0:
                # paq3 and paq4 are on same side of line paq1-paq2
                # then the area to propogate pheromone is a quadrilateral
                # next step is generating a list of points in the display coordinates
                # and check if they are inside the quadrilateral
                # a crude method I used is traversing points in the smallest rectangle
                # that covers all four vertices of the quadrilateral
                # first convert vertices to display coordiantes
                # 'p' for point, 'd' for display coordinates, 'q' for quadrilateral
                pdq1 = arena_to_display(paq1, arena_size, screen_size)
                pdq2 = arena_to_display(paq2, arena_size, screen_size)
                pdq3 = arena_to_display(paq3, arena_size, screen_size)
                pdq4 = arena_to_display(paq4, arena_size, screen_size)
                # find the edges of the rough rectangle, should not exceed the display
                x_min = max(min(pdq1[0], pdq2[0], pdq3[0], pdq4[0]), 0)
                x_max = min(max(pdq1[0], pdq2[0], pdq3[0], pdq4[0]), screen_size[0]-1)
                y_min = max(min(pdq1[1], pdq2[1], pdq3[1], pdq4[1]), 0)
                y_max = min(max(pdq1[1], pdq2[1], pdq3[1], pdq4[1]), screen_size[1]-1)
                # check if the pixels in the rectangle are inside the quadrilateral
                for i_x in range(x_min, x_max+1):  # this includes x_max
                    for i_y in range(y_min, y_max+1):
                        # convert to arena coordinates
                        pt = display_to_arena([i_x, i_y], screen_size, arena_size)
                        # check if it's on the left of every side of quadrilateral
                        # use "if" in serial, will quit when one condition is unsatisfied
                        if ((pt[1]-paq1[1])*(paq2[0]-paq1[0])-
                            (pt[0]-paq1[0])*(paq2[1]-paq1[1])) > 0:
                            # on the left of line paq1-paq2
                            if ((pt[1]-paq2[1])*(paq3[0]-paq2[0])-
                                (pt[0]-paq2[0])*(paq3[1]-paq2[1])) > 0:
                                # on the left of line paq2-paq3
                                if ((pt[1]-paq3[1])*(paq4[0]-paq3[0])-
                                    (pt[0]-paq3[0])*(paq4[1]-paq3[1])) > 0:
                                    # on the left of line paq3-paq4
                                    if ((pt[1]-paq4[1])*(paq1[0]-paq4[0])-
                                        (pt[0]-paq4[0])*(paq1[1]-paq4[1])) > 0:
                                        # on the left of line paq4-paq1
                                        # if here, then pixel is inside quadrilateral
                                        # next step is to update pheromone
                                        # equation for distance from a point to a line:
                                        # https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line
                                        dist_temp = dist_point_to_line(pt, pos_a_before, pos_a_after)
                                        # the pheromone vector to be added
                                        p_len_incre = (radia_radius_temp - dist_temp) * radia_ratio
                                        p_ori_incre = reset_radian((ori_a_before+ori_a_after)/2 +
                                                                 alpha_temp)
                                        # the original pheromone vector
                                        p_len_orig = p_len[i_x][i_y]
                                        p_ori_orig = p_ori[i_x][i_y]
                                        # adding the pheromone vectors
                                        v_x = p_len_orig * math.cos(p_ori_orig) + p_len_incre * math.cos(p_ori_incre)
                                        v_y = p_len_orig * math.sin(p_ori_orig) + p_len_incre * math.sin(p_ori_incre)
                                        # assign the new pheromone vector
                                        p_len[i_x][i_y] = math.sqrt(pow(v_x,2) + pow(v_y,2))
                                        p_ori[i_x][i_y] = math.atan2(v_y, v_x)
            else:
                # paq3 and paq4 are on different side of line paq1-paq2,
                # or one of them is on the line of pq1-pq2
                # in either case, the pheromone area is a triangle
                # if both on the line(should not happen), then no pheromone area
                if (paq3_pole == 0) and (paq4_pole == 0):
                    print("error: both end points are on old line")
                    # print("%f %f %f %f %f %f %f %f")%(paq1[0],paq1[1],paq2[0],paq2[1],
                    #                                   paq3[0],paq3[1],paq4[0],paq4[1])
                    continue
                # calculate intersection of old and new sweeping line
                pt_inter = intersection(paq1, paq2, paq3, paq4)
                if paq3_pole > 0:
                    # point paq3 is on the left
                    # new triangle is made of pt_inter, paq2, paq3
                    # new vertices for the triangle in arena coordinates
                    # 'p' for point, 'a' for arena coordinates, 't' triangle
                    pat1 = pt_inter
                    pat2 = paq2
                    pat3 = paq3
                else:
                    # point paq4 is on the left
                    # new triangle if made of paq1, pt_inter, paq4
                    pat1 = paq1
                    pat2 = pt_inter
                    pat3 = paq4
                # convert vertices to display coordinates
                # 'p' for point, 'd' for display coordinates, 't' triangle
                pdt1 = arena_to_display(pat1, arena_size, screen_size)
                pdt2 = arena_to_display(pat2, arena_size, screen_size)
                pdt3 = arena_to_display(pat3, arena_size, screen_size)
                # use the same technique to find all the possible pixels
                # find the edges of the rough rectangle
                x_min = max(min(pdt1[0], pdt2[0], pdt3[0]), 0)
                x_max = min(max(pdt1[0], pdt2[0], pdt3[0]), screen_size[0]-1)
                y_min = max(min(pdt1[1], pdt2[1], pdt3[1]), 0)
                y_max = min(max(pdt1[1], pdt2[1], pdt3[1]), screen_size[1]-1)
                # check if pixels in the rectangle are inside the triangle
                for i_x in range(x_min, x_max+1):
                    for i_y in range(y_min, y_max+1):
                        pt = display_to_arena([i_x, i_y], screen_size, arena_size)
                        # check if it's on the left of every side of triangle
                        if ((pt[1]-pat1[1])*(pat2[0]-pat1[0])-
                            (pt[0]-pat1[0])*(pat2[1]-pat1[1])) > 0:
                            # on the left of line pat1-pat2
                            if ((pt[1]-pat2[1])*(pat3[0]-pat2[0])-
                                (pt[0]-pat2[0])*(pat3[1]-pat2[1])) > 0:
                                # on the left of line pat2-pat3
                                if ((pt[1]-pat3[1])*(pat1[0]-pat3[0])-
                                    (pt[0]-pat3[0])*(pat1[1]-pat3[1])) > 0:
                                    # on the left of line pat3-pat1
                                    # if here, this pixel is inside the triangle
                                    # update pheromone the same way
                                    dist_temp = dist_point_to_line(pt, pos_a_before, pos_a_after)
                                    # the pheromone vector to be added
                                    p_len_incre = (radia_radius_temp - dist_temp) * radia_ratio
                                    p_ori_incre = reset_radian((ori_a_before+ori_a_after)/2 +
                                                            alpha_temp)
                                    # the original pheromone vector
                                    p_len_orig = p_len[i_x][i_y]
                                    p_ori_orig = p_ori[i_x][i_y]
                                    # adding the pheromone vectors
                                    v_x = p_len_orig * cos(p_ori_orig) + p_len_incre * cos(p_ori_incre)
                                    v_y = p_len_orig * sin(p_ori_orig) + p_len_incre * sin(p_ori_incre)
                                    # assign the new pheromone vector
                                    p_len[i_x][i_y] = sqrt(pow(v_x,2) + pow(v_y,2))
                                    p_ori[i_x][i_y] = atan2(v_y, v_x)

            # rebound automaton if running out of boundaries
            automata[i].check_boundary(arena_size, delta_t)

        timer_physics = pygame.time.get_ticks()
        print("time for updating automata physics: %d"%(timer_physics-timer_now))

        # update pheromone map by dissipation over time
        # decrease length of all pheromone vectors by a fixed length
        for i in range(screen_size[0]):
            for j in range(screen_size[1]):
                # avoid decreasing to negative
                p_len[i][j] = max(p_len[i][j] - dissi_delta, 0)

        timer_pheromone = pygame.time.get_ticks()
        print("time for dissipating pheromone map: %d"%(timer_pheromone-timer_physics))

        # visualize the pheromone map and automata in display, automata on top
        screen.fill(background_color)  # prepare the background first
        # generate color code for the pheromone vector, and draw on screen
        for i in range(screen_size[0]):
            for j in range(screen_size[1]):
                rgb_temp = vector_to_color(p_len[i][j], pheromone_visual_max, p_ori[i][j])
                pygame.gfxdraw.pixel(screen, i, j, rgb_temp)

        timer_rendering1 = pygame.time.get_ticks()
        print("time for rendering1: %d"%(timer_rendering1-timer_pheromone))

        # draw the automata
        for i in range(automata_quantity):
            # prepare position of this automaton
            pos_arena_temp = automata[i].get_pos()  # get raw position in arena
            # convert arena position to display position
            pos_disp_temp = arena_to_display(pos_arena_temp, arena_size, screen_size)
            # draw the automaton, a solid circle representing the automaton
            pygame.draw.circle(screen, automaton_color, pos_disp_temp, automaton_size, 0)

        pygame.display.update()

        timer_rendering2 = pygame.time.get_ticks()
        print("time for rendering2: %d"%(timer_rendering2-timer_rendering1))

        # reset timer_last
        timer_last = timer_now

# quit pygame
pygame.quit()



