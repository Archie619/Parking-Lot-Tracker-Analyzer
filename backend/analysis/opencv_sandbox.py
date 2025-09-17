import cv2, numpy
from math_functions import merge_lines, calc_intersects, calc_intersect_line_points
from space_detection import (calc_space_lines, prune_space_lines, build_spots, 
                             detect_fullness)

# load an image, resizing it to an appropriate size
img_w = 800
img_h = 445
pl_img = cv2.imread('..\images\diag_PL2.jpg', 1)
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

# merge close together lines
merged_lines = merge_lines(5, 100, lines)

# find all intersection points in image
intersect_points = calc_intersects(merged_lines)

# acquire lines used to define a parking space
space_lines_side1, space_lines_side2, intersect_lines = calc_space_lines(merged_lines,
                                                                         intersect_points)

# decompose intersect line list into list of points
intersect_line_points = calc_intersect_line_points(intersect_lines)

# prune space line arrays
prune_space_lines(space_lines_side1, intersect_line_points)
prune_space_lines(space_lines_side2, intersect_line_points)

# build list of all spots in the lot
spots = []
spots += build_spots(space_lines_side1, intersect_lines, 1)
spots += build_spots(space_lines_side2, intersect_lines, 2)

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

# with spots marked we need to check if a car is in
# the spot or not; use background subtraction
# NOTE: WE NEED TO KEEP A SAMPLE OF THE EMPTY LOT FOR ME TO DO THIS
#       i.e during initialization take a snap of the lot and store 
#       in DB
empty_lot = cv2.imread('..\images\diag_PL2.jpg', 1)
empty_lot = cv2.resize(empty_lot, (img_w, img_h))
live_lot = cv2.imread('..\images\live_diag_PL2.jpg', 1)
live_lot = cv2.resize(live_lot, (img_w, img_h))

spot_occupancy = detect_fullness(empty_lot, live_lot, (img_h, img_w), spots)

# after detection zone statuses are determined overlay the color
# on the live image
i = 0
overlay = live_lot.copy()
for spot in spots:
    if spot_occupancy[i] == 1:
        cv2.fillPoly(overlay, [numpy.array(spot)], (0, 255, 0))
    else:
        cv2.fillPoly(overlay, [numpy.array(spot)], (0, 0, 255))
    i += 1

# apply a transparency filter over the original image
transparency = 0.3
cv2.addWeighted(overlay, transparency, live_lot, 1 - transparency, 0, live_lot) 

# display the images
cv2.imshow('Analysis', live_lot)
cv2.waitKey(0)
cv2.destroyAllWindows()