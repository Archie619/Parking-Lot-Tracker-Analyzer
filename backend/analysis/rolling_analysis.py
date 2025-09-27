import cv2, numpy
from analysis.space_detection import define_spots, detect_fullness

img_w = 800
img_h = 444

lots = []   
lot_maps = {}
lot_previews = {}

'''
Show spots in a lot

Inputs:
    e_lot_img: empty image of lot
    l_lot_img: live image of lot

Outputs:
    None
'''
def show_detection_as_image():
    #########################################################
    # THIS WILL BE REMOVED FOR A INPUT VARIABLE TO FUNCTION #
    #########################################################
    empty_lot = cv2.imread('.\images\diag_PL2.jpg', 1)
    live_lot = cv2.imread('.\images\live_diag_PL2.jpg', 1)
    #########################################################

    # resize images to appropriate size for analysis
    empty_lot = cv2.resize(empty_lot, (img_w, img_h))
    live_lot = cv2.resize(live_lot, (img_w, img_h))

    cv2.imshow('Analysis', empty_lot)

    # identify spots from the empty lot image
    spots = define_spots(empty_lot)   # NOTE: EVENTUALLY WILL NEED TO PASS IMG HERE

    # now with our list of spot quadrilaterals, draw the spot
    # detection zones
    analysis_img = live_lot.copy()
    for spot_row in spots:
        for spot in spot_row:
            p1 = spot[0]
            p2 = spot[1]
            p3 = spot[2]
            p4 = spot[3]
            cv2.line(analysis_img, p1, p2, (0, 0, 0), 3)
            cv2.line(analysis_img, p2, p3, (0, 0, 0), 3)
            cv2.line(analysis_img, p3, p4, (0, 0, 0), 3)
            cv2.line(analysis_img, p4, p1, (0, 0, 0), 3)
    
    # with spots marked we need to check if a car is in
    # the spot or not; use background subtraction
    # NOTE: WE NEED TO KEEP A SAMPLE OF THE EMPTY LOT FOR ME TO DO THIS
    #       i.e during initialization take a snap of the lot and store 
    #       in DB
    spot_occupancy, a_spots, t_spots = detect_fullness(empty_lot, live_lot, 
                                                       (img_h, img_w), spots)

    # after detection zone statuses are determined overlay the color
    # on the live image
    i = 0
    j = 0
    for spot_row in spots:
        for spot in spot_row:
            if spot_occupancy[i][j]['occupied']:
                cv2.fillPoly(analysis_img, [numpy.array(spot)], (0, 255, 0))
            else:
                cv2.fillPoly(analysis_img, [numpy.array(spot)], (0, 0, 255))
            j += 1
        i += 1
        j = 0

    # apply a transparency filter over the original image
    transparency = 0.3
    cv2.addWeighted(analysis_img, transparency, live_lot, 1 - transparency, 0, live_lot) 

    # display the images
    cv2.imshow('Analysis', live_lot)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return None



'''
Start infinite loop to analyze lots

Inputs:
    None

Outputs:
    None
'''
def begin_rolling_analysis():
    
    i = -1
    while 1:
        
        if len(lots) > 0:
            # rolling i increment
            i = (i + 1) % len(lots)

            # open the live lot stream and take a snapshot
            stream = cv2.VideoCapture(lots[i]["live_lot_stream"])

        if len(lots) > 0 and stream.isOpened():
            success, live_img = stream.read()        
            if success:
                # resize images to a reasonable size
                lots[i]["empty_lot_img"] = cv2.resize(lots[i]["empty_lot_img"], 
                                                      (img_w, img_h))
                live_img = cv2.resize(live_img, (img_w, img_h))
                
                # detect spot fullness
                spot_map, a_spots, t_spots = detect_fullness(lots[i]["empty_lot_img"],
                                                            live_img,
                                                            (img_h, img_w),
                                                            lots[i]["spots"])
                
                # update status lists
                lot_maps[lots[i]["name"]] = spot_map
                lot_previews[lots[i]["name"]] = {'available': a_spots,
                                                'total': t_spots}
