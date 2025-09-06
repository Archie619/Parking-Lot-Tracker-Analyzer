import cv2, numpy, math, sys

# load an image, resizing it to an appropriate size
img_w = 800
img_h = 445
pl_img = cv2.imread('.\images\diag_PL2.jpg', 1)
pl_img = cv2.resize(pl_img, (img_w, img_h))

# convert to HSV (Hue, Saturation, Brightness)
hsv = cv2.cvtColor(pl_img, cv2.COLOR_BGR2HSV)

# apply a mask that masks anything outside a white range 
# (space lines are white)
lower_white = numpy.array([0, 0, 200])
upper_white = numpy.array([180, 25, 255])
mask = cv2.inRange(hsv, lower_white, upper_white)

# detect straight lines in the image
lines = cv2.HoughLinesP(mask,
                        rho=1,               # indiv. pixel granularity
                        theta=numpy.pi/180,  # sweep image in 1 deg incs
                        threshold=80,        # x pixel hits during sweep 
                                             # to be considered a line
                        minLineLength=50,    # lines must be x pixels long
                        maxLineGap=10)       # lines may have a x pixel gap

# merge lines that are collinear or so close
# they might as well be
angle_threshold = 5            # angle difference between lines
dist_threshold = 100           # pixel distance difference between lines
merged_lines = []              # line list post merge
consumed = [False] * len(lines)  # list of lines in / out of a group

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
            (distance_btw_1 < dist_threshold or
             distance_btw_2 < dist_threshold or
             distance_btw_3 < dist_threshold or
             distance_btw_4 < dist_threshold)
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

# draw start & end points
line_se_img = pl_img.copy()
masked_w_dots = mask.copy()
start_points = []
end_points = []
masked_w_dots = cv2.cvtColor(masked_w_dots, cv2.COLOR_GRAY2BGR)
for line in merged_lines:
    x1, y1, x2, y2 = line[0]
    start_points.append((x1, y1))
    end_points.append((x2, y2))
    cv2.circle(line_se_img, (x1,y1), 6, (0,255,0), -1)    # start point  (green)
    cv2.circle(line_se_img, (x2,y2), 6, (255,0,0), -1)    # end point    (blue)
    cv2.circle(masked_w_dots, (x1,y1), 6, (0,255,0), -1)  # start point  (green)
    cv2.circle(masked_w_dots, (x2,y2), 6, (255,0,0), -1)  # end point    (blue)

# detect intersection points between lines, using determinants
# equation can be found here: 
# https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
intersect_points= []
for i in range(len(merged_lines)):
    for j in range(i + 1, len(merged_lines)):
        x1_1, y1_1, x2_1, y2_1 = merged_lines[i][0]
        x1_2, y1_2, x2_2, y2_2 = merged_lines[j][0]

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
                                     merged_lines[i][0], merged_lines[j][0]))
            cv2.circle(line_se_img, (int(x_intersect), int(y_intersect)), 6, 
                    (0, 0, 255), -1)
            cv2.circle(masked_w_dots, (int(x_intersect), int(y_intersect)), 6, 
                    (0, 0, 255), -1)

# define parking space lines which are:
# startpoint -> intersection point
# or 
# endpoint -> intersection point
# to do this, first cut intersected spaces in two groups
space_lines_side1 = []
space_lines_side2 = []
intersect_lines = []
line_1_found = 0
line_2_found = 0    
for line in merged_lines:
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
            space_lines_side1.append((start_x, start_y, intersect_x, intersect_y))
            space_lines_side2.append((intersect_x, intersect_y, end_x, end_y))

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

# prune space line arrays to get rid of intersect lines or derivatives
# of intersect lines
intersect_line_points = []
for intersect_line in intersect_lines:
    x1, y1, x2, y2 = intersect_line
    intersect_line_points.append((x1, y1))
    intersect_line_points.append((x2, y2))
i = 0
popped = False
while i < len(space_lines_side1): 
    x_s, y_s, x_e, y_e = space_lines_side1[i]
    for point_1 in intersect_line_points:
        for point_2 in intersect_line_points:
            if point_1 == point_2:
                continue
            if ((x_s == point_1[0] and y_s == point_1[1] and 
                 x_e == point_2[0] and y_e == point_2[1]) or
                (x_s == point_2[0] and y_s == point_2[1] and 
                 x_e == point_1[0] and y_e == point_1[1])):
                space_lines_side1.pop(i)
                popped = True
                break
        if popped:
            break
    if not popped:
        i += 1
    popped = False
i = 0
popped = False
while i < len(space_lines_side2): 
    x_s, y_s, x_e, y_e = space_lines_side2[i]
    for point_1 in intersect_line_points:
        for point_2 in intersect_line_points:
            if point_1 == point_2:
                continue
            if ((x_s == point_1[0] and y_s == point_1[1] and 
                 x_e == point_2[0] and y_e == point_2[1]) or
                (x_s == point_2[0] and y_s == point_2[1] and 
                 x_e == point_1[0] and y_e == point_1[1])):
                space_lines_side2.pop(i)
                popped = True
                break
        if popped:
            break
    if not popped:
        i += 1
    popped = False

# TEST REMOVE
for line in space_lines_side1:
    x1, y1, x2, y2 = line
    p1 = (x1, y1)
    p2 = (x2, y2)
    cv2.line(line_se_img, p1, p2, (0, 255, 0), 3)
for line in space_lines_side2:
    x1, y1, x2, y2 = line
    p1 = (x1, y1)
    p2 = (x2, y2)
    cv2.line(line_se_img, p1, p2, (255, 0, 0), 3)
for line in intersect_lines:
    x1, y1, x2, y2 = line
    p1 = (x1, y1)
    p2 = (x2, y2) 
    cv2.line(line_se_img, p1, p2, (0, 0, 255), 3)

# with the parking space lines we can now build a
# digital spot
spots = []
s_x, s_y = -1, -1
i1_x, i1_y = -1, -1
i2_x, i2_y = -1, -1
e_x, e_y = -1, -1
intersect_found = False
end_found = False
# get side 1 spots...
for line in space_lines_side1:
    s1_x1_s, s1_y1_s, s1_x1_e, s1_y1_e = line
    s_x = s1_x1_s   # point 1 of spot
    s_y = s1_y1_s

    # for first side 1 line, endpoint should connect with
    # intersect startpoint
    for ti_line in intersect_lines:
        ti_x1_s, ti_y1_s, ti_x1_e, ti_y1_e = ti_line

        if s1_x1_e == ti_x1_s and s1_y1_e == ti_y1_s:
            i1_x = ti_x1_s   # point 2 of spot
            i1_y = ti_y1_s
            i2_x = ti_x1_e   # point 3 of spot
            i2_y = ti_y1_e
            intersect_found = True
    
    # point 3 (intersect endpoint) should connect with other
    # side 1 line endpoint
    for line in space_lines_side1:
        s2_x1_s, s2_y1_s, s2_x1_e, s2_y1_e = line

        if s2_x1_e == i2_x and s2_y1_e == i2_y:
            e_x = s2_x1_s   # point 4 of spot
            e_y = s2_y1_s
            end_found = True

    if intersect_found and end_found:
        spots.append(((s_x, s_y), (i1_x, i1_y), (i2_x, i2_y), (e_x, e_y)))
    s_x, s_y = -1, -1
    i1_x, i1_y = -1, -1
    i2_x, i2_y = -1, -1
    e_x, e_y = -1, -1
    intersect_found = False
    end_found = False

# get side 2 spots...
for line in space_lines_side2:
    s1_x1_s, s1_y1_s, s1_x1_e, s1_y1_e = line
    s_x = s1_x1_e   # point 1 of spot
    s_y = s1_y1_e

    # for first side 2 line, startpoint should connect with
    # intersect startpoint
    for ti_line in intersect_lines:
        ti_x1_s, ti_y1_s, ti_x1_e, ti_y1_e = ti_line

        if s1_x1_s == ti_x1_s and s1_y1_s == ti_y1_s:
            i1_x = ti_x1_s   # point 2 of spot
            i1_y = ti_y1_s
            i2_x = ti_x1_e   # point 3 of spot
            i2_y = ti_y1_e
            intersect_found = True
    
    # point 3 (intersect endpoint) should connect with other
    # side 2 line startpoint
    for line in space_lines_side2:
        s2_x1_s, s2_y1_s, s2_x1_e, s2_y1_e = line

        if s2_x1_s == i2_x and s2_y1_s == i2_y:
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

# now with our list of spot quadrilaterals, draw the spot
# detection zones
detection_zones_img = pl_img.copy()
for spot in spots:
    p1 = spot[0]
    p2 = spot[1]
    p3 = spot[2]
    p4 = spot[3]
    cv2.line(detection_zones_img, p1, p2, (0, 0, 255), 3)
    cv2.line(detection_zones_img, p2, p3, (0, 0, 255), 3)
    cv2.line(detection_zones_img, p3, p4, (0, 0, 255), 3)
    cv2.line(detection_zones_img, p4, p1, (0, 0, 255), 3)

# display the images
cv2.imshow('Current Analysis', detection_zones_img)
cv2.imshow('Dots n Lines', line_se_img)
cv2.waitKey(0)
cv2.destroyAllWindows()