import cv2
from fastapi import APIRouter
from pydantic import BaseModel
from analysis.rolling_analysis import lots, lot_maps, img_w, img_h
from analysis.space_detection import define_spots

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
    
    # attempt to open rtsp connection; taking snapshot
    # of the empty lot
    stream = cv2.VideoCapture(lot.lot_feed_source)

    if not stream.isOpened():
        status = 'failure'
        message = 'rtsp link could not be established'
    else:
        success, ss = stream.read()
        if not success:
            status = 'failure'
            message = ('rtsp link reached but screenshot could not' +
                       'be produced')

    # add the lot to the rolling analysis, if everything has been
    # successful up to this point
    if status == 'success':
        lots.append({'name': lot.lot_name,
                     'empty_lot_img': ss,
                     'live_lot_stream': lot.lot_feed_source + '?rtsp_transport=tcp&stimeout=2000000',
                     'spots': define_spots(cv2.resize(ss, (img_w, img_h)))})

    return {'status': status,
            'message': message}