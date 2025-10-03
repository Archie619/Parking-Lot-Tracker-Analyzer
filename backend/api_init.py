import cv2
import numpy
import threading
from fastapi import FastAPI
from routers import lot_init, lot_status
from analysis.rolling_analysis import begin_rolling_analysis, lots, img_w, img_h
from analysis.space_detection import define_spots
from db_init import cursor

app = FastAPI(
    title="Parking Lot API",
    description="API for monitoring parking lot spot availability",
    version="1.0"
)

app.include_router(lot_init.router)
app.include_router(lot_status.router)

# pull all saved lots from the DB
cursor.execute('SELECT lot_code, empty_img_path, live_stream '
               'FROM lot_media')
saved_lots = cursor.fetchall()

# add saved_lots to rolling_analysis
for lot in saved_lots:

    numpy_byte_img = numpy.frombuffer(lot[1], dtype=numpy.uint8)
    empty_lot_img = cv2.imdecode(numpy_byte_img, cv2.IMREAD_COLOR)
    
    lots.append({'name': lot[0],
                 'empty_lot_img': empty_lot_img,
                 'live_lot_stream': lot[2] + '?rtsp_transport=tcp&stimeout=2000000',
                 'spots': define_spots(cv2.resize(empty_lot_img, (img_w, img_h)))})

threading.Thread(target=begin_rolling_analysis, daemon=True).start()

'''
Check if the backend opened up successfully
'''
@app.get("/")
def root():
    return {"backend status": "open"}
