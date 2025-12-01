import logging
from fastapi import APIRouter, Header
from pydantic import BaseModel
from analysis.rolling_analysis import lot_maps, lot_previews
from db_init import cursor, db_con

router = APIRouter()

########################################
#           PYDANTIC MODELS            #
########################################

class LotNames(BaseModel):
    lot_names: list[str]

class SpotStatus(BaseModel):
    spot_id: int
    occupied: bool

class LotPreview(BaseModel):
    lot_name: str
    available_spots: int
    total_spots: int

class LotMap(BaseModel):
    lot_name: str
    spot_map: list[list[SpotStatus]]

########################################
#             FUNCTIONS                #
########################################

'''
Load names of all known lots
'''
@router.get('/lot-names', response_model=LotNames)
async def load_lot_names():

    try: 
        # pull all known lot names from the database
        cursor.execute('SELECT lot_code FROM lot_media')
        ans = cursor.fetchall()
        
        # reformat list; break tuples
        for i in range(0, len(ans)):
            ans[i] = ans[i][0]

        logging.info("Lot names successfully retrieved from database")
    except Exception:
        ans = []
        logging.error("Unable to retrieve lot names from database")

    return {'lot_names': ans}



'''
Load a preview of a specific lot's statistics
'''
@router.get('/lot-preview', response_model=LotPreview)
async def load_lot_preview(lot_name: str = Header()):

    try:
        # update DB
        cursor.execute('SELECT 1 FROM lot_summary WHERE lot_code = ?', (lot_name,))
        ans = cursor.fetchone()
        if ans is None:
            cursor.execute('INSERT INTO lot_summary (lot_code, total_spaces, occupied, free, handicap_) '
                        'VALUES (?, ?, ?, ?, ?)', (lot_name, lot_previews[lot_name]["total"], 
                            lot_previews[lot_name]["total"] - lot_previews[lot_name]["available"],
                            lot_previews[lot_name]["available"], 0))
        else:
            cursor.execute('UPDATE lot_summary SET total_spaces = ?, occupied = ?, free = ? ' 
                        'WHERE lot_code = ?', (lot_previews[lot_name]["total"], 
                            lot_previews[lot_name]["total"] - lot_previews[lot_name]["available"],
                            lot_previews[lot_name]["available"], lot_name))
        db_con.commit()
        logging.info(f"Lot {lot_name}'s preview data updated in database")
    except Exception:
        logging.error(f"Unable to update lot {lot_name}'s preview data in the database")

    if lot_name not in lot_previews.keys():
        available = 0
        total = 0
        logging.warning(f"Requested lot {lot_name} does not exist")
    else:
        available = lot_previews[lot_name]["available"]
        total = lot_previews[lot_name]["total"]
        logging.info(f"Requested lot {lot_name}'s preview retrieved")

    return {'lot_name': lot_name,
            'available_spots': available,
            'total_spots': total}



'''
Load a specific lot's simplified status map
'''
@router.get('/lot-map', response_model=LotMap)
async def load_lot_map(lot_name: str = Header()):

    if lot_name not in lot_maps.keys():
        spot_map = []
        logging.warning(f"Requested lot {lot_name} does not exist")
    else:
        spot_map = lot_maps[lot_name]
        logging.info(f"Requested lot {lot_name}'s spot map retrieved")

    return {'lot_name': lot_name,
            'spot_map': spot_map}
