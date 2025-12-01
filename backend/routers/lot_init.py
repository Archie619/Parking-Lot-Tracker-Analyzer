import cv2
import logging
from fastapi import APIRouter
from pydantic import BaseModel
from analysis.rolling_analysis import lots, lot_maps, img_w, img_h
from analysis.space_detection import define_spots
from db_init import cursor, db_con

router = APIRouter()

########################################
#           PYDANTIC MODELS            #
########################################

class NewLot(BaseModel):
    lot_name: str
    lot_feed_source: str    # source should be a rtsp stream
                            # ex. rtsp://192.168.1.1:22/stream

class LotInitResponse(BaseModel):
    status: str
    message: str | None

########################################
#             FUNCTIONS                #
########################################

'''
Initialize a new lot
'''
@router.post('/lot-init', response_model=LotInitResponse)
async def init_lot(lot: NewLot):
    
    status = 'success'
    message = None

    # confirm lot does not already exist
    if lot.lot_name in lot_maps:
        status = 'failure'
        message = 'lot name already exists'
        logging.warning("Attempt to create lot with name of existing lot, lot creation cancelled")
    
    # attempt to open rtsp connection; taking snapshot
    # of the empty lot
    stream = cv2.VideoCapture(lot.lot_feed_source)

    if not stream.isOpened():
        status = 'failure'
        message = 'rtsp link could not be established'
        logging.error("RTSP stream could not be opened, lot creation cancelled")
    else:
        success, ss = stream.read()
        logging.info("RTSP stream for lot creation successfully opened")
        if not success:
            status = 'failure'
            message = ('rtsp link reached but screenshot could not' +
                       'be produced')
            logging.error("RTSP stream could be opened but screenshot could not be produced," +
                          " lot creation cancelled")

    try:
        # define the spot map for the new lot
        spot_map = define_spots(cv2.resize(ss, (img_w, img_h)))
        logging.info("Spot map created for lot creation")
    except Exception:
        status = 'failure'
        message = 'screenshot created but spot map could not be created'
        logging.error("Spot map could not be produced from screenshot, lot creation cancelled")

    # add the lot to the rolling analysis and database, if everything has been
    # successful up to this point
    if status == 'success':

        # add lot to rolling analysis
        lots.append({'name': lot.lot_name,
                     'empty_lot_img': ss,
                     'live_lot_stream': lot.lot_feed_source + '?rtsp_transport=tcp&stimeout=2000000',
                     'spots': spot_map})
        
        # encode image to bytes
        success, img_bytes = cv2.imencode(".png", ss)
        
        if success:
            logging.info("Empty lot image successfully encoded")
            try:
                # add overall lot information
                cursor.execute('INSERT INTO lot_media (lot_code, empty_img_path, live_stream)' 
                            'VALUES (?, ?, ?)', (lot.lot_name, img_bytes.tobytes(), lot.lot_feed_source))
                db_con.commit()
                logging.info("Newly created lot media successfully added to database")
            except Exception:
                logging.warning("Newly created lot could not be added to database, lot creation continuing")
        else:
            logging.warning("Empty lot image could not be encoded, lot creation continuing")

        try:
            last_space = 0
            # add lot row information
            for i in range(0, len(spot_map)):
                cursor.execute('INSERT INTO lot_row (lot_code, row_index)'
                            'VALUES (?, ?)', (lot.lot_name, i))
                db_con.commit()
                cursor.execute('SELECT row_id FROM lot_row WHERE lot_code = ? AND row_index = ?', 
                            (lot.lot_name, i))
                row_id = cursor.fetchone()[0]

                # add spot information
                for j in range(0, len(spot_map[i])):
                    cursor.execute('INSERT INTO space (lot_code, space_number, row_id)'
                                'VALUES (?, ?, ?)', (lot.lot_name, last_space + j, row_id))
                    db_con.commit()
                    cursor.execute('SELECT space_id FROM space '
                                'WHERE lot_code = ? AND space_number = ? AND row_id = ?', 
                                (lot.lot_name, last_space + j, row_id))
                    space_id = cursor.fetchone()[0]

                    # add spot mapping information
                    for k in range(0, 4):
                        cursor.execute('INSERT INTO space_polygon_point (space_id, point_index, '
                                    'x, y) VALUES (?, ?, ?, ?)', 
                                    (space_id, k, float(spot_map[i][j][k][0]), 
                                        float(spot_map[i][j][k][1])))
                        db_con.commit()
                last_space += len(spot_map[i])
            logging.info("Newly created lot's spot map successfully added to database")
        except Exception:
            logging.warning("Newly created lot's spot map could not be added to database, lot creation continuing")

    return {'status': status,
            'message': message}
