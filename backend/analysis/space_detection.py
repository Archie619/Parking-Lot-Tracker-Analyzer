import cv2, numpy, math
from analysis.math_functions import (merge_lines, calc_intersects, calc_intersect_line_points,
                                    clean_fragment_lines)

img_w = 800
img_h = 444

points = []

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
            intersect_lines.append((intersect_points[(len(intersect_lines) % len(intersect_points)) - 1][0],
                                    intersect_points[(len(intersect_lines) % len(intersect_points)) - 1][1],
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

    spots.sort()
    
    return spots



'''
Function for handling the clicks on the image to remove the background

Inputs:
    None

Outputs:
    None
'''
def click(event, x, y, flags, param):
    if event == 1 and len(points) < 4:
        points.append((x, y))
        if len(points) == 4:
            cv2.destroyAllWindows()



'''
Blackout the background that isn't the parking lot

Inputs:
    empty_lot: empty image of lot

Outputs:
    empty_lot: removed background empty lot image
'''
def remove_background(empty_lot):
    
    global points
    points = []

    cv2.imshow('Click Lot Points', empty_lot)
    cv2.setMouseCallback('Click Lot Points', click)
    cv2.waitKey(0)

    mask = numpy.zeros(empty_lot.shape[:2], dtype=numpy.uint8)
    cv2.fillPoly(mask, [numpy.array(points)], 255)
    empty_lot[mask == 0] = 0

    return empty_lot



'''
Classify lines based on whether they can make spots on
the edge of the lot or on the inside of the lot

Inputs:
    lines: list of all lines detected in the lot

Outputs:
    edge_lines: list of lines that are on the edge of the lot
                (used to make lot edge spaces)
    inner_lines: list of lines that are on the inside of the lot
                 (used to make inner lot spaces)
'''
def classify_lines(lines: list, empty_lot):

    offset = 25    # pixel offset allowed for lot edge classification

    start_point_edge_T = False   # start point is close to top edge of lot
    start_point_edge_L = False   # start point is close to left edge of lot
    end_point_edge_B = False     # end point is close to bottom edge of lot
    end_point_edge_R = False     # end point is close to right edge of lot

    edge_added = False

    edge_lines = []
    inner_lines= []

    # for each line, check if the start XOR the end point
    # of the line is close to the lot edge; if it is classify
    # as a edge line, else a inner line
    for line in lines:
        x1, y1, x2, y2 = line[0]

        # set offsets
        top_offset = y1 - offset if y1 - offset >= 0 else 0
        bottom_offset = y2 + offset if y2 + offset <= img_h - 1 else img_h - 1
        left_offset = x1 - offset if x1 - offset >= 0 else 0
        right_offset = x2 + offset if x2 + offset <= img_w else img_w - 1

        if all(val == 0 for val in empty_lot[top_offset][x1]):
            start_point_edge_T = True
            loc = 'top'
        if all(val == 0 for val in empty_lot[bottom_offset][x2]):
            end_point_edge_B = True
            loc = 'bottom'
        if start_point_edge_T ^ end_point_edge_B:
            edge_added = True
            edge_lines.append((line, loc))

        if all(val == 0 for val in empty_lot[y1][left_offset]):
            start_point_edge_L = True
            loc = 'left'
        if all(val == 0 for val in empty_lot[y2][right_offset]):
            end_point_edge_R = True
            loc = 'right'
        if start_point_edge_L ^ end_point_edge_R:
            edge_added = True
            edge_lines.append((line, loc))

        if not edge_added:
            inner_lines.append(line)

        start_point_edge_T = False
        start_point_edge_L = False
        end_point_edge_B = False
        end_point_edge_R = False
        edge_added = False
    
    return edge_lines, inner_lines



'''
Build edge spots using edge lines

Inputs:
    edge_lines: list of edge lines to build spots from
    axis: str representing axis to care about for searching

Outputs:
    edge_spots: list of spots created from edge lines
'''
def build_edge_spots(edge_lines: list, axis: str):

    # get rid of outlier lines based on angle
    angles = []
    for line in edge_lines:
        x1, y1, x2, y2 = line[0]
        angles.append(math.degrees(math.atan2(y2 - y1, x2 - x1)))
    median_ang = numpy.median(angles)

    i = 0
    while i < len(edge_lines):
        x1, y1, x2, y2 = edge_lines[i][0]
        ang = math.degrees(math.atan2(y2 - y1, x2 - x1))

        diff = abs(ang - median_ang)
        if diff > 180:
            diff = 360 - diff

        if diff <= 15:
            i += 1
        else:
            edge_lines.pop(i)

    # order lines left based on their x startpoint
    if axis == 'x':
        edge_lines = sorted(edge_lines, key=lambda x: x[0][0])
    if axis == 'y':
        edge_lines = sorted(edge_lines, key=lambda y: y[0][1])

    # with lines ordered, from left to right build spots
    i = 0
    edge_spots = []
    while i < len(edge_lines) - 1:
        x1_1, y1_1, x2_1, y2_1 = edge_lines[i][0]      # spot line 1
        x1_2, y1_2, x2_2, y2_2 = edge_lines[i + 1][0]  # spot line 2
        edge_spots.append(((x1_1, y1_1), (x2_1, y2_1), (x2_2, y2_2), (x1_2, y1_2)))
        i += 1

    return edge_spots



'''
Once spots are calculated, remove the outliers; outliers are either spots
with too large / too small of areas or only a couple spots on a side

Inputs: 
    spots: list of spots which contain 4 tuples of points

Outputs:
    spots: trimmed list of spots which contain 4 tuples of points
'''
def remove_outlier_spots(spots: list):

    # calculate the median area
    all_areas = []
    for spot_row in spots:
        for spot in spot_row:
            all_x = [point[0] for point in spot]
            all_y = [point[1] for point in spot]
            area = 0.5 * abs(sum((all_x[i] * all_y[i + 1]) - (all_x[i + 1] * all_y[i]) 
                                 for i in range(-1, len(all_x) - 1)))
            all_areas.append(area)
    median_area = numpy.median(all_areas)

    # look through all spots; remove spots based on outlier area
    # or outlier row length
    i = 0
    j = 0
    while i < len(spots):
        while j < len(spots[i]):
            all_x = [point[0] for point in spots[i][j]]
            all_y = [point[1] for point in spots[i][j]]
            area = 0.5 * abs(sum((all_x[i] * all_y[i + 1]) - (all_x[i + 1] * all_y[i]) 
                                 for i in range(-1, len(all_x) - 1)))
            if area >= median_area * 2 or area <= median_area * 0.5:
                spots[i].pop(j)
            else:
                j += 1
        if len(spots[i]) < 2:
            spots[i] = []
        i += 1
        j = 0

    return spots



'''
Take trimmed map and make the simplified map more realistic to the
actual lot setup

Inputs:
    spots: spot map where everything is left justified, left and right on bottom indexes

Outputs:
    realistic_spots: spot map where map represents actual lot setup
'''
def build_realistic_map(spots: list):

    realistic_spots = []

    top = spots[0]
    mid_1 = spots[1]
    mid_2 = spots[2]
    bottom = spots[3]
    left = spots[4]
    right = spots[5]

    null_spot = ((-1, -1), (-1, -1), (-1, -1), (-1, -1))

    # take tops and bottoms IF they aren't empty, pad the shorter one
    # with nulls
    pad_len = 0
    if top != [] and bottom != []:
        if len(top) > len(bottom):
            for _ in range(len(bottom), len(top)):
                bottom.append(null_spot)
            realistic_spots.append(top)
            realistic_spots.append(bottom)
            pad_len = len(top)
        else:
            for _ in range(len(top), len(bottom)):
                top.append(null_spot)
            realistic_spots.append(top)
            realistic_spots.append(bottom)
            pad_len = len(bottom)
    elif top != []:
        realistic_spots.append(top)
        pad_len = len(top)
    elif bottom != []:
        realistic_spots.append(bottom)
        pad_len = len(bottom)

    # take lefts and rights IF they aren't empty, pad the shorter one with
    # nulls (on the vertical), prepend lefts, append rights
    if left != [] and right != []:
        if len(left) > len(right):
            for _ in range(len(right), len(left)):
                right.append(null_spot)
            for _ in range(0, len(left)):
                realistic_spots.insert(1, [null_spot for _ in range(0, pad_len)])
        else:
            for _ in range(len(left), len(right)):
                left.append(null_spot)
            for _ in range(0, len(right)):
                realistic_spots.insert(1, [null_spot for _ in range(0, pad_len)])
    elif left != []:
        for _ in range(0, len(left)):
            realistic_spots.insert(1, [null_spot for _ in range(0, pad_len)])
    elif right != []:
        for _ in range(0, len(right)):
            realistic_spots.insert(1, [null_spot for _ in range(0, pad_len)])

    if left != []:
        realistic_spots[0].insert(0, null_spot)
        for i in range(1, len(realistic_spots) - 1):
            realistic_spots[i].insert(0, left[i - 1])
        realistic_spots[len(realistic_spots) - 1].insert(0, null_spot)
    if right != []:
        realistic_spots[0].insert(len(realistic_spots[0]) - 1, null_spot)
        for i in range(1, len(realistic_spots) - 1):
            realistic_spots[i].append(right[i - 1])
        realistic_spots[len(realistic_spots) - 1].append(null_spot)

    # put middle group in the middle of nulls, if lot has edges, if not 
    # only spots in lot
    if top != [] and bottom != [] and left != [] and right != []:
        mid_vert = int((len(realistic_spots) - 2) / 2)
        mid_horiz = int((len(realistic_spots[mid_vert]) - 2) / 2)
        start_horiz = mid_horiz - int(len(mid_1) / 2)
        for i in range(start_horiz, start_horiz + len(mid_1)):
            realistic_spots[mid_vert][i] = mid_1[i - start_horiz]
            realistic_spots[mid_vert + 1][i] =  mid_2[i - start_horiz]
    else:
        realistic_spots.append(mid_1)
        realistic_spots.append(mid_2)

    return realistic_spots



'''
Detect spots in an empty lot

Inputs:
    empty_lot: empty image of lot

Outputs:
    spots: list of all spots detected; 
           spots in the form of coordinates
'''
def define_spots(empty_lot):

    # remove the background (everything that isn't the lot)
    empty_lot = remove_background(empty_lot)

    # convert to HSV (Hue, Saturation, Brightness)
    hsv = cv2.cvtColor(empty_lot, cv2.COLOR_BGR2HSV)

    # apply a mask that masks anything outside a white range 
    # (space lines are white)
    lower_white = numpy.array([0, 0, 180])
    upper_white = numpy.array([179, 100, 255])
    mask = cv2.inRange(hsv, lower_white, upper_white)

    # detect straight lines in the image
    lines = cv2.HoughLinesP(mask,
                            rho=1,               # indiv. pixel granularity
                            theta=numpy.pi/180,  # sweep image in 1 deg incs
                            threshold=40,        # x pixel hits during sweep 
                                                 # to be considered a line
                            minLineLength=50,    # lines must be x pixels long
                            maxLineGap=10)       # lines may have a x pixel gap
    
    # standardize line start & end
    for line in lines:
        x1, y1, x2, y2 = line[0]
        dy = abs(y2 - y1)
        dx = abs(x2 - x1)
        if dy > dx:  # closer to vertical than horizontal
            if y2 < y1:
                line[0] = x2, y2, x1, y1
        else:        # closer to horizontal than vertical
            if x2 < x1:
                line[0] = x2, y2, x1, y1
    
    # merge close together lines
    merged_lines = merge_lines(5, 20, lines)
    
    # clean small fragment lines that escaped merging
    merged_lines = clean_fragment_lines(merged_lines)

    # classify lines based on edge lines inner lines
    edge_lines, inner_lines = classify_lines(merged_lines, empty_lot)

    ###########################
    #    EDGE LINES LOGIC     #
    ###########################

    # sort edge lines by edge side
    top_lines, bottom_lines, left_lines, right_lines = [], [], [], []
    for line in edge_lines:
        if line[1] == 'top':
            top_lines.append(line[0])
        elif line[1] == 'bottom':
            bottom_lines.append(line[0])
        elif line[1] == 'left':
            left_lines.append(line[0])
        else:
            right_lines.append(line[0])

    # with the edges sorted, attempt to build spots based on side
    top_spots = build_edge_spots(top_lines, 'x')
    bottom_spots = build_edge_spots(bottom_lines, 'x')
    left_spots = build_edge_spots(left_lines, 'y')
    right_spots = build_edge_spots(right_lines, 'y')
    
    ###########################
    #    INNER LINES LOGIC    #
    ###########################

    # find all intersection points in image
    intersect_points = calc_intersects(inner_lines)

    # acquire lines used to define a parking space
    space_lines_side1, space_lines_side2, intersect_lines = calc_space_lines(inner_lines,
                                                                            intersect_points)

    # decompose intersect line list into list of points
    intersect_line_points = calc_intersect_line_points(intersect_lines)

    # prune space line arrays
    prune_space_lines(space_lines_side1, intersect_line_points)
    prune_space_lines(space_lines_side2, intersect_line_points)

    ###########################
    #  BRING SPACES TOGETHER  #
    ###########################

    # build list of all spots in the lot; separate by type
    spots = []
    spots += [top_spots]
    spots += [build_spots(space_lines_side1, intersect_lines, 1)]
    spots += [build_spots(space_lines_side2, intersect_lines, 2)]
    spots += [bottom_spots]
    spots += [left_spots]
    spots += [right_spots]

    spots = remove_outlier_spots(spots)

    # with outliers removed from spot groups, assemble a map that accurately
    # represents the lot
    spots = build_realistic_map(spots)

    return spots



'''
Use background subtraction to determine spot fullness

Inputs:
    empty_lot: image of empty lot
    live_lot: live image of lot
    dimensions: dimensions of image (h, w)
    spots: list of spots to analyze

Output:
    spot_occupancy: list of occupancy within spot (0 = empty, 1 = full)
    available_spots: number of available spots to park in
    total_spots: number of available and unavailable spots
'''
def detect_fullness(empty_lot, live_lot, dimensions, spots):

    # subtract the empty lot from the live lot, gray scale for color
    # consistency
    subtracted_lot = cv2.absdiff(empty_lot, live_lot)
    gray_subtracted = cv2.cvtColor(subtracted_lot, cv2.COLOR_BGR2GRAY)
    cv2.threshold(gray_subtracted, 55, 255, cv2.THRESH_BINARY, gray_subtracted)

    # check spot detection zones for certain amount of changed
    # pixels; if over threshold, spot occupied
    spot_occupancy = []
    spot_row_occupancy = []
    available_spots = 0
    total_spots = 0
    fake_spot_id = 1000
    for spot_row in spots:
        for spot in spot_row:
            if spot[0][0] != -1:
                mask = numpy.zeros(dimensions, dtype=numpy.uint8)
                cv2.fillPoly(mask, [numpy.array(spot)], (255, 255, 255))
                isolated_spot = cv2.bitwise_and(gray_subtracted, gray_subtracted, mask=mask)

                spot_area = cv2.countNonZero(mask)
                changed_pixels = cv2.countNonZero(isolated_spot)
                percent_filled = (changed_pixels / spot_area) * 100

                total_spots += 1
                if percent_filled > 25:
                    spot_row_occupancy.append({'spot_id': total_spots,
                                               'occupied': True})
                else:
                    spot_row_occupancy.append({'spot_id': total_spots,
                                               'occupied': False})
                    available_spots += 1
            else:  # empty spacer spots don't get a real spot id, any id over 1000 is a "fake" spot
                spot_row_occupancy.append({'spot_id': fake_spot_id,
                                           'occupied': False})
                fake_spot_id += 1
        spot_occupancy.append(spot_row_occupancy)
        spot_row_occupancy = []
    
    return spot_occupancy, available_spots, total_spots
