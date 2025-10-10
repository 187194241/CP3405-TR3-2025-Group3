from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base

app = FastAPI(title="SmartSeat Backend API", version="2.0")

DATABASE_URL = "sqlite:///./smartseat.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Seat(Base):
    __tablename__ = "seats"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, unique=True)
    is_booked = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

class SeatCreate(BaseModel):
    number: str

class SeatResponse(BaseModel):
    id: int
    number: str
    is_booked: bool
    class Config:
        from_attributes = True

class BookRequest(BaseModel):
    seat_id: int

@app.get("/")
def home():
    return {"message": "Welcome to SmartSeat Backend with Database!"}

@app.get("/seats", response_model=List[SeatResponse])
def get_all_seats():
    db = SessionLocal()
    seats = db.query(Seat).all()
    db.close()
    return seats

@app.post("/seats", response_model=SeatResponse)
def create_seat(seat: SeatCreate):
    db = SessionLocal()
    new_seat = Seat(number=seat.number)
    db.add(new_seat)
    db.commit()
    db.refresh(new_seat)
    db.close()
    return new_seat

@app.post("/book")
def book_seat(request: BookRequest):
    db = SessionLocal()
    seat = db.query(Seat).filter(Seat.id == request.seat_id).first()
    if not seat:
        db.close()
        raise HTTPException(status_code=404, detail="Seat not found.")
    if seat.is_booked:
        db.close()
        raise HTTPException(status_code=400, detail="Seat already booked.")
    seat.is_booked = True
    db.commit()
    db.close()
    return {"message": f"Seat {seat.number} booked successfully."}

@app.post("/cancel")
def cancel_booking(request: BookRequest):
    db = SessionLocal()
    seat = db.query(Seat).filter(Seat.id == request.seat_id).first()
    if not seat:
        db.close()
        raise HTTPException(status_code=404, detail="Seat not found.")
    if not seat.is_booked:
        db.close()
        raise HTTPException(status_code=400, detail="Seat is not booked.")
    seat.is_booked = False
    db.commit()
    db.close()
    return {"message": f"Booking for seat {seat.number} canceled successfully."}