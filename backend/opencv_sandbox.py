import cv2, numpy

# load an image, resizing it to an appropriate size
pl_img = cv2.imread('.\images\diag_PL2.jpg', 1)
pl_img = cv2.resize(pl_img, (800, 445))

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

# draw start & end points
line_se_img = pl_img.copy()
for line in lines:
    x1, y1, x2, y2 = line[0]   
    cv2.circle(line_se_img, (x1,y1), 5, (0,255,0), -1)  # start point  (green)
    cv2.circle(line_se_img, (x2,y2), 5, (255,0,0), -1)  # end point    (blue)

# detect intersection points between lines, using determinants
# equation can be found here: 
# https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
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
            cv2.circle(line_se_img, (int(x_intersect), int(y_intersect)), 5, 
                    (0, 0, 255), -1)

# display the image
cv2.imshow('Current Analysis', line_se_img)
cv2.waitKey(0)
cv2.destroyAllWindows()