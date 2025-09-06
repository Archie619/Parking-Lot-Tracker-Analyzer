'''
Define parking space lines as:
    startpoint -> intersection point
    or
    endpoint   -> intersection point

Inputs:
    lines: list of lines to be considered
    intersect_points: all points where two lines intersect

Outputs:
    space_lines_side_1: detected lines on side 1 of the intersect line
    space_lines_side_2: detected lines on side 2 of the intersect line
    intersect_lines: detected lines used to connect space lines 
'''
def calc_space_lines(lines: list,
                     intersect_points: list):
    
    space_lines_side_1 = []
    space_lines_side_2 = []
    intersect_lines = []

    line_1_found = 0
    line_2_found = 0    
    
    for line in lines:
        for intersect_point in intersect_points:
            start_x, start_y, end_x, end_y = line[0]
            intersect_x, intersect_y, line_1, line_2 = intersect_point

            # line_1 and line_2 are the lines that created the intersection
            x1_1, y1_1, x2_1, y2_1 = line_1
            x1_2, y1_2, x2_2, y2_2 = line_2

            # check if intersection point is on current line
            # if it is, break the line into two, split by intersection point
            if ((start_x == x1_1 and start_y == y1_1 and end_x == x2_1 and end_y == y2_1) or
                (start_x == x1_2 and start_y == y1_2 and end_x == x2_2 and end_y == y2_2)
                ):
                space_lines_side_1.append((start_x, start_y, intersect_x, intersect_y))
                space_lines_side_2.append((intersect_x, intersect_y, end_x, end_y))

            # cut the intersect line itself based off the intersection points
            # a line is defined as an intersection line if has two or more intersect
            # points along it
            if start_x == x1_1 and start_y == y1_1 and end_x == x2_1 and end_y == y2_1:
                line_1_found += 1
            elif start_x == x1_2 and start_y == y1_2 and end_x == x2_2 and end_y == y2_2:
                line_2_found += 1

        if line_1_found >= 2 or line_2_found >= 2:
            start_x, start_y, end_x, end_y = line[0]

            # sort the intersect points to align at the beginning with
            # start_x and at the end with end_x
            # NOTE: I don't think this will account for y correctly...may 
            #       need to fix later
            intersect_points.sort()

            # startpoint -> intersection point
            intersect_lines.append((start_x, start_y, 
                                    intersect_points[0][0], intersect_points[0][1]))
            # intersection point -> intersection point
            for i in range(0, len(intersect_points) - 1):
                ip_x1, ip_y1, line_1_1, line_2_1 = intersect_points[i]
                ip_x2, ip_y2, line_1_2, line_2_2 = intersect_points[i + 1]
                intersect_lines.append((ip_x1, ip_y1, ip_x2, ip_y2)) 
            # intersection point -> endpoint
            intersect_lines.append((intersect_points[len(intersect_lines) - 1][0],
                                    intersect_points[len(intersect_lines) - 1][1],
                                    end_x, end_y))

        # reset line intersection counts
        line_1_found = 0
        line_2_found = 0

    return space_lines_side_1, space_lines_side_2, intersect_lines



'''
Prune space line array to get rid of false positive intersect
lines or derivatives of intersect lines

Inputs:
    space_lines: list of space lines to prune
    intersect_line_points: list of intersection line points within lot
                           * NOT THE SAME AS BASE INTERSECT POINTS *
Outputs:
    None
'''
def prune_space_lines(space_lines: list, intersect_line_points: list):

    i = 0
    popped = False

    while i < len(space_lines): 
        x_1, y_1, x_2, y_2 = space_lines[i]
        for p_1 in intersect_line_points:
            for p_2 in intersect_line_points:
                if p_1 == p_2:
                    continue
                if ((x_1 == p_1[0] and y_1 == p_1[1] and 
                     x_2 == p_2[0] and y_2 == p_2[1]) or
                    (x_1 == p_2[0] and y_1 == p_2[1] and 
                     x_2 == p_1[0] and y_2 == p_1[1])):
                    space_lines.pop(i)
                    popped = True
                    break
            if popped:
                break
        if not popped:
            i += 1
        popped = False



'''
Build a spot list using space lines and intersect lines

Inputs:
    space_lines: list of space lines to build from
    intersect_lines: list of lines used to connect space lines
    side: side of intersection line expected, 1 or 2

Output:
    spots: list of detected spots
'''
def build_spots(space_lines: list, intersect_lines: list, side: int):
    
    spots = []
    s_x, s_y = -1, -1
    i1_x, i1_y = -1, -1
    i2_x, i2_y = -1, -1
    e_x, e_y = -1, -1
    intersect_found = False
    end_found = False

    for line in space_lines:
        s1_x1_s, s1_y1_s, s1_x1_e, s1_y1_e = line

        # spot begins with a startpoint if on side 1,
        # spot begins with a endpoint if on side 2
        if side == 1:
            s_x = s1_x1_s   # point 1 of spot
            s_y = s1_y1_s
        elif side == 2:
            s_x = s1_x1_e   # point 1 of spot
            s_y = s1_y1_e

        # for first side 1 line, endpoint should connect with
        # intersect startpoint
        # for first side 2 line, startpoint should connect with
        # intersect startpoint
        for ti_line in intersect_lines:
            ti_x1_s, ti_y1_s, ti_x1_e, ti_y1_e = ti_line

            if ((s1_x1_e == ti_x1_s and s1_y1_e == ti_y1_s and side == 1) or
                (s1_x1_s == ti_x1_s and s1_y1_s == ti_y1_s and side == 2)):
                i1_x = ti_x1_s   # point 2 of spot
                i1_y = ti_y1_s
                i2_x = ti_x1_e   # point 3 of spot
                i2_y = ti_y1_e
                intersect_found = True
        
        # point 3 (intersect endpoint) should connect with other
        # side 1 line endpoint
        # if side 1, intersect endpoint should connect with other
        # side 1 endpoint
        # if side 2, intersect endpoint should connect with other
        # side 2 line startpoint
        for line in space_lines:
            s2_x1_s, s2_y1_s, s2_x1_e, s2_y1_e = line

            if s2_x1_e == i2_x and s2_y1_e == i2_y and side == 1:
                e_x = s2_x1_s   # point 4 of spot
                e_y = s2_y1_s
                end_found = True
            elif s2_x1_s == i2_x and s2_y1_s == i2_y and side == 2:
                e_x = s2_x1_e   # point 4 of spot
                e_y = s2_y1_e
                end_found = True

        if intersect_found and end_found:
            spots.append(((s_x, s_y), (i1_x, i1_y), (i2_x, i2_y), (e_x, e_y)))

        s_x, s_y = -1, -1
        i1_x, i1_y = -1, -1
        i2_x, i2_y = -1, -1
        e_x, e_y = -1, -1
        intersect_found = False
        end_found = False
    
    return spots
