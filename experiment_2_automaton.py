# automaton class for experiment 2
# increase sensing sectors to 4, pulling and pushing in alternative order

from math import *
from utilities import reset_radian

class Automaton:
    def __init__(self, pos, vel, ori, radius, alpha):
        self.pos = list(pos)  # pos[0] for x, pos[1] for y, convert to list
        self.vel = vel  # signed scalar
        self.ori = ori  # global orientation of positive moving axis
        self.radius = radius  # radius of circle for sensing range
        # alpha is relative angle of moving direction to dividing direction
        self.alpha = alpha  # should not be changed during the life of the automaton
        self.neighbor_detected = False  # boolean to indicate if there is neighbor in range
        self.fb_vector = [0, 0]  # feedback vector as acceleration
        self.fb_mag_coef = 5.0
        self.accel_t = 0.0  # tangential acceleration, can be negative
        self.accel_r = 0.0  # centripetal acceleration, can be negative
        self.accel_ori = 0.0  # relative orientation of acceleration
    def reset_detection(self):
        # reset feedback vector and detection flag
        self.fb_vector = [0, 0]
        self.neighbor_detected = False
    def check_neighbor(self, pos):
        # input position of the automaton to be compared with
        # accumulate changes on the feedback vector
        dist_temp = hypot(pos[0]-self.pos[0], pos[1]-self.pos[1])
        if dist_temp < self.radius:  # input automaton inside sensing circle
            if (not self.neighbor_detected):
                self.neighbor_detected = True  # set detection flag
            # 1.calculate feedback based on distance
            # proportional to how close the neighbor to the automaton
            fb_magnitude = (self.radius - dist_temp) * self.fb_mag_coef
            # 2.also change magnitude of feedback according to beta
            # theta_fb is the absolute direction of feedback vector
            theta_fb = atan2(pos[1]-self.pos[1], pos[0]-self.pos[0])
            # beta is angle of feedback vector to positive dividing direction
            beta = reset_radian(theta_fb - self.ori + self.alpha)
            # beta_coef is to be applied to fb_magnitude, in [-1, 1]
                # (0, pi/2) pulling sector
                # (pi/2, pi) pushing sector
                # (pi, 3*pi/2) pulling sector
                # (3*pi/2, 2*pi) pushing sector
            beta_coef = sin(beta*2)  # it happens to be a sin() function
            # apply beta_coef to the feedback magnetitude, make it signed
            fb_magnitude = fb_magnitude * beta_coef
            # 3.add feedback as acceleration from input automaton
            self.fb_vector[0] = self.fb_vector[0] + cos(theta_fb)*fb_magnitude
            self.fb_vector[1] = self.fb_vector[1] + sin(theta_fb)*fb_magnitude
    def calculate_accel(self):
        # calculate both tangential and centripetal acceleration
        # based on accumulated feedback vector from all in-range neighbors
        accel_magnitude = hypot(self.fb_vector[0], self.fb_vector[1])
        # relative orientation to the positive moving direction
        self.accel_ori = reset_radian(atan2(self.fb_vector[1], self.fb_vector[0]) - self.ori)
        # tangiential and centripetal acceleration
        self.accel_t = accel_magnitude * cos(self.accel_ori)
        self.accel_r = accel_magnitude * sin(self.accel_ori)
    def update_with_accel(self, delta_t):  # update with calculated acceleration
        # update position, velocity, and orientation
        vel_new = self.vel + self.accel_t * delta_t
        # ori_delta is the change in orientation, counter-clockwise is positive
        if self.vel == 0:  # no change in orientation if no speed
            ori_delta = 0
        else:
            # velocity is signed; should not reset this radian angle ori_delta
            ori_delta = self.accel_r*delta_t/self.vel
        # should avoid overshooting of rotating angle, choosing smaller one
        if self.accel_r > 0:
            if self.vel > 0:
                ori_delta = min(ori_delta, reset_radian(self.accel_ori))
            elif self.vel < 0:
                ori_delta = max(ori_delta, reset_radian(self.accel_ori - pi))
        elif self.accel_r < 0:
            if self.vel > 0:
                ori_delta = max(ori_delta, reset_radian(self.accel_ori))
            elif self.vel < 0:
                ori_delta = min(ori_delta, reset_radian(self.accel_ori + pi))
        ori_new = reset_radian(self.ori + ori_delta)
        # use middle value of velocity and orientation to calculation next position
        vel_mid = (vel_new + self.vel) / 2
        ori_mid = (ori_new + self.ori) / 2
        # update position
        self.pos[0] = self.pos[0] + cos(ori_mid)*vel_mid * delta_t
        self.pos[1] = self.pos[1] + sin(ori_mid)*vel_mid * delta_t
        # update the new velocity and orientation
        self.vel = vel_new
        self.ori = ori_new
    def update_without_accel(self, delta_t):  # update without acceleration
        # if no acceleration, velocity keeps the same
        self.pos[0] = self.pos[0] + cos(self.ori)*self.vel * delta_t
        self.pos[1] = self.pos[1] + sin(self.ori)*self.vel * delta_t
    def check_boundary(self, arena_size):  # rebound the automaton on boundaries
        if self.vel == 0: return  # nothing to do if automaton is still
        # use velocities in Cartesian arena coordinates to control automaton rebound
        vel_x_temp = self.vel * cos(self.ori)
        vel_y_temp = self.vel * sin(self.ori)
        if (self.pos[0] >= arena_size[0]/2 and vel_x_temp > 0) \
            or (self.pos[0] <= -arena_size[0]/2 and vel_x_temp < 0):
            # if automaton out of left or right bouddaries
            # flip positive moving direction along vertical line
            self.ori = reset_radian(2*(pi/2) - self.ori)
        if (self.pos[1] >= arena_size[1]/2 and vel_y_temp > 0) \
            or (self.pos[1] <= -arena_size[1]/2 and vel_y_temp < 0):
            # if automaton out of top or bottom bouddaries
            # flip positive moving direction along horizontal line
            self.ori = reset_radian(2*(0) - self.ori)
    # accessors for Automaton class
    def get_pos(self):
        return self.pos
    def get_ori(self):
        return self.ori
    def get_radius(self):
        return self.radius
    def get_alpha(self):
        return self.alpha
    def get_detection_status(self):
        return self.neighbor_detected



