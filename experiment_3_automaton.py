# automaton class for experiment 3

# automaton has constant velocity, the moving direction changed by pheromone
# which is produced by the automata, and pheromone weakens over time
# in this way the automaton no loonger needs a moving direction fixed to the body
# it is free to move omnidirectional like a partical now

from math import *
from utilities import reset_radian

class Automaton:
    def __init__(self, pos, vel, ori, radia_radius, alpha):
        self.pos = list(pos)  # pos[0] for x, pos[1] for y, convert to list
        self.vel = vel  # unsigned scalar, constant
        self.ori = ori  # global orientation of moving direction
        # radiation length and alpha are attributes of this automaton
        self.radia_radius = radia_radius  # radiation length
        # alpha is relative angle of generated pheromone to moving direction
        self.alpha = alpha
    def update_with_accel(self, accel_r, delta_t):
        # update position and orientation of automaton with acceleration
        # accel_r is signed centripetal acceleration, rotating ccw is positive
        ori_delta = accel_r*delta_t/self.vel
        # print warning msg if rotation angle is too large
        if ori_delta > pi/2:
            print("rotation angle is too large for one update")
        # use middle orientation to calculate new position
        ori_mid = reset_radian(self.ori + ori_delta/2)
        self.pos[0] = self.pos[0] + cos(ori_mid) * self.vel*delta_t
        self.pos[1] = self.pos[1] + sin(ori_mid) * self.vel*delta_t
        # update orientation
        self.ori = reset_radian(self.ori + ori_delta)
    def update_without_accel(self, delta_t):
        # update position and orientation of automaton without acceleration
        self.pos[0] = self.pos[0] + cos(self.ori) * self.vel*delta_t
        self.pos[1] = self.pos[1] + sin(self.ori) * self.vel*delta_t
    def check_boundary(self, arena_size, delta_t):  # rebound the automaton on boundaries
        if self.vel == 0: return  # nothing to do if automaton is still
        # use velocities in Cartesian arena coordinates to control automaton rebound
        vel_x_temp = self.vel * cos(self.ori)
        vel_y_temp = self.vel * sin(self.ori)
        if ((self.pos[0] >= arena_size[0]/2 and vel_x_temp > 0)
            or (self.pos[0] <= -arena_size[0]/2 and vel_x_temp < 0)):
            # if automaton out of left or right bouddaries
            # flip positive moving direction along vertical line
            self.ori = reset_radian(2*(pi/2) - self.ori)
            # update once again so the position is inside arena
            self.update_without_accel(delta_t)
        if ((self.pos[1] >= arena_size[1]/2 and vel_y_temp > 0)
            or (self.pos[1] <= -arena_size[1]/2 and vel_y_temp < 0)):
            # if automaton out of top or bottom bouddaries
            # flip positive moving direction along horizontal line
            self.ori = reset_radian(2*(0) - self.ori)
            self.update_without_accel(delta_t)
    # accessors for Automaton class
    def get_pos(self):
        # return a copy of pos, not binding to another variable
        return self.pos[:]
    def get_ori(self):
        return self.ori
    def get_radia_radius(self):
        return self.radia_radius
    def get_alpha(self):
        return self.alpha




