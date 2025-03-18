# type: ignore

from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import SessionLocal, Jeepney

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # or specify ['http://localhost:5173']
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# MANUAL DEBUG ---------
# # Mock data for Jeepneys
# JEEPNEY_DATA: list[dict[str, float | str]] = [
#     {"lat": 14.648792269553422, "lng": 121.06847648049134, "popup": 'Jeepney #1'},
#     {"lat": 14.654, "lng": 121.070, "popup": "Jeepney #2"},
#     {"lat": 14.650, "lng": 121.065, "popup": "Jeepney #3"},
# ]
# @app.get("/api/jeepneys")
# def get_jeepneys():
#     # Returns a list of jeepney coordinates and popup info. 
#     # The Svelte frontend will call this every 30 secs to update markers on the map.

#     return JSONResponse(content=JEEPNEY_DATA)
# MANUAL DEBUG ---------


# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/jeepneys")
def get_jeepneys(db: Session = Depends(get_db)) -> list[dict[str, float | str]]:
    jeepneys = db.query(Jeepney).all()
    results = [{"lat": j.lat, "lng": j.lng, "popup": j.popup} for j in jeepneys]
    return JSONResponse(content=results)

class JeepneyCreate(BaseModel):
    lat: float
    lng: float
    popup: str | None = None

@app.post("/api/jeepneys")
def add_jeepney(jeepney: JeepneyCreate, db: Session = Depends(get_db)):
    """
    If a Jeepney with the same 'popup' already exists, update its lat/lng.
    Otherwise, create a new record.
    """
    existing = db.query(Jeepney).filter(Jeepney.popup == jeepney.popup).first()
    if existing:
        # Update the existing record
        existing.lat = jeepney.lat
        existing.lng = jeepney.lng
        db.commit()
        db.refresh(existing)
        return {"status": "updated", "id": existing.id}
    else:
        # Create a new record
        new_jeepney = Jeepney(
            lat=jeepney.lat,
            lng=jeepney.lng,
            popup=jeepney.popup
        )
        db.add(new_jeepney)
        db.commit()
        db.refresh(new_jeepney)
        return {"status": "created", "id": new_jeepney.id}