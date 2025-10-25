import cv2, numpy
import threading, os, sys
import logging
from fastapi import FastAPI
from routers import lot_init, lot_status
from analysis.rolling_analysis import begin_rolling_analysis, lots
from db_init import cursor

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s | %(levelname)s | %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                    stream=sys.stdout)

app = FastAPI(
    title="Parking Lot API",
    description="API for monitoring parking lot spot availability",
    version="1.0"
)
logging.info("Backend API online")

app.include_router(lot_init.router)
app.include_router(lot_status.router)
logging.info("Routers linked")

try:
    # pull all saved lots from the DB
    cursor.execute('SELECT lot_code, empty_img_path, live_stream '
               'FROM lot_media')
    saved_lots = cursor.fetchall()
    logging.info("Lots successfully pulled from database")
except Exception:
    logging.error("Could not pull lots from database")

# add saved_lots to rolling_analysis
for lot in saved_lots:

    try:
        numpy_byte_img = numpy.frombuffer(lot[1], dtype=numpy.uint8)
        empty_lot_img = cv2.imdecode(numpy_byte_img, cv2.IMREAD_COLOR)
        logging.info(f"Lot {lot[0]}'s empty lot image decoded successfully")
    except Exception:
        logging.error(f"Lot {lot[0]}'s empty lot image could not be decoded, skipping lot")
        continue

    try:
        # retrieve spot map
        cursor.execute('SELECT lr.row_index, s.space_number, spp.point_index, spp.x, spp.y '
                    'FROM lot_row AS lr '
                        'JOIN space AS s '
                            'ON lr.row_id = s.row_id '
                        'JOIN space_polygon_point AS spp '
                            'ON s.space_id = spp.space_id '
                        'WHERE lr.lot_code = ?', (lot[0],))
        spot_points = cursor.fetchall()
        logging.info(f"Lot {lot[0]}'s spot map retrieved successfully")
    except Exception:
        logging.error(f"Lot {lot[0]}'s spot map could not be retrieved, skipping lot")
        continue
    
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
    logging.info(f"Lot {lot[0]} added to rolling analysis")

# suppress stderr to not flood console with ffmpeg logs
# NOTE: I'm sure there's a better way to do this but I'm
#       tired of fighting with it :)
dump = open(os.devnull, 'w') 
os.dup2(dump.fileno(), sys.stderr.fileno())

# begin rolling analysis as it's own thread
threading.Thread(target=begin_rolling_analysis, daemon=True).start()

'''
Check if the backend opened up successfully
'''
@app.get("/")
def root():
    return {"backend status": "open"}
