from fastapi import APIRouter, HTTPException
from typing import Dict

router = APIRouter()

@router.get("/lot/{lot_id}/analytics")
def get_lot_analytics(lot_id: str):
    if lot_id not in parking_lots:
        raise HTTPException(status_code=404, detail="Lot not found")
    
    lot = parking_lots[lot_id]
    capacity = lot["capacity"]
    occupied = lot["occupied"]

    if capacity == 0:
        return {"lot_id": lot_id, "percent_full": 0.0}

    percent_full = (occupied / capacity) * 100
    return {
        "lot_id": lot_id,
        "capacity": capacity,
        "occupied": occupied,
        "percent_full": round(percent_full, 2)  # e.g. 70.0
    }
