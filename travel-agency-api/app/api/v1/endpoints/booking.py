from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db

# Import your models and schemas
from app.models.booking import Booking, HotelReservation, FlightReservation, User
from app.schemas.booking import BookingCreate, BookingDetailResponse

router = APIRouter(prefix="", tags=["booking"])

@router.post("", response_model=BookingDetailResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=BookingDetailResponse, status_code=status.HTTP_201_CREATED)
def create_booking(booking_in: BookingCreate, db: Session = Depends(get_db)):
    """
    Receives all selected booking information from the frontend and 
    persists it accurately to the database.
    """
    
    user = db.query(User).filter(User.User_ID == booking_in.User_Id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Cannot create booking.")

    new_booking = Booking(
        User_Id=booking_in.User_Id,
        Agent_Id=booking_in.Agent_Id,
        Start_Date=booking_in.Start_Date,
        End_Date=booking_in.End_Date
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking) 

    if booking_in.hotel_reservations:
        for hotel_res in booking_in.hotel_reservations:
            new_hotel = HotelReservation(
                Booking_Id=new_booking.Booking_Id,
                **hotel_res.model_dump() 
            )
            db.add(new_hotel)

    if booking_in.flight_reservations:
        for flight_res in booking_in.flight_reservations:
            new_flight = FlightReservation(
                Booking_Id=new_booking.Booking_Id,
                **flight_res.model_dump() 
            )
            db.add(new_flight)

    if booking_in.hotel_reservations or booking_in.flight_reservations:
        db.commit()
        db.refresh(new_booking)

    return new_booking

@router.get("/by-agent-user", response_model=List[BookingDetailResponse])
def get_user_bookings(user_id: int, agency_id: int = None, db: Session = Depends(get_db)):
    """
    Fetches actual bookings from the database based on the User and Agency context.
    """
    query = db.query(Booking).filter(Booking.User_Id == user_id)
    
    if agency_id:
        query = query.filter(Booking.Agent_Id == agency_id)
        
    bookings = query.all()
    
    if not bookings:
        raise HTTPException(status_code=404, detail="No bookings found for this user/agency.")
        
    return bookings
