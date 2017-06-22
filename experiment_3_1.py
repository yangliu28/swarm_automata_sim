# based on experiment 3, change is in the pheromone implementation

############### pheromone implementation ###############
# previously pheromone is implemented in discrete display coordinates
# the problem is that the number of pheromone values is the same with number of pixels
# which can be at the level of millions
# it takes around 370 ms to calculate the time dissipation alone
# and it takes more to update the automata physics under influence of pheromone
# A CHANGE to the implementation is that I no longer store pheromone in a discrete
# coordinates like the display coordinates, but only record its emission as it is
# in the arena coordinates. The advantage is that I have very limited pheromone
# data, since it's in the continuous arena coordinates, the acceleration from
# pheromone is calculate in a more precise way. But when updating physics for each
# automaton, it needs to search all pheromone emissions for the influence.
# also each automaton generate one pheromone emission for each frame, the frame rate
# should be controlled in an appropriate speed
# in this method, pheromone dissipation is a must have, otherwise there will be
# infinite number of pheromone emissions, and it would be impossible to index

############### analysis ###############
# 00/00/0000

import pygame
import pygame.gfxdraw
import random
import math

# use the same automaton
from experiment_3_automaton import Automaton
from utilities import *  # my utilities 

pygame.init()  # initialize pygame

# for display
screen_size = (1200, 900)  # width and height in pixels, even numbers
# black background, white automaton, pheromone is visualized as different colors
# it's like colored pheromone is radiated from white automaton
background_color = (0, 0, 0)  # background in black
automaton_color = (255, 255, 255)  # automaton in white
automaton_size = 4  # number of pixels of radius, for the size of automaton
arrow_size = 1.2  # a line segment to indicate moving, in arena coordinates

# set up the simulation window and surface object
icon = pygame.image.load('pacman4_icon.png')
pygame.display.set_icon(icon)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Continuous Mobile Automata 3.1')
# define frame updating period, also used in automata physics
frame_period = 100  # in ms
delta_t = frame_period / 1000.0  # in second

# physics for automata, the virtual world the automata exist
# the size of the world the automata play, proportional to display size, no unit
arena_size = (100.0, 100.0 * screen_size[1]/screen_size[0])
# a key size for reference of distance
key_dist = arena_size[0] / 20  # 1/10 on both size of x axis

# variables to configure the simulation
automata_quantity = 30
const_vel = key_dist * 0.5  # constant velocity, per second
# 2-D pheromone is only radiated to left and right along the path
# be aware that I use "radius" in the variable, but pheromone only radiates to
# its left and right, not radiate into a circle
radia_radius_com = key_dist * 1.0  # typical radius, it can change on each autumaton
# alpha is the relative angle of the generated pheromone vector to the moving direction
alpha = math.pi/2
# inside one ecosystem, pheromone from all automata should have same gradient
# that means given a radiation length, we should be able to calculate
# the strongest radiation strength for that automaton, vice verse
# so the ratio of radiation strength over distance is an attribute of the system
# and the maximum strength or distance is an attribute of the automaton
# here I choose maximum radiation radius as the attribute
# so maximum radiation strength need to be calculated for each automaton
radia_ratio = 1.5  # change of pheromone strength over distance
# the pheromone propogation rule is that it's strongest on the line
# and decrease linearly with distance until reach zero
# pheromone dissipation speed is an attribute of pheromone map
# time to dissipate the (standard) strongest pherome from one automaton
dissi_time = 5000  # in ms
# decrease of pheromone strength in each update
dissi_delta = (radia_radius_com*radia_ratio) / (dissi_time/frame_period)
# predict a maximum length for pheromone vector, for color density in visualization
pheromone_visual_max = (radia_radius_com*radia_ratio) * 1.0

# instantiate the automata swarm
automata = []  # container for all automata
for i in range(automata_quantity):
    # random position, away from the boundaries
    pos_temp = ((random.random()*arena_size[0] - arena_size[0]/2) * 0.9,
                (random.random()*arena_size[1] - arena_size[1]/2) * 0.9)
    vel_temp = const_vel
    ori_temp = random.random() * 2*math.pi - math.pi  # create random in (-pi, pi)
    radia_radius_temp = radia_radius_com  # same radiation length, homogeneous swarm
    alpha_temp = alpha  # same alpha, homogeneous swarm
    object_temp = Automaton(pos_temp, vel_temp, ori_temp, radia_radius_temp, alpha_temp)
    automata.append(object_temp)

# variables for the pheromone
# recording the positions(in arena coordinates) of automata in a fifo
# when calculating acceleration from pheromone for one automaton, it searches the
# position history for line segment that automaton is in its pheromone range
# the size of the fifo for each automaton depends on frame rate, and dissipation speed
# each updating frame will generate a new position in the fifo
# so frame rate should be under control, such that the simulation can run in real time
p_radia_radius = [automata[i].get_radia_radius() for i in range(automata_quantity)]
# followed is the number of position points in the fifo history for each automaton
p_fifo_size = [int(p_radia_radius[i]*radia_ratio/dissi_delta)+1 
               for i in range(automata_quantity)]
# the fifo for automata positions, index by [automaton][fifo][x_y]
p_pos = [[] for i in range(automata_quantity)]
# fill up the fifo before the main loop
for i in range(automata_quantity):  # the current position as first on in fifo
    p_pos[i].append(automata[i].get_pos())
    for j in range(p_fifo_size[i]-1):  # for the rest points in fifo
        automata[i].update_without_accel(delta_t)
        automata[i].check_boundary(arena_size, delta_t)
        p_pos[i].append(automata[i].get_pos())

# the loop
sim_exit = False  # simulation exit flag
sim_pause = False  # simulation pause flag
timer_last = pygame.time.get_ticks()  # return number of milliseconds after pygame.init()
timer_now = timer_last  # initialize it with timer_last
loop_count = 0
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

    # loop_count = loop_count + 1
    # print("\nin the loop %d"%loop_count)

    # update automata positions when it's time to update the frame
    timer_now = pygame.time.get_ticks()
    if (timer_now - timer_last) > frame_period:
        # update automata physics(position, orientation), speed is constant
        # by translate pheromone data to centripetal acceleration
        for i in range(automata_quantity):
            # print("##########################")  # start of debug message
            # get position and orientation in arena coordinates before update
            pos_a = automata[i].get_pos()  # "a" for in arena coordinates
            ori_a = automata[i].get_ori()
            accel_x = 0  # instantiate the acceleration container
            accel_y = 0
            # search all the pheromone records of other automata
            for j in range(automata_quantity):
                if j == i: continue  # skip itself
                # search fifo history from the end to the beginning, newest first
                # stop when find a match, one pheromone from each automaton at most
                for k in range(p_fifo_size[j]-1, 0, -1):  # reversed list
                    # line segment k starts at p_pos[j][k-1], ends at p_pos[j][k]
                    # full strength of pheromone for segment k is k*dissi_delta
                    # this segment has radiation radius of k*dissi_delta/radia_ratio
                    # first tell if the point is on left/right region of the segment
                        # by telling if the projection is between the two end points
                        # let 'AB' be the line segment, 'P' is to be evaluated
                        # gamma=(AB)*(AP)/pow(abs(AB),2), projection of 'P' is between
                        # 'A' and 'B' if gamma is in (0, 1]
                    gamma = (((pos_a[0]-p_pos[j][k-1][0])*(p_pos[j][k][0]-p_pos[j][k-1][0]) + 
                             (pos_a[1]-p_pos[j][k-1][1])*(p_pos[j][k][1]-p_pos[j][k-1][1]))/
                             ((pow(p_pos[j][k][0]-p_pos[j][k-1][0],2) +
                             pow(p_pos[j][k][1]-p_pos[j][k-1][1],2))))
                    if gamma > 0 and gamma <= 1:
                        # check if distance is in radiation radius
                        dist_temp = dist_point_to_line(pos_a, p_pos[j][k-1], p_pos[j][k])
                        if (dist_temp < k*dissi_delta/radia_ratio):
                            # if here, line segment matches, collect acceleration
                            p_len_temp = k*dissi_delta - radia_ratio*dist_temp
                            p_ori_temp = reset_radian(automata[j].get_ori() +
                                                      automata[j].get_alpha())
                            accel_x = accel_x + p_len_temp * math.cos(p_ori_temp)
                            accel_y = accel_y + p_len_temp * math.sin(p_ori_temp)
                            # break from history check from this automaton
                            # but this will still check another automaton for pheromone
                            break
            # update the physics from the acceleration
            p_len_temp = math.sqrt(pow(accel_x,2) + pow(accel_y,2))
            p_ori_temp = math.atan2(accel_y, accel_x)
            if p_len_temp == 0:  # no pheromone detected
                automata[i].update_without_accel(delta_t)
            else:
                # calculate centripetal acceleration from pheromone vector projection
                rot_temp = reset_radian(p_ori_temp - automata[i].get_ori())
                accel_r = p_len_temp * math.sin(rot_temp)  # signed
                automata[i].update_with_accel(accel_r, delta_t)
                # print("%d: len %f rot %f"%(i,p_len_temp,rot_temp))

            # rebound automaton if running out of boundaries
            automata[i].check_boundary(arena_size, delta_t)

            # update the pheromone fifo is pretty simple
            p_pos[i].pop(0)  # pop the oldest position
            p_pos[i].append(automata[i].get_pos())  # append the newest position

        # timer_physics = pygame.time.get_ticks()
        # print("time for automata physics: %d"%(timer_physics-timer_now))

        # visualize the pheromone map and automata in display, automata on top
        screen.fill(background_color)  # prepare the background first
        # draw the automata
        for i in range(automata_quantity):
            # just use the newest pos in fifo history, convert to display coordinates
            # "start" is the position of automaton itself
            pos_start_temp = arena_to_display(p_pos[i][-1], arena_size, screen_size)
            # "end" is the position of arrow end
            ori_temp = automata[i].get_ori()
            pos_end_temp = arena_to_display([p_pos[i][-1][0] + arrow_size * math.cos(ori_temp),
                                            p_pos[i][-1][1] + arrow_size * math.sin(ori_temp)],
                                            arena_size, screen_size)
            # draw the automaton, a solid circle representing the automaton
            pygame.draw.circle(screen, automaton_color, pos_start_temp, automaton_size, 0)
            # draw the line segment representing the moving direction
            pygame.draw.line(screen, automaton_color, pos_start_temp, pos_end_temp, 2)
        pygame.display.update()

        # timer_rendering = pygame.time.get_ticks()
        # print("time for rendering: %d"%(timer_rendering-timer_physics))

        # reset timer_last
        timer_last = timer_now

        # make sure to measure updating time each time simulation configuration changes
        # make sure frame_period is higher than measured time
            # general time for a update is less than 800ms
            # with fifo size of 30, automaton quantity of 30
        print("time for this update: %d"%(pygame.time.get_ticks()-timer_now))

# quit pygame
pygame.quit()



