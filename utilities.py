
# utility functions for the automata simulation

import math

# reset radian angle to (-pi, pi]
def reset_radian(radian):
    while radian > math.pi:
        radian = radian - 2*math.pi
    while radian <= -math.pi:
        radian = radian + 2*math.pi
    return radian

# originally used in automaton 1 & 2
# convert position in arena coordinates to display coordinates
def arena_to_display(input_pos, arena_size, display_size):
    pos_display = [0, 0]
    # int() will always round down, this is exactly what I desired
    pos_display[0] = int((input_pos[0]/arena_size[0] + 0.5) * display_size[0])
    pos_display[1] = int((0.5 - input_pos[1]/arena_size[1]) * display_size[1])
    return pos_display

# originally used in automaton 3
def display_to_arena(input_pos, display_size, arena_size):
    pos_arena = [0, 0]
    pos_arena[0] = (float(input_pos[0])/display_size[0] - 0.5) * arena_size[0]
    pos_arena[1] = (0.5 - float(input_pos[1])/display_size[1]) * arena_size[1]
    return pos_arena

# distance from a point to a line defined by two points
# https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line
def dist_point_to_line(p, l1, l2):
    # p is the point, l1 and l2 are the two points defining the line
    return (abs((l2[1]-l1[1])*p[0] - (l2[0]-l1[0])*p[1] + l2[0]*l1[1] - l2[1]*l1[0]) /
            math.sqrt(pow(l2[1]-l1[1],2) + pow(l2[0]-l1[0],2)))

# intersection of two lines both defined by two points
# https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
def intersection(l1, l2, l3, l4):
    # l1 & l2 are two points of line 1, l3 & l4 are of line 2
    return [((l1[0]*l2[1]-l1[1]*l2[0]) * (l3[0]-l4[0]) - (l1[0]-l2[0]) *
            (l3[0]*l4[1]-l3[1]*l4[0])) / ((l1[0]-l2[0])*(l3[1]-l4[1]) -
            (l1[1]-l2[1])*(l3[0]-l4[0])),
            ((l1[0]*l2[1]-l1[1]*l2[0]) * (l3[1]-l4[1]) - (l1[1]-l2[1]) *
            (l3[0]*l4[1]-l3[1]*l4[0])) / ((l1[0]-l2[0])*(l3[1]-l4[1]) -
            (l1[1]-l2[1])*(l3[0]-l4[0]))]

# originally used in experiment 3
# encode a vector to a RGB color
# vector orientation decides which one or two color in code
# vector length decides magnitude of RGB values
# seeing RGB as a color wheel, red at top, green at right bottom, blue at left bottom
def vector_to_color(v_len, v_len_max, v_ori):
    # input length and orientation of a vector
    if v_len == 0:
        return [0, 0, 0]
    else:
        # red is point up in color wheel
        red = int((v_len/v_len_max) * 256 * math.cos(v_ori - math.pi/2))
        red = min(max(red, 0), 255)  # avoid overshooting on both sides
        # green is toward right bottom
        green = int((v_len/v_len_max) * 256 * math.cos(v_ori + math.pi/6))
        green = min(max(green, 0), 255)
        # blue is toward left bottom
        blue = int((v_len/v_len_max) * 256 * math.cos(v_ori + 5*math.pi/6))
        blue = min(max(blue, 0), 255)
        return [red, green, blue]


