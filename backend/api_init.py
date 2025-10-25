import cv2
import numpy
import threading
from fastapi import FastAPI
from routers import lot_init, lot_status
from analysis.rolling_analysis import begin_rolling_analysis, lots
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

    # retrieve spot map
    cursor.execute('SELECT lr.row_index, s.space_number, spp.point_index, spp.x, spp.y '
                   'FROM lot_row AS lr '
                    'JOIN space AS s '
                        'ON lr.row_id = s.row_id '
                    'JOIN space_polygon_point AS spp '
                        'ON s.space_id = spp.space_id '
                    'WHERE lr.lot_code = ?', (lot[0],))
    spot_points = cursor.fetchall()
    
    # build spot map
    spots = [[[]]]
    row = 0
    spot = 0
    curr_space_id = 0
    for point in spot_points:
        if point[0] != row:
            spot = -1
            row += 1
            spots.append([])
        if point[1] != curr_space_id:
            curr_space_id = point[1]
            spot += 1
            spots[row].append([])
        spots[row][spot].append((point[3], point[4]))

    lots.append({'name': lot[0],
                 'empty_lot_img': empty_lot_img,
                 'live_lot_stream': lot[2] + '?rtsp_transport=tcp&stimeout=2000000',
                 'spots': spots})

threading.Thread(target=begin_rolling_analysis, daemon=True).start()

'''
Check if the backend opened up successfully
'''
@app.get("/")
def root():
    return {"backend status": "open"}
