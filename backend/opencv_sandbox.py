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
consumed = [False]*len(lines)  # list of lines in / out of a group

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
    cv2.circle(line_se_img, (x1,y1), 5, (0,255,0), -1)    # start point  (green)
    cv2.circle(line_se_img, (x2,y2), 5, (255,0,0), -1)    # end point    (blue)
    cv2.circle(masked_w_dots, (x1,y1), 5, (0,255,0), -1)  # start point  (green)
    cv2.circle(masked_w_dots, (x2,y2), 5, (255,0,0), -1)  # end point    (blue)

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
            intersect_points.append((int(x_intersect), int(y_intersect)))
            cv2.circle(line_se_img, (int(x_intersect), int(y_intersect)), 5, 
                    (0, 0, 255), -1)
            cv2.circle(masked_w_dots, (int(x_intersect), int(y_intersect)), 5, 
                    (0, 0, 255), -1)

# display the images
cv2.imshow('Current Analysis', line_se_img)
cv2.imshow('Mask', masked_w_dots)
cv2.waitKey(0)
cv2.destroyAllWindows()