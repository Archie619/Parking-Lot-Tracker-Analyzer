from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="Parking Lot API",
    description="API for monitoring parking lot spot availability",
    version="0.1"
)

'''
Root health check
'''
@app.get("/")
def root():
    return {"backend status": "open"}


# ---------- Models ----------
class SpotUpdate(BaseModel):
    spot_id: int
    occupied: bool

class SpotStatus(BaseModel):
    spot_id: int
    occupied: bool

class LotStatus(BaseModel):
    total_spots: int
    available_spots: int
    spots: List[SpotStatus]



# ---------- Endpoints ----------
@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/spots", response_model=LotStatus)
def get_spots():
    total = len(spots)
    available = sum(not occupied for occupied in spots.values())
    spot_list = [{"spot_id": sid, "occupied": occ} for sid, occ in spots.items()]
    return {"total_spots": total, "available_spots": available, "spots": spot_list}

@app.post("/spots/update")
def update_spot(update: SpotUpdate):
    spots[update.spot_id] = update.occupied
    return {"message": f"Spot {update.spot_id} updated to {update.occupied}"}

@app.get("/lot/info")
def lot_info():
    return {
        "lot_id": 1,
        "location": "Main Lot",
        "total_spots": len(spots),
        "reserved_spots": 1
    }