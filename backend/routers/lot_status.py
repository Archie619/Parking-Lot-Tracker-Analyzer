from fastapi import APIRouter, Header
from pydantic import BaseModel
from analysis.rolling_analysis import lot_stats

router = APIRouter()

########################################
#           PYDANTIC MODELS            #
########################################

class SpotStatus(BaseModel):
    spot_id: int
    occupied: bool

class LotPreview(BaseModel):
    available_spots: int
    total_spots: int

class LotMap(BaseModel):
    spot_map: list[list[SpotStatus]]

########################################
#             FUNCTIONS                #
########################################

'''
Load a preview of a specific lot's statistics
'''
@router.get('/lot-preview', response_model=LotPreview)
async def load_lot_preview(lot_name: str = Header()):
    
    available_spots = 0
    total_spots = 0
    
    return {'available_spots': available_spots,
            'total_spots': total_spots}



'''
Load a specific lot's simplified status map
'''
@router.get('/lot-map') # NOTE: re-add this... response_model=LotMap
async def load_lot_map(lot_name: str = Header()):
    print()
    return {'spot_map': lot_stats[lot_name]}