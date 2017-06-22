# (obsolete, this class has been integrated in the main program)

# pheromone class for experiment 3
# need only one instantiation for the simulation

# a class to maintain the pheromone map in the display coordinates
# each pixel in display window will have a 2-D pheromone representation
# two dimensions of the pheromone are strength and orientation
# equivalently, 2-D pheromone is a vector comprised of x and y components
# pheromone gets updated by new pheromone emission, and dissipates over time

# both polar and Cartesian coordinates can be used to store pheromone infomation
# polar coordinates are convenient to calculate centripetal acceleration on automaton
# Cartesian coordinates are convenient to update newly emitted pheromone
# conversion between the two is inevitable in this manner

from math import *
from utilities import reset_radian

class Pheromone:
    def __init__(self, screen_size, dissi_delta):
        # len is pheromone strength, representing the length of pheromone vector
        # ori is the orientation of pheromone vector
        # both variable array initialized to 0
        self.len = [[0 for j in range(screen_size[1])] for i in range(screen_size[0])]
        self.ori = [[0 for j in range(screen_size[1])] for i in range(screen_size[0])]
        # dissipation speed, decrease pheromone this much when update by dissipation
        self.dissi_delta = dissi_delta
    def read_index(self, index):
        # read pheromone from pheromone map by index
        # return the pheromone length and orientation at that display location
        return [self.len[index[0]][index[1]], self.ori[index[0]][index[1]]]
    def read_all(self):
        # real the entire pheromone map
        return [self.len, self.ori]
    def update_incre(self, index, pheromone_len, pheromone_ori):
        # update pheromone with new pheromone emission, incrementally
        # calculation in Cartesian coordinates
        x = (self.len[index[0]][index[1]] * cos(self.ori[index[0]][index[1]]) +
             pheromone_len * cos(pheromone_ori))
        y = (self.len[index[0]][index[1]] * sin(self.ori[index[0]][index[1]]) +
             pheromone_len * sin(pheromone_ori))
        self.len[index[0]][index[1]] = sqrt(pow(x,2), pow(y,2))
        self.ori[index[0]][index[1]] = atan2(y, x)
    def update_dissi(self, index, time):
        # update pheromone by dissipation over time
        len_temp = self.len[index[0]][index[1]]
        if len_temp == 0:
            return
        else:
            if len_temp <= self.dissi_delta:
                self.len[index[0]][index[1]] = 0
                self.ori[index[0]][index[1]] = 0
            else:
                self.len[index[0]][index[1]] = len_temp - self.dissi_delta




