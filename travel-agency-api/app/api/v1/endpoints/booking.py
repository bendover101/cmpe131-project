from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, date

from app.core.database import get_db
from app.models.booking import Booking, HotelReservation, FlightReservation, AttractionReservation, User, HotelMaster
from app.schemas.booking import BookingDetailResponse

router = APIRouter(prefix="", tags=["booking"])

@router.post("", response_model=BookingDetailResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=BookingDetailResponse, status_code=status.HTTP_201_CREATED)
def create_booking(payload: Dict[str, Any], db: Session = Depends(get_db)):
    user_id = payload.get("User_Id") or payload.get("userId") or payload.get("user_id") or 1
    
    user = db.query(User).filter(User.User_ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Cannot create booking.")

    agent_id = payload.get("Agent_Id") or payload.get("agentId")
    if not agent_id:
        agency_id = payload.get("agency_id") or payload.get("agencyId")
        if agency_id:
            val = str(agency_id).strip().lower()
            if val in ("agenta", "1"):
                agent_id = 1
            elif val in ("agentb", "2"):
                agent_id = 2
    if not agent_id:
        agent_id = 1

    search_params = payload.get("searchParams", {})
    start_date_str = payload.get("Start_Date") or payload.get("startDate") or search_params.get("fromDate")
    end_date_str = payload.get("End_Date") or payload.get("endDate") or search_params.get("toDate")

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else date.today()
    except:
        start_date = date.today()

    try:
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else date.today()
    except:
        end_date = date.today()

    new_booking = Booking(
        User_Id=user_id,
        Agent_Id=agent_id,
        Start_Date=start_date,
        End_Date=end_date
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    hotel_res_list = payload.get("hotel_reservations") or payload.get("hotelReservations")
    if not hotel_res_list:
        hotel_data = payload.get("hotel")
        if hotel_data:
            hotel_res_list = [hotel_data]

    if hotel_res_list:
        for hotel_item in hotel_res_list:
            hotel_code = hotel_item.get("Hotel_Code") or hotel_item.get("hotelCode") or hotel_item.get("id")
            if not hotel_code:
                continue

            if int(hotel_code) == 999999 and agent_id != 1:
                raise HTTPException(
                    status_code=403,
                    detail="Access Denied: This exclusive inventory is only available to authorized agencies."
                )

            h_in_str = hotel_item.get("Check_In_Date") or hotel_item.get("checkInDate") or hotel_item.get("checkin") or start_date_str
            h_out_str = hotel_item.get("Check_Out_Date") or hotel_item.get("checkOutDate") or hotel_item.get("checkout") or end_date_str

            try:
                check_in_date = datetime.strptime(h_in_str, "%Y-%m-%d").date() if h_in_str else start_date
            except:
                check_in_date = start_date

            try:
                check_out_date = datetime.strptime(h_out_str, "%Y-%m-%d").date() if h_out_str else end_date
            except:
                check_out_date = end_date

            rate = hotel_item.get("Rate") or hotel_item.get("rate") or hotel_item.get("totalPrice") or hotel_item.get("price") or 0.0
            try:
                rate = float(rate)
            except:
                rate = 0.0

            hotel_name = hotel_item.get("Hotel_Name") or hotel_item.get("hotelName") or hotel_item.get("name") or "Standard Cozy Stay"
            existing_master = db.query(HotelMaster).filter(HotelMaster.Hotel_Code == int(hotel_code)).first()
            if not existing_master:
                new_master = HotelMaster(Hotel_Code=int(hotel_code), Hotel_Name=hotel_name)
                db.add(new_master)
                db.commit()

            new_hotel = HotelReservation(
                Booking_Id=new_booking.Booking_Id,
                Hotel_Code=int(hotel_code),
                Check_In_Date=check_in_date,
                Check_In_Time=hotel_item.get("Check_In_Time") or hotel_item.get("checkInTime") or "14:00",
                Check_Out_Date=check_out_date,
                Check_Out_Time=hotel_item.get("Check_Out_Time") or hotel_item.get("checkOutTime") or "11:00",
                Rate=rate
            )
            db.add(new_hotel)

    flight_res_list = payload.get("flight_reservations") or payload.get("flightReservations")
    if not flight_res_list:
        flight_data = payload.get("flight")
        if flight_data:
            if isinstance(flight_data, dict) and ("outbound" in flight_data or "return" in flight_data):
                if flight_data.get("outbound"):
                    flight_res_list = [flight_data.get("outbound")]
                if flight_data.get("return"):
                    if flight_res_list:
                        flight_res_list.append(flight_data.get("return"))
                    else:
                        flight_res_list = [flight_data.get("return")]
            else:
                flight_res_list = [flight_data]

    if flight_res_list:
        for flight_item in flight_res_list:
            airline_code = flight_item.get("Airline_Code") or flight_item.get("airlineCode") or flight_item.get("airline", "UA")[:2].upper()
            flight_num = flight_item.get("Flight_Number") or flight_item.get("flightNumber") or "100"

            dep_date_str = flight_item.get("Departure_Date") or flight_item.get("departureDate") or flight_item.get("_raw_departure_date") or start_date_str
            if dep_date_str and "T" in dep_date_str:
                dep_date_str = dep_date_str.split("T")[0]

            arr_date_str = flight_item.get("Arrive_Date") or flight_item.get("arriveDate") or flight_item.get("_raw_arrival_date") or end_date_str or dep_date_str
            if arr_date_str and "T" in arr_date_str:
                arr_date_str = arr_date_str.split("T")[0]

            try:
                dep_date = datetime.strptime(dep_date_str, "%Y-%m-%d").date() if dep_date_str else start_date
            except:
                dep_date = start_date

            try:
                arr_date = datetime.strptime(arr_date_str, "%Y-%m-%d").date() if arr_date_str else end_date
            except:
                arr_date = end_date

            dep_time = flight_item.get("Departure_Time") or flight_item.get("departureTime") or "08:00"
            arr_time = flight_item.get("Arrive_Time") or flight_item.get("arrivalTime") or "12:00"

            origin = flight_item.get("Origin_Airport_Code") or flight_item.get("originAirportCode") or flight_item.get("origin") or "SFO"
            dest = flight_item.get("Destination_Airport_Code") or flight_item.get("destinationAirportCode") or flight_item.get("destination") or "LAX"

            rate = flight_item.get("Rate") or flight_item.get("rate") or flight_item.get("totalPrice") or flight_item.get("price") or 0.0
            try:
                rate = float(rate)
            except:
                rate = 0.0

            new_flight = FlightReservation(
                Booking_Id=new_booking.Booking_Id,
                Airline_Code=str(airline_code),
                Flight_Number=str(flight_num),
                Departure_Date=dep_date,
                Departure_Time=str(dep_time),
                Arrive_Date=arr_date,
                Arrive_Time=str(arr_time),
                Rate=rate,
                Origin_Airport_Code=str(origin),
                Destination_Airport_Code=str(dest)
            )
            db.add(new_flight)

    attr_res_list = payload.get("attraction_reservations") or payload.get("attractionReservations")
    if not attr_res_list:
        attr_data = payload.get("activities")
        if isinstance(attr_data, list):
            attr_res_list = attr_data

    if attr_res_list:
        for attr_item in attr_res_list:
            name = attr_item.get("Attraction_Name") or attr_item.get("attractionName") or attr_item.get("name") or "Activity"
            location = attr_item.get("Location") or attr_item.get("location") or "Destination"

            rate = attr_item.get("Rate") or attr_item.get("rate") or attr_item.get("totalPrice") or attr_item.get("price") or 0.0
            try:
                rate = float(rate)
            except:
                rate = 0.0

            price_type = attr_item.get("Price_Type") or attr_item.get("priceType") or ("Free" if rate == 0 else "Fixed")

            new_attr = AttractionReservation(
                Booking_Id=new_booking.Booking_Id,
                Attraction_Name=str(name),
                Location=str(location),
                Date=start_date,
                Time=attr_item.get("Time") or attr_item.get("duration") or "10:00",
                Price_Type=price_type,
                Rate=rate
            )
            db.add(new_attr)

    db.commit()
    db.refresh(new_booking)
    return new_booking

@router.get("/by-agent-user", response_model=List[BookingDetailResponse])
def get_user_bookings(user_id: int, agency_id: str = None, db: Session = Depends(get_db)):
    query = db.query(Booking).filter(Booking.User_Id == user_id)

    if agency_id:
        agent_id = None
        val = str(agency_id).strip().lower()
        if val in ("1", "agenta"):
            agent_id = 1
        elif val in ("2", "agentb"):
            agent_id = 2

        if agent_id:
            query = query.filter(Booking.Agent_Id == agent_id)

    bookings = query.all()
    return bookings

@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
@router.delete("/{booking_id}/", status_code=status.HTTP_204_NO_CONTENT)
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.Booking_Id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")
    db.delete(booking)
    db.commit()
    return None

@router.put("/{booking_id}", response_model=BookingDetailResponse)
@router.put("/{booking_id}/", response_model=BookingDetailResponse)
def update_booking(booking_id: int, payload: Dict[str, Any], db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.Booking_Id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")
    
    start_date_str = payload.get("Start_Date") or payload.get("startDate")
    end_date_str = payload.get("End_Date") or payload.get("endDate")
    
    if start_date_str:
        try:
            booking.Start_Date = datetime.strptime(start_date_str.split("T")[0], "%Y-%m-%d").date()
        except:
            pass
            
    if end_date_str:
        try:
            booking.End_Date = datetime.strptime(end_date_str.split("T")[0], "%Y-%m-%d").date()
        except:
            pass
            
    hotel_res = payload.get("hotel_reservations") or payload.get("hotelReservations") or []
    for h in hotel_res:
        res_no = h.get("Reservation_No") or h.get("reservationNo")
        if res_no:
            db_h = db.query(HotelReservation).filter(HotelReservation.Reservation_No == res_no).first()
            if db_h:
                rate = h.get("Rate") or h.get("rate")
                if rate is not None:
                    db_h.Rate = float(rate)
                h_in = h.get("Check_In_Date") or h.get("checkInDate")
                if h_in:
                    db_h.Check_In_Date = datetime.strptime(h_in.split("T")[0], "%Y-%m-%d").date()
                h_out = h.get("Check_Out_Date") or h.get("checkOutDate")
                if h_out:
                    db_h.Check_Out_Date = datetime.strptime(h_out.split("T")[0], "%Y-%m-%d").date()

    flight_res = payload.get("flight_reservations") or payload.get("flightReservations") or []
    for f in flight_res:
        res_no = f.get("Reservation_No") or f.get("reservationNo")
        if res_no:
            db_f = db.query(FlightReservation).filter(FlightReservation.Reservation_No == res_no).first()
            if db_f:
                rate = f.get("Rate") or f.get("rate")
                if rate is not None:
                    db_f.Rate = float(rate)
                f_dep = f.get("Departure_Date") or f.get("departureDate")
                if f_dep:
                    db_f.Departure_Date = datetime.strptime(f_dep.split("T")[0], "%Y-%m-%d").date()
                f_arr = f.get("Arrive_Date") or f.get("arriveDate")
                if f_arr:
                    db_f.Arrive_Date = datetime.strptime(f_arr.split("T")[0], "%Y-%m-%d").date()

    db.commit()
    db.refresh(booking)
    return booking


