import math, sys

'''
Merge collinear lines or lines so close together they
might as well be

Inputs: 
    angle_threshold: angle difference between lines
    distance_threshold: pixel distance difference between lines
    lines: list of lines to be considered

Outputs:
    merged_lines: line list post merge
'''
def merge_lines(angle_threshold: int, distance_threshold: int, 
                lines: list):
    
    merged_lines = []                 # line list post merge
    consumed = [False] * len(lines)   # list of lines in / out of a group

    # make groups of similar angle / distance (between line points) lines 
    for i in range(len(lines)):
        if consumed[i]:
            continue
        x1_1, y1_1, x2_1, y2_1 = lines[i][0]
        group = [(x1_1, y1_1, x2_1, y2_1)]
        consumed[i] = True

        for j in range(i + 1, len(lines)):
            if consumed[j]:
                continue
            x1_2, y1_2, x2_2, y2_2 = lines[j][0]
            
            # angle of line calculated using arctangent w/slope
            ang_1 = math.degrees(math.atan2(y2_1 - y1_1, x2_1 - x1_1))
            ang_2 = math.degrees(math.atan2(y2_2 - y1_2, x2_2 - x1_2))

            # distance between line points calculated using distance equation
            distance_btw_1 = math.sqrt((x1_2 - x1_1)**2 + (y1_2 - y1_1)**2)
            distance_btw_2 = math.sqrt((x2_2 - x1_1)**2 + (y2_2 - y1_1)**2)
            distance_btw_3 = math.sqrt((x1_2 - x2_1)**2 + (y1_2 - y2_1)**2)
            distance_btw_4 = math.sqrt((x2_2 - x2_1)**2 + (y2_2 - y2_1)**2) 
            
            # lines must be close in angle and distance in order to
            # be merged
            if ((abs(ang_1 - ang_2) < angle_threshold or 
                abs(abs(ang_1 - ang_2)-180) < angle_threshold) and
                (distance_btw_1 < distance_threshold or
                distance_btw_2 < distance_threshold or
                distance_btw_3 < distance_threshold or
                distance_btw_4 < distance_threshold)
                ):
                    group.append((x1_2, y1_2, x2_2, y2_2))
                    consumed[j] = True
        
        # merge group of lines into one line, use 
        # unit vectors to represent direction of line
        # helpful refresh for unit vectors:
        # https://en.wikipedia.org/wiki/Unit_vector
        magnitude = math.sqrt((x2_1 - x1_1)**2 + (y2_1 - y1_1)**2)
        uv_x = (x2_1 - x1_1) / magnitude
        uv_y = (y2_1 - y1_1) / magnitude

        # now that we have unit vectors to represent the original
        # line's x and y direction we can separate the lines into a
        # general point group, we no longer care about point pairs
        points = [(x1_1,  y1_1), (x2_1, y2_1)]
        for x1, y1, x2, y2 in group[1:]:
            points.append((x1, y1))
            points.append((x2, y2))

        # with the general direction and points, we can now find the
        # point pair that will give us the longest line
        # we do this by checking which points will give us vectors
        # with the longest / shortest magnitude, when combined into a
        # normal point pair this will give use the longest line
        curr_mag = -1
        min_mag = sys.maxsize
        max_mag = -1
        min_point = (None, None)
        max_point = (None, None)
        for (x, y) in points:
            curr_mag = (x * uv_x) +  (y * uv_y)
            if curr_mag < min_mag:
                min_mag = curr_mag
                min_point = (x,y)
            if curr_mag > max_mag:
                max_mag = curr_mag
                max_point = (x, y) 

        merged_lines.append([(min_point[0], min_point[1], max_point[0], max_point[1]), None])

    return merged_lines



'''
Detect intersection points between lines, using determinants
equation used can be found here:
https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection

Inputs: 
    lines: list of lines to be considered

Outputs:
    intersect_points: all points where two lines intersect
'''
def calc_intersects(lines: list):
    
    intersect_points= []

    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            x1_1, y1_1, x2_1, y2_1 = lines[i][0]
            x1_2, y1_2, x2_2, y2_2 = lines[j][0]

            denom = ((x1_1 - x2_1) * (y1_2 - y2_2)) - ((y1_1 - y2_1) * (x1_2 - x2_2))

            # if lines are parallel or coincident, denom is 0
            if denom == 0:
                continue

            x_intersect = ((((x1_1 * y2_1) - (y1_1 * x2_1)) * (x1_2 - x2_2)) - 
                        ((x1_1 - x2_1) * ((x1_2 * y2_2) - (y1_2 * x2_2)))) / denom
            y_intersect = ((((x1_1 * y2_1) - (y1_1 * x2_1)) * (y1_2 - y2_2)) - 
                        ((y1_1 - y2_1) * ((x1_2 * y2_2) - (y1_2 * x2_2)))) / denom
            
            # confirm the calculated intersect is within both lines
            if (min(x1_1, x2_1) <= x_intersect <= max(x1_1, x2_1) and
                min(y1_1, y2_1) <= y_intersect <= max(y1_1, y2_1) and
                min(x1_2, x2_2) <= x_intersect <= max(x1_2, x2_2) and
                min(y1_2, y2_2) <= y_intersect <= max(y1_2, y2_2)
                ):
                intersect_points.append((int(x_intersect), int(y_intersect), 
                                        lines[i][0], lines[j][0]))
                
    return intersect_points



'''
Make a point list out of cut intersect lines

Inputs:
    intersect_lines: list of intersect lines

Outputs:
    intersect_line_points: list of points created from intersect
                           line list
'''
def calc_intersect_line_points(intersect_lines: list):

    intersect_line_points = []
    
    for intersect_line in intersect_lines:
        x1, y1, x2, y2 = intersect_line
        intersect_line_points.append((x1, y1))
        intersect_line_points.append((x2, y2))

    return intersect_line_points
