from fastapi import APIRouter, Header
from pydantic import BaseModel
from analysis.rolling_analysis import lot_maps, lot_previews

router = APIRouter()

########################################
#           PYDANTIC MODELS            #
########################################

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
Load a preview of a specific lot's statistics
'''
@router.get('/lot-preview', response_model=LotPreview)
async def load_lot_preview(lot_name: str = Header()):
    return {'lot_name': lot_name,
            'available_spots': lot_previews[lot_name]["available"],
            'total_spots': lot_previews[lot_name]["total"]}



'''
Load a specific lot's simplified status map
'''
@router.get('/lot-map', response_model=LotMap)
async def load_lot_map(lot_name: str = Header()):
    return {'lot_name': lot_name,
            'spot_map': lot_maps[lot_name]}
