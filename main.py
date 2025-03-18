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
    # You’re returning floats and strings, not Column objects
    results = [{"lat": j.lat, "lng": j.lng, "popup": j.popup} for j in jeepneys]
    return JSONResponse(content=results)

class JeepneyCreate(BaseModel):
    lat: float
    lng: float
    popup: str | None = None

@app.post("/api/jeepneys")
def add_jeepney(jeepney: JeepneyCreate, db: Session = Depends(get_db)):
    new_jeepney = Jeepney(
        lat=jeepney.lat,
        lng=jeepney.lng,
        popup=jeepney.popup
    )
    db.add(new_jeepney)
    db.commit()
    db.refresh(new_jeepney)
    return {"status": "success", "id": new_jeepney.id}