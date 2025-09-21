import threading
from fastapi import FastAPI
from routers import lot_init, lot_status
from analysis.rolling_analysis import begin_rolling_analysis

app = FastAPI(
    title="Parking Lot API",
    description="API for monitoring parking lot spot availability",
    version="1.0"
)

app.include_router(lot_init.router)
app.include_router(lot_status.router)

threading.Thread(target=begin_rolling_analysis, daemon=True).start()

'''
Check if the backend opened up successfully
'''
@app.get("/")
def root():
    return {"backend status": "open"}
