import cv2, numpy

# load an image, resizing it to an appropriate size
pl_img = cv2.imread('.\images\empty_PL1.jpg', 1)
pl_img = cv2.resize(pl_img, (800, 445))

# mask out everything that isn't a parking space line
hsv_img = cv2.cvtColor(pl_img, cv2.COLOR_BGR2HSV)

line_low_lim = numpy.array([0, 0, 200])
line_high_lim = numpy.array([255, 50, 255])

mask_img = cv2.inRange(hsv_img, line_low_lim, line_high_lim)

# display the image
cv2.imshow('Parking Lot', pl_img)
cv2.imshow('Parking Lot Mask', mask_img)
cv2.waitKey(0)
cv2.destroyAllWindows()